"""Download NASA's MODIS/VIIRS Global Flood Product (MCDWD_L3, reprocessed
historical archive) for our virtual gauge stations, as a second, satellite-
*observed* flood label to cross-validate against / extend GFMS's modeled
Flood_byStor label. See MODEL_BUILD_PLAN.md Part 1c addendum (2026-08-05).

Why this exists: GFMS's UMD-hosted archive turned out to only be actually
downloadable for ~8 of ~25 nominal years (see ingest_gfms.py docstring).
MCDWD_L3 is hosted directly by NASA on LAADS DAAC and covers 2003-2025 with
a real, reviewed archive (2000-2002 also exists but NASA itself flags it as
not-yet-quality-reviewed, Terra-only pre-Aqua-launch -- treat as lower
confidence if ever used). It's real satellite water-detection, not a
hydrological model's output, so it's also a philosophically more direct
"was this actually flooded" signal than GFMS's routed-storage-based one.

Product facts (from MCDWD_VCDWD_UserGuide_RevE + MCDWD_LAADS_Desc.pdf, both
fetched and read 2026-08-05):
  - Format: HDF4 (HDF-EOS2 Grid), one file per 10x10-degree tile, per day.
  - Grid: MODIS "Linear Latitude/Longitude" (LLL) tiling, NOT the sinusoidal
    MODIS grid -- a simple global geographic grid, 36 tiles wide (h00-h35)
    x 18 tiles tall (v00-v17), each 4800x4800 pixels at 0.0020833 deg/pixel
    (~232m at the equator). Tile-index formula (empirically verified against
    the User Guide's own worked example, "h09v05 for SE USA", lon~-82.5,
    lat~32.5 -> h=floor((lon+180)/10)=9, v=floor((90-lat)/10)=5, exact match):
      h = floor((lon + 180) / 10)
      v = floor((90 - lat) / 10)
    Within a tile, pixel (0,0) is the NW corner (same north-up convention as
    GFMS): col = floor((lon - tile_lon_min) / pixel_size), row = floor((tile_lat_max - lat) / pixel_size).
  - Our 6 stations fall in exactly 2 tiles: h26v06 (all 4 Jamuna stations,
    lon ~89.6-89.7E) and h27v06 (both Surma stations, lon ~91.4-91.9E), both
    v06 (lat 20-30N band). No cross-tile edge cases (stations aren't within
    a pixel of a tile boundary).
  - Filename: <SHORTNAME>.A<YYYYDOY>.<TILE>.061.<PRODTIMESTAMP>.hdf, e.g.
    MCDWD_L3.A2024183.h26v06.061.<timestamp>.hdf. PRODTIMESTAMP is not
    predictable, so the exact filename must be discovered per day via the
    LAADS API (or a directory listing) before downloading -- can't be
    constructed from the date alone like GFMS's filenames could.
  - Key layers (8-bit, all in the same HDF file): Flood_1Day_250m,
    FloodCS_1Day_250m (cloud-shadow-screened), Flood_2Day_250m,
    Flood_3Day_250m. Pixel values: 0=no water, 1=surface water (normal),
    2=recurring flood (not yet populated by NASA), 3=flood (unusual --
    **this is our positive-label value**), 255=insufficient data (usually
    cloud cover). We use Flood_3Day_250m as the primary layer (most robust
    to daily cloud gaps, per the User Guide's recommendation to prefer
    longer composites for stability) and also keep Flood_1Day_250m for a
    same-day comparison.

Auth: requires a free NASA Earthdata Login + generated token (see plan doc
for the exact registration steps given to the user 2026-08-05). Reads
EARTHDATA_TOKEN from the repo-root `.env` file (D:\\Projects\\pred_flood\\.env,
NOT backend/.env -- matches where the BWDB credentials already live).

STATUS AS WRITTEN (2026-08-05): the tile-index math and HDF4 reading path
(pyhdf, confirmed installed and importable in this venv) are solid. The
per-day file-discovery step (LAADS API v2 `content/details` query) is
constructed from the documented pattern for the sibling NRT API
(nrt3.modaps.eosdis.nasa.gov) since the exact param names for ladsweb's
archive collection weren't independently confirmed against a live response
(no token available yet to test with) -- treat --smoke-test's first real run
as the actual verification step, the same way ingest_gfms.py's row-order and
ingest_chirps.py's lat-ordering were verified empirically before trusting
them for a full backfill. If the API query shape is wrong, `find_file_for_day`
will raise with the raw response body, not fail silently.

Backfill scope (decided 2026-08-06, see MODEL_BUILD_PLAN.md "OPEN DECISION" entry
2026-08-05): full daily 2003-2025 coverage would be ~47 hours (not viable as one
run) and even monsoon-only-full-range is ~15.7h, so the user picked the
narrowest, highest-value option first -- restrict to years where GFMS's
Flood_byStor is actually accessible (2013-2016 partial, 2021-2025, see
ingest_gfms.py) intersected with monsoon season (Jun-Sep), ~6 hours. This
directly answers "does MCDWD's satellite-observed label agree with GFMS's
modeled label" before spending more time on the wider ranges. --scope monsoon-full
and --scope full remain available (unverified timing estimates, same day-loop)
for a later expansion once that cross-validation is done.

Usage:
    python train/ingest_mcdwd.py --smoke-test          # a few known-flood days, one station, verify end-to-end
    python train/ingest_mcdwd.py                        # full backfill, default scope (gfms-overlap), all stations
    python train/ingest_mcdwd.py --scope monsoon-full   # wider range, once gfms-overlap is validated
    python train/ingest_mcdwd.py --scope full           # full daily 2003-2025, needs chunking across sessions
"""

