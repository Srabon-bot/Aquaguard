"""Part 3 extension #4 -- ingest FFWC's own Annual Flood Reports (2012-2021)
as a FOURTH positive-only flood label source, alongside DFO (1985-2010),
GFD (2002-2017) and Copernicus GFM (2016-2020). See DECISIONS.md SS17/SS18
for how this lead was found (HaorFloodAlert's literature review) and why it
was deliberately deferred to its own session.

Why this source matters more than the other three, for the years it covers:
these are FFWC's OWN reports -- the actual national forecasting agency,
using their own ~100+ gauge network (a superset of our 30 stations) and
their own definition of "Danger Level" (the same DL our stations.py already
stores) -- authoritative, not a remote-sensing proxy. They cover 2012-2021,
squarely including 2017-2020, our previously thinnest gap (GFM only found
28 positive station-days there via sparse SAR revisits; these reports give
direct textual confirmation from the agency that actually watches these
gauges daily).

Real access problem found and fixed before trusting anything: FFWC's
current site (www.ffwc.gov.bd) is an Angular/React SPA whose server-side
routing has NO real 404 -- ANY path, including /images/annual12.pdf,
returns HTTP 200 with the exact same 30KB index-page HTML shell (verified
directly: all 14 "PDF" downloads from that domain were byte-identical,
md5 2a27d90...). The actual PDFs live on the legacy domain,
old.ffwc.gov.bd, which still serves them as real static files (confirmed:
distinct sizes 6.8-11MB, distinct page counts 10-127, real extractable
text) -- old.ffwc.gov.bd/images/annual12.pdf through annual21.pdf all
resolve; annual22.pdf+ give a genuine Apache 404 (report years 2022+ were
apparently never uploaded there), so this source's real coverage is
2012-2021, not the originally-hoped 2012-2025.

Report structure (Chapter 3, "River Situation", confirmed present across
2012-2021 with only page-number drift -- located dynamically per report via
each page's own heading line, not a fixed page number): basin-by-basin
prose narrative naming individual river/station pairs, giving EITHER an
explicit continuous above-Danger-Level date range in one sentence (older
reports, e.g. 2012: "crossed the DL on 6 July...flowed above DL for 6 days
till 11 July") OR a single peak-date mention (newer reports, e.g. 2020:
"attained the peak of 32.92 m PWD...on 29th September"). This script mines
BOTH: for each sentence in the chapter, it first matches explicit "DATE to
DATE" sub-ranges (e.g. "6 July...till 11 July"), then treats any leftover
unconsumed date mention as its own single-day positive. Each is kept as a
SEPARATE (began, ended) interval, not collapsed into one min/max span per
sentence -- some sentences narrate two or three genuinely separate flood
pulses joined by commas/"then"/"finally" rather than periods, e.g. "...from
1st April to 6th April for 6 days, then 3rd June to 20th July for 44 days
and finally from 4th August to 16th September..." (a real example from the
2017 report). An earlier version of this script took min/max across the
whole sentence and would have manufactured a false ~5-month continuous
flood claim spanning two real gaps the report itself says were dry --
caught by spot-checking the longest resulting "intervals" before trusting
any of this (the worst was a fabricated 169-day span) and fixed to emit the
3 separate real pulses instead. Standalone "DD-DD Month" hyphenated ranges
(no "to") were considered and rejected as a pattern to parse: spot-checking
their actual occurrences across all 10 reports showed they're almost always
pdfplumber's plain-text reconstruction of a numeric TABLE column mashed
against a row label (e.g. "10 - 5 Brahmaputra"), not real date ranges --
attempting to parse them would trade a coverage gain for new false
positives, not a trade worth making.

Safety guard: any sentence containing a 4-digit year token other than the
report's own year is skipped entirely (not just the foreign-year part) --
these reports also contain historical-comparison tables/captions (e.g.
"...current year 2020 and historical events of 2007 and 1998") reconstructed
by pdfplumber's plain extract_text() as flowing text alongside the prose;
excluding them outright is simpler and safer than trying to separate
Table 3.x's tabular numbers from Chapter 3's narrative programmatically.
Table 3.x's "Days above Danger Level" COLUMN (a count, no dates) is not
parsed by this script -- it can't produce a (began, ended) range on its own,
and cross-checking prose-derived positives against it is left as a possible
future addition, not blocking this one.

Same trust model as DFO/GFD/GFM (DECISIONS.md SS13/SS16): a match here is a
trusted POSITIVE; a station/day this script does NOT flag is NOT a
confident negative (FFWC's prose only narrates notable episodes, not a
daily grid -- absence of a mention proves nothing).

Usage:
    python train/ingest_ffwc_reports.py
    (re-)downloads the 2012-2021 PDFs from old.ffwc.gov.bd if not already
    present, parses Chapter 3 of each, matches to stations, and writes
    backend/data_raw/ffwc_reports/matched_sentences.csv (full audit trail
    -- year, station, dates, source sentence) and
    backend/data_raw/ffwc_reports/station_flood_days.csv (the
    station_id,began,ended,severity rows build_features.py consumes).
"""

