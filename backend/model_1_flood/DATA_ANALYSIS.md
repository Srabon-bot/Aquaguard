# Data Analysis — `new_approach` (Abdullah et al., MDPI Hydrology)

**Source:** Multi-Satellite High-Frequency Monitoring of Water Levels, Discharge, and
Floodplain Dynamics in the Brahmaputra River, Bangladesh — Faruque Abdullah et al.
(submitted to MDPI Hydrology).

**Location:** `new_models/new_approach/`
**Scope:** 18 files — 9 CSV, 8 GeoTIFF, 1 README.

---

## 1. Headline

This dataset **fixes the central weakness of the earlier AquaGuard work.**

The previous project (`new_models/RESULTS.md`) had to derive its water-level target
from GloFAS discharge using a rating curve I calibrated myself, with a stated
accuracy floor of roughly ±0.5 m. That made the headline result indefensible — an
RMSE of 0.08 m was measuring how well the model reproduced GloFAS through my own
curve, not real gauge skill.

`Own_Rated_Q_2008-2022_Bahadurabad.csv` is **in-situ gauge data** at the same station
(Bahadurabad), passed through the paper authors' own rating curve. That is a
materially stronger foundation, and it is directly usable.

---

## 2. File inventory

| File | Rows | Period | What it is |
|---|---|---|---|
| `Q/Own_Rated_Q_2008-2022_Bahadurabad.csv` | 5,479 | 2008-01-01 → 2022-12-31 | **Daily in-situ WL + rated discharge** |
| `WL/WL-from-Altimetry_Bahadurabad_2008-2022.csv` | 631 | 2008-07-21 → 2022-12-30 | JASON-2/3 + Sentinel-3A/3B satellite WL |
| `WL/WL-from-S1_S2-Bahadurabad_2016-2022.csv` | 349 | 2016-01-01 → 2022-12-30 | Sentinel-1/2 width → inverse rating curve |
| `WL/COMBINED-WL-...csv` | 925 | 2008–2022 | Merge of the two above |
| `Q/Q-from-Altimetry_2008-2022_Bahadurabad.csv` | 631 | 2008–2022 | Altimetry WL → discharge |
| `Q/Q-from-S1_S2_2016-2022_Bahadurabad.csv` | 349 | 2016–2022 | Sentinel width → discharge |
| `Q/COMBINED_Q-...csv` | 925 | 2008–2022 | Merge of the two above |
| `Threshold/S1-TH-timeseries.csv` | 365 | 2016–2022 | Otsu threshold, S1 land/water split |
| `Threshold/Width-TH_timeseries_position01_...csv` | 365 | 2016–2022 | River width + threshold |
| `FPDEM/2016…2022.tif` (7 files) | — | 2016–2022 | Annual waterline-derived DEM, 90 m |
| `FPDEM/FPDEM_16-22.tif` | — | 2016–2022 | All waterlines combined |

**Recommended primary source: `Own_Rated_Q_2008-2022_Bahadurabad.csv`.** Everything
else is either a sparse cross-check or out of scope for a level-forecast model.

---

## 3. The primary dataset in detail

```
Date,WL,Q_R
2008-01-01,13.88,7430.13
2008-01-02,13.86,7370.00
2008-01-03,13.85,7340.08
```

| Property | Value |
|---|---|
| Rows | 5,479 |
| Date coverage | 2008-01-01 → 2022-12-31 |
| Missing calendar days | **0** (fully continuous) |
| Null values | 335 (6.1%) in `WL` and `Q_R` |
| Gaps > 7 days | 0 |
| WL range | 11.68 → **21.16 m** |
| Q range | 2,810 → 79,902 m³/s |
| WL mean / median | 15.52 / 15.10 m |
| Q mean / median | 18,806 / 11,923 m³/s |

### Why continuity matters

A fully unbroken 15-year daily record is unusual for river gauge data, where
monsoon-season instrument failures are normal. This series has no gaps longer than
a week and no missing dates at all, which makes it safe to use lag features without
accidentally creating false "7-day gap" features.

### Exceedance counts against official FFWC thresholds

Bahadurabad, FFWC station `SW46.9L`, Danger Level **19.05 m**, Recorded Highest
Water Level **20.63 m**, extreme trigger DL + 0.85 = **19.90 m**.

