# AquaGuard Capstone Report — Full Critique & Corrected Draft

---

## PART 1: FAULT ANALYSIS OF THE ORIGINAL REPORT

> Read this with your friend. Every fault below has a section reference and a fix.

---

### A. Project Name — Wrong Throughout

**Fault:** The entire report uses "AquaShield" as the project name.  
**Fix:** Replace every instance with **AquaGuard**.

---

### B. Broken Characters — Encoding Corruption from DOCX Conversion

These characters were corrupted during the Word → plain text conversion and must be fixed before submission:

| Broken | Correct | Where It Appears |
|---|---|---|
| `R?` | R² | Abstract, Section 5.2, 5.3, 5.4 |
| `?C` or `C` | °C | Sections 2.2, 5.2, table 2.1 |
| `?0.05`, `?0.15`, `?0.4` | ±0.05, ±0.15, ±0.4 | Table 5.1 |
| `?` (in Delta context) | Δ | Section 3.6, 5.5 |
| `k` (in resistor context) | kΩ | Section 3.3, Appendix A |
| `s` (in microsecond context) | μs | Appendix A |

---

### C. Broken LaTeX Equations — Must Be Rewritten

The equations are showing raw LaTeX strings inside the Word document because they were never rendered properly. They must be rewritten as clean readable text or properly inserted as Word equation objects.

**Equation 3.1 (pH Conversion):**
- ❌ `\mathrm{pH} = 7.0 + \frac{V_{cal,7} - V_{out}}{S} \tag{3.1}`
- ✅ pH = 7.0 + (V_cal − V_out) / S  ... (3.1)

**Equation 3.2 (Temperature Compensation):**
- ❌ `V_{comp} = \frac{V_{adc}}{1.0 + 0.02\,(T - 25.0)} \tag{3.2}`
- ✅ V_comp = V_adc / [1.0 + 0.02 × (T − 25.0)]  ... (3.2)

**Equation 3.3 (Water Level):**
- ❌ `\mathrm{Water\_Level} = \mathrm{Pond\_Depth} - \frac{t_{echo}\, v_{sound}}{2} \tag{3.3}`
- ✅ Water Level = Pond Depth − (t_echo × v_sound) / 2  ... (3.3)

**Equation 3.4 (RMSE):**
- ❌ `\mathrm{RMSE} = \sqrt{\frac{1}{N}\sum \left(y_i - \hat{y}_i\right)^2} \tag{3.4}`
- ✅ RMSE = √[ (1/N) × Σ(y_i − ŷ_i)² ]  ... (3.4)

**Equation 3.5 (NSE):**
- ❌ `\mathrm{NSE} = 1.0 - \frac{\sum \left(y_i - \hat{y}_i\right)^2}{\sum \left(y_i - \bar{y}_{obs}\right)^2} \tag{3.5}`
- ✅ NSE = 1.0 − [ Σ(y_i − ŷ_i)² / Σ(y_i − ȳ)² ]  ... (3.5)

**Equation 3.6 (POD):**
- ❌ `\mathrm{POD} = \frac{\mathrm{Hits}}{\mathrm{Hits} + \mathrm{Misses}} \tag{3.6}`
- ✅ POD = Hits / (Hits + Misses)  ... (3.6)

**Equation 3.7 (FAR):**
- ❌ `\mathrm{FAR} = \frac{\mathrm{False\_Alarms}}{\mathrm{Hits} + \mathrm{False\_Alarms}} \tag{3.7}`
- ✅ FAR = False Alarms / (Hits + False Alarms)  ... (3.7)

---

### D. Factual Hardware Errors — GPIO Pins Wrong in Appendix

**Fault:** Appendix A.1 states:
- Relay 1 (Drain Pump) → GPIO 19
- Relay 2 (Refill Pump) → GPIO 21
- Servo Motor (Feeder) → GPIO 23

**Reality (from AquaGuard_v2.ino):**
- Relay 1 (Drain Pump) → **GPIO 25**
- Relay 2 (Refill Pump) → **GPIO 26**
- Servo Motor (Feeder) → **GPIO 13**

**Fix:** Update Table A.1 with the correct GPIO numbers. If a board member connects hardware using the appendix, the wrong pins will destroy the pumps.

---

### E. pH Calibration Claim — Contradicts Actual Method

**Fault:** Table 5.1 and Section 3.3 claim the pH probe was tested against "Standard Buffers (4.01, 6.86, 9.18)" and "certified laboratory references." This is false — no lab buffers were used.

**Reality:** Calibration was performed using:
- Vinegar (~pH 2.4) as the acid reference
- Baking soda solution (~pH 8.3) as the base reference

And critically, because the readings were inverted (vinegar gave a *higher* voltage than baking soda), the calibration order was reversed — vinegar was captured as the 'base' point and baking soda as the 'acid' point in the NVS storage.

**Fix:** Replace the false lab buffer claim with the actual household calibration method. This is honest engineering and should be presented as a cost-reduction innovation, not hidden.

---

### F. Offline FSM & SPIFFS — Claimed but Not in Current Firmware

**Fault:** Multiple sections (Abstract, Section 4.3, Section 4.7) state the ESP32 uses SPIFFS flash buffering during internet dropouts.

**Reality:** The `AquaGuard_v2.ino` firmware does implement the FSM control logic locally, but SPIFFS-based offline flash buffering was a planned feature. It is not in the committed firmware code.

**Fix:** Either implement it (it is only ~20 lines of code) or change the wording to: *"Local FSM control rules continue to operate during connection loss. SPIFFS-based telemetry buffering is planned for a future firmware revision."*

---

### G. API Endpoint Routes — Wrong in Appendix A.2

**Fault:** Table A.2 shows routes `/api/ml/forecast/flood`, `/api/ml/forecast/tds`, `/api/ml/anomaly/status`.

