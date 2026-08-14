"""Part 6f -- empirically answers "which distance-to-river feature gives
better results": self-derived (pysheds flow-accumulation) vs. independent
(HydroRIVERS vector network) vs. both together. Same spatial CV + held-out
station-test methodology as train_susceptibility_model.py, so the three
variants are directly comparable -- not a guess, a real re-run.

Usage:
    python train/compare_river_distance_features.py
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import GroupKFold

from train_susceptibility_model import N_CV_FOLDS, RANDOM_STATE, held_out_test_stations

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "susceptibility" / "susceptibility_training_table.csv"
CROSSCHECK_PATH = Path(__file__).resolve().parent.parent / "data_raw" / "susceptibility" / "distance_to_river_crosscheck.csv"

BASE_FEATURES = ["elevation_m", "slope_deg", "drainage_density_km_per_km2", "landcover_class", "basin"]
CATEGORICAL = ["landcover_class", "basin"]

VARIANTS = {
    "pysheds_only (current model)": BASE_FEATURES + ["dist_to_river_m"],
    "hydrorivers_only (replacement)": BASE_FEATURES + ["dist_to_river_m_hydrorivers"],
    "both": BASE_FEATURES + ["dist_to_river_m", "dist_to_river_m_hydrorivers"],
}


def evaluate(model, X, y) -> dict:
    proba = model.predict_proba(X)[:, 1]
    return {"roc_auc": float(roc_auc_score(y, proba)), "pr_auc": float(average_precision_score(y, proba))}


def spatial_cv_score(X, y, groups) -> list[dict]:
    gkf = GroupKFold(n_splits=N_CV_FOLDS)
    fold_metrics = []
    for tr_idx, va_idx in gkf.split(X, y, groups):
        model = RandomForestClassifier(n_estimators=300, max_depth=8, min_samples_leaf=5,
                                        random_state=RANDOM_STATE, n_jobs=-1)
        model.fit(X.iloc[tr_idx], y.iloc[tr_idx])
        fold_metrics.append(evaluate(model, X.iloc[va_idx], y.iloc[va_idx]))
    return fold_metrics


def main():
    df = pd.read_csv(DATA_PATH)
    cc = pd.read_csv(CROSSCHECK_PATH)
    df = df.merge(cc[["point_id", "dist_to_river_m_hydrorivers"]], on="point_id", how="left")
    for col in CATEGORICAL:
        df[col] = df[col].astype("category")

    test_stations = held_out_test_stations()
    train_df = df[~df["station_id"].isin(test_stations)].reset_index(drop=True)
    test_df = df[df["station_id"].isin(test_stations)].reset_index(drop=True)
    print(f"Train: {len(train_df)} points, Test: {len(test_df)} points (same 7 held-out stations as the original run)\n")

    results = {}
    for name, feature_cols in VARIANTS.items():
        X_train = train_df[feature_cols].copy()
        X_test = test_df[feature_cols].copy()
        for col in CATEGORICAL:
            X_train[col] = X_train[col].cat.codes
            X_test[col] = X_test[col].cat.codes
        y_train, y_test = train_df["label"], test_df["label"]

        folds = spatial_cv_score(X_train, y_train, train_df["station_id"])
        cv_mean_roc = np.mean([f["roc_auc"] for f in folds])
        cv_mean_pr = np.mean([f["pr_auc"] for f in folds])

        final_model = RandomForestClassifier(n_estimators=300, max_depth=8, min_samples_leaf=5,
                                              random_state=RANDOM_STATE, n_jobs=-1)
        final_model.fit(X_train, y_train)
        test_metrics = evaluate(final_model, X_test, y_test)

        print(f"=== {name} ===")
        print(f"  features: {feature_cols}")
        print(f"  spatial CV:  mean ROC-AUC={cv_mean_roc:.4f}  mean PR-AUC={cv_mean_pr:.4f}  "
              f"(folds: {[round(f['roc_auc'], 3) for f in folds]})")
        print(f"  held-out test: ROC-AUC={test_metrics['roc_auc']:.4f}  PR-AUC={test_metrics['pr_auc']:.4f}\n")

        results[name] = {
            "features": feature_cols,
            "cv_mean_roc_auc": float(cv_mean_roc), "cv_mean_pr_auc": float(cv_mean_pr),
            "cv_folds": folds,
            "held_out_test": test_metrics,
        }

    out_path = Path(__file__).resolve().parent.parent / "models" / "susceptibility" / "river_distance_variant_comparison.json"
    out_path.write_text(json.dumps(results, indent=2))
    print(f"Wrote {out_path}")

    best = max(results, key=lambda k: results[k]["held_out_test"]["roc_auc"])
    print(f"\nBest held-out test ROC-AUC: {best} ({results[best]['held_out_test']['roc_auc']:.4f})")


if __name__ == "__main__":
    main()
