"""Part 6d -- trains the flood SUSCEPTIBILITY model (model #3) on the
1,381-point table build_susceptibility_dataset.py produced (362 positive /
1,019 negative, dropped-for-insufficient-data and dropped-for-no-coverage
already excluded there).

EVALUATION DISCIPLINE -- SPATIAL, not random, and a genuine held-out test
set, not just cross-validation: mirrors train_model.py's own "never a
random shuffle" rule for the temporal classifier, translated to the spatial
dimension. The literature is explicit that random splits on spatially
autocorrelated data inflate AUC by 5-15% (see MODEL_BUILD_PLAN.md research
log) -- nearby grid points within the same station's 49-point neighborhood
share almost all their terrain signal, so a random split would leak a
station's own local geography between train and test.

  - HELD-OUT TEST STATIONS: ~20% of stations per basin (never touched
    during training or model selection) -- stratified by basin, not a flat
    20% of all 30, so the test set still spans flat Brahmaputra/Ganges
    floodplain, Meghna haor wetlands, AND the hilly Chittagong Hill Tracts,
    rather than accidentally testing only on one terrain type.
  - SPATIAL GROUP K-FOLD within the remaining training stations (grouped by
    station_id, via sklearn's GroupKFold) for the validation slice used in
    early stopping -- same "no point from a station's neighborhood appears
    on both sides of a split" discipline, one level down.

TWO MODEL FAMILIES COMPARED, not just LightGBM by default: the research
found at least one Bangladesh-specific study where plain Random Forest beat
XGBoost specifically in hilly terrain (flash-flood susceptibility,
southeastern Bangladesh) -- and this project's own grid spans both flat
delta AND the hilly CHT, so which family wins here is worth actually
checking rather than assuming LightGBM (the classifier's own choice, for a
DIFFERENT problem) transfers.

Usage:
    python train/train_susceptibility_model.py
"""

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import shap
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import GroupKFold

import lightgbm as lgb
from stations import STATIONS

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "susceptibility" / "susceptibility_training_table.csv"
MODELS_DIR = Path(__file__).resolve().parent.parent / "models" / "susceptibility"
N_CV_FOLDS = 4
RANDOM_STATE = 42

FEATURE_COLUMNS = ["elevation_m", "slope_deg", "dist_to_river_m", "drainage_density_km_per_km2", "landcover_class", "basin"]
CATEGORICAL = ["landcover_class", "basin"]


def held_out_test_stations() -> set[str]:
    """~20% of stations per basin, evenly spaced through each basin's own
    (deterministically sorted) station list -- see module docstring for why
    stratified-by-basin, not a flat random 20%."""
    from collections import defaultdict
    by_basin: dict[str, list[str]] = defaultdict(list)
    for s in STATIONS:
        by_basin[s.basin].append(s.station_id)
    held_out = set()
    for basin, ids in by_basin.items():
        ids = sorted(ids)
        n_hold = max(1, round(0.2 * len(ids)))
        idxs = np.linspace(0, len(ids) - 1, n_hold, dtype=int)
        held_out.update(ids[i] for i in idxs)
    return held_out


def evaluate(model, X, y) -> dict:
    proba = model.predict_proba(X)[:, 1]
    return {
        "roc_auc": float(roc_auc_score(y, proba)) if y.nunique() > 1 else float("nan"),
        "pr_auc": float(average_precision_score(y, proba)) if y.nunique() > 1 else float("nan"),
        "n": int(len(y)), "positive_rate": float(y.mean()),
    }


def spatial_cv_score(make_model, X: pd.DataFrame, y: pd.Series, groups: pd.Series, categorical_idx=None) -> list[dict]:
    gkf = GroupKFold(n_splits=N_CV_FOLDS)
    fold_metrics = []
    for fold, (tr_idx, va_idx) in enumerate(gkf.split(X, y, groups)):
        model = make_model()
        X_tr, y_tr = X.iloc[tr_idx], y.iloc[tr_idx]
        X_va, y_va = X.iloc[va_idx], y.iloc[va_idx]
        if isinstance(model, lgb.LGBMClassifier):
            model.fit(X_tr, y_tr, categorical_feature=CATEGORICAL)
        else:
            model.fit(X_tr, y_tr)
        m = evaluate(model, X_va, y_va)
        m["fold"] = fold
        fold_metrics.append(m)
    return fold_metrics


