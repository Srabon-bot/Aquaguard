# AquaGuard Defense Strategy
**The Regional Pilot Approach**

This document outlines the presentation strategy, narrative framing, and anticipated Q&A for defending the AquaGuard project before the academic board.

---

## 1. Core Narrative: "The Regional Pilot"
Do not present Model 1 as an "unfinished national model." Present it deliberately as a **High-Fidelity Regional Pilot Deployment**.

* **The Problem:** Flooding in Bangladesh is geographically diverse. The Surma basin experiences 24-hour flash floods, while the Jamuna basin experiences slow-rising 7-day monsoon floods. A single "national model" would be inaccurate.
* **The Solution:** We built a highly accurate, station-specific pipeline tailored to the **Jamuna River (Bahadurabad Transit)** — one of the most critical and vulnerable aquaculture regions in the country.
* **The Scale Argument:** The architecture (Data Ingestion → Feature Engineering → ML → FastAPI → IoT Dashboard) is proven. Adding new rivers simply requires plugging a new CSV into the pipeline. 

---

## 2. PRD Alignment Checklist
Remind the board that the project explicitly satisfies the required PRD:
* ✅ **Continuous Prediction:** We predict exact water levels (m), not a vague "flood/no-flood" binary. This allows farmers to calculate exactly how high to raise their embankments.
* ✅ **Model Evaluation:** We evaluated Baselines, Linear Regression, Random Forest, and XGBoost (10 models total across 4 horizons).
* ✅ **Strict Validation:** We used Leave-One-Year-Out (LOYO) cross-validation to strictly prevent time-series data leakage.
* ✅ **Actionable UI:** We integrated bilingual (English/Bengali) actionable advice tailored specifically to fish farming.

---

## 3. The 3 ML Models (Key Talking Points)

### Model 1: River Water-Level Forecasting
* **The Finding:** Linear Regression beat XGBoost for short horizons (1–3 days). 
* **The Defense:** Tree-based models (RF/XGB) cannot extrapolate beyond the maximum value in their training set. When a record-breaking flood hits, they flatten out. Linear models extrapolate the extreme trend correctly.
* **The Honest Limitation:** ML models smooth their predictions, which causes them to miss *more* peak flood days than a naive baseline. We mitigated this by setting the UI warning trigger 0.5m below the official danger line.

### Model 2: Pond TDS Forecasting (+60 min)
* **The Finding:** The Persistence Baseline (R²: 0.94) vastly outperformed XGBoost (R²: 0.71).
* **The Defense:** Over a short 60-minute window, pond chemistry drifts very slowly. Complex algorithms over-complicated the math and fit to sensor noise. We followed the data, not algorithm hype.

### Model 3: Sensor Anomaly Detection
* **The Finding:** Isolation Forest detected 67 anomalies vs. 55 by standard Z-scores.
* **The Defense:** Z-scores only catch univariate anomalies (e.g., pH is extremely high). Isolation Forests catch *multivariate* anomalies (e.g., pH is 8.2 and Temp is 32°C — neither is extreme alone, but together they cause toxic ammonia spikes). 

---

## 4. Anticipated Q&A

**Q: Why did you only cover Bahadurabad and not Sylhet (Surma basin)?**
> *Answer:* We prioritized accuracy over geographical coverage for the pilot. Sylhet suffers from flash floods which require hourly data, while the Jamuna suffers from monsoon floods which require daily data. The pipeline is built so Sylhet can be added in Phase 2 by simply swapping the input dataset.

**Q: Why didn't you use standard K-Fold Cross Validation?**
> *Answer:* Standard K-Fold randomly shuffles data. If we shuffle time-series data, a data point from December could end up in the training set, while November is in the test set. The model would "look into the future." LOYO (Leave-One-Year-Out) trains on block years (e.g., 2010-2020) and tests on a strictly unseen future year (e.g., 2021). 

**Q: Does an 'Anomaly' in Model 3 mean the fish are dead?**
> *Answer:* No. The model avoids making biological claims. An anomaly simply means: "The current multivariate sensor pattern differs substantially from the patterns considered normal by historical standards." It acts as an early-warning decision-support signal for the farmer to manually inspect the pond.

**Q: Why did you power the pH sensor at 3.3V when all tutorials say 5V?**
> *Answer:* The ESP32's ADC pins (like GPIO 34) have no over-voltage protection and burn out above 3.3V. Powering the sensor at 5V risks the analog output exceeding 3.3V. We powered it at 3.3V to physically protect the board, and compensated for the altered voltage range using our custom 2-point software calibration.

---

## 5. Live Demo Strategy

1. **Start at the Dashboard:** Show the live sensor tiles and explain how they read from Firebase.
2. **Scroll to Model 1:** Show the 14-day hydrograph and read the Bengali advice out loud to prove local relevance.
3. **The "Simulate Spike" Button:** When explaining Model 3, click the `Simulate Sensor Spike` button. The card will instantly turn RED and flash `ANOMALY DETECTED`. Defense boards love interactive features that prove the machine learning is running live!
