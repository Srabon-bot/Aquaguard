"""Download historical rainfall AND soil moisture for our virtual gauge
stations (local point) and their upstream catchments (sampled grid) via
Open-Meteo's free Historical Weather API (ERA5/ERA5-Land reanalysis).

Why this replaces CHIRPS as the primary rainfall source (see
MODEL_BUILD_PLAN.md Part 1b, decided 2026-08-07):
  - Same free/no-key/no-registration trust profile as the discharge API
    already in use (flood-api.open-meteo.com) and the live rainfall API
    already wired into app/services/weather.py -- one provider, one pattern,
    for everything.
  - Longer history: ERA5-Land goes back to 1950 (CHIRPS: 1981).
  - Point-based JSON, not global gridded netCDF -- no multi-GB per-year
    downloads, no xarray subsetting, and critically, no dependency on
    data.chc.ucsb.edu, which got our IP CrowdSec-banned (see plan log,
    2026-08-05/07) with no ETA on when/if it clears.
  - Bonus: the SAME endpoint also serves soil moisture (4 depths, 1950+),
    which CHIRPS never had. Soil moisture (antecedent wetness) is a
    top-cited flood driver in the Bangladesh-specific ML literature and was
    completely absent from this pipeline before now.
  - Supports multiple lat/lon points in a single request (comma-separated),
    so the whole 76-year, 24-point pull below takes ~8 requests total, not
    thousands.

Source: https://archive-api.open-meteo.com/v1/archive
Variables pulled: precipitation_sum, soil_moisture_0_to_7cm_mean (daily).
0-7cm depth chosen because it's the layer most directly relevant to
immediate runoff response, and it's what a shallow-buried IoT soil
moisture probe (see plan Part 5b) would actually measure -- keeping the
trained feature's depth/units consistent with what the live sensor will
eventually report matters more than picking a deeper, slower-changing layer.

Points fetched:
  - 25 "local" points: the real public lat/lon of each virtual station, see
    train/stations.py (expanded from 6 to 25 on 2026-08-07 for full-Bangladesh
    coverage -- see MODEL_BUILD_PLAN.md Part 1/2).
  - Upstream catchment points: a 3x3 sample grid across each basin's
    upstream bounding box (train/stations.py's UPSTREAM_BOXES, one per basin:
    brahmaputra/ganges/meghna/cht) -- averaged client-side per basin at merge
    time (build_dataset.py) to approximate an area-mean, since this point
    API has no true raster/area-integral mode.

Usage:
    python train/ingest_openmeteo_historical.py                # everything, full history
    python train/ingest_openmeteo_historical.py --start 2015-01-01 --end 2022-12-31
    python train/ingest_openmeteo_historical.py --point-id SW90_local
"""

import argparse
import csv
import datetime as dt
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stations import STATIONS, UPSTREAM_BOXES, upstream_points  # noqa: E402

BASE_URL = "https://archive-api.open-meteo.com/v1/archive"
OUT_DIR = Path(__file__).resolve().parent.parent / "data_raw" / "openmeteo_weather"

FIRST_DATE = "1950-01-01"  # ERA5-Land start; API returns nulls before real coverage if any
DAILY_VARS = "precipitation_sum,soil_moisture_0_to_7cm_mean"


@dataclass
class Point:
    point_id: str
    lat: float
    lon: float
    role: str  # "local" | "upstream"
    basin: str  # "brahmaputra" | "ganges" | "meghna" | "cht" -- which upstream-average group this belongs to


def build_points() -> list[Point]:
    points = [
        Point(f"{s.station_id}_local", s.lat, s.lon, "local", s.basin)
        for s in STATIONS
    ]
    for basin in UPSTREAM_BOXES:
        for i, (lat, lon) in enumerate(upstream_points(basin, n=3)):
            points.append(Point(f"{basin}_upstream_{i}", lat, lon, "upstream", basin))
    return points


def out_path(point: Point) -> Path:
    return OUT_DIR / f"{point.point_id}.csv"