def main():
    df = pd.read_csv(DATA_PATH)
    for col in CATEGORICAL:
        df[col] = df[col].astype("category")

    test_stations = held_out_test_stations()
    print(f"Held-out test stations ({len(test_stations)}/30): {sorted(test_stations)}")

    train_df = df[~df["station_id"].isin(test_stations)].reset_index(drop=True)
    test_df = df[df["station_id"].isin(test_stations)].reset_index(drop=True)
    print(f"Train: {len(train_df)} points ({100*train_df['label'].mean():.1f}% positive, {train_df['station_id'].nunique()} stations)")
    print(f"Test:  {len(test_df)} points ({100*test_df['label'].mean():.1f}% positive, {test_df['station_id'].nunique()} stations)")

    X_train, y_train, groups_train = train_df[FEATURE_COLUMNS], train_df["label"], train_df["station_id"]
    X_test, y_test = test_df[FEATURE_COLUMNS], test_df["label"]

    print("\n=== Spatial GroupKFold CV (within training stations only) ===")
    results = {}
    for name, make_model in [
        ("lightgbm", lambda: lgb.LGBMClassifier(n_estimators=300, learning_rate=0.05, num_leaves=15,
                                                  min_child_samples=10, random_state=RANDOM_STATE, verbosity=-1)),
        ("random_forest", lambda: RandomForestClassifier(n_estimators=300, max_depth=8, min_samples_leaf=5,
                                                            random_state=RANDOM_STATE, n_jobs=-1)),
    ]:
        # RandomForest needs numeric categoricals, not pandas 'category' dtype
        X_train_fit = X_train.copy()
        if name == "random_forest":
            for col in CATEGORICAL:
                X_train_fit[col] = X_train_fit[col].cat.codes
        folds = spatial_cv_score(make_model, X_train_fit, y_train, groups_train)
        mean_auc = np.mean([f["roc_auc"] for f in folds])
        mean_prauc = np.mean([f["pr_auc"] for f in folds])
        print(f"{name}: mean ROC-AUC={mean_auc:.3f} (folds: {[round(f['roc_auc'],3) for f in folds]}), "
              f"mean PR-AUC={mean_prauc:.3f}")
        results[name] = {"cv_folds": folds, "cv_mean_roc_auc": float(mean_auc), "cv_mean_pr_auc": float(mean_prauc)}

    winner = max(results, key=lambda k: results[k]["cv_mean_roc_auc"])
    print(f"\nWinner by spatial CV mean ROC-AUC: {winner}")

    print(f"\n=== Final {winner} model: fit on ALL training stations, evaluate on held-out test stations ===")
    if winner == "lightgbm":
        final_model = lgb.LGBMClassifier(n_estimators=300, learning_rate=0.05, num_leaves=15,
                                          min_child_samples=10, random_state=RANDOM_STATE, verbosity=-1)
        final_model.fit(X_train, y_train, categorical_feature=CATEGORICAL)
        X_test_fit = X_test
    else:
        final_model = RandomForestClassifier(n_estimators=300, max_depth=8, min_samples_leaf=5,
                                              random_state=RANDOM_STATE, n_jobs=-1)
        X_train_fit = X_train.copy()
        for col in CATEGORICAL:
            X_train_fit[col] = X_train_fit[col].cat.codes
        final_model.fit(X_train_fit, y_train)
        X_test_fit = X_test.copy()
        for col in CATEGORICAL:
            X_test_fit[col] = X_test_fit[col].cat.codes

    test_metrics = evaluate(final_model, X_test_fit, y_test)
    print(f"HELD-OUT TEST (never touched during training/CV): ROC-AUC={test_metrics['roc_auc']:.3f}, "
          f"PR-AUC={test_metrics['pr_auc']:.3f}, n={test_metrics['n']}, positive_rate={test_metrics['positive_rate']:.3f}")

    # SHAP -- same explainability tool as the temporal classifier, for a
    # consistent interpretability story across all 3 models. Handles both
    # shap API shapes seen in practice: older versions return a
    # [neg_class, pos_class] list, newer versions return one ndarray shaped
    # (n_samples, n_features, n_classes) -- confirmed by hitting the second
    # shape for real against RandomForestClassifier here, not assumed.
    explainer = shap.TreeExplainer(final_model)
    shap_values = explainer.shap_values(X_test_fit)
    if isinstance(shap_values, list):
        shap_values = shap_values[1]
    elif shap_values.ndim == 3:
        shap_values = shap_values[:, :, 1]
    mean_abs_shap = pd.Series(np.abs(shap_values).mean(axis=0), index=FEATURE_COLUMNS).sort_values(ascending=False)
    print("\nFeature importance (mean |SHAP| on held-out test set):")
    for feat, val in mean_abs_shap.items():
        print(f"  {feat:35s} {val:.4f}")

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(final_model, MODELS_DIR / f"susceptibility_{winner}.joblib")
    (MODELS_DIR / "metrics.json").write_text(json.dumps({
        "winner": winner,
        "cv_comparison": results,
        "held_out_test": test_metrics,
        "held_out_test_stations": sorted(test_stations),
        "feature_importance_shap": mean_abs_shap.round(4).to_dict(),
        "train_n": len(train_df), "test_n": len(test_df),
    }, indent=2))
    (MODELS_DIR / "feature_schema.json").write_text(json.dumps({
        "model_type": winner,
        "feature_columns": FEATURE_COLUMNS,
        "categorical_features": CATEGORICAL,
        "landcover_classes": {10: "tree", 20: "shrubland", 30: "grassland", 40: "cropland",
                               50: "built-up", 60: "bare/sparse", 70: "snow/ice", 80: "water",
                               90: "wetland", 95: "mangrove", 100: "moss/lichen"},
        "basins": sorted(set(s.basin for s in STATIONS)),
        "notes": "landcover_class and basin must be provided as their pandas 'category' codes "
                 "if using random_forest, or as pandas 'category' dtype directly if using lightgbm.",
    }, indent=2))
    print(f"\nWrote model + metrics + feature_schema to {MODELS_DIR}")


if __name__ == "__main__":
    main()