import argparse
import csv
import datetime as dt
import re
import sys
from collections import Counter
from pathlib import Path

import pdfplumber
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stations import STATIONS  # noqa: E402
from ingest_dfo_floods import STATION_KEYWORDS as _DFO_STATION_KEYWORDS  # noqa: E402

# DFO's STATION_KEYWORDS include bare basin/river names (e.g. "jamuna") as a
# fallback because DFO events are one point per whole-basin event -- basin-
# wide matching is the right granularity there. FFWC's Chapter 3 instead
# narrates INDIVIDUAL named gauges one sentence at a time (e.g. Aricha,
# Kazipur, Fulchari, Bahadurabad, Sariakandi and Serajganj are all separate
# Jamuna gauges, each with their own sentence) -- reusing the bare river-name
# keywords here caused real over-matching, caught by spot-checking: every
# "Jamuna" sentence, regardless of which specific gauge it named, was being
# attributed to ALL THREE of SW90/SW93/SW99 (identical 71-match counts gave
# it away). So any keyword shared by >1 station in the DFO dict -- always a
# bare river/basin name, never a place name -- is dropped here; matching
# falls back to the place-name keywords only, which are gauge-specific.
_kw_station_counts = Counter(kw for kws in _DFO_STATION_KEYWORDS.values() for kw in kws)
STATION_KEYWORDS = {
    sid: [kw for kw in kws if _kw_station_counts[kw] == 1]
    for sid, kws in _DFO_STATION_KEYWORDS.items()
}

OUT_DIR = Path(__file__).resolve().parent.parent / "data_raw" / "ffwc_reports"
BASE_URL = "http://old.ffwc.gov.bd/images"  # NOT www.ffwc.gov.bd -- see module docstring
REPORT_YEARS = list(range(2012, 2022))  # 2012-2021 confirmed downloadable; 2022+ 404s on this domain

