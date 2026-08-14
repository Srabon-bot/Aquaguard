"""Part 3 extension #3 -- ingest Copernicus Global Flood Monitoring (GFM) via
its public STAC catalog, as a FOURTH positive-only flood label source
alongside GFMS (primary, 2013+), DFO (1985-2010), and GFD (2002-2017, see
ingest_global_flood_db.py).

Why this exists: every other source in this pipeline (GFMS, DFO's satellite
corroboration, GFD, JRC Global Surface Water -- investigated and rejected,
see DECISIONS.md SS16) is optical/IR-based, which is blind exactly when
Bangladesh floods most: monsoon season means heavy cloud cover. GFM is
Sentinel-1 SAR (radar) -- it sees through clouds -- and is a CONTINUOUS,
systematic archive since 2015-01-01 (not event-gated like DFO/GFD), with
Sentinel-1's dense multi-track coverage over Bangladesh giving far more
observations per station than any event catalog could.

No registration needed, despite the GFM Product User Manual describing a
token-based REST-API/Web-Portal flow -- that flow is for the convenience
access methods. The underlying STAC catalog (stac.eodc.eu) and the raw
Cloud-Optimized GeoTIFFs it points to (data.eodc.eu) are both public,
unauthenticated, and directly HTTP-range-readable -- confirmed directly
(not assumed) before building this: a real STAC search returned real
items, and rasterio could open + point-sample one of the underlying COGs
over plain HTTPS with no credentials.

Tile grid, not per-swath footprints: GFM publishes to a FIXED Equi7Grid
tile grid (e.g. "E039N021T3"), each ~300x300km, reprocessed at every
Sentinel-1 pass. All 30 of our stations fall within just 5 of these tiles
(see MODEL_BUILD_PLAN.md for the full station->tile mapping) -- this
script filters to those 5 tile IDs before opening anything, since a
station's flood status is only ever affected by its own tile's time
series, not the other ~30+ tiles STAC's bbox search also happens to
return for the wider search area.

Scope: 2016-04-01 through 2020-12-31 only -- the currently-blank GFMS gap
(GFMS accessible 2013-01..2016-03 + 2021-2026, see DECISIONS.md SS6). The
full 2015-2026 archive is available and could be pulled later for
additional cross-validation of already-covered years, but that's a much
larger fetch (~39k items vs ~10k in just the gap) with lower marginal
value since GFMS/GFD already cover those years -- deliberately scoped to
where the value actually is for now.

The `ensemble_flood_extent` band's pixel value: 0 = not flooded, 1 =
flooded, 255 = nodata (no valid observation at this pixel for this pass --
common in hilly terrain, e.g. SAR radar shadow/layover, or where an
acquisition's swath edge falls short of the pixel; spot-checked directly
against Sylhet's June 2022 flood before trusting this encoding). Same
positive-only trust model as every other historical source here: a 1 is a
real trusted positive; 255 (no observation) or 0 (observed, not flooded)
are NOT treated as confident negatives at the daily label level here --
they just don't produce a positive row. (0 does mean something real --
"this exact pass observed no flood here" -- but a single 20m pixel's
single-pass reading is a much weaker negative signal than the aggregated
"confidently no flood in the whole accessible month" GFMS gives, so this
script only ever contributes positives, consistent with DFO/GFD.)

Usage:
    python train/ingest_copernicus_gfm.py
    python train/ingest_copernicus_gfm.py --start 2016-04-01 --end 2020-12-31
    python train/ingest_copernicus_gfm.py --probe-only   # just report tile assignment + item counts, no download
"""

