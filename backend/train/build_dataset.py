"""Part 2 ETL merge: combine Open-Meteo rainfall+soil-moisture, Open-Meteo
discharge, and GFMS flood-intensity labels into one (virtual_station, date)
table per station. See MODEL_BUILD_PLAN.md Part 2.

Inputs (all produced by the sibling ingest_*.py scripts):
  backend/data_raw/openmeteo_weather/<point_id>.csv  -- date, precipitation_sum, soil_moisture_0_to_7cm_mean
  backend/data_raw/discharge/discharge_<id>.csv      -- date, river_discharge_m3s
  backend/data_raw/gfms/gfms_<id>.csv                -- date, flood_byStor

**2026-08-07: switched primary rainfall source from CHIRPS to Open-Meteo's
Historical Weather API** (ERA5/ERA5-Land reanalysis) -- see
MODEL_BUILD_PLAN.md Part 1b decision log for the full rationale. Short
version: same free/no-key trust profile as the discharge API already used
here, longer history (1950 vs CHIRPS's 1981), point-based JSON instead of
multi-GB gridded netCDF, and it sidesteps the CrowdSec ban that stalled
CHIRPS indefinitely. It also adds **soil moisture**, a rainfall-independent
antecedent-wetness signal that was completely absent before and is
deliberately kept at the same 0-7cm depth a shallow-buried IoT probe would
report, so the trained feature and a future live sensor reading line up
without a unit/depth mismatch (see Part 5b).

**2026-08-07: expanded from 6 to 30 stations** for full-Bangladesh coverage
(previously only the Jamuna/Brahmaputra + Surma were represented, with no
station for the Ganges/Padma, the lower Meghna/Dhaka, the Chittagong Hill
Tracts, or the southern coastal belt -- see DECISIONS.md §7). Station
definitions now live in `train/stations.py` (single source of truth, no
longer duplicated per-script).

For each station we use two rainfall (and, for "local", soil moisture) series:
  - "local": the station's own point (`<id>_local.csv`).
  - "upstream": mean across a 3x3 sample grid over a hand-picked upstream
    catchment box (`train/stations.py`'s `UPSTREAM_BOXES`, one per basin:
    brahmaputra/ganges/meghna/cht), since Bangladesh flooding is driven as
    much by upstream India/Nepal/Bhutan rain as by local rain (see plan.md).
    This is a deliberately coarse engineering approximation (what Part 3's
    more careful travel-time-lag features will refine) -- see
    `stations.py`'s module docstring for the per-basin rationale.
  Soil moisture is only tracked "local" (not upstream) -- an IoT sensor at
  the farm can only ever report local conditions, so upstream soil moisture
  would be a training-only feature with no live-inference equivalent.

Output: for each station, one parquet (+ CSV for eyeballing) under
  backend/data/processed/<version>/<station_id>.parquet
with columns: date, rainfall_local_mm, rainfall_upstream_mm,
soil_moisture_local, river_discharge_m3s, flood_byStor, and a `*_missing`
boolean flag per source column -- missing/no-data days are explicitly
flagged, never silently interpolated or dropped (per the Part 2 checklist).

Usage:
    python train/build_dataset.py                 # build from whatever data currently exists
    python train/build_dataset.py --version 2026-08-05
"""

import argparse
import datetime as dt
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stations import STATIONS, Station  # noqa: E402

WEATHER_DIR = Path(__file__).resolve().parent.parent / "data_raw" / "openmeteo_weather"
DISCHARGE_DIR = Path(__file__).resolve().parent.parent / "data_raw" / "discharge"
GFMS_DIR = Path(__file__).resolve().parent.parent / "data_raw" / "gfms"
OUT_ROOT = Path(__file__).resolve().parent.parent / "data" / "processed"


def _load_weather_point(point_id: str) -> pd.DataFrame | None:
    path = WEATHER_DIR / f"{point_id}.csv"
    if not path.exists():
        return None
    df = pd.read_csv(path, parse_dates=["date"])
    df = df.set_index("date")
    df.index = df.index.normalize()
    return df


def local_weather_series(station: Station) -> tuple[pd.Series, pd.Series]:
    """Returns (rainfall_local_mm, soil_moisture_local) for this station's own point."""
    df = _load_weather_point(f"{station.station_id}_local")
    if df is None:
        print(f"  no local Open-Meteo weather file for {station.station_id}")
        return (pd.Series(name="rainfall_local_mm", dtype=float),
                pd.Series(name="soil_moisture_local", dtype=float))
    rain = df["precipitation_sum"].rename("rainfall_local_mm")
    soil = df["soil_moisture_0_to_7cm_mean"].rename("soil_moisture_local")
    return rain, soil


