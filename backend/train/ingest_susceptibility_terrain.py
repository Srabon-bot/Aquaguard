"""Part 6b -- terrain + land-cover conditioning factors for the 1,470-point
susceptibility grid (susceptibility_grid.py), sourced entirely from free,
unauthenticated data:

  - Elevation, slope, distance-to-river, drainage density: derived from
    Copernicus DEM GLO-30 (ESA/Airbus, hosted unauthenticated on AWS Open
    Data -- verified directly with a real HEAD request before writing this,
    not assumed: 1-degree COG tiles named
    Copernicus_DSM_COG_10_N{lat:02d}_00_E{lon:03d}_00_DEM.tif, Accept-Ranges:
    bytes confirmed). NOT a replacement for STATIC_TERRAIN's MERIT-Hydro
    elevation_m/hand_m in stations.py (that's a peer-reviewed, purpose-built
    HAND product used by the temporal classifier -- see DECISIONS.md
    SS17/18) -- this is a SEPARATE, self-computed set of features for the
    susceptibility model specifically, needed because MERIT Hydro's own
    values only exist at the 30 station points (a one-time manual Earth
    Engine pull), not the ~1,470-point spatial grid a susceptibility model
    needs. Slope/distance-to-river/drainage-density are computed from ONE
    consistent DEM source per tile (never mixing two products' native
    resolutions) via pysheds' flow-routing -- the specific resampling
    mismatch DECISIONS.md SS17/18 warned about was about mixing DIFFERENT
    products' grids, not about self-computing from one internally-consistent
    source, so that concern doesn't transfer here. Chosen over richdem
    (needs a C++ compiler this machine doesn't have -- confirmed by a real
    failed `pip install`) -- pysheds is pure-Python/numba, installs cleanly.

  - Land cover: ESA WorldCover 10m v200 (2021), also unauthenticated on AWS
    (verified: real HEAD requests against 5 candidate 3-degree tile names
    covering Bangladesh all returned 200). 11 discrete classes (10=tree,
    20=shrub, 30=grassland, 40=cropland, 50=built-up, 60=bare/sparse,
    70=snow/ice, 80=water, 90=wetland, 95=mangrove, 100=moss/lichen) -- kept
    as the raw integer class, one-hot/target-encoded at training time (Part
    6d), not here.

METHOD (per DEM tile, not per point -- Bangladesh's ~30 station
neighborhoods only span a handful of 1-degree tiles, so processing per tile
once and sampling every grid point that falls inside it is far cheaper than
re-deriving flow-routing per point):
  1. Load the whole 1-degree tile (pysheds `Grid.from_raster`/`read_raster`
     directly against the remote HTTPS COG -- no local download, same
     approach ingest_copernicus_gfm.py already uses for GFM).
  2. Condition it (fill_pits -> fill_depressions -> resolve_flats) -- the
     standard hydrological DEM-conditioning sequence, required before flow
     routing is meaningful (otherwise spurious pits break flow paths).
  3. Compute flow direction (D8) and flow accumulation.
  4. Slope: numpy gradient on the raw (unconditioned) elevation, scaled from
     degree cell-size to meters using a local cos(latitude) correction for
     longitude -- confirmed necessary and correct via a real test at this
     tile's latitude before trusting it in this script (28.1m x 30.9m
     effective cell size at ~24-25N, not square despite a "30m" nominal
     resolution).
  5. "River" cells: flow accumulation > RIVER_ACC_THRESHOLD (500 cells,
     ~0.45 sq km contributing area -- a standard minimum stream-initiation
     threshold in flat terrain per the flood-susceptibility literature).
  6. Distance-to-river: Euclidean distance transform (scipy) from every
     cell to the nearest river cell, in the same meter-scaled units as
     slope.
  7. Drainage density: river-cell count within a fixed-radius local window
     (DRAINAGE_WINDOW_M) around each grid point, divided by that window's
     area -- km of (approximated, one-cell-per-~30m) stream per sq km.

VERIFIED before trusting this script: the full per-tile pipeline (load,
condition, flowdir, accumulation, slope, distance-to-river) was run
interactively against a real Bangladesh tile (N24E090) first -- sane
elevation range (-8.5m to 49.8m, plausible for a coastal/deltaic tile),
sane slope (mean 2.6 degrees, matching "Bangladesh is flat" expectations),
sane distance-to-river (max ~1.6km within a 111km tile, ~3% of cells
classified as river). See MODEL_BUILD_PLAN.md for the full verification log.

Usage:
    python train/ingest_susceptibility_terrain.py
    python train/ingest_susceptibility_terrain.py --limit-stations SW90,SW93   # smoke test
"""

