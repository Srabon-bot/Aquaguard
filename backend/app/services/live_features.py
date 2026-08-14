"""Part 5: live feature assembly for FloodGBMModel.

Builds the exact 42-column feature dict app/models/flood_gbm_model.py's
predict() needs (minus station_id/basin/doy_sin/doy_cos, which that module
derives itself), using LIVE current data instead of the historical archive
train/build_features.py reads.

Deliberately REUSES train/build_features.py's own transformation functions
(add_lags_and_rolling, add_static_terrain_features, UPSTREAM_CHAIN) and
train/stations.py's constants rather than reimplementing them -- the live
and trained feature for the same name MUST be computed identically, or the
model sees inputs shaped differently from what it learned on. Same reason
this module imports train/ingest_discharge.py's query_coords(): several
stations' raw lat/lon land on a zero/near-zero GloFAS discharge grid cell
(a real bug caught and fixed 2026-08-07 via GLOFAS_COORD_OVERRIDE) --
skipping that override here would silently reintroduce the exact same bug
for live predictions only, since app/ has never needed discharge before now.

Live data sources (see app/services/open_meteo.py for why these are
different endpoints from what training used):
  - rainfall_local_mm, soil_moisture_local: Open-Meteo forecast API at the
    station's own point.
  - rainfall_upstream_mm: same endpoint, mean across the 9-point upstream
    grid (train/stations.py's UPSTREAM_BOXES) -- combined into ONE request
    with the local point (10 points total) rather than two round trips.
  - river_discharge_m3s (+ upstream_chain_discharge / upstream_reference_
    discharge where applicable): Open-Meteo flood API, combined into ONE
    request per station covering every discharge point this station needs
    (its own point, plus an in-network upstream chain point and/or the
    Silchar India-side reference point when applicable) -- again one round
    trip instead of up to three.

History window: WEATHER_PAST_DAYS=90 is a deliberate margin, not the bare
minimum -- soil_moisture_swi (build_features.py's exponential filter,
halflife=10 days) needs real lookback to converge from a cold start; 90
days is ~9 halflives (<0.2% residual from the cold-start assumption), a
close approximation to what training's swi (computed over that station's
FULL multi-decade history) converges to, though not bit-identical --
disclosed here as a known, bounded live/train approximation, not hidden.
DISCHARGE_PAST_DAYS=10 only needs to cover the deepest lag used anywhere
(the 5-day own-discharge lag, or the 3-day Silchar reference lag) with a
small buffer.

Graceful degradation, not all-or-nothing: a rainfall/soil-moisture fetch
failure is fatal (LiveFeatureError) -- without it there is no "today" row
or date index to build ANY lag feature against. A discharge fetch failure
is NOT fatal -- FloodGBMModel already treats every feature as
NaN-tolerant by design (that's what the *_missing flags exist for), so a
transient flood-api.open-meteo.com outage degrades to a rainfall/soil-
moisture-only prediction rather than a hard failure of the whole request.

Real bug found and fixed 2026-08-09 (a few hours after Part 5 first shipped):
every fetch here originally used the implicit `forecast_days=0` default,
which -- confirmed directly, not assumed -- makes Open-Meteo's `past_days`
window end YESTERDAY, not today. Every prediction made in that window was
silently built one full day stale (lag1d was really lag2d, "today's"
reading was actually yesterday's). See FORECAST_DAYS_INCLUDE_TODAY below.
This does NOT mean the model now uses forward-looking forecast rain as a
feature -- it doesn't; FloodGBMModel was trained purely on backward-looking
lag/rolling features, so there's no trained feature slot for a rain
forecast even though Open-Meteo could supply one via a larger
`forecast_days`. That's a real, disclosed capability gap (a 24-72h-ahead
flood model with zero visibility into already-issued rain forecasts), not
something this fix addresses -- it would need a new feature and a
retrain, not a live-serving change.
"""

from __future__ import annotations

import datetime as dt

import pandas as pd

from train.build_features import UPSTREAM_CHAIN, add_lags_and_rolling, add_static_terrain_features
from train.ingest_discharge import query_coords
from train.stations import STATIONS, UPSTREAM_REFERENCE_CHAIN, UPSTREAM_REFERENCE_STATIONS, upstream_points

