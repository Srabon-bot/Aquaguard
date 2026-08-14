"""Part 3 extension -- ingest the Dartmouth Flood Observatory (DFO) Global
Active Archive of Large Flood Events as a SECOND, POSITIVE-ONLY flood label
source, to extend labeled coverage back before GFMS's earliest accessible
year (2013).

Why this exists: build_features.py's flood_within_Nh labels can only be
"confidently False" inside GFMS's known-accessible archive window
(2013-01-01..2016-03-31, 2021-01-01..2026-02-02, see DECISIONS.md SS12) --
everything before 2013 is genuinely unlabeled, not "no flood happened".
DFO's archive covers 1985-2010 for Bangladesh with real event dates and
(critically) free-text Rivers/Detailed_L fields naming the actual rivers
and districts affected -- close enough to our station river/town names to
match many events to specific stations without guessing.

Source and its real limitations (read before trusting this):
  - DFO's own live site (floodobservatory.colorado.edu) underwent a
    redesign in Jan 2026 and is mid-transition as of 2026-08-07 -- the
    direct archive download path (/Archives/) currently returns HTTP 410
    Gone. Verified directly, not assumed. So this script does NOT hit DFO's
    own server; it uses the stable HDX (UN OCHA Humanitarian Data Exchange)
    mirror instead: a static, versioned snapshot dated 2019-04-18, hosted on
    HDX's own stable infrastructure (not DFO's in-flux one).
      https://data.humdata.org/dataset/global-active-archive-of-large-flood-events-dfo
  - That snapshot's actual event coverage tops out at 2010 (matches DFO's
    own "more than 4000 records...1985-2010" description) -- there is NO
    overlap/conflict with GFMS's 2013+ window, so no cross-source
    disagreement to resolve here (contrast with the GFMS-vs-MCDWD case in
    DECISIONS.md SS5, which did have overlap).
  - DFO only records LARGE, notable flood events -- it is nowhere near as
    exhaustive as GFMS's daily satellite grid. This means "no DFO event
    matched to this station on this day" is NOT strong evidence of "no
    flood" (unlike GFMS's own accessible-window negatives). Accordingly,
    THIS SOURCE IS USED FOR POSITIVES ONLY: build_features.py ORs a DFO
    match into the positive side of the label, but does NOT treat
    DFO-covered non-matching days as a confident False. See DECISIONS.md
    SS12/SS13 for the full reasoning.
  - Each event has only ONE representative point (not a real polygon
    extent) plus free-text Rivers/Detailed_L fields -- station attribution
    here is done by keyword/substring matching against those text fields
    (river name + town name, with known spelling variants seen in the
    source data, e.g. "Kushiara"/"Kushiyara", "Bramaputra"/"Brahmaputra"),
    not by geometry. Events with no keyword match to any of our 30 stations
    are logged and left unmatched, not force-assigned to a "nearest" guess.

Usage:
    python train/ingest_dfo_floods.py
    (re-)downloads the HDX snapshot if not already present, extracts
    Bangladesh events, matches them to stations, and writes
    backend/data_raw/dfo/bangladesh_events.csv and
    backend/data_raw/dfo/station_flood_days.csv (the actual per-station
    per-event-day rows build_features.py consumes).
"""

import argparse
import csv
import datetime as dt
import zipfile
from pathlib import Path

import requests
import shapefile

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from stations import STATIONS  # noqa: E402

OUT_DIR = Path(__file__).resolve().parent.parent / "data_raw" / "dfo"
ZIP_URL = (
    "https://data.humdata.org/dataset/1fd855de-57c6-42b3-83e1-9cf989b0f70d/"
    "resource/984cc240-b2b7-4266-9f61-5715a9e10ff5/download/"
    "wlf_nhr_fl_dfomasterlist_20190418.zip"
)
SHP_STEM = "wlf_nhr_fl_dfomasterlist_20190418"

