"""Part 5 (classifier improvements, 2026-08-14) -- empirically tests whether
extending the classifier's fixed LAG_DAYS=[1,2,3,5] (build_features.py) with
cross-correlation-suggested additional lags actually improves held-out
performance, rather than assuming it would (the same "test it, don't guess"
discipline the distance-to-river swap used for model #3).

CROSS-CORRELATION FINDING (see MODEL_BUILD_PLAN.md 2026-08-14 entry for the
full table): correlation between lagged rainfall_local_mm and
flood_within_Nh decays smoothly from lag 0 (r~0.34-0.35, already a feature
in its own right) down to ~0.13-0.14 around lag 8-9, then plateaus with a
small secondary bump around lag 12-13 and 18-20 (r~0.17) -- plausibly the
~2-week monsoon accumulation cycle the existing ROLLING_WINDOWS=[7,14]
sum-features already partially capture. No sharp alternate peak was found;
this script tests the two most-supported candidate additions (lag 7, lag
12) rather than the whole 0-20 range, to avoid a fishing-expedition of
adding every mildly-elevated lag.

METHOD: reuses train_model.py's own time_split/train_one_horizon exactly
(same TEST_CUTOFF, same sample weighting, same threshold-tuning target
recall) on a COPY of the real featured dataset with two extra lag columns
added post-hoc (rainfall_local_mm_lag7d, rainfall_local_mm_lag12d) --
doesn't touch build_features.py or require re-running the full ingest
pipeline, since the base rainfall_local_mm column is already present in
the existing parquet.

Usage:
    python train/experiment_cross_correlation_lags.py
"""

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from train_model import FEATURES_ROOT, HORIZONS, add_seasonal_features, train_one_horizon  # noqa: E402

EXTRA_LAGS = [7, 12]
VERSION = "2026-08-07c"
OUT_SUFFIX = "-lag-experiment"


def main():
    in_path = FEATURES_ROOT / VERSION / "all_stations.parquet"
    print(f"Loading {in_path} ...")
    df = pd.read_parquet(in_path)
    df = df.sort_values(["station_id", "date"]).reset_index(drop=True)

    for lag in EXTRA_LAGS:
        col = f"rainfall_local_mm_lag{lag}d"
        assert col not in df.columns, f"{col} already exists -- unexpected"
        df[col] = df.groupby("station_id")["rainfall_local_mm"].shift(lag)
        print(f"Added {col} ({df[col].notna().sum()} non-null of {len(df)} rows)")

    df = add_seasonal_features(df)

    out_dir = Path(__file__).resolve().parent.parent / "models" / f"{VERSION}{OUT_SUFFIX}"
    print(f"\n{'='*70}\nTraining with EXTRA lags {EXTRA_LAGS} added to the existing [1,2,3,5]\n{'='*70}")
    results = [train_one_horizon(h, df, out_dir) for h in HORIZONS]
    for r in results:
        r.pop("fit_cols", None)
    (out_dir / "metrics.json").write_text(json.dumps(results, indent=2))
    print(f"\nWrote {out_dir / 'metrics.json'}")


if __name__ == "__main__":
    main()
