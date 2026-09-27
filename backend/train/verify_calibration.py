"""Calibration verification script.

Loads the trained models from backend/models/<version>/, reproduces the exact
train/test split and feature columns from train_model.py, computes raw vs.
calibrated probabilities on the test set, and reports Brier score improvement.

Usage:
    python backend/train/verify_calibration.py --version 2026-08-07c
"""

import argparse
import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import brier_score_loss

# Make train/ importable
sys.path.insert(0, str(Path(__file__).resolve().parent))
from train_model import (
    FEATURES_ROOT,
    MODELS_ROOT,
    HORIZONS,
    TEST_CUTOFF,
    add_seasonal_features,
    feature_columns,
    time_split,
)

OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "calibration_report.json"


def verify_version(version: str) -> dict:
    in_path = FEATURES_ROOT / version / "all_stations.parquet"
    out_dir = MODELS_ROOT / version
    if not in_path.exists():
        raise FileNotFoundError(f"Feature parquet not found: {in_path}")
    if not out_dir.exists():
        raise FileNotFoundError(f"Model artifacts not found: {out_dir}")

    print(f"Loading {in_path} ...")
    df = pd.read_parquet(in_path)
    df = add_seasonal_features(df)

    results = {}
    for horizon in HORIZONS:
        print(f"\n=== Horizon: {horizon} ===")
        X_train, y_train, X_test, y_test = time_split(df, horizon)
        fit_cols = [c for c in X_train.columns if c not in ("date", "label_regime")]

        model = joblib.load(out_dir / f"model_{horizon}.joblib")
        calibrator = joblib.load(out_dir / f"model_{horizon}_calibrator.joblib")

        # Verify calibrator type
        calibrator_type = type(calibrator).__name__
        print(f"  Calibrator type: {calibrator_type}")
        if not hasattr(calibrator, "transform"):
            raise RuntimeError(
                f"Calibrator for {horizon} ({calibrator_type}) has no .transform() — "
                "this is the bug this script is meant to catch."
            )

        # Raw probabilities
        proba = model.predict_proba(X_test[fit_cols])[:, 1]
        # Calibrated probabilities via transform()
        proba_calibrated = calibrator.transform(np.array(proba))

        brier_raw = float(brier_score_loss(y_test.astype(int), proba))
        brier_calibrated = float(brier_score_loss(y_test.astype(int), proba_calibrated))
        improvement = brier_raw - brier_calibrated

        print(f"  Brier(raw)        = {brier_raw:.4f}")
        print(f"  Brier(calibrated) = {brier_calibrated:.4f}")
        print(f"  Improvement       = {improvement:+.4f}")

        results[horizon] = {
            "calibrator_type": calibrator_type,
            "has_transform": hasattr(calibrator, "transform"),
            "brier_raw": brier_raw,
            "brier_calibrated": brier_calibrated,
            "improvement": improvement,
            "n_test_rows": int(len(X_test)),
            "test_positive_rate": float(y_test.mean()),
        }

    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", required=True, help="Model version directory under backend/models/")
    args = parser.parse_args()

    results = verify_version(args.version)

    report = {
        "version": args.version,
        "verification_script": str(Path(__file__).name),
        "horizons": results,
        "summary": {
            h: {
                "brier_raw": r["brier_raw"],
                "brier_calibrated": r["brier_calibrated"],
                "improvement": r["improvement"],
            }
            for h, r in results.items()
        },
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(report, indent=2))
    print(f"\nWrote calibration report to {OUT_PATH}")


if __name__ == "__main__":
    main()