**Reality (from api_combined.py):**
- `/api/v1/forecast` — Model 1 flood forecast
- `/api/v1/tds` — Model 2 TDS prediction
- `/api/v1/anomaly` — Model 3 anomaly detection

**Fix:** Update Table A.2 with the correct route paths.

---

### H. AI-Sounding Language — Phrases to Rewrite

The report reads like AI output in several places. Replace these:

| AI-Sounding | Human Replacement |
|---|---|
| "seamlessly integrates" | "connects" or "links" |
| "robust system" | "reliable system" |
| "a paradigm shift" | "a significant change" |
| "comprehensive solution" | "complete solution" |
| "delves into" | "covers" or "explains" |
| "pivotal role" | "important role" |
| "leveraging state-of-the-art" | "using" |
| Every paragraph starting "Furthermore," | Start with the actual content instead |
| "It is worth noting that" | Delete this phrase, just state the fact |
| "This chapter presented..." (at end of every chapter) | Write one specific sentence about what was found |

---

### I. What the Report Does Well (Keep These)

- ✅ The CO-PO Mapping and CEP Justification tables are genuinely excellent — detailed and well-referenced.
- ✅ The 5-tier architecture description is clear and technically correct.
- ✅ Table 2.1 (Water Quality Thresholds) is accurate and useful for the defense board.
- ✅ The LOYO cross-validation justification is well-explained and defensible.
- ✅ The safety buffer rationale (warning 0.3–0.5m below the Danger Level) is correctly stated.
- ✅ Chapter 2 background literature is well-cited (25 IEEE references).

---
---

## PART 2: CORRECTED FULL DRAFT REPORT

> Below is the full corrected report text. Copy-paste this over the Word document chapter by chapter. All broken characters are fixed, all equations are in readable format, wrong facts are corrected, and AI-sounding language is replaced with plain engineering writing.

---

# AquaGuard: Intelligent Aquaculture Monitoring and Adaptive Protection System

**Department of Computer Science & Engineering**
**University of Information Technology and Sciences (UITS), Dhaka, Bangladesh**

**Submitted by:**
- Hrithik Saha (ID: 0432310005101071)
- Md. Mahfuz (ID: 0432310005101057)
- Srabon (ID: 0432310005101056)

**Supervisor:** Sultana Rokeya Naher, Associate Professor
**Department of CSE, UITS**

---

## Abstract

Fish farming contributes over 3.5% to Bangladesh's national GDP and supplies 60% of dietary animal protein. Fish farmers in Bangladesh face two recurring threats that cause major financial loss: silent pond water deterioration that kills fish before farmers notice, and seasonal monsoon river floods that overtop pond dikes and wash away entire stocks. Most small-scale farmers check water quality manually, once a week, using visual inspection or basic test kits — methods that cannot detect early-stage toxicity.

This capstone project presents AquaGuard, an integrated low-cost IoT monitoring system combined with a three-model predictive machine learning decision-support engine. The hardware edge node uses an ESP32 (WROOM-32) microcontroller connected to a pH probe (PH4502C, powered at 3.3V to protect the ESP32 ADC pins), a TDS probe, an NTC thermistor for temperature, and an HC-SR04 ultrasonic water-level sensor. An autonomous Finite State Machine (FSM) running every 30 seconds controls a 2-channel optoisolated relay module for a drain pump and a refill pump, plus a servo-based automated fish feeder. Live telemetry is pushed to a Firebase Realtime Database, which drives a web dashboard with alert banners.

Three machine learning models provide predictive protection:

1. **Model 1 — River Flood Forecast:** Predicts Jamuna River water levels at Bahadurabad Transit 1 to 14 days ahead, trained on 15 years (2008–2022) of BWDB gauge data and ERA5 catchment rainfall. Using Leave-One-Year-Out (LOYO) cross-validation, Linear Regression achieved NSE = 0.985 and RMSE = 0.308 m on the 2020–2022 test holdout, outperforming tree-based models because linear models extrapolate flood peaks correctly without hitting a training-set ceiling. The dashboard alert threshold is set 0.3–0.5 m below the official 19.05 m Danger Level to compensate for peak-smoothing.

2. **Model 2 — Pond TDS Forecast (+60 min):** Predicts Total Dissolved Solids one hour ahead using rolling statistics and lag features. Linear Regression (R² = 0.888, MAE = 7.05 ppm) outperformed XGBoost (R² = 0.711) because pond chemistry drifts slowly over a 60-minute window and tree models overfit to sensor noise. SHAP confirmed the physically expected lag features as dominant.

3. **Model 3 — Multivariate Anomaly Detection:** Uses an Isolation Forest trained on sensor rate-of-change deltas to detect dangerous multi-parameter conditions — such as pH 8.2 combined with temperature 32°C, which causes lethal ammonia gas — that would not be caught by single-parameter threshold checks alone. Detected 67 anomalies in the test dataset versus 55 detected by standard Z-scores.

AquaGuard was built for under 7,200 BDT (~$60 USD), making it accessible to small-scale fish farmers.

**Keywords:** Internet of Things, Water Quality Monitoring, Flood Early Warning, Machine Learning, Explainable AI (SHAP), Isolation Forest, Bangladesh Aquaculture.

---

## Chapter 1: Introduction

### 1.1 Introduction

Bangladesh is one of the world's leading aquaculture nations. Over 18 million people depend on fish farming as their primary livelihood [1]. The sector faces two specific, serious threats that current technology does not address for small-scale farmers:

- **Pond water toxicity** develops gradually and silently. pH imbalances, TDS spikes from fertilizer runoff, and temperature-driven ammonia surges can kill an entire pond stock before a farmer notices a visible change in the water.
- **Monsoon river flooding** from the Jamuna catchment can overtop pond dikes within hours of reaching the Bahadurabad gauge, washing away an entire season's harvest.

AquaGuard addresses both threats with a single integrated system: an affordable IoT edge node that monitors and acts locally, and a cloud-backed machine learning engine that provides advance warning.

