"""Spatial sample grid for the flood SUSCEPTIBILITY model (model #3 -- see
MODEL_BUILD_PLAN.md "Part 6"). Distinct concern from stations.py's
UPSTREAM_BOXES: those cover upstream catchments OUTSIDE Bangladesh for
rainfall/discharge lag features on the temporal classifier; this covers a
local neighborhood AROUND each of the 30 in-Bangladesh stations, because
susceptibility is a spatial-classification problem ("how flood-prone is
this exact patch of ground") that needs many points with real spatial
variance -- 30 constant per-station values (STATIC_TERRAIN) aren't enough
to train a spatial model, only enough to feature-enrich the temporal one.

WHY A LOCAL GRID PER STATION, NOT A UNIFORM GRID OVER ALL OF BANGLADESH:
this project's actual use case is scoring the 30 monitored stations'
surroundings, not producing a national susceptibility atlas -- a local grid
directly serves that (each station ends up with real spatial context to
average/interpolate a susceptibility score from) without the much larger
labeling effort a full-country grid would need. Defensible scope, not
laziness: see MODEL_BUILD_PLAN.md for the explicit reasoning.

GRID SIZE -- 7x7 = 49 points per station, spanning +/-0.09 degrees
(~10km) in each direction from the station coordinate, so each grid cell
is ~1.65km apart (5 gaps across a ~19.8km box). Chosen to:
  - stay well inside a single GFM Equi7Grid tile / Copernicus DEM tile per
    station (no cross-tile stitching complexity)
  - give real spatial variance (riverbank vs. a few km inland) rather than
    points so close together they're all "the same place" to a 30m-90m DEM
  - land in the middle of the literature's reported inventory sizes
    (200-12,000 points; see MODEL_BUILD_PLAN.md research log) once all 30
    stations are combined: 30 * 49 = 1,470 points before any are dropped
    for missing data/nodata coverage.

Usage:
    from susceptibility_grid import grid_points
    points = grid_points()  # list[GridPoint], 1,470 rows before filtering
"""

from dataclasses import dataclass

from stations import STATIONS

GRID_N = 7  # per side -- see module docstring
HALF_SPAN_DEG = 0.09  # ~10km at Bangladesh's latitude


@dataclass(frozen=True)
class GridPoint:
    station_id: str  # which station's neighborhood this point belongs to
    basin: str
    grid_i: int  # 0..GRID_N-1, row index within this station's local grid
    grid_j: int  # 0..GRID_N-1, column index
    lat: float
    lon: float

    @property
    def point_id(self) -> str:
        return f"{self.station_id}_{self.grid_i}_{self.grid_j}"


def grid_points() -> list[GridPoint]:
    """One local GRID_N x GRID_N grid per station, centered on that
    station's own (lat, lon). Deterministic order (station list order, then
    row-major within each station) so re-running produces byte-identical
    output -- important for the resumable ingestion scripts built on top of
    this (see ingest_susceptibility_features.py)."""
    points: list[GridPoint] = []
    step = (2 * HALF_SPAN_DEG) / (GRID_N - 1)
    for s in STATIONS:
        for i in range(GRID_N):
            lat = s.lat - HALF_SPAN_DEG + i * step
            for j in range(GRID_N):
                lon = s.lon - HALF_SPAN_DEG + j * step
                points.append(GridPoint(
                    station_id=s.station_id, basin=s.basin,
                    grid_i=i, grid_j=j, lat=round(lat, 6), lon=round(lon, 6),
                ))
    return points


if __name__ == "__main__":
    pts = grid_points()
    print(f"{len(pts)} grid points across {len(STATIONS)} stations ({GRID_N}x{GRID_N} each)")
    print("first 3:", pts[:3])
    print("last 3:", pts[-3:])
