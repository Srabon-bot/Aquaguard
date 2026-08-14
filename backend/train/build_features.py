"""Part 3 -- Feature engineering. Reads the merged per-station tables from
build_dataset.py (backend/data/processed/<version>/) and adds:

  - Lag features (t-1, t-2, t-3, t-5) for rainfall_local, rainfall_upstream,
    soil_moisture_local, river_discharge_m3s.
  - Rolling sums (7d/14d) for rainfall_local and rainfall_upstream, plus a
    trend ratio (recent 7d / prior 7d) mirroring app/services/weather.py's
    live trend_ratio calc, so the trained feature and the live-inference
    feature are computed the same way.
  - A soil-moisture 30-day delta (today vs 30 days ago) as a cheap
    antecedent-wetness-trend proxy -- absolute soil moisture varies a lot by
    season, what likely matters more for flood risk is "wetter than it was
    a month ago", not the raw value alone.
  - Static per-station terrain (elevation_m, hand_m -- Height Above Nearest
    Drainage, MERIT Hydro) -- added 2026-08-09 after a literature review
    found this project had zero static geomorphological features despite
    them recurring across multiple independent sources as important flood
    factors. See DECISIONS.md SS17/SS18 and add_static_terrain_features().
  - Upstream India-side discharge (Silchar, Assam, on the Barak -- becomes
    our Surma/Kushiyara) for the 5 stations directly on that system --
    added 2026-08-09 per HaorFloodAlert's reported ~36h lead time from
    this exact signal. See stations.py's UPSTREAM_REFERENCE_CHAIN and
    add_upstream_reference_discharge_feature().
  - Upstream travel-time-shifted discharge: for station pairs on the same
    river chain where we have a defensible real-world travel-time estimate
    (see UPSTREAM_CHAIN below), add the upstream station's discharge shifted
    forward by that many days -- e.g. Sirajganj's table gets a column that is
    Sariakandi's discharge from 1 day earlier, since a flood pulse measured
    upstream today is expected to arrive downstream about that many days
    later. Deliberately conservative: only chains with real, checkable
    geography are included; stations with no clear upstream Bangladesh-
    internal neighbor (CHT rivers, coastal stations, the most-upstream point
    of each chain) simply don't get this feature, not a fabricated one.
  - Flood-horizon labels: flood_within_24h/48h/72h, each a bool for whether
    flood_byStor is positive at any point in the next 1/2/3 days respectively
    (forward-looking, never using same-day or past information -- this is
    what makes it a legitimate "predict ahead" label rather than nowcasting).
    A positive is trusted from any of THREE independent sources: GFMS's
    Flood_byStor (2013+, satellite-detected) OR a matched DFO historical
    flood event (1985-2010, see ingest_dfo_floods.py) OR a matched Global
    Flood Database event (2002-2017, per-pixel MODIS-detected, see
    ingest_global_flood_db.py) -- both DFO and GFD extend real positive
    examples beyond GFMS's window without inventing new negatives (neither
    records every flood, only large/catalogued events, so an unmatched day
    is NOT good evidence of "no flood", unlike GFMS's own accessible-window
    non-detections -- see DECISIONS.md SS13/SS15). Each horizon also gets a
    companion `flood_within_Nh_label_regime` column ("observed" vs
    "unobserved_positive") so Part 4 can tell the reliable GFMS-balanced
    rows apart from the positive-only DFO/GFD-extension rows instead of
    blending them silently.

Travel-time estimates (UPSTREAM_CHAIN) are engineering approximations, not
measured values -- daily-resolution data means sub-day travel times aren't
resolvable anyway, so every listed pair uses a 1-day lag except where a
segment is clearly longer based on real distance. See DECISIONS.md for the
caveat that these are not hydrologically validated travel times.

Usage:
    python train/build_features.py --version 2026-08-07c
"""

import argparse
import csv
import datetime as dt
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stations import STATIC_TERRAIN, UPSTREAM_REFERENCE_CHAIN  # noqa: E402

PROCESSED_ROOT = Path(__file__).resolve().parent.parent / "data" / "processed"
DISCHARGE_RAW_DIR = Path(__file__).resolve().parent.parent / "data_raw" / "discharge"
FEATURES_ROOT = Path(__file__).resolve().parent.parent / "data" / "features"
DFO_STATION_DAYS_CSV = Path(__file__).resolve().parent.parent / "data_raw" / "dfo" / "station_flood_days.csv"
GFD_STATION_DAYS_CSV = Path(__file__).resolve().parent.parent / "data_raw" / "gfd" / "station_flood_days.csv"
GFM_STATION_DAYS_CSV = Path(__file__).resolve().parent.parent / "data_raw" / "gfm" / "station_flood_days.csv"
FFWC_STATION_DAYS_CSV = Path(__file__).resolve().parent.parent / "data_raw" / "ffwc_reports" / "station_flood_days.csv"