# station_id -> list of case-insensitive substrings to search for in the
# event's Rivers + Detailed_L text. River name first (with real spelling
# variants observed in the source data itself), then the station's own
# town/place name(s) pulled from stations.py's `name` field. Deliberately
# conservative -- e.g. "Old Brahmaputra" (OB01) is NOT matched on the bare
# word "Brahmaputra" alone, since that would over-match onto mainstem-Jamuna
# events; it relies on the town name (Mymensingh) instead.
STATION_KEYWORDS: dict[str, list[str]] = {
    "SW90": ["jamuna", "bahadurabad"],
    "SW93": ["jamuna", "sariakandi", "sariakandhi"],
    "SW99": ["jamuna", "sirajganj", "sirajgonj", "serajganj"],  # "Serajganj" spelling seen in FFWC annual reports
    "SW17": ["brahmaputra", "bramaputra", "brahmputra", "chilmari"],
    "TE01": ["teesta", "tista", "dalia"],
    "TE02": ["teesta", "tista", "kaunia", "rangpur"],
    "OB01": ["mymensingh", "mymensing"],
    "DH01": ["dharla", "darala", "dharala", "kurigram"],
    "GA01": ["ganges", "hardinge", "kushtia"],
    "GA02": ["padma", "goalanda", "goalundo"],
    "GA03": ["padma", "mawa"],
    "GA04": ["padma", "bhagyakul", "munshiganj"],
    "GO01": ["gorai", "kamarkhali", "kushtia"],
    "GO02": ["madhumati", "gopalganj", "gopalgonj"],
    "ME01": ["meghna", "chandpur"],
    "ME02": ["meghna", "bhairab"],
    "ME03": ["dhaleswari", "dhaleshwari", "buriganga", "dhaka"],
    "SW267": ["surma", "sunamganj", "sunamgonj"],
    "SW174": ["surma", "sylhet"],
    "KU01": ["kushiara", "kushiyara", "sherpur"],
    "KU02": ["kushiara", "kushiyara", "amalshid", "zakiganj"],
    "NM01": ["someswari", "someshwari", "netrokona", "netrakona", "durgapur"],
    "CH01": ["karnaphuli", "rangamati"],
    "CH02": ["sangu", "bandarban"],
    "CH03": ["halda", "chittagong"],
    "CO01": ["kirtankhola", "barisal"],
    "CO02": ["rupsha", "khulna"],
    "CO03": ["baleswar", "baleshwar", "bagerhat"],
    "CO04": ["payra", "patuakhali"],
    "CO05": ["bakkhali", "cox's bazar", "coxs bazar", "cox bazar"],
}


def ensure_shapefile() -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    shp_path = OUT_DIR / f"{SHP_STEM}.shp"
    if shp_path.exists():
        return shp_path
    zip_path = OUT_DIR / "dfo_archive.zip"
    print(f"Downloading DFO archive (HDX mirror) from {ZIP_URL} ...")
    resp = requests.get(ZIP_URL, timeout=60)
    resp.raise_for_status()
    zip_path.write_bytes(resp.content)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(OUT_DIR)
    print(f"Extracted to {OUT_DIR}")
    return shp_path


def load_bangladesh_events(shp_path: Path) -> list[dict]:
    sf = shapefile.Reader(str(shp_path.with_suffix("")))
    fields = [f[0] for f in sf.fields[1:]]
    events = []
    for i in range(len(sf)):
        rec = dict(zip(fields, sf.record(i)))
        if "Bangladesh" not in str(rec.get("Country__c", "")):
            continue
        began, ended = rec.get("Began"), rec.get("Ended")
        if not began or not ended:
            continue
        events.append({
            "began": began if isinstance(began, dt.date) else None,
            "ended": ended if isinstance(ended, dt.date) else None,
            "severity": rec.get("Severity__"),
            "main_cause": (rec.get("Main_cause") or "").strip(),
            "rivers": (rec.get("Rivers") or "").strip(),
            "detailed_location": (rec.get("Detailed_L") or "").strip(),
        })
    return [e for e in events if e["began"] and e["ended"]]


def match_stations(event: dict) -> list[str]:
    haystack = f"{event['rivers']} {event['detailed_location']}".lower()
    matched = []
    for station_id, keywords in STATION_KEYWORDS.items():
        if any(kw in haystack for kw in keywords):
            matched.append(station_id)
    return matched


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.parse_args()

    shp_path = ensure_shapefile()
    events = load_bangladesh_events(shp_path)
    print(f"Loaded {len(events)} Bangladesh events from DFO archive "
          f"({min(e['began'] for e in events)} to {max(e['ended'] for e in events)}).")

    events_csv = OUT_DIR / "bangladesh_events.csv"
    with open(events_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["began", "ended", "severity", "main_cause", "rivers", "detailed_location", "matched_stations"])
        n_matched, n_unmatched = 0, 0
        station_day_rows = []
        for e in events:
            matched = match_stations(e)
            w.writerow([e["began"], e["ended"], e["severity"], e["main_cause"],
                        e["rivers"], e["detailed_location"], ";".join(matched)])
            if matched:
                n_matched += 1
                for sid in matched:
                    station_day_rows.append((sid, e["began"], e["ended"], e["severity"]))
            else:
                n_unmatched += 1

    print(f"{n_matched} events matched to >=1 station, {n_unmatched} unmatched (no river/place keyword hit).")

    station_days_csv = OUT_DIR / "station_flood_days.csv"
    with open(station_days_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["station_id", "began", "ended", "severity"])
        for row in station_day_rows:
            w.writerow(row)

    # Coverage summary per station (sanity check before this feeds features).
    from collections import Counter
    counts = Counter(sid for sid, *_ in station_day_rows)
    print("\nPer-station matched-event counts:")
    for s in STATIONS:
        print(f"  {s.station_id:6s} {s.name:35s} {counts.get(s.station_id, 0)}")

    print(f"\nWrote {events_csv} and {station_days_csv}")


if __name__ == "__main__":
    main()
