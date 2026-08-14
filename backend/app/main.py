import logging
import math
from contextlib import asynccontextmanager
from datetime import datetime, timezone

import pandas as pd
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.models.flood_gbm_model import FloodGBMModel, build_reasoning
from app.models.schemas import (
    DataSources,
    DistrictsResponse,
    ErrorResponse,
    HorizonRisk,
    ResolvedLocation,
    RiskResponse,
)
from app.services import ffwc
from app.services.districts import find_district, load_districts, nearest_district
from app.services.live_features import LiveFeatureError, build_live_feature_row

logger = logging.getLogger("flood_api")

model_registry: dict[str, FloodGBMModel] = {}

# horizons list is ordered 24h/48h/72h by feature_schema.json; the response's
# top-level risk_level/risk_score mirror the FIRST (soonest, most actionable
# for someone deciding whether to act today) rather than always 72h.
HEADLINE_HORIZON = "24h"

# Bangladesh's real bounding box (20.5-26.67N, 88.03-92.67E per the FFWC's
# own Annual Flood Report) with a margin for near-border stations/upstream
# points. A lat/lon far outside this isn't a crash risk (nearest_district/
# get_nearest_station_reading always return SOMETHING via haversine, however
# far away) but silently snapping a query from, say, another continent to
# "the nearest Bangladesh station" would produce a confident-looking, totally
# meaningless prediction instead of an honest "out of coverage area" error --
# a correctness problem this validation catches explicitly rather than
# leaving as a silent footgun.
BD_LAT_RANGE = (20.0, 27.0)
BD_LON_RANGE = (87.5, 93.0)


def _json_safe_features(features: dict) -> dict:
    # NaN is a legitimate, expected VALUE for a missing live reading (see
    # live_features.py -- LightGBM handles it natively, and it must stay a
    # real float NaN, not None, for model.predict()'s single-row DataFrame
    # to keep the right dtype). But strict JSON has no NaN literal --
    # Starlette's default JSONResponse rejects it outright ("Out of range
    # float values are not JSON compliant"), confirmed by actually calling
    # this endpoint before shipping it, not assumed. So the RESPONSE gets a
    # separate None-substituted copy; the dict passed to predict() above is
    # never touched.
    return {k: (None if isinstance(v, float) and math.isnan(v) else v) for k, v in features.items()}


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        model_registry["flood_model"] = FloodGBMModel.load(settings.flood_model_version)
    except FileNotFoundError as exc:
        # Server still starts so /health and /districts work; /predict/risk
        # will report a clear 503 until the model is trained.
        print(f"[startup warning] {exc}")
    yield
    model_registry.clear()


app = FastAPI(
    title="Flood Early-Warning API",
    description=(
        "Backend for a flood early-warning system for fish farmers in Bangladesh. "
        "Given a district/upazila or lat/lon, returns a plain-language flood risk "
        "assessment for the next 24/48/72 hours from the trained LightGBM models "
        "(backend/models/, see DECISIONS.md SS14-19). Intended to be consumed by a "
        "separate frontend (web/mobile) -- see README.md for the API contract."
    ),
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Final safety net -- does NOT catch HTTPException (Starlette dispatches
    # that to its own more-specific handler first, so every deliberate
    # `raise HTTPException(...)` below still returns its real status code/
    # detail unchanged). This only fires for a genuinely unanticipated bug,
    # and its whole job is to guarantee the client always gets back clean
    # JSON -- never a raw Python traceback or a dropped connection -- while
    # the real exception still gets logged server-side for debugging. Added
    # after hardening live_features.py/open_meteo.py to guarantee only
    # typed errors escape those modules; this is the last line of defense
    # for anything that gets through anyway (a bug in FastAPI/pydantic
    # itself, a code path this session didn't think to test, etc.).
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content=ErrorResponse(detail="Internal server error.").model_dump())


@app.get("/health")
async def health():
    return {"status": "ok", "model_loaded": "flood_model" in model_registry}


@app.get("/districts", response_model=DistrictsResponse)
async def get_districts():
    return DistrictsResponse(districts=load_districts())


@app.get("/predict/risk", response_model=RiskResponse)
async def predict_risk(
    district: str | None = Query(None, description="e.g. 'Sirajganj'"),
    upazila: str | None = Query(None, description="e.g. 'Sirajganj Sadar'"),
    lat: float | None = Query(None, ge=-90, le=90),
    lon: float | None = Query(None, ge=-180, le=180),
):
    flood_model = model_registry.get("flood_model")
    if flood_model is None:
        raise HTTPException(
            status_code=503,
            detail=f"Model not loaded. Run `python train/train_model.py --version <features_version>` "
                    f"on the server (expected at backend/models/{settings.flood_model_version}/), then restart.",
        )

    resolved_district, resolved_upazila = district, upazila
    if lat is None or lon is None:
        if not district or not upazila:
            raise HTTPException(
                status_code=400,
                detail="Provide either (district and upazila) or (lat and lon).",
            )
        entry = find_district(district, upazila)
        if entry is None:
            raise HTTPException(status_code=404, detail=f"Unknown district/upazila: {district}/{upazila}")
        lat, lon = entry.lat, entry.lon
        basin = entry.basin
    else:
        # No district/upazila named -- snap to the nearest known district only
        # to infer which river basin this coordinate drains into.
        basin = nearest_district(lat, lon).basin

    # nearest_district/get_nearest_station_reading below use plain haversine
    # distance and will always return SOMETHING no matter how far away the
    # query point is -- not a crash risk, but silently snapping a
    # far-outside-Bangladesh coordinate to "the nearest station" would
    # produce a confident-looking, meaningless prediction instead of an
    # honest error. Checked explicitly here rather than left as a silent
    # footgun (verified: this is coordinate-based, so district/upazila
    # lookups can't trigger it -- districts.json entries are all real
    # Bangladesh locations).
    if not (BD_LAT_RANGE[0] <= lat <= BD_LAT_RANGE[1] and BD_LON_RANGE[0] <= lon <= BD_LON_RANGE[1]):
        raise HTTPException(
            status_code=400,
            detail=f"lat/lon ({lat}, {lon}) is outside this system's coverage area "
                    f"(Bangladesh, roughly {BD_LAT_RANGE[0]}-{BD_LAT_RANGE[1]}N / {BD_LON_RANGE[0]}-{BD_LON_RANGE[1]}E).",
        )

    # The model is trained per-station (station_id is a categorical feature),
    # so live inference needs the nearest of the 30 real stations, not just a
    # basin label -- reuses the same nearest-station lookup ffwc.py already
    # has for water-level display.
    station_reading = ffwc.get_nearest_station_reading(lat, lon)
    if station_reading is None:
        raise HTTPException(status_code=500, detail="No station network configured.")
    station = station_reading.station

    try:
        features = await build_live_feature_row(station.station_id)
    except LiveFeatureError as exc:
        raise HTTPException(status_code=502, detail=f"Live data fetch failed: {exc}") from exc

    predictions = flood_model.predict(features, station_id=station.station_id, prediction_date=pd.Timestamp.now())
    horizons = [
        HorizonRisk(horizon=p.horizon, risk_level=p.risk_level, probability=round(p.probability, 3),
                    threshold=round(p.threshold, 3))
        for p in predictions
    ]
    headline = next(h for h in horizons if h.horizon == HEADLINE_HORIZON)

    reasoning = build_reasoning(features, predictions, basin, station.name)

    return RiskResponse(
        location=ResolvedLocation(
            district=resolved_district, upazila=resolved_upazila, lat=lat, lon=lon, basin=basin
        ),
        nearest_station=f"{station.name} ({round(station_reading.distance_km, 1)} km away)",
        horizons=horizons,
        risk_level=headline.risk_level,
        risk_score=headline.probability,
        horizon_hours=24,
        generated_at=datetime.now(timezone.utc),
        reasoning=reasoning,
        features_used=_json_safe_features(features),
        model_version=flood_model.version,
        data_sources=DataSources(
            station_level=station.name,
        ),
    )