import argparse
import csv
import datetime as dt
import os
import re
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Must be set BEFORE importing rasterio (GDAL reads these at first use).
# Cut per-file remote-open latency roughly in half in testing (~5.3s ->
# ~2.6s) and were necessary for real thread-level concurrency to actually
# materialize -- without CPL_VSIL_CURL_USE_HEAD=NO in particular, opening
# each remote COG issues an extra blocking HEAD request per file that
# serializes badly under concurrent load. See MODEL_BUILD_PLAN.md for the
# timing comparison that led to this.
os.environ.setdefault("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
os.environ.setdefault("CPL_VSIL_CURL_ALLOWED_EXTENSIONS", ".tif")
os.environ.setdefault("VSI_CACHE", "TRUE")
os.environ.setdefault("GDAL_HTTP_VERSION", "2")
os.environ.setdefault("CPL_VSIL_CURL_USE_HEAD", "NO")

import rasterio
import requests
from rasterio.warp import transform

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stations import STATIONS  # noqa: E402

OUT_DIR = Path(__file__).resolve().parent.parent / "data_raw" / "gfm"
STAC_SEARCH_URL = "https://stac.eodc.eu/api/v1/search"
BANGLADESH_BBOX = [88.0, 20.5, 93.0, 26.5]  # covers all 30 stations with margin
DEFAULT_START = "2016-04-01"
DEFAULT_END = "2020-12-31"
NODATA = 255
N_WORKERS = 24  # I/O-bound remote reads -- safe to run well beyond CPU count

TILE_RE = re.compile(r"(E\d+N\d+T\d+)$")


def stac_search_all(start: str, end: str) -> list[dict]:
    """Paginate through the STAC search API, returning every matching
    item's lightweight metadata (id + bbox + datetime + asset href) --
    cheap, no raster data touched yet."""
    items = []
    body = {"collections": ["GFM"], "bbox": BANGLADESH_BBOX,
            "datetime": f"{start}T00:00:00Z/{end}T23:59:59Z", "limit": 200}
    url = STAC_SEARCH_URL
    while True:
        resp = requests.post(url, json=body, timeout=60)
        resp.raise_for_status()
        d = resp.json()
        items.extend(d["features"])
        next_link = next((link for link in d.get("links", []) if link.get("rel") == "next"), None)
        print(f"\r  fetched {len(items)} item records...", end="", flush=True)
        if not next_link:
            break
        url, body = next_link["href"], next_link.get("body", body)
    print()
    return items


def station_tile_map() -> dict[str, str]:
    """One-time lookup (using a short recent window, since the tile grid
    itself is static/date-independent) of which Equi7Grid tile each
    station falls in. See module docstring -- all 30 fall within 5 tiles."""
    body = {"collections": ["GFM"], "bbox": BANGLADESH_BBOX,
            "datetime": "2024-01-01T00:00:00Z/2024-02-01T00:00:00Z", "limit": 200}
    resp = requests.post(STAC_SEARCH_URL, json=body, timeout=60)
    resp.raise_for_status()
    tiles: dict[str, list[float]] = {}
    for f in resp.json()["features"]:
        tile_id = TILE_RE.search(f["id"]).group(1)
        tiles[tile_id] = f["bbox"]

    mapping = {}
    for s in STATIONS:
        for tile_id, bbox in tiles.items():
            if bbox[0] <= s.lon <= bbox[2] and bbox[1] <= s.lat <= bbox[3]:
                mapping[s.station_id] = tile_id
                break  # first match is fine -- station falls in exactly one tile's "home" grid cell in practice
    return mapping


def sample_item(item: dict, stations_in_tile: list) -> list[tuple]:
    """Open one item's ensemble_flood_extent COG (remote, range-read only)
    and sample every station that falls in this item's tile. Returns
    (station_id, date, value) tuples -- caller filters to value==1."""
    href = item["assets"]["ensemble_flood_extent"]["href"]
    date = dt.datetime.fromisoformat(item["properties"]["datetime"].replace("Z", "+00:00")).date()
    results = []
    try:
        with rasterio.open(href) as src:
            lons = [s.lon for s in stations_in_tile]
            lats = [s.lat for s in stations_in_tile]
            xs, ys = transform("EPSG:4326", src.crs, lons, lats)
            for s, x, y in zip(stations_in_tile, xs, ys):
                if not (src.bounds.left <= x <= src.bounds.right and src.bounds.bottom <= y <= src.bounds.top):
                    continue
                val = list(src.sample([(x, y)]))[0][0]
                if val != NODATA:
                    results.append((s.station_id, date, int(val)))
    except Exception as exc:  # noqa: BLE001 -- a single bad remote read shouldn't kill the whole run
        print(f"\n  WARNING: failed to read {href}: {exc}")
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--start", default=DEFAULT_START)
    parser.add_argument("--end", default=DEFAULT_END)
    parser.add_argument("--probe-only", action="store_true")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Determining station -> Equi7Grid tile assignment...")
    tile_of = station_tile_map()
    relevant_tiles = set(tile_of.values())
    print(f"  {len(relevant_tiles)} relevant tiles: {sorted(relevant_tiles)}")
    stations_by_tile: dict[str, list] = defaultdict(list)
    for s in STATIONS:
        t = tile_of.get(s.station_id)
        if t:
            stations_by_tile[t].append(s)
        else:
            print(f"  WARNING: {s.station_id} did not match any tile in the probe window -- skipped")

    print(f"Searching GFM STAC catalog {args.start}..{args.end} over the Bangladesh bbox...")
    all_items = stac_search_all(args.start, args.end)
    print(f"  {len(all_items)} total items found")

    relevant_items = [it for it in all_items if TILE_RE.search(it["id"]).group(1) in relevant_tiles]
    print(f"  {len(relevant_items)} items intersect our 5 station tiles (skipping the rest)")

    if args.probe_only:
        print("Probe-only mode, stopping before any raster reads.")
        return

    print(f"Sampling {len(relevant_items)} items with {N_WORKERS} concurrent workers...")
    positive_rows: list[tuple] = []
    n_done = 0
    with ThreadPoolExecutor(max_workers=N_WORKERS) as ex:
        futures = {}
        for item in relevant_items:
            tile_id = TILE_RE.search(item["id"]).group(1)
            futures[ex.submit(sample_item, item, stations_by_tile[tile_id])] = item
        for fut in as_completed(futures):
            for station_id, date, val in fut.result():
                if val == 1:
                    positive_rows.append((station_id, date))
            n_done += 1
            if n_done % 100 == 0 or n_done == len(relevant_items):
                print(f"\r  {n_done}/{len(relevant_items)} items processed, "
                      f"{len(positive_rows)} positive station-days found so far", end="", flush=True)
    print()

    # Collapse to unique (station_id, date) pairs -- multiple items can
    # cover the same station/date (overlapping swaths, revisits within a
    # day), only need one positive per day.
    unique_days = sorted(set(positive_rows))
    print(f"{len(unique_days)} unique positive station-days after dedup (from {len(positive_rows)} raw hits)")

    station_days_csv = OUT_DIR / "station_flood_days.csv"
    with open(station_days_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["station_id", "began", "ended", "severity"])
        for station_id, date in unique_days:
            w.writerow([station_id, date, date, ""])  # single-day "event" -- began==ended

    from collections import Counter
    counts = Counter(sid for sid, _ in unique_days)
    print("\nPer-station positive-day counts:")
    for s in STATIONS:
        print(f"  {s.station_id:6s} {s.name:35s} {counts.get(s.station_id, 0)}")
    print(f"\nWrote {station_days_csv}")


if __name__ == "__main__":
    main()
