"""Regenerates every figure used in Discharge_Forecaster_Model_Report.pdf
from the real trained model + real data on disk, including the deepened
NSE/KGE diagnostics added 2026-08-14 (per-station KGE, the r/alpha/beta
component breakdown that explains the 24h "model KGE < persistence KGE"
finding, and predicted-vs-actual scatter plots).

Usage:
    python reports/generate_discharge_assets.py
"""

import json
import sys
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent
TRAIN_DIR = ROOT / "backend" / "train"
sys.path.insert(0, str(TRAIN_DIR))
from stations import STATIONS  # noqa: E402
from train_regression_model import add_seasonal_features, time_split  # noqa: E402

ASSETS = Path(__file__).resolve().parent / "assets"
ASSETS.mkdir(exist_ok=True)

VERSION = "2026-08-07c-discharge-regression"
MODELS_DIR = ROOT / "backend" / "models" / VERSION
FEATURES_PATH = ROOT / "backend" / "data" / "features" / VERSION / "all_stations.parquet"
HORIZONS = ["24h", "48h", "72h"]
BASIN_COLORS = {"brahmaputra": "#2a78d6", "ganges": "#0ca30c", "meghna": "#a06b09", "cht": "#d03b3b"}
STATION_BASIN = {s.station_id: s.basin for s in STATIONS}

plt.rcParams.update({"font.size": 10, "figure.dpi": 150, "savefig.bbox": "tight"})


def save(fig, name):
    path = ASSETS / name
    fig.savefig(path)
    plt.close(fig)
    print(f"  wrote {path}")


def main():
    print(f"Loading {FEATURES_PATH} ...")
    df = pd.read_parquet(FEATURES_PATH)
    df = add_seasonal_features(df)
    schema = json.loads((MODELS_DIR / "feature_schema.json").read_text())
    fit_cols = schema["feature_columns"]
    metrics = json.loads((MODELS_DIR / "metrics.json").read_text())
    metrics_by_horizon = {m["horizon"]: m for m in metrics}

    # === NSE/KGE bar chart: model vs persistence, all horizons ===
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
    x = np.arange(len(HORIZONS))
    width = 0.35
    for ax, metric, title in [(axes[0], "nse", "NSE"), (axes[1], "kge", "KGE")]:
        model_vals = [metrics_by_horizon[h]["model_metrics"][metric] for h in HORIZONS]
        pers_vals = [metrics_by_horizon[h]["persistence_baseline_metrics"][metric] for h in HORIZONS]
        ax.bar(x - width / 2, model_vals, width, label="Model", color="#2a78d6")
        ax.bar(x + width / 2, pers_vals, width, label="Persistence", color="#0ca30c")
        ax.set_xticks(x); ax.set_xticklabels(HORIZONS)
        ax.set_title(f"{title} (pooled, all stations)")
        ax.set_ylim(min(model_vals + pers_vals) - 0.02, 1.0)
        ax.legend(fontsize=8)
    fig.suptitle("Model vs. persistence baseline: NSE and KGE")
    save(fig, "fig_nse_kge_comparison.png")

    # === KGE component breakdown (r, alpha, beta) ===
    fig, ax = plt.subplots(figsize=(8, 5))
    components = ["kge_r", "kge_alpha", "kge_beta"]
    labels = ["r (correlation)", "alpha (variability ratio)", "beta (bias ratio)"]
    x = np.arange(len(components))
    width = 0.12
    for i, h in enumerate(HORIZONS):
        model_c = [metrics_by_horizon[h]["model_metrics"][c] for c in components]
        pers_c = [metrics_by_horizon[h]["persistence_baseline_metrics"][c] for c in components]
        ax.bar(x + (i - 1) * width * 2, model_c, width, label=f"Model {h}", color=plt.cm.Blues(0.4 + i * 0.2))
        ax.bar(x + (i - 1) * width * 2 + width, pers_c, width, label=f"Persistence {h}", color=plt.cm.Greens(0.4 + i * 0.2))
    ax.axhline(1.0, color="k", ls="--", lw=1, alpha=0.5, label="ideal = 1.0")
    ax.set_xticks(x); ax.set_xticklabels(labels)
    # Zoomed to where the real differences are -- all values sit in a ~2%
    # band near 1.0, so a 0-1 axis would compress every bar into a sliver
    # and hide the exact pattern this chart exists to show.
    all_vals = [metrics_by_horizon[h]["model_metrics"][c] for h in HORIZONS for c in components] + \
               [metrics_by_horizon[h]["persistence_baseline_metrics"][c] for h in HORIZONS for c in components]
    ax.set_ylim(min(all_vals) - 0.005, 1.003)
    ax.set_title("KGE components: model vs. persistence (zoomed)\n(explains why model KGE < persistence KGE at short horizons)")
    ax.legend(fontsize=7, ncol=2, loc="lower left")
    save(fig, "fig_kge_components.png")

    # === Per-station NSE bar chart (24h) ===
    per_station_nse = metrics_by_horizon["24h"]["per_station_nse"]
    items = sorted(per_station_nse.items(), key=lambda kv: kv[1])
    colors = [BASIN_COLORS[STATION_BASIN[sid]] for sid, _ in items]
    fig, ax = plt.subplots(figsize=(7, 9))
    ax.barh([k for k, _ in items], [v for _, v in items], color=colors)
    ax.set_xlabel("Per-station NSE (24h horizon, held-out test)")
    ax.set_title("Per-station NSE, all 30 stations\n(pooled NSE=0.996, median=0.989 -- ME03 is the clear outlier)")
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in BASIN_COLORS.values()]
    ax.legend(handles, BASIN_COLORS.keys(), title="Basin", loc="lower right", fontsize=8)
    save(fig, "fig_per_station_nse.png")

    # === ME03 degradation with lead time ===
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    me03_nse = [metrics_by_horizon[h]["per_station_nse"]["ME03"] for h in HORIZONS]
    other_median = [metrics_by_horizon[h]["per_station_nse_median"] for h in HORIZONS]
    ax.plot(HORIZONS, me03_nse, "o-", color="#d03b3b", label="ME03 (Dhaka/Buriganga)", linewidth=2)
    ax.plot(HORIZONS, other_median, "o-", color="#2a78d6", label="Median across all 30 stations", linewidth=2)
    ax.set_ylabel("NSE"); ax.set_title("The one station that degrades sharply with lead time")
    ax.legend()
    save(fig, "fig_me03_degradation.png")

    # === Predicted vs actual scatter, per horizon (log-log) ===
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for i, h in enumerate(HORIZONS):
        model = joblib.load(MODELS_DIR / f"model_{h}.joblib")
        _, _, X_test, y_test = time_split(df, h)
        pred = np.clip(np.expm1(model.predict(X_test[fit_cols])), 0, None)
        axes[i].scatter(y_test.values, pred, s=4, alpha=0.15, color="#2a78d6")
        lim = max(y_test.max(), pred.max())
        axes[i].plot([1, lim], [1, lim], "k--", lw=1, alpha=0.6)
        axes[i].set_xscale("log"); axes[i].set_yscale("log")
        axes[i].set_xlabel("Actual discharge (m3/s)")
        axes[i].set_ylabel("Predicted discharge (m3/s)" if i == 0 else "")
        axes[i].set_title(f"{h} (NSE={metrics_by_horizon[h]['model_metrics']['nse']:.3f})")
    fig.suptitle("Predicted vs. actual discharge, held-out test set (log-log)")
    save(fig, "fig_predicted_vs_actual.png")

    print(f"\nAll figures written to {ASSETS}")


if __name__ == "__main__":
    main()