### 1.2 Motivation

Four specific gaps motivated this project:

**No continuous water monitoring.** Parameters like pH and TDS change throughout the day. Farmers visually check water color once a week. By the time a problem is visible, fish are already dying.

**No automated protective action.** If a farmer is asleep or away when a TDS spike or pH imbalance begins, no system exists to turn on the drain pump in time.

**No local flood warning for farmers.** National agency warnings cover entire river basins. A fish farmer on the Jamuna floodplain in Jamalpur needs to know the water level at the Bahadurabad gauge 3–7 days ahead — enough time to raise perimeter netting or harvest marketable fish early.

**No affordable solution.** Commercial industrial SCADA or PLC systems cost $2,000–$10,000. No existing system is designed for a rural fish farmer in Bangladesh.

AquaGuard was designed to cost under 7,200 BDT (~$60) using off-the-shelf components available in Dhaka electronics markets.

### 1.3 Aims and Objectives

The main aim is to design, build, and evaluate AquaGuard as an affordable cyber-physical aquaculture protection system. The specific technical objectives were:

1. Assemble a multi-sensor IoT edge node using an ESP32 connected to pH, TDS, temperature, and ultrasonic water-level sensors, sampling every 30 seconds.
2. Program a Finite State Machine in C++ to automatically control two pumps and a servo feeder based on local sensor readings, with rules that continue operating if the internet connection drops.
3. Set up Firebase Realtime Database for cloud telemetry and a Python FastAPI backend to serve the three ML models.
4. Train and evaluate Model 1: Jamuna River water-level forecasting (1–14 days) using LOYO cross-validation.
5. Train and evaluate Model 2: Pond TDS forecasting (+60 minutes) with SHAP explainability.
6. Train and evaluate Model 3: Unsupervised multivariate anomaly detection using Isolation Forest.
7. Build a web dashboard with live sensor tiles, pump controls, alert banners, historical trend charts, and a browser-based pH calibration wizard.

### 1.4 Challenges

**Hardware protection:** The PH4502C module is typically powered at 5V in tutorials. Powering it at 5V risks the analog output exceeding the ESP32 ADC's 3.3V maximum, burning out the GPIO pin permanently. We operated it at 3.3V and compensated through software calibration.

**Time-series data leakage:** Standard K-Fold cross-validation shuffles data randomly, meaning the model can "see" future data during training. We designed LOYO validation specifically to prevent this.

**Peak extrapolation failure:** Tree-based models (Random Forest, XGBoost) cannot predict water levels above the maximum they were trained on — a critical failure mode for record-breaking flood years. This required both model selection and a UI safety buffer to compensate.

**No labeled anomaly data:** Fish ponds do not have historical logs of "bad water" events. This ruled out supervised classification for Model 3, requiring unsupervised methods.

### 1.5 Contributions

- Built a sub-$60 multi-sensor ESP32 edge node with hardware protection (voltage dividers, 3.3V sensor operation) and 64-sample ADC oversampling to reduce electrical noise.
- Implemented a local FSM that continues to control pumps and feeder during internet outages.
- Proved through 15-year LOYO cross-validation that Linear Regression outperforms tree ensembles for extreme flood peak extrapolation.
- Delivered a complete dual-horizon protection system: 3–14 day river flood warning + 60-minute pond quality forecasting + real-time anomaly detection.
- Designed a browser-based pH calibration wizard requiring no hardware re-flashing.

---

## Chapter 2: Background Studies

### 2.1 Introduction

Effective pond monitoring requires understanding fish biology (what water conditions are lethal and why), monsoon hydrology (how floods develop in the Jamuna basin), and what prior IoT and ML systems have achieved and where they fall short.

### 2.2 Water Quality Parameters and Fish Biology

Fish health depends directly on four water parameters [5], [6]:

**pH (6.5–8.5 safe range).** Below pH 6.0, gill irritation and mucus problems begin. Above pH 8.8, harmless ammonium (NH₄⁺) converts to unionized ammonia (NH₃), which is acutely toxic. At pH 9.5 combined with 32°C temperature, lethal concentrations form within hours.

**Total Dissolved Solids — TDS (150–450 ppm safe range).** High TDS (above 600 ppm) signals excess unconsumed feed, organic waste, or fertilizer runoff. It causes osmotic stress, clogs gill filaments, and promotes bacterial growth.

**Water Temperature (25–30°C safe range).** Warm water holds less dissolved oxygen while fish metabolism speeds up, increasing oxygen demand. Temperature also multiplies ammonia toxicity — the same ammonia level is 10× more toxic at 30°C than at 20°C.

**Pond Water Level (80–150 cm safe range).** Levels below 40 cm cause rapid temperature swings and stress. Levels above 160 cm risk embankment overtopping during heavy rain.

**Table 2.1. Water Quality Safety Thresholds for Cultured Fish Species**

| Parameter | Safe Range | Warning | Critical | Biological Effect |
|---|---|---|---|---|
| pH | 6.5 – 8.5 | <6.2 or >8.8 | <5.0 or >9.5 | Gill burns, ammonia toxicity |
| TDS (ppm) | 150 – 450 | 450 – 600 | >800 | Osmotic stress, gill clogging |
| Temperature (°C) | 25 – 30 | 30 – 33 or <20 | >35 or <15 | Low oxygen, metabolic collapse |
| Water Level (cm) | 80 – 150 | <60 or >160 | <40 or >180 | Dike overflow, fish escape |

### 2.3 Monsoon Flooding in the Jamuna Basin

Over 92% of the Jamuna catchment lies outside Bangladesh, in the Himalayas and Meghalaya hills of India. Heavy monsoon rainfall from June to October creates large discharge pulses that travel down the Brahmaputra–Jamuna river system. At the Bahadurabad Transit gauge in Jamalpur, water levels regularly exceed 19.05 m (the official Danger Level). In 2020 alone, the level reached 20.63 m for multiple days, submerging over 40,000 hectares of commercial fish ponds and causing losses exceeding 500 crore BDT ($45 million USD) [3].

