# Flood Susceptibility (model #3)

A standalone FastAPI service, self-contained like `flood-risk-classifier` and `discharge-forecaster`
(own `stations.py`, own trained model artifacts, own `requirements.txt`).

## What this model answers, and why it's a genuinely different question

The other two models are both **temporal**: "will this station flood in the next 24/48/72h" (the
classifier), "how much water will be flowing" (the forecaster) — both need live weather/discharge
data every call, both are honestly hard (rare-event forecasting).

This model is **spatial and static**: *how flood-prone is this ground by nature* — its elevation,
slope, distance to the nearest river, drainage density, and land cover. None of that changes day to
day, so this doesn't need live data at all — it's asking "if it floods nearby, is this exact patch of
ground the kind that goes under, or the kind that stays dry?"

## How it was built (short version — see `MODEL_BUILD_PLAN.md` for the full log)

- **1,470-point spatial grid**: a local 7x7 grid (~10km radius) around each of the 30 monitored
  stations — not a national map, deliberately scoped to what this project actually monitors.
- **Labels**: aggregated across the *entire* 2016–2026 Copernicus GFM (Sentinel-1 SAR) archive per
  point — 918,423 total observations, ~625 per point on average. A point is "flooded" if it was ever
  observed flooded across that whole archive; "non-flooded" only if observed 200+ times with zero
  detections (a deliberately strict bar for trusting a negative). 362 positive / 1,019 negative /
  89 dropped for insufficient data.
- **Features**: elevation, slope, distance-to-river, drainage density (all self-computed from
  Copernicus DEM GLO-30 via `pysheds` flow-routing — free, no registration) + land-cover class (ESA
  WorldCover, also free/no-key).
- **Model**: Random Forest, chosen over LightGBM by a real head-to-head on spatial cross-validation
  (0.892 vs 0.879 mean ROC-AUC) — matches a Bangladesh-specific finding in the literature that plain
  RF can beat gradient boosting in hilly terrain, and this grid spans both the flat delta and the
  hilly Chittagong Hill Tracts.
- **Evaluation — spatially honest, not just cross-validated**: 7 of 30 stations (stratified across
  all 4 basins, so the test set still covers flat floodplain, haor wetlands, AND hills) were held out
  completely — never touched during training or model selection. Final result on that genuinely
  unseen set: **ROC-AUC 0.903, PR-AUC 0.769**. Random-split evaluation (what a lot of published
  susceptibility papers do) is documented to inflate AUC by 5–15% on spatially autocorrelated data
  like this — this number is real, not the inflated kind.

## Why the API doesn't compute features live

Deriving slope/drainage-density for a brand-new point means loading and flow-routing a ~50MB DEM
tile (30–60 seconds) — unusable for an interactive dashboard call. Instead, every one of the 30
stations' 49-point neighborhoods was already scored once at training time
(`models/per_station_susceptibility.csv`); this service just looks up (or nearest-station-snaps for
an arbitrary lat/lon) into that table. `rasterio`/`pysheds`/`scikit-learn` are **not** runtime
dependencies of this package — only `backend/train/` needs them, to build the table in the first
place. That's also why `requirements.txt` here is much shorter than the other two packages'.

The full trained model (`models/susceptibility_random_forest.joblib`) is included for reference/
offline re-scoring of new points, but the live API doesn't load or use it directly.

## Running it

```
cd packages/flood-susceptibility
uvicorn main:app --port 8002
```

Then `GET /predict?station_id=SW267` or `GET /predict?lat=..&lon=..`. See `/docs` for interactive
API docs.

## Combining with the other two models

Recommended combination (see `MODEL_BUILD_PLAN.md` Part 6f): `combined_risk = classifier_probability
x (0.5 + 0.5 x susceptibility_score)` — susceptibility acts as a bounded modulator (never fully zeroes
out the temporal signal, since a genuinely extreme storm can still flood low-susceptibility ground) on
top of the classifier's own time-bound probability, rather than a black-box meta-model. One formula,
one slide, defensible in thirty seconds — see the frontend's model section for where this is surfaced.
