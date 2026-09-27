This project is a locally-built machine learning system designed to give fish farmers across Bangladesh an early warning of potential flooding in their specific area, 2 to 3 days before it happens, so they can take protective action for their ponds and stock. The system draws on Bangladesh's Flood Forecasting & Warning Centre (FFWC) network of over 100 real-time water level monitoring stations, combined with satellite-based rainfall data (such as CHIRPS and GPM) covering both local and upstream river basins, since a large share of Bangladesh's flooding originates from monsoon rainfall upstream in India and Nepal rather than from rainfall within Bangladesh itself. A machine learning model — starting with gradient-boosted decision trees and evolving toward more sophisticated time-series models as historical data accumulates — is trained to predict the probability that river water levels near a given area will exceed danger thresholds within the next 24 to 72 hours, using features like current water level trends, recent and forecasted rainfall, and upstream gauge readings that reflect the time it takes floodwater to travel downstream. These station-level predictions are then mapped to specific districts and upazilas using elevation data, so that a farmer can select their local area and see a simple, plain-language flood risk indicator (such as low, moderate, or high risk) along with the reasoning behind it, rather than raw hydrological data they'd have no way to interpret. The end goal is a practical, accessible early-warning tool — delivered through a simple website — that turns publicly available but hard-to-interpret government and satellite data into timely, localized, actionable flood risk information for a community whose livelihood is directly threatened by sudden water level changes.

## Phase 2: Operational Excellence & Pipeline Hardening (2026-08-30)

### Priority 1 — Serve the Real Model End-to-End (1–2 days)
- [ ] Confirm `backend/app/main.py` loads `FloodGBMModel` (not the synthetic `risk_model.py` placeholder) on startup
- [ ] Add model-loading health check that fails fast if artifact is missing
- [ ] Add request/response logging for every `/predict/risk` call (timestamp, features, model version, output)
- [ ] Add model version hash in API response so frontend can display "Model v2.3 (trained 2026-08-15)"

### Priority 2 — Fix Precision: Threshold Tuning + Tiered Alerts (3–5 days)
- [ ] Apply probability calibration (Platt scaling / isotonic regression) on validation set
- [ ] Implement region-specific thresholds per hydrological basin (Brahmaputra, Ganges, Meghna, CHT)
- [ ] Add cost-sensitive training to re-weight false positives during LightGBM training
- [ ] Replace binary "flood / no flood" with 3-tier system: Watch / Warning / Emergency
- [ ] Add tier cutoffs as presentation-layer config (not hardcoded in model)

### Priority 3 — Coastal Flood / Storm Surge Module (5–7 days)
- [ ] Research free coastal data sources: BMD cyclone forecasts, BIWTA tide gauges, SRTM DEM, distance-to-coast
- [ ] Build lightweight coastal flood risk module (logistic regression or Random Forest)
- [ ] Combine with riverine models via meta-classifier or weighted ensemble
- [ ] Cover coastal polder areas: Barisal, Patuakhali, Bhola, Cox's Bazar, Teknaf

### Priority 4 — Complete Live Feature Pipeline (2–3 days)
- [ ] Finish `discharge-forecaster/live_features.py` for BWDB discharge + Open-Meteo soil moisture
- [ ] Add feature freshness check in API (downgrade confidence if features > N hours old)
- [ ] Add in-process cache (TTL) for fetched features to avoid hammering upstream APIs

### Priority 5 — Uncertainty Quantification (3–4 days)
- [ ] Implement LightGBM quantile regression for prediction intervals (q10, q50, q90)
- [ ] OR: train 5–10 model ensemble with different seeds, report prediction spread
- [ ] Surface uncertainty in alert tier: "High confidence warning" vs "Low confidence, monitor closely"

### Priority 6 — Farmer Feedback Loop (ongoing)
- [ ] Design simple SMS/USSD/WhatsApp bot for farmer reports: "Flooded / Not flooded / Water level at X"
- [ ] Pipe verified reports back as training labels
- [ ] Retrain models quarterly with accumulated feedback
- [ ] Use active learning: prioritize uncertain predictions for human verification

### Priority 7 — Engineering Hardening (1–2 days)
- [ ] Add `Makefile` or `scripts/setup.sh` for one-command environment setup
- [ ] Lock CORS to Vercel domain in production, localhost in dev
- [ ] Add `pip freeze > requirements.lock` for reproducible dependencies
- [ ] Store model version hash in API response
- [ ] Add prediction audit logging

### Data Enhancement Opportunities
- [ ] Complete CHIRPS backfill (1981–present) — 26 of 46 years already on disk
- [ ] Register for Copernicus CDS (free) and pull GloFAS-ERA5 discharge (1979–present, 40+ years)
- [ ] Integrate SRTM DEM (NASA, 30m free) for elevation-based flood susceptibility
- [ ] Add SoilGrids (ISRIC, free) for soil type and drainage class features
- [ ] Pull Sentinel-1 SAR (Copernicus) for actual flood extent validation labels
- [ ] Add TerraClimate (free, 4km, 1958–present) for high-resolution precipitation and soil moisture
- [ ] Supplement rainfall with PERSIANN or GSMaP satellite precipitation
- [ ] Add ESA WorldCover (10m land cover) for runoff curve numbers
- [ ] Integrate BBS census data for population density and impact weighting
- [ ] Use OpenStreetMap for drainage network and road access mapping

### Model Architecture Improvements
- [ ] Keep LightGBM as primary (fast, handles missing data, SHAP-explaining)
- [ ] Add XGBoost + CatBoost + Logistic Regression ensemble with meta-learner
- [ ] Apply probability calibration (Platt scaling / isotonic regression) to all models
- [ ] For coastal module: Random Forest or Logistic Regression (simpler, less data required)
- [ ] Consider Temporal Fusion Transformer if data volume exceeds 100k rows
- [ ] Maintain synthetic placeholder (`risk_model.py`) as rollback reference — never delete

### Rollback Strategy
All improvements are implemented in parallel copies:
- Model code: `backend/app/models_enhanced/` (never touches `backend/app/models/`)
- Model artifacts: `backend/models_improved/` (never touches `backend/models/`)
- To revert: swap the import in `backend/app/main.py` back to the original module path