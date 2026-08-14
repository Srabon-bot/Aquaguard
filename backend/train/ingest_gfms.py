"""Download NASA GFMS (Global Flood Monitoring System) daily flood-intensity
and streamflow readings for our virtual gauge stations, for use as the
primary training label (Flood_byStor) and a secondary discharge feature (Q).
See MODEL_BUILD_PLAN.md Part 1c.

Source: http://eagle2.umd.edu/flood/download/<year>/<yearmonth>/<Var>_<yyyymmddhh>.bin
3-hourly, flat binary, 4-byte float, no header, global-ish grid:
  nrows=800, ncols=2458, xllcorner=-127.25, yllcorner=-50.0, cellsize=0.125,
  NoData=-9999. Confirmed via GFMS_readme.pdf and a verified sample file
  (2024/202407/Flood_byStor_2024070100.bin, exact expected size).

Row order empirically verified 2026-08-05 (not documented in the readme):
row 0 = north edge (lat=50N), row increases southward. Verified by checking
7 well-known river locations worldwide (Bahadurabad, Cairo/Nile, Amazon,
Mississippi, Mekong, Congo, Murray) against the sparse river-network grid --
the north-up hypothesis matched every location to within ~1-11 grid cells,
while the south-up hypothesis was off by 20-130+ cells everywhere except the
near-equatorial Amazon point (which is close to symmetric either way).

The Flood_byStor/Q grids are SPARSE (~2.6% of cells have real data -- only
river-network pixels are populated, everything else is legitimate NoData,
not a bug). Our stations' raw lat/lon don't land exactly on a river pixel,
so each station's nearest valid grid cell was calibrated once (2026-08-05,
against the same sample file) and hardcoded below -- this offset is a fixed
property of the static river network grid, not date-dependent, so it does
not need to be recalibrated per file. Use --recalibrate to redo this lookup
against a fresh sample file if the grid definition is ever suspected to have
changed.

Efficiency: instead of downloading each full ~7.8MB grid, we HTTP Range-fetch
only the contiguous row band spanning all 6 stations' calibrated rows (one
small request per day covers every station at once -- confirmed the server
supports byte-range requests, ~0.5s per request regardless of range size vs
~7s for a full download).

Only Flood_byStor is actually served by this archive -- empirically confirmed
2026-08-05 by listing several months' directories (2020-01, 2021-01, 2024-01,
2024-07, 2026-01): every one contains only `Flood_byStor_*.bin` files, despite
GFMS_readme.pdf documenting Q/Routed/V as available variables too (they may
exist in some other NASA product/portal, but not in this bulk download tree).
Not a blocker: Open-Meteo's Flood API (ingest_discharge.py) already covers
the discharge/streamflow role for Part 1c. So GFMS here supplies exactly one
thing -- the flood-intensity-above-threshold label -- which is also its most
important role per the plan (Part 3's primary label source).

Sampling: one reading/day at 00 UTC (not all 8 3-hourly timesteps) to keep
the backfill tractable. Matches Part 2's per-station-per-day table design.
GFMS's real-time feed stalled 2026-02-02 (see plan) so this is a
historical-only source; --end defaults to that cutoff.

IMPORTANT -- most of the "2001-2025" archive is NOT actually downloadable
(discovered 2026-08-05): despite every year/month appearing in the directory
listing, direct file access 403s for most of it. Empirically mapped by
probing one file per month across all 300 months 2001-2025: only 2013-2015,
Jan-Mar 2016, and 2021-2025 (~99 months, ~33%) return real data; everything
else (2001-2012, Apr 2016-2020) is a permanent 403 Forbidden, evidently a
server-side permissions/storage-tier restriction on UMD's end, not something
fixable from our side. This script probes month-by-month accessibility once
up front (one request per month, ~2-3 min for the full range) and skips
inaccessible months entirely rather than wasting a request per day on months
that will only ever 403 -- so the real usable historical window is roughly
2013-2016 (partial) + 2021-present, not the full 25 years originally hoped
for. Combined with CHIRPS (1981+) and Open-Meteo discharge (~1997+), this is
still the limiting factor on how far back the merged training table can go.

Usage:
    python train/ingest_gfms.py                      # full range, all stations, auto-skips inaccessible months
    python train/ingest_gfms.py --start 2021-01-01 --end 2021-12-31   # smoke test
    python train/ingest_gfms.py --recalibrate         # redo pixel-offset calibration only
    python train/ingest_gfms.py --probe-only          # just print the accessibility map and exit
"""

import argparse
import csv
import datetime as dt
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import requests

BASE_URL = "http://eagle2.umd.edu/flood/download"
OUT_DIR = Path(__file__).resolve().parent.parent / "data_raw" / "gfms"

NROWS, NCOLS = 800, 2458
XLLCORNER, YLLCORNER, CELLSIZE = -127.25, -50.0, 0.125
NODATA = -9999.0
BYTES_PER_VAL = 4

FIRST_DATE = "2001-01-01"
LAST_DATE = "2026-02-02"  # GFMS real-time feed confirmed stalled after this date
CALIBRATION_URL = f"{BASE_URL}/2024/202407/Flood_byStor_2024070100.bin"
CALIBRATION_SEARCH_PAD = 15  # grid cells (~1.9 deg) to search for nearest valid river pixel


sys.path.insert(0, str(Path(__file__).resolve().parent))
from stations import STATIONS as _BASE_STATIONS  # noqa: E402


@dataclass
class Station:
    station_id: str
    name: str
    lat: float
    lon: float
    row: int | None = None  # calibrated nearest-river-pixel grid row, filled in below
    col: int | None = None


# row/col are the *calibrated nearest river-network pixel*, not the raw
# lat/lon-derived cell (see module docstring). Original 6 computed 2026-08-05
# against CALIBRATION_URL with CALIBRATION_SEARCH_PAD=15, all resolved within
# 7 cells. Extended to all 30 stations (train/stations.py) on 2026-08-07 --
# the 24 new ones' row/col were (re-)computed the same way via `calibrate()`
# and hardcoded here (station names/lat/lon now come from the shared
# train/stations.py so there's one source of truth for coordinates; row/col
# stay GFMS-specific since no other script needs them).
_CALIBRATED_ROWCOL: dict[str, tuple[int, int]] = {
    "SW90": (197, 1736), "SW93": (197, 1736), "SW99": (198, 1738), "SW17": (195, 1736),
    "SW267": (199, 1749), "SW174": (200, 1752),
    # 2026-08-07 additions, from `python train/ingest_gfms.py --recalibrate`
    # against the same CALIBRATION_URL -- all resolved within <=6.71 cells
    # (most <=2), original 6 re-verified to match their existing values above
    # exactly, confirming the stations.py refactor didn't change anything.
    "TE01": (192, 1734), "TE02": (193, 1734), "OB01": (198, 1742), "DH01": (193, 1734),
    "GA01": (210, 1729), "GA02": (215, 1734), "GA03": (215, 1741), "GA04": (210, 1744),
    "GO01": (210, 1729), "GO02": (216, 1735),
    "ME01": (215, 1741), "ME02": (205, 1746), "ME03": (210, 1744),
    "KU01": (201, 1752), "KU02": (202, 1755), "NM01": (198, 1743),
    "CH01": (218, 1755), "CH02": (222, 1755), "CH03": (219, 1752),
    "CO01": (218, 1739), "CO02": (217, 1733), "CO03": (218, 1736), "CO04": (220, 1739),
    "CO05": (228, 1754),
}

STATIONS: list[Station] = [
    Station(s.station_id, s.name, s.lat, s.lon,
            row=_CALIBRATED_ROWCOL.get(s.station_id, (None, None))[0],
            col=_CALIBRATED_ROWCOL.get(s.station_id, (None, None))[1])
    for s in _BASE_STATIONS
]

VARIABLES = ["Flood_byStor"]  # only variable actually served by this archive -- see module docstring


def row_of(lat: float) -> int:
    """North-up: row 0 = north edge (lat=50N), row increases southward."""
    return int((YLLCORNER + NROWS * CELLSIZE - lat) / CELLSIZE)


def col_of(lon: float) -> int:
    return int((lon - XLLCORNER) / CELLSIZE)


def file_url(variable: str, timestamp: dt.datetime) -> str:
    year = timestamp.strftime("%Y")
    yearmonth = timestamp.strftime("%Y%m")
    stamp = timestamp.strftime("%Y%m%d%H")
    return f"{BASE_URL}/{year}/{yearmonth}/{variable}_{stamp}.bin"


def calibrate() -> None:
    """Redo the nearest-valid-river-pixel lookup for every station against a
    fresh sample file and print the results (does not modify this file)."""
    print(f"Calibrating against {CALIBRATION_URL} ...")
    resp = requests.get(CALIBRATION_URL, timeout=60)
    resp.raise_for_status()
    grid = np.frombuffer(resp.content, dtype=np.float32).reshape(NROWS, NCOLS)

    for station in STATIONS:
        r0, c0 = row_of(station.lat), col_of(station.lon)
        pad = CALIBRATION_SEARCH_PAD
        r_lo, r_hi = max(0, r0 - pad), min(NROWS, r0 + pad + 1)
        c_lo, c_hi = max(0, c0 - pad), min(NCOLS, c0 + pad + 1)
        window = grid[r_lo:r_hi, c_lo:c_hi]
        mask = window != NODATA
        if not mask.any():
            print(f"  {station.station_id}: NO valid cell found within +-{pad} of raw (row={r0},col={c0})")
            continue
        rc = np.argwhere(mask)
        cy, cx = r0 - r_lo, c0 - c_lo
        dists = np.sqrt((rc[:, 0] - cy) ** 2 + (rc[:, 1] - cx) ** 2)
        i = dists.argmin()
        abs_r, abs_c = r_lo + rc[i, 0], c_lo + rc[i, 1]
        print(f"  {station.station_id}: raw (row={r0},col={c0}) -> nearest valid "
              f"(row={abs_r},col={abs_c}), dist={dists.min():.2f} cells, val={window[tuple(rc[i])]:.4g}")


def probe_month(year: int, month: int) -> bool:
    """Cheap accessibility check: try a 100-byte range fetch of the 1st-of-month
    00 UTC file. Returns True if the month is actually downloadable (200/206),
    False for 403 (the observed restricted-archive case) or 404/error."""
    url = file_url("Flood_byStor", dt.datetime(year, month, 1, 0))
    try:
        resp = requests.get(url, headers={"Range": "bytes=0-99"}, timeout=15)
        return resp.status_code in (200, 206)
    except requests.RequestException:
        return False


def probe_accessible_months(start_date: dt.date, end_date: dt.date) -> set[tuple[int, int]]:
    """Probe every (year, month) in [start_date, end_date] once and return the
    set of months that are actually downloadable. See module docstring --
    most of the nominal 2001-2025 archive 403s despite being listed."""
    months: list[tuple[int, int]] = []
    y, m = start_date.year, start_date.month
    while (y, m) <= (end_date.year, end_date.month):
        months.append((y, m))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)

    print(f"Probing accessibility of {len(months)} months (1 request/month)...")
    accessible: set[tuple[int, int]] = set()
    for i, (yr, mo) in enumerate(months):
        if probe_month(yr, mo):
            accessible.add((yr, mo))
        if (i + 1) % 24 == 0 or (yr, mo) == months[-1]:
            print(f"\r  probed {i + 1}/{len(months)} months, {len(accessible)} accessible so far", end="", flush=True)
        time.sleep(0.1)
    print()

    # Summarize as contiguous ranges for readability.
    ranges = []
    sorted_months = sorted(accessible)
    for ym in sorted_months:
        if ranges and ranges[-1][1] == ((ym[0], ym[1] - 1) if ym[1] > 1 else (ym[0] - 1, 12)):
            ranges[-1] = (ranges[-1][0], ym)
        else:
            ranges.append((ym, ym))
    print(f"Accessible: {len(accessible)}/{len(months)} months. Ranges: "
          + ", ".join(f"{a[0]}-{a[1]:02d}..{b[0]}-{b[1]:02d}" for a, b in ranges))
    return accessible


def out_path(station: Station) -> Path:
    return OUT_DIR / f"gfms_{station.station_id}.csv"


def last_date_in(path: Path) -> str | None:
    """Return the last row's date, skipping a malformed trailing row -- e.g. a
    power cut mid-write can leave the final CSV line truncated (missing its
    second field or newline). A truncated row must never be trusted as a
    valid resume point (worst case we just re-fetch one already-written day,
    which is harmless and idempotent)."""
    if not path.exists():
        return None
    last = None
    with open(path, newline="") as f:
        reader = csv.reader(f)
        next(reader, None)  # header
        for row in reader:
            if len(row) != 2:
                continue
            try:
                dt.date.fromisoformat(row[0])
            except ValueError:
                continue
            last = row[0]
    return last


def fetch_row_band(variable: str, timestamp: dt.datetime, row_lo: int, row_hi: int) -> np.ndarray | None:
    """Range-fetch the contiguous row band [row_lo, row_hi] (inclusive) for one
    variable's grid file at one timestamp. Returns a (row_hi-row_lo+1, NCOLS)
    float32 array, or None if the file doesn't exist / fetch failed."""
    url = file_url(variable, timestamp)
    byte_start = row_lo * NCOLS * BYTES_PER_VAL
    byte_end = (row_hi + 1) * NCOLS * BYTES_PER_VAL - 1
    try:
        resp = requests.get(url, headers={"Range": f"bytes={byte_start}-{byte_end}"}, timeout=30)
        if resp.status_code not in (200, 206):
            return None
        arr = np.frombuffer(resp.content, dtype=np.float32)
        expected = (row_hi - row_lo + 1) * NCOLS
        if arr.size != expected:
            return None
        return arr.reshape(row_hi - row_lo + 1, NCOLS)
    except requests.RequestException:
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--start", default=FIRST_DATE)
    parser.add_argument("--end", default=LAST_DATE)
    parser.add_argument("--force", action="store_true", help="ignore existing progress, refetch from --start")
    parser.add_argument("--recalibrate", action="store_true", help="only redo the pixel-offset calibration and exit")
    parser.add_argument("--probe-only", action="store_true", help="only print the month-accessibility map and exit")
    args = parser.parse_args()

    if args.recalibrate:
        calibrate()
        return

    start_date = dt.date.fromisoformat(args.start)
    end_date = dt.date.fromisoformat(args.end)

    accessible_months = probe_accessible_months(start_date, end_date)
    if args.probe_only:
        return
    if not accessible_months:
        print("No accessible months in this range -- nothing to fetch.")
        return

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    row_lo = min(s.row for s in STATIONS)
    row_hi = max(s.row for s in STATIONS)
    print(f"Row band for all stations: rows {row_lo}-{row_hi} "
          f"({(row_hi - row_lo + 1) * NCOLS * BYTES_PER_VAL} bytes/request)")

    # Resume: find the latest common date already written across all station
    # files (the min of their last dates), start the day after that.
    existing_last_dates = [last_date_in(out_path(s)) for s in STATIONS]
    if args.force or not all(existing_last_dates):
        # (re)write headers fresh
        for station in STATIONS:
            with open(out_path(station), "w", newline="") as f:
                csv.writer(f).writerow(["date", "flood_byStor"])
    else:
        resume_from = min(dt.date.fromisoformat(d) for d in existing_last_dates)
        start_date = resume_from + dt.timedelta(days=1)
        print(f"Resuming from {start_date} (found existing progress in {OUT_DIR})")

    if start_date > end_date:
        print("Nothing to do -- already up to date.")
        return

    files = {station.station_id: open(out_path(station), "a", newline="") for station in STATIONS}
    writers = {sid: csv.writer(f) for sid, f in files.items()}

    n_days = (end_date - start_date).days + 1
    day = start_date
    n_done = 0
    n_missing = 0
    n_skipped_inaccessible = 0
    try:
        while day <= end_date:
            if (day.year, day.month) not in accessible_months:
                # Known-inaccessible month (see module docstring) -- write a
                # blank row without spending a request on it.
                for station in STATIONS:
                    writers[station.station_id].writerow([day.isoformat(), ""])
                n_skipped_inaccessible += 1
                n_done += 1
                day += dt.timedelta(days=1)
                continue

            timestamp = dt.datetime(day.year, day.month, day.day, 0)
            per_var_bands: dict[str, np.ndarray | None] = {}
            for variable in VARIABLES:
                per_var_bands[variable] = fetch_row_band(variable, timestamp, row_lo, row_hi)
                time.sleep(0.15)  # polite delay, no key/quota to throttle us

            if all(band is None for band in per_var_bands.values()):
                n_missing += 1

            for station in STATIONS:
                flood_val = ""
                band = per_var_bands.get("Flood_byStor")
                if band is not None:
                    v = band[station.row - row_lo, station.col]
                    flood_val = "" if v == NODATA else float(v)
                writers[station.station_id].writerow([day.isoformat(), flood_val])

            n_done += 1
            if n_done % 50 == 0 or day == end_date:
                for f in files.values():
                    f.flush()
                pct = 100 * n_done / n_days
                print(f"\r  {day.isoformat()}: {n_done}/{n_days} days ({pct:.1f}%), "
                      f"{n_missing} fully-missing days, {n_skipped_inaccessible} skipped (inaccessible month)", end="", flush=True)

            day += dt.timedelta(days=1)
    finally:
        for f in files.values():
            f.close()
    print()
    print(f"Done. Wrote up to {end_date} for {len(STATIONS)} stations under {OUT_DIR}. "
          f"{n_missing} fetched days had no data (archive gaps), "
          f"{n_skipped_inaccessible} days skipped entirely (inaccessible month).")


if __name__ == "__main__":
    main()
