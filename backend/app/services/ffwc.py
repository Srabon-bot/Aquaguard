"""Placeholder for Bangladesh FFWC (Flood Forecasting & Warning Centre) station data.

FFWC (https://www.ffwc.gov.bd) does not expose a public JSON/REST API — its
100+ real-time water level stations are only published as HTML/PDF bulletins.
Real integration requires either scraping ffwc.gov.bd's daily water level
pages or acquiring a data-sharing arrangement with BWDB/FFWC.

This module currently returns a nearest-station match by distance only,
with the water level reading left as `None` so callers know it isn't wired
up yet. The model and API already treat station data as optional so the
pipeline works end-to-end with rainfall data alone until this is filled in.

TODO (real integration):
  1. Scrape/ingest daily station water levels from ffwc.gov.bd (or BWDB
     Hydrology data portal) on a schedule.
  2. Replace STATIONS below with the full verified station list + confirmed
     danger levels (do not trust the placeholder danger_level_m values here).
  3. Populate StationReading.current_level_m / trend from the scraped feed.
"""

from dataclasses import dataclass

from app.services.geo import haversine_km
from train.stations import STATIONS as _TRAIN_STATIONS


@dataclass
class Station:
    station_id: str
    name: str
    lat: float
    lon: float
    danger_level_m: float | None = None  # PLACEHOLDER: verify against FFWC before use


@dataclass
class StationReading:
    station: Station
    distance_km: float
    current_level_m: float | None
    trend: str | None  # "rising" | "falling" | "steady" | None if unknown


# Station list expanded 2026-08-07 from a starter 6 (Jamuna/Brahmaputra +
# Surma only) to the full 30-station set covering every major Bangladesh
# river system -- see train/stations.py (single source of truth, shared with
# the training pipeline) and DECISIONS.md §7 for the coverage rationale.
# Coordinates are real-town/known-confluence approximations; extend/verify
# against the official FFWC station list before treating as precise gauge
# locations.
STATIONS: list[Station] = [
    Station(s.station_id, f"{s.name} ({s.river})", s.lat, s.lon)
    for s in _TRAIN_STATIONS
]


def get_nearest_station_reading(lat: float, lon: float) -> StationReading | None:
    if not STATIONS:
        return None
    nearest = min(STATIONS, key=lambda station: haversine_km(lat, lon, station.lat, station.lon))
    distance = haversine_km(lat, lon, nearest.lat, nearest.lon)
    # current_level_m/trend intentionally None until real ingestion exists (see TODO above).
    return StationReading(station=nearest, distance_km=round(distance, 1), current_level_m=None, trend=None)
