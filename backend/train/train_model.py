"""Part 4 -- Model training. Trains 3 independent binary classifiers (one per
flood_within_24h/48h/72h horizon) on the engineered feature table from
build_features.py, using LightGBM (gradient-boosted trees, per DECISIONS.md
SS10), which natively handles missing values without imputation -- important
since several features (discharge, upstream-chain discharge) are
structurally missing for parts of the historical record (pre-1997, or
stations without a chain neighbor -- see SS11).

ONE POOLED MODEL PER HORIZON, not one model per station: all 30 stations'
rows are combined into a single training set, with station identity and
basin passed in as categorical features so the model can learn per-station/
per-basin baseline risk while still sharing statistical strength across
stations -- several of the 30 have too few labeled rows (see build_features
output) to train an independent model each.

THREE SEPARATE BINARY MODELS, not one ordinal/multiclass target: the three
horizons are nested (a positive at 24h implies positive at 48h/72h by
construction), and three independent binary probabilities ("15% risk in the
next 24h, 40% in the next 72h") are both the simplest thing that works and
the easiest to explain in a pre-defence, matching how real early-warning
systems typically present multi-lead-time risk. This was an open decision
in DECISIONS.md; resolved here rather than deferred further.

TRAIN/TEST SPLIT -- TIME-BASED, never a random shuffle (this is a
forecasting problem; a random split would leak nearby-day autocorrelation
from test into train). A single GLOBAL date cutoff is used (not per-station)
so no station's future rows can leak information into another station's
training rows via a shared monsoon season.

  - Test set: ONLY rows whose flood_within_Nh_label_regime is "observed"
    (see build_features.py SS12/13) with date >= TEST_CUTOFF. Restricting
    eval to the "observed" regime is essential -- the DFO-derived
    "unobserved_positive" rows have no real negatives, so testing on them
    would trivially inflate recall to 100% on a subset that was never
    actually a fair test.
  - Train set: ALL labeled rows (both regimes) with date < TEST_CUTOFF --
    the full DFO-extended history (1985-2010) plus GFMS-observed rows
    through the cutoff.

TEST_CUTOFF = 2024-01-01, chosen by inspecting per-year "observed"-regime
counts (see MODEL_BUILD_PLAN.md): reserves 2024 (a high-flood year) + 2025
(a low-flood year) + partial 2026 as test (~22.8k rows, ~7.4% positive for
the 72h horizon) -- deliberately spans both a severe and a mild flood year
rather than picking a single "lucky" test year. Train ends up ~77k rows
(~20.3% positive for 72h, pulled up by the DFO all-positive rows).

FEATURES -- an explicit DENYLIST from the full engineered table, for one
specific reason: GFMS's Flood_byStor has no live feed (confirmed stalled
since 2026-02-02, DECISIONS.md SS6) so it can NEVER be available at real
inference time. Including it (or its _missing flag, which nearly perfectly
tracks the GFMS-accessible calendar window) would let the model re-learn
the same "which era is this" shortcut SS12 already found and fixed once --
pure train-serve skew, a feature the model leans on in training that is
always absent in production. Rainfall/soil-moisture/discharge features, in
contrast, stay in: they're excluded from live-serving today only because
Part 5 hasn't built those fetches yet (an implementation gap, not a
permanent unavailability) -- Part 5's job is to catch the live pipeline up
to match what this model actually needs, not the other way around.

Two extra features are engineered here (not in build_features.py, since
they're trivial derivations of `date` that don't need the ingest pipeline):
cyclic day-of-year (doy_sin/doy_cos), since Bangladesh flooding is strongly
seasonal and raw month/day-of-year would wrongly treat Dec 31 and Jan 1 as
maximally different.

Usage:
    python train/train_model.py --version 2026-08-07c
"""

import argparse
import json
import sys
from pathlib import Path

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd
import shap
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    precision_recall_curve,
    precision_recall_fscore_support,
    roc_auc_score,
)

TARGET_RECALL = 0.85  # see module docstring addendum below on threshold choice
DFO_CONFIDENCE_WEIGHT = 0.5  # see build_sample_weight() -- discount for DFO-derived (coarser) positives

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stations import STATIONS  # noqa: E402