MONTHS = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10, "nov": 11, "november": 11, "dec": 12, "december": 12,
}
MONTH_PATTERN = "|".join(sorted(MONTHS, key=len, reverse=True))
DATE_RE = re.compile(rf"\b(\d{{1,2}})(?:st|nd|rd|th)?\s+({MONTH_PATTERN})\b", re.IGNORECASE)
# A single sentence often narrates MULTIPLE separate above-DL pulses joined by
# commas/"then"/"finally" rather than periods, e.g. "...from 1st April to 6th
# April for 6 days, then 3rd June to 20th July for 44 days and finally from
# 4th August to 16th September..." -- naively taking min/max of every date in
# such a sentence would manufacture a false ~5-month continuous flood claim
# across gaps the report itself says were dry. So explicit "DATE to DATE"
# sub-ranges are matched FIRST and kept as separate intervals; only leftover
# dates not part of any such pair become standalone single-day positives.
RANGE_RE = re.compile(
    rf"\b(\d{{1,2}})(?:st|nd|rd|th)?\s+({MONTH_PATTERN})\s+to\s+(\d{{1,2}})(?:st|nd|rd|th)?\s+({MONTH_PATTERN})\b",
    re.IGNORECASE,
)
FOREIGN_YEAR_RE = re.compile(r"\b(19\d{2}|20\d{2})\b")
# Sentences reporting a station's SEASONAL PEAK still mention a date even when
# that peak stayed below Danger Level (e.g. "attained the peak of 29.98m on
# 5th August which was 2cm below the DL(30.0m)") -- a genuine did-NOT-flood
# narrative, not a positive. Found by spot-checking this script's own output
# before trusting it: 73/619 (12%) of first-pass matches were exactly this
# pattern. Any sentence containing one of these phrases is skipped in full
# rather than guessing which date in it (if any) is still safe.
NEGATION_RE = re.compile(
    r"\bbelow\b|\bdid not\b|\bdidn.t\b|\bno flood|\bnot cross|\bremained below"
    r"|\bunder (?:its|their) (?:respective )?DL\b|\bfailed to (?:cross|reach)|\bcould not (?:cross|reach)",
    re.IGNORECASE,
)
CHAPTER3_START_RE = re.compile(r"^CHAPTER\s*3\s*:?\s*RIVER SITUATION", re.IGNORECASE)
CHAPTER4_START_RE = re.compile(r"^CHAPTER\s*4\b", re.IGNORECASE)


def ensure_pdf(year: int) -> Path | None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    suffix = str(year)[2:]  # 2012 -> "12"
    path = OUT_DIR / f"annual{suffix}.pdf"
    if path.exists():
        return path
    url = f"{BASE_URL}/annual{suffix}.pdf"
    print(f"Downloading {year} report from {url} ...")
    resp = requests.get(url, timeout=90)
    if resp.status_code != 200 or resp.headers.get("Content-Type", "").startswith("text/html"):
        print(f"  NOT AVAILABLE ({resp.status_code}, {resp.headers.get('Content-Type')}) -- skipping {year}.")
        return None
    path.write_bytes(resp.content)
    return path


def find_chapter3_bounds(pdf: "pdfplumber.PDF") -> tuple[int, int] | None:
    """Locate Chapter 3's real content pages by scanning each page's own
    first line (not the Table of Contents' dotted-leader listing, which
    also contains "CHAPTER 3 : RIVER SITUATION" text but isn't the actual
    start of the chapter) -- robust to the page-number drift seen across
    reports (chapter 3 starts anywhere from printed page 20 to 38 depending
    on year)."""
    start = end = None
    for i, page in enumerate(pdf.pages):
        text = (page.extract_text() or "").strip()
        if not text:
            continue
        first_line = text.splitlines()[0]
        if start is None and CHAPTER3_START_RE.match(first_line):
            start = i
        elif start is not None and i > start and CHAPTER4_START_RE.match(first_line):
            end = i
            break
    if start is None:
        return None
    return start, (end if end is not None else start + 1)


def extract_chapter_text(pdf: "pdfplumber.PDF", start: int, end: int) -> str:
    pages_text = [(p.extract_text() or "") for p in pdf.pages[start:end]]
    return " ".join(pages_text).replace("\n", " ")


def split_sentences(text: str) -> list[str]:
    # Split on ". " / ".<end>" -- safe against decimal values like "27.6mPWD"
    # since those never have a space (or end-of-string) right after the period.
    return [s.strip() for s in re.split(r"(?<=\.)\s+", text) if s.strip()]


def _make_date(year: int, month_str: str, day_str: str) -> dt.date | None:
    try:
        return dt.date(year, MONTHS[month_str.lower()], int(day_str))
    except ValueError:
        return None  # malformed match (e.g. "32 July"), skip rather than guess