def upstream_rainfall_series(station: Station) -> pd.Series:
    """Mean rainfall across the 3x3 upstream sample grid for this station's basin."""
    # Point IDs must match ingest_openmeteo_historical.py's build_points() naming
    # exactly (a flat 0-8 index via stations.upstream_points(), not a 2D i,j pair).
    point_ids = [f"{station.basin}_upstream_{i}" for i in range(9)]
    frames = []
    for pid in point_ids:
        df = _load_weather_point(pid)
        if df is not None:
            frames.append(df["precipitation_sum"])
    if not frames:
        print(f"  no upstream Open-Meteo weather files for basin {station.basin}")
        return pd.Series(name="rainfall_upstream_mm", dtype=float)
    combined = pd.concat(frames, axis=1)
    s = combined.mean(axis=1)
    s.name = "rainfall_upstream_mm"
    return s


def load_discharge(station: Station) -> pd.Series:
    path = DISCHARGE_DIR / f"discharge_{station.station_id}.csv"
    if not path.exists():
        print(f"  no discharge file for {station.station_id}")
        return pd.Series(name="river_discharge_m3s", dtype=float)
    df = pd.read_csv(path, parse_dates=["date"])
    s = df.set_index("date")["river_discharge_m3s"]
    s.index = s.index.normalize()
    return s


def load_gfms(station: Station) -> pd.Series:
    path = GFMS_DIR / f"gfms_{station.station_id}.csv"
    if not path.exists():
        print(f"  no GFMS file for {station.station_id}")
        return pd.Series(name="flood_byStor", dtype=float)
    df = pd.read_csv(path, parse_dates=["date"])
    s = df.set_index("date")["flood_byStor"]
    s.index = s.index.normalize()
    return s


def build_station_table(station: Station) -> pd.DataFrame:
    local_rain, local_soil = local_weather_series(station)
    upstream_rain = upstream_rainfall_series(station)
    discharge = load_discharge(station)
    flood = load_gfms(station)

    all_dates = local_rain.index.union(local_soil.index).union(upstream_rain.index).union(discharge.index).union(flood.index)
    if len(all_dates) == 0:
        return pd.DataFrame(columns=["date", "rainfall_local_mm", "rainfall_upstream_mm",
                                      "soil_moisture_local", "river_discharge_m3s", "flood_byStor"])

    df = pd.DataFrame(index=sorted(all_dates))
    df["rainfall_local_mm"] = local_rain
    df["rainfall_upstream_mm"] = upstream_rain
    df["soil_moisture_local"] = local_soil
    df["river_discharge_m3s"] = discharge
    df["flood_byStor"] = flood

    # Explicit missing-data flags -- never silently interpolate/drop (Part 2
    # checklist). A value can be legitimately absent for different reasons
    # per source (Open-Meteo rainfall/soil moisture: essentially never, ERA5
    # reanalysis is continuous back to 1950; discharge: before ~1997 GloFAS
    # reanalysis coverage; GFMS: either a genuine no-flood day, or an
    # inaccessible archive month -- see ingest_gfms.py docstring, this table
    # doesn't currently distinguish the two, both surface as flood_byStor NaN).
    for col in ["rainfall_local_mm", "rainfall_upstream_mm", "soil_moisture_local",
                "river_discharge_m3s", "flood_byStor"]:
        df[f"{col}_missing"] = df[col].isna()

    df.index.name = "date"
    df = df.reset_index()
    df.insert(1, "station_id", station.station_id)
    df.insert(2, "station_name", station.name)
    return df


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", default=dt.date.today().isoformat(),
                         help="output subfolder name under backend/data/processed/ (default: today's date)")
    args = parser.parse_args()

    out_dir = OUT_ROOT / args.version
    out_dir.mkdir(parents=True, exist_ok=True)

    all_frames = []
    for station in STATIONS:
        print(f"Building table for {station.station_id} ({station.name})...")
        df = build_station_table(station)
        if df.empty:
            print(f"  WARNING: no data at all for {station.station_id}, skipping file write")
            continue

        n = len(df)
        date_min, date_max = df["date"].min(), df["date"].max()
        coverage = {
            col: f"{100 * (1 - df[f'{col}_missing'].mean()):.1f}%"
            for col in ["rainfall_local_mm", "rainfall_upstream_mm", "soil_moisture_local",
                        "river_discharge_m3s", "flood_byStor"]
        }
        print(f"  {n} rows, {date_min.date()}..{date_max.date()}, coverage: {coverage}")

        csv_path = out_dir / f"{station.station_id}.csv"
        parquet_path = out_dir / f"{station.station_id}.parquet"
        df.to_csv(csv_path, index=False)
        df.to_parquet(parquet_path, index=False)
        all_frames.append(df)

    if all_frames:
        combined = pd.concat(all_frames, ignore_index=True)
        combined_path = out_dir / "all_stations.parquet"
        combined.to_parquet(combined_path, index=False)
        print(f"\nWrote {len(all_frames)} per-station files + combined "
              f"({len(combined)} total rows) under {out_dir}")
    else:
        print("\nNo station data available -- nothing written. "
              "Run the ingest_*.py scripts first.")


if __name__ == "__main__":
    main()
