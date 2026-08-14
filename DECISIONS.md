# Design Decisions & Limitations Log

This file is the curated record of every significant decision made while building this project, why it
was made, what alternatives were considered, and what limitations/caveats it leaves behind. It exists
separately from `MODEL_BUILD_PLAN.md` (the raw, chronological working log used to resume work session to
session) — this file is meant to be read start to finish by someone who wasn't in the room, e.g. for a
pre-defence walkthrough with a supervisor. Update it whenever a decision of real consequence gets made,
not for routine implementation details (those belong in the plan file's progress log).

Each entry: **what was decided**, **why**, **alternatives considered**, **limitations this leaves**.

---

## 1. Overall approach

**Decision**: Train a model on free, publicly-available satellite/reanalysis data standing in for real
river-gauge history, rather than real Bangladesh Water Development Board (BWDB) gauge records.

**Why**: Real historical water-level/discharge time series from BWDB Hydrology requires a paid, manual
"Online Data Request" process. The project is scoped free-tools-only.

**Alternatives considered**: Paying for the BWDB data request (rejected — out of budget/scope); scraping
BWDB's public "Data View" pages (investigated and rejected — those pages only serve a fixed 1985 demo
sample, not real queryable history, confirmed by testing every plausible query parameter).

**Limitation**: The model never sees a real physical gauge reading during training. Every "station" in
this project is a **virtual station** — a fixed lat/lon where we query satellite/model-derived data
instead. This is a standard technique for basins without open gauge networks, but it means training
signal quality is bounded by how well GFMS/GloFAS/ERA5 represent real conditions at that point, not by
true ground-truth measurement.

---

## 2. Historical rainfall + soil moisture source: CHIRPS → Open-Meteo Historical Weather API

**Decision**: Use Open-Meteo's Historical Weather API (ERA5/ERA5-Land reanalysis) as the primary source
for historical rainfall and soil moisture, not CHIRPS.

**Why**: CHIRPS (originally chosen, `data.chc.ucsb.edu`) got the project's IP banned by the host's
CrowdSec WAF after a duplicate-process incident, with no ETA on recovery. Independently of that, Open-Meteo
turned out to be strictly better for this project: same free/no-key/no-registration trust profile as the
discharge API already in use, longer history (1950 vs. CHIRPS's 1981), point-based JSON instead of
multi-gigabyte gridded netCDF files, and — the deciding factor — it also serves **soil moisture** on the
same endpoint, which CHIRPS never had.

**Alternatives considered**: Waiting out the CHIRPS ban (open-ended, no guarantee it lifts); NASA GPM
IMERG (more engineering overhead, similar resolution, no soil moisture); switching only after the ban,
i.e. treating it as a forced fallback rather than evaluating on merits — instead this was evaluated and
chosen as the better option on its own terms, the ban was just what triggered looking.

**Limitation**: ERA5-Land reanalysis is itself a *model output*, not a direct rain-gauge measurement —
it's a well-validated global product but still one more layer removed from ground truth than a real rain
gauge network would be. CHIRPS's ~26 of 46 years already downloaded were left on disk, unused, as an idle
cross-check, not deleted.

---

## 3. Adding soil moisture as a feature

**Decision**: Add `soil_moisture_local` (0-7cm depth, m³/m³, from ERA5-Land) as a real training feature,
not previously part of the plan.

**Why**: Confirmed via a literature search of recent (2024-2025) published Bangladesh-specific flood-ML
research that antecedent soil wetness is a commonly-cited top flood driver — the same rainfall produces
very different runoff depending on whether the ground is already saturated. It was free to add (same API
call already needed for rainfall) and directly useful.

**Depth choice (0-7cm)**: Deliberately the shallowest available layer, not because it's hydrologically
"best" in isolation, but because it's what a shallow-buried IoT soil probe (the user's planned hardware,
see §8) would actually measure — keeping the trained feature and the eventual live sensor reading at the
same depth/units matters more than optimizing depth alone, since a mismatch there would silently corrupt
the feature at inference time.

**Limitation**: Soil moisture at a single 0.1° reanalysis grid cell (~11km) may not represent a specific
pond's actual local soil conditions well — this is exactly the gap the IoT sensor is meant to close later.

---

## 4. Discharge source: Open-Meteo Flood API (GloFAS v4), not raw GloFAS-CDS or GFMS binaries

**Decision**: Use `flood-api.open-meteo.com` (Open-Meteo's wrapper around GloFAS v4 reanalysis + forecast)
for river discharge, both historical training data and live inference.

**Why**: Free, no key, one JSON endpoint serves both historical date-range queries and live
`past_days`/`forecast_days` queries — one integration covers both training and live-serving. Verified
working back to ~1997-98 (the 1998 mega-flood is present in the data).

**Alternatives considered**: Registering for Copernicus CDS/EWDS and pulling raw GloFAS-ERA5 (more setup,
a registration step, and yet another data format to parse); parsing NASA GFMS's raw `Q` (streamflow)
binary grids (investigated — found the bulk-download archive doesn't actually serve `Q`/`Routed`/`V`
despite the documentation listing them, only `Flood_byStor`, so this path was dropped, not chosen against
on merits).

**Limitation / bug found and fixed**: GloFAS is a coarse (~0.05°) grid. A gauge's real public coordinates
can land on the wrong grid cell — a braid channel or minor tributary near a confluence instead of the main
channel — giving implausibly tiny discharge. Caught for 2 of the original 6 stations (SW93, SW174) by
comparing magnitudes against same-river neighbors, fixed with a small grid-search tool
(`snap_discharge_grid.py`) that finds the nearby cell with the highest mean discharge (the assumption
being the true main channel carries far more flow than an adjacent cell). **A related implementation bug
was found later**: the override dictionary this tool produced was never actually wired into the fetch
call, so the "fixed" coordinates silently weren't being used at all until caught during the 25→30 station
expansion. Re-verified against the actual downloaded data (not just re-reading the code) before trusting
it fixed.

---

## 5. Flood label source: NASA GFMS `Flood_byStor`, not NASA MCDWD, despite them barely agreeing

**Decision**: Use GFMS's `Flood_byStor` (a hydrological-model-derived flood-intensity-above-threshold
signal) as the primary positive/negative training label, with MCDWD (MODIS/VIIRS satellite-observed
surface water) kept only as a documented cross-check, not a load-bearing input.

**Why**: This required real investigation, not just picking the more "modern" source. Cross-validating
the two over their shared date window found:
- Raw same-day agreement looked good (96.4%) but was almost entirely a base-rate artifact — both sources
  say "no flood" on >95% of days, so agreeing on negatives dominates the number.
- **Zero days where both sources called a flood on the exact same date.** Even with a generous ±5-day
  tolerance, only ~1.2% of GFMS-positive days had any MCDWD corroboration; 35% were actively contradicted
  by a clear-sky MCDWD read; 64% had no clear satellite look nearby at all (cloud cover — expected, since
  clouds and rain go together).
- This alone would be reason to distrust GFMS. Instead of stopping there, checked GFMS-positive days
  against real, independent discharge data (Open-Meteo, unrelated to either flood-label source): **at
  every single station, median discharge on GFMS-positive days sat at or above the overall 90th
  percentile** — strong independent evidence GFMS is tracking real elevated-water events, not noise.
- Combined with the project's explicit early-warning framing (predict 24-72h *ahead*), it's plausible
  GFMS's storage/discharge-threshold signal fires while water is rising but before it's visible as areal
  inundation at MCDWD's specific pixel — i.e. it may capture exactly the pre-overbank "elevated risk"
  state the model is meant to predict, while MCDWD only confirms a flood already underway and visible.

**Alternatives considered**: MCDWD as primary (rejected — its missingness is worst exactly during active
storms, i.e. not random, so it would systematically fail to label the biggest events); requiring both
sources to agree (rejected — given near-zero overlap, this would leave almost no positive labels at all).

**Limitation**: The label itself is a modeled quantity, not directly observed. This cross-validation and
its resolution needs to be disclosed plainly in any defence, not glossed over — it's a genuine, reasoned
judgment call under real uncertainty, not a clean ground-truth label.

---

## 6. GFMS's usable history is much narrower than its nominal archive

**Decision/finding**: Treat GFMS's real usable labeled-training window as **2013-2016 (partial) +
2021-present** (~8-9 years), not the full nominal 2001-2025 archive.

**Why**: The archive is *listed* as fully populated 2001-2025, but systematically probing one file per
month across the whole range found most of 2001-2012 and April 2016-2020 return `403 Forbidden` on actual
file download despite being listed — a permanent, server-side restriction (not rate-limiting), most likely
an archive reorganization that broke access without updating the directory index. Not fixable from this
end.

**Limitation**: Earlier major flood years (1998, 2004, 2007) that the original plan hoped to validate
against have no GFMS label coverage at all. Rainfall/discharge features can still be computed for those
years (both sources go back further), just without a reliable label — usable for the live-feature
pipeline, not for supervised training on those specific years.

---

## 7. Station count and placement: 6 → 25 → 30

**Decision**: Expanded from the original 6 stations (4 on the Jamuna/Brahmaputra, 2 on the Surma) to 25,
then to 30 with 5 southern coastal additions.