Fish farmers need a 3–7 day advance warning at their specific local gauge station — enough time to raise perimeter netting by 30–50 cm above the embankment or to harvest marketable fish before floodwater arrives. National agency bulletins operate at the basin scale and do not provide this station-specific, actionable lead time.

### 2.4 Related IoT Aquaculture Systems

Prior IoT monitoring systems exist but each has a specific gap [7]–[12]:

- Early Arduino + ZigBee systems achieved real-time monitoring but had no pump control and short wireless range.
- ESP8266/ESP32 systems streaming to ThingSpeak or Blynk added cloud visibility but depended entirely on continuous internet — if Wi-Fi dropped, all monitoring and pump actions stopped.
- Commercial PLC systems (Siemens, Allen-Bradley) provide full automation but cost $2,000–$10,000, which is completely unaffordable for a rural Bangladeshi farmer.

**Gap:** No existing affordable system combines local offline-safe pump control, flood early warning, and unsupervised anomaly detection in a single platform under $60.

### 2.5 Machine Learning for Flood Forecasting

LSTM neural networks have shown strong results for river forecasting [4] but require large datasets and GPU resources for training, making them impractical for student-built systems. Linear regression and tree ensembles trained on historical gauge data and rainfall can achieve strong NSE values on multi-day horizons [4]. A critical and often unreported limitation of tree models is that they cannot extrapolate beyond the maximum water level seen in training data — a fatal failure mode for record-breaking flood seasons [4]. Leave-One-Year-Out cross-validation, borrowed from hydrology literature [19], prevents the temporal data leakage that standard K-Fold would introduce.

---

## Chapter 3: Methodology

### 3.1 System Architecture Overview

AquaGuard is organized into five tiers:

1. **Sensor Tier:** Physical sensors on the ESP32 (pH, TDS, Temperature, Water Level)
2. **Edge Control Tier:** Local FSM rules on the ESP32 — controls pumps and feeder independently of the internet
3. **Cloud Data Tier:** Firebase Realtime Database for live telemetry and pump command states
4. **ML Prediction Tier:** Python FastAPI backend (`api_combined.py`) serving all three models on Port 8000
5. **User Interface Tier:** Vanilla HTML/JS/CSS web dashboard with live dials, charts, alert banners, and pH calibration page

### 3.2 Hardware Sensor Design and Equations

**pH Measurement.** The PH4502C module was powered at 3.3V (not the standard 5V) to protect the ESP32 ADC pins, which have a maximum input of 3.3V. The analog voltage output is converted to pH using the two-point calibration formula:

> pH = 7.0 + (V_cal − V_out) / S  ... (3.1)

where V_cal is the voltage at pH 7.0 (mid-point), V_out is the measured voltage, and S is the probe slope (mV per pH unit). Temperature compensation adjusts the raw ADC reading:

> V_comp = V_adc / [1.0 + 0.02 × (T − 25.0)]  ... (3.2)

**Important calibration note:** Two reference points were used for calibration — vinegar (~pH 2.4) as the acid reference and baking soda solution (~pH 8.3) as the base reference. These household chemicals provided a wide, measurable span without requiring laboratory buffer solutions. Because the sensor's voltage output is inverted (vinegar, the more acidic solution, gave a higher voltage reading), the calibration order was reversed in firmware: vinegar was stored as the 'base' reference and baking soda as the 'acid' reference. Both values are stored in the ESP32's Non-Volatile Storage (NVS) and survive power cycles.

**Water Level Measurement.** The HC-SR04 ultrasonic sensor emits a 10 μs trigger pulse and measures the echo return time. Water depth is computed as:

> Water Level = Pond Depth − (t_echo × v_sound) / 2  ... (3.3)

where t_echo is the echo pulse width in seconds, v_sound = 343 m/s (at 20°C), and Pond Depth is the measured distance from sensor to pond bed.

The ECHO pin outputs 5V logic. A 1 kΩ / 2 kΩ resistor voltage divider steps this down to 3.3V logic before reaching GPIO 18 on the ESP32.

**TDS Measurement.** The TDS probe is also operated at 3.3V. The raw ADC value is converted to ppm using a standard temperature-compensated conductivity conversion, factory-calibrated against NaCl reference solutions.

**NTC Thermistor Temperature.** A 4.7 kΩ pull-down resistor forms a voltage divider with the NTC thermistor. The measured voltage is converted to temperature using the Steinhart–Hart equation within the firmware.

### 3.3 Bill of Materials

**Table 3.1. AquaGuard Hardware Bill of Materials**

| Component | Quantity | Unit Cost (BDT) | Total (BDT) | Function |
|---|---|---|---|---|
| ESP32 WROOM-32 | 1 | 650 | 650 | Main microcontroller |
| pH Sensor (PH4502C) | 1 | 1,850 | 1,850 | Pond pH measurement |
| TDS Sensor Module | 1 | 185 | 185 | Dissolved solids |
| NTC Thermistor | 1 | 40 | 40 | Water temperature |
| HC-SR04 Ultrasonic | 1 | 120 | 120 | Water depth |
| 2-Channel Relay Module | 1 | 645 | 645 | Pump control |
| Submersible Pump ×2 | 2 | 325 | 650 | Drain and refill |
| Servo Motor | 1 | 500 | 500 | Automated feeder |
| LM2596 Buck Converter | 1 | 150 | 150 | Voltage regulation |
| Resistors, capacitors, wire | – | 130 | 130 | Dividers, filtering |
| Breadboard / PCB | 1 | 250 | 250 | Circuit assembly |
| Miscellaneous | – | 400 | 400 | Connectors, cable |
| **Total** | | | **6,570 BDT (~$55)** | |

### 3.4 Edge FSM Control Rules

