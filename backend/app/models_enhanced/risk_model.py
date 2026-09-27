"""Wrapper around the flood-risk classifier used for inference.

IMPORTANT: the shipped model artifact is trained on SYNTHETIC data (see
train/train_placeholder_model.py) purely so the API has a working
end-to-end prediction path. It is NOT trained on real FFWC/CHIRPS/GPM
history yet and its outputs should not be treated as real flood risk
until retrained on real historical data.

SUPERSEDED as of 2026-08-09 (Part 5): app/main.py now loads
app/models/flood_gbm_model.py's FloodGBMModel (the real LightGBM models,
backend/models/) instead of this synthetic placeholder. Kept in the tree
for reference/rollback, not deleted -- nothing currently imports this
module.
"""

from pathlib import Path

import joblib
import numpy as np

from app.config import settings

FEATURE_NAMES = [
    "past_7d_rain_mm",
    "past_14d_rain_mm",
    "forecast_3d_rain_mm",
    "rain_trend_ratio",
    "station_level_ratio",
]

RISK_THRESHOLDS = {"low": 0.34, "moderate": 0.67}  # score >= moderate threshold -> "high"

MODEL_VERSION = "placeholder-synthetic-v0.1"

BASIN_LABELS = {
    "brahmaputra": "Brahmaputra/Jamuna",
    "meghna": "Surma-Meghna",
    "ganges": "Ganges-Padma",
}


class RiskModel:
    def __init__(self, estimator):
        self._estimator = estimator

    @classmethod
    def load(cls, path: str | Path | None = None) -> "RiskModel":
        model_path = Path(path or settings.model_path)
        if not model_path.exists():
            raise FileNotFoundError(
                f"No model artifact at {model_path}. Run `python train/train_placeholder_model.py` first."
            )
        return cls(joblib.load(model_path))

    def predict(self, features: dict[str, float]) -> tuple[float, str]:
        x = np.array([[features[name] for name in FEATURE_NAMES]])
        score = float(self._estimator.predict_proba(x)[0, 1])
        level = self._score_to_level(score)
        return score, level

    @staticmethod
    def _score_to_level(score: float) -> str:
        if score < RISK_THRESHOLDS["low"]:
            return "low"
        if score < RISK_THRESHOLDS["moderate"]:
            return "moderate"
        return "high"


def build_reasoning(
    features: dict[str, float], risk_level: str, has_station_data: bool, basin: str | None = None
) -> list[str]:
    reasons = []
    basin_label = BASIN_LABELS.get(basin) if basin else None
    if basin_label:
        reasons.append(
            f"This area drains into the {basin_label} river system, where flooding is often "
            "driven by upstream monsoon rainfall in India and Nepal rather than local rain alone."
        )

    if features["past_14d_rain_mm"] > 150:
        reasons.append(
            f"Heavy rainfall over the past 14 days ({features['past_14d_rain_mm']:.0f} mm) raises upstream runoff."
        )
    elif features["past_14d_rain_mm"] > 60:
        reasons.append(f"Moderate rainfall over the past 14 days ({features['past_14d_rain_mm']:.0f} mm).")
    else:
        reasons.append(f"Rainfall over the past 14 days has been light ({features['past_14d_rain_mm']:.0f} mm).")

    if features["forecast_3d_rain_mm"] > 80:
        reasons.append(f"Forecast shows heavy rain ahead ({features['forecast_3d_rain_mm']:.0f} mm over 3 days).")
    elif features["forecast_3d_rain_mm"] > 30:
        reasons.append(f"Some rain is forecast over the next 3 days ({features['forecast_3d_rain_mm']:.0f} mm).")

    if features["rain_trend_ratio"] > 1.5:
        reasons.append("Rainfall has been intensifying compared to the prior week.")
    elif features["rain_trend_ratio"] < 0.5:
        reasons.append("Rainfall has been easing compared to the prior week.")

    if not has_station_data:
        reasons.append(
            "No live water-level reading is available for the nearest FFWC station yet; "
            "this assessment currently relies on rainfall data only."
        )

    reasons.append(f"Overall assessed risk: {risk_level}.")
    return reasons