def extract_intervals(sentence: str, year: int) -> list[tuple[dt.date, dt.date]]:
    """Returns a list of (began, ended) positive intervals -- one per
    explicit "DATE to DATE" sub-range, plus one per leftover single-date
    mention not already consumed by a range match (began == ended for
    those). Kept as SEPARATE intervals rather than one min/max span per
    sentence -- see RANGE_RE's comment for why that matters."""
    intervals: list[tuple[dt.date, dt.date]] = []
    consumed_spans: list[tuple[int, int]] = []
    for m in RANGE_RE.finditer(sentence):
        d1 = _make_date(year, m.group(2), m.group(1))
        d2 = _make_date(year, m.group(4), m.group(3))
        if d1 and d2:
            intervals.append((min(d1, d2), max(d1, d2)))
            consumed_spans.append(m.span())

    for m in DATE_RE.finditer(sentence):
        if any(s <= m.start() and m.end() <= e for s, e in consumed_spans):
            continue  # already part of a matched range above
        d = _make_date(year, m.group(2), m.group(1))
        if d:
            intervals.append((d, d))
    return intervals


def match_stations(sentence: str) -> list[str]:
    haystack = sentence.lower()
    return [sid for sid, keywords in STATION_KEYWORDS.items() if any(kw in haystack for kw in keywords)]


def process_report(year: int, path: Path) -> list[tuple[str, dt.date, dt.date, int, str]]:
    """Returns rows: (station_id, began, ended, duration_days, sentence)."""
    rows = []
    with pdfplumber.open(path) as pdf:
        bounds = find_chapter3_bounds(pdf)
        if bounds is None:
            print(f"  {year}: could not locate Chapter 3 heading -- SKIPPED (format drift, not silently guessed).")
            return rows
        start, end = bounds
        text = extract_chapter_text(pdf, start, end)

    for sentence in split_sentences(text):
        foreign_years = {int(y) for y in FOREIGN_YEAR_RE.findall(sentence)}
        if foreign_years - {year}:
            continue  # historical-comparison sentence/table caption -- skip entirely, don't guess which part is safe
        if NEGATION_RE.search(sentence):
            continue  # "did not cross the DL" / "X cm below the DL" -- a did-NOT-flood narrative, not a positive
        intervals = extract_intervals(sentence, year)
        if not intervals:
            continue
        matched = match_stations(sentence)
        if not matched:
            continue
        for began, ended in intervals:
            for sid in matched:
                rows.append((sid, began, ended, (ended - began).days + 1, sentence[:300]))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.parse_args()

    all_rows: list[tuple[str, dt.date, dt.date, int, str, int]] = []  # + year
    for year in REPORT_YEARS:
        path = ensure_pdf(year)
        if path is None:
            continue
        rows = process_report(year, path)
        print(f"  {year}: {len(rows)} matched positive intervals.")
        all_rows.extend((sid, began, ended, dur, sent, year) for sid, began, ended, dur, sent in rows)

    sentences_csv = OUT_DIR / "matched_sentences.csv"
    with open(sentences_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["year", "station_id", "began", "ended", "duration_days", "sentence"])
        for sid, began, ended, dur, sent, year in all_rows:
            w.writerow([year, sid, began, ended, dur, sent])

    station_days_csv = OUT_DIR / "station_flood_days.csv"
    with open(station_days_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["station_id", "began", "ended", "severity"])
        for sid, began, ended, dur, sent, year in all_rows:
            w.writerow([sid, began, ended, dur])

    counts = Counter(r[0] for r in all_rows)
    print("\nPer-station matched-interval counts:")
    for s in STATIONS:
        print(f"  {s.station_id:6s} {s.name:35s} {counts.get(s.station_id, 0)}")

    years_covered = sorted({y for *_, y in all_rows})
    print(f"\n{len(all_rows)} total matched intervals across report years {years_covered}.")
    print(f"Wrote {sentences_csv} and {station_days_csv}")


if __name__ == "__main__":
    main()