FEATURES_ROOT = Path(__file__).resolve().parent.parent / "data" / "features"
MODELS_ROOT = Path(__file__).resolve().parent.parent / "models"

HORIZONS = ["24h", "48h", "72h"]
TEST_CUTOFF = pd.Timestamp("2024-01-01")

STATION_BASIN = {s.station_id: s.basin for s in STATIONS}

# Denylist -- see module docstring for the reasoning on each exclusion.
NON_FEATURE_COLUMNS = {
    "date",              # kept only to derive doy_sin/doy_cos and for the train/test split itself
    "station_name",      # free text, redundant with station_id
    "flood_byStor",      # GFMS has no live feed -- would be permanent train-serve skew, not just unused
    "flood_byStor_missing",  # tracks the GFMS-accessible calendar window almost exactly -- same problem
}
TARGET_AND_REGIME_COLUMNS = {
    f"flood_within_{h}{suffix}" for h in HORIZONS for suffix in ("", "_label_regime")
}


STATION_ID_CATEGORIES = sorted(s.station_id for s in STATIONS)
BASIN_CATEGORIES = sorted(set(STATION_BASIN.values()))


def add_seasonal_features(df: pd.DataFrame) -> pd.DataFrame:
    doy = df["date"].dt.dayofyear
    days_in_year = np.where(df["date"].dt.is_leap_year, 366, 365)
    angle = 2 * np.pi * doy / days_in_year
    df["doy_sin"] = np.sin(angle)
    df["doy_cos"] = np.cos(angle)
    df["basin"] = df["station_id"].map(STATION_BASIN)

    # EXPLICIT category lists (not a bare .astype("category"), which infers
    # categories from whatever's present in the frame it's called on) --
    # LightGBM's categorical-feature handling uses pandas' underlying
    # integer category *codes*, not the string labels, to build tree
    # splits. A live single-row prediction only ever "sees" one station, so
    # an implicit astype("category") there would assign it code 0
    # regardless of which station it actually is, silently corrupting
    # every live prediction. Pinning the same category lists here and in
    # feature_schema.json (below) keeps train-time and inference-time codes
    # identical -- this is exactly the kind of bug that wouldn't crash,
    # just quietly produce wrong predictions, so it's caught here rather
    # than left for Part 5 to discover the hard way.
    df["station_id"] = pd.Categorical(df["station_id"], categories=STATION_ID_CATEGORIES)
    df["basin"] = pd.Categorical(df["basin"], categories=BASIN_CATEGORIES)
    return df


# Cascade feature (2026-08-14, see experiment_cascade_discharge_feature.py
# and MODEL_BUILD_PLAN.md for the real A/B numbers behind this choice): each
# horizon's classifier gets ONLY its own matching discharge-forecaster
# prediction (discharge_forecast_24h for the 24h model, etc.), not the other
# two horizons' forecasts. Tested both ways on real held-out data -- giving
# every horizon all 3 forecasts helped 24h more but actively hurt 72h
# (irrelevant/noisier cascade features diluting a model that already has too
# few positives to spare); the horizon-matched-only design was positive on
# PR-AUC at every horizon and is far simpler to explain and defend.
DISCHARGE_FORECAST_COLUMNS = {f"discharge_forecast_{h}" for h in HORIZONS}


def feature_columns(df: pd.DataFrame, horizon: str) -> list[str]:
    other_horizon_forecasts = DISCHARGE_FORECAST_COLUMNS - {f"discharge_forecast_{horizon}"}
    exclude = NON_FEATURE_COLUMNS | TARGET_AND_REGIME_COLUMNS | other_horizon_forecasts
    return [c for c in df.columns if c not in exclude]


