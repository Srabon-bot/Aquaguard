"""Shared low-level client for Open-Meteo's LIVE forecast/flood endpoints,
used by Part 5's live-feature assembly (app/services/live_features.py).

Why this is a separate client from what training used: training's rainfall/
soil-moisture history (train/ingest_openmeteo_historical.py) comes from
Open-Meteo's Historical Weather API (`archive-api.open-meteo.com`, ERA5/
ERA5-Land reanalysis) -- real, but reanalysis has a genuine processing lag
and is NOT available for "today", which is fine for building a training set
but wrong for live inference. app/services/weather.py already solved this
for rainfall alone by using the regular forecast API (`api.open-meteo.com`)
with `past_days`, verified 2026-08-09 to return real, non-null values
through the actual current date. This module generalizes that same
approach to also cover soil moisture (same forecast endpoint, confirmed
supported) and discharge (`flood-api.open-meteo.com`, same `past_days`
mechanism, also confirmed live-current) -- live inference needs a
live-current source for all three, not just rainfall.

Multi-point requests: Open-Meteo accepts comma-separated latitude/longitude
lists and returns a JSON *array* of per-point objects (each with its own
`daily` block) instead of one object -- confirmed directly 2026-08-09, not
assumed. This module accepts point lists and normalizes both the
single-point (dict) and multi-point (list) response shapes to a uniform
list of DataFrames, one per point, in request order.

Timezone pinned to "UTC" for every call here -- matches
ingest_openmeteo_historical.py's training-time choice (not "auto", which
returns a different local timezone per point and would shift daily
aggregation boundaries by up to several hours between live and trained
data for the exact same calendar day).
"""

from __future__ import annotations

import httpx
import pandas as pd


class OpenMeteoError(RuntimeError):
    pass


async def fetch_daily(
    base_url: str,
    lats: list[float],
    lons: list[float],
    daily_vars: list[str],
    past_days: int,
    forecast_days: int = 0,
    timeout: float = 15.0,
) -> list[pd.DataFrame]:
    """One HTTP request for 1..N points. Returns one DataFrame per point (in
    the same order as lats/lons), indexed by `date`, one column per
    variable in `daily_vars`. A variable Open-Meteo didn't return for a
    point becomes an all-NaN column, not a KeyError -- callers see a
    missing reading the same way a genuinely absent training-data day
    does.

    Every failure mode here raises OpenMeteoError, and ONLY OpenMeteoError
    -- callers (live_features.py) catch exactly that type to decide
    fatal-vs-degrade, so a gap here (an exception type this function lets
    through uncaught) would silently bypass that whole design. Originally
    `resp.json()` and the response-shape parsing sat OUTSIDE the
    request's try/except -- a malformed body (a proxy error page, a
    truncated response, anything that isn't valid JSON or isn't shaped the
    way this function assumes) raised json.JSONDecodeError/AttributeError/
    KeyError straight through, uncaught by anything. Found by deliberately
    feeding this function bad input (not by inspection alone) while
    hardening Part 5 -- see live_features.py's own hardening pass, same
    session. Fixed by wrapping the ENTIRE request+parse in one try/except
    that catches every exception type this function can raise internally,
    not just httpx's."""
    if len(lats) != len(lons):
        raise OpenMeteoError(f"lats/lons length mismatch: {len(lats)} vs {len(lons)}")
    if not lats:
        raise OpenMeteoError("fetch_daily called with zero points")

    params = {
        "latitude": ",".join(str(x) for x in lats),
        "longitude": ",".join(str(x) for x in lons),
        "daily": ",".join(daily_vars),
        "past_days": past_days,
        "forecast_days": forecast_days,
        "timezone": "UTC",
    }
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(base_url, params=params)
            resp.raise_for_status()
            payload = resp.json()

        records = payload if isinstance(payload, list) else [payload]
        if len(records) != len(lats):
            raise OpenMeteoError(
                f"Expected {len(lats)} points in Open-Meteo response, got {len(records)} ({base_url})"
            )

        frames = []
        for rec in records:
            if not isinstance(rec, dict):
                raise OpenMeteoError(f"Unexpected non-object record in Open-Meteo response ({base_url}): {rec!r}")
            daily = rec.get("daily")
            if not isinstance(daily, dict):
                raise OpenMeteoError(f"Response for a point had no 'daily' block ({base_url})")
            dates = daily.get("time", [])
            if not isinstance(dates, list):
                raise OpenMeteoError(f"'daily.time' was not a list ({base_url})")
            df = pd.DataFrame({"date": pd.to_datetime(dates)})
            for var in daily_vars:
                values = daily.get(var)
                # A present-but-wrong-length array would silently misalign
                # every date once assigned as a column -- treat that as
                # "missing", not a value that happens to land on the wrong day.
                if not isinstance(values, list) or len(values) != len(dates):
                    values = [None] * len(dates)
                df[var] = values
            frames.append(df.set_index("date"))
        return frames
    except OpenMeteoError:
        raise
    except Exception as exc:  # noqa: BLE001 -- deliberately broad, see docstring: every
        # failure mode this function can hit (bad JSON, wrong shape, a pandas
        # error building the frame) must come out as OpenMeteoError so
        # live_features.py's fatal-vs-degrade split actually holds.
        # str(exc) alone can be EMPTY for some exception types (observed live,
        # 2026-08-09: a transient httpx failure logged as
        # "...failed (url): " with nothing after the colon) -- always include
        # the exception's own class name too so a degraded-mode log line is
        # still actually useful for debugging, not just "something happened."
        raise OpenMeteoError(
            f"Open-Meteo request/parse failed ({base_url}): {type(exc).__name__}: {exc}"
        ) from exc
