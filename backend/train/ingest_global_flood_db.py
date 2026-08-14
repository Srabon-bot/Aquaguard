"""Part 3 extension #2 -- ingest the Global Flood Database (GFD; Tellman et
al. 2021, built by Cloud to Street + Dartmouth Flood Observatory from MODIS
imagery) via Google Earth Engine, as a THIRD positive-only flood label
source alongside GFMS (primary, 2013+) and DFO (1985-2010, see
ingest_dfo_floods.py).

Why this exists: GFD's "flooded" band is a per-pixel (250m), per-EVENT flood
mask -- each event is one Earth Engine Image spanning the event's
begin/end date, built by comparing observed water extent against
`jrc_perm_water` (JRC's permanent-water baseline) so it's flood-specific,
not just "any water" (spot-checked directly, see MODEL_BUILD_PLAN.md --
stations with flooded=1 showed jrc_perm_water=0, ruling out a
permanent-river false-positive). This gives REAL per-pixel precision at our
30 station points, unlike DFO's single centroid-point + free-text keyword
matching -- and covers a few events DFO's snapshot doesn't (2011, 2014,
2016, 2017), most importantly two events squarely inside the currently
totally-blank GFMS gap (Apr 2016-2020): 2016-07-25..08-26 and
2017-03-30..04-18 / 2017-08-10..08-26.

Runs entirely server-side (Earth Engine's reduceRegion/sampleRegions) --
no bulk downloads. This is a deliberate pivot away from an earlier attempt
to use UNOSAT's raw flood-extent shapefiles for the same purpose: those
files turned out to be 30MB-1.5GB EACH (full-resolution SAR polygon
meshes across many sensors/dates/derived-layer-types), impractical to
fetch at the scale needed. GFD gives comparable per-pixel precision without
that cost, because Earth Engine does the heavy lifting server-side and
only returns the small per-point result.

Filtered to `dfo_country == "Bangladesh"` (the event's PRIMARY country,
not the broader `countries` field which includes any country touched even
peripherally by a larger regional event) -- 23 events, matching the same
precision-over-recall judgment call already made for DFO's own country
filter. Checked all 23 against our 30 station points before committing to
this script: 20/23 touch at least one station (0-9 stations each,
median ~3) -- see MODEL_BUILD_PLAN.md for the full per-event breakdown.

Same trust model as DFO (DECISIONS.md SS13): a station showing flooded=1
for an event is a trusted POSITIVE for that event's full date range; a
station NOT showing flooded=1 is NOT treated as a confident negative (GFD,
like DFO, only maps events large enough to be catalogued -- absence of
detection here doesn't mean "definitely no flood", just "not covered by
this event's mapped extent"). build_features.py folds this in exactly like
DFO's station_flood_days.csv, via the same positive-only OR-in mechanism.

Usage:
    python train/ingest_global_flood_db.py
    Requires Earth Engine already authenticated (see DECISIONS.md open
    items -- `earthengine authenticate` run once, credentials cached
    locally) and the `pred-flood` Cloud project registered for Earth
    Engine access (already done, see MODEL_BUILD_PLAN.md 2026-08-07/08).
"""

import argparse
import csv
import datetime as dt
from pathlib import Path

import ee

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from stations import STATIONS  # noqa: E402

OUT_DIR = Path(__file__).resolve().parent.parent / "data_raw" / "gfd"
EE_PROJECT = "pred-flood"
COLLECTION = "GLOBAL_FLOOD_DB/MODIS_EVENTS/V1"
SAMPLE_SCALE_M = 250  # native MODIS resolution of the 'flooded' band


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ee.Initialize(project=EE_PROJECT)

    col = ee.ImageCollection(COLLECTION)
    bgd = col.filter(ee.Filter.stringContains("dfo_country", "Bangladesh"))
    n_events = bgd.size().getInfo()
    print(f"Found {n_events} Bangladesh-primary-country events in {COLLECTION}")

    points = ee.FeatureCollection([
        ee.Feature(ee.Geometry.Point([s.lon, s.lat]), {"station_id": s.station_id})
        for s in STATIONS
    ])

    events = bgd.toList(n_events).getInfo()
    rows = []
    events_csv = OUT_DIR / "bangladesh_events.csv"
    with open(events_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["gfd_id", "began", "ended", "dfo_severity", "dfo_main_cause", "matched_stations"])

        for i, feat in enumerate(events):
            props = feat["properties"]
            gfd_id = props["id"]
            began = dt.datetime.utcfromtimestamp(props["system:time_start"] / 1000).date()
            ended = dt.datetime.utcfromtimestamp(props["system:time_end"] / 1000).date()

            img = ee.Image(feat["id"]).select("flooded")
            sampled = img.sampleRegions(collection=points, scale=SAMPLE_SCALE_M, geometries=False).getInfo()
            matched = [x["properties"]["station_id"] for x in sampled["features"] if x["properties"].get("flooded") == 1]

            w.writerow([gfd_id, began, ended, props.get("dfo_severity"), props.get("dfo_main_cause"), ";".join(matched)])
            for sid in matched:
                rows.append((sid, began, ended, props.get("dfo_severity")))
            print(f"  [{i+1}/{n_events}] {began}..{ended} (id {gfd_id}): {len(matched)} stations -- {matched}")

    station_days_csv = OUT_DIR / "station_flood_days.csv"
    with open(station_days_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["station_id", "began", "ended", "severity"])
        for row in rows:
            w.writerow(row)

    from collections import Counter
    counts = Counter(sid for sid, *_ in rows)
    print("\nPer-station matched-event counts:")
    for s in STATIONS:
        print(f"  {s.station_id:6s} {s.name:35s} {counts.get(s.station_id, 0)}")
    print(f"\nWrote {events_csv} and {station_days_csv}")


if __name__ == "__main__":
    main()
