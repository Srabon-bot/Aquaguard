"""Regenerates every figure used in Flood_Susceptibility_Model_Report.pdf
from the real trained model + real data on disk -- nothing here is a mockup
or a hand-drawn illustrative number. Run before build_susceptibility_report.py.

Usage:
    python reports/generate_susceptibility_assets.py
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
from sklearn.metrics import (
    ConfusionMatrixDisplay, RocCurveDisplay, PrecisionRecallDisplay,
    confusion_matrix, precision_recall_curve, roc_curve, average_precision_score, roc_auc_score,
)

ROOT = Path(__file__).resolve().parent.parent.parent
TRAIN_DIR = ROOT / "backend" / "train"
sys.path.insert(0, str(TRAIN_DIR))
from stations import STATIONS  # noqa: E402
from train_susceptibility_model import FEATURE_COLUMNS, CATEGORICAL, held_out_test_stations  # noqa: E402

ASSETS = Path(__file__).resolve().parent / "assets"
ASSETS.mkdir(exist_ok=True)

DATA_PATH = ROOT / "backend" / "data" / "susceptibility" / "susceptibility_training_table.csv"
TERRAIN_PATH = ROOT / "backend" / "data_raw" / "susceptibility" / "grid_point_terrain.csv"
COUNTS_PATH = ROOT / "backend" / "data_raw" / "susceptibility" / "grid_point_flood_counts.csv"
MODELS_DIR = ROOT / "backend" / "models" / "susceptibility"
PER_STATION_PATH = MODELS_DIR / "per_station_susceptibility.csv"

BASIN_COLORS = {"brahmaputra": "#2a78d6", "ganges": "#0ca30c", "meghna": "#a06b09", "cht": "#d03b3b"}
plt.rcParams.update({"font.size": 10, "figure.dpi": 150, "savefig.bbox": "tight"})


def save(fig, name):
    path = ASSETS / name
    fig.savefig(path)
    plt.close(fig)
    print(f"  wrote {path}")


def fig_station_map():
    per_station = pd.read_csv(PER_STATION_PATH)
    station_by_id = {s.station_id: s for s in STATIONS}
    per_station["lat"] = per_station["station_id"].map(lambda i: station_by_id[i].lat)
    per_station["lon"] = per_station["station_id"].map(lambda i: station_by_id[i].lon)

    fig, ax = plt.subplots(figsize=(6.5, 7))
    sc = ax.scatter(per_station["lon"], per_station["lat"], c=per_station["mean_proba"],
                     cmap="YlOrRd", s=140, edgecolors="black", linewidths=0.6, vmin=0, vmax=0.45)
    for _, row in per_station.iterrows():
        ax.annotate(row["station_id"], (row["lon"], row["lat"]), fontsize=6.5,
                    xytext=(4, 3), textcoords="offset points")
    plt.colorbar(sc, ax=ax, label="Mean susceptibility score", shrink=0.8)
    ax.set_xlabel("Longitude"); ax.set_ylabel("Latitude")
    ax.set_title("30 monitored stations, colored by mean susceptibility score\n(plain lat/lon scatter, not a GIS basemap)")
    ax.set_aspect("equal")
    save(fig, "fig_station_map.png")


def fig_station_bar():
    per_station = pd.read_csv(PER_STATION_PATH).sort_values("mean_proba", ascending=True)
    station_by_id = {s.station_id: s for s in STATIONS}
    colors = [BASIN_COLORS[station_by_id[i].basin] for i in per_station["station_id"]]

    fig, ax = plt.subplots(figsize=(7, 9))
    ax.barh(per_station["station_id"], per_station["mean_proba"], color=colors)
    ax.set_xlabel("Mean susceptibility score (across 49 local grid points)")
    ax.set_title("Per-station susceptibility, all 30 stations")
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in BASIN_COLORS.values()]
    ax.legend(handles, BASIN_COLORS.keys(), title="Basin", loc="lower right", fontsize=8)
    save(fig, "fig_station_bar.png")


def fig_feature_importance():
    metrics = json.loads((MODELS_DIR / "metrics.json").read_text())
    importances = metrics["feature_importance_shap"]
    items = sorted(importances.items(), key=lambda kv: kv[1])
    fig, ax = plt.subplots(figsize=(6.5, 3.5))
    ax.barh([k for k, _ in items], [v for _, v in items], color="#2a78d6")
    ax.set_xlabel("Mean |SHAP value| (held-out test set)")
    ax.set_title("Feature importance, final Random Forest model")
    save(fig, "fig_feature_importance.png")


def fig_cv_comparison():
    metrics = json.loads((MODELS_DIR / "metrics.json").read_text())
    fig, ax = plt.subplots(figsize=(6.5, 4))
    x = np.arange(4)
    width = 0.35
    for i, (name, label, color) in enumerate([("lightgbm", "LightGBM", "#a06b09"), ("random_forest", "Random Forest", "#2a78d6")]):
        aucs = [f["roc_auc"] for f in metrics["cv_comparison"][name]["cv_folds"]]
        ax.bar(x + (i - 0.5) * width, aucs, width, label=label, color=color)
    ax.axhline(metrics["cv_comparison"]["lightgbm"]["cv_mean_roc_auc"], color="#a06b09", ls="--", lw=1, alpha=0.6)
    ax.axhline(metrics["cv_comparison"]["random_forest"]["cv_mean_roc_auc"], color="#2a78d6", ls="--", lw=1, alpha=0.6)
    ax.set_xticks(x); ax.set_xticklabels([f"Fold {i}" for i in range(4)])
    ax.set_ylabel("ROC-AUC"); ax.set_ylim(0.7, 1.0)
    ax.set_title("Spatial GroupKFold CV: LightGBM vs Random Forest\n(dashed lines = mean across folds)")
    ax.legend()
    save(fig, "fig_cv_comparison.png")


def _load_test_xy():
    df = pd.read_csv(DATA_PATH)
    for col in CATEGORICAL:
        df[col] = df[col].astype("category")
    test_stations = held_out_test_stations()
    test_df = df[df["station_id"].isin(test_stations)].reset_index(drop=True)
    X_test = test_df[FEATURE_COLUMNS].copy()
    for col in CATEGORICAL:
        X_test[col] = X_test[col].cat.codes
    y_test = test_df["label"]
    return X_test, y_test, sorted(test_stations)


def fig_roc_pr_confusion():
    model = joblib.load(MODELS_DIR / "susceptibility_random_forest.joblib")
    X_test, y_test, test_stations = _load_test_xy()
    proba = model.predict_proba(X_test)[:, 1]

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    RocCurveDisplay.from_predictions(y_test, proba, ax=axes[0], color="#2a78d6")
    axes[0].plot([0, 1], [0, 1], "k--", lw=1, alpha=0.5)
    axes[0].set_title(f"ROC curve (held-out: {', '.join(test_stations)})")

    PrecisionRecallDisplay.from_predictions(y_test, proba, ax=axes[1], color="#0ca30c")
    axes[1].axhline(y_test.mean(), color="gray", ls="--", lw=1, label=f"baseline (positive rate={y_test.mean():.2f})")
    axes[1].legend(fontsize=8)
    axes[1].set_title("Precision-Recall curve")

    pred = (proba >= 0.5).astype(int)
    cm = confusion_matrix(y_test, pred)
    ConfusionMatrixDisplay(cm, display_labels=["non-flooded", "flooded"]).plot(ax=axes[2], cmap="Blues", colorbar=False)
    axes[2].set_title("Confusion matrix @ threshold 0.5")

    fig.suptitle("Held-out spatial test set (7 stations, never touched during training/CV)", y=1.03)
    save(fig, "fig_roc_pr_confusion.png")

    return {
        "roc_auc": float(roc_auc_score(y_test, proba)),
        "pr_auc": float(average_precision_score(y_test, proba)),
        "n_test": int(len(y_test)),
        "confusion_matrix": cm.tolist(),
    }


def fig_nvalid_hist():
    counts = pd.read_csv(COUNTS_PATH)
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.hist(counts["n_valid"], bins=40, color="#2a78d6", edgecolor="white", linewidth=0.3)
    ax.axvline(200, color="#d03b3b", ls="--", label="negative-label threshold (200)")
    ax.set_xlabel("n_valid (independent SAR observations per grid point)")
    ax.set_ylabel("Number of grid points")
    ax.set_title("Observation depth per point, full 2016-2026 GFM archive\n(1,470 points total)")
    ax.legend()
    save(fig, "fig_nvalid_hist.png")


def fig_landcover_by_label():
    df = pd.read_csv(DATA_PATH)
    lc_names = {10: "tree", 20: "shrub", 30: "grassland", 40: "cropland", 50: "built-up",
                60: "bare", 70: "snow/ice", 80: "water", 90: "wetland", 95: "mangrove", 100: "moss"}
    df["lc_name"] = df["landcover_class"].map(lc_names)
    ct = pd.crosstab(df["lc_name"], df["label"], normalize="index") * 100
    ct = ct.reindex(ct.sort_values(1, ascending=False).index if 1 in ct.columns else ct.index)

    fig, ax = plt.subplots(figsize=(7, 4))
    ct.plot(kind="barh", stacked=True, ax=ax, color=["#0ca30c", "#d03b3b"])
    ax.set_xlabel("% of points in this land-cover class")
    ax.set_ylabel("")
    ax.legend(["non-flooded", "flooded"], title="Label")
    ax.set_title("Flooded-point rate by land-cover class")
    save(fig, "fig_landcover_by_label.png")


def fig_basin_comparison():
    per_station = pd.read_csv(PER_STATION_PATH)
    station_by_id = {s.station_id: s for s in STATIONS}
    per_station["basin"] = per_station["station_id"].map(lambda i: station_by_id[i].basin)
    grouped = per_station.groupby("basin")["mean_proba"].agg(["mean", "std", "count"]).reindex(BASIN_COLORS.keys())

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(grouped.index, grouped["mean"], yerr=grouped["std"], capsize=5,
           color=[BASIN_COLORS[b] for b in grouped.index])
    ax.set_ylabel("Mean susceptibility score")
    ax.set_title("Susceptibility by basin (error bars = std. dev. across stations)")
    for i, (b, row) in enumerate(grouped.iterrows()):
        ax.annotate(f"n={int(row['count'])}", (i, row["mean"] + row["std"] + 0.01), ha="center", fontsize=8)
    save(fig, "fig_basin_comparison.png")


def fig_class_balance():
    counts = pd.read_csv(COUNTS_PATH)
    n_total = len(counts)
    n_pos = (counts["n_flooded"] > 0).sum()
    n_zero_cov = (counts["n_valid"] == 0).sum()
    n_neg = ((counts["n_flooded"] == 0) & (counts["n_valid"] >= 200)).sum()
    n_dropped_low_n = n_total - n_pos - n_neg - n_zero_cov

    labels = ["Flooded\n(positive)", "Non-flooded\n(negative)", "Dropped:\ninsufficient obs.", "Dropped:\nno tile coverage"]
    values = [n_pos, n_neg, n_dropped_low_n, n_zero_cov]
    colors = ["#d03b3b", "#0ca30c", "#a06b09", "#676d7c"]
    fig, ax = plt.subplots(figsize=(6.5, 4))
    bars = ax.bar(labels, values, color=colors)
    for b, v in zip(bars, values):
        ax.annotate(str(v), (b.get_x() + b.get_width() / 2, v + 8), ha="center", fontsize=9)
    ax.set_ylabel("Number of grid points (of 1,470 total)")
    ax.set_title("Final label composition")
    save(fig, "fig_class_balance.png")


def main():
    print("Generating figures from real data + real trained model...")
    fig_station_map()
    fig_station_bar()
    fig_feature_importance()
    fig_cv_comparison()
    test_metrics = fig_roc_pr_confusion()
    fig_nvalid_hist()
    fig_landcover_by_label()
    fig_basin_comparison()
    fig_class_balance()

    (ASSETS / "recomputed_test_metrics.json").write_text(json.dumps(test_metrics, indent=2))
    print("\nRecomputed held-out test metrics (should match backend/models/susceptibility/metrics.json):")
    print(json.dumps(test_metrics, indent=2))
    print(f"\nAll figures written to {ASSETS}")


if __name__ == "__main__":
    main()
