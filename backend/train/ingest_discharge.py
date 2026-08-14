"""Download historical river discharge (GloFAS v4 reanalysis) for our virtual
gauge stations via Open-Meteo's free Flood API, since real BWDB gauge history
is a paid product (see MODEL_BUILD_PLAN.md Part 1a/1c decision).

Source: https://flood-api.open-meteo.com/v1/flood
Free, no API key for non-commercial use, no documented rate limit. Real
coverage confirmed from ~late 1990s (1998 mega-flood present, 1990 is null)
through present + short forecast. One JSON call per station covering the
full date range (the API accepts arbitrarily long start/end windows), so no
temp-file/subset dance is needed like CHIRPS.

Usage:
    python train/ingest_discharge.py                # all stations, full history
    python train/ingest_discharge.py --start 2015-01-01 --end 2022-12-31
    python train/ingest_discharge.py --station-id SW90
"""

import argparse
import csv
import datetime as dt
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stations import STATIONS, Station, UPSTREAM_REFERENCE_STATIONS  # noqa: E402

BASE_URL = "https://flood-api.open-meteo.com/v1/flood"
OUT_DIR = Path(__file__).resolve().parent.parent / "data_raw" / "discharge"

FIRST_DATE = "1990-01-01"  # earliest requested; API returns null until real coverage starts

# GloFAS (the model behind Open-Meteo's Flood API) is a ~0.05 deg grid. The
# real gauge coordinates in stations.py are fine for nearest-station distance
# matching (ffwc.py's use case) but can land on the wrong grid cell for
# discharge extraction -- a braid channel or minor tributary near a
# confluence instead of the actual main channel -- giving implausibly tiny
# discharge. Found 2026-08-07 via train/snap_discharge_grid.py for the
# original 6: SW90/SW99/SW17 (Jamuna) agree at ~20-22k m3/s mean; SW93's raw
# coords read ~2 m3/s, SW174 read ~11 vs SW267's ~570-680 (same river,
# Surma). Grid search found nearby cells matching the expected order of
# magnitude for both. SW267 was checked too and is fine (barely moved,
# 571->657) -- Surma genuinely carries less flow than Jamuna.
# When the station list expanded to 30 (2026-08-07), re-ran the same
# grid-search tool against all 24 new stations before trusting their
# discharge coordinates. IMPORTANT judgment call made while reviewing those
# results (see DECISIONS.md): the tool's heuristic ("pick whichever nearby
# cell has the highest mean discharge") can be WRONG for a tributary that
# joins a much bigger river close to the station -- it can walk the point
# onto the big parent river's channel instead of genuinely finding the
# tributary's own flow. Caught this for DH01 (Dharla) and GO01 (Gorai): both
# "best" cells matched the neighboring Jamuna/Ganges MAINSTEM's discharge
# magnitude almost exactly, which would misrepresent a smaller distributary
# as if it carried the full parent river's flow. Deliberately did NOT apply
# an override for those two -- their low raw-coordinate discharge values are
# kept as the lesser evil (possibly a minor channel, but at least not
# actively wrong in a different way), flagged here for future manual
# verification against a real river map rather than trusted either way.
GLOFAS_COORD_OVERRIDE: dict[str, tuple[float, float]] = {
    "SW93": (24.745, 89.647),   # orig (24.8952, 89.5975) -> mean 2 to 21,852 m3/s
    "SW174": (24.745, 91.919),  # orig (24.8949, 91.8687) -> mean 11 to 1,328 m3/s
    "TE01": (25.767, 89.433),   # orig (25.9167, 89.2833) -> mean 3.9 to 1,090.6 m3/s (Teesta)
    "GA01": (24.071, 88.979),   # orig (24.0708, 89.0294) -> mean 0.9 to 14,215.4 m3/s (Ganges mainstem)
    "GA02": (23.767, 89.733),   # orig (23.7167, 89.7833) -> mean 0.7 to 36,857.9 m3/s (Jamuna-Ganges confluence)
    "GA04": (23.467, 90.117),   # orig (23.5167, 90.2667) -> mean 2.1 to 36,866.6 m3/s (Padma mainstem, matches GA03)
    "GO02": (22.867, 89.876),   # orig (23.0167, 89.8265) -> mean 1.9 to 94.7 m3/s (Madhumati, plausible distributary scale)
    "ME01": (23.233, 90.567),   # orig (23.2333, 90.6667) -> mean 68 to 41,292.4 m3/s (Padma-Meghna confluence -- genuinely the biggest point in the whole system)
    "ME02": (24.100, 91.033),   # orig (24.05, 90.9833) -> mean 2.5 to 3,509.9 m3/s (upper Meghna mainstem, between Surma/Kushiyara and the confluence -- right order of magnitude)
    "KU02": (24.867, 92.050),   # orig (24.8167, 92.2) -> mean 6.2 to 1,227.8 m3/s (matches KU01's Kushiyara magnitude ~1329)
    "NM01": (25.000, 90.583),   # orig (25.15, 90.7333) -> mean 6.7 to 312.9 m3/s (Someshwari, plausible smaller haor tributary)
    "CH01": (22.483, 92.033),   # orig (22.6333, 92.1833) -> mean 250 to 293.7 m3/s (Karnaphuli, modest correction)
    "CH02": (22.195, 92.068),   # orig (22.1953, 92.2183) -> mean 64.9 to 74.8 m3/s (Sangu, modest correction)
    "CH03": (22.350, 91.750),   # orig (22.5, 91.85) -> mean 1.2 to 394.3 m3/s (Halda, comparable order to neighboring Karnaphuli)
    "CO01": (22.551, 90.504),   # orig (22.701, 90.3535) -> mean 0.75 to 25.9 m3/s (Kirtankhola, plausible coastal-river scale)
    "CO02": (22.746, 89.490),   # orig (22.8456, 89.5403) -> mean 182.7 to 209.6 m3/s (Rupsha, modest correction)
    "CO03": (22.760, 89.940),   # orig (22.6602, 89.7895) -> mean 0.9 to 100.3 m3/s (Baleswar, plausible coastal-river scale)
    "CO04": (22.210, 90.180),   # orig (22.3596, 90.3296) -> mean 2.7 to 27.7 m3/s (Payra, plausible coastal-river scale)
    "CO05": (21.477, 91.906),   # orig (21.4272, 92.0058) -> mean 21.6 to 27.7 m3/s (Bakkhali, modest correction)
    # NOT overridden (see note above): DH01, GO01, ME03 -- "best" cell found
    # was actually the neighboring mainstem river, not the station's own
    # river -- most notable for ME03, since that station exists specifically
    # to represent Dhaka's OWN local hydrology (Buriganga), and forcing it
    # onto the nearby Padma/Dhaleshwari mainstem's much larger flow would
    # defeat that purpose entirely. Flagged for future manual verification.
}


