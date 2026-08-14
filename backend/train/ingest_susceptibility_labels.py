"""Part 6a -- flood SUSCEPTIBILITY labels for the 1,470-point spatial grid
(susceptibility_grid.py), from the same Copernicus GFM (Sentinel-1 SAR)
archive ingest_copernicus_gfm.py already proved is public/unauthenticated/
COG-range-readable (see that file's docstring for the verification).

DIFFERENT LABELING MODEL from the temporal classifier's GFM usage, and
deliberately so:

  - ingest_copernicus_gfm.py treats a single day's observation at a single
    station as positive-only evidence (a 0 that day is NOT trusted as "no
    flood," because one SAR pass's single-pixel reading is weak evidence
    for a specific calendar date -- see that file's docstring).
  - Susceptibility asks a different question ("is this LOCATION prone to
    flooding at all," not "did it flood on date X"), so it can aggregate
    ACROSS the whole time series per point instead of trusting any single
    day: a point observed dozens/hundreds of times over years with zero
    floods is real negative evidence in aggregate, even though any one of
    those individual daily 0s would not be. This script stores raw
    (n_valid, n_flooded) counts per point -- the actual flooded/non-flooded
    label threshold is a separate decision made once real coverage numbers
    are in (see build_susceptibility_labels.py), the same "decide from
    real data, not upfront" discipline train_model.py's TEST_CUTOFF used.

SCOPE: full archive 2016-04-01 through the most recent available date (GFM
is continuous since 2015-01-01; starting a few months in matches the other
script's confirmed-available start). Wider than ingest_copernicus_gfm.py's
gap-filling window on purpose -- susceptibility wants maximum observation
DEPTH per point, not a specific calendar gap to fill.

Usage:
    python train/ingest_susceptibility_labels.py --probe-only   # item count only, no raster reads
    python train/ingest_susceptibility_labels.py --start 2016-04-01 --end 2026-08-01
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

os.environ.setdefault("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
os.environ.setdefault("CPL_VSIL_CURL_ALLOWED_EXTENSIONS", ".tif")
os.environ.setdefault("VSI_CACHE", "TRUE")
os.environ.setdefault("GDAL_HTTP_VERSION", "2")
os.environ.setdefault("CPL_VSIL_CURL_USE_HEAD", "NO")

import rasterio
import requests
from rasterio.warp import transform

sys.path.insert(0, str(Path(__file__).resolve().parent))
from susceptibility_grid import GridPoint, grid_points  # noqa: E402

OUT_DIR = Path(__file__).resolve().parent.parent / "data_raw" / "susceptibility"
STAC_SEARCH_URL = "https://stac.eodc.eu/api/v1/search"
BANGLADESH_BBOX = [88.0, 20.5, 93.0, 26.5]  # same as ingest_copernicus_gfm.py
DEFAULT_START = "2016-04-01"
DEFAULT_END = dt.date.today().isoformat()
NODATA = 255
N_WORKERS = 24

TILE_RE = re.compile(r"(E\d+N\d+T\d+)$")


def stac_search_all(start: str, end: str) -> list[dict]:
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


def point_tile_map(points: list[GridPoint]) -> dict[str, str]:
    """Per-GRID-POINT tile assignment (not per-station) -- grid points sit
    ~up to 10km from their station, close enough that they should usually
    share its tile, but this checks each point independently against real
    tile bboxes rather than assuming, since a station near a tile boundary
    could have grid points split across two tiles."""
    body = {"collections": ["GFM"], "bbox": BANGLADESH_BBOX,
            "datetime": "2024-01-01T00:00:00Z/2024-02-01T00:00:00Z", "limit": 200}
    resp = requests.post(STAC_SEARCH_URL, json=body, timeout=60)
    resp.raise_for_status()
    tiles: dict[str, list[float]] = {}
    for f in resp.json()["features"]:
        tile_id = TILE_RE.search(f["id"]).group(1)
        tiles[tile_id] = f["bbox"]

    mapping = {}
    unmatched = []
    for p in points:
        for tile_id, bbox in tiles.items():
            if bbox[0] <= p.lon <= bbox[2] and bbox[1] <= p.lat <= bbox[3]:
                mapping[p.point_id] = tile_id
                break
        else:
            unmatched.append(p.point_id)
    if unmatched:
        print(f"  WARNING: {len(unmatched)} grid points matched no tile: {unmatched[:5]}{'...' if len(unmatched) > 5 else ''}")
    return mapping


def sample_item(item: dict, points_in_tile: list[GridPoint]) -> list[tuple]:
    """Same remote-COG-sample pattern as ingest_copernicus_gfm.py's
    sample_item(), generalized to however many grid points share this
    item's tile. Returns (point_id, value) for every point with a valid
    (non-nodata) reading -- caller aggregates across all items itself."""
    href = item["assets"]["ensemble_flood_extent"]["href"]
    results = []
    try:
        with rasterio.open(href) as src:
            lons = [p.lon for p in points_in_tile]
            lats = [p.lat for p in points_in_tile]
            xs, ys = transform("EPSG:4326", src.crs, lons, lats)
            for p, x, y in zip(points_in_tile, xs, ys):
                if not (src.bounds.left <= x <= src.bounds.right and src.bounds.bottom <= y <= src.bounds.top):
                    continue
                val = list(src.sample([(x, y)]))[0][0]
                if val != NODATA:
                    results.append((p.point_id, int(val)))
    except Exception as exc:  # noqa: BLE001 -- one bad remote read shouldn't kill the run
        print(f"\n  WARNING: failed to read {href}: {exc}")
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--start", default=DEFAULT_START)
    parser.add_argument("--end", default=DEFAULT_END)
    parser.add_argument("--probe-only", action="store_true")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    points = grid_points()
    print(f"{len(points)} grid points to label")

    print("Determining grid-point -> Equi7Grid tile assignment...")
    tile_of = point_tile_map(points)
    relevant_tiles = set(tile_of.values())
    print(f"  {len(relevant_tiles)} relevant tiles: {sorted(relevant_tiles)}")
    points_by_tile: dict[str, list[GridPoint]] = defaultdict(list)
    for p in points:
        t = tile_of.get(p.point_id)
        if t:
            points_by_tile[t].append(p)

    print(f"Searching GFM STAC catalog {args.start}..{args.end} over the Bangladesh bbox...")
    all_items = stac_search_all(args.start, args.end)
    print(f"  {len(all_items)} total items found")

    relevant_items = [it for it in all_items if TILE_RE.search(it["id"]).group(1) in relevant_tiles]
    print(f"  {len(relevant_items)} items intersect our {len(relevant_tiles)} tiles")

    if args.probe_only:
        print("Probe-only mode, stopping before any raster reads.")
        print(f"Estimated raster-read work: {len(relevant_items)} items x ~{len(points)//max(len(relevant_tiles),1)} points/tile avg")
        return

    print(f"Sampling {len(relevant_items)} items with {N_WORKERS} concurrent workers...")
    counts: dict[str, dict[str, int]] = {p.point_id: {"n_valid": 0, "n_flooded": 0} for p in points}
    n_done = 0
    with ThreadPoolExecutor(max_workers=N_WORKERS) as ex:
        futures = {}
        for item in relevant_items:
            tile_id = TILE_RE.search(item["id"]).group(1)
            futures[ex.submit(sample_item, item, points_by_tile[tile_id])] = item
        for fut in as_completed(futures):
            for point_id, val in fut.result():
                counts[point_id]["n_valid"] += 1
                if val == 1:
                    counts[point_id]["n_flooded"] += 1
            n_done += 1
            if n_done % 100 == 0 or n_done == len(relevant_items):
                print(f"\r  {n_done}/{len(relevant_items)} items processed...", end="", flush=True)
    print()

    out_path = OUT_DIR / "grid_point_flood_counts.csv"
    with out_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["point_id", "station_id", "basin", "lat", "lon", "n_valid", "n_flooded"])
        for p in points:
            c = counts[p.point_id]
            w.writerow([p.point_id, p.station_id, p.basin, p.lat, p.lon, c["n_valid"], c["n_flooded"]])

    total_valid = sum(c["n_valid"] for c in counts.values())
    total_flooded = sum(c["n_flooded"] for c in counts.values())
    n_ever_flooded = sum(1 for c in counts.values() if c["n_flooded"] > 0)
    n_zero_coverage = sum(1 for c in counts.values() if c["n_valid"] == 0)
    print(f"Wrote {out_path}")
    print(f"  total valid observations: {total_valid}, total flooded observations: {total_flooded}")
    print(f"  points with >=1 flooded observation: {n_ever_flooded}/{len(points)}")
    print(f"  points with ZERO valid observations (no tile coverage): {n_zero_coverage}/{len(points)}")


if __name__ == "__main__":
    main()
