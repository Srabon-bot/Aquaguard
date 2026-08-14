from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class StationInfo(BaseModel):
    station_id: str
    name: str
    river: str
    lat: float
    lon: float
    basin: str


class StationsResponse(BaseModel):
    stations: list[StationInfo]


class DataSources(BaseModel):
    rainfall: str = "Open-Meteo forecast API (local point + 9-point upstream basin grid, past 90 days)"
    soil_moisture: str = "Open-Meteo forecast API (0-7cm depth, local point)"
    discharge: str = "Open-Meteo flood API (GloFAS reanalysis/forecast)"


class HorizonForecastOut(BaseModel):
    horizon: Literal["24h", "48h", "72h"]
    predicted_discharge_m3s: float
    trend: Literal["rising", "falling", "steady", "unknown"]


class ForecastResponse(BaseModel):
    station_id: str
    station_name: str
    station_distance_km: float
    basin: str
    current_discharge_m3s: float | None = Field(
        None, description="Today's own reading, if the live discharge fetch succeeded; null if unavailable."
    )
    forecasts: list[HorizonForecastOut]
    generated_at: datetime
    note: str = (
        "This model predicts river discharge (m3/s), not a flood/no-flood decision. It does not know "
        "each station's official danger level in discharge units -- read the trend and magnitude "
        "relative to what's typical for this river, not as a direct flood alert."
    )
    data_sources: DataSources


class ErrorResponse(BaseModel):
    detail: str