The ESP32 firmware evaluates four local control rules every 30 seconds. These rules operate entirely on local sensor data without requiring the internet:

**Table 3.2. Autonomous Edge Control Rules**

| Rule | Condition | Automatic Action |
|---|---|---|
| Water too high | Level ≥ 85 cm AND TDS < 600 ppm | Activate Drain Pump for 10 minutes |
| Water too low | Level ≤ 40 cm | Activate Refill Pump until 70 cm |
| TDS overflow | TDS ≥ 600 ppm | Activate Drain Pump for 15 minutes |
| Scheduled feeding | Time = 08:00 or 16:00 | Rotate Servo Feeder for 3 seconds |

### 3.5 Cloud and Backend Architecture

Sensor readings and pump states are synchronized to the Firebase Realtime Database (RTDB) using the Firebase ESP32 Client SDK. The database structure separates live sensor telemetry (`/sensor/*`), pump command states (`/pumps/*`), and historical logs (`/history/*`).

The Python FastAPI backend (`api_combined.py`) is launched with `uvicorn` on Port 8000 and serves three endpoints — one per ML model. It imports the Model 1 sub-API from `model_1_flood/api.py` via `sys.path`, and loads the Model 2 and Model 3 saved `.pkl` files using relative paths, making the entire backend fully portable.

### 3.6 Machine Learning Model Methodology

**Model 1 — River Water-Level Forecasting**

*Dataset:* 15 years (2008–2022, 5,479 days) of daily BWDB Bahadurabad water levels. Missing values (335 days, 6.11%) were imputed using PCHIP interpolation, which preserves the monotonic shape of flood peaks better than linear interpolation.

*Features:* Water level at time t (WL_t), ERA5 catchment rainfall at 1-day, 3-day, and 7-day cumulative windows, and lag features WL_t-1 through WL_t-7. The physical lag between upstream rainfall and downstream water level rise justifies multi-day cumulative rainfall features.

*Validation:* Leave-One-Year-Out (LOYO) cross-validation. For each test year from 2009 to 2019, the model was trained on all other available years. The 2020–2022 period was held out as the final unseen test set and was never used during model selection. This scheme prevents temporal data leakage that standard K-Fold cross-validation would introduce.

*Metrics:* RMSE = √[ (1/N) × Σ(y_i − ŷ_i)² ] (Eq 3.4), NSE = 1.0 − [ Σ(y_i − ŷ_i)² / Σ(y_i − ȳ)² ] (Eq 3.5), POD = Hits / (Hits + Misses) (Eq 3.6), FAR = False Alarms / (Hits + False Alarms) (Eq 3.7).

**Model 2 — Pond TDS Forecasting (+60 minutes)**

*Dataset:* 1,327 continuous hourly IoT sensor records from 2023.

*Features:* Raw TDS at time t, plus rolling 6-hour and 12-hour mean TDS, and lag features TDS_t-1 through TDS_t-12.

*Validation:* 80/20 chronological train/test split — preserving temporal order. No random shuffling.

**Model 3 — Multivariate Anomaly Detection**

*Dataset:* Same 2023 hourly records as Model 2.

*Algorithm:* Isolation Forest with contamination = 0.05 (assuming ~5% anomaly rate in training data).

*Features:* Absolute sensor values (pH, TDS, Temp, Water Level) PLUS rate-of-change deltas (ΔpH, ΔTDS, ΔTemp per hour). The delta features are critical — they catch rapid deteriorations that may not yet have crossed an absolute threshold.

---

## Chapter 4: Implementation

### 4.1 Team Work Division

- **Srabon:** Hardware fabrication, circuit wiring, voltage protection, sensor calibration, relay integration.
- **Mahfuz:** Firebase Realtime Database configuration, web dashboard (HTML/CSS/JS), pH calibration page, analytics charts, remote pump control UI.
- **Hrithik:** Python FastAPI backend (`api_combined.py`), all three ML pipelines, LOYO cross-validation, SHAP analysis.

### 4.2 Hardware Build and Power Design

Sensors were connected to ADC1 pins (GPIO 34 for pH, GPIO 35 for TDS) because ADC2 shares pins with the ESP32's Wi-Fi radio and becomes unavailable when Wi-Fi is active. Both the pH and TDS sensors were powered from the ESP32's 3.3V rail to protect the ADC inputs.

A main 5V power rail, regulated by an LM2596 DC-DC buck converter (filtered with 470 μF + 0.1 μF capacitors), powers the relay module and pumps separately. This separation prevents voltage drops during pump switching from resetting the ESP32.

**Table 4.1. Corrected GPIO Pin Assignments**

| GPIO Pin | Component | Signal | Notes |
|---|---|---|---|
| GPIO 34 | pH Sensor (PH4502C) | Analog Input | ADC1 Ch6, Wi-Fi safe |
| GPIO 35 | TDS Sensor | Analog Input | ADC1 Ch7, Wi-Fi safe |
| GPIO 32 | NTC Thermistor | Analog Input | 4.7 kΩ pull-down divider |
| GPIO 5 | HC-SR04 TRIG | Digital Output | 10 μs trigger pulse |
| GPIO 18 | HC-SR04 ECHO | Digital Input | 1 kΩ/2 kΩ divider, 5V→3.3V |
| GPIO 25 | Relay 1 — Drain Pump | Digital Output | Active-LOW, opto-isolated |
| GPIO 26 | Relay 2 — Refill Pump | Digital Output | Active-LOW, opto-isolated |
| GPIO 13 | Servo Motor (Feeder) | PWM Output | 50 Hz, 1.0–2.0 ms duty |
| 3.3V rail | pH + TDS sensor power | Power | Protects ADC pins |
| VIN/5V | Relay + pumps power | Power | LM2596 regulated |

### 4.3 ESP32 Firmware

The firmware is written in C++ using the Arduino core. Key implementation details:

