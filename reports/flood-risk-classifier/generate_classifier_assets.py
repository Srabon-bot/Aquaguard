"""Regenerates every figure used in Flood_Risk_Classifier_Model_Report.pdf
from the real trained model + real data on disk. Deepens the calibration
testing beyond the single Brier-score number train_model.py already reports
(2026-08-14) -- adds reliability diagrams (predicted vs. observed frequency
per bin), Expected Calibration Error (ECE), and log loss, so the "isotonic
calibration helped" claim rests on more than one proper scoring rule.

Usage:
    python reports/generate_classifier_assets.py
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
from sklearn.calibration import calibration_curve
from sklearn.metrics import (
    ConfusionMatrixDisplay, PrecisionRecallDisplay, RocCurveDisplay,
    confusion_matrix, log_loss, precision_recall_curve, roc_auc_score, average_precision_score,
)

ROOT = Path(__file__).resolve().parent.parent.parent
TRAIN_DIR = ROOT / "backend" / "train"
sys.path.insert(0, str(TRAIN_DIR))
from train_model import add_seasonal_features, time_split, naive_baselines  # noqa: E402

ASSETS = Path(__file__).resolve().parent / "assets"
ASSETS.mkdir(exist_ok=True)

VERSION = "2026-08-07c"
MODELS_DIR = ROOT / "backend" / "models" / VERSION
FEATURES_PATH = ROOT / "backend" / "data" / "features" / VERSION / "all_stations.parquet"
HORIZONS = ["24h", "48h", "72h"]

plt.rcParams.update({"font.size": 10, "figure.dpi": 150, "savefig.bbox": "tight"})
HORIZON_COLORS = {"24h": "#2a78d6", "48h": "#a06b09", "72h": "#d03b3b"}


def save(fig, name):
    path = ASSETS / name
    fig.savefig(path)
    plt.close(fig)
    print(f"  wrote {path}")


def expected_calibration_error(y_true, proba, n_bins=10) -> float:
    """ECE: bin predictions by confidence, weight each bin's |predicted -
    observed| gap by how many points fall in it. Standard calibration
    metric, reported alongside Brier score and log loss (not a replacement
    for either -- three different properness/calibration angles on the
    same question, not redundant with each other)."""
    bins = np.linspace(0, 1, n_bins + 1)
    bin_idx = np.digitize(proba, bins[1:-1])
    ece = 0.0
    for b in range(n_bins):
        mask = bin_idx == b
        if mask.sum() == 0:
            continue
        conf = proba[mask].mean()
        acc = y_true[mask].mean()
        ece += (mask.sum() / len(proba)) * abs(conf - acc)
    return float(ece)


def main():
    print(f"Loading {FEATURES_PATH} ...")
    df = pd.read_parquet(FEATURES_PATH)
    df = add_seasonal_features(df)
    schema = json.loads((MODELS_DIR / "feature_schema.json").read_text())
    fit_cols = schema["feature_columns"]

    metrics = json.loads((MODELS_DIR / "metrics.json").read_text())
    metrics_by_horizon = {m["horizon"]: m for m in metrics}

    calib_summary = {}

    # === Per-horizon: ROC/PR/confusion + calibration reliability diagram ===
    for h in HORIZONS:
        model = joblib.load(MODELS_DIR / f"model_{h}.joblib")
        calibrator = joblib.load(MODELS_DIR / f"model_{h}_calibrator.joblib")
        X_train, y_train, X_test, y_test = time_split(df, h)
        proba = model.predict_proba(X_test[fit_cols])[:, 1]
        proba_cal = calibrator.transform(proba)
        y = y_test.astype(int).values

        # --- ROC / PR / confusion ---
        threshold = json.loads((MODELS_DIR / f"model_{h}_threshold.json").read_text())["threshold"]
        fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
        RocCurveDisplay.from_predictions(y, proba, ax=axes[0], color=HORIZON_COLORS[h])
        axes[0].plot([0, 1], [0, 1], "k--", lw=1, alpha=0.5)
        axes[0].set_title(f"ROC curve ({h})")
        PrecisionRecallDisplay.from_predictions(y, proba, ax=axes[1], color="#0ca30c")
        axes[1].axhline(y.mean(), color="gray", ls="--", lw=1, label=f"baseline (positive rate={y.mean():.3f})")
        axes[1].legend(fontsize=8)
        axes[1].set_title("Precision-Recall curve")
        pred = (proba >= threshold).astype(int)
        cm = confusion_matrix(y, pred)
        ConfusionMatrixDisplay(cm, display_labels=["no flood", "flood"]).plot(ax=axes[2], cmap="Blues", colorbar=False)
        axes[2].set_title(f"Confusion matrix @ threshold={threshold:.3f}\n(tuned for 85% recall)")
        fig.suptitle(f"Held-out test set, {h} horizon (test date >= 2024-01-01, 'observed' regime only)", y=1.03)
        save(fig, f"fig_{h}_roc_pr_confusion.png")

        # --- Calibration reliability diagram: raw vs. calibrated ---
        frac_pos_raw, mean_pred_raw = calibration_curve(y, proba, n_bins=10, strategy="quantile")
        frac_pos_cal, mean_pred_cal = calibration_curve(y, proba_cal, n_bins=10, strategy="quantile")
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.plot([0, 1], [0, 1], "k--", lw=1, alpha=0.5, label="perfect calibration")
        ax.plot(mean_pred_raw, frac_pos_raw, "o-", color="#d03b3b", label="raw (uncalibrated)")
        ax.plot(mean_pred_cal, frac_pos_cal, "o-", color="#0ca30c", label="isotonic-calibrated")
        ax.set_xlabel("Mean predicted probability (per bin)")
        ax.set_ylabel("Observed flood frequency (per bin)")
        ax.set_title(f"Reliability diagram, {h} horizon\n(quantile-binned, 10 bins, held-out test set)")
        ax.legend(fontsize=9)
        save(fig, f"fig_{h}_calibration_reliability.png")

        ece_raw = expected_calibration_error(y, proba)
        ece_cal = expected_calibration_error(y, proba_cal)
        ll_raw = float(log_loss(y, np.clip(proba, 1e-6, 1 - 1e-6)))
        ll_cal = float(log_loss(y, np.clip(proba_cal, 1e-6, 1 - 1e-6)))
        calib_summary[h] = {
            "ece_raw": round(ece_raw, 4), "ece_calibrated": round(ece_cal, 4),
            "log_loss_raw": round(ll_raw, 4), "log_loss_calibrated": round(ll_cal, 4),
            "brier_raw": metrics_by_horizon[h]["calibration"]["brier_raw"],
            "brier_calibrated": metrics_by_horizon[h]["calibration"]["brier_calibrated"],
        }
        print(f"{h}: ECE raw={ece_raw:.4f} -> calibrated={ece_cal:.4f}   "
              f"log_loss raw={ll_raw:.4f} -> calibrated={ll_cal:.4f}")

    (ASSETS / "calibration_summary.json").write_text(json.dumps(calib_summary, indent=2))

    # === Combined 3-horizon calibration reliability figure ===
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for i, h in enumerate(HORIZONS):
        model = joblib.load(MODELS_DIR / f"model_{h}.joblib")
        calibrator = joblib.load(MODELS_DIR / f"model_{h}_calibrator.joblib")
        _, _, X_test, y_test = time_split(df, h)
        proba = model.predict_proba(X_test[fit_cols])[:, 1]
        proba_cal = calibrator.transform(proba)
        y = y_test.astype(int).values
        frac_pos_raw, mean_pred_raw = calibration_curve(y, proba, n_bins=10, strategy="quantile")
        frac_pos_cal, mean_pred_cal = calibration_curve(y, proba_cal, n_bins=10, strategy="quantile")
        axes[i].plot([0, 1], [0, 1], "k--", lw=1, alpha=0.5)
        axes[i].plot(mean_pred_raw, frac_pos_raw, "o-", color="#d03b3b", label="raw")
        axes[i].plot(mean_pred_cal, frac_pos_cal, "o-", color="#0ca30c", label="calibrated")
        axes[i].set_title(h)
        axes[i].set_xlabel("Predicted probability")
        if i == 0:
            axes[i].set_ylabel("Observed frequency")
        axes[i].legend(fontsize=8)
    fig.suptitle("Calibration reliability, all 3 horizons")
    save(fig, "fig_calibration_all_horizons.png")

    # === Naive baseline comparison bar chart ===
    fig, ax = plt.subplots(figsize=(7, 4.5))
    x = np.arange(len(HORIZONS))
    width = 0.25
    model_pr = [metrics_by_horizon[h]["pr_auc"] for h in HORIZONS]
    clim_pr = [metrics_by_horizon[h]["naive_baselines"]["climatology_pr_auc"] for h in HORIZONS]
    pers_pr = [metrics_by_horizon[h]["naive_baselines"]["persistence_pr_auc"] for h in HORIZONS]
    ax.bar(x - width, clim_pr, width, label="Climatology baseline", color="#a06b09")
    ax.bar(x, model_pr, width, label="Trained model", color="#2a78d6")
    ax.bar(x + width, pers_pr, width, label="Persistence baseline", color="#0ca30c")
    ax.set_xticks(x)
    ax.set_xticklabels(HORIZONS)
    ax.set_ylabel("PR-AUC (held-out test set)")
    ax.set_title("Model vs. naive baselines, all 3 horizons")
    ax.legend()
    save(fig, "fig_baseline_comparison.png")

    # === SHAP feature importance (top 12, 24h horizon) ===
    top_features = metrics_by_horizon["24h"]["top_features"]
    items = sorted(top_features.items(), key=lambda kv: kv[1])[-12:]
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.barh([k for k, _ in items], [v for _, v in items], color="#2a78d6")
    ax.set_xlabel("Mean |SHAP value|")
    ax.set_title("Feature importance, 24h horizon model")
    save(fig, "fig_feature_importance.png")

    # === Persistence's precision/recall vs model's, matched-recall check ===
    h = "24h"
    model = joblib.load(MODELS_DIR / f"model_{h}.joblib")
    _, _, X_test, y_test = time_split(df, h)
    proba = model.predict_proba(X_test[fit_cols])[:, 1]
    prec, rec, thresh = precision_recall_curve(y_test, proba)
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(rec, prec, color="#2a78d6", label="Model (full PR curve)")
    ax.scatter([0.616], [0.616], color="#0ca30c", s=100, zorder=5, label="Persistence baseline (24h)\n(precision=recall=0.616)")
    idx = np.argmin(np.abs(rec[:-1] - 0.616))
    ax.scatter([rec[idx]], [prec[idx]], color="#d03b3b", s=100, zorder=5,
               label=f"Model @ matched recall\n(precision={prec[idx]:.3f})")
    ax.set_xlabel("Recall"); ax.set_ylabel("Precision")
    ax.set_title("Model vs. persistence at matched recall, 24h horizon")
    ax.legend(fontsize=8)
    save(fig, "fig_persistence_matched_recall.png")

    print(f"\nAll figures written to {ASSETS}")


if __name__ == "__main__":
    main()
