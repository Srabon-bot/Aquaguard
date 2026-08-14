from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

SusceptibilityBand = Literal["low", "moderate", "high", "very_high"]


class StationInfo(BaseModel):
    station_id: str
    name: str
    river: str
    lat: float
    lon: float
    basin: str


class StationsResponse(BaseModel):
    stations: list[StationInfo]


class SusceptibilityResponse(BaseModel):
    station_id: str
    station_name: str
    station_distance_km: float
    basin: str
    susceptibility_band: SusceptibilityBand
    susceptibility_score: float = Field(ge=0.0, le=1.0, description="Mean modeled probability across this station's local terrain grid.")
    peak_score: float = Field(ge=0.0, le=1.0, description="Highest single grid-point score in this station's neighborhood -- worst-case nearby ground.")
    n_grid_points: int
    top_factors: list[str]
    generated_at: datetime
    honesty_note: str = (
        "A geographic/terrain score (elevation, slope, distance-to-river, drainage density, "
        "land cover) -- how flood-prone this ground is by nature, NOT a forecast of when it will "
        "flood. Pair with the flood-risk-classifier's time-bound probability for a full picture. "
        "Evaluated on a genuinely held-out set of stations (never seen during training), not a "
        "random split -- see README.md for why that distinction matters here."
    )


class ErrorResponse(BaseModel):
    detail: str
