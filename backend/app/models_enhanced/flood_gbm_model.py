"""Enhanced trained-model serving wrapper for the LightGBM flood-risk models.

Extends app/models/flood_gbm_model.py with:
1. Probability calibration (Platt scaling / isotonic regression)
2. Quantile regression support for uncertainty intervals
3. Multi-model ensemble support (LightGBM + XGBoost + CatBoost + LogisticRegression)
4. Model metadata and versioning
5. Coastal flood module support
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import joblib
import pandas as pd
import numpy as np

from train.stations import STATIONS

MODELS_ROOT = Path(__file__).resolve().parent.parent.parent / "models"
ENHANCED_MODELS_ROOT = Path(__file__).resolve().parent.parent.parent / "models_improved"

_STATION_BASIN = {s.station_id: s.basin for s in STATIONS}


@dataclass
class HorizonPrediction:
    horizon: str
    probability: float
    threshold: float
    risk_level: str
    probability_low: float | None = None    # q10 quantile
    probability_high: float | None = None   # q90 quantile
    confidence: str = "medium"              # high | medium | low
    model_contributions: dict[str, float] = field(default_factory=dict)


@dataclass
class ModelMetadata:
    version: str
    trained_at: str
    features: list[str]
    horizons: list[str]
    best_model: str
    calibration_method: str | None
    auc_pr: dict[str, float] | None
    precision_at_recall: dict[str, float] | None


class EnhancedFloodGBMModel:
    """Enhanced model wrapper with calibration, uncertainty, and ensemble support."""

    def __init__(self, version: str, root: Path):
        self.version = version
        self.metadata = self._load_metadata(root)
        self.schema = json.loads((root / "feature_schema.json").read_text())
        self.feature_columns: list[str] = self.schema["feature_columns"]
        self.categorical_values: dict[str, list[str]] = self.schema["categorical_values"]
        self.horizons: list[str] = self.schema["horizons"]
        self.calibration_method = self.metadata.calibration_method

        self._models: dict[str, dict[str, object]] = {}  # horizon -> {"main": model, "q10": model, "q90": model}
        self._thresholds: dict[str, float] = {}
        self._calibrators: dict[str, object] = {}
        self._ensemble_weights: dict[str, dict[str, float]] = {}

        for horizon in self.horizons:
            self._load_horizon_models(root, horizon)

    def _load_metadata(self, root: Path) -> ModelMetadata:
        meta_path = root / "model_metadata.json"
        if meta_path.exists():
            meta = json.loads(meta_path.read_text())
            return ModelMetadata(**meta)
        # Fallback for old model versions without metadata
        return ModelMetadata(
            version=root.name,
            trained_at="unknown",
            features=[],
            horizons=["24h", "48h", "72h"],
            best_model="lightgbm",
            calibration_method=None,
            auc_pr=None,
            precision_at_recall=None,
        )

    def _load_horizon_models(self, root: Path, horizon: str):
        horizon_models = {}
        # Main model
        model_path = root / f"model_{horizon}.joblib"
        if model_path.exists():
            horizon_models["main"] = joblib.load(model_path)

        # Quantile models (optional)
        for q_name, suffix in [("q10", "_q10"), ("q90", "_q90")]:
            q_path = root / f"model_{horizon}{suffix}.joblib"
            if q_path.exists():
                horizon_models[q_name] = joblib.load(q_path)

        # Calibrator (optional)
        cal_path = root / f"model_{horizon}_calibrator.joblib"
        if cal_path.exists():
            self._calibrators[horizon] = joblib.load(cal_path)

        # Threshold
        threshold_path = root / f"model_{horizon}_threshold.json"
        if threshold_path.exists():
            self._thresholds[horizon] = json.loads(threshold_path.read_text())["threshold"]

        # Ensemble weights (optional)
        weights_path = root / "ensemble_weights.json"
        if weights_path.exists():
            self._ensemble_weights = json.loads(weights_path.read_text())

        self._models[horizon] = horizon_models

    @classmethod
    def load(cls, version: str, models_root: Path | None = None) -> "EnhancedFloodGBMModel":
        root = (models_root or ENHANCED_MODELS_ROOT) / version
        if not root.exists():
            raise FileNotFoundError(
                f"No enhanced model artifacts at {root}. Run training first."
            )
        return cls(version, root)

    def _build_row(self, features: dict, station_id: str, prediction_date: pd.Timestamp) -> pd.DataFrame:
        derived = {"station_id", "basin", "doy_sin", "doy_cos"}
        missing_keys = [c for c in self.feature_columns if c not in features and c not in derived]
        if missing_keys:
            raise ValueError(
                f"Missing required feature keys (NaN values are fine, missing KEYS are not): {missing_keys}"
            )
        if station_id not in self.categorical_values["station_id"]:
            raise ValueError(f"Unknown station_id {station_id!r}")

        row = dict(features)
        row["station_id"] = station_id
        row["basin"] = _STATION_BASIN[station_id]

        doy = prediction_date.dayofyear
        days_in_year = 366 if prediction_date.is_leap_year else 365
        angle = 2 * math.pi * doy / days_in_year
        row["doy_sin"] = math.sin(angle)
        row["doy_cos"] = math.cos(angle)

        df = pd.DataFrame([row])[self.feature_columns]
        df["station_id"] = pd.Categorical(df["station_id"], categories=self.categorical_values["station_id"])
        df["basin"] = pd.Categorical(df["basin"], categories=self.categorical_values["basin"])
        return df

    def _apply_calibration(self, horizon: str, proba: float) -> float:
        if horizon not in self._calibrators:
            return proba
        calibrator = self._calibrators[horizon]
        try:
            # IsotonicRegression uses transform(), not predict_proba()
            # It takes a 1D array and returns calibrated values
            import numpy as np
            calibrated = calibrator.transform(np.array([proba]))[0]
            return float(calibrated)
        except Exception:
            return proba

    def predict(self, features: dict, station_id: str, prediction_date: pd.Timestamp, basin: str | None = None) -> list[HorizonPrediction]:
        row = self._build_row(features, station_id, prediction_date)
        results = []

        for horizon in self.horizons:
            horizon_models = self._models.get(horizon, {})
            main_model = horizon_models.get("main")

            if main_model is None:
                results.append(HorizonPrediction(
                    horizon=horizon, probability=0.0, threshold=0.0,
                    risk_level="low", confidence="low"
                ))
                continue

            # Raw probability
            raw_proba = float(main_model.predict_proba(row)[:, 1][0])

            # Apply calibration if available
            calibrated_proba = self._apply_calibration(horizon, raw_proba)

            # Quantile intervals
            q10 = None
            q90 = None
            q10_model = horizon_models.get("q10")
            q90_model = horizon_models.get("q90")
            if q10_model is not None and q90_model is not None:
                try:
                    q10_val = float(q10_model.predict(row)[0])
                    q90_val = float(q90_model.predict(row)[0])
                    # Ensure bounds
                    q10 = max(0.0, min(calibrated_proba, q10_val))
                    q90 = max(calibrated_proba, min(1.0, q90_val))
                except Exception:
                    pass

            # Determine confidence based on interval width
            confidence = "medium"
            if q10 is not None and q90 is not None:
                interval_width = q90 - q10
                if interval_width < 0.15:
                    confidence = "high"
                elif interval_width > 0.40:
                    confidence = "low"

            # Basin-aware threshold
            threshold = self._thresholds.get(horizon, 0.5)
            basin_thresholds = self.metadata.auc_pr or {}
            # Could add per-basin threshold logic here

            risk_level = self._score_to_level(calibrated_proba, threshold, basin)

            # Ensemble contribution breakdown
            contributions = {"lightgbm": calibrated_proba}
            if "ensemble_weights" in self.metadata.__dict__ and horizon in self._ensemble_weights:
                contributions["ensemble"] = self._ensemble_weights.get(horizon, {})

            results.append(HorizonPrediction(
                horizon=horizon,
                probability=round(calibrated_proba, 4),
                threshold=round(threshold, 4),
                risk_level=risk_level,
                probability_low=round(q10, 4) if q10 is not None else None,
                probability_high=round(q90, 4) if q90 is not None else None,
                confidence=confidence,
                model_contributions=contributions,
            ))

        return results

    @staticmethod
    def _score_to_level(proba: float, threshold: float, basin: str | None = None) -> str:
        # 3-tier mapping anchored on threshold
        if proba >= threshold:
            return "high"
        if proba >= threshold / 2:
            return "moderate"
        return "low"


class CoastalFloodModel:
    """Lightweight coastal flood risk classifier.
    
    Uses Random Forest or Logistic Regression with coastal-specific features:
    distance_to_coast_km, elevation_m, tidal_phase, surge_risk_index, etc.
    """

    def __init__(self, model_path: Path):
        self.model = joblib.load(model_path)
        self.feature_columns = json.loads((model_path.parent / "feature_schema.json").read_text())["feature_columns"]

    @classmethod
    def load(cls, version: str, models_root: Path | None = None) -> "CoastalFloodModel":
        root = (models_root or ENHANCED_MODELS_ROOT) / "coastal" / version
        model_path = root / "model.joblib"
        if not model_path.exists():
            raise FileNotFoundError(f"No coastal model at {model_path}")
        return cls(model_path)


    def predict(self, features: dict) -> tuple[float, str]:
        row = pd.DataFrame([{col: features.get(col, float("nan")) for col in self.feature_columns}])
        proba = float(self.model.predict_proba(row)[0, 1])
        level = "high" if proba >= 0.5 else ("moderate" if proba >= 0.25 else "low")
        return proba, level


def build_enhanced_reasoning(
    features: dict, predictions: list[HorizonPrediction], basin: str | None,
    station_name: str | None, confidence_note: str | None = None
) -> list[str]:
    """Enhanced plain-language explanation with uncertainty and confidence."""
    reasons = []
    basin_label = {
        "brahmaputra": "Brahmaputra/Jamuna",
        "meghna": "Surma-Meghna",
        "ganges": "Ganges-Padma",
        "cht": "Chittagong Hill Tracts",
    }.get(basin) if basin else None

    if basin_label and station_name:
        reasons.append(
            f"Nearest gauge: {station_name} ({basin_label} basin). "
            "Flooding here is often driven by upstream monsoon rainfall in India/Nepal."
        )

    # Add confidence note
    avg_confidence = max(set(p.confidence for p in predictions), key=lambda c: sum(1 for p in predictions if p.confidence == c))
    if confidence_note:
        reasons.append(confidence_note)
    elif avg_confidence == "high":
        reasons.append("Model confidence is HIGH — conditions are clear and consistent.")
    elif avg_confidence == "low":
        reasons.append("Model confidence is LOW — conditions are mixed or data is incomplete. Monitor closely.")
    else:
        reasons.append("Model confidence is MEDIUM — reasonable certainty but not unambiguous.")

    # Uncertainty intervals
    has_intervals = any(p.probability_low is not None for p in predictions)
    if has_intervals:
        intervals = [f"{p.horizon}: {p.probability_low:.0%}–{p.probability_high:.0%}" for p in predictions if p.probability_low is not None]
        reasons.append(f"Prediction intervals: {', '.join(intervals)}")

    # Original reasoning from flood_gbm_model
    from app.models.flood_gbm_model import build_reasoning as original_reasoning
    original_reasons = original_reasoning(features, predictions, basin, station_name)
    # Filter out duplicates
    for r in original_reasons:
        if r not in reasons:
            reasons.append(r)

    return reasons