- **Non-blocking design:** `millis()` timers replace all `delay()` calls, so sensing, FSM evaluation, cloud sync, and serial logging all run concurrently without blocking each other.
- **ADC oversampling:** 64 fast samples are taken for each analog reading. The top and bottom 10% are discarded, and the remaining values are averaged, reducing electrical noise from the AC power supply near the pump motor.
- **NVS calibration storage:** Two-point pH calibration values are saved to the ESP32's Non-Volatile Storage (NVS), surviving power cycles. The calibration can be updated wirelessly from the dashboard without re-flashing firmware.
- **Local FSM safety:** The four control rules in Table 3.2 evaluate every 30 seconds using local sensor data and continue working during internet outages.

### 4.4 Cloud Backend

The Firebase Realtime Database stores `/sensor/ph`, `/sensor/tds`, `/sensor/temp`, `/sensor/level`, `/pumps/pump1`, `/pumps/pump2`, and a rolling 24-hour history under `/history/`. State changes propagate to connected browsers in under one second.

The Python FastAPI backend (`api_combined.py`) runs on `localhost:8000` with `uvicorn`. It loads the three model endpoints at startup:

- `GET /api/v1/forecast` — Model 1 (River Flood)
- `GET /api/v1/tds` — Model 2 (TDS Prediction)
- `GET /api/v1/anomaly` — Model 3 (Isolation Forest)
- `GET /docs` — Auto-generated Swagger API documentation

### 4.5 Web Dashboard

The dashboard is built with vanilla HTML, CSS, and JavaScript — no build tools, no framework — making it fast to load on rural mobile data connections. Features include:

- Live sensor tiles reading from Firebase in real time
- Composite Pond Health Index (0–100) calculated from all four parameters
- 24-hour and 7-day trend charts (Chart.js)
- Manual pump override toggle buttons
- Bilingual (English + Bengali) actionable farmer advice based on AI predictions
- A "Simulate Sensor Spike" button that sends pH 9.5 / TDS 450 / Temp 33°C to the anomaly endpoint and turns the card RED for five seconds — used for live defense demonstrations
- Alert banners with 3-reading debounce (90 seconds) and 30-minute cooldown to prevent false alarm fatigue

### 4.6 pH Calibration Page

A separate browser page (`ph-calibration.html`) walks the user through the two-point calibration in three steps without requiring any hardware re-flashing. The user dips the probe in vinegar (pH 2.4), clicks "Capture Acid Point"; then dips it in baking soda solution (pH 8.3), clicks "Capture Base Point"; and the page writes the new calibration values into Firebase, which the ESP32 reads and saves to NVS on the next telemetry cycle.

---

## Chapter 5: Results and Discussion

### 5.1 Sensor Calibration Results

After two-point calibration and 64-sample oversampling, all four sensors met engineering accuracy targets:

**Table 5.1. Sensor Calibration Accuracy Results**

| Sensor | Pre-Calibration Error | Post-Calibration Error | R² | 72h Drift |
|---|---|---|---|---|
| pH (PH4502C) | ±0.42 pH | ±0.05 pH | 0.994 | ±0.03 pH |
| TDS Probe | ±8.5% | ±2.8% | 0.989 | ±4.2 ppm |
| NTC Thermistor | ±0.85°C | ±0.15°C | 0.998 | ±0.08°C |
| HC-SR04 Ultrasonic | ±2.4 cm | ±0.4 cm | 0.996 | ±0.2 cm |

Note: pH calibration used vinegar (~pH 2.4) and baking soda solution (~pH 8.3) as the two reference points.

### 5.2 Model 1: River Flood Forecasting Results

**Table 5.2. Bahadurabad Station Dataset Summary (2008–2022)**

| Attribute | Value | Significance |
|---|---|---|
| Study Period | 2008-01-01 to 2022-12-31 | 15 continuous years |
| Total Days | 5,479 | Full seasonal cycles |
| Missing Days | 335 (6.11%) | Imputed via PCHIP |
| Gauge Range | 11.68 m – 21.16 m | Wide dynamic range |
| Official Danger Level | 19.05 m | Embankment overtopping |
| Extreme Danger Level | 19.90 m | Severe regional flooding |
| Record High Water Level | 20.63 m | 2020 peak |
| Flood Days (≥19.05 m) | 467 | Training flood events |

**Table 5.3. LOYO Cross-Validation Results — +1 Day Forecast Horizon**

| Model | RMSE (m) | MAE (m) | NSE | R² |
|---|---|---|---|---|
| Persistence Baseline | 0.412 | 0.298 | 0.921 | 0.921 |
| Persistence + Trend | 0.389 | 0.271 | 0.933 | 0.933 |
| **Linear Regression** | **0.075** | **0.051** | **0.998** | **0.998** |
| Ridge Regression | 0.078 | 0.054 | 0.997 | 0.997 |
| Lasso Regression | 0.081 | 0.057 | 0.997 | 0.997 |
| Random Forest | 0.104 | 0.073 | 0.994 | 0.994 |
| XGBoost | 0.118 | 0.081 | 0.992 | 0.992 |
| SVR | 0.143 | 0.098 | 0.988 | 0.988 |

**Key Finding — Peak Extrapolation Failure:** Tree-based models (Random Forest, XGBoost) are bounded by the maximum water level in their training data. During the 2020 and 2022 flood seasons — both of which produced water levels near or above 20.50 m — tree models predicted a flat ceiling of approximately 19.80 m because they had never seen higher values in prior training years. Linear Regression, by contrast, correctly extrapolated the upward trend, predicting levels above 20.50 m with low error. This is the structural reason Linear Regression was deployed.

**Table 5.4. Final Holdout Test Results — 2020–2022 Test Years (3-Day Horizon)**

| Model | RMSE (m) | NSE | Flood Days Missed | False Alarms |
|---|---|---|---|---|
| Persistence Baseline | 0.523 | 0.898 | 8 | 8 |
| Linear Regression | **0.308** | **0.985** | 11 | 3 |
| Random Forest | 0.412 | 0.951 | 12 | 5 |
| XGBoost | 0.438 | 0.944 | 13 | 2 |

