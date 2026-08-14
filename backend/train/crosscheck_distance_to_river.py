"""Part 6e -- cross-checks the susceptibility model's self-derived
distance-to-river feature (pysheds flow-accumulation-based, computed per-DEM-
tile in ingest_susceptibility_terrain.py) against an INDEPENDENT method:
vector distance to the nearest reach in HydroRIVERS v1.0 (Lehner &
Grill 2013), a peer-reviewed global river network product, downloaded
directly (no registration) from data.hydrosheds.org.

WHY THIS MATTERS: the flow-routing distance-to-river was self-derived from
a single DEM via standard hydrological algorithms (fill -> flow direction
-> accumulation -> threshold), which is methodologically sound but has
never been checked against an independently-built river network. This
script is that check -- not a replacement for the existing feature, a
validation of it.

METHOD:
  1. Load HydroRIVERS' Asia shapefile, bbox-filtered to Bangladesh + margin
     (63,560 reaches -- confirmed live before trusting the full read).
  2. Reproject both the river network and the 1,470 grid points to
     EPSG:32646 (UTM 46N) for genuine metric distances -- a real projected
     CRS, not the same latitude-scaled approximation the pysheds pipeline
     used, so this is a methodologically independent measurement, not just
     a second run of the same math.
  3. Build a shapely STRtree over the river geometries for fast
     nearest-neighbor queries, compute distance from every grid point to
     its nearest reach.
  4. Compare against the existing dist_to_river_m column in
     grid_point_terrain.csv: correlation, mean/median absolute difference,
     and a scatter plot.

Usage:
    python train/crosscheck_distance_to_river.py
"""

import sys
from pathlib import Path

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from shapely import STRtree
from shapely.geometry import Point

sys.path.insert(0, str(Path(__file__).resolve().parent))
from susceptibility_grid import grid_points  # noqa: E402

HYDRORIVERS_PATH = (Path(__file__).resolve().parent.parent / "data_raw" / "hydrorivers" /
                    "extracted" / "HydroRIVERS_v10_as_shp" / "HydroRIVERS_v10_as.shp")
TERRAIN_PATH = Path(__file__).resolve().parent.parent / "data_raw" / "susceptibility" / "grid_point_terrain.csv"
OUT_DIR = Path(__file__).resolve().parent.parent / "data_raw" / "susceptibility"
BANGLADESH_BBOX = (87.5, 20.0, 93.5, 27.0)  # same as ingest_copernicus_gfm.py, with margin
UTM_CRS = "EPSG:32646"  # UTM zone 46N -- covers the great majority of Bangladesh


def main():
    print(f"Loading HydroRIVERS (bbox-filtered)...")
    rivers = gpd.read_file(HYDRORIVERS_PATH, bbox=BANGLADESH_BBOX, engine="pyogrio")
    print(f"  {len(rivers)} river reaches loaded")
    rivers_utm = rivers.to_crs(UTM_CRS)

    print("Building spatial index (STRtree)...")
    tree = STRtree(rivers_utm.geometry.values)

    points = grid_points()
    print(f"{len(points)} grid points to check")
    pts_gdf = gpd.GeoDataFrame(
        {"point_id": [p.point_id for p in points], "station_id": [p.station_id for p in points]},
        geometry=[Point(p.lon, p.lat) for p in points], crs="EPSG:4326",
    ).to_crs(UTM_CRS)

    print("Querying nearest river reach per point...")
    nearest_idx = tree.nearest(pts_gdf.geometry.values)
    dist_hydrorivers_m = pts_gdf.geometry.values.distance(rivers_utm.geometry.values[nearest_idx])

    result = pd.DataFrame({
        "point_id": pts_gdf["point_id"],
        "station_id": pts_gdf["station_id"],
        "dist_to_river_m_hydrorivers": dist_hydrorivers_m,
    })

    terrain = pd.read_csv(TERRAIN_PATH)
    merged = terrain.merge(result, on="point_id", how="inner")
    merged = merged.dropna(subset=["dist_to_river_m", "dist_to_river_m_hydrorivers"])
    print(f"\n{len(merged)} points with both distance measurements")

    diff = merged["dist_to_river_m"] - merged["dist_to_river_m_hydrorivers"]
    abs_diff = diff.abs()
    corr = merged["dist_to_river_m"].corr(merged["dist_to_river_m_hydrorivers"])
    corr_log = np.log1p(merged["dist_to_river_m"]).corr(np.log1p(merged["dist_to_river_m_hydrorivers"]))

    print(f"Pearson correlation (raw meters):      {corr:.3f}")
    print(f"Pearson correlation (log1p-transformed): {corr_log:.3f}")
    print(f"Mean absolute difference:  {abs_diff.mean():.0f} m")
    print(f"Median absolute difference: {abs_diff.median():.0f} m")
    print(f"Mean (pysheds - hydrorivers): {diff.mean():+.0f} m  (positive = pysheds reports farther)")
    print(f"pysheds dist_to_river_m:    median={merged['dist_to_river_m'].median():.0f}m, "
          f"mean={merged['dist_to_river_m'].mean():.0f}m, max={merged['dist_to_river_m'].max():.0f}m")
    print(f"HydroRIVERS dist_to_river_m: median={merged['dist_to_river_m_hydrorivers'].median():.0f}m, "
          f"mean={merged['dist_to_river_m_hydrorivers'].mean():.0f}m, max={merged['dist_to_river_m_hydrorivers'].max():.0f}m")

    merged.to_csv(OUT_DIR / "distance_to_river_crosscheck.csv", index=False)
    print(f"\nWrote {OUT_DIR / 'distance_to_river_crosscheck.csv'}")

    # --- scatter plot ---
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    ax = axes[0]
    ax.scatter(merged["dist_to_river_m_hydrorivers"], merged["dist_to_river_m"], s=10, alpha=0.4, color="#2a78d6")
    lim = max(merged["dist_to_river_m"].max(), merged["dist_to_river_m_hydrorivers"].max())
    ax.plot([0, lim], [0, lim], "k--", lw=1, alpha=0.6, label="y = x (perfect agreement)")
    ax.set_xlabel("HydroRIVERS distance-to-river (m)")
    ax.set_ylabel("pysheds (self-derived) distance-to-river (m)")
    ax.set_title(f"Raw scale (Pearson r = {corr:.2f})")
    ax.legend(fontsize=8)

    ax = axes[1]
    ax.scatter(np.log1p(merged["dist_to_river_m_hydrorivers"]), np.log1p(merged["dist_to_river_m"]),
               s=10, alpha=0.4, color="#0ca30c")
    loglim = max(np.log1p(merged["dist_to_river_m"]).max(), np.log1p(merged["dist_to_river_m_hydrorivers"]).max())
    ax.plot([0, loglim], [0, loglim], "k--", lw=1, alpha=0.6, label="y = x (perfect agreement)")
    ax.set_xlabel("log(1 + HydroRIVERS distance, m)")
    ax.set_ylabel("log(1 + pysheds distance, m)")
    ax.set_title(f"Log scale (Pearson r = {corr_log:.2f})")
    ax.legend(fontsize=8)

    fig.suptitle("Distance-to-river cross-check: self-derived (pysheds) vs. independent (HydroRIVERS)")
    fig.tight_layout()
    fig_path = Path(__file__).resolve().parent.parent.parent / "reports" / "flood-susceptibility" / "assets" / "fig_river_distance_crosscheck.png"
    fig.savefig(fig_path, dpi=150, bbox_inches="tight")
    print(f"Wrote {fig_path}")


if __name__ == "__main__":
    main()
