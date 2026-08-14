"""Part 4 pivot -- trains 3 independent LightGBM REGRESSORS (one per
discharge_target_24h/48h/72h) on the discharge-regression feature table
from build_regression_targets.py. Sits alongside, not instead of,
train_model.py's flood_within_Nh classifiers -- see DECISIONS.md SS23 for
why this pivot exists and build_regression_targets.py's docstring for why
discharge is a more tractable target than a rare binary flood flag.

WRITES TO A SEPARATE MODEL DIRECTORY (backend/models/<version>-discharge-
regression/) -- backend/models/<version>/ (the classifier) is never
touched by this script.

TARGET TRANSFORM -- log1p(discharge), not raw m3/s. Real, verified reason:
station discharge spans ~5 orders of magnitude (checked directly: station
means range from ~2 m3/s at ME03/Dhaka's Buriganga to ~39,000 m3/s at
ME01's Padma-Meghna confluence). A plain L2/MSE objective on raw m3/s
would be completely dominated by the largest-magnitude stations' squared
error, effectively training a Jamuna/Padma-only model that ignores small
rivers' predictive accuracy. log1p makes the loss behave like a RELATIVE
(percentage-ish) error across every station's own scale instead, and
handles the exact-zero discharge values a couple of small coastal stations
have (log1p(0)=0, plain log(0) is undefined). Predictions are back-
transformed (expm1) for real-unit (m3/s) reporting.

HONEST BASELINE -- discharge is highly autocorrelated day-to-day (today's
discharge is a strong predictor of tomorrow's by simple physical
persistence, not because a model learned anything deep), so a naive
"tomorrow = today" persistence baseline is reported ALONGSIDE the trained
model's metrics for every horizon. A model that only matches persistence
has added no real skill even if its raw R²/MAE numbers look good in
isolation -- this project's own standing practice (SS10/SS14/SS18) is to
compare against a naive baseline rather than quote a number without context.

TRAIN/TEST SPLIT -- same TEST_CUTOFF as the classifier (2024-01-01) for a
directly comparable evaluation period, but simpler: discharge has no
GFMS-style "accessible window"/label-regime complexity to account for
(see build_regression_targets.py), so it's a plain date-based split with
no regime filtering.

Usage:
    python train/train_regression_model.py --version 2026-08-07c
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
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, mean_squared_error, r2_score

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stations import STATIONS  # noqa: E402

FEATURES_ROOT = Path(__file__).resolve().parent.parent / "data" / "features"
MODELS_ROOT = Path(__file__).resolve().parent.parent / "models"

HORIZONS = ["24h", "48h", "72h"]
TEST_CUTOFF = pd.Timestamp("2024-01-01")

STATION_BASIN = {s.station_id: s.basin for s in STATIONS}
STATION_ID_CATEGORIES = sorted(s.station_id for s in STATIONS)
BASIN_CATEGORIES = sorted(set(STATION_BASIN.values()))

TARGET_COLUMNS = {f"discharge_target_{h}" for h in HORIZONS}
# Same denylist reasoning as train_model.py: GFMS's flood_byStor has no live
# feed (permanent train-serve skew if included), and the classifier's own
# flood_within_Nh/label_regime columns are that OTHER model's targets, not
# inputs here -- mixing them in would be a strange, unnecessary coupling
# between two models meant to be independently evaluable.
NON_FEATURE_COLUMNS = {
    "date", "station_name",
    "flood_byStor", "flood_byStor_missing",
} | TARGET_COLUMNS | {f"flood_within_{h}" for h in HORIZONS} | {f"flood_within_{h}_label_regime" for h in HORIZONS}


def add_seasonal_features(df: pd.DataFrame) -> pd.DataFrame:
    doy = df["date"].dt.dayofyear
    days_in_year = np.where(df["date"].dt.is_leap_year, 366, 365)
    angle = 2 * np.pi * doy / days_in_year
    df["doy_sin"] = np.sin(angle)
    df["doy_cos"] = np.cos(angle)
    df["basin"] = df["station_id"].map(STATION_BASIN)
    # Explicit category lists, not implicit astype("category") -- same
    # reasoning as train_model.py: a live single-row prediction must get the
    # same category CODES train time used, or the model silently reads the
    # wrong station/basin. See that file's own comment for the full story.
    df["station_id"] = pd.Categorical(df["station_id"], categories=STATION_ID_CATEGORIES)
    df["basin"] = pd.Categorical(df["basin"], categories=BASIN_CATEGORIES)
    return df


def kge_with_components(y_true: np.ndarray, y_pred: np.ndarray) -> tuple[float, float, float, float]:
    """KGE = 1 - sqrt((r-1)^2 + (alpha-1)^2 + (beta-1)^2):
        r     = Pearson correlation (timing/shape agreement)
        alpha = std(pred)/std(true)  (variability ratio -- over/under-dispersed?)
        beta  = mean(pred)/mean(true) (bias ratio)
    Returns (kge, r, alpha, beta) -- the components, not just the final
    scalar, specifically so a low KGE can be diagnosed (module-level, not
    nested in metrics_for(), so both the pooled AND per-station breakdowns
    below can reuse the identical formula without drifting apart)."""
    std_true = np.std(y_true)
    if std_true == 0 or np.std(y_pred) == 0 or np.mean(y_true) == 0:
        return float("nan"), float("nan"), float("nan"), float("nan")  # degenerate slice -- don't fake a number
    r = float(np.corrcoef(y_true, y_pred)[0, 1])
    alpha = float(np.std(y_pred) / std_true)
    beta = float(np.mean(y_pred) / np.mean(y_true))
    kge = float(1 - np.sqrt((r - 1) ** 2 + (alpha - 1) ** 2 + (beta - 1) ** 2))
    return kge, r, alpha, beta


def feature_columns(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if c not in NON_FEATURE_COLUMNS]


def time_split(df: pd.DataFrame, horizon: str) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    target_col = f"discharge_target_{horizon}"
    labeled = df[df[target_col].notna() & df["river_discharge_m3s"].notna()].copy()

    train_mask = labeled["date"] < TEST_CUTOFF
    test_mask = labeled["date"] >= TEST_CUTOFF

    cols = feature_columns(labeled) + ["date"]
    X_train, y_train = labeled.loc[train_mask, cols], labeled.loc[train_mask, target_col]
    X_test, y_test = labeled.loc[test_mask, cols], labeled.loc[test_mask, target_col]
    return X_train, y_train, X_test, y_test


def train_one_horizon(horizon: str, df: pd.DataFrame, out_dir: Path) -> dict:
    print(f"\n=== Horizon: {horizon} ===")
    X_train, y_train, X_test, y_test = time_split(df, horizon)
    print(f"  train: {len(X_train)} rows, test: {len(X_test)} rows")

    val_cutoff = X_train["date"].quantile(0.85, interpolation="nearest")
    val_mask = X_train["date"] >= val_cutoff
    fit_cols = [c for c in X_train.columns if c != "date"]

    y_train_log = np.log1p(y_train)

    model = lgb.LGBMRegressor(
        n_estimators=1000,
        learning_rate=0.03,
        num_leaves=31,
        max_depth=-1,
        min_child_samples=40,
        feature_fraction=0.85,
        bagging_fraction=0.85,
        bagging_freq=1,
        random_state=42,
        verbosity=-1,
    )
    model.fit(
        X_train.loc[~val_mask, fit_cols], y_train_log.loc[~val_mask],
        eval_X=X_train.loc[val_mask, fit_cols], eval_y=y_train_log.loc[val_mask],
        eval_metric="rmse",
        callbacks=[lgb.early_stopping(stopping_rounds=50, verbose=False)],
        categorical_feature=["station_id", "basin"],
    )

    pred_log = model.predict(X_test[fit_cols])
    pred = np.expm1(pred_log)
    pred = np.clip(pred, 0, None)  # discharge can't be negative; a log1p model shouldn't produce this, but don't trust it blindly

    # Persistence baseline: "tomorrow's discharge = today's discharge" -- see
    # module docstring. Reported for every metric so the trained model's
    # real added value (or lack of it) is visible, not just its raw score.
    persistence_pred = X_test["river_discharge_m3s"].values

    def metrics_for(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
        # NSE (Nash-Sutcliffe Efficiency) and KGE (Kling-Gupta Efficiency) --
        # added per the literature-research pass on 2026-08-14: "the most
        # widely used indices in hydrology for evaluation of streamflow
        # models" (MODEL_BUILD_PLAN.md same-day entry). Computed on the RAW
        # m3/s scale, same as every other metric here, so they're directly
        # comparable to how the hydrology literature reports them -- not on
        # the log1p-transformed scale the model actually optimizes (that's
        # log_space_rmse, reported separately). See kge_with_components()
        # for the r/alpha/beta breakdown -- exposed here too, not just the
        # final scalar, so a low KGE can actually be diagnosed (is it a
        # timing problem, a spread problem, or a bias problem?).
        nse = float(r2_score(y_true, y_pred))
        kge, r, alpha, beta = kge_with_components(y_true, y_pred)
        return {
            "mae_m3s": float(mean_absolute_error(y_true, y_pred)),
            "rmse_m3s": float(np.sqrt(mean_squared_error(y_true, y_pred))),
            "mape_pct": float(mean_absolute_percentage_error(
                np.where(y_true == 0, 1e-6, y_true), y_pred  # avoid div-by-zero on the rare exact-0 discharge day
            ) * 100),
            "r2": float(r2_score(y_true, y_pred)),
            "nse": nse,
            "kge": kge,
            "kge_r": r, "kge_alpha": alpha, "kge_beta": beta,
        }

    model_metrics = metrics_for(y_test.values, pred)
    baseline_metrics = metrics_for(y_test.values, persistence_pred)
    log_rmse = float(np.sqrt(mean_squared_error(np.log1p(y_test.values), pred_log)))

    # Per-station NSE, not just pooled -- added alongside NSE/KGE themselves
    # (2026-08-14 literature-research pass) after checking directly: pooling
    # all 30 stations before computing NSE lets between-station variance
    # (discharge spans ~4 orders of magnitude across stations) inflate the
    # number relative to genuine within-station day-to-day predictive skill.
    # Real check, not assumed: pooled NSE came out at 0.996 for 24h, but the
    # per-station MEDIAN was 0.989 and one station (Dhaka's Buriganga, the
    # smallest-discharge station in the network) came out at 0.56 -- a real,
    # actionable weak point the pooled number alone would have hidden.
    pred_series = pd.Series(pred, index=X_test.index)
    per_station_nse: dict[str, float] = {}
    per_station_kge: dict[str, float] = {}
    for sid, idx in X_test.groupby("station_id", observed=True).groups.items():
        if len(idx) < 10:
            continue
        yt, yp = y_test.loc[idx].values, pred_series.loc[idx].values
        ss_res = float(np.sum((yt - yp) ** 2))
        ss_tot = float(np.sum((yt - yt.mean()) ** 2))
        per_station_nse[sid] = round(1 - ss_res / ss_tot, 4) if ss_tot > 0 else float("nan")
        station_kge, _, _, _ = kge_with_components(yt, yp)
        per_station_kge[sid] = round(station_kge, 4)

    print(f"  best_iteration: {model.best_iteration_}")
    print(f"  log-space RMSE (what the model optimizes): {log_rmse:.4f}")
    print(f"  model:       MAE={model_metrics['mae_m3s']:.1f} m3/s  RMSE={model_metrics['rmse_m3s']:.1f} m3/s  "
          f"MAPE={model_metrics['mape_pct']:.1f}%  R2={model_metrics['r2']:.4f}  "
          f"NSE={model_metrics['nse']:.4f}  KGE={model_metrics['kge']:.4f}")
    print(f"  persistence: MAE={baseline_metrics['mae_m3s']:.1f} m3/s  RMSE={baseline_metrics['rmse_m3s']:.1f} m3/s  "
          f"MAPE={baseline_metrics['mape_pct']:.1f}%  R2={baseline_metrics['r2']:.4f}  "
          f"NSE={baseline_metrics['nse']:.4f}  KGE={baseline_metrics['kge']:.4f}")
    skill_vs_persistence = 1 - (model_metrics["mae_m3s"] / baseline_metrics["mae_m3s"])
    print(f"  MAE improvement over persistence: {skill_vs_persistence*100:+.1f}%"
          f"{'  (WORSE than just guessing no change)' if skill_vs_persistence < 0 else ''}")
    worst_stations = sorted(per_station_nse.items(), key=lambda kv: kv[1])[:3]
    print(f"  per-station NSE: median={np.median(list(per_station_nse.values())):.4f} "
          f"(pooled NSE above can be inflated by between-station variance -- this is the honest number)")
    print(f"  weakest stations: {worst_stations}")

    sample = X_test[fit_cols].sample(n=min(1500, len(X_test)), random_state=42)
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(sample)
    mean_abs_shap = pd.Series(np.abs(shap_values).mean(axis=0), index=fit_cols).sort_values(ascending=False)
    print("  top 8 features by mean|SHAP| (log-discharge space):")
    for feat, val in mean_abs_shap.head(8).items():
        print(f"    {feat:40s} {val:.4f}")

    out_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, out_dir / f"model_{horizon}.joblib")

    return {
        "horizon": horizon,
        "train_rows": len(X_train), "test_rows": len(X_test),
        "best_iteration": int(model.best_iteration_),
        "log_space_rmse": log_rmse,
        "model_metrics": model_metrics,
        "persistence_baseline_metrics": baseline_metrics,
        "mae_improvement_over_persistence_pct": float(skill_vs_persistence * 100),
        "per_station_nse": per_station_nse,
        "per_station_nse_median": float(np.median(list(per_station_nse.values()))),
        "per_station_kge": per_station_kge,
        "per_station_kge_median": float(np.nanmedian(list(per_station_kge.values()))),
        "top_features": mean_abs_shap.head(15).round(4).to_dict(),
        "fit_cols": fit_cols,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", required=True,
                         help="reads data/features/<version>-discharge-regression/all_stations.parquet, "
                              "writes to backend/models/<version>-discharge-regression/")
    args = parser.parse_args()

    features_dir_name = f"{args.version}-discharge-regression"
    in_path = FEATURES_ROOT / features_dir_name / "all_stations.parquet"
    out_dir = MODELS_ROOT / features_dir_name
    print(f"Loading {in_path} ...")
    df = pd.read_parquet(in_path)
    df = add_seasonal_features(df)

    results = [train_one_horizon(h, df, out_dir) for h in HORIZONS]

    fit_cols_per_horizon = [r.pop("fit_cols") for r in results]
    assert all(cols == fit_cols_per_horizon[0] for cols in fit_cols_per_horizon), (
        "Horizons disagree on feature columns -- investigate before shipping feature_schema.json."
    )
    feature_schema = {
        "trained_on_version": features_dir_name,
        "model_type": "discharge_regression",
        "target_transform": "log1p (predictions back-transformed via expm1, clipped at 0)",
        "horizons": HORIZONS,
        "feature_columns": fit_cols_per_horizon[0],
        "categorical_features": ["station_id", "basin"],
        "categorical_values": {
            "station_id": STATION_ID_CATEGORIES,
            "basin": BASIN_CATEGORIES,
        },
        "notes": (
            "Predicts river_discharge_m3s N hours ahead (log1p-transformed target, "
            "expm1 + clip(0) at inference). station_id/basin must be pandas 'category' "
            "dtype with these exact category lists, same reasoning as the flood "
            "classifier's feature_schema.json. This is a SEPARATE model from the "
            "flood_within_Nh classifier -- see DECISIONS.md SS23."
        ),
    }
    (out_dir / "feature_schema.json").write_text(json.dumps(feature_schema, indent=2))

    report_path = out_dir / "metrics.json"
    report_path.write_text(json.dumps(results, indent=2))
    print(f"\nWrote models + metrics + feature_schema.json to {out_dir}")


if __name__ == "__main__":
    main()