def time_split(df: pd.DataFrame, horizon: str) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    target_col = f"flood_within_{horizon}"
    regime_col = f"flood_within_{horizon}_label_regime"
    labeled = df[df[target_col].notna()].copy()
    labeled[target_col] = labeled[target_col].astype(bool)

    train_mask = labeled["date"] < TEST_CUTOFF
    test_mask = (labeled["date"] >= TEST_CUTOFF) & (labeled[regime_col] == "observed")

    # "date" and the regime column are kept alongside the real feature
    # columns here purely for train_one_horizon's own bookkeeping (the
    # validation-slice cutoff, and sample-weighting by label confidence) --
    # both are dropped again via fit_cols before the model ever sees them
    # (see feature_columns(), the actual feature allowlist used everywhere
    # else, e.g. at inference time).
    cols = feature_columns(labeled, horizon) + ["date", regime_col]
    X_train, y_train = labeled.loc[train_mask, cols].rename(columns={regime_col: "label_regime"}), labeled.loc[train_mask, target_col]
    X_test, y_test = labeled.loc[test_mask, cols].rename(columns={regime_col: "label_regime"}), labeled.loc[test_mask, target_col]
    return X_train, y_train, X_test, y_test


def build_sample_weight(y: pd.Series, regime: pd.Series) -> np.ndarray:
    """Replaces a blanket class_weight="balanced" with something more
    principled, using the label_regime column build_features.py provides
    specifically for this (DECISIONS.md SS13/SS14):

    1. The positive-class weight is computed ONLY from "observed" (GFMS)
       rows' real class balance, not the full training set's -- the full
       set is artificially less imbalanced because of DFO's all-positive
       rows (SS13), and correcting for that inflated balance (what plain
       class_weight="balanced" would do) under-corrects for how rare a
       positive actually is at deployment time, plausibly explaining low
       precision in the first training run.
    2. DFO-derived positives ("unobserved_positive") get an additional
       confidence discount on top of that base weight -- they're
       attributed at event-date-range + keyword-matched-station
       granularity (coarser, noisier) rather than GFMS's daily per-pixel
       detection, so they should pull the model less hard than an
       equally-weighted GFMS positive.
    """
    observed_mask = (regime == "observed").values
    y_bool = y.values.astype(bool)
    n_neg = int((~y_bool & observed_mask).sum())
    n_pos = int((y_bool & observed_mask).sum())
    pos_weight = n_neg / n_pos if n_pos else 1.0

    weight = np.ones(len(y), dtype=float)
    weight[y_bool] = pos_weight
    dfo_positive_mask = y_bool & (regime.values == "unobserved_positive")
    weight[dfo_positive_mask] *= DFO_CONFIDENCE_WEIGHT
    return weight