| Threshold | Days | Share of series |
|---|---|---|
| ≥ Danger Level 19.05 m | **467** | 9.1% |
| ≥ Extreme 19.90 m | 93 | 1.8% |
| ≥ RHWL 20.63 m | 16 | 0.3% |
| Peak (2019-07-18) | 21.16 m | |

Danger-level exceedance days by year:

| Year | Days ≥ DL | Year | Days ≥ DL |
|---|---|---|---|
| 2008 | 33 | 2016 | 33 |
| 2009 | 12 | 2017 | 36 |
| 2010 | **69** | 2018 | 23 |
| 2011 | 22 | 2019 | 21 |
| 2012 | 59 | 2020 | **70** |
| 2013 | 26 | 2021 | 14 |
| 2014 | 27 | 2022 | 7 |
| 2015 | 15 | | |

**467 exceedance days is the single most valuable property of this dataset.** The
earlier project had only 43, all derived from GloFAS. Any hit-rate, miss-rate or
false-alarm statistic computed here will rest on a sample large enough to be
statistically meaningful, and every year contains events, so a chronological split
will not accidentally leave a test period without floods.

---

## 4. Validation of the satellite series against the gauge

Both altimetry series were joined to the in-situ gauge on matching dates:

| Series | Overlap | Bias | MAE | RMSE | Correlation |
|---|---|---|---|---|---|
| Altimetry (JASON/Sentinel-3) | 631 days | **0.000 m** | **0.355 m** | 0.528 m | **0.9764** |
| Sentinel-1/2 | 349 days | +0.106 m | 0.691 m | 0.889 m | 0.9389 |

The altimetry series is unbiased and correlates at 0.976 with the gauge. That is a
credible independent confirmation that the authors' rating curve is sound — the
satellite measurements, derived by a completely different method, land on the same
water levels.

**But note the sampling rate.** Altimetry points are ~8.4 days apart on average
(range 1–20 days). Sentinel-1/2 points are similarly sparse. Neither is dense
enough to train a daily model on. Their correct use is as an independent check on
the rating curve during flood peaks, particularly on days where the in-situ record
is null.

---

## 5. Autocorrelation structure and what it implies

| Lag | Autocorrelation |
|---|---|
| 1 day | **0.9976** |
| 2 days | 0.9929 |
| 3 days | 0.9869 |
| 7 days | 0.9590 |
| 30 days | 0.7721 |
| 365 days | 0.6635 |

Two consequences:

1. **Persistence is a strong baseline.** At lag 1 the series is almost perfectly
   autocorrelated. Any model must beat a one-step naive forecast to demonstrate
   anything, and that bar is high. Reporting RMSE without a persistence comparison
   would be meaningless.
2. **Real skill extends well past 24 hours.** Autocorrelation stays above 0.95 out
   to 7 days. A 3-day and 7-day forecast are genuinely feasible, and a lead-time
   sweep showing where skill collapses is a stronger result structure than a single
   24-hour number.

Seasonal naive (same day last year) fails badly — RMSE ~1.99 m against ~0.17 m for
one-step naive. There is no useful year-on-year recurrence at daily resolution.

---

## 6. Quick skill test on real gauge data

Water level at t+24 h, lag-based features (`lag1…lag30`, day-over-day changes,
`q_lag1`, annual harmonics). Chronological split: train 2008–2016 (3,427 rows),
test 2017–2022 (735 rows).

| Model | RMSE (m) | MAE (m) | R² |
|---|---|---|---|
| Persistence | 0.285 | 0.186 | 0.9848 |
| **LinearRegression** | **0.109** | **0.062** | **0.9978** |
| RandomForest | 0.145 | 0.090 | 0.9961 |

**LinearRegression reduces RMSE by 62% against persistence, on real observed data.**

This is a genuine result. There is no GloFAS in the loop and no self-consistency
inflation, because the target is the authors' gauge-derived series and the
predictors are its own lags.

**Important caveat on interpretation.** Feature importances were almost entirely
concentated: `lag1` 0.52 and `q_lag1` 0.47, with every other feature below 0.01.
Roughly 99% of the predictive signal is yesterday's state. The model is
forecasting from persistence plus a little rate-of-change information. That is
perfectly legitimate for a 24-hour forecast, but it means:

- the model is not learning hydrology, it is learning a damped persistence
- explanations based on rainfall or catchment behaviour would not be honest
- if the gauge reading is wrong, the forecast is wrong