def fetch_batch(points: list[Point], start: str, end: str) -> dict[str, tuple[list[str], list, list]]:
    """One request, all points at once (Open-Meteo's multi-coordinate mode).
    Returns {point_id: (dates, precip, soil_moisture)}."""
    lats = ",".join(str(p.lat) for p in points)
    lons = ",".join(str(p.lon) for p in points)
    params = {
        "latitude": lats,
        "longitude": lons,
        "start_date": start,
        "end_date": end,
        "daily": DAILY_VARS,
        "timezone": "UTC",
    }
    resp = requests.get(BASE_URL, params=params, timeout=180)
    resp.raise_for_status()
    payload = resp.json()
    # Single-point requests return a dict; multi-point return a list in the
    # same order as the input lat/lon lists -- normalize to a list either way.
    results = payload if isinstance(payload, list) else [payload]
    out = {}
    for point, result in zip(points, results):
        daily = result.get("daily", {})
        out[point.point_id] = (
            daily.get("time", []),
            daily.get("precipitation_sum", []),
            daily.get("soil_moisture_0_to_7cm_mean", []),
        )
    return out


def last_date_in(path: Path) -> str | None:
    """Last valid ISO date already on disk for this point, skipping any
    truncated trailing row from a crash mid-write (same discipline as
    ingest_gfms.py's last_date_in) -- BUT ALSO requires every day between the
    first and last row to actually be present, with no gap. Trusting only
    the last row's date (the original version of this function) is not
    enough: a real run hit a mid-backfill crash + resume that left a whole
    decade silently missing from the *middle* of several files while the
    last row still looked perfectly valid, so a "resume from the last date"
    check alone would have accepted the gap forever, permanently corrupting
    that point's data with no error ever surfacing. If any gap is found, we
    don't try to be clever about patching just the hole -- return None so
    the caller does a full, guaranteed-contiguous refetch for this point
    instead (cheap: a few requests, not worth the complexity of partial
    gap-filling)."""
    if not path.exists():
        return None
    dates: list[str] = []
    with open(path, newline="") as f:
        reader = csv.reader(f)
        next(reader, None)  # header
        for row in reader:
            if len(row) >= 1:
                try:
                    dt.date.fromisoformat(row[0])
                    dates.append(row[0])
                except ValueError:
                    continue  # truncated trailing row from a crash mid-write
    if not dates:
        return None
    prev = dt.date.fromisoformat(dates[0])
    for d in dates[1:]:
        cur = dt.date.fromisoformat(d)
        if (cur - prev).days != 1:
            print(f"  WARNING: gap detected in {path.name} between {prev} and {cur} -- "
                  f"forcing a full refetch for this point rather than trusting a corrupt resume point")
            return None
        prev = cur
    return dates[-1]