LAG_DAYS = [1, 2, 3, 5]
ROLLING_WINDOWS = [7, 14]
SOIL_TREND_DAYS = 30
SWI_HALFLIFE_DAYS = 10  # see add_lags_and_rolling()'s SWI comment
HORIZONS = {"24h": 1, "48h": 2, "72h": 3}  # horizon name -> days ahead

# (station_id -> (upstream_station_id, travel_time_days)). Only pairs with
# real, checkable geography -- see module docstring. Distances are
# approximate; 1 day is the default for adjacent chain steps (consistent
# with how FFWC bulletins commonly use ~1-day-upstream stations as a
# forecast reference), bumped to 2 for the longer confluence segments.
UPSTREAM_CHAIN: dict[str, tuple[str, int]] = {
    # Jamuna/Brahmaputra mainstem, north to south
    "SW90": ("SW17", 1),    # Bahadurabad <- Chilmari
    "SW93": ("SW90", 1),    # Sariakandi <- Bahadurabad
    "SW99": ("SW93", 1),    # Sirajganj <- Sariakandi
    # Teesta
    "TE02": ("TE01", 1),    # Kaunia <- Dalia (Teesta Barrage)
    # Ganges/Padma mainstem
    "GA02": ("GA01", 1),    # Goalanda <- Hardinge Bridge
    "GA03": ("GA02", 1),    # Mawa <- Goalanda
    "GA04": ("GA02", 1),    # Bhagyakul <- Goalanda
    # Lower Meghna confluence (combines both Padma and Meghna chains)
    "ME01": ("GA03", 1),    # Chandpur <- Mawa (Padma side)
    "ME02_from_surma": None,  # placeholder, see below -- Bhairab Bazar has two real upstream inputs
}
# Bhairab Bazar (ME02) sits below BOTH the Surma and Kushiyara systems --
# a real limitation of the simple one-upstream-station model above (it
# can only carry one lag feature per station). Approximated with the
# larger of the two systems (Kushiyara via KU01) rather than fabricating a
# combined index; documented, not silently dropped.
UPSTREAM_CHAIN["ME02"] = ("KU01", 2)
del UPSTREAM_CHAIN["ME02_from_surma"]

# GFMS's Flood_byStor is a sparse "event flag" grid, not a continuous
# discharge/intensity series: empirically confirmed 2026-08-07 that across
# ALL 30 stations x 25 years of raw data (274,920 rows) there is not one
# single exact-0.0 value -- every non-blank row is a positive flood
# detection (4,563 rows), everything else is blank/NaN, including ordinary
# non-flood days *within* archive-accessible months (e.g. all of Jan-Feb
# 2014 is blank for every station despite 2014 being a fully accessible
# year -- see ingest_gfms.py's probe_accessible_months()). So a blank
# flood_byStor means one of two very different things: "checked, wasn't
# flooding" (inside an accessible month) or "never checked at all" (outside
# one -- i.e. all of 1950-2012 and Apr 2016-2020, which is ~88% of the full
# table). Silently treating both as "not flooding" would bias a model
# toward learning "post-2013/2021 calendar dates" instead of real
# hydrology, since positives can only ever appear in the accessible window.
#
# Fix: only conclude a confident "False" (no flood in the horizon window)
# when EVERY day in that window falls in a known-accessible date range; a
# positive hit is always trusted (a real value was recorded, full stop),
# but a horizon window that includes any inaccessible day and had no
# positive hit is left NaN (unknown), not False. This mirrors the existing
# end-of-series NaN truncation logic below, applied to the label's *source
# data availability* rather than just the table's edge.
#
# Accessible date ranges per ingest_gfms.py's empirical probe (2026-08-05/07,
# documented in MODEL_BUILD_PLAN.md): 2013-01-01 through 2016-03-31, and
# 2021-01-01 through 2026-02-02. The end date is exact, not just
# month-granular -- ingest_gfms.py's LAST_DATE cutoff (2026-02-02, when
# GFMS's real-time feed confirmed stalled) means Feb 3-28 2026 was NEVER
# fetched at all (verified: the raw CSV's last row is 2026-02-02, nothing
# after it). An earlier version of this check used year-month codes, which
# wrongly treated all of February 2026 as "accessible" and would have
# produced spurious confident-False labels for the last ~26 days of that
# month -- caught before it reached training data (see DECISIONS.md §12).
ACCESSIBLE_RANGES: list[tuple[str, str]] = [
    ("2013-01-01", "2016-03-31"),
    ("2021-01-01", "2026-02-02"),
]


