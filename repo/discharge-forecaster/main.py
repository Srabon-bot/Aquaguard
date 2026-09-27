"""Discharge Forecaster -- standalone FastAPI service.

Run locally:
    uvicorn main:app --reload --port 8001

Then open http://127.0.0.1:8001/docs for interactive API docs, or see
README.md for plain curl/JavaScript examples.

NOTE: this model predicts river discharge (m3/s), NOT a flood/no-flood
decision -- see schemas.py's ForecastResponse.note. It's a separate,
independent model from the flood-risk-classifier package; see that
package's own README for the yes/no flood-risk model.
"""

import logging
import math
from contextlib import asynccontextmanager
from datetime import datetime, timezone

import pandas as pd
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from discharge_model import DischargeForecastModel
from live_features import LiveFeatureError, build_live_feature_row
from schemas import DataSources, ErrorResponse, ForecastResponse, HorizonForecastOut, StationInfo, StationsResponse
from stations import STATIONS

logger = logging.getLogger("discharge_forecaster")

model_registry: dict[str, DischargeForecastModel] = {}

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        model_registry["model"] = DischargeForecastModel.load()
    except FileNotFoundError as exc:
        print(f"[startup warning] {exc}")
    yield
    model_registry.clear()


app = FastAPI(
    title="River Discharge Forecaster",
    description="Predicts river discharge (m3/s) 24h/48h/72h ahead for 30 Bangladesh river gauge "
                 "stations, using live rainfall/soil-moisture/discharge data. NOT a flood/no-flood "
                 "decision -- see the /predict response's `note` field.",
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


@app.get("/predict", response_model=ForecastResponse)
async def predict_discharge(
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

    try:
        features = await build_live_feature_row(station.station_id)
    except LiveFeatureError as exc:
        raise HTTPException(status_code=502, detail=f"Live data fetch failed: {exc}") from exc

    forecasts = model.predict(features, station_id=station.station_id, prediction_date=pd.Timestamp.now())

    return ForecastResponse(
        station_id=station.station_id,
        station_name=station.name,
        station_distance_km=distance_km,
        basin=station.basin,
        current_discharge_m3s=forecasts[0].current_discharge_m3s,
        forecasts=[
            HorizonForecastOut(horizon=f.horizon, predicted_discharge_m3s=f.predicted_discharge_m3s, trend=f.trend)
            for f in forecasts
        ],
        generated_at=datetime.now(timezone.utc),
        data_sources=DataSources(),
    )