import argparse
import csv
import math
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

os.environ.setdefault("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
os.environ.setdefault("VSI_CACHE", "TRUE")
os.environ.setdefault("GDAL_HTTP_VERSION", "2")
os.environ.setdefault("CPL_VSIL_CURL_USE_HEAD", "NO")

import numpy as np
import rasterio
from pysheds.grid import Grid
from scipy.ndimage import distance_transform_edt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from susceptibility_grid import GridPoint, grid_points  # noqa: E402

OUT_DIR = Path(__file__).resolve().parent.parent / "data_raw" / "susceptibility"
DEM_URL_TMPL = (
    "https://copernicus-dem-30m.s3.amazonaws.com/"
    "Copernicus_DSM_COG_10_N{lat:02d}_00_E{lon:03d}_00_DEM/"
    "Copernicus_DSM_COG_10_N{lat:02d}_00_E{lon:03d}_00_DEM.tif"
)
WORLDCOVER_URL_TMPL = (
    "https://esa-worldcover.s3.eu-central-1.amazonaws.com/"
    "v200/2021/map/ESA_WorldCover_10m_2021_v200_N{lat:02d}E{lon:03d}_Map.tif"
)
DEM_NODATA = -32768
RIVER_ACC_THRESHOLD = 500  # cells (~0.45 sq km contributing area) -- see module docstring
DRAINAGE_WINDOW_M = 1000  # radius for the local drainage-density window
DEG_TO_M_LAT = 111320.0


def dem_tile_id(lat: float, lon: float) -> tuple[int, int]:
    """SW-corner integer (lat, lon) of the 1-degree DEM tile containing this
    point -- matches Copernicus DEM's own naming (floor, not round)."""
    return math.floor(lat), math.floor(lon)


def worldcover_tile_id(lat: float, lon: float) -> tuple[int, int]:
    """SW-corner of the 3-degree WorldCover tile, floored to a multiple of
    3 -- confirmed against real tile names (N21E087, N21E090, N24E087,
    N24E090, N24E093 all real) before trusting this formula."""
    return (math.floor(lat / 3) * 3, math.floor(lon / 3) * 3)


def process_dem_tile(tile_lat: int, tile_lon: int, points: list[GridPoint]) -> dict[str, dict]:
    """Load + condition one 1-degree DEM tile, derive slope/distance-to-
    river/drainage-density, and sample every grid point that falls inside
    it. Returns {point_id: {elevation_m, slope_deg, dist_to_river_m,
    drainage_density_km_per_km2}}."""
    url = DEM_URL_TMPL.format(lat=tile_lat, lon=tile_lon)
    t0 = time.time()
    try:
        grid = Grid.from_raster(url, nodata=DEM_NODATA)
        dem = grid.read_raster(url, nodata=DEM_NODATA)
    except Exception as exc:  # noqa: BLE001 -- a missing/unreachable tile shouldn't kill the run
        print(f"  WARNING: could not load DEM tile N{tile_lat:02d}E{tile_lon:03d}: {exc}")
        return {}

    pit_filled = grid.fill_pits(dem)
    flooded = grid.fill_depressions(pit_filled)
    inflated = grid.resolve_flats(flooded)
    fdir = grid.flowdir(inflated)
    acc = grid.accumulation(fdir)

    a, e, c, f = grid.affine.a, grid.affine.e, grid.affine.c, grid.affine.f
    nrows, ncols = dem.shape
    lat_mean = f + e * (nrows / 2)
    deg_to_m_lon = DEG_TO_M_LAT * math.cos(math.radians(lat_mean))
    cellsize_m_x = abs(a) * deg_to_m_lon
    cellsize_m_y = abs(e) * DEG_TO_M_LAT

    dem_arr = np.asarray(dem, dtype=np.float32)
    gy, gx = np.gradient(dem_arr, cellsize_m_y, cellsize_m_x)
    slope_deg = np.degrees(np.arctan(np.sqrt(gx**2 + gy**2)))

    river_mask = np.asarray(acc) > RIVER_ACC_THRESHOLD
    dist_to_river_m = distance_transform_edt(~river_mask, sampling=(cellsize_m_y, cellsize_m_x))

    win_rows = max(1, int(round(DRAINAGE_WINDOW_M / cellsize_m_y)))
    win_cols = max(1, int(round(DRAINAGE_WINDOW_M / cellsize_m_x)))
    window_area_km2 = (2 * win_rows * cellsize_m_y / 1000) * (2 * win_cols * cellsize_m_x / 1000)
    cell_len_km = cellsize_m_x / 1000  # approx river length per river cell

    results = {}
    for p in points:
        col = int(round((p.lon - c) / a))
        row = int(round((p.lat - f) / e))
        if not (0 <= row < nrows and 0 <= col < ncols):
            continue
        r0, r1 = max(0, row - win_rows), min(nrows, row + win_rows + 1)
        c0, c1 = max(0, col - win_cols), min(ncols, col + win_cols + 1)
        river_cells_nearby = int(river_mask[r0:r1, c0:c1].sum())
        drainage_density = (river_cells_nearby * cell_len_km) / window_area_km2

        elev = float(dem_arr[row, col])
        results[p.point_id] = {
            "elevation_m": elev if elev != DEM_NODATA else float("nan"),
            "slope_deg": float(slope_deg[row, col]),
            "dist_to_river_m": float(dist_to_river_m[row, col]),
            "drainage_density_km_per_km2": drainage_density,
        }

    print(f"  DEM tile N{tile_lat:02d}E{tile_lon:03d}: {len(results)}/{len(points)} points sampled in {time.time()-t0:.1f}s")
    return results


def process_worldcover_tile(tile_lat: int, tile_lon: int, points: list[GridPoint]) -> dict[str, int]:
    """Point-sample (not full-tile-process) land cover -- categorical, no
    flow-routing needed, so a plain windowed rasterio point read is enough
    (same pattern ingest_copernicus_gfm.py uses for GFM)."""
    url = WORLDCOVER_URL_TMPL.format(lat=tile_lat, lon=tile_lon)
    results = {}
    try:
        with rasterio.open(url) as src:
            for p in points:
                row, col = src.index(p.lon, p.lat)
                if not (0 <= row < src.height and 0 <= col < src.width):
                    continue
                val = list(src.sample([(p.lon, p.lat)]))[0][0]
                results[p.point_id] = int(val)
    except Exception as exc:  # noqa: BLE001
        print(f"  WARNING: could not load WorldCover tile N{tile_lat:02d}E{tile_lon:03d}: {exc}")
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--limit-stations", default=None, help="comma-separated station IDs, for a fast smoke test")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    points = grid_points()
    if args.limit_stations:
        wanted = set(args.limit_stations.split(","))
        points = [p for p in points if p.station_id in wanted]
    print(f"{len(points)} grid points to process")

    dem_groups: dict[tuple[int, int], list[GridPoint]] = defaultdict(list)
    wc_groups: dict[tuple[int, int], list[GridPoint]] = defaultdict(list)
    for p in points:
        dem_groups[dem_tile_id(p.lat, p.lon)].append(p)
        wc_groups[worldcover_tile_id(p.lat, p.lon)].append(p)
    print(f"{len(dem_groups)} DEM tiles, {len(wc_groups)} WorldCover tiles needed")

    terrain: dict[str, dict] = {}
    print("Processing DEM tiles (elevation/slope/distance-to-river/drainage-density)...")
    for i, ((tlat, tlon), pts) in enumerate(sorted(dem_groups.items()), 1):
        print(f"[{i}/{len(dem_groups)}]", end=" ")
        terrain.update(process_dem_tile(tlat, tlon, pts))

    landcover: dict[str, int] = {}
    print("Processing WorldCover tiles (land cover class)...")
    for i, ((tlat, tlon), pts) in enumerate(sorted(wc_groups.items()), 1):
        print(f"[{i}/{len(wc_groups)}] WorldCover tile N{tlat:02d}E{tlon:03d}...", end=" ")
        result = process_worldcover_tile(tlat, tlon, pts)
        landcover.update(result)
        print(f"{len(result)}/{len(pts)} sampled")

    out_path = OUT_DIR / "grid_point_terrain.csv"
    with out_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["point_id", "station_id", "basin", "lat", "lon",
                    "elevation_m", "slope_deg", "dist_to_river_m",
                    "drainage_density_km_per_km2", "landcover_class"])
        n_complete = 0
        for p in points:
            t = terrain.get(p.point_id, {})
            lc = landcover.get(p.point_id)
            row = [p.point_id, p.station_id, p.basin, p.lat, p.lon,
                   t.get("elevation_m", ""), t.get("slope_deg", ""),
                   t.get("dist_to_river_m", ""), t.get("drainage_density_km_per_km2", ""),
                   lc if lc is not None else ""]
            if t and lc is not None:
                n_complete += 1
            w.writerow(row)
    print(f"Wrote {out_path} ({n_complete}/{len(points)} points with complete terrain+landcover data)")


if __name__ == "__main__":
    main()