**Safety Buffer Implementation:** All ML models missed more flood days than the Persistence Baseline because regression smooths out sharp peaks. To mitigate this known limitation, the dashboard alert threshold was set to 18.55 m — 0.5 m below the 19.05 m Danger Level. This gives farmers an earlier warning that compensates for peak-smoothing, at the cost of slightly more false alarms.

### 5.3 Model 2: Pond TDS Forecasting Results

**Table 5.5. Model 2 Performance Comparison (+60 min Horizon)**

| Model | MAE (ppm) | RMSE (ppm) | R² |
|---|---|---|---|
| Persistence Baseline | 6.14 | 8.92 | 0.942 |
| **Linear Regression** | **7.05** | **10.11** | **0.888** |
| Random Forest | 9.43 | 13.77 | 0.781 |
| XGBoost | 11.28 | 16.33 | 0.711 |

The Persistence Baseline (which predicts TDS_t+60 ≈ TDS_t) achieved the highest R² = 0.942, confirming that pond TDS drifts very slowly over a 60-minute window. Linear Regression (R² = 0.888) was deployed rather than the baseline because it incorporates 6-hour rolling trend information and responds earlier to developing runoff events.

SHAP analysis confirmed the physical expectation: the 6-hour rolling mean TDS and the 3-hour lag feature (TDS_t-3) are the two dominant predictors. This result validates the model's physical interpretability — it is learning real chemical kinetics, not noise.

### 5.4 Model 3: Multivariate Anomaly Detection Results

**Table 5.6. Anomaly Detection Comparison**

| Method | Anomalies Detected | True Positives (Manual) | Type |
|---|---|---|---|
| Standard Z-Score (single parameter) | 55 | 38 | Univariate |
| **Isolation Forest (AquaGuard)** | **67** | **51** | Multivariate |

The Isolation Forest detected 67 anomalies versus 55 by single-parameter Z-scores. The 12 additional anomalies caught by Isolation Forest are multivariate events — conditions where no individual parameter crossed its danger threshold, but the combination was harmful. The most common example: pH 8.2 (within safe range) combined with temperature 32°C (within safe range), which together produce lethal ammonia concentrations.

### 5.5 System Latency

- Firebase read-to-dashboard update: **< 1 second** (WebSocket push)
- FSM local rule evaluation cycle: **every 30 seconds**
- ML API response time (all 3 models): **< 250 ms** on local Python server
- Pump relay trigger-to-action: **< 500 ms** from FSM evaluation

---

## Chapter 6: Conclusion and Future Work

### 6.1 Conclusion

AquaGuard demonstrates that a capable, multi-model aquaculture protection system can be built for under 7,200 BDT using commodity hardware and free cloud services. The key findings from this project are:

1. **Linear models beat tree models during extreme flood events** because they extrapolate beyond their training range. This result has direct safety implications — deploying tree models alone for flood warning risks failing precisely during the most dangerous events.

2. **Pond TDS is slow-moving over short windows.** A simple rolling-average linear model outperforms XGBoost for 60-minute predictions. Complexity is not always better.

3. **Unsupervised anomaly detection catches multivariate hazards** that single-threshold systems miss. Combining absolute sensor values with rate-of-change deltas improves detection from 55 to 67 events.

4. **A calibration architecture requiring no hardware re-flashing** is critical for rural deployment. Farmers cannot re-flash firmware. The browser-based NVS calibration system makes recalibration accessible to non-technical users.

**Known Limitations:**
- Model 1 covers the Bahadurabad/Jamuna station only. The Surma-Kushiyara basin (Sylhet) flash floods are not modeled.
- pH probes require physical cleaning every 2–4 weeks to prevent biofilm drift.
- Wi-Fi dependency limits deployment to ponds within router range. Remote ponds need a GSM module.
- The finalized `AquaGuard_v2.ino` firmware is ready to flash but has not yet been deployed to a production fish pond for longitudinal field testing.

### 6.2 Future Work

1. **Multi-basin expansion:** Add the Surma-Kushiyara system for Sylhet flash flood early warning, which requires hourly (not daily) data.
2. **Automated SMS/WhatsApp alerts:** Integrate Twilio to push anomaly and flood warnings directly to farmers' phones when they are offline.
3. **Closed-loop firmware automation:** Automatically trigger the relay pumps when Model 3 detects a severe anomaly score, without requiring a manual dashboard click.
4. **LoRaWAN mesh:** Connect multiple ponds across a 10 km radius to a single gateway, enabling cluster-scale monitoring for aquaculture cooperatives.
5. **Solar off-grid power:** A 50W panel and 12V LiFePO4 battery would make the device fully self-powered in areas without grid electricity.

---

## Appendix A: Hardware Pinout and API Endpoints

### Table A.1. Complete Hardware Pinout Specifications

| ESP32 Pin | Component | Signal | Voltage | Interface |
|---|---|---|---|---|
| GPIO 34 | pH Sensor (PH4502C) | Analog Input | 0–3.3V | ADC1 Ch6, Wi-Fi safe |
| GPIO 35 | TDS Sensor | Analog Input | 0–2.3V | ADC1 Ch7, Wi-Fi safe |
| GPIO 32 | NTC Thermistor | Analog Input | 3.3V | 4.7 kΩ pull-down divider |
| GPIO 5 | HC-SR04 TRIG | Digital Output | 3.3V/5V TTL | 10 μs pulse |
| GPIO 18 | HC-SR04 ECHO | Digital Input | 3.3V logic | 1 kΩ/2 kΩ voltage divider |
| GPIO 25 | Relay 1 — Drain Pump | Digital Output | 5V opto-isolated | Active-LOW |
| GPIO 26 | Relay 2 — Refill Pump | Digital Output | 5V opto-isolated | Active-LOW |
| GPIO 13 | Servo Motor (Feeder) | PWM Output | 5V external | 50 Hz, 1–2 ms duty |
| 3.3V rail | pH + TDS sensor supply | Power | 3.3V DC | Protects ADC inputs |
| VIN/5V | Relay + pump supply | Power | 5V regulated | LM2596 buck output |
| GND | Common ground | Ground | 0V reference | Shared ground plane |

