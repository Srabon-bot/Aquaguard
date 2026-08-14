"""Part 6c -- join grid_point_terrain.csv + grid_point_flood_counts.csv into
one training-ready table, and decide the flooded/non-flooded label
threshold FROM THE REAL OBSERVATION-COUNT DISTRIBUTION, not a number picked
in advance -- same discipline train_model.py's TEST_CUTOFF used ("chosen by
inspecting per-year counts").

LABELING RULE:
  - label = 1 ("flooded") if n_flooded >= 1 -- a single confirmed SAR
    detection over the whole archive is trusted (same positive-only trust
    model as every other GFM/DFO/GFD usage in this project).
  - label = 0 ("non-flooded") if n_flooded == 0 AND n_valid >=
    MIN_VALID_FOR_NEGATIVE -- requires enough independent observations
    that "never seen flooded" is real evidence, not just sparse coverage.
  - otherwise: DROPPED (insufficient data to trust either way) -- printed
    as a count, not silently discarded.

Run with --report-only first to see the real n_valid/n_flooded
distribution before picking MIN_VALID_FOR_NEGATIVE; the default below is a
placeholder until that real distribution is inspected (see
MODEL_BUILD_PLAN.md for the actual values found and the final choice made).

Usage:
    python train/build_susceptibility_dataset.py --report-only
    python train/build_susceptibility_dataset.py --min-valid-for-negative 30
"""

import argparse
import csv
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data_raw" / "susceptibility"
OUT_DIR = Path(__file__).resolve().parent.parent / "data" / "susceptibility"


def load_terrain() -> dict[str, dict]:
    rows = {}
    with (DATA_DIR / "grid_point_terrain.csv").open() as f:
        for row in csv.DictReader(f):
            rows[row["point_id"]] = row
    return rows


def load_counts() -> dict[str, dict]:
    rows = {}
    with (DATA_DIR / "grid_point_flood_counts.csv").open() as f:
        for row in csv.DictReader(f):
            rows[row["point_id"]] = row
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--min-valid-for-negative", type=int, default=30,
                         help="min n_valid observations required to trust a n_flooded==0 point as a real negative")
    parser.add_argument("--report-only", action="store_true", help="print the distribution, write nothing")
    args = parser.parse_args()

    terrain = load_terrain()
    counts = load_counts()
    print(f"{len(terrain)} terrain rows, {len(counts)} label-count rows")

    # --- distribution report, always printed (not just --report-only) ---
    n_valid_vals = sorted(int(c["n_valid"]) for c in counts.values())
    n_flooded_gt0 = sum(1 for c in counts.values() if int(c["n_flooded"]) > 0)
    n_zero_valid = sum(1 for c in counts.values() if int(c["n_valid"]) == 0)

    def pct(p):
        idx = min(len(n_valid_vals) - 1, int(len(n_valid_vals) * p))
        return n_valid_vals[idx]

    print("n_valid distribution across all points:")
    print(f"  min={n_valid_vals[0]}  p10={pct(0.10)}  p25={pct(0.25)}  median={pct(0.50)}  "
          f"p75={pct(0.75)}  p90={pct(0.90)}  max={n_valid_vals[-1]}")
    print(f"  points with n_flooded > 0: {n_flooded_gt0}/{len(counts)}")
    print(f"  points with n_valid == 0 (no coverage at all): {n_zero_valid}/{len(counts)}")

    if args.report_only:
        return

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "susceptibility_training_table.csv"
    n_pos = n_neg = n_dropped = n_missing_terrain = 0
    with out_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["point_id", "station_id", "basin", "lat", "lon",
                    "elevation_m", "slope_deg", "dist_to_river_m",
                    "drainage_density_km_per_km2", "landcover_class", "label"])
        for point_id, c in counts.items():
            t = terrain.get(point_id)
            if not t or t.get("elevation_m", "") == "":
                n_missing_terrain += 1
                continue
            n_valid, n_flooded = int(c["n_valid"]), int(c["n_flooded"])
            if n_flooded >= 1:
                label = 1
            elif n_valid >= args.min_valid_for_negative:
                label = 0
            else:
                n_dropped += 1
                continue
            n_pos += label
            n_neg += (1 - label)
            w.writerow([point_id, t["station_id"], t["basin"], t["lat"], t["lon"],
                        t["elevation_m"], t["slope_deg"], t["dist_to_river_m"],
                        t["drainage_density_km_per_km2"], t["landcover_class"], label])

    print(f"\nWrote {out_path}")
    print(f"  positive (flooded): {n_pos}")
    print(f"  negative (non-flooded, n_valid >= {args.min_valid_for_negative}): {n_neg}")
    print(f"  dropped (insufficient data): {n_dropped}")
    print(f"  dropped (missing terrain features): {n_missing_terrain}")


if __name__ == "__main__":
    main()
