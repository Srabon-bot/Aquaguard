"""Flood Susceptibility -- standalone FastAPI service.

Model #3 in this project's flood pipeline: a genuinely different question
from the other two. flood-risk-classifier asks "will this station flood in
the next 24/48/72h" (temporal, needs live weather); discharge-forecaster
asks "how much water will be flowing" (temporal, regression). This asks
"how flood-prone is this ground by nature" (static geography -- elevation,
slope, distance-to-river, drainage density, land cover) -- see README.md
for the full reasoning and how the three combine.

Run locally:
    uvicorn main:app --reload --port 8002

Then open http://127.0.0.1:8002/docs for interactive API docs.
"""

import json
import logging
import math
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from schemas import ErrorResponse, StationInfo, StationsResponse, SusceptibilityResponse
from stations import STATIONS
from susceptibility_model import SusceptibilityModel

logger = logging.getLogger("flood_susceptibility")

model_registry: dict[str, SusceptibilityModel] = {}
TOP_FACTORS_LIMIT = 3

# Same bounding-box honesty check as the other two packages -- see their
# main.py for the "why not just silently snap to nearest station" reasoning.
BD_LAT_RANGE = (20.0, 27.0)
BD_LON_RANGE = (87.5, 93.0)


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def nearest_station(lat: float, lon: float):
    return min(STATIONS, key=lambda s: haversine_km(lat, lon, s.lat, s.lon))


def _load_top_factors() -> list[str]:
    metrics_path = Path(__file__).resolve().parent / "models" / "metrics.json"
    try:
        metrics = json.loads(metrics_path.read_text())
        importances = metrics["feature_importance_shap"]
        ranked = sorted(importances.items(), key=lambda kv: kv[1], reverse=True)
        return [name for name, _ in ranked[:TOP_FACTORS_LIMIT]]
    except Exception:  # noqa: BLE001 -- reasoning text degrading gracefully beats a startup crash
        return ["land cover", "slope", "distance to river"]


TOP_FACTORS_GLOBAL = None  # filled in at startup


@asynccontextmanager
async def lifespan(app: FastAPI):
    global TOP_FACTORS_GLOBAL
    try:
        model_registry["model"] = SusceptibilityModel.load()
        TOP_FACTORS_GLOBAL = _load_top_factors()
    except FileNotFoundError as exc:
        print(f"[startup warning] {exc}")
    yield
    model_registry.clear()


app = FastAPI(
    title="Flood Susceptibility",
    description="Static terrain-based flood susceptibility (elevation, slope, distance-to-river, "
                 "drainage density, land cover) for 30 Bangladesh river gauge station neighborhoods. "
                 "Model #3 alongside flood-risk-classifier and discharge-forecaster.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content=ErrorResponse(detail="Internal server error.").model_dump())


@app.get("/health")
async def health():
    return {"status": "ok", "model_loaded": "model" in model_registry}


@app.get("/stations", response_model=StationsResponse)
async def list_stations():
    return StationsResponse(stations=[
        StationInfo(station_id=s.station_id, name=s.name, river=s.river, lat=s.lat, lon=s.lon, basin=s.basin)
        for s in STATIONS
    ])


@app.get("/predict", response_model=SusceptibilityResponse)
async def predict_susceptibility(
    station_id: str | None = Query(None, description="e.g. 'SW90' -- see GET /stations for the full list"),
    lat: float | None = Query(None, ge=-90, le=90),
    lon: float | None = Query(None, ge=-180, le=180),
):
    model = model_registry.get("model")
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded -- check server startup logs.")

    if station_id is None:
        if lat is None or lon is None:
            raise HTTPException(status_code=400, detail="Provide either station_id, or both lat and lon.")
        if not (BD_LAT_RANGE[0] <= lat <= BD_LAT_RANGE[1] and BD_LON_RANGE[0] <= lon <= BD_LON_RANGE[1]):
            raise HTTPException(
                status_code=400,
                detail=f"lat/lon ({lat}, {lon}) is outside this model's coverage area "
                        f"(Bangladesh, roughly {BD_LAT_RANGE[0]}-{BD_LAT_RANGE[1]}N / {BD_LON_RANGE[0]}-{BD_LON_RANGE[1]}E).",
            )
        station = nearest_station(lat, lon)
        distance_km = round(haversine_km(lat, lon, station.lat, station.lon), 1)
    else:
        matches = [s for s in STATIONS if s.station_id == station_id]
        if not matches:
            raise HTTPException(status_code=404, detail=f"Unknown station_id {station_id!r}. See GET /stations.")
        station = matches[0]
        distance_km = 0.0

    result = model.for_station(station.station_id)
    if result is None:
        raise HTTPException(status_code=500, detail=f"No susceptibility data for {station.station_id!r} -- lookup table incomplete.")

    return SusceptibilityResponse(
        station_id=station.station_id,
        station_name=station.name,
        station_distance_km=distance_km,
        basin=station.basin,
        susceptibility_band=result.band,
        susceptibility_score=result.mean_proba,
        peak_score=result.max_proba,
        n_grid_points=result.n_grid_points,
        top_factors=TOP_FACTORS_GLOBAL or [],
        generated_at=datetime.now(timezone.utc),
    )