def _accessible_mask(dates: pd.Series) -> pd.Series:
    mask = pd.Series(False, index=dates.index)
    for start, end in ACCESSIBLE_RANGES:
        mask |= (dates >= pd.Timestamp(start)) & (dates <= pd.Timestamp(end))
    return mask


def _load_station_days_csv(path: Path, source_name: str) -> dict[str, list[tuple[dt.date, dt.date]]]:
    """Shared loader for any "station_id,began,ended,..." CSV -- both
    ingest_dfo_floods.py and ingest_global_flood_db.py write this exact
    schema. Missing file -> empty dict + a note, not an error, so
    build_features.py still works with whichever positive-only sources
    have actually been run."""
    if not path.exists():
        print(f"  NOTE: {path} not found -- run the {source_name} ingest script "
              f"to include its events. Proceeding without this source.")
        return {}
    events: dict[str, list[tuple[dt.date, dt.date]]] = defaultdict(list)
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            began = dt.date.fromisoformat(row["began"])
            ended = dt.date.fromisoformat(row["ended"])
            events[row["station_id"]].append((began, ended))
    return dict(events)


def load_positive_only_events() -> dict[str, list[tuple[dt.date, dt.date]]]:
    """station_id -> list of (began, ended) date ranges, merged from every
    positive-only historical flood-event source this project has (DFO
    1985-2010, GFD/Global Flood Database 2002-2017, GFM/Copernicus Global
    Flood Monitoring 2016-2020, FFWC Annual Flood Reports 2012-2021 -- see
    ingest_dfo_floods.py, ingest_global_flood_db.py,
    ingest_copernicus_gfm.py, ingest_ffwc_reports.py). All four are trusted
    identically: a match is a real positive, absence of a match is NOT
    evidence of a negative (see DECISIONS.md SS13/SS16) -- so merging them
    is just a union of positive evidence, no reconciliation between sources
    is needed the way GFMS-vs-MCDWD required in SS5 (none of these
    contradict each other, they only ever add more trusted positives)."""
    merged: dict[str, list[tuple[dt.date, dt.date]]] = defaultdict(list)
    sources = [
        (DFO_STATION_DAYS_CSV, "DFO"),
        (GFD_STATION_DAYS_CSV, "Global Flood Database"),
        (GFM_STATION_DAYS_CSV, "Copernicus GFM"),
        (FFWC_STATION_DAYS_CSV, "FFWC Annual Flood Reports"),
    ]
    for path, name in sources:
        for station_id, intervals in _load_station_days_csv(path, name).items():
            merged[station_id].extend(intervals)
    return dict(merged)