import argparse
import calendar
import csv
import datetime as dt
import os
import time
from dataclasses import dataclass
from pathlib import Path

import requests
from dotenv import load_dotenv

OUT_DIR = Path(__file__).resolve().parent.parent / "data_raw" / "mcdwd"
ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"  # repo root .env

LAADS_BASE = "https://ladsweb.modaps.eosdis.nasa.gov"
API_DETAILS_URL = f"{LAADS_BASE}/api/v2/content/details"
ARCHIVE_PRODUCT = "MCDWD_L3"  # reprocessed historical archive, 2003-2025
COLLECTION = "61"

TILE_SIZE_DEG = 10.0
PIXELS_PER_TILE = 4800
PIXEL_SIZE_DEG = TILE_SIZE_DEG / PIXELS_PER_TILE

NODATA = 255  # "insufficient data" (usually cloud cover)
FLOOD_VALUE = 3  # "flood (unusual)" -- our positive label

FIRST_DATE = "2003-01-01"  # start of the reviewed/reliable reprocessed archive
LAST_DATE = "2025-12-31"   # end of the MCDWD_L3 archive collection (2026+ is the separate _NRT collection)

FLOOD_LAYERS = ["Flood_1Day_250m", "Flood_3Day_250m"]


@dataclass
class Station:
    station_id: str
    name: str
    lat: float
    lon: float


# Mirrors ingest_discharge.py / ingest_gfms.py STATIONS.
STATIONS: list[Station] = [
    Station("SW90", "Bahadurabad (Jamuna)", 25.1897, 89.6595),
    Station("SW93", "Sariakandi (Jamuna)", 24.8952, 89.5975),
    Station("SW99", "Sirajganj (Jamuna)", 24.4534, 89.7009),
    Station("SW17", "Chilmari (Brahmaputra)", 25.5333, 89.6833),
    Station("SW267", "Sunamganj (Surma)", 25.0658, 91.3950),
    Station("SW174", "Sylhet (Surma)", 24.8949, 91.8687),
]


