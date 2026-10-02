# AquaGuard: Project Report
**Bangladesh Flood Early Warning & IoT Pond Management System**
*Final Project Report — October 2026*

---

## 1. Executive Summary

AquaGuard is an end-to-end hardware and software ecosystem designed to protect aquaculture (fish farming) in Bangladesh from sudden environmental shocks. The system bridges upstream hydrometeorological forecasting with localized IoT pond management.

The project delivers three core components:
1. **IoT Hardware:** An ESP32-based sensor suite measuring pond water quality and level, with automated pumps and feeders.
2. **Web Dashboard:** A farmer-facing interface showing live sensor telemetry, historical analytics, and bilingual protective advice.
3. **Machine Learning AI:** Three predictive models forecasting river flooding, pond water quality degradation, and invisible sensor anomalies.

---

## 2. Hardware Subsystem (IoT Edge Device)

The physical device was built incrementally across 7 strict hardware revisions to ensure component isolation and reliability.

### 2.1 Components
- **Microcontroller:** ESP32 (WROOM-32)
- **Sensors:** 
  - pH Probe (PH4502C) via GPIO 34 (3.3V logic)
  - Ultrasonic Rangefinder (HC-SR04) via GPIO 5/18 (5V logic, stepped down via 1kΩ/2kΩ divider)
  - Thermistor (NTC) via GPIO 32 (passive divider)
  - TDS Probe via GPIO 35 (3.3V logic)
- **Actuators:**
  - 2x Submersible Water Pumps controlled via a 2-channel 5V active-LOW relay (GPIO 25, 26)
  - 1x Servo Motor (feeder/gate) via GPIO 13

### 2.2 Calibration & Connectivity
Unlike standard tutorials, the pH sensor was powered safely at 3.3V to prevent ESP32 pin burnout, and calibrated using a custom two-point software calibration sequence (Vinegar pH 2.4 and Baking Soda pH 8.3). The calibration is stored in the ESP32's non-volatile flash memory (NVS) and can be triggered directly from the web dashboard.
The device pushes telemetry every 5 minutes to a **Firebase Realtime Database**.

---

## 3. Web Dashboard (Frontend)

The frontend is a lightweight, zero-build-step Vanilla HTML/JS/CSS application designed for low-bandwidth environments.

### 3.1 Features
- **Live Telemetry:** Real-time reads from Firebase `/sensor/*`.
- **Remote Actuation:** Toggle buttons for remote pump control writing to Firebase `/pumps/*`.
- **Analytics Engine:** `analytics.html` buckets historical Firebase `/history` data into daily, weekly, and monthly min/max/average charts.
- **pH Calibration Wizard:** A browser-based interface to perform 2-point pH calibration wirelessly.
- **Bilingual Actionable Advice:** Generates English and Bengali instructions for farmers (e.g., "Raise net heights," "Harvest marketable fish") based on AI predictions.

---

## 4. Machine Learning Subsystem

The AI layer was rebuilt from scratch to satisfy the final PRD, shifting from unhelpful binary classifiers (Flood/No-Flood) to continuous regression and unsupervised anomaly detection.

### 4.1 Model 1: River Water-Level Forecaster (Regional Pilot)
- **Target:** Predict Jamuna River water levels (Bahadurabad Transit) 1 to 14 days ahead.
- **Data:** BWDB historical gauge data + ERA5 upstream catchment rainfall.
- **Validation:** Strict Leave-One-Year-Out (LOYO) cross-validation to prevent time-series data leakage.
- **Result:** Linear Regression (RMSE: 0.075m, R²: 0.998) outperformed Random Forest and XGBoost.
- **Critical Finding:** Tree-based models (RF/XGBoost) inherently cannot extrapolate beyond the maximum value seen in training. During unprecedented flood peaks, they flatten out. Linear Regression successfully extrapolates these extremes.
- **Safety Buffer:** Evaluation revealed that *all* ML models missed more flood events than a naive persistence baseline due to peak-smoothing. The system mitigates this by triggering warnings 0.3m–0.5m *before* the official 19.05m Danger Level.

### 4.2 Model 2: Pond TDS Forecaster
- **Target:** Predict Total Dissolved Solids (TDS) 60 minutes into the future to preempt toxic fertilizer runoff spikes.
- **Data:** 1,327 continuous hourly IoT records (2023). Features included 6-hour rolling means and lag windows (t-1 to t-12).
- **Result:** The Persistence Baseline (R²: 0.942) and Linear Regression (R²: 0.888) vastly outperformed XGBoost (R²: 0.711). Pond chemistry drifts slowly; complex tree models overfit to hardware noise within the 60-minute window.

### 4.3 Model 3: Sensor Anomaly Detector
- **Target:** Detect dangerous pond conditions without labeled training data.
- **Algorithm:** Isolation Forest (Unsupervised).
- **Features:** Absolute sensor values + rate-of-change deltas (ΔpH, ΔTDS, ΔTemp).
- **Result:** Detected 67 anomalies (vs. 55 by statistical Z-scores). Isolation Forests catch *multivariate* anomalies (e.g., a specific pH combined with a specific temperature that is deadly, even if neither crosses a danger threshold on its own).

---

## 5. System Deployment & Portability

The entire ML backend is unified under a single FastAPI server (`api_combined.py`). The system is 100% portable, utilizing relative pathing. The complete developer handoff package is stored in `new_models/new_approach/AquaGuard_Web_Bundle/`, allowing instant deployment on any machine with Python 3.9+.

---

## 6. Limitations & Future Work

1. **Hardware Integration Gap:** The final combined firmware (`AquaGuard_v2.ino`) is written but requires flashing to the physical ESP32.
2. **Live ML Bridging:** While Model 1 reads live FFWC API data, Models 2 and 3 currently infer on the historical test set. They need to be pointed to the live Firebase `/sensor` paths.
3. **Spatial Scale:** Model 1 is a regional pilot limited to the Jamuna River basin. Phase 2 must expand coverage to the Surma-Kushiyara (Sylhet) flash-flood basin.
4. **Alerting:** The SMS/WhatsApp automated alert engine remains unbuilt.