from app.services.open_meteo import OpenMeteoError, fetch_daily

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
FLOOD_URL = "https://flood-api.open-meteo.com/v1/flood"
WEATHER_PAST_DAYS = 90
DISCHARGE_PAST_DAYS = 10
# Real bug, found live 2026-08-09 by actually checking what date `past_days`
# alone returns: Open-Meteo's `past_days` window ends YESTERDAY, not today --
# confirmed directly (past_days=5&forecast_days=0 returned dates ending one
# day before the actual current date). Every prediction made before this fix
# was silently built one full day stale -- lag1d was really lag2d, "today's"
# rainfall/soil-moisture/discharge was actually yesterday's, etc. `past_days`
# + `forecast_days=1` is what actually includes today (confirmed: adds
# exactly one more day, today's date, with a real blended
# observed-so-far/nowcast value -- not a multi-day-ahead forecast, which this
# module deliberately does NOT use, see FloodGBMModel's feature set: it was
# trained purely on backward-looking lag/rolling features, no forecast-rain
# feature exists to feed even if we fetched one).
FORECAST_DAYS_INCLUDE_TODAY = 1

_STATIONS_BY_ID = {s.station_id: s for s in STATIONS}
_SILCHAR = UPSTREAM_REFERENCE_STATIONS[0]

# Every column FloodGBMModel expects that this module is responsible for
# (station_id/basin/doy_sin/doy_cos are derived by FloodGBMModel itself).
# Used only to pre-seed the 4 upstream-chain/-reference columns to None so a
# station that qualifies for neither still has every key present (a MISSING
# key fails FloodGBMModel's contract check; a None/NaN VALUE is fine).
_UPSTREAM_LINK_COLUMNS = [
    "upstream_chain_discharge_lag1d",
    "upstream_chain_discharge_lag2d",
    "upstream_reference_discharge_lag2d",
    "upstream_reference_discharge_lag3d",
]


class LiveFeatureError(RuntimeError):
    pass


async def _fetch_weather(station) -> tuple[pd.DataFrame, pd.Series]:
    """Returns (local_df with rainfall_local_mm/soil_moisture_local, upstream_rain
    series) for one station, in a single multi-point request (local point +
    9-point upstream grid)."""
    grid_points = upstream_points(station.basin)
    lats = [station.lat] + [p[0] for p in grid_points]
    lons = [station.lon] + [p[1] for p in grid_points]
    frames = await fetch_daily(
        WEATHER_URL, lats, lons,
        ["precipitation_sum", "soil_moisture_0_to_7cm_mean"], WEATHER_PAST_DAYS,
        forecast_days=FORECAST_DAYS_INCLUDE_TODAY,
    )
    local = frames[0].rename(columns={
        "precipitation_sum": "rainfall_local_mm",
        "soil_moisture_0_to_7cm_mean": "soil_moisture_local",
    })
    upstream_rain = pd.concat([f["precipitation_sum"] for f in frames[1:]], axis=1).mean(axis=1)
    upstream_rain.name = "rainfall_upstream_mm"
    return local, upstream_rain


async def _fetch_discharge_points(points: list[tuple[str, float, float]]) -> dict[str, pd.Series]:
    """points: list of (key, lat, lon). Returns key -> discharge Series,
    one combined request. Callers decide what each key means (own point,
    chain-upstream point, Silchar)."""
    lats = [p[1] for p in points]
    lons = [p[2] for p in points]
    frames = await fetch_daily(
        FLOOD_URL, lats, lons, ["river_discharge"], DISCHARGE_PAST_DAYS,
        forecast_days=FORECAST_DAYS_INCLUDE_TODAY,
    )
    return {points[i][0]: frames[i]["river_discharge"] for i in range(len(points))}


def _value_n_days_ago(series: pd.Series, n: int) -> float:
    """The reading from n days before the series' own last (most recent)
    entry -- mirrors build_features.py's upstream-chain shift direction
    (an upstream reading dated N days ago is today's leading indicator).
    Returns float('nan'), never None/pd.NA -- see build_live_feature_row's
    link_values comment: a single-row DataFrame built from a dict infers
    `object` dtype for an all-None column (LightGBM then rejects it
    outright), but a real float NaN infers `float64` correctly."""
    if len(series) <= n:
        return float("nan")
    v = series.iloc[-1 - n]
    return float(v) if pd.notna(v) else float("nan")