def write_point_csv(path: Path, rows: list[tuple[str, str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_suffix(path.suffix + ".partial")
    with open(partial, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "precipitation_sum", "soil_moisture_0_to_7cm_mean"])
        writer.writerows(rows)
    # Atomic rename -- see ingest_chirps.py's crash-safety fix for why. On
    # Windows this occasionally raises PermissionError/WinError 5 even when
    # nothing is actually wrong, because a brief transient handle (AV
    # real-time scan, search indexer) can hold the destination file open for
    # a few milliseconds right after it's written -- confirmed by hitting
    # this once in testing with no other explanation (no other process of
    # ours touches these files, and the retry always succeeds within one or
    # two attempts). Retry with backoff instead of letting one flaky rename
    # kill an hours-long backfill.
    for attempt in range(5):
        try:
            partial.replace(path)
            return
        except PermissionError:
            if attempt == 4:
                raise
            time.sleep(0.5 * (attempt + 1))


def main():
    today = dt.date.today().isoformat()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--start", default=FIRST_DATE)
    parser.add_argument("--end", default=today)
    parser.add_argument("--point-id", help="only fetch this one point, e.g. SW90_local")
    parser.add_argument("--force", action="store_true", help="redownload points that already have output")
    args = parser.parse_args()

    all_points = build_points()
    points = all_points
    if args.point_id:
        points = [p for p in all_points if p.point_id == args.point_id]
        if not points:
            raise SystemExit(f"Unknown point_id: {args.point_id}")

    print(f"{len(points)} point(s) to fetch: {sum(1 for p in points if p.role=='local')} local, "
          f"{sum(1 for p in points if p.role=='upstream')} upstream")

    # Resume: each point has its own resume start date (day after its last
    # on-disk date, or --start if fresh/--force). Points are grouped by that
    # shared start date so they can still be fetched together in one batched
    # request per chunk (the common case: a fresh run, or a clean resume
    # where every point stalled at the same point) -- WITHOUT ever refetching
    # a date range a point already has on disk, which would silently write
    # duplicate rows (caught in testing: resuming with the old chunk-vs-whole
    # -range logic re-fetched and duplicated already-saved years).
    existing: dict[str, list[tuple[str, str, str]]] = {}
    resume_groups: dict[str, list[Point]] = {}
    for p in points:
        path = out_path(p)
        if args.force or not path.exists():
            existing[p.point_id] = []
            resume_groups.setdefault(args.start, []).append(p)
            continue
        last = last_date_in(path)
        if last is not None and last >= args.end:
            print(f"[{p.point_id}] already have data through {last}, skipping (use --force to redo)")
            continue
        if last is None:
            # Either no valid rows at all, or last_date_in found a gap and
            # deliberately returned None to force a full redo (see its
            # docstring) -- either way, don't preserve the existing file's
            # rows or we'd duplicate the parts that were actually fine once
            # the full refetch below re-adds them from args.start.
            existing[p.point_id] = []
            resume_groups.setdefault(args.start, []).append(p)
            continue
        with open(path, newline="") as f:
            reader = csv.reader(f)
            next(reader, None)
            existing[p.point_id] = [tuple(row) for row in reader if row]
        own_start = (dt.date.fromisoformat(last) + dt.timedelta(days=1)).isoformat()
        resume_groups.setdefault(own_start, []).append(p)

    if not resume_groups:
        print("Nothing to do -- all points already up to date.")
        return

    for group_start, group_points in resume_groups.items():
        if group_start > args.end:
            continue
        start_year = int(group_start[:4])
        end_year = int(args.end[:4])
        for chunk_start_year in range(start_year, end_year + 1, 10):
            chunk_end_year = min(chunk_start_year + 9, end_year)
            chunk_start = f"{chunk_start_year}-01-01" if chunk_start_year != start_year else group_start
            chunk_end = f"{chunk_end_year}-12-31" if chunk_end_year != end_year else args.end

            print(f"[{chunk_start}..{chunk_end}] fetching {len(group_points)} point(s)...")
            # Retry transient failures (429 rate-limit, timeouts) with
            # backoff instead of silently skipping the chunk -- a real run
            # hit a 429 on one chunk, which the old skip-and-move-on logic
            # turned into a permanent, silent 10-year gap in the final data
            # (caught by chance, not by any error surfacing -- see plan log
            # 2026-08-07). A skipped chunk is never retried automatically by
            # a later run either, since resume logic only looks at whether
            # data exists, not whether it's complete -- so this has to be
            # handled here, not left to "just rerun the script."
            batch = None
            for attempt in range(5):
                try:
                    batch = fetch_batch(group_points, chunk_start, chunk_end)
                    break
                except requests.RequestException as exc:
                    wait = 5 * (attempt + 1)
                    print(f"  chunk request failed (attempt {attempt + 1}/5): {exc}")
                    if attempt == 4:
                        print(f"  giving up on this chunk after 5 attempts -- "
                              f"this WILL leave a gap, rerun the script afterward to fill it "
                              f"(the gap-detection fix will catch it on the next run)")
                        break
                    print(f"  retrying in {wait}s...")
                    time.sleep(wait)
            if batch is None:
                continue

            for p in group_points:
                dates, precip, soil = batch[p.point_id]
                new_rows = [
                    (d, "" if pr is None else pr, "" if sm is None else sm)
                    for d, pr, sm in zip(dates, precip, soil)
                ]
                existing[p.point_id].extend(new_rows)
                n_real = sum(1 for r in new_rows if r[1] != "")
                print(f"  {p.point_id}: +{len(new_rows)} days ({n_real} with real precip)")

            # Atomic full-file rewrite after every chunk, not just at the end
            # -- so a crash mid-backfill loses at most one chunk's worth of
            # progress, same crash-safety discipline as ingest_mcdwd.py.
            for p in group_points:
                write_point_csv(out_path(p), existing[p.point_id])

            time.sleep(0.5)  # polite anonymous client

    for group_points in resume_groups.values():
        for p in group_points:
            rows = existing.get(p.point_id)
            if rows:
                print(f"[{p.point_id}] {out_path(p)}: {len(rows)} rows total")


if __name__ == "__main__":
    main()
