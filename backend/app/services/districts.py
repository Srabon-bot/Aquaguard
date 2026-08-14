import json
from functools import lru_cache
from pathlib import Path

from app.models.schemas import DistrictInfo
from app.services.geo import haversine_km

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "districts.json"


@lru_cache
def load_districts() -> list[DistrictInfo]:
    raw = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    return [DistrictInfo(**entry) for entry in raw]


def find_district(district: str, upazila: str) -> DistrictInfo | None:
    district_l, upazila_l = district.strip().lower(), upazila.strip().lower()
    for entry in load_districts():
        if entry.district.lower() == district_l and entry.upazila.lower() == upazila_l:
            return entry
    return None


def nearest_district(lat: float, lon: float) -> DistrictInfo:
    """Fall back for lat/lon queries that don't name a district/upazila.

    Used only to infer which river basin a raw coordinate belongs to
    (for reasoning/context) — the coordinate itself is still used as-is
    for rainfall/station lookups, not snapped to the matched district.
    """
    return min(load_districts(), key=lambda entry: haversine_km(lat, lon, entry.lat, entry.lon))
