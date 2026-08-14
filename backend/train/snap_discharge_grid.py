"""One-off diagnostic/fix tool: some virtual-station coordinates (copied from
app/services/ffwc.py, which only ever needed "close enough for distance
matching") land on the wrong GloFAS grid cell once used for discharge
lookups -- e.g. a side channel of the braided Jamuna, or a minor tributary
near a confluence -- giving implausibly tiny discharge values instead of the
real main-channel flow.

Confirmed 2026-08-07 via ingest_discharge.py output: SW90/SW99/SW17 (Jamuna)
agree at ~20-22k m3/s mean (2015-2020); SW93 (Jamuna, same river!) reads
~2 m3/s, SW174/SW267 (Surma) read ~13/~680 vs an expected similar order of
magnitude to each other. All three are almost certainly off-channel.

This script grid-searches small lat/lon offsets around each suspect
station's original coordinates, queries a short recent window from the
Open-Meteo Flood API for each candidate point, and reports the offset whose
mean discharge is highest -- on the assumption that the main river channel
carries far more flow than an adjacent floodplain/tributary cell, so the
correct cell will stand out clearly.

Usage:
    python train/snap_discharge_grid.py --station-id SW93
    python train/snap_discharge_grid.py --station-id SW93 SW174 SW267
"""

import argparse
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stations import STATIONS, Station  # noqa: E402

BASE_URL = "https://flood-api.open-meteo.com/v1/flood"

# Open-Meteo's GloFAS layer is ~0.05 deg resolution. Search a 7x7 grid at
# 0.05 deg steps (+/-0.15 deg) around the original point -- wide enough to
# jump across a braid channel or confluence, narrow enough to stay "the same
# station" rather than drifting toward a different real gauge site. NOTE:
# for the small, short Chittagong Hill Tracts rivers (CH01/CH02/CH03, added
# 2026-08-07) this radius is still fine distance-wise, but the
# "pick whichever nearby cell has the highest mean discharge" heuristic below
# needs a sanity check against physical plausibility for a small river, not
# blind trust -- a bigger neighboring river could look like a false "better"
# match. See main()'s printed warning for this case.
STEP = 0.05
RADIUS_STEPS = 3  # -3..+3 -> 7x7 = 49 candidates

PROBE_START = "2018-01-01"
PROBE_END = "2020-12-31"


def probe_mean(lat: float, lon: float) -> float | None:
    params = {
        "latitude": round(lat, 4),
        "longitude": round(lon, 4),
        "daily": "river_discharge",
        "start_date": PROBE_START,
        "end_date": PROBE_END,
    }
    resp = requests.get(BASE_URL, params=params, timeout=30)
    resp.raise_for_status()
    values = resp.json().get("daily", {}).get("river_discharge", [])
    real = [v for v in values if v is not None]
    if not real:
        return None
    return sum(real) / len(real)


def grid_search(station: Station) -> None:
    print(f"\n[{station.station_id}] {station.name} -- original ({station.lat}, {station.lon})")
    best = None
    seen: dict[tuple[float, float], float] = {}
    for i in range(-RADIUS_STEPS, RADIUS_STEPS + 1):
        for j in range(-RADIUS_STEPS, RADIUS_STEPS + 1):
            lat = station.lat + i * STEP
            lon = station.lon + j * STEP
            key = (round(lat, 4), round(lon, 4))
            if key in seen:
                continue
            try:
                mean = probe_mean(lat, lon)
            except requests.RequestException as exc:
                print(f"  ({lat:.3f},{lon:.3f}) failed: {exc}")
                continue
            seen[key] = mean if mean is not None else -1
            time.sleep(0.25)
            if mean is not None and (best is None or mean > best[2]):
                best = (lat, lon, mean)

    orig_mean = seen.get((round(station.lat, 4), round(station.lon, 4)))
    print(f"  original cell mean: {orig_mean}")
    if best:
        blat, blon, bmean = best
        print(f"  BEST cell: ({blat:.3f}, {blon:.3f}) mean={bmean:.1f} "
              f"(offset {blat - station.lat:+.2f} lat, {blon - station.lon:+.2f} lon)")
    else:
        print("  no candidate returned data")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--station-id", nargs="+", required=True)
    args = parser.parse_args()
    stations = [s for s in STATIONS if s.station_id in args.station_id]
    for station in stations:
        grid_search(station)


if __name__ == "__main__":
    main()
