"""Real trained-model serving wrapper for the LightGBM flood-risk models
(train/train_model.py, see DECISIONS.md SS14). Loads the 3 per-horizon
models + their tuned decision thresholds + feature_schema.json for a given
model version, and exposes a single predict() call for Part 5's live
endpoint to use.

THIS MODULE DOES NOT GATHER LIVE DATA -- that's app/services/live_features.py
(built 2026-08-09, Part 5), which assembles the exact feature dict this
module expects from Open-Meteo's live forecast/flood APIs, reusing
train/build_features.py's own lag/rolling/SWI functions so the live and
trained feature for the same name are computed identically. This module
only knows how to turn an already-assembled feature dict into a
prediction, enforcing the exact feature-schema contract (column names/
order, categorical encoding) train_model.py established.

Wired into app/main.py as of 2026-08-09, replacing app/models/risk_model.py
-- the old SYNTHETIC-DATA PLACEHOLDER (train/train_placeholder_model.py, 5
hand-picked features, fake training data). risk_model.py is kept in the
tree for reference/rollback but is no longer imported by main.py.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import joblib
import pandas as pd

from train.stations import STATIONS

MODELS_ROOT = Path(__file__).resolve().parent.parent.parent / "models"

_STATION_BASIN = {s.station_id: s.basin for s in STATIONS}


@dataclass
class HorizonPrediction:
    horizon: str          # "24h" | "48h" | "72h"
    probability: float    # model.predict_proba, i.e. P(flood within this horizon)
    threshold: float      # this horizon's tuned decision threshold (85% recall on the 2024-2026 test set)
    risk_level: str       # "low" | "moderate" | "high" -- see _score_to_level for how this is derived


class FloodGBMModel:
    """Loads one trained model version's artifacts and serves predictions.

    Usage:
        model = FloodGBMModel.load("2026-08-07c")
        predictions = model.predict(features, station_id="SW90", prediction_date=pd.Timestamp.now())
    """

    def __init__(self, version: str, root: Path):
        self.version = version
        self.schema = json.loads((root / "feature_schema.json").read_text())
        self.feature_columns: list[str] = self.schema["feature_columns"]
        self.categorical_values: dict[str, list[str]] = self.schema["categorical_values"]
        self.horizons: list[str] = self.schema["horizons"]

        self._models: dict[str, object] = {}
        self._thresholds: dict[str, float] = {}
        for horizon in self.horizons:
            self._models[horizon] = joblib.load(root / f"model_{horizon}.joblib")
            threshold_info = json.loads((root / f"model_{horizon}_threshold.json").read_text())
            self._thresholds[horizon] = threshold_info["threshold"]

    @classmethod
    def load(cls, version: str, models_root: Path | None = None) -> "FloodGBMModel":
        root = (models_root or MODELS_ROOT) / version
        if not root.exists():
            raise FileNotFoundError(
                f"No trained model artifacts at {root}. Run "
                f"`python train/train_model.py --version <features_version>` first."
            )
        return cls(version, root)

    def _build_row(self, features: dict, station_id: str, prediction_date: pd.Timestamp) -> pd.DataFrame:
        # station_id/basin/doy_sin/doy_cos are derived here, not expected in
        # `features` -- everything else in feature_columns must be present
        # as a KEY (NaN is a fine VALUE -- LightGBM handles missing
        # natively -- but an absent key almost always means a caller forgot
        # to compute something, which should fail loudly, not silently).
        derived = {"station_id", "basin", "doy_sin", "doy_cos"}
        missing_keys = [c for c in self.feature_columns if c not in features and c not in derived]
        if missing_keys:
            raise ValueError(
                f"Missing required feature keys (NaN values are fine, missing KEYS are not): {missing_keys}"
            )
        if station_id not in self.categorical_values["station_id"]:
            raise ValueError(
                f"Unknown station_id {station_id!r}, expected one of {self.categorical_values['station_id']}"
            )

        row = dict(features)
        row["station_id"] = station_id
        row["basin"] = _STATION_BASIN[station_id]

        # Must match add_seasonal_features() in train/train_model.py exactly.
        doy = prediction_date.dayofyear
        days_in_year = 366 if prediction_date.is_leap_year else 365
        angle = 2 * math.pi * doy / days_in_year
        row["doy_sin"] = math.sin(angle)
        row["doy_cos"] = math.cos(angle)

        df = pd.DataFrame([row])[self.feature_columns]
        # Explicit category lists pinned to what training used (see
        # train_model.py's STATION_ID_CATEGORIES/BASIN_CATEGORIES comment --
        # a single-row frame with an implicit astype("category") would
        # otherwise assign category code 0 regardless of the actual
        # station, silently corrupting the prediction).
        df["station_id"] = pd.Categorical(df["station_id"], categories=self.categorical_values["station_id"])
        df["basin"] = pd.Categorical(df["basin"], categories=self.categorical_values["basin"])
        return df

    def predict(self, features: dict, station_id: str, prediction_date: pd.Timestamp) -> list[HorizonPrediction]:
        row = self._build_row(features, station_id, prediction_date)
        results = []
        for horizon in self.horizons:
            proba = float(self._models[horizon].predict_proba(row)[:, 1][0])
            threshold = self._thresholds[horizon]
            results.append(HorizonPrediction(
                horizon=horizon, probability=proba, threshold=threshold,
                risk_level=self._score_to_level(proba, threshold),
            ))
        return results

    @staticmethod
    def _score_to_level(proba: float, threshold: float) -> str:
        # 3-tier mapping anchored on this horizon's own tuned threshold
        # (chosen for 85% recall, DECISIONS.md SS14): "high" at/above the
        # alert threshold, "moderate" in its lower half, "low" below that.
        # A defensible default, not a retrained/calibrated boundary --
        # Part 5 or the frontend can adjust tier cutoffs freely since it's
        # a presentation choice layered on top of the same probability,
        # not something that requires touching the model.
        if proba >= threshold:
            return "high"
        if proba >= threshold / 2:
            return "moderate"
        return "low"


BASIN_LABELS = {
    "brahmaputra": "Brahmaputra/Jamuna",
    "meghna": "Surma-Meghna",
    "ganges": "Ganges-Padma",
    "cht": "Chittagong Hill Tracts",
}


def _is_nan(v) -> bool:
    return isinstance(v, float) and math.isnan(v)


def build_reasoning(
    features: dict, predictions: list[HorizonPrediction], basin: str | None, station_name: str | None
) -> list[str]:
    """Plain-language explanation grounded in the SAME features the model
    actually used (train/build_features.py's SHAP analysis, DECISIONS.md
    SS14/SS18, found rainfall_local_mm_sum14d and doy_sin/doy_cos as the
    top-ranked features on every horizon, with soil_moisture_swi in the
    top 6-8) -- these bullets lead with those, not an arbitrary feature
    order, so the explanation reflects what actually drove the score."""
    reasons = []
    basin_label = BASIN_LABELS.get(basin) if basin else None
    if basin_label and station_name:
        reasons.append(
            f"Nearest gauge: {station_name} ({basin_label} basin) -- flooding here is often driven by "
            "upstream monsoon rainfall in India/Nepal as much as local rain."
        )

    sum14d = features.get("rainfall_local_mm_sum14d")
    if sum14d is not None and not _is_nan(sum14d):
        if sum14d > 150:
            reasons.append(f"Heavy local rainfall over the past 14 days ({sum14d:.0f} mm).")
        elif sum14d > 60:
            reasons.append(f"Moderate local rainfall over the past 14 days ({sum14d:.0f} mm).")
        else:
            reasons.append(f"Local rainfall over the past 14 days has been light ({sum14d:.0f} mm).")

    trend = features.get("rainfall_local_mm_trend_ratio")
    if trend is not None and not _is_nan(trend):
        if trend > 1.5:
            reasons.append("Rainfall has been intensifying compared to the prior week.")
        elif trend < 0.5:
            reasons.append("Rainfall has been easing compared to the prior week.")

    delta30 = features.get("soil_moisture_delta_30d")
    if delta30 is not None and not _is_nan(delta30):
        if delta30 > 0.03:
            reasons.append("Soil is notably wetter than it was a month ago, meaning less capacity to absorb more rain.")
        elif delta30 < -0.03:
            reasons.append("Soil is drier than it was a month ago.")

    discharge = features.get("river_discharge_m3s")
    if features.get("river_discharge_m3s_missing"):
        reasons.append("Live river discharge data was unavailable for this forecast; relying on rainfall and soil moisture only.")
    elif discharge is not None and not _is_nan(discharge):
        reasons.append(f"Current river discharge near this gauge is {discharge:,.0f} m³/s.")

    upstream_keys = [
        "upstream_reference_discharge_lag2d", "upstream_reference_discharge_lag3d",
        "upstream_chain_discharge_lag1d", "upstream_chain_discharge_lag2d",
    ]
    if any(not _is_nan(features.get(k)) for k in upstream_keys if features.get(k) is not None):
        reasons.append("An upstream discharge reading (India-side or an upstream in-network gauge) is factored in as a leading indicator.")

    horizon_bits = ", ".join(f"{p.horizon} {p.risk_level}" for p in predictions)
    reasons.append(f"Risk by horizon: {horizon_bits}.")
    return reasons