async def build_live_feature_row(station_id: str, as_of: dt.date | None = None) -> dict:
    """Builds today's (or `as_of`'s, if given -- reserved for testing; live
    callers should omit it) feature row for one station. Raises
    LiveFeatureError -- and ONLY LiveFeatureError, see the outer try/except
    below -- if the rainfall/soil-moisture backbone can't be fetched;
    discharge-side failures degrade to NaN instead of raising."""
    if station_id not in _STATIONS_BY_ID:
        raise LiveFeatureError(f"Unknown station_id {station_id!r}")
    station = _STATIONS_BY_ID[station_id]

    # Everything below this point is wrapped in one try/except that converts
    # ANY exception -- not just the ones this function's own code
    # anticipates -- into LiveFeatureError. This is the real hardening: a
    # missing UPSTREAM_BOXES/STATIC_TERRAIN entry, a pandas edge case in
    # add_lags_and_rolling, or any other bug not yet found would otherwise
    # propagate as a raw, untyped exception past main.py's
    # `except LiveFeatureError` and surface as an unhandled 500 to the
    # caller. main.py's own global exception handler is a second, final
    # safety net on top of this one -- this one exists so /predict/risk's
    # SPECIFIC `except LiveFeatureError -> HTTPException(502)` branch (a
    # useful, descriptive error) is the one that actually fires, rather than
    # falling through to the generic catch-all.
    try:
        try:
            local, upstream_rain = await _fetch_weather(station)
        except OpenMeteoError as exc:
            raise LiveFeatureError(f"weather fetch failed for {station_id}: {exc}") from exc
        if local.empty:
            raise LiveFeatureError(f"weather fetch returned no rows for {station_id}")

        df = pd.concat([local, upstream_rain], axis=1).reset_index()
        df["river_discharge_m3s"] = float("nan")  # overwritten below if the discharge fetch succeeds

        # float('nan'), not None -- see _value_n_days_ago's docstring for why.
        link_values: dict[str, float] = dict.fromkeys(_UPSTREAM_LINK_COLUMNS, float("nan"))

        # --- one combined discharge request for every point this station needs ---
        discharge_points: list[tuple[str, float, float]] = []
        own_lat, own_lon = query_coords(station)
        discharge_points.append(("own", own_lat, own_lon))

        chain_pair = UPSTREAM_CHAIN.get(station_id)
        if chain_pair is not None:
            up_id, chain_lag = chain_pair
            up_station = _STATIONS_BY_ID.get(up_id)
            if up_station is None:
                # A UPSTREAM_CHAIN entry pointing at a station_id not in
                # STATIONS would be a stations.py data-integrity bug, not a
                # live-request problem -- degrade this one link rather than
                # failing the whole prediction over a config typo.
                print(f"[live_features] UPSTREAM_CHAIN[{station_id}] points at unknown station {up_id!r}, skipping")
                chain_pair = None
            else:
                up_lat, up_lon = query_coords(up_station)
                discharge_points.append(("chain", up_lat, up_lon))

        ref_pair = UPSTREAM_REFERENCE_CHAIN.get(station_id)
        if ref_pair is not None:
            _, ref_lag = ref_pair
            discharge_points.append(("reference", _SILCHAR.lat, _SILCHAR.lon))

        try:
            discharge_series = await _fetch_discharge_points(discharge_points)
        except OpenMeteoError as exc:
            # Degrade, don't fail -- see module docstring. Every discharge-derived
            # column (including its lags/missing-flag) stays NaN, which
            # FloodGBMModel/LightGBM handle natively.
            print(f"[live_features] discharge fetch failed for {station_id}, continuing without it: {exc}")
            discharge_series = {}

        if "own" in discharge_series:
            own = discharge_series["own"].rename("river_discharge_m3s")
            df = df.drop(columns=["river_discharge_m3s"]).merge(own.reset_index(), on="date", how="left")
        if "chain" in discharge_series and chain_pair is not None:
            link_values[f"upstream_chain_discharge_lag{chain_lag}d"] = _value_n_days_ago(
                discharge_series["chain"], chain_lag
            )
        if "reference" in discharge_series and ref_pair is not None:
            link_values[f"upstream_reference_discharge_lag{ref_lag}d"] = _value_n_days_ago(
                discharge_series["reference"], ref_lag
            )

        for col in ["rainfall_local_mm", "rainfall_upstream_mm", "soil_moisture_local", "river_discharge_m3s"]:
            df[f"{col}_missing"] = df[col].isna()

        df = add_lags_and_rolling(df)
        df = add_static_terrain_features(df, station_id)

        today_row = df.iloc[-1].to_dict()
        today_row.pop("date", None)
        today_row.update(link_values)
        return today_row
    except LiveFeatureError:
        raise
    except Exception as exc:  # noqa: BLE001 -- deliberate catch-all, see comment above
        raise LiveFeatureError(f"unexpected error building live features for {station_id}: {exc}") from exc