def tile_of(lat: float, lon: float) -> tuple[int, int]:
    h = int((lon + 180) // 10)
    v = int((90 - lat) // 10)
    return h, v


def pixel_of(lat: float, lon: float, h: int, v: int) -> tuple[int, int]:
    tile_lon_min = h * 10 - 180
    tile_lat_max = 90 - v * 10
    col = int((lon - tile_lon_min) / PIXEL_SIZE_DEG)
    row = int((tile_lat_max - lat) / PIXEL_SIZE_DEG)
    return row, col


def get_token() -> str:
    load_dotenv(ENV_PATH)
    token = os.environ.get("EARTHDATA_TOKEN")
    if not token:
        raise SystemExit(
            f"EARTHDATA_TOKEN not found in {ENV_PATH}. Register at "
            "https://urs.earthdata.nasa.gov/users/new, generate a token at "
            "https://urs.earthdata.nasa.gov/profile ('Generate Token'), and "
            f"add a line `EARTHDATA_TOKEN=<token>` to {ENV_PATH}."
        )
    return token


def get_basic_auth() -> tuple[str, str]:
    """EDL username/password, needed only for the OAuth-authorize hop in the
    archive download redirect chain (see download_hdf docstring) -- the
    Bearer token alone is not accepted there, confirmed 2026-08-05 (the
    urs.earthdata.nasa.gov/oauth/authorize step returns
    `401 HTTP Basic: Access denied.` for a Bearer-only request)."""
    load_dotenv(ENV_PATH)
    user = os.environ.get("EARTHDATA_USERNAME") or os.environ.get("EARTHDATA_user")
    pw = os.environ.get("EARTHDATA_PASSWORD") or os.environ.get("EARTHDATA_pass")
    if not user or not pw:
        raise SystemExit(
            f"EARTHDATA_USERNAME/EARTHDATA_PASSWORD not found in {ENV_PATH}. "
            "The Bearer token alone isn't accepted by the archive download's "
            "OAuth-authorize hop -- add your real Earthdata Login username/"
            f"password as EARTHDATA_USERNAME=... / EARTHDATA_PASSWORD=... to {ENV_PATH}."
        )
    return user, pw


HDF_NAME_RE_TEMPLATE = r"[A-Za-z0-9_.]+\.hdf"


def _dir_listing_url(year: int, doy: int) -> str:
    return f"{LAADS_BASE}/archive/allData/{COLLECTION}/{ARCHIVE_PRODUCT}/{year}/{doy:03d}/"


def find_file_for_day(bearer_token: str, tile: str, date: dt.date) -> str | None:
    """Find the exact filename of the archive product for one tile+day by
    scraping the plain directory listing page (filenames embed an
    unpredictable production timestamp, so can't be constructed directly).

    NOTE (2026-08-05): the documented `api/v2/content/details` query
    (products/collections/dateRanges/areaOfInterest params) returns HTTP 200
    with an always-empty `content: []` regardless of params tried -- verified
    directly, not just inferred (dropped areaOfInterest entirely, still
    empty; tried `x26y6` tile syntax, still empty) -- so that endpoint is
    either deprecated or needs an undocumented param shape. Confirmed by
    hand that the plain directory listing HTML at the URL below *does*
    contain the real filenames (e.g. `MCDWD_L3.A2020194.h26v06.061.<ts>.hdf`
    found for the 2020-07-12 smoke-test date), so this scrapes that instead
    -- same "plain unauthenticated/authenticated directory listing" pattern
    already used successfully for GFMS and CHIRPS elsewhere in this project.

    Deliberately a plain stateless `requests.get`, not a shared Session --
    see download_hdf's docstring for why (2026-08-06 incident: a Session that
    had been through a failed OAuth redirect chain started 401ing on *every*
    subsequent plain Bearer-token request, including this one).
    """
    doy = date.timetuple().tm_yday
    url = _dir_listing_url(date.year, doy)
    resp = requests.get(url, headers={"Authorization": f"Bearer {bearer_token}"}, timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(f"LAADS directory listing error {resp.status_code} for {tile} {date}: {resp.text[:500]}")
    import re
    files = set(re.findall(HDF_NAME_RE_TEMPLATE, resp.text))
    matches = sorted(f for f in files if f"A{date.year}{doy:03d}.{tile}." in f)
    if not matches:
        return None
    return matches[0]


def download_hdf(
    filename: str,
    tile: str,
    dest: Path,
    basic_auth: tuple[str, str],
    bearer_token: str,
) -> None:
    """Download one archive file. Unlike the directory-listing GETs (which
    work fine with just the Bearer token), the actual file bytes are served
    behind a legacy OAuth-app-authorization wrapper: GET archive-file-url ->
    303 -> /profiles/licenses/<same path> -> 302 -> /oauth/login -> 302 ->
    urs.earthdata.nasa.gov/oauth/authorize (this hop wants HTTP Basic
    username/password, NOT the Bearer token -- confirmed 2026-08-05 via
    curl/requests both reproducing the identical redirect-to-HTML-login
    result the officially-documented wget+Bearer command also hit) -> on
    success, a further redirect chain back through /oauth/callback to the
    original archive URL, which *then* serves the real bytes given the
    session cookie set along the way. So: follow redirects manually, keeping
    one Session (for cookie persistence across hosts *within this one
    file's chain only*) and switching which credential we present per-host
    at each hop.

    IMPORTANT (incident 2026-08-06): this Session is created fresh here,
    local to a single call, and discarded after -- it must NEVER be shared
    across multiple downloads or with find_file_for_day's listing requests.
    The first full backfill run passed in one long-lived Session shared
    across the whole run; after a single download hit the OAuth hop badly
    (ended the 10-hop loop without reaching a final 200), every subsequent
    request made through that same Session -- including plain Bearer-token
    directory listings that had been working fine for 95 prior days --
    started 401ing, and never recovered (19 failures in the next 9 days
    before this was caught and the run stopped). A brand-new Session against
    the same URL immediately after confirmed the token itself was still
    valid; the shared Session had picked up some bad cookie/auth state
    (most likely from the failed urs.earthdata.nasa.gov hop) that poisoned
    every later request on that Session, on any host. Isolating each
    download to its own throwaway Session (and find_file_for_day to a
    session-less plain request) makes that failure mode structurally
    impossible: one bad file can only ever cost that one file."""
    session = requests.Session()
    year = filename.split(".A")[1][:4]
    doy = filename.split(".A")[1][4:7]
    url = f"{LAADS_BASE}/archive/allData/{COLLECTION}/{ARCHIVE_PRODUCT}/{year}/{doy}/{filename}"

    cur = url
    resp = None
    for _ in range(10):
        from urllib.parse import urlparse
        host = urlparse(cur).hostname
        if host == "urs.earthdata.nasa.gov":
            resp = session.get(cur, auth=basic_auth, timeout=60, allow_redirects=False)
        else:
            resp = session.get(cur, headers={"Authorization": f"Bearer {bearer_token}"}, timeout=60, allow_redirects=False)
        if resp.status_code in (301, 302, 303) and resp.headers.get("location"):
            loc = resp.headers["location"]
            if loc.startswith("/"):
                base = urlparse(cur)
                loc = f"{base.scheme}://{base.netloc}{loc}"
            cur = loc
            continue
        break

    if resp is None or resp.status_code != 200:
        raise RuntimeError(f"Download failed for {filename}: final status {resp.status_code if resp else '?'} at {cur}")
    if resp.headers.get("content-type", "").startswith("text/html"):
        raise RuntimeError(f"Download for {filename} returned HTML, not the HDF file (auth/redirect chain broke): {resp.text[:300]}")

    partial = dest.with_suffix(dest.suffix + ".partial")
    partial.write_bytes(resp.content)
    partial.replace(dest)  # atomic, same crash-safety pattern as ingest_chirps.py


def read_flood_values(hdf_path: Path, pixels: dict[str, tuple[int, int]]) -> dict[str, dict[str, int]]:
    """Read FLOOD_LAYERS from an HDF4 file, return {station_id: {layer: value}}."""
    from pyhdf.SD import SD, SDC

    sd = SD(str(hdf_path), SDC.READ)
    result: dict[str, dict[str, int]] = {sid: {} for sid in pixels}
    for layer in FLOOD_LAYERS:
        try:
            dataset = sd.select(layer)
        except Exception as exc:
            print(f"  WARNING: layer {layer} not found in {hdf_path.name}: {exc}")
            continue
        arr = dataset.get()
        for sid, (row, col) in pixels.items():
            result[sid][layer] = int(arr[row, col])
        dataset.endaccess()
    sd.end()
    return result


def out_path(station: Station) -> Path:
    return OUT_DIR / f"mcdwd_{station.station_id}.csv"


MONSOON_MONTHS = (6, 7, 8, 9)

# Years where GFMS's Flood_byStor is actually accessible (see ingest_gfms.py
# module docstring: 2013-01..2016-03 and 2021-01..2026-02) intersected with
# monsoon season -- 2016 is excluded because GFMS's window that year ends in
# March, before monsoon starts, so there's no overlap to cross-validate.
GFMS_OVERLAP_MONSOON_YEARS = [2013, 2014, 2015, 2021, 2022, 2023, 2024, 2025]
MONSOON_FULL_YEARS = range(2003, 2026)
FULL_YEARS = range(2003, 2026)

CSV_FIELDS = ["date"] + FLOOD_LAYERS


def scope_dates(scope: str) -> list[dt.date]:
    if scope == "gfms-overlap":
        years, months = GFMS_OVERLAP_MONSOON_YEARS, MONSOON_MONTHS
    elif scope == "monsoon-full":
        years, months = MONSOON_FULL_YEARS, MONSOON_MONTHS
    elif scope == "full":
        years, months = FULL_YEARS, range(1, 13)
    else:
        raise ValueError(f"unknown --scope {scope!r}")
    dates = []
    for year in years:
        for month in months:
            n_days = calendar.monthrange(year, month)[1]
            dates.extend(dt.date(year, month, d) for d in range(1, n_days + 1))
    return sorted(dates)


def tile_of_station(station: Station) -> str:
    h, v = tile_of(station.lat, station.lon)
    return f"h{h:02d}v{v:02d}"


def load_existing(station: Station) -> dict[str, list[str]]:
    """Load already-written rows for a station, keyed by date string. Skips
    any row that isn't exactly len(CSV_FIELDS) columns with a valid ISO date
    in the first column -- same crash-safety discipline as
    ingest_gfms.py::last_date_in (a power cut mid-write must never be trusted
    as a valid entry, worst case we just re-fetch one day, which is harmless
    and idempotent)."""
    path = out_path(station)
    if not path.exists():
        return {}
    records: dict[str, list[str]] = {}
    with open(path, newline="") as f:
        reader = csv.reader(f)
        next(reader, None)  # header
        for row in reader:
            if len(row) != len(CSV_FIELDS):
                continue
            try:
                dt.date.fromisoformat(row[0])
            except ValueError:
                continue
            records[row[0]] = row
    return records


def write_station_csv(station: Station, records: dict[str, list[str]]) -> None:
    """Atomic full rewrite (temp + rename), sorted by date -- safe against a
    crash mid-write since out_path() only ever exists in a fully-valid state,
    same pattern as ingest_chirps.py's subset_and_save fix."""
    path = out_path(station)
    tmp = path.with_suffix(path.suffix + ".partial")
    with open(tmp, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_FIELDS)
        for date_str in sorted(records):
            writer.writerow(records[date_str])
    tmp.replace(path)


def run_smoke_test(basic_auth: tuple[str, str], bearer_token: str) -> None:
    """A few known-flood dates (per this project's earlier discharge/GFMS
    findings) for one station, to verify the whole path end-to-end before
    trusting a full backfill."""
    station = STATIONS[0]  # SW90 Bahadurabad
    tile_h, tile_v = tile_of(station.lat, station.lon)
    tile = f"h{tile_h:02d}v{tile_v:02d}"
    row, col = pixel_of(station.lat, station.lon, tile_h, tile_v)
    print(f"{station.station_id} ({station.name}) -> tile {tile}, pixel (row={row}, col={col})")

    test_dates = [
        dt.date(2020, 7, 12),   # documented 2020 Jamuna monsoon flood peak (discharge-verified earlier)
        dt.date(2020, 1, 15),   # dry season control, expect no flood
    ]
    for date in test_dates:
        print(f"\nQuerying {date}...")
        filename = find_file_for_day(bearer_token, tile, date)
        if filename is None:
            print(f"  no file found for {tile} {date} (archive gap or before/after coverage)")
            continue
        print(f"  found: {filename}")
        dest = OUT_DIR / "_smoke_test" / filename
        dest.parent.mkdir(parents=True, exist_ok=True)
        download_hdf(filename, tile, dest, basic_auth, bearer_token)
        values = read_flood_values(dest, {station.station_id: (row, col)})
        print(f"  values: {values[station.station_id]}")


def run_backfill(scope: str, force: bool, basic_auth: tuple[str, str], token: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Group stations by tile so we only fetch/download each tile-day once,
    # regardless of how many stations share it (2 tiles cover all 6 stations).
    pixels_by_tile: dict[str, dict[str, tuple[int, int]]] = {}
    stations_by_tile: dict[str, list[Station]] = {}
    for station in STATIONS:
        h, v = tile_of(station.lat, station.lon)
        tile = f"h{h:02d}v{v:02d}"
        row, col = pixel_of(station.lat, station.lon, h, v)
        pixels_by_tile.setdefault(tile, {})[station.station_id] = (row, col)
        stations_by_tile.setdefault(tile, []).append(station)

    dates = scope_dates(scope)
    print(f"Scope '{scope}': {len(dates)} target days, tiles={list(pixels_by_tile)}, "
          f"{len(STATIONS)} stations.")

    records: dict[str, dict[str, list[str]]] = {}  # station_id -> date_str -> row
    for station in STATIONS:
        records[station.station_id] = {} if force else load_existing(station)

    def tile_needs_date(tile: str, date_str: str) -> bool:
        return any(date_str not in records[s.station_id] for s in stations_by_tile[tile])

    tmp_dir = OUT_DIR / ".tmp_downloads"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    n_total = len(dates)
    n_done_dates = sum(
        1 for d in dates if not any(tile_needs_date(t, d.isoformat()) for t in pixels_by_tile)
    )
    print(f"Already have {n_done_dates}/{n_total} days fully covered across all stations, resuming rest.")

    n_processed = 0
    n_nofile = 0
    n_error = 0
    last_flush = time.monotonic()
    try:
        for date in dates:
            date_str = date.isoformat()
            for tile, pixels in pixels_by_tile.items():
                if not tile_needs_date(tile, date_str):
                    continue
                try:
                    filename = find_file_for_day(token, tile, date)
                    if filename is None:
                        values = None
                        n_nofile += 1
                    else:
                        dest = tmp_dir / filename
                        download_hdf(filename, tile, dest, basic_auth, token)
                        values = read_flood_values(dest, pixels)
                        dest.unlink(missing_ok=True)
                except Exception as exc:
                    print(f"\n  WARNING: {tile} {date_str} failed: {exc}")
                    values = None
                    n_error += 1
                for station in stations_by_tile[tile]:
                    if date_str in records[station.station_id]:
                        continue
                    if values is not None:
                        v = values[station.station_id]
                        row = [date_str] + [str(v.get(layer, "")) for layer in FLOOD_LAYERS]
                    else:
                        row = [date_str] + ["" for _ in FLOOD_LAYERS]
                    records[station.station_id][date_str] = row
                time.sleep(0.2)  # polite delay

            n_processed += 1
            if time.monotonic() - last_flush > 120 or date == dates[-1]:
                for station in STATIONS:
                    write_station_csv(station, records[station.station_id])
                last_flush = time.monotonic()
                pct = 100 * n_processed / n_total
                print(f"\r  {date_str}: {n_processed}/{n_total} days ({pct:.1f}%), "
                      f"{n_nofile} no-file, {n_error} errors", end="", flush=True)
    finally:
        for station in STATIONS:
            write_station_csv(station, records[station.station_id])
    print()
    print(f"Done (or stopped). Wrote up to {n_processed}/{n_total} target days for "
          f"{len(STATIONS)} stations under {OUT_DIR}. {n_nofile} no-file days, {n_error} errors.")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--smoke-test", action="store_true", help="run a small end-to-end verification and exit")
    parser.add_argument("--scope", default="gfms-overlap", choices=["gfms-overlap", "monsoon-full", "full"],
                         help="how much history to backfill (default: gfms-overlap, ~6h, see module docstring)")
    parser.add_argument("--force", action="store_true", help="ignore existing progress, refetch everything in scope")
    args = parser.parse_args()

    token = get_token()
    basic_auth = get_basic_auth()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if args.smoke_test:
        run_smoke_test(basic_auth, token)
        return

    run_backfill(args.scope, args.force, basic_auth, token)


if __name__ == "__main__":
    main()
