"""Loads the 3 trained LightGBM discharge-forecasting models (24h/48h/72h)
and serves predictions from an already-assembled feature dict (see
live_features.py for how to build one).

Target transform: the models were trained on log1p(discharge) -- see
train/train_regression_model.py's docstring for why (river discharge spans
~5 orders of magnitude across stations; a plain squared-error objective on
raw m3/s would be dominated entirely by the largest rivers). Predictions
are back-transformed here via expm1 and clipped at 0 (discharge can't be
negative).
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import joblib
import pandas as pd

from stations import STATIONS

MODELS_DIR = Path(__file__).resolve().parent / "models"

_STATION_BASIN = {s.station_id: s.basin for s in STATIONS}


@dataclass
class HorizonForecast:
    horizon: str              # "24h" | "48h" | "72h"
    predicted_discharge_m3s: float
    current_discharge_m3s: float | None  # today's own reading, for comparison
    trend: str                # "rising" | "falling" | "steady" | "unknown"


class DischargeForecastModel:
    """Usage:
        model = DischargeForecastModel.load()
        forecasts = model.predict(features, station_id="SW90", prediction_date=pd.Timestamp.now())
    """

    def __init__(self, root: Path):
        self.schema = json.loads((root / "feature_schema.json").read_text())
        self.feature_columns: list[str] = self.schema["feature_columns"]
        self.categorical_values: dict[str, list[str]] = self.schema["categorical_values"]
        self.horizons: list[str] = self.schema["horizons"]

        self._models: dict[str, object] = {}
        for horizon in self.horizons:
            self._models[horizon] = joblib.load(root / f"model_{horizon}.joblib")

    @classmethod
    def load(cls, models_dir: Path | None = None) -> "DischargeForecastModel":
        root = models_dir or MODELS_DIR
        if not root.exists():
            raise FileNotFoundError(f"No model artifacts at {root}")
        return cls(root)

    def _build_row(self, features: dict, station_id: str, prediction_date: pd.Timestamp) -> pd.DataFrame:
        derived = {"station_id", "basin", "doy_sin", "doy_cos"}
        missing_keys = [c for c in self.feature_columns if c not in features and c not in derived]
        if missing_keys:
            raise ValueError(f"Missing required feature keys (NaN values are fine, missing KEYS are not): {missing_keys}")
        if station_id not in self.categorical_values["station_id"]:
            raise ValueError(f"Unknown station_id {station_id!r}, expected one of {self.categorical_values['station_id']}")

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

    def predict(self, features: dict, station_id: str, prediction_date: pd.Timestamp) -> list[HorizonForecast]:
        row = self._build_row(features, station_id, prediction_date)
        current = features.get("river_discharge_m3s")
        current = None if current is None or (isinstance(current, float) and math.isnan(current)) else float(current)

        results = []
        for horizon in self.horizons:
            pred_log = float(self._models[horizon].predict(row)[0])
            predicted = max(0.0, math.expm1(pred_log))
            if current is None:
                trend = "unknown"
            elif predicted > current * 1.05:
                trend = "rising"
            elif predicted < current * 0.95:
                trend = "falling"
            else:
                trend = "steady"
            results.append(HorizonForecast(
                horizon=horizon, predicted_discharge_m3s=round(predicted, 1),
                current_discharge_m3s=current, trend=trend,
            ))
        return results
