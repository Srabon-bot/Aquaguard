from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

RiskLevel = Literal["low", "moderate", "high"]


class DistrictInfo(BaseModel):
    district: str
    upazila: str
    lat: float
    lon: float
    basin: str


class DistrictsResponse(BaseModel):
    districts: list[DistrictInfo]


class ResolvedLocation(BaseModel):
    district: str | None = None
    upazila: str | None = None
    lat: float
    lon: float
    basin: str | None = None


class DataSources(BaseModel):
    rainfall: str = "Open-Meteo forecast API (local point + 9-point upstream basin grid, past 90 days)"
    soil_moisture: str = "Open-Meteo forecast API (0-7cm depth, local point)"
    discharge: str = "Open-Meteo flood API (GloFAS reanalysis/forecast)"
    station_level: str | None = None


class HorizonRisk(BaseModel):
    horizon: Literal["24h", "48h", "72h"]
    risk_level: RiskLevel
    probability: float = Field(ge=0.0, le=1.0)
    threshold: float = Field(ge=0.0, le=1.0, description="This horizon's tuned decision threshold (85% recall).")


class RiskResponse(BaseModel):
    # protected_namespaces=() silences pydantic's warning about
    # `model_version` colliding with its reserved "model_" prefix.
    model_config = {"protected_namespaces": ()}

    location: ResolvedLocation
    nearest_station: str | None = None
    horizons: list[HorizonRisk]
    # Mirrors the highest-priority horizon (24h) for callers that just want
    # a single headline level/score rather than all three -- see main.py.
    risk_level: RiskLevel
    risk_score: float = Field(ge=0.0, le=1.0)
    horizon_hours: int = 24
    generated_at: datetime
    reasoning: list[str]
    features_used: dict[str, float | bool | None]
    model_version: str
    data_sources: DataSources


class ErrorResponse(BaseModel):
    detail: str