Also note LinearRegression beating RandomForest here, the opposite of the earlier
GloFAS-based project. With a target this smooth and this autocorrelated, a linear
model has less room to overfit than trees do.

---

## 7. Models that can be built on this

### 7.1 Water level forecast, t+24 h (direct replacement)

Target `WL.shift(-1)`. Demonstrated above at RMSE 0.109 m against real gauge data.
This is the model the project should lead with, because unlike the earlier version
the accuracy claim is defensible.

### 7.2 Lead-time sweep

Repeat for t+1, +3, +7, +14 days and report where skill collapses. Autocorrelation
says +7 days should retain meaningful skill (0.959). A single table showing RMSE
against lead time is more informative than one 24-hour result.

### 7.3 Discharge forecast

Identical setup targeting `Q_R` instead of `WL`. Uses the same 5,479-day record.

### 7.4 Flood event classification

Label each day by FFWC threshold:

| Label | Rule | Positives |
|---|---|---|
| NORMAL | < 19.05 m | ~4,677 |
| WARNING | 19.05–19.90 m | 374 |
| SEVERE | 19.90–20.63 m | 77 |
| EXTREME | ≥ 20.63 m | 16 |

467 positives across 15 years is enough to train an imbalanced classifier and report
genuine precision-recall and confusion-matrix numbers, which the earlier project
could not do with 43 derived events.

### 7.5 Threshold tuning for the alert system

The `glofas_alerts` pipeline selects WARNING at p95 by default. With real exceedance
labels this becomes an empirical choice instead of an assumption — sweep the
percentile, measure hits, misses and false alarms against actual 19.05 m crossings,
and pick the operating point. This directly satisfies the "tune once" step in that
plan with real evidence rather than a proxy.

### 7.6 Validate the GloFAS pipeline

This is the highest-value use of the dataset.

The `glofas_alerts` validation was run in **synthetic mode** — GloFAS p95 compared
against GloFAS p95 — which necessarily returns a hit rate of 1.0 and proves nothing
about skill. With this gauge series the comparison can be made honestly for
Bahadurabad: GloFAS threshold crossings against genuine 19.05 m exceedances.

Even one station done properly converts that pipeline from unvalidated to measured.
That is worth more than a tenth station in the alert CSV.

---

## 8. What not to use

| Item | Reason |
|---|---|
| `FPDEM/*.tif` (8 files, 36 MB) | Waterline DEMs, annual 2016–2022. Only relevant to a floodplain inundation component. Scope creep. |
| `Threshold/S1-TH-timeseries.csv` | Otsu thresholds for SAR land/water segmentation. Narrow-band radar classification detail, not useful for level forecasting. |
| `Threshold/Width-TH_timeseries_position01` | River width from Sentinel-1, 365 rows. Could support a width-based feature, but adds a weak predictor for real effort. |
| `COMBINED_*` files | Straight merges. Derive them on load if needed. |
| Altimetry as a training target | ~8-day sampling. Too sparse. Use for cross-validation of the rating curve only. |

---

## 9. Limitations to state in any write-up

1. **The levels are still rating-curve derived**, just by the paper's authors rather
   than by this project. That curve is better documented and independently
   cross-validated by altimetry (MAE 0.355 m), but it remains a curve, not a raw
   sensor trace. Sub-decimetre claims should still be framed carefully.
2. **Single station.** Everything is Bahadurabad. No spatial transfer is possible,
   and the `glofas_alerts` pipeline's other six stations remain unvalidated.
3. **6.1% nulls** in the primary series. Needs explicit handling, not silent
   interpolation.
4. **2016–2022 altimetry overlap only** for the Sentinel series, so the independent
   cross-check is thinner there.
5. **Dominance of `lag1`** means the model has limited explanatory depth. Do not
   claim rainfall-driven or catchment-driven skill the features do not support.

---

## 10. Recommendation

Use `Own_Rated_Q_2008-2022_Bahadurabad.csv` as the single primary dataset for a
revised water-level forecasting model. Lead with the +24 h result and a lead-time
sweep, validated against persistence, on genuinely observed data.

Then use the same series to validate the GloFAS alert pipeline at Bahadurabad,
replacing the synthetic result with a measured hit rate and false-alarm ratio.

Retain the altimetry series as an independent check on the rating curve at flood
peaks, where it is most informative and in-situ data is most likely missing.