"""Client for Open-Meteo's free forecast API.

Used to pull recent + forecast daily rainfall for a lat/lon, since a large
share of Bangladesh's flooding is driven by upstream monsoon rainfall rather
than local rain alone. No API key is required for Open-Meteo's free tier.

SUPERSEDED for /predict/risk as of 2026-08-09 (Part 5): app/main.py now
builds its feature set via app/services/live_features.py (rainfall + soil
moisture + discharge, matching FloodGBMModel's real 42-feature contract)
instead of this module's RainfallSummary. Kept in the tree, not deleted --
this module's request pattern (api.open-meteo.com's forecast endpoint with
`past_days`, verified to return real values through the current date, not
just a forecast) is exactly what live_features.py's own client
(app/services/open_meteo.py) generalizes, so it's a useful reference even
though nothing currently imports it.
"""

from dataclasses import dataclass

import httpx

from app.config import settings

PAST_DAYS = 14
FORECAST_DAYS = 3


class WeatherServiceError(RuntimeError):
    pass


@dataclass
class RainfallSummary:
    daily_dates: list[str]
    daily_precip_mm: list[float]
    past_7d_total_mm: float
    past_14d_total_mm: float
    forecast_3d_total_mm: float
    trend_ratio: float  # recent 7d vs prior 7d; >1 means rainfall is intensifying


async def fetch_rainfall(lat: float, lon: float) -> RainfallSummary:
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "precipitation_sum",
        "past_days": PAST_DAYS,
        "forecast_days": FORECAST_DAYS,
        "timezone": "auto",
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(settings.open_meteo_base_url, params=params)
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise WeatherServiceError(f"Open-Meteo request failed: {exc}") from exc

    payload = resp.json()
    daily = payload.get("daily", {})
    dates: list[str] = daily.get("time", [])
    precip: list[float] = [v if v is not None else 0.0 for v in daily.get("precipitation_sum", [])]

    if len(dates) < PAST_DAYS + 1 or len(precip) != len(dates):
        raise WeatherServiceError("Unexpected Open-Meteo response shape")

    # First PAST_DAYS entries are history, remainder (including today) is forecast.
    past = precip[:PAST_DAYS]
    forecast = precip[PAST_DAYS:]

    past_7d = sum(past[-7:])
    past_14d = sum(past)
    prior_7d = sum(past[-14:-7]) or 1e-6  # avoid div-by-zero
    forecast_3d = sum(forecast)

    return RainfallSummary(
        daily_dates=dates,
        daily_precip_mm=precip,
        past_7d_total_mm=round(past_7d, 2),
        past_14d_total_mm=round(past_14d, 2),
        forecast_3d_total_mm=round(forecast_3d, 2),
        trend_ratio=round(past_7d / prior_7d, 3),
    )