def add_lags_and_rolling(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("date").reset_index(drop=True)
    base_cols = ["rainfall_local_mm", "rainfall_upstream_mm", "soil_moisture_local", "river_discharge_m3s"]

    for col in base_cols:
        for lag in LAG_DAYS:
            df[f"{col}_lag{lag}d"] = df[col].shift(lag)

    for col in ["rainfall_local_mm", "rainfall_upstream_mm"]:
        for window in ROLLING_WINDOWS:
            df[f"{col}_sum{window}d"] = df[col].rolling(window, min_periods=1).sum()
        recent7 = df[col].rolling(7, min_periods=1).sum()
        prior7 = df[col].shift(7).rolling(7, min_periods=1).sum()
        df[f"{col}_trend_ratio"] = recent7 / prior7.replace(0, np.nan)

    df["soil_moisture_delta_30d"] = df["soil_moisture_local"] - df["soil_moisture_local"].shift(SOIL_TREND_DAYS)

    # Soil Wetness Index (SWI) -- an exponential recursive filter over raw
    # surface soil moisture (Wagner et al. 1999's standard method for
    # deriving a root-zone-like antecedent-wetness proxy from a surface
    # observation), found via literature review 2026-08-08 (DECISIONS.md
    # SS17) as a richer companion to the existing raw-value +
    # soil_moisture_delta_30d features -- no new data needed, pure
    # feature-engineering on soil_moisture_local we already have.
    # pandas' .ewm(halflife=T) computes exactly this recursive form
    # (SWI[t] = SWI[t-1] + K*(SM[t]-SWI[t-1]), K set by the halflife) --
    # no manual loop needed. T=SWI_HALFLIFE_DAYS is a flood-relevant
    # "recent antecedent wetness" timescale (fast catchment response), at
    # the shorter end of the range used in the literature (which spans
    # days to ~100 for deeper groundwater proxies) since river flooding
    # here responds to catchment wetness over days, not months.
    df["soil_moisture_swi"] = df["soil_moisture_local"].ewm(halflife=SWI_HALFLIFE_DAYS, adjust=False).mean()

    return df


def add_static_terrain_features(df: pd.DataFrame, station_id: str) -> pd.DataFrame:
    """Attach elevation_m/hand_m (see stations.py's STATIC_TERRAIN) as
    constant-per-station columns. Static geomorphological features like
    these were entirely absent from this project's feature set until now
    -- every existing feature is weather/time-series-driven -- despite
    recurring independently across multiple literature sources as
    important flood-susceptibility factors (DECISIONS.md SS17). hand_m
    (Height Above Nearest Drainage) in particular is a well-established,
    peer-reviewed proxy for "how close is this point, vertically, to the
    nearest stream" -- lower means more flood-prone."""
    elevation_m, hand_m = STATIC_TERRAIN[station_id]
    df["elevation_m"] = elevation_m
    df["hand_m"] = hand_m
    return df


def add_horizon_labels(df: pd.DataFrame, station_id: str, positive_only_events: dict[str, list[tuple[dt.date, dt.date]]]) -> pd.DataFrame:
    df = df.sort_values("date").reset_index(drop=True)
    flood_positive = df["flood_byStor"].notna() & (df["flood_byStor"] > 0)

    # Fold in DFO (1985-2010) + Global Flood Database (2002-2017) matched
    # historical events as additional trusted positives -- see module
    # docstring and DECISIONS.md SS13/SS15. Only ORs into the positive
    # side; never affects `observed` below, since an unmatched day under
    # either source is not good evidence of "no flood" the way an
    # accessible-but-non-detecting GFMS day is.
    for began, ended in positive_only_events.get(station_id, []):
        flood_positive |= (df["date"] >= pd.Timestamp(began)) & (df["date"] <= pd.Timestamp(ended))

    # Nullable boolean dtype so shift()'s introduced NaN stays pd.NA instead
    # of silently upcasting to object dtype (which triggered a pandas
    # FutureWarning on fillna below) -- purely a dtype-hygiene fix, no
    # behavior change.
    observed = _accessible_mask(df["date"]).astype("boolean")  # see ACCESSIBLE_RANGES note above

    for name, n_days in HORIZONS.items():
        # "any positive in the next n_days" -- shift the positive-flag series
        # backward (negative shift = look into the future) for each of the
        # n_days ahead, OR them together. Never touches today's own value.
        future_hits = [flood_positive.shift(-k) for k in range(1, n_days + 1)]
        any_hit = pd.concat(future_hits, axis=1).any(axis=1)
        # A confident False requires every day in the window to have been in
        # a known-accessible (checkable) date range -- see ACCESSIBLE_RANGES
        # note above. shift() introduces NaN at the series edges, which
        # fillna(False) treats as "not observed" (conservative: unknown
        # trailing days can't support a confident negative either).
        future_observed = [observed.shift(-k).fillna(False).astype(bool) for k in range(1, n_days + 1)]
        all_observed = pd.concat(future_observed, axis=1).all(axis=1)
        # A day where we can't see far enough ahead (near the end of the
        # table) can't be labeled -- leave as NaN, not False, so it's
        # excluded from training rather than silently counted as "safe".
        can_see_ahead = df.index < (len(df) - n_days)
        confident_label = np.where(any_hit, True, np.where(all_observed, False, np.nan))
        df[f"flood_within_{name}"] = pd.Series(
            np.where(can_see_ahead, confident_label, np.nan), index=df.index
        )

        # DECISIONS.md SS13: pre-2012 (DFO-only) and post-2012 (GFMS) rows
        # come from label-generation processes with very different positive
        # rates and cannot be blended silently -- this column lets Part 4
        # filter/stratify/weight explicitly instead of guessing from dates.
        # "observed": the horizon window fell fully inside GFMS's accessible
        #   range, so both True and False labels here are as reliable as
        #   GFMS gets (the normal, balanced case).
        # "unobserved_positive": labeled True purely because of a hit found
        #   outside full GFMS observation (i.e. relies at least partly on a
        #   DFO match, or a GFMS positive whose window wasn't fully
        #   accessible) -- trustworthy as a positive, but there is no
        #   equivalent "unobserved_negative": we never claim False without
        #   full observation, so this category is positive-only by
        #   construction.
        regime = np.where(all_observed, "observed",
                           np.where(any_hit, "unobserved_positive", None))
        df[f"flood_within_{name}_label_regime"] = pd.Series(
            np.where(can_see_ahead, regime, None), index=df.index
        )
    return df


def add_upstream_travel_time_feature(df: pd.DataFrame, station_id: str, all_tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    pair = UPSTREAM_CHAIN.get(station_id)
    if pair is None:
        return df
    upstream_id, lag_days = pair
    if upstream_id not in all_tables:
        print(f"  WARNING: {station_id}'s upstream chain station {upstream_id} not found, skipping this feature")
        return df
    upstream = all_tables[upstream_id][["date", "river_discharge_m3s"]].copy()
    upstream["date"] = upstream["date"] + pd.Timedelta(days=lag_days)
    upstream = upstream.rename(columns={"river_discharge_m3s": f"upstream_chain_discharge_lag{lag_days}d"})
    df = df.merge(upstream, on="date", how="left")
    return df


def add_upstream_reference_discharge_feature(df: pd.DataFrame, station_id: str) -> pd.DataFrame:
    """Same idea as add_upstream_travel_time_feature(), but for an
    upstream INDIA-side reference point (stations.py's
    UPSTREAM_REFERENCE_STATIONS/UPSTREAM_REFERENCE_CHAIN) instead of
    another in-network station -- added 2026-08-09 per HaorFloodAlert's
    finding (DECISIONS.md SS17). Reads the raw discharge CSV directly
    since the reference point was never part of build_dataset.py's merge
    (it's not one of our 30 stations, see stations.py's module comment)."""
    pair = UPSTREAM_REFERENCE_CHAIN.get(station_id)
    if pair is None:
        return df
    ref_id, lag_days = pair
    ref_path = DISCHARGE_RAW_DIR / f"discharge_{ref_id}.csv"
    if not ref_path.exists():
        print(f"  NOTE: {ref_path} not found -- run `ingest_discharge.py --station-id {ref_id}` "
              f"first to include this feature. Skipping for {station_id}.")
        return df
    ref = pd.read_csv(ref_path, parse_dates=["date"])
    ref["date"] = ref["date"] + pd.Timedelta(days=lag_days)
    col = f"upstream_reference_discharge_lag{lag_days}d"
    ref = ref.rename(columns={"river_discharge_m3s": col})[["date", col]]
    df = df.merge(ref, on="date", how="left")
    return df


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", required=True, help="which backend/data/processed/<version>/ to read")
    args = parser.parse_args()

    in_dir = PROCESSED_ROOT / args.version
    out_dir = FEATURES_ROOT / args.version
    out_dir.mkdir(parents=True, exist_ok=True)

    station_files = sorted(in_dir.glob("*.parquet"))
    station_files = [f for f in station_files if f.stem != "all_stations"]
    if not station_files:
        raise SystemExit(f"No per-station parquet files found in {in_dir}")

    print(f"Loading {len(station_files)} station tables from {in_dir}...")
    raw_tables = {f.stem: pd.read_parquet(f) for f in station_files}

    positive_only_events = load_positive_only_events()
    if positive_only_events:
        print(f"Loaded DFO + Global Flood Database historical events for {len(positive_only_events)} stations "
              f"(extends positive-only labels back to 1985, see DECISIONS.md SS13/SS15).")

    all_frames = []
    for station_id, raw in raw_tables.items():
        print(f"Building features for {station_id}...")
        df = add_lags_and_rolling(raw)
        df = add_static_terrain_features(df, station_id)
        df = add_horizon_labels(df, station_id, positive_only_events)
        df = add_upstream_travel_time_feature(df, station_id, raw_tables)
        df = add_upstream_reference_discharge_feature(df, station_id)

        n_labeled = int(df["flood_within_72h"].notna().sum())
        n_positive_72h = int((df["flood_within_72h"] == True).sum())  # noqa: E712
        print(f"  {len(df)} rows, {n_labeled} labelable (72h horizon fits), "
              f"{n_positive_72h} positive ({100*n_positive_72h/n_labeled:.2f}%)" if n_labeled else "  no labelable rows")

        csv_path = out_dir / f"{station_id}.csv"
        parquet_path = out_dir / f"{station_id}.parquet"
        df.to_csv(csv_path, index=False)
        df.to_parquet(parquet_path, index=False)
        all_frames.append(df)

    combined = pd.concat(all_frames, ignore_index=True)
    combined_path = out_dir / "all_stations.parquet"
    combined.to_parquet(combined_path, index=False)
    print(f"\nWrote {len(all_frames)} per-station files + combined ({len(combined)} total rows) under {out_dir}")
    print(f"Columns: {list(combined.columns)}")


if __name__ == "__main__":
    main()