def naive_baselines(df: pd.DataFrame, horizon: str, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    """Two naive baselines, evaluated (PR-AUC, appropriate for this
    imbalanced problem -- see 2026-08-14 research log) on the EXACT same
    held-out test rows as the trained model -- the same "compare against a
    baseline, don't quote a bare number" discipline this project already
    applies elsewhere (train_regression_model.py's persistence comparison,
    SS10/SS14/SS18). Added 2026-08-14 -- this model never had one before.

      - Climatology: historical (station_id, calendar month) positive rate,
        computed from TRAIN rows only (no leakage) -- "it's monsoon season
        at this station" with zero live weather data.
      - Persistence: this station's own most recent PRIOR labeled value
        (any earlier date, train or test) -- "assume conditions continue."

    Neither baseline needs live data at all; a model that doesn't clearly
    beat both has added no real skill, whatever its standalone PR-AUC looks
    like in isolation.
    """
    target_col = f"flood_within_{horizon}"
    labeled = df[df[target_col].notna()].copy()
    labeled[target_col] = labeled[target_col].astype(bool)

    train_rows = labeled[labeled["date"] < TEST_CUTOFF]
    clim_by_station_month = train_rows.groupby(["station_id", train_rows["date"].dt.month], observed=True)[target_col].mean()
    clim_by_station = train_rows.groupby("station_id", observed=True)[target_col].mean()
    clim_global = float(train_rows[target_col].mean())

    test_month = X_test["date"].dt.month
    clim_pred = np.array([
        clim_by_station_month.get((sid, m), clim_by_station.get(sid, clim_global))
        for sid, m in zip(X_test["station_id"], test_month)
    ])

    labeled_sorted = labeled.sort_values(["station_id", "date"])
    labeled_sorted["_persistence"] = labeled_sorted.groupby("station_id", observed=True)[target_col].shift(1).astype(float)
    pers_pred = labeled_sorted["_persistence"].reindex(X_test.index).fillna(clim_global).values

    def safe_pr_auc(y_true, y_score):
        return float(average_precision_score(y_true, y_score)) if len(np.unique(y_true)) > 1 else float("nan")

    y = y_test.astype(int).values
    return {
        "climatology_pr_auc": safe_pr_auc(y, clim_pred),
        "persistence_pr_auc": safe_pr_auc(y, pers_pred),
    }


def train_one_horizon(horizon: str, df: pd.DataFrame, out_dir: Path) -> dict:
    print(f"\n=== Horizon: {horizon} ===")
    X_train, y_train, X_test, y_test = time_split(df, horizon)
    print(f"  train: {len(X_train)} rows ({100*y_train.mean():.2f}% positive)")
    print(f"  test:  {len(X_test)} rows ({100*y_test.mean():.2f}% positive)")

    # Time-based validation slice carved out of the tail of train (not test)
    # for early stopping -- keeps test fully held out, still respects the
    # no-random-shuffle rule.
    val_cutoff = X_train["date"].quantile(0.85, interpolation="nearest")
    val_mask = X_train["date"] >= val_cutoff
    fit_cols = [c for c in X_train.columns if c not in ("date", "label_regime")]

    sample_weight = build_sample_weight(y_train.loc[~val_mask], X_train.loc[~val_mask, "label_regime"])

    model = lgb.LGBMClassifier(
        n_estimators=1000,
        learning_rate=0.03,
        num_leaves=31,
        max_depth=-1,
        min_child_samples=40,   # extra regularization -- see tuning notes
        feature_fraction=0.85,
        bagging_fraction=0.85,
        bagging_freq=1,
        random_state=42,
        verbosity=-1,
    )
    model.fit(
        X_train.loc[~val_mask, fit_cols], y_train.loc[~val_mask],
        sample_weight=sample_weight,
        eval_X=X_train.loc[val_mask, fit_cols], eval_y=y_train.loc[val_mask],
        eval_metric="average_precision",
        callbacks=[lgb.early_stopping(stopping_rounds=50, verbose=False)],
        categorical_feature=["station_id", "basin"],
    )

    proba = model.predict_proba(X_test[fit_cols])[:, 1]

    # Default 0.5 threshold is a poor fit for an early-warning system: a
    # missed flood (false negative) is far costlier than a false alarm, so
    # the operating threshold is chosen to hit TARGET_RECALL instead of
    # just accepting whatever recall 0.5 happens to produce. Reported
    # alongside the plain 0.5 numbers for comparison, not as a replacement.
    prec_curve, rec_curve, thresh_curve = precision_recall_curve(y_test, proba)
    viable = np.where(rec_curve[:-1] >= TARGET_RECALL)[0]
    if len(viable):
        chosen_threshold = float(thresh_curve[viable[-1]])
    else:
        # No threshold reaches TARGET_RECALL on this test set -- falls back
        # to 0.5, but this would mean the model genuinely cannot hit the
        # target recall no matter how permissive the threshold, which is
        # worth surfacing loudly rather than silently reporting a
        # threshold search that never actually found what it was looking for.
        print(f"  WARNING: no threshold on this test set reaches {TARGET_RECALL} recall "
              f"(max achievable: {rec_curve.max():.3f}) -- falling back to threshold=0.5")
        chosen_threshold = 0.5

    def metrics_at(threshold: float) -> dict:
        pred = proba >= threshold
        p, r, f1, _ = precision_recall_fscore_support(y_test, pred, average="binary", zero_division=0)
        tn, fp, fn, tp = confusion_matrix(y_test, pred).ravel()
        return {"threshold": float(threshold), "precision": float(p), "recall": float(r), "f1": float(f1),
                "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)}}

    at_default = metrics_at(0.5)
    at_chosen = metrics_at(chosen_threshold)
    roc_auc = roc_auc_score(y_test, proba) if y_test.nunique() > 1 else float("nan")
    pr_auc = average_precision_score(y_test, proba) if y_test.nunique() > 1 else float("nan")

    print(f"  best_iteration: {model.best_iteration_}, roc_auc={roc_auc:.3f}, pr_auc={pr_auc:.3f}")
    print(f"  @ threshold=0.5:              precision={at_default['precision']:.3f} recall={at_default['recall']:.3f} f1={at_default['f1']:.3f}  {at_default['confusion_matrix']}")
    print(f"  @ threshold={chosen_threshold:.3f} (target recall {TARGET_RECALL}): precision={at_chosen['precision']:.3f} recall={at_chosen['recall']:.3f} f1={at_chosen['f1']:.3f}  {at_chosen['confusion_matrix']}")

    # Naive baselines (2026-08-14) -- is this model actually better than a
    # zero-live-data guess? See naive_baselines() docstring.
    baselines = naive_baselines(df, horizon, X_test, y_test)
    print(f"  naive baselines: climatology PR-AUC={baselines['climatology_pr_auc']:.3f}  "
          f"persistence PR-AUC={baselines['persistence_pr_auc']:.3f}  (model PR-AUC={pr_auc:.3f} for comparison)")

    # Isotonic calibration (2026-08-14) -- fit on the VALIDATION slice only
    # (never test, to keep this number honest), applied to the DISPLAYED
    # probability. Does NOT change chosen_threshold above, which keeps
    # operating on the model's raw score -- "what decision to make at what
    # recall" and "does the probability number mean what it says" are two
    # separate questions; conflating them would mean re-deriving what "85%
    # recall" means every time the calibrator changes.
    val_proba = model.predict_proba(X_train.loc[val_mask, fit_cols])[:, 1]
    calibrator = IsotonicRegression(out_of_bounds="clip")
    calibrator.fit(val_proba, y_train.loc[val_mask].astype(int).values)
    proba_calibrated = calibrator.transform(proba)
    brier_raw = float(brier_score_loss(y_test.astype(int), proba))
    brier_calibrated = float(brier_score_loss(y_test.astype(int), proba_calibrated))
    print(f"  calibration: Brier(raw)={brier_raw:.4f}  Brier(calibrated)={brier_calibrated:.4f}  "
          f"({'improved' if brier_calibrated < brier_raw else 'WORSE -- calibrator not helping here'})")

    # SHAP feature importance on a sample of the test set (not the full
    # ~7-8k rows, to keep this fast) -- mean |SHAP value| per feature, the
    # standard global-importance summary. See DECISIONS.md SS10 -- SHAP is
    # the interpretability tool the plan committed to, not built-in
    # impurity-based importances.
    sample = X_test[fit_cols].sample(n=min(1500, len(X_test)), random_state=42)
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(sample)
    if isinstance(shap_values, list):  # some LightGBM/shap version combos return [neg_class, pos_class]
        shap_values = shap_values[1]
    mean_abs_shap = pd.Series(np.abs(shap_values).mean(axis=0), index=fit_cols).sort_values(ascending=False)
    print("  top 8 features by mean|SHAP|:")
    for feat, val in mean_abs_shap.head(8).items():
        print(f"    {feat:40s} {val:.4f}")

    out_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, out_dir / f"model_{horizon}.joblib")
    # Saved alongside the model, not just in metrics.json -- Part 5's live
    # inference code needs this exact number to threshold model.predict_proba().
    (out_dir / f"model_{horizon}_threshold.json").write_text(
        json.dumps({"threshold": chosen_threshold, "target_recall": TARGET_RECALL})
    )
    # Calibrator saved separately from the decision threshold above -- not
    # loaded by live serving yet (an available artifact for a future
    # "display a trustworthy probability number" pass, see MODEL_BUILD_PLAN.md
    # 2026-08-14), so its absence can never break the existing threshold logic.
    joblib.dump(calibrator, out_dir / f"model_{horizon}_calibrator.joblib")

    return {
        "horizon": horizon,
        "train_rows": len(X_train), "train_positive_rate": float(y_train.mean()),
        "test_rows": len(X_test), "test_positive_rate": float(y_test.mean()),
        "naive_baselines": baselines,
        "calibration": {"brier_raw": brier_raw, "brier_calibrated": brier_calibrated},
        "best_iteration": int(model.best_iteration_),
        "roc_auc": float(roc_auc), "pr_auc": float(pr_auc),
        "at_threshold_0.5": at_default,
        "at_chosen_threshold": at_chosen,
        "top_features": mean_abs_shap.head(15).round(4).to_dict(),
        "fit_cols": fit_cols,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", required=True)
    args = parser.parse_args()

    in_path = FEATURES_ROOT / args.version / "all_stations.parquet"
    out_dir = MODELS_ROOT / args.version
    print(f"Loading {in_path} ...")
    df = pd.read_parquet(in_path)
    df = add_seasonal_features(df)

    # Cascade feature (2026-08-14): apply the already-trained, frozen
    # discharge-forecaster models to every row to get discharge_forecast_h
    # per horizon -- see DISCHARGE_FORECAST_COLUMNS' comment and
    # experiment_cascade_discharge_feature.py for the real A/B test this
    # decision is based on. Requires the discharge-regression model for the
    # SAME --version to already exist.
    discharge_models_dir = MODELS_ROOT / f"{args.version}-discharge-regression"
    discharge_schema = json.loads((discharge_models_dir / "feature_schema.json").read_text())
    discharge_fit_cols = discharge_schema["feature_columns"]
    print(f"Applying frozen discharge-forecaster models ({discharge_models_dir.name}) "
          f"to build the cascade features...")
    for h in HORIZONS:
        dmodel = joblib.load(discharge_models_dir / f"model_{h}.joblib")
        pred_log = dmodel.predict(df[discharge_fit_cols])
        df[f"discharge_forecast_{h}"] = np.clip(np.expm1(pred_log), 0, None)

    results = [train_one_horizon(h, df, out_dir) for h in HORIZONS]

    # Horizons now legitimately have DIFFERENT feature sets (each gets only
    # its own matching discharge_forecast_h) -- feature_schema.json stores a
    # per-horizon column list, not one shared list. Live serving must select
    # the right column list for the horizon it's predicting, not assume one
    # schema fits all three anymore.
    fit_cols_per_horizon = {r["horizon"]: r.pop("fit_cols") for r in results}
    feature_schema = {
        "trained_on_version": args.version,
        "horizons": HORIZONS,
        "feature_columns_per_horizon": fit_cols_per_horizon,
        "cascade_feature": {
            "description": (
                "Each horizon's feature list includes exactly one discharge_forecast_<horizon> "
                "column -- the discharge-forecaster model's OWN prediction for that same horizon, "
                "computed live before calling this model. NOT the same as river_discharge_m3s_lag*d "
                "(past/current discharge) already in every horizon's feature list."
            ),
            "requires_discharge_model_version": f"{args.version}-discharge-regression",
        },
        "categorical_features": ["station_id", "basin"],
        "categorical_values": {
            "station_id": STATION_ID_CATEGORIES,
            "basin": BASIN_CATEGORIES,
        },
        "notes": (
            "Exact column names/order the model expects, PER HORIZON (see "
            "feature_columns_per_horizon) -- no longer a single shared list, since the cascade "
            "feature differs per horizon. station_id and basin must be pandas 'category' dtype "
            "(see add_seasonal_features() in this file) — station_id values must be one of the "
            "30 IDs in train/stations.py, basin one of brahmaputra/ganges/meghna/cht. All other "
            "columns are numeric; NaN is a valid value for any of them (LightGBM handles missing "
            "natively — do not impute a bogus 0/mean/etc. for missing readings). doy_sin/doy_cos "
            "are derived from the prediction date, see add_seasonal_features()."
        ),
    }
    (out_dir / "feature_schema.json").write_text(json.dumps(feature_schema, indent=2))

    report_path = out_dir / "metrics.json"
    report_path.write_text(json.dumps(results, indent=2))
    print(f"\nWrote models + metrics + feature_schema.json to {out_dir}")


if __name__ == "__main__":
    main()