def query_coords(station: Station) -> tuple[float, float]:
    return GLOFAS_COORD_OVERRIDE.get(station.station_id, (station.lat, station.lon))


def out_path(station: Station) -> Path:
    return OUT_DIR / f"discharge_{station.station_id}.csv"


def fetch_discharge(station: Station, start: str, end: str) -> tuple[list[str], list[float | None]]:
    lat, lon = query_coords(station)  # applies GLOFAS_COORD_OVERRIDE when this station needs it --
    # NOTE: this was a real bug until 2026-08-07 -- query_coords() existed and
    # GLOFAS_COORD_OVERRIDE was correctly identified via snap_discharge_grid.py,
    # but was never actually called here, so fetch_discharge() silently kept
    # using the raw (off-channel, wrong-magnitude) coordinates the whole time.
    # Confirmed by checking the already-downloaded discharge_SW93.csv on disk:
    # it read ~1.7 m3/s mean for 2019, matching the KNOWN-BROKEN value, not
    # the corrected ~21,852 the override was supposed to produce. Caught while
    # extending this script for the 25-station expansion, not by the original
    # "verified plausible values" smoke test, which apparently only checked
    # SW90 (whose coordinates were fine, so it wouldn't have caught this).
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "river_discharge",
        "start_date": start,
        "end_date": end,
    }
    resp = requests.get(BASE_URL, params=params, timeout=30)
    resp.raise_for_status()
    payload = resp.json()
    daily = payload.get("daily", {})
    return daily.get("time", []), daily.get("river_discharge", [])


def process_station(station: Station, start: str, end: str, force: bool = False) -> None:
    dest = out_path(station)
    if dest.exists() and not force:
        print(f"[{station.station_id}] already have {dest}, skipping (use --force to redo)")
        return

    print(f"[{station.station_id}] {station.name}: fetching {start}..{end}")
    # The API caps how much a single call returns in practice; chunk by
    # decade to stay well under any implicit limit and to make progress
    # visible/resumable if one chunk fails.
    all_dates: list[str] = []
    all_values: list[float | None] = []
    start_year = int(start[:4])
    end_year = int(end[:4])
    for chunk_start_year in range(start_year, end_year + 1, 10):
        chunk_end_year = min(chunk_start_year + 9, end_year)
        chunk_start = f"{chunk_start_year}-01-01" if chunk_start_year != start_year else start
        chunk_end = f"{chunk_end_year}-12-31" if chunk_end_year != end_year else end
        try:
            dates, values = fetch_discharge(station, chunk_start, chunk_end)
        except requests.HTTPError as exc:
            print(f"  [{chunk_start}..{chunk_end}] failed: {exc}, skipping chunk")
            continue
        all_dates.extend(dates)
        all_values.extend(values)
        n_real = sum(1 for v in values if v is not None)
        print(f"  {chunk_start}..{chunk_end}: {len(dates)} days, {n_real} with real data")
        time.sleep(0.5)  # be a polite anonymous client, no key to throttle us

    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "river_discharge_m3s"])
        for date, value in zip(all_dates, all_values):
            writer.writerow([date, "" if value is None else value])

    n_real_total = sum(1 for v in all_values if v is not None)
    print(f"  saved {dest} ({len(all_dates)} rows, {n_real_total} with real data)")


def main():
    today = dt.date.today().isoformat()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default=FIRST_DATE)
    parser.add_argument("--end", default=today)
    parser.add_argument("--station-id", help="only fetch this one station_id, e.g. SW90")
    parser.add_argument("--force", action="store_true", help="redownload stations that already have output")
    args = parser.parse_args()

    # UPSTREAM_REFERENCE_STATIONS (e.g. Silchar, India) are always included
    # here -- they use the exact same GloFAS discharge fetch as our 30 real
    # stations, just written under their own station_id (out_path() already
    # keys on station_id, no special-casing needed). Kept out of every
    # OTHER loop in this codebase (labels, event-matching, live-serving) --
    # see stations.py's module comment on why they're a separate list.
    all_fetchable = STATIONS + UPSTREAM_REFERENCE_STATIONS
    stations = all_fetchable
    if args.station_id:
        stations = [s for s in all_fetchable if s.station_id == args.station_id]
        if not stations:
            raise SystemExit(f"Unknown station_id: {args.station_id}")

    for station in stations:
        process_station(station, args.start, args.end, force=args.force)


if __name__ == "__main__":
    main()
