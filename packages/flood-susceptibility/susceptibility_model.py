"""Loads the trained susceptibility model (Random Forest, chosen over
LightGBM by real spatial-CV comparison -- see models/metrics.json) and the
precomputed per-station lookup table.

WHY A PRECOMPUTED LOOKUP, NOT LIVE FEATURE COMPUTATION: unlike the flood
risk classifier and discharge forecaster (which need genuinely live
weather/discharge data every call), susceptibility is static geography --
elevation, slope, distance-to-river, drainage density, land cover don't
change day to day. Computing them live would mean pulling a Copernicus DEM
tile (30-60s per 1-degree tile, see backend/train/ingest_susceptibility_
terrain.py) on every request -- unusable for an interactive dashboard.
Instead, every one of the 30 stations' 49-point local grid was already
scored once at training time; this service just looks up (or nearest-
station-snaps) into that table. Real geospatial libraries (rasterio,
pysheds, scipy) are NOT a runtime dependency of this package at all --
only needed in backend/train/ to build the table in the first place, which
is exactly why this stays as fast and self-contained as the other two
packages.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

MODELS_DIR = Path(__file__).resolve().parent / "models"

# Fixed, round-number bands -- not equal-sized quantiles of the 30 stations'
# own distribution -- chosen so the band a station falls in has a stable,
# explainable meaning ("below 15% mean modeled probability") instead of
# shifting definition if more stations were ever added later.
BANDS = [
    (0.35, "very_high"),
    (0.25, "high"),
    (0.15, "moderate"),
    (0.0, "low"),
]


def classify(proba: float) -> str:
    for cutoff, label in BANDS:
        if proba >= cutoff:
            return label
    return "low"


@dataclass(frozen=True)
class StationSusceptibility:
    station_id: str
    mean_proba: float
    max_proba: float
    n_grid_points: int
    band: str


class SusceptibilityModel:
    def __init__(self, lookup: dict[str, StationSusceptibility]):
        self._lookup = lookup

    @classmethod
    def load(cls) -> "SusceptibilityModel":
        path = MODELS_DIR / "per_station_susceptibility.csv"
        if not path.exists():
            raise FileNotFoundError(
                f"{path} not found -- run backend/train/train_susceptibility_model.py "
                "then copy its outputs here (see README.md)."
            )
        lookup = {}
        with path.open() as f:
            for row in csv.DictReader(f):
                proba = float(row["mean_proba"])
                lookup[row["station_id"]] = StationSusceptibility(
                    station_id=row["station_id"],
                    mean_proba=round(proba, 4),
                    max_proba=round(float(row["max_proba"]), 4),
                    n_grid_points=int(row["n_points"]),
                    band=classify(proba),
                )
        return cls(lookup)

    def for_station(self, station_id: str) -> StationSusceptibility | None:
        return self._lookup.get(station_id)
