"""Cross-validate GFMS's modeled flood label (Flood_byStor) against MCDWD's
satellite-observed flood label (Flood_3Day_250m) over their shared date
range (the `gfms-overlap` scope: 2013-2016 partial + 2021-2025, monsoon
months Jun-Sep, 976 days) -- this is the whole reason that scope exists per
MODEL_BUILD_PLAN.md Part 1.

GFMS positive  = flood_byStor is non-null (any value above its internal
                 threshold; NoData/non-flood days are blank in our CSVs)
MCDWD read     = Flood_3Day_250m in {0,1,2,3} (i.e. not 255 = cloud/no-data)
MCDWD positive = Flood_3Day_250m == 3 (flood, unusual)

Only compared on days where MCDWD actually got a clear read -- comparing
against MCDWD's cloud days would just be comparing GFMS against noise.
"""

import csv
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data_raw"
STATIONS = ["SW90", "SW93", "SW99", "SW17", "SW267", "SW174"]
STATION_NAMES = {
    "SW90": "Bahadurabad (Jamuna)",
    "SW93": "Sariakandi (Jamuna)",
    "SW99": "Sirajganj (Jamuna)",
    "SW17": "Chilmari (Brahmaputra)",
    "SW267": "Sunamganj (Surma)",
    "SW174": "Sylhet (Surma)",
}


def load_gfms(station: str) -> dict[str, bool]:
    path = DATA_DIR / "gfms" / f"gfms_{station}.csv"
    out = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            out[row["date"]] = bool(row["flood_byStor"].strip())
    return out


def load_mcdwd(station: str) -> dict[str, int | None]:
    path = DATA_DIR / "mcdwd" / f"mcdwd_{station}.csv"
    out = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            val = row["Flood_3Day_250m"].strip()
            out[row["date"]] = int(val) if val else None
    return out


def main():
    print(f"{'station':22} {'clear-sky days':>14} {'agree':>8} {'gfms+/mcdwd-':>14} {'gfms-/mcdwd+':>14} {'agreement%':>11}")
    totals = {"clear": 0, "agree": 0, "gfms_only": 0, "mcdwd_only": 0, "both_pos": 0, "both_neg": 0}

    for station in STATIONS:
        gfms = load_gfms(station)
        mcdwd = load_mcdwd(station)
        dates = sorted(set(gfms) & set(mcdwd))

        clear = agree = gfms_only = mcdwd_only = both_pos = both_neg = 0
        for d in dates:
            m = mcdwd[d]
            if m is None or m == 255:
                continue  # cloud/no-data, can't compare
            clear += 1
            g_pos = gfms[d]
            m_pos = m == 3
            if g_pos and m_pos:
                agree += 1
                both_pos += 1
            elif not g_pos and not m_pos:
                agree += 1
                both_neg += 1
            elif g_pos and not m_pos:
                gfms_only += 1
            else:
                mcdwd_only += 1

        pct = 100 * agree / clear if clear else float("nan")
        print(f"{STATION_NAMES[station]:22} {clear:>14} {agree:>8} {gfms_only:>14} {mcdwd_only:>14} {pct:>10.1f}%")
        for k, v in [("clear", clear), ("agree", agree), ("gfms_only", gfms_only),
                     ("mcdwd_only", mcdwd_only), ("both_pos", both_pos), ("both_neg", both_neg)]:
            totals[k] += v

    print("-" * 90)
    pct = 100 * totals["agree"] / totals["clear"] if totals["clear"] else float("nan")
    print(f"{'TOTAL':22} {totals['clear']:>14} {totals['agree']:>8} {totals['gfms_only']:>14} {totals['mcdwd_only']:>14} {pct:>10.1f}%")
    print()
    print(f"Of {totals['clear']} clear-sky comparable station-days:")
    print(f"  both say flood:     {totals['both_pos']}")
    print(f"  both say no-flood:  {totals['both_neg']}")
    print(f"  GFMS flood only:    {totals['gfms_only']}  (GFMS positive, MCDWD says no/clear)")
    print(f"  MCDWD flood only:   {totals['mcdwd_only']}  (MCDWD positive, GFMS says no)")
    base_rate_gfms = 100 * (totals['both_pos'] + totals['gfms_only']) / totals['clear']
    base_rate_mcdwd = 100 * (totals['both_pos'] + totals['mcdwd_only']) / totals['clear']
    print(f"  GFMS positive rate:  {base_rate_gfms:.2f}%")
    print(f"  MCDWD positive rate: {base_rate_mcdwd:.2f}%")


if __name__ == "__main__":
    main()
