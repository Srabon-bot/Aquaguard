"""Part 3 extension #5 -- a PIVOT, not a replacement: adds forward-shifted
river-discharge regression targets on top of the existing engineered
feature table, for a NEW discharge-forecasting model that sits alongside
(not instead of) the flood_within_Nh classifier train_model.py already
trains. See DECISIONS.md SS23 for the full reasoning.

Why this pivot: the classifier's precision ceiling (13-18% at 85% recall,
SS14/SS18/SS19/SS22) is a real, structural consequence of two things --
positive labels are genuinely rare (~10% base rate even in the confident
GFMS window) and most of the historical record can only supply POSITIVE
examples (DFO/GFD/GFM/FFWC, see SS13/SS15/SS16/SS19), never confident
negatives. Discharge has neither problem: it's a dense, continuous,
near-100%-covered signal for every station from ~1997 onward (confirmed:
~324k rows here vs ~101k labelable rows for the classifier), so predicting
its future VALUE rather than a binary flood flag sidesteps the label-
sparsity ceiling entirely -- a fundamentally more tractable target, not
just a different one.

This does NOT touch backend/models/2026-08-07c/ (the classifier) or its
source features at data/features/2026-08-07c/ in any way -- it READS that
directory's already-engineered per-station files (all the lag/rolling/SWI/
terrain feature engineering is identical and correct there, no need to
redo it) and WRITES a separate copy under data/features/2026-08-07c-
discharge-regression/ with 3 new target columns added. Two completely
independent pipelines from this point on, exactly so the classifier stays
available as a known-good fallback while the regression pivot is
evaluated on its own merits (user's explicit ask).

Targets added (station-sorted-by-date, forward .shift(-N), never touching
today's own value or the past):
  discharge_target_24h = river_discharge_m3s, 1 day ahead
  discharge_target_48h = river_discharge_m3s, 2 days ahead
  discharge_target_72h = river_discharge_m3s, 3 days ahead

No accessible-window/regime masking is needed here the way
add_horizon_labels() needed for flood_byStor (SS12) -- discharge isn't a
sparse satellite-detection product with inaccessible archive months, it's
a continuous reanalysis/forecast series that's either present (real value)
or absent (NaN, e.g. pre-1997) with no third "unknown-because-unchecked"
state to reason about. A row's target is simply NaN if that future day's
own discharge reading doesn't exist, same as any ordinary missing value.

Usage:
    python train/build_regression_targets.py --version 2026-08-07c
"""

import argparse
from pathlib import Path

import pandas as pd

FEATURES_ROOT = Path(__file__).resolve().parent.parent / "data" / "features"

TARGET_LAGS = {"discharge_target_24h": 1, "discharge_target_48h": 2, "discharge_target_72h": 3}


def add_discharge_targets(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("date").reset_index(drop=True)
    for col, n_days in TARGET_LAGS.items():
        df[col] = df["river_discharge_m3s"].shift(-n_days)
    return df


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", required=True, help="which data/features/<version>/ to read from")
    parser.add_argument("--out-suffix", default="-discharge-regression",
                         help="output dir is data/features/<version><suffix>/")
    args = parser.parse_args()

    in_dir = FEATURES_ROOT / args.version
    out_dir = FEATURES_ROOT / f"{args.version}{args.out_suffix}"
    out_dir.mkdir(parents=True, exist_ok=True)

    station_files = sorted(in_dir.glob("*.parquet"))
    station_files = [f for f in station_files if f.stem != "all_stations"]
    if not station_files:
        raise SystemExit(f"No per-station parquet files found in {in_dir} -- run build_features.py first.")

    print(f"Reading {len(station_files)} station tables from {in_dir}, adding discharge targets, "
          f"writing to {out_dir} (source directory untouched) ...")

    all_frames = []
    for f in station_files:
        station_id = f.stem
        df = pd.read_parquet(f)
        df = add_discharge_targets(df)
        n_labelable = int(df["discharge_target_72h"].notna().sum())
        print(f"  {station_id}: {len(df)} rows, {n_labelable} with a real 72h discharge target")
        df.to_parquet(out_dir / f"{station_id}.parquet", index=False)
        all_frames.append(df)

    combined = pd.concat(all_frames, ignore_index=True)
    combined.to_parquet(out_dir / "all_stations.parquet", index=False)
    total_labelable = int(combined["discharge_target_72h"].notna().sum())
    print(f"\nWrote {len(all_frames)} per-station files + combined ({len(combined)} total rows, "
          f"{total_labelable} with a real 72h discharge target) under {out_dir}")


if __name__ == "__main__":
    main()