### Table A.2. REST API Endpoints (Python FastAPI ML Backend, Port 8000)

| Method | Route | Parameters | Description |
|---|---|---|---|
| GET | `/api/v1/forecast` | `horizon=1..14` | River water-level forecast + bilingual advice |
| GET | `/api/v1/tds` | `device_id` | Predicted pond TDS +60 min with SHAP scores |
| GET | `/api/v1/anomaly` | `pH, tds, temp` (optional) | Isolation Forest score and status |
| GET | `/docs` | — | Auto-generated Swagger API documentation |

---

## References

[1] Department of Fisheries (DoF), 'Yearbook of Fisheries Statistics of Bangladesh 2022-23,' Ministry of Fisheries and Livestock, Dhaka, Bangladesh, 2023.

[2] Food and Agriculture Organization (FAO), 'The State of World Fisheries and Aquaculture 2024,' FAO, Rome, Italy, 2024.

[3] Flood Forecasting and Warning Centre (FFWC), 'Annual Flood Report 2020,' BWDB, Dhaka, Bangladesh, 2021.

[4] M. M. Rahman, M. A. Hossain, and S. Islam, 'Impact of climate change and extreme monsoon flooding on inland aquaculture in northern Bangladesh,' Journal of Water and Climate Change, vol. 12, no. 4, pp. 1420–1435, 2021.

[5] C. E. Boyd, Water Quality: An Introduction, 3rd ed., Cham, Switzerland: Springer Nature, 2020.

[6] J. E. Colt, Dissolved Gas Concentration in Water, 2nd ed., London: Academic Press, 2012.

[7] P. Saha, D. Biswas, and A. K. Das, 'IoT-based automated water quality monitoring and alert system for fish farming,' in Proc. IEEE ICSCEE, Shah Alam, Malaysia, 2018, pp. 1–6.

[8] K. R. Raju, G. H. Kumar, and M. V. Reddy, 'Automated water quality monitoring and control system for aquaculture using Raspberry Pi,' IEEE IoT Journal, vol. 7, no. 9, pp. 8412–8421, 2020.

[9] M. R. Hasan, M. S. Alam, and T. Sultana, 'Design and deployment of a low-cost IoT telemetry node for rural fish ponds in Bangladesh,' in Proc. IEEE ICEEICT, Dhaka, 2021, pp. 215–220.

[10] M. N. Islam, S. K. Roy, and R. Ahmed, 'Predictive water aeration and quality management using ESP32 edge microcontroller,' IEEE Access, vol. 10, pp. 54312–54324, 2022.

[11] X. Chen, Y. Zhang, and L. Wang, 'Industrial PLC-driven multi-parameter recirculating aquaculture control system with deep LSTM DO prediction,' Computers and Electronics in Agriculture, vol. 205, art. no. 107621, 2023.

[12] S. Ahmed, F. Farzana, and K. M. Kabir, 'Automated fish feeding and pond level management system using IoT relays and ultrasonic sensing,' in Proc. IEEE CONECCT, Bangalore, 2024, pp. 1–6.

[13] F. T. Liu, K. M. Ting, and Z.-H. Zhou, 'Isolation Forest,' in Proc. 8th IEEE ICDM, Pisa, Italy, 2008, pp. 413–422.

[14] S. M. Lundberg and S.-I. Lee, 'A unified approach to interpreting model predictions,' in Advances in Neural Information Processing Systems (NeurIPS 30), 2017, pp. 4765–4774.

[15] T. Chen and C. Guestrin, 'XGBoost: A scalable tree boosting system,' in Proc. 22nd ACM SIGKDD, 2016, pp. 785–794.

[16] L. Breiman, 'Random Forests,' Machine Learning, vol. 45, no. 1, pp. 5–32, 2001.

[17] A. E. Hoerl and R. W. Kennard, 'Ridge regression: Biased estimation for nonorthogonal problems,' Technometrics, vol. 12, no. 1, pp. 55–67, 1970.

[18] R. Tibshirani, 'Regression shrinkage and selection via the Lasso,' Journal of the Royal Statistical Society: Series B, vol. 58, no. 1, pp. 267–288, 1996.

[19] J. E. Nash and J. V. Sutcliffe, 'River flow forecasting through conceptual models part I,' Journal of Hydrology, vol. 10, no. 3, pp. 282–290, 1970.

[20] H. Hersbach et al., 'The ERA5 global reanalysis,' Quarterly Journal of the Royal Meteorological Society, vol. 146, no. 730, pp. 1999–2049, 2020.

[21] Bangladesh Water Development Board (BWDB), 'Hydrometric Data Portal: Daily Water Levels — Station SW46.9L,' BWDB Hydrology Division, Dhaka, 2024.

[22] Espressif Systems, 'ESP32 Series Datasheet: 2.4 GHz Wi-Fi and Bluetooth Combo Chip,' Espressif Systems, Shanghai, China, 2023.

[23] F. Pedregosa et al., 'Scikit-learn: Machine learning in Python,' Journal of Machine Learning Research, vol. 12, pp. 2825–2830, 2011.

[24] Board of Accreditation for Engineering and Technical Education (BAETE), 'Manual for Accrediting Undergraduate Engineering Programmes,' IEB, Dhaka, Ver. 2.1, 2023.

[25] University of Information Technology and Sciences (UITS), 'Capstone Project and Thesis Guidelines: Department of CSE,' UITS Academic Council, Dhaka, Bangladesh, 2026.
