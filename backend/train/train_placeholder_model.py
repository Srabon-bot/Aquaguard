"""Trains a PLACEHOLDER flood-risk classifier on synthetic data.

This exists only so the API has a working inference path end-to-end before
real historical FFWC water-level + CHIRPS/GPM rainfall data has been
collected and labeled. The synthetic generator below encodes a rough,
plausible relationship (more/heavier rain -> higher risk) but is not
calibrated to real Bangladesh flood events.

Once real historical data is available, replace `make_synthetic_dataset`
with a loader for the real feature/label table and retrain the same way
(swap GradientBoostingClassifier for LightGBM/XGBoost if desired).

Usage:
    python train/train_placeholder_model.py
"""

from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split

from app.models.risk_model import FEATURE_NAMES

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "app" / "models" / "artifacts" / "risk_model.joblib"
N_SAMPLES = 5000
RANDOM_SEED = 42


def make_synthetic_dataset(n: int, rng: np.random.Generator):
    past_7d = rng.gamma(shape=2.0, scale=20.0, size=n)  # mm
    past_14d = past_7d + rng.gamma(shape=2.0, scale=25.0, size=n)
    forecast_3d = rng.gamma(shape=1.5, scale=15.0, size=n)
    trend_ratio = np.clip(rng.normal(loc=1.0, scale=0.5, size=n), 0.05, 4.0)
    station_level_ratio = np.clip(rng.normal(loc=0.5, scale=0.2, size=n), 0.0, 1.3)

    # Latent "flood pressure" score combining the signals, plus noise, then
    # thresholded into a binary label the classifier learns to reconstruct.
    pressure = (
        0.015 * past_14d
        + 0.02 * forecast_3d
        + 0.3 * (trend_ratio - 1.0)
        + 0.8 * station_level_ratio
        + rng.normal(0, 0.3, size=n)
    )
    label = (pressure > np.quantile(pressure, 0.7)).astype(int)

    x = np.column_stack([past_7d, past_14d, forecast_3d, trend_ratio, station_level_ratio])
    return x, label


def main():
    rng = np.random.default_rng(RANDOM_SEED)
    x, y = make_synthetic_dataset(N_SAMPLES, rng)
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=RANDOM_SEED)

    clf = GradientBoostingClassifier(random_state=RANDOM_SEED)
    clf.fit(x_train, y_train)
    train_acc = clf.score(x_train, y_train)
    test_acc = clf.score(x_test, y_test)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(clf, OUTPUT_PATH)

    print(f"Trained on synthetic data. Features: {FEATURE_NAMES}")
    print(f"Train accuracy: {train_acc:.3f} | Test accuracy: {test_acc:.3f}")
    print(f"Saved model to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