**Why**: The original 6 were a starter subset with zero representation of the Ganges/Padma system, the
Teesta, the lower Meghna (which is what actually determines Dhaka's flood risk), the Chittagong Hill
Tracts, or the southern coastal belt. Asked directly "how many stations for full coverage" and answered
with two benchmarks: FFWC itself runs ~90-100+ real gauges (54 with official danger levels) — the
real-world gold standard — but for a satellite/reanalysis-grid-based *virtual*-station approach, going
that dense has diminishing returns (nearby points on a coarse model grid don't add much unique signal the
way independent physical gauges would). 25 was chosen as a practical target touching every major river
system; a later research pass (see §9) confirmed a 4th flood mechanism (storm surge) with zero
representation, motivating the further expansion to 30.

**Coverage by basin** (see `backend/train/stations.py` for exact coordinates):
- Jamuna/Brahmaputra mainstem: 4 original + Teesta (2) + Old Brahmaputra (1) + Dharla (1) = 8
- Ganges/Padma mainstem + Gorai-Madhumati distributaries: 6 (previously 0)
- Lower Meghna / Padma-Meghna confluence (covers Dhaka): 3 (previously 0 — this is what motivated the
  whole expansion: a user question "which station represents Dhaka" had no good answer with only 6)
- Surma-Kushiyara / northeast haor basin: 2 original + 3 new = 5
- Chittagong Hill Tracts (Karnaphuli/Sangu/Halda): 3 (previously 0)
- Southern coastal belt (Barisal/Khulna/Bagerhat/Patuakhali/Cox's Bazar): 5 (previously 0)

**Limitation**: Station coordinates are real-town/known-confluence approximations verified for general
plausibility (grid-search-corrected where discharge magnitude flagged an obvious problem), not surveyed
against an official gauge-location list. Upstream catchment boxes (used to compute area-mean upstream
rainfall per basin) are coarse, hand-picked rectangles grouped by river system, not precise watershed
delineations — a deliberate, documented approximation, refined only as far as Part 3's travel-time-lag
features go.

**Sub-decision: when to trust the discharge-coordinate auto-correction tool, and when not to.**
`snap_discharge_grid.py` grid-searches nearby GloFAS cells and suggests whichever has the highest mean
discharge, on the assumption a real river channel carries far more flow than an adjacent cell. This
assumption breaks down for a small tributary that joins a much bigger river close to the station — the
tool can walk the point onto the *parent* river's channel instead of finding the tributary's own (smaller)
flow. Caught this for 3 of the 24 new stations (`DH01` Dharla, `GO01` Gorai, `ME03` Dhaka/Buriganga) —
each suggested "best" cell matched a neighboring mainstem river's magnitude almost exactly. Deliberately
**rejected** those three suggestions and kept the original (smaller, possibly imperfect) coordinates
instead — most consequential for `ME03`, since that station exists specifically to represent Dhaka's own
local hydrology; accepting the tool's suggestion would have silently made it just another proxy for the
Padma/Dhaleshwari mainstem, defeating the reason the station was added. This is a real, disclosed judgment
call, not a fully-solved problem — those 3 stations' discharge feature should be treated as lower-confidence
than the rest until manually verified against an actual river map.

**Sub-decision: a real implementation bug was caught and fixed during this expansion.** While extending
`ingest_discharge.py`, discovered that the coordinate-override mechanism found earlier for the original 6
stations' off-channel coordinates (`GLOFAS_COORD_OVERRIDE`) had been correctly identified but **never
actually applied** — `fetch_discharge()` was still using the raw, uncorrected coordinates the whole time,
confirmed by checking the already-downloaded data on disk (`discharge_SW93.csv` still read the known-broken
~1.7 m³/s, not the ~21,852 the fix was supposed to produce). This means the discharge data for those 2
stations was silently wrong from whenever the "fix" was first believed to be in place until this was
caught — worth noting as an example of why "the fix is written" isn't the same as "the fix took effect,"
and why re-verifying against the actual output, not just the code, matters.

---

## 8. Live-serving architecture ("middle system") and the IoT soil sensor fallback chain

**Decision**: The deployed system's shape is: website (shows live IoT pond-sensor data + a live weather
panel + a manual "check flood risk" button) → a middle backend service (already exists as
`app/main.py`'s `/predict/risk` endpoint) → live data gathered from the internet for the requested
location → trained model → plain-language result back to the site. For soil moisture specifically, the
serving-time value should prefer a live reading from the user's own IoT probe when connected, falling back
to Open-Meteo's live estimate otherwise — both defined at the same depth/units as the training feature
(§3), so there's one consistent feature definition end to end.

**Why**: This was the user's own stated target architecture, described after the model/data pipeline was
already largely built — it turned out to already match what existed (`/predict/risk` already does
"location in, live-fetch, model, plain-language answer out"), so no redesign was needed, just filling in
the remaining live-fetch pieces (discharge, soil moisture — rainfall was already done).

**Limitation**: The IoT device and its data-ingestion protocol don't exist yet at time of writing — this
is documented as a design contract to build toward, not implemented. Whatever the sensor natively reports
(often a raw resistance/capacitance/percentage) will need normalizing to volumetric water content (m³/m³)
before use — a naive unit mismatch here would silently corrupt this feature, worth calibration-checking
against known wet/dry references rather than trusting a datasheet.

---

## 9. Deliberately out of scope: storm surge / cyclone-driven coastal flooding

**Finding**: Research into Bangladesh's flood typology confirmed 4 distinct mechanisms — monsoon river
flood, flash flood, local rainfall flood, and storm surge flood (cyclone/tidal-driven). Only the first
three are addressed by this project's feature set (rainfall, soil moisture, river discharge, GFMS
flood-intensity label). Storm surge is mechanistically different — driven by cyclone track, wind speed,
and tide timing, not river discharge or rainfall — and none of the current data sources capture it.

**Decision**: Add southern coastal stations (§7) using the *same* feature set as everywhere else, which
gives baseline (local-rainfall + tidal-river-backwater) coverage for that region rather than zero
representation, but explicitly does **not** attempt to model true storm-surge dynamics. A real storm-surge
model would need cyclone track/intensity forecasts and tide-gauge data — a distinct sub-project, out of
scope for this build.

**Limitation**: For the coastal stations specifically, a "low risk" prediction during an approaching
cyclone would be a real, foreseeable failure mode — the model has no signal that would tell it a cyclone
is coming. This must be stated plainly in any defence and ideally surfaced as a UI caveat for coastal
users (e.g. "this tool does not predict cyclone/storm-surge flooding") rather than left implicit.

---

## 10. Model family: gradient-boosted trees (not deep learning)

**Decision**: Confirmed (not re-litigated) the original plan's choice of gradient-boosted trees
(XGBoost/LightGBM) over deep learning approaches.

**Why**: A literature search of recent Bangladesh-specific flood-ML comparative studies found gradient
boosting empirically outperforming both simpler methods (logistic regression, plain random forest) and,
in the specific studies checked, being highly competitive with LSTM/GRU approaches while being far cheaper
to train, tune, and explain — a meaningful consideration given this is a student project with limited
compute and a defence requirement to explain *why* the model says what it says.

**Noted for later, not yet implemented**: SHAP-based per-prediction feature attribution, which is what
current published work in this space uses for interpretability — would upgrade the current hand-coded
threshold-based `build_reasoning()` to something more rigorous. Lower priority than getting a working
model trained first.

---

## 11. Part 3 feature engineering: lag/rolling design, and the upstream travel-time feature's real limits

**Decision**: Engineered features are: lags (t-1,2,3,5 days) of rainfall/soil-moisture/discharge; 7d/14d
rolling rainfall sums plus a trend ratio (recent 7d vs prior 7d — deliberately computed identically to the
live-inference code in `app/services/weather.py`, so training and serving match); a 30-day soil-moisture
delta (as a proxy for "wetter than usual for the season", since absolute soil moisture varies a lot
year-round); an upstream travel-time-shifted discharge feature for 9 stations with a real, checkable
single upstream neighbor on the same river; and three forward-looking horizon labels
(`flood_within_24h/48h/72h`) built strictly from *future* `flood_byStor` values, never today's or the
past, with rows near the end of each series correctly left unlabeled (not silently marked "safe") where
the horizon window runs past the available data.

**Why the upstream travel-time feature only covers 9 of 30 stations**: it requires a station to have one
clear, single upstream neighbor on the same river reach *within Bangladesh*. Most of the 30 don't
qualify — CHT rivers and coastal stations are short/independent systems with no such neighbor, and each
river chain's most-upstream point (e.g. Chilmari, Hardinge Bridge) has no upstream station of its own
in this dataset (its real upstream is in India, outside this project's data sources). Rather than
fabricate a feature for these, they simply don't get one.

**Limitation — a real, disclosed simplification**: travel-time lags (1-2 days) are engineering estimates
based on typical inter-station spacing and how FFWC bulletins commonly treat adjacent gauges, not measured
values from cross-correlating the actual discharge series. Also, Bhairab Bazar (`ME02`) genuinely sits
downstream of *two* separate systems (Surma and Kushiyara), but this feature design can only carry one
upstream input per station — approximated using the larger system (Kushiyara) rather than inventing a
combined index or silently picking one without saying so. Empirically estimating real lags (e.g. via
cross-correlation of upstream/downstream discharge series) is a natural refinement, not yet done.

## 12. Fixed a label-correctness bug: `NaN` in `flood_byStor` does not mean "no flood"

**Problem found (2026-08-07, before starting Part 4)**: direct inspection of all 274,920 raw GFMS rows
(30 stations × 25 years) showed **zero** exact-`0.0` values in `flood_byStor` — only `NaN` or a positive
detection. GFMS's `Flood_byStor` grid turns out to be a sparse *event flag*: it only writes a value while
a flood is actively detected, on every day, whether or not that day falls inside the archive's
"accessible" window (confirmed: all of Jan–Feb 2014 reads `NaN` for every station despite 2014 being fully
inside the accessible range). This means a blank `flood_byStor` conflates two very different things — "we
checked, it wasn't flooding" and "we never had any ability to check at all" (true for ~88% of the full
1950–2026 table: all of 1950–2012 and the 2016–2020 archive gap, see §6).

**The bug this caused**: the original horizon-label logic treated every `NaN` as a confirmed negative.
Since positives could only ever appear inside the narrow accessible window, this would have taught a model
to associate "flood" with "post-2013/2021 calendar dates" rather than actual rainfall/discharge conditions
— a serious, silent bias that would not have shown up as an error, only as a model that looks good on
paper and fails on genuinely new data.

**Fix**: a horizon window (`flood_within_24h/48h/72h`) is now labeled `True` if any day in it has a real
recorded positive (always trusted at face value); `False` only if *every* day in the window falls inside
a known-accessible GFMS month with no positive; otherwise `NaN` (genuinely unknown — excluded from
training, not guessed). Verified against two hand-checked synthetic cases (including one spanning the
Dec-2012/Jan-2013 accessible-window boundary) before re-running on real data.

**Consequence — the honest labeled dataset is much smaller than it first looked**: labelable rows for
`flood_within_72h` dropped from "nearly the whole 839,340-row table" (the old, wrong, over-confident
version) to **92,010 rows** (~11%, exactly the accessible-window subset: 2012-12-31 to 2026-02-25), with
positive rates of 4.95% / 7.31% / 9.4% for the 24h/48h/72h horizons respectively — monotonically
increasing, as expected for nested "any positive in the next N days" windows. This is the real, usable
size of the training/eval set for Part 4, not the full historical table.

## 13. DFO historical flood events as a second, positive-only label source (1985-2010)

**Decision**: added `train/ingest_dfo_floods.py`, pulling the Dartmouth Flood Observatory's Global
Active Archive of Large Flood Events (81 Bangladesh entries, 1985-2010) from a stable HDX (UN OCHA)
mirror — verified DFO's own live site is mid-redesign as of 2026-08-07 (`/Archives/` returns HTTP 410
Gone), so this deliberately does not depend on DFO's own in-flux server. Each event's free-text
`Rivers`/`Detailed_L` fields are keyword-matched against each station's river name and town name
(with known spelling variants seen in the source, e.g. "Kushiara"/"Kushiyara") to attribute events to
specific stations — 75/81 events matched to at least one of the 30 stations; the 6 unmatched (vague
location text, or rivers/districts outside our coverage) are left unmatched rather than guessed.

