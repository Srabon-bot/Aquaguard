"""Part 6 (classifier improvements, continued) -- empirically tests the
"cascade generalization" idea flagged early in this project's model-work
discussion but never built: feed the discharge forecaster's OWN prediction
for the matching horizon into the flood risk classifier as a live feature,
instead of the classifier only ever seeing PAST discharge.

WHY THIS IS SAFE TO TRY DIRECTLY (checked, not assumed): the classifier's
and discharge forecaster's feature schemas are byte-identical -- same 42
columns, same order, same categorical station_id/basin encodings (both
derive from the same build_features.py pipeline). This means the already-
trained discharge models can be applied directly to the classifier's own
feature rows with zero alignment work.

A REAL, DISCLOSED CAVEAT, not hidden: applying the discharge model to the
classifier's TRAIN rows uses IN-SAMPLE predictions (the discharge model was
also trained on those same rows), a mild leakage risk the stacking
literature warns about (2026-08-14 research: "must use different training
sets for base model training and meta-learning"). The classifier's TEST
rows are NOT affected by this -- the discharge model's own TEST_CUTOFF is
identical (2024-01-01), so its predictions there are genuinely out-of-
sample for both models. Since the decision to keep or reject this feature
is made from TEST-set performance only, the train-side leakage risk cannot
inflate the number that decides the outcome -- if it doesn't help on the
clean held-out test, that's real, and if it does, that's real too.

Usage:
    python train/experiment_cascade_discharge_feature.py
"""

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from train_model import FEATURES_ROOT, HORIZONS, MODELS_ROOT, add_seasonal_features, train_one_horizon  # noqa: E402

VERSION = "2026-08-07c"
DISCHARGE_MODELS_DIR = MODELS_ROOT / f"{VERSION}-discharge-regression"
OUT_SUFFIX = "-cascade-experiment"


def main():
    in_path = FEATURES_ROOT / VERSION / "all_stations.parquet"
    print(f"Loading {in_path} ...")
    df = pd.read_parquet(in_path)
    df = add_seasonal_features(df)

    schema = json.loads((DISCHARGE_MODELS_DIR / "feature_schema.json").read_text())
    discharge_fit_cols = schema["feature_columns"]
    assert all(c in df.columns for c in discharge_fit_cols), "classifier df missing a discharge-model feature column"

    print("Applying the 3 frozen, already-trained discharge models to every row "
          "(see module docstring for the train-side in-sample caveat)...")
    for h in HORIZONS:
        model = joblib.load(DISCHARGE_MODELS_DIR / f"model_{h}.joblib")
        pred_log = model.predict(df[discharge_fit_cols])
        col = f"discharge_forecast_{h}"
        df[col] = np.clip(np.expm1(pred_log), 0, None)
        print(f"  added {col}: min={df[col].min():.1f}, median={df[col].median():.1f}, max={df[col].max():.1f}")

    out_dir = Path(__file__).resolve().parent.parent / "models" / f"{VERSION}{OUT_SUFFIX}"
    print(f"\n{'='*70}\nTraining WITH discharge-forecast cascade features added\n{'='*70}")
    results = [train_one_horizon(h, df, out_dir) for h in HORIZONS]
    for r in results:
        r.pop("fit_cols", None)
    (out_dir / "metrics.json").write_text(json.dumps(results, indent=2))
    print(f"\nWrote {out_dir / 'metrics.json'}")


if __name__ == "__main__":
    main()