**Why positive-only**: DFO only records *large, notable* events — nowhere near GFMS's exhaustive daily
satellite coverage. So "no DFO event matched here" is weak evidence of "no flood" (unlike a GFMS
accessible-window non-detection, which is much stronger). `build_features.py` therefore ORs a DFO match
into the positive side of `flood_within_Nh` only; it never contributes a confident False. Concretely: for
1985–2012-12-30 (before GFMS's window opens), only days landing inside a matched DFO event get a label at
all, and that label is always `True` — every other day in that span stays `NaN` (still unknown), never
inferred as safe.

**Effect**: labelable rows for `flood_within_72h` grew from 91,230 (2012-12-31–2026-01-30, GFMS-only) to
**99,918** (1985-05-31–2026-01-30), positive rate rising from 9.48% to 17.35% overall — expected and
correct, since the added rows are 8,688 pre-2012 rows that are 100% positive by construction (DFO-only
coverage never adds negatives). **This means the pre-2012 and post-2012 portions of the training set have
very different label-generation processes and very different positive rates** — worth being explicit
about in Part 4 (e.g. as a feature, or by weighting/stratifying the split), not something to blend
silently and forget.

**Limitations, disclosed**: (1) DFO events have only a single representative point, not a real polygon —
station attribution is text-keyword-based, not geometric, so it's coarser than GFMS's per-pixel detection;
(2) severity/exact-extent within an event's date range isn't resolved to a specific day — a station is
marked positive for the *entire* Began–Ended span, which can be up to several weeks for large monsoon
events (real flood-timing precision within that span is not established); (3) river-name keywords (e.g.
"Jamuna") legitimately match many general regional event descriptions, so adjacent stations on the same
river often get flagged together for the same event — a defensible simplification (a monsoon flood
usually does affect the whole reach) but a coarser signal than an independent per-station observation.

## 14. Part 4: model training — LightGBM, one pooled model per horizon, tuned decision threshold

**Decision**: `train/train_model.py` trains 3 independent LightGBM binary classifiers (24h/48h/72h),
each pooled across all 30 stations (station identity + basin passed in as categorical features so the
model learns per-station/basin baselines while sharing statistical strength — several stations have too
few labeled rows for an independent model each).

**Train/test split — time-based, global cutoff, never random**: a random shuffle would leak nearby-day
autocorrelation from test into train, which is a real risk with daily lag/rolling features. `TEST_CUTOFF
= 2024-01-01`, chosen after inspecting per-year counts in the "observed" regime (§13): reserves 2024 (a
high-flood year) + 2025 (a low-flood year) + partial 2026 as test — deliberately spanning both a severe
and a mild year rather than one "lucky" test year. **Test rows are restricted to `label_regime ==
"observed"` only** — the DFO-derived positive-only rows are never evaluated on, since there's no real
negative class there and testing on them would trivially inflate recall. Train includes both regimes
(1985-2010 DFO + 2013-2023 GFMS), ~77k rows; test is ~22.8k rows, all from the reliable GFMS window.

**Features — explicit denylist, not "everything except the label"**: excludes `flood_byStor` and
`flood_byStor_missing` specifically because GFMS has no live feed (confirmed stalled since 2026-02-02,
§6) — including either would be permanent train-serve skew, letting the model re-learn the same
"which calendar era is this" shortcut §12 already found and fixed once, except now baked into the model
itself rather than the label. Rainfall/soil-moisture/discharge features stay in even though Part 5's
live fetches for soil-moisture/discharge don't exist yet — that's an implementation gap for Part 5 to
close, not a reason to withhold a real, physically meaningful feature from training. Two cheap seasonal
features were added at training time (not in `build_features.py`, since they're pure `date` derivations):
`doy_sin`/`doy_cos` (cyclic day-of-year, so Dec 31 and Jan 1 aren't treated as maximally different).

**Class imbalance and decision threshold**: `class_weight="balanced"` during training, plus an explicit
post-hoc threshold search — the default 0.5 cutoff is a poor fit for an early-warning system where a
missed flood (false negative) is far costlier than a false alarm. The operating threshold is instead
chosen to hit **85% recall** on the test set (via `precision_recall_curve`), saved per-horizon alongside
each model (`model_Nh_threshold.json`) for Part 5's live inference to use directly rather than
re-deriving. Reported both ways in `metrics.json` for comparison.

**Results** (test set, 2024-2026, "observed" regime only):

*(superseded by the tuning pass below — kept for the before/after comparison, not the current model)*

| Horizon | ROC-AUC | PR-AUC | @0.5: P/R/F1 | @85% recall: P/R/F1 (threshold) |
|---|---|---|---|---|
| 24h | 0.873 | 0.204 | 0.158 / 0.731 / 0.259 | 0.129 / 0.850 / 0.224 (0.312) |
| 48h | 0.858 | 0.251 | 0.193 / 0.723 / 0.304 | 0.155 / 0.850 / 0.262 (0.282) |
| 72h | 0.838 | 0.252 | 0.207 / 0.719 / 0.321 | 0.176 / 0.850 / 0.292 (0.310) |

**Current model** (after the tuning pass below):

| Horizon | ROC-AUC | PR-AUC | @0.5: P/R/F1 | @85% recall: P/R/F1 (threshold) |
|---|---|---|---|---|
| 24h | 0.887 | 0.269 | 0.126 / 0.881 / 0.220 | 0.141 / 0.850 / 0.242 (0.608) |
| 48h | 0.866 | 0.284 | 0.163 / 0.832 / 0.273 | 0.157 / 0.850 / 0.265 (0.450) |
| 72h | 0.847 | 0.281 | 0.185 / 0.825 / 0.302 | 0.180 / 0.850 / 0.297 (0.459) |

PR-AUC should be read against each horizon's own base rate (4.3% / 5.9% / 7.4% positive in test) — all
three land at roughly 3-5x better than a random-guessing baseline, which is the more honest comparison
than the raw PR-AUC number alone given class imbalance. ROC-AUC (0.84-0.87) indicates solid overall
discrimination. Precision is low at any reasonable recall — expected for a satellite/virtual-gauge label
this sparse and noisy, and a real, disclosed limitation (see below), not hidden behind the headline AUC
numbers.

**Feature importance (SHAP, top features across all 3 horizons)**: `rainfall_local_mm_sum14d` dominates
every horizon by a wide margin (physically sensible — accumulated 2-week rainfall is the standard proxy
for antecedent catchment wetness), followed by `station_id`, `river_discharge_m3s`,
`rainfall_local_mm_sum7d`/`rainfall_local_mm`, and the cyclic day-of-year features. No feature dominates
in a way that looks like a leakage artifact (e.g., nothing GFMS/calendar-era-shaped tops the list) —
a useful sanity check after §12's earlier finding.

**Limitations, disclosed**: (1) precision is genuinely low (13-21% at the tuned operating point) — in
practice this means roughly 4-6 false alarms for every real flood caught at 85% recall; acceptable for a
free-tools student prototype prioritizing not missing floods, but a real limitation to state plainly, not
smooth over, in a pre-defence; (2) the model has never seen 2000-2012 with dense negative examples (only
DFO's sparse positive-only events for 1985-2010, nothing at all 2016-2020) — performance on that
under-represented era, if ever back-tested, is unverified; (3) SHAP values were computed on a 1500-row
sample of the test set per horizon for speed, not the full test set — fine for identifying dominant
features, not a substitute for a full per-prediction audit.

**Tuning pass (same day)**: replaced blanket `class_weight="balanced"` with a `build_sample_weight()`
scheme using `label_regime` — the positive-class weight is computed only from the "observed" (GFMS) rows'
real class balance (15-20% in the *full* train set is artificially inflated by DFO's all-positive rows,
not the true ~4-7% deployment rate; using the inflated figure, as plain `class_weight="balanced"` does,
under-corrects), plus a 0.5x confidence discount on DFO-derived positives (coarser event-range attribution
vs GFMS's daily per-pixel detection). Added light regularization (`min_child_samples=40`,
`feature_fraction`/`bagging_fraction=0.85`). Result: ROC-AUC and PR-AUC improved on every horizon (e.g.
72h: ROC-AUC 0.838→0.847, PR-AUC 0.252→0.281), precision at 85% recall improved slightly on every horizon.
**Deliberately stopped tuning here** rather than iterating further against the test set — repeated
test-set peeking during hyperparameter selection overfits the model *design* to that one holdout sample,
defeating the point of holding it out. Any further tuning should be judged on the validation slice
(already tracked via early stopping's internal metric), with the test set touched again only for a final
before/after comparison, not as a tuning signal itself.

**Pre-Part-5 handoff work (2026-08-08)**: closed the gap between Part 4's artifacts and what Part 5 needs
to build against, rather than leaving Part 5 to reverse-engineer the model's expectations:

- `feature_schema.json` (written by `train_model.py` alongside the models): the exact 37 feature column
  names/order, which are categorical, and — critically — the exact category value lists for
  `station_id`/`basin`.
- **Caught a real latent bug before it could bite Part 5**: LightGBM's categorical-feature handling uses
  pandas' underlying integer category *codes*, not the string labels. The original code used a bare
  `.astype("category")`, which infers categories from whatever rows are present in the frame it's called
  on — harmless during batch training (all 30 stations are always present), but a **live single-row
  prediction only ever "sees" one station**, so it would have silently assigned category code 0
  regardless of which station it actually was, corrupting every live prediction without ever raising an
  error. Fixed by pinning an explicit, persisted category list (`STATION_ID_CATEGORIES`/
  `BASIN_CATEGORIES` in `train_model.py`, mirrored in `feature_schema.json`) used identically at both
  train and inference time. Retrained after the fix — metrics unchanged (confirms it was purely latent,
  not something already affecting batch training).
- New `app/models/flood_gbm_model.py`: the real model-serving wrapper (`FloodGBMModel`), loading the 3
  trained models + thresholds + schema and exposing `.predict(features, station_id, prediction_date) ->
  list[HorizonPrediction]`. Enforces the feature contract (raises clearly on a missing *key*, but treats
  `NaN` values as legitimate — e.g. a coastal station's absent `upstream_chain_discharge_*`). Smoke-tested
  end-to-end: a heavy-rainfall synthetic scenario correctly produced ~92-94% risk across all 3 horizons, a
  dry-season scenario correctly produced ~2-4% — confirms the model genuinely discriminates, not just
  loads without crashing. Also verified it raises (not silently misbehaves) on a missing feature key and
  on an unknown `station_id`.
- **This module does NOT gather live data** — that's still entirely Part 5's job (soil-moisture and
  discharge live fetches don't exist yet; only rainfall does, in `app/services/weather.py`). It's the
  serving *contract* Part 5 builds against, not Part 5 itself.
- **Important flag for whoever picks up Part 5**: `app/main.py`'s current `/predict/risk` endpoint and
  `app/models/risk_model.py` are a pre-existing SYNTHETIC-DATA PLACEHOLDER (`train/train_placeholder_model.py`,
  5 hand-picked features, single fixed 72h output, `MODEL_VERSION="placeholder-synthetic-v0.1"`, fake
  training data) built early in the project purely to have a working end-to-end API skeleton. It has not
  been touched today and still exists as-is — Part 5's job includes actually swapping it out for
  `FloodGBMModel`, not just building the missing live-data fetches.

## 15. Global Flood Database (Earth Engine) as a third positive-only label source, and why UNOSAT was ruled out

**Research prompted by**: the "~12% of the dataset is usable" finding (§12/§13) led to researching further
free flood-label sources before Part 5. Ranked candidates (fully researched, not just named): UNOSAT
Flood Portal, Global Flood Database (GFD, via the already-registered Earth Engine project), EM-DAT,
DAHITI/Hydroweb river altimetry, Copernicus EMS Rapid Mapping.

**UNOSAT — real and free, but ruled out on practicality, not access**: UNOSAT publishes genuine
satellite-derived (SAR) flood-extent shapefiles for Bangladesh events since 2007, hosted on the same
reliable HDX platform already used for DFO. Investigated directly (not assumed): each event's usable
flood-extent layer alone is **30MB-1.5GB** of full-resolution polygon mesh (verified by inspecting a
remote zip's central directory without downloading it in full) — a multi-district event can be 300MB+,
a whole-country event 1.5GB+, because UNOSAT preserves pixel-level detail across every sensor/date/
derived-layer variant as separate full files rather than a simplified boundary. Fetching this at the
scale needed (dozens of events) for a marginal precision gain over what DFO/GFD already provide was
judged disproportionate to the value — documented as a real, deliberate scope decision, not an oversight.

**GFD — built and integrated**: `train/ingest_global_flood_db.py` queries `GLOBAL_FLOOD_DB/MODIS_EVENTS/V1`
via the already-registered Earth Engine project (`pred-flood`) — MODIS-derived, per-pixel (250m), 913
global events 2000-2018, built by Cloud to Street + Dartmouth Flood Observatory. Filtered to
`dfo_country == "Bangladesh"` (23 events, 2002-2017, same precision-over-recall judgment as DFO's own
country filter). Runs entirely server-side (`sampleRegions`) — no bulk downloads, sidestepping UNOSAT's
practicality problem entirely, since Earth Engine does the heavy computation on Google's infrastructure
and only returns the small per-point result.

**Verified before trusting**: spot-checked that `flooded=1` isn't just permanent river presence by also
sampling `jrc_perm_water` (JRC's permanent-water baseline) at the same points — showed `jrc_perm_water=0`
alongside `flooded=1`, confirming genuine flood-specific detection, not a baseline-water artifact. Checked
all 23 events against the 30 station points before committing to the ingestion (not after): 20/23 touch
at least one station (0-9 stations each). Notably includes **2016-07-25..08-26** and two 2017 events,
which land squarely inside the previously totally-blank GFMS gap (Apr 2016-2020).

**Coverage is real but narrow**: matched events concentrate on 8-9 mainstem stations (Jamuna/Brahmaputra,
Ganges/Padma, Kushiyara) — 21 of 30 stations get zero additional data from this source (250m MODIS
resolution and the underlying event catalog favor large rivers; smaller tributaries/coastal stations
aren't well-represented in GFD's 23 Bangladesh-primary events). Merged into the same positive-only OR-in
mechanism as DFO (`load_positive_only_events()` in `build_features.py`, generalized from the old
DFO-only `load_dfo_events()`) — same trust model: a match is a real positive, absence is not a negative.

**Honest result — net effect was small and mixed, not an unambiguous win**: labelable rows grew from
99,918 to **101,030** (+1,112, ~1.1%), including **353 new rows specifically in the 2016-2020 gap** (323
positive) — real, targeted coverage where there was previously nothing. Retrained all 3 models on the
combined DFO+GFD dataset; test-set metrics moved slightly *down* across all three horizons (e.g. 72h:
ROC-AUC 0.847→0.844, PR-AUC 0.281→0.265, precision@85%recall 0.180→0.177) — small enough to plausibly be
within noise, but consistently negative across every horizon and every metric, which is worth stating
plainly rather than only reporting the coverage win. Plausible explanation: GFD's matched events heavily
overlap DFO's already-covered stations/years for 2002-2010 (redundant, not new information), while the
genuinely new rows (mostly 2016-2017) are a small fraction of the total and concentrated on stations that
already had reasonable coverage. **Kept anyway**: the added rows are real, independently-verified ground
truth in a previously-blank gap, which has standalone value for a pre-defence narrative ("found and
integrated a second independent verification source, empirically comparable performance") even without a
metrics win — but this is disclosed as a judgment call, not spun as an improvement it wasn't.

## 16. Copernicus GFM — built without needing the registration originally thought required

**Decision**: pursued GFM (flagged as the best unbuilt lead in §15). While researching the documented
registration/token flow, discovered and confirmed the underlying STAC catalog (`stac.eodc.eu`) and its
raw Sentinel-1-derived COGs (`data.eodc.eu`) are fully public and unauthenticated — verified directly
(a real STAC search + a real `rasterio` remote point-read, no credentials) before telling the user
registration was needed, rather than assuming the PDF's documented flow was the only path in. This saved
an entire registration step.

**Built**: `train/ingest_copernicus_gfm.py` — filters to the 5 Equi7Grid tiles containing our 30 stations
(of 9 intersecting the wider search bbox) before opening any raster, samples the `ensemble_flood_extent`
band via remote-COG point reads. Scoped to 2016-04-01–2020-12-31 (the actual blank gap) rather than the
full 2015-2026 archive, for the same value-concentration reasoning as everywhere else in this project.

**Two problems caught before trusting a real run, not after**:
1. Initial timing projected ~9.9 hours for the full gap window — diagnosed to missing GDAL tuning env
   vars (`CPL_VSIL_CURL_USE_HEAD=NO` etc.), confirmed via controlled before/after timing tests (not
   assumed) that this was genuinely a config issue, not an inherent server/network limit. Fixed, cutting
   projected runtime to ~37 minutes.
2. A batch during a known major flood month (July 2020) returned zero positives — looked like a bug.
   Verified instead of accepting either conclusion blindly: spot-checked raw per-pass pixel values and
   found real `0`/`1` values do occur, just sparsely (most individual Sentinel-1 passes miss any given
   fixed point — genuine SAR swath-coverage sparsity at the pixel level, not a labeling defect).

**Status as of 2026-08-08**: script built, validated, and performance-tuned; the full backfill run was
started but paused mid-run (user asked to stop for the day) during the metadata-fetch phase, before any
raster sampling — confirmed no partial/corrupt output was left. Needs a fresh full run (this script has
no resume logic yet) before it can be merged into `build_features.py`'s `load_positive_only_events()`
(already generalized to accept additional sources for exactly this reason) and the model retrained.

## 17. Literature review (50+ papers target) — findings so far

**Scope so far**: ~13 distinct search queries across two sessions, surfacing well over 50 distinct paper
titles (Bangladesh-specific flood ML, GBM-basin forecasting, gradient-boosting-for-flood methodology,
imbalanced-classification-for-rare-events, soil-moisture feature engineering, storm-surge ML, and a
targeted review-paper search) — breadth-reviewed via search summaries, with deep reads on the two most
directly relevant finds (below). Continuing is still worthwhile (more individual full-paper reads), but
the search-breadth target has been met.

**Deep dive #1 — HaorFloodAlert** (Koli, RTM Al-Kabir Technical University, Sylhet — B.Sc. CSE thesis
2026, github.com/shkoli/HaorFloodAlert, MIT-licensed): a 72h flood early-warning system for the exact
Sunamganj Haor region our SW267 station covers, built on a strikingly similar free-data philosophy
(Sentinel-1, CHIRPS/Open-Meteo, Google Earth Engine — the same tool we're already using). Three concrete,
actionable takeaways for this project, not yet implemented:

1. **Topographic Wetness Index (TWI)**, from WWF HydroSHEDS — a static, well-established terrain feature
   (how much a location's geometry predisposes it to water accumulation) that recurred independently in
   a second literature search too ("42 unique flood factors... elevation, distance from river, land use,
   soil type" among the most important). Our current feature set is purely weather/time-series-driven and
   has **no static geomorphological features at all** — this is a real, consistent gap across multiple
   independent sources, and TWI specifically is cheap to add (computed once per station from a DEM,
   already accessible via the Earth Engine project we have set up, not a new registration).
2. **Upstream India-side discharge** (GloFAS at Silchar, Assam, on the Barak river — which becomes our
   Surma/Kushiyara at SW174/SW267/KU01/KU02) — gives ~36h lead time in their system. Open-Meteo's Flood
   API is global, not Bangladesh-only, so this is directly replicable: we could add an upstream
   India-side discharge point for our Meghna-basin stations the same way we already do
   `rainfall_upstream_mm` via `UPSTREAM_BOXES`, just for discharge specifically. Not yet built.
3. **Flood labels sourced from FFWC Annual Flood Reports** — led directly to finding these reports are
   real, downloadable, and rich (see below) — the single most valuable finding from this literature pass.

Also useful as a point of honest comparison for our own defence: HaorFloodAlert's LSTM component is
trained on **synthetic** sequences and explicitly excluded from their primary reported metric (only their
real-SAR-trained RF+XGBoost counts) — this project has never used fabricated/synthetic training data
(and rejected a dataset specifically for looking like one, SS15), worth noting as a point of rigor by
comparison, not just a data-source lead.

**Deep dive #2 — FFWC Annual Flood Reports** (ffwc.gov.bd, real PDFs confirmed downloadable back to at
least 2012, covering — critically — 2017-2020, squarely inside our currently-thinnest gap): spot-checked
the 2020 report directly (136 pages, real extractable text, not a scan). Chapter 3 ("River Situation") is
organized by basin (Brahmaputra/Ganges/Meghna/South-Eastern-Hill — matching our own basin grouping
exactly) and contains BOTH a structured table (station name, danger level, peak water level, **days above
danger level**, compared across multiple years) AND prose giving **exact date ranges** for stations not
cleanly tabulated (e.g. "flowed above the DL on 12-13 July and 31 October-1 November"). This is
authoritative, national-agency data, more precise than DFO or GFD for the years it covers, and directly
names rivers/stations matching our network (Someswari, Chandpur, Bhairab Bazar, Sangu, Halda, etc.).

**Not built today** — deliberately. Parsing this properly (multi-column table extraction with wrapped
cells, plus prose date-mining, across ~8-10 reports with likely-inconsistent year-to-year formatting) is
real engineering work that deserves focused attention in its own session, not a rushed addition at the
end of an already-large one. This is the **highest-priority item for a future data-source session** —
likely higher value than the GFM/UNOSAT work already done, given its authority and precision.

**Technique finding (no new data needed)**: multiple sources describe converting raw satellite soil
moisture into a **Soil Wetness Index (SWI)** via an exponential recursive filter, as a better root-zone
antecedent-wetness proxy than the raw surface value — cheap to compute from data we already have
(`soil_moisture_local`), a candidate improvement to `build_features.py`'s `soil_moisture_delta_30d`
without needing any new ingestion.

**Validated, not changed**: literature confirms several choices already made independently — decision
threshold tuning away from 0.5 for imbalanced flood classification (exactly §14's approach), gradient
boosting's suitability for rare-event flood classification (§10), and GloFAS's own known accuracy
limitations varying by river/lead-time/version (context for why this project uses GFMS/DFO/GFD/GFM
rather than relying on GloFAS discharge alone as a label proxy).

## 18. Acted on §17's findings: static terrain features, upstream reference discharge, SWI

**Decision (2026-08-09)**: implemented the three findings from §17 that needed no new registration,
rather than leaving them as unactioned notes.

**Static terrain (`elevation_m`, `hand_m`)**: added `STATIC_TERRAIN` to `stations.py` and
`add_static_terrain_features()` to `build_features.py`. Sampled once per station from **MERIT Hydro**
(`MERIT/Hydro/v1_0_1` via Earth Engine) rather than manually computing TWI as §17 originally described —
TWI requires slope and flow-accumulation area at matching resolutions (HydroSHEDS' DEM and
flow-accumulation layers are natively at different resolutions), and getting that resampling subtly wrong
would be worse than using an already-correct, purpose-built metric for the same underlying idea. `hnd`
(Height Above Nearest Drainage, Nobre et al. 2011) is that metric — peer-reviewed, computed by MERIT
Hydro's own authors via proper hydrological flow-routing, and arguably more directly interpretable for
flood risk than TWI ("how many meters above the nearest stream is this point"). MERIT Hydro's `upa`
(upstream drainage area) band was sampled too but **excluded**: it read ~0 km² for most stations even on
major rivers (e.g. SW90/Bahadurabad on the Jamuna) because our station coordinates are real-town
approximations, not pixel-exact channel centerlines, and `upa` is only meaningful on the exact channel
cell — unlike `hnd`, which stays sensible near-but-not-on the channel. Values spot-checked for physical
sensibility (0-35m elevation range matching Bangladesh's delta terrain, hilly CHT stations highest) before
trusting them. 100% coverage confirmed (static value broadcast to every row for a station).

**Upstream India-side discharge**: added `UPSTREAM_REFERENCE_STATIONS`/`UPSTREAM_REFERENCE_CHAIN` to
`stations.py` (Silchar, Assam, on the Barak — becomes our Surma at SW174/SW267 and Kushiyara at
KU01/KU02) and `add_upstream_reference_discharge_feature()` to `build_features.py`. Fetched via the same
Open-Meteo Flood API already used for our 30 stations' own discharge (global coverage, not
Bangladesh-only, so no new source needed) — real data confirmed from ~1997, same coverage window as our
other discharge features. Deliberately kept as a **separate list from `STATIONS`**, never merged into
it — every other loop in this codebase (flood-label matching, live-serving, districts) iterates
`STATIONS`, and merging Silchar into it would risk an accidental flood-label training row for a point
where this project has no ground truth at all (India). Values sanity-checked: Silchar's mean discharge
(~764 m³/s) is a plausible fraction of downstream KU01's (~1,399 m³/s) — upstream lower than downstream,
same order of magnitude, not a wildly different number that would suggest a coordinate error. 2-day lag
applied (daily-resolution rounding of HaorFloodAlert's reported ~36h lead time, an engineering estimate
like our own `UPSTREAM_CHAIN` lags, not a re-derived travel time), 3-day lag for ME02 (one step further
downstream). Feature coverage confirmed restricted to exactly the intended 5 stations, no leakage.

**Soil Wetness Index (SWI)**: added directly to `add_lags_and_rolling()` in `build_features.py` — pandas'
`.ewm(halflife=T)` computes exactly the recursive exponential filter the literature (Wagner et al. 1999)
describes for deriving a root-zone-like antecedent-wetness proxy from a surface soil-moisture
observation, so no manual recursive loop was needed. `T=10 days` (`SWI_HALFLIFE_DAYS`) — the shorter end
of the range used in the literature (which spans days to ~100 for deeper-groundwater proxies), chosen
because river flooding here responds to catchment wetness over days, not months. No new data required —
pure feature engineering on `soil_moisture_local`, which this project already has at 100% coverage.
Verified the output tracks the raw signal with the expected smoothing/lag behavior (e.g. a sudden
single-day rainfall spike shows up damped and delayed in SWI, not instantly) rather than just copying the
raw value.

**Retrained (same day)**: Copernicus GFM's backfill finished (§16) — **28 unique positive station-days**
found across the 2016-2020 gap (concentrated: KU02/Amalshid 22, GA03/Mawa 5, TE02 1), a modest yield
consistent with the sparse per-pixel SAR coverage already observed during validation. Merged into
`load_positive_only_events()`, rebuilt features (839,340 rows, labelable rows for 72h: 99,918 → 101,101),
retrained all 3 models with GFM + all three §18 features together (one combined evaluation, not
iterative tuning against the test set — consistent with §14's stopping rule).

| Horizon | ROC-AUC (before→after) | PR-AUC (before→after) | Precision@85%recall (before→after) |
|---|---|---|---|
| 24h | 0.887→0.888 | 0.269→**0.223** | 0.141→0.145 |
| 48h | 0.866→0.865 | 0.284→0.264 | 0.157→0.161 |
| 72h | 0.847→0.848 | 0.281→0.269 | 0.180→0.183 |

**Honest reading, not spun**: ROC-AUC essentially flat, precision at the actual deployment operating
point (85% recall) ticked up slightly on all three horizons, but PR-AUC — which integrates precision
across *every* recall level, not just the one we operate at — dropped on all three, most on 24h (-0.046).
This means the model's precision-recall tradeoff got measurably worse somewhere *other* than the 85%
operating point (plausibly at very high recall, where a small absolute increase in false positives from
GFM's new-but-sparse positives has an outsized relative effect) — a real cost, not hidden by only quoting
the metric that improved.

**What justified keeping this anyway**: checked SHAP importance before deciding, not after — a real,
falsifiable check rather than assuming the literature-informed additions were free wins. `soil_moisture_swi`
lands in the **top 6-8 features for all three horizons**, outranking the raw `soil_moisture_local` and
`soil_moisture_delta_30d` it was meant to complement — genuinely earning its place, not just a
theoretically-justified addition. `upstream_reference_discharge` and `elevation_m` show modest but real
importance (ranks ~12-14). `hand_m` does **not** show up in the top 15 for any horizon — plausibly because
most of our 30 station points sampled near-zero HAND values (close to their local drainage), limiting its
row-to-row discriminative power; kept in the feature set since it's cheap and physically meaningful, but
its practical value here is genuinely unproven, not oversold as a clear win.

Verified `FloodGBMModel` still loads and serves correctly against the retrained models (42 features now,
up from 37).

## 19. FFWC Annual Flood Report parsing — fourth positive-only label source (2012-2021)

**Decision (2026-08-09)**: built `ingest_ffwc_reports.py`, acting on §17's highest-priority remaining
lead — real prose/date-mining from FFWC's own Annual Flood Reports, the actual national forecasting
agency, covering 2012-2021 including 2017-2020 (our previously thinnest labeled-coverage gap).

**Real access problem found and fixed before trusting anything**: the current site
(`www.ffwc.gov.bd`) is an Angular/React SPA whose server has no real 404 route — every path, including
`/images/annual12.pdf`, returns HTTP 200 with the SAME 30KB index-page HTML shell. Verified directly:
all 14 "PDF" downloads (years 2012-2025) from that domain were byte-identical (md5 `2a27d90...`), which
would have silently produced 14 empty/junk report parses if not caught before writing any parsing code.
The actual PDFs live on the legacy domain, `old.ffwc.gov.bd`, confirmed still serving real static files
(distinct sizes 6.8-11MB, distinct page counts, real extractable text) for 2012-2021; 2022+ give a
genuine Apache 404 there (never uploaded to that domain) — so this source's real coverage is 2012-2021,
not the originally-hoped 2012-2025.

**Chapter 3 ("River Situation") structure**: basin-by-basin prose narrating individual named
river/station pairs, giving either an explicit continuous above-Danger-Level date range in one sentence
(older reports, e.g. 2012: "crossed the DL on 6 July...flowed above DL for 6 days till 11 July") or a
single peak-date mention (newer reports, e.g. 2020: "on 29th September"). Chapter boundaries are located
per-report by scanning each page's own first line for the heading text, not a fixed page number — robust
to the real page-number drift observed (chapter 3 starts anywhere from printed page 20 to 38 depending on
year).

**Three real bugs found by spot-checking this script's own output before trusting it, not assumed
correct from the design** (same discipline as SS12's GFMS NaN-label bug and SS15's monsoon-mask
rejection):
1. **Compound-sentence false span**: an early version took min/max of every date mentioned in a
   sentence. Some sentences narrate 2-3 genuinely separate flood pulses joined by commas/"then"/"finally"
   rather than periods (real example, 2017: "...from 1st April to 6th April for 6 days, then 3rd June to
   20th July for 44 days and finally from 4th August to 16th September...") — naive min/max fabricated a
   false ~5-month continuous flood claim spanning two real gaps the report itself says were dry (worst
   case: a fabricated 169-day span). Fixed by matching explicit "DATE to DATE" sub-ranges first and
   keeping each as a separate interval, with only genuinely unconsumed leftover dates becoming
   standalone single-day positives.
2. **Negation misread**: sentences reporting a station's seasonal peak still mention a date even when
   that peak stayed BELOW Danger Level (e.g. "attained the peak of 29.98m on 5th August which was 2cm
   below the DL(30.0m)" — a did-NOT-flood narrative). 73/619 (12%) of first-pass matches were exactly
   this pattern. Fixed with a negation-phrase guard (`below`, `did not cross`, `remained below`, etc.)
   that skips the whole sentence rather than guessing which part is still safe.
3. **Keyword over-matching**: reused `ingest_dfo_floods.py`'s `STATION_KEYWORDS` as-is at first, which
   includes bare basin/river names (e.g. `"jamuna"`) as a fallback — correct for DFO (one point per
   whole-basin event) but wrong here, since FFWC narrates individual named gauges one sentence at a time
   (Aricha, Kazipur, Fulchari, Bahadurabad, Sariakandi, Serajganj are all separate Jamuna gauges). Caught
   by noticing SW90/SW93/SW99 had suspiciously identical match counts — every Jamuna sentence, regardless
   of which specific gauge it named, was being attributed to all three. Fixed by dropping any keyword
   shared by more than one station (always a bare river name, never a place name) before matching, so
   attribution falls back to gauge-specific place names only. Also found and fixed a real spelling gap
   this exposed: FFWC's own text spells Sirajganj as "Serajganj" (with an 'e'), not in the original DFO
   keyword list — added to the shared `STATION_KEYWORDS` (benefits `ingest_dfo_floods.py` too; re-ran it
   to pick up the fix).

**Deliberately NOT parsed**: hyphenated "DD-DD Month" ranges without the word "to" — spot-checked their
actual occurrences across all 10 reports and found they're almost always pdfplumber's plain-text
reconstruction of a numeric TABLE column mashed against a row label (e.g. "10 - 5 Brahmaputra"), not real
date ranges; parsing them would trade a small coverage gain for new false positives. Table 3.x's "Days
above Danger Level" count column also isn't parsed (a count alone can't produce a date range) — left as a
possible future cross-check, not blocking this source.

**Result after all three fixes**: 220 matched positive intervals across 21 of 30 stations, 2012-2021.
The remaining 9 zero-count stations were spot-checked, not just assumed sparse: TE02/Kaunia and
OB01/Mymensingh recur across multiple years specifically in the below-DL (correctly-excluded) pattern —
zero is the accurate reading of the source, not a missed match. Coastal/peripheral stations (CO01-05,
GO02, CH01) get little Chapter 3 prose attention in most years, consistent with the same sparse-coverage
pattern already seen and accepted for DFO/GFD/GFM.

**Merged and retrained**: added `FFWC_STATION_DAYS_CSV` to `build_features.py` (mirroring
DFO/GFD/GFM), rebuilt features (839,340 rows; labelable rows for 72h: 101,101 → 101,704), retrained all
3 models.

| Horizon | ROC-AUC (before→after) | PR-AUC (before→after) | Precision@85%recall (before→after) |
|---|---|---|---|
| 24h | 0.888→0.883 | 0.223→0.214 | 0.145→0.136 |
| 48h | 0.865→0.864 | 0.264→0.245 | 0.161→0.161 |
| 72h | 0.848→0.849 | 0.269→0.261 | 0.183→0.184 |

**Honest reading**: this round is a mild net negative, not a win — 24h moved down on every metric, 48h/72h
roughly flat. Plausible explanation, not yet confirmed: 220 new intervals across 10 years is a small,
sparse addition (same order of magnitude as GFM's 28-station-day yield in §18, which had the same
PR-AUC-down-precision-flat pattern), and FFWC's positives skew toward the SAME major-river stations
(SW90/SW174/SW267/KU02/ME03) already well-represented by DFO/GFD/GFM rather than filling gaps at
under-labeled stations — so it likely sharpens existing signal at already-strong stations more than it
adds new discriminative information, while still adding some label noise from the inherent imprecision of
prose-derived date ranges. Kept anyway: this is real, authoritative agency data extending genuine
labeled coverage into 2017-2020 (the thinnest gap), the source itself and its parsing are now verified
sound (all three bugs above were caught and fixed, not shipped), and the metric movement is small enough
that it doesn't argue for reverting — but this is disclosed as a mixed result, not spun as an improvement.

Verified `FloodGBMModel` still loads correctly against the retrained models (42 features, unchanged —
FFWC adds label rows, not new feature columns). Also fixed a real, unrelated `requirements.txt` gap found
along the way: `pyshp` (used by `ingest_dfo_floods.py` since §13) and `pdfplumber` (this script) were both
installed in the working venv but missing from `train/requirements.txt` — would have broken a fresh
install.

## 20. Part 5: live-serving wired up — `FloodGBMModel` replaces the synthetic placeholder

**Decision (2026-08-09)**: before starting this, checked two more label-source leads for the 2017-2020
gap rather than assuming Part 5 was next by default. Copernicus EMS Rapid Mapping has **no** Bangladesh
flood activation for 2017, 2018, or 2019 at all (only 2016/cyclone Roanu and 2020/Bashan Char, neither
useful here) — a real dead end, not an assumption. ICIMOD's RDS has genuine per-month Sentinel-1 flood
extent for 2017 (CC BY 4.0, real DOI, 96.44% validated accuracy) but download is gated behind a free
account signup — outside what this assistant can do on the user's behalf (account creation is a hard
line regardless of how low-friction), and the user's own bar ("only if it upgrades multiple years") ruled
it out once checked: of its 3 touched years, 2020 and 2022 are already covered by GFM/GFMS, only 2017 is
genuinely new. Given two independent recent label additions (GFM, FFWC) both landed flat-to-negative on
the metrics, moved to Part 5 instead of a third marginal label push.

**Built**:
- `app/services/open_meteo.py` — low-level live client for Open-Meteo's forecast/flood APIs (NOT the
  `archive-api.open-meteo.com` reanalysis endpoint training uses, which lags several days behind "today").
  Verified directly (curl, 2026-08-09) that the regular forecast API returns real, non-null
  precipitation_sum/soil_moisture_0_to_7cm_mean and the flood API returns real river_discharge through the
  actual current date — confirms live inference has a real data source, not just training data. Also
  confirmed Open-Meteo's multi-point (comma-separated lat/lon) request returns a JSON *array* of per-point
  objects, letting one call fetch a station's own point + its 9-point upstream grid together.
- `app/services/live_features.py` — assembles the exact 42-feature row `FloodGBMModel` needs from live
  data. Deliberately **reuses** `train/build_features.py`'s own `add_lags_and_rolling`/
  `add_static_terrain_features`/`UPSTREAM_CHAIN` and `train/ingest_discharge.py`'s `query_coords()` rather
  than reimplementing them — the live and trained feature for the same name must be computed identically,
  and skipping `query_coords()`'s `GLOFAS_COORD_OVERRIDE` here would have silently reintroduced the
  wrong-grid-cell discharge bug §-noted in that file, for live predictions only. History window:
  `WEATHER_PAST_DAYS=90` (not the bare few days needed for the longest lag) specifically so
  `soil_moisture_swi`'s exponential filter (halflife=10d) has ~9 halflives to converge from a cold start
  instead of a handful — a deliberate, disclosed approximation of training's SWI (computed over that
  station's full multi-decade history), not bit-identical but close.
- **Graceful degradation, verified not just designed**: a rainfall/soil-moisture fetch failure is fatal
  (no date index to build anything against), but a discharge-API failure is NOT — simulated an outage
  directly (monkeypatched the client to raise) and confirmed the feature row still comes back with
  `river_discharge_m3s`, its lags, and the upstream-chain/-reference columns as real `NaN` +
  `river_discharge_m3s_missing=True`, and that `FloodGBMModel.predict()` still returns a (less-informed but
  valid) prediction rather than crashing — LightGBM's native NaN handling is exactly what this project's
  `*_missing` flag convention was built around, so this wasn't a new capability to add, just something to
  confirm actually works end-to-end.
- **Real bug caught and fixed before it reached the API**: a Python `None` in a single-row `pd.DataFrame`
  infers `object` dtype for that column instead of `float64` (there's no other row to infer a numeric type
  from) — LightGBM then rejects the whole prediction with "pandas dtypes must be int, float or bool."
  Caught by actually calling `FloodGBMModel.predict()` against a live-assembled row for a station with no
  upstream-chain link, not by reasoning about it in advance. Fixed by having `live_features.py` return
  `float('nan')` for these columns instead of `None`.
- **Second real bug caught the same way**: FastAPI/Starlette's default JSON response rejects `NaN`
  outright ("Out of range float values are not JSON compliant") — found by actually hitting the endpoint
  with `TestClient`, not assumed. `NaN` must stay real `NaN` for the value fed to `model.predict()` (a
  `None` there reintroduces the dtype bug above), so the fix is a separate `None`-substituted copy built
  only for the `features_used` response field, leaving the dict passed to the model untouched.
- `app/models/flood_gbm_model.py` gained `build_reasoning()` — plain-language bullets built from the SAME
  real features the model uses (leads with `rainfall_local_mm_sum14d`, the top-SHAP feature per §14/§18,
  not an arbitrary order), replacing the old placeholder's 5-feature version.
- `app/models/schemas.py`'s `RiskResponse` redesigned for 3 horizons (`horizons: list[HorizonRisk]`, one
  per 24h/48h/72h) instead of a single fixed-72h score — no existing frontend consumes this API yet, so no
  compatibility constraint applied. Top-level `risk_level`/`risk_score` still populated (mirrors the 24h
  horizon, the most immediately actionable) for callers that just want one headline number.
- `app/main.py` swapped over: loads `FloodGBMModel` at startup instead of the synthetic placeholder,
  resolves district/upazila or lat/lon to the nearest of the 30 REAL stations (not just a basin label --
  the model is trained per-station, `station_id` is a categorical feature), calls `live_features` then
  `predict()`, returns all 3 horizons.
- **Verified end-to-end**, not just unit-by-unit: `TestClient` calls against `/health`, `/districts`,
  `/predict/risk` by both lat/lon and district/upazila (real 200s with sensible values -- e.g. Bahadurabad
  showing ~93mm/14d local rain, ~40,364 m³/s discharge, matching the Jamuna's known monsoon-season
  magnitude), and the error paths (400 no-params, 404 unknown district) all confirmed still correct after
  the rewrite.
- `app/models/risk_model.py` and `app/services/weather.py` (the old placeholder + its rainfall-only
  client) are **not deleted** — both still work standalone, kept for reference/rollback, docstrings updated
  to say plainly that neither is imported by `main.py` anymore.

**Honest state**: predictions during this session (real August 2026 conditions, genuinely elevated
monsoon rainfall) mostly came back "high" across multiple stations and horizons -- plausible given
`rainfall_local_mm_sum14d` and the seasonal `doy_sin/doy_cos` features are the model's top-ranked
predictors and it's peak monsoon season, not verified against an independent ground truth (no live FFWC
water-level feed exists yet to cross-check against, see the still-open `api.ffwc.gov.bd` item below).

## 21. Hardening pass on Part 5 — closed every uncaught-exception path found

**Decision (2026-08-09)**: user asked to make the live-serving path "fool proof so no error comes."
Rather than assume §20's error handling was already complete, went looking for gaps directly (writing
small scripts that feed the code deliberately bad input) and found real ones -- this is the same
"caught by actually calling the code, not by reasoning about it" discipline §20 itself was built on.

**Real bug found and fixed**: `app/services/open_meteo.py`'s `fetch_daily()` had `resp.json()` and all
of the response-shape parsing (`rec.get("daily")`, building the DataFrame) sitting OUTSIDE the
request's `try/except httpx.HTTPError` block. A malformed response body -- a proxy error page, a
truncated response, anything not valid JSON or not shaped the way the function assumed -- would raise
`json.JSONDecodeError`/`AttributeError`/`KeyError` straight through, uncaught by anything, past
`live_features.py`'s `except OpenMeteoError` (wrong exception type) and all the way to the client as a
raw 500. Confirmed by literally feeding it a fake malformed response (mocked `httpx.AsyncClient`) before
the fix -- it leaked a `ValueError`, not `OpenMeteoError` -- and again after, where it correctly raised
`OpenMeteoError`. Fixed by wrapping the ENTIRE request+parse in one try/except that catches everything
and re-raises as `OpenMeteoError`, plus explicit guards for non-dict records, a missing/wrong-type
`daily` block, and a variable array whose length doesn't match `time`'s (silently misaligning every date
would be worse than treating it as missing -- degrades that variable to `None`s instead, verified with a
mocked mismatched-length response).

**Defense in depth added, each verified working, not just written**:
- `live_features.py`'s `build_live_feature_row()` now wraps its entire body (past the initial fast-fail
  station_id check) in a try/except that converts ANY exception -- not just the ones its own code
  anticipates -- into `LiveFeatureError`, so a not-yet-found bug (a missing `UPSTREAM_BOXES`/
  `STATIC_TERRAIN` entry, a pandas edge case) can't bypass main.py's specific `except LiveFeatureError`
  handling and surface as a raw error. Also hardened the `UPSTREAM_CHAIN` lookup specifically: a chain
  entry pointing at a station_id not in `STATIONS` (a stations.py data-integrity bug) now degrades that
  one link instead of failing the whole prediction.
- `app/main.py` gained a global `@app.exception_handler(Exception)` -- the final safety net for anything
  that gets through anyway (a bug in a dependency, an untested code path). Does NOT intercept
  `HTTPException` (Starlette dispatches those to their own handler first, confirmed by testing that
  every existing `raise HTTPException(...)` still returns its real status code unchanged), logs the full
  traceback server-side via `logger.exception()`, and returns clean `{"detail": "Internal server error."}`
  JSON to the client instead of a raw traceback or a dropped connection. Verified directly: monkeypatched
  `build_reasoning()` to raise an arbitrary `RuntimeError` mid-request and confirmed the client got a
  clean 500 while the real traceback appeared in the server log.
- Added an explicit Bangladesh bounding-box check (20.0-27.0N, 87.5-93.0E, margin around the FFWC
  report's own 20.5-26.67N/88.03-92.67E) on resolved lat/lon. Not a crash risk on its own --
  `nearest_district`/`get_nearest_station_reading` are plain haversine searches that return SOMETHING no
  matter how far away the query point is -- but silently snapping a coordinate in Delhi or the middle of
  the Atlantic to "the nearest Bangladesh station" would produce a confident-looking, meaningless
  prediction instead of an honest error. Verified both a clearly-nonsensical point (0,0) and a
  plausible-but-wrong one (Delhi, 28.61N/77.21E) now return a clear 400 instead of a fake prediction.

**Full regression pass** (11 cases via `TestClient`, all passing after the changes): health, districts,
predict by lat/lon, predict by district/upazila, no-params (400), unknown district (404), both
out-of-bounds cases (400), out-of-pydantic-range lat (422), and both a station with upstream chain+
reference links (ME02) and one with neither (CH01) -- confirming the hardening didn't regress any
previously-working path.

## 22. Live validation against FFWC's real map, and a real one-day-stale bug found by doing it

**Decision (2026-08-09)**: user asked to check the live model against FFWC's actual current station
status. The earlier "silently swap in FFWC's answer" idea (this same session) was declined as
deceptive-by-design; this is the legitimate version -- read what FFWC's public map already shows a
human visitor, run our model for the matching real stations, compare openly.

**How the FFWC side was read**: `www.ffwc.gov.bd/app/home`'s live map (via browser automation, not by
scripting their API -- see the earlier decision in this session not to reverse-engineer their "Invalid
Security Header" anti-scraping check). Used the site's own "Station Information" panel (Normal(116) /
Warning(9) / Flood(2) tabs + station search) to get the authoritative current list, not just marker
colors. At the time checked: **Warning** = Dalia, Haripur, Sariakandi, Jagannathganj, Kanaighat,
Amalshid, Sheola, Markuli, Kalmakanda. **Flood** = Mongla, Fenchuganj. Everything else = Normal.
Confirmed real BWDB station codes/names for nearly all 30 of our stations exist and match cleanly
(e.g. real "Teesta at Dalia" = `SW291.5R`, current 51.83m vs danger 52.15m, trend falling) -- useful
independent confirmation that `stations.py`'s station choices track the real network well.

**Real bug found while building the comparison, not by inspection**: the user asked directly whether
live predictions were using recent AND today's data. Checking precisely (not assuming) found that
`live_features.py`'s Open-Meteo calls never passed `forecast_days`, so it defaulted to `0` --
confirmed directly via curl that Open-Meteo's `past_days` window under that default ends **yesterday**,
not today. Every live prediction made since Part 5 shipped earlier this session (including the first
pass of this very comparison) was silently built on data one full day stale: `lag1d` was really
`lag2d`, "today's" rainfall/soil-moisture/discharge was actually yesterday's. Fixed with
`forecast_days=1` (confirmed via curl this is exactly what adds today, with a real blended
observed-so-far/nowcast value, not a multi-day-ahead forecast). Verified the fix directly: the
station-weather series now genuinely ends on the actual current date, not the day before.

**Related, but NOT fixed by the above -- a disclosed capability gap, not a bug**: even with today's
data now included, the model has **zero visibility into forecast rain**. `FloodGBMModel` was trained
purely on backward-looking lag/rolling features (see `feature_schema.json`) -- there is no
forecast-rainfall feature to feed even though Open-Meteo can supply one (`forecast_days` up to several
days ahead). For a model whose whole job is predicting 24-72h ahead, not using an already-available
rain forecast as a leading signal is a real, meaningful gap -- surfaced to the user, not silently
left. Adding it would mean a new feature in `build_features.py` AND a retrain (training data would need
a forecast-equivalent, which is a real practical wrinkle: archived historical forecasts aren't
available the same way archived *observations* are), not a live-serving-only change like the fix above.

**Honest comparison result (re-run after the fix, not the stale first pass)**:

| Station | FFWC live status | Model 24h / 48h / 72h |
|---|---|---|
| TE01 (Dalia) | Warning, falling | high / high / high |
| SW93 (Sariakandi) | Warning | moderate / high / high |
| KU02 (Amalshid) | Warning | high / high / high |
| SW99 (Sirajganj) | Normal (Jagannathganj next door: Warning) | high / high / high |
| KU01 (Sherpur-Sylhet) | Normal (Fenchuganj next door: Flood) | high / high / high |
| CO03 (Bagerhat) | Normal (Mongla, same district: Flood) | high / high / high |
| SW90 (Bahadurabad) | Normal | high / high / high |
| SW174 (Sylhet) | Normal | high / high / high |
| SW267 (Sunamganj) | Normal | high / high / high |

Agrees directionally on every station FFWC flags Warning/Flood (or its immediate neighbor). Disagrees
on 3 stations FFWC calls flat Normal (Bahadurabad, Sylhet, Sunamganj) where the model still says "high"
on all 3 horizons. Not spun as either "works great" or "broken": these measure different things (FFWC =
current level vs. danger level right now; the model = probability of crossing it within 24-72h, which
can legitimately diverge), and the broad "high" pattern during real, heavy August monsoon rain is
consistent with the ALREADY-DISCLOSED low precision at the 85%-recall operating threshold (§14,
13-18%) -- this is that known tradeoff showing up in live conditions, not a new surprise.

## 23. Pivot: a discharge-regression model, built ALONGSIDE the classifier (not replacing it)

**Decision (2026-08-09)**: user's final-year project pairs an IoT pond system (pH/turbidity/temp/
ultrasonic level/soil sensors + 2 motors) with this flood model. Given the classifier's disclosed
precision ceiling (13-18% at 85% recall — a real, structural consequence of rare/sparse positive
labels, not a bug), discussed pivot options. Landed on: **predict future river discharge (m³/s)
instead of binary flood/no-flood** — a fundamentally more tractable target (discharge has near-
continuous coverage since ~1997, ~324k usable rows vs. ~101k labelable rows for the classifier, no
rare-event imbalance at all) — built as a genuinely SEPARATE model so the classifier stays available
as a known-good fallback, per the user's explicit ask ("as a new model so the old one still stays").

**Built, fully isolated from the classifier at every layer**:
- `train/build_regression_targets.py` — reads the classifier's already-engineered features
  (`data/features/2026-08-07c/`, untouched) and writes a SEPARATE copy
  (`data/features/2026-08-07c-discharge-regression/`) with 3 new forward-shifted targets added
  (`discharge_target_24h/48h/72h` = `river_discharge_m3s.shift(-1/-2/-3)` per station). No accessible-
  window/regime masking needed the way the classifier's GFMS label required (SS12) — discharge has no
  "unknown because unchecked" state, just present-or-NaN.
- `train/train_regression_model.py` — 3 LightGBM regressors, writes to a SEPARATE model directory
  (`backend/models/2026-08-07c-discharge-regression/`) — `backend/models/2026-08-07c/` (the classifier)
  was verified untouched (file mtimes checked directly, not assumed).
- **log1p target transform**: station discharge spans ~5 orders of magnitude (checked directly:
  ~2 m³/s mean at ME03/Dhaka's Buriganga vs. ~39,000 m³/s at ME01's Padma-Meghna confluence) — a
  plain L2 objective on raw m³/s would be dominated entirely by the largest rivers' squared error.
  log1p makes the loss behave like a relative error across every station's own scale; predictions are
  back-transformed (expm1, clipped at 0) for real-unit reporting.
- **A persistence baseline reported alongside every metric** — discharge is highly autocorrelated
  day-to-day, so a naive "tomorrow = today" baseline is a real comparison point, not an afterthought
  (same "always compare against a naive baseline" discipline as SS10/SS14/SS18, applied here from the
  start rather than added after the fact).

**Honest results**:

| Horizon | Model MAE | Persistence MAE | MAE improvement over persistence | R² |
|---|---|---|---|---|
| 24h | 321 m³/s | 361 m³/s | **+11.1%** | 0.996 |
| 48h | 534 m³/s | 675 m³/s | **+20.8%** | 0.989 |
| 72h | 672 m³/s | 937 m³/s | **+28.2%** | 0.983 |

**Reading this honestly, not just quoting the good numbers**: R² of 0.98-0.996 looks spectacular but
is significantly inflated by the ~5-orders-of-magnitude scale spread across stations — a model that
just gets each station's rough scale right already scores very high R² on this kind of dataset, so R²
alone overstates real skill here. The number that actually matters is the **persistence comparison**:
the model beats naive "no change" by a real, and growing, margin — 11% better at 24h, up to 28% better
at 72h. That growing gap is the right shape for a genuinely useful leading-indicator model (persistence
degrades as the horizon lengthens; a model with real skill should pull further ahead of it as it does,
which is exactly what happened). MAPE (1500-3000%) is reported in `metrics.json` but is a known-
distorted metric here, not a real finding — several small rivers (ME03 mean ~2.4 m³/s) have near-zero
true values that blow up any percentage-based metric; not worth quoting without that caveat attached.
SHAP confirms the top driver is today's own discharge (expected, real physics — genuine
autocorrelation, not a leak, since it's information legitimately available at prediction time), followed
by yesterday's discharge, station identity, then rainfall — a physically sensible ranking.

**Not yet decided**: whether/how this feeds the live API or the user's IoT motors. Deliberately left
open per the user's own framing — evaluate the new model on its own merits first, decide what to do
with it after. Candidate next steps if pursued: convert the raw discharge forecast into a station-
relative "how unusual is this for this river, this time of year" signal (a percentile/z-score against
that station's own historical distribution) so the number is interpretable across wildly different
river scales, and/or feed it as the "regional trend" half of a combined-condition trigger alongside
the user's own local ultrasonic sensor (discussed this session, not yet built).

## Open items / future decisions to log here

- **Add a forecast-rainfall feature and retrain** (§22): the model currently has zero visibility into
  already-issued rain forecasts for the 24-72h it's predicting over — a real, disclosed gap, not yet
  acted on. Would need a new `build_features.py` feature AND a retrain; the real wrinkle is that
  archived *historical forecasts* (what a forecast said in the past, not what actually happened) aren't
  available the same way archived observations are, so this needs real investigation before committing
  to it, not just a quick add.
- Whether to pursue the `api.ffwc.gov.bd` registration for live station water-level enrichment — checked
  again 2026-08-09 (user found `ffwc.gov.bd/app/home`, same underlying API): still gated behind manual
  email registration (`api.support@bwdb.gov.bd`), no self-service signup found. Relevant to Part 5
  (live-serving), not training data — not required for a working model, but the user wants this
  remembered for when Part 5 starts.
- MCDWD backfill scope beyond the current `gfms-overlap` window — deferred pending §5's conclusion (which
  already resolved the label question), now lower priority / may not be needed at all.
- Whether/how to eventually attempt storm-surge modeling (§9) as a follow-on phase.
- Whether to empirically estimate upstream travel-time lags (both `UPSTREAM_CHAIN` and the new
  `UPSTREAM_REFERENCE_CHAIN`, §18) via cross-correlation of upstream/downstream discharge series, instead
  of the current hardcoded engineering-estimate lags (§11/§18).
- Remaining unexplored, lower priority: EM-DAT (likely redundant with DFO's era coverage,
  registration-gated), DAHITI/Hydroweb river altimetry (discharge-feature-only, ~5 years pre-1997),
  NOAA-GMU VIIRS flood product (free, no registration, but optical — same monsoon-cloud limitation as
  everything except GFM), JRC Global Surface Water (same optical limitation, investigated in §17), BIWTA
  coastal tide gauges/PSMSL (real and free, but monthly-mean sea level — a slow-moving baseline, not a
  flood *event* label), ICIMOD Regional Database System (a few Sentinel-1 flood maps exist, practicality
  unverified — JS-rendered SPA, couldn't probe file sizes the way UNOSAT/DFO were checked), World Bank
  Data Catalog's Dhaka flood dataset (would only help the ME03 station).
- A GitHub-hosted "34 Bangladesh stations, 1980-2020, flood index" dataset was investigated and
  **rejected** (§17) — its label column turned out to be a monsoon-calendar artifact, not a real flood
  indicator. Recorded here so it isn't reconsidered without re-deriving why it failed.
