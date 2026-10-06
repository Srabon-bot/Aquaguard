"""
Script to generate GPT_REPORT_EDITING_EVIDENCE.md
"""

content = """# GPT_REPORT_EDITING_EVIDENCE.md
**CONFIDENTIAL & AUTHORITATIVE PROJECT GROUND TRUTH**
**Purpose:** Provide absolute factual evidence for editing `AquaShield_Capstone_Project_Report_Humanized.md`.
**Source Priority Used:** Source Code > Config Files > Datasets/Outputs > Hardware Docs > Project Docs > Old Reports.

---

## SECTION 1 — PROJECT IDENTITY
* **Official Project Name:** AquaGuard
* **Names used in source code/repo:** AquaGuard (e.g., `AquaGuard_v2.ino`, `AQUAGUARD_ML_FINAL_REPORT.md`, `HOW_TO_RUN_AQUAGUARD.md`)
* **Names used in reports:** AquaShield (in older/humanized docs), AquaGuard (in corrected docs)
* **Status:** AquaShield and AquaGuard refer to the exact same project. 
* **Rule:** "AquaGuard" must be preferred everywhere. "AquaShield" is a legacy name and should be fully replaced.

---

## SECTION 2 — SYSTEM ARCHITECTURE
* **IoT/hardware:** IMPLEMENTED. (ESP32-based node).
* **ESP32:** IMPLEMENTED. (WROOM-32).
* **Sensors:** IMPLEMENTED. (pH, TDS, Temp, Ultrasonic Level).
* **Local control:** IMPLEMENTED. (FSM offline control of relays/servo).
* **Cloud/Firebase:** IMPLEMENTED. (Realtime Database).
* **Backend/FastAPI:** IMPLEMENTED. (Runs locally on Port 8000, `api_combined.py`).
* **ML models:** IMPLEMENTED. (3 independent ML models running in FastAPI).
* **Dashboard:** IMPLEMENTED. (HTML/JS/CSS frontend).
* **Recommendations/alerts:** IMPLEMENTED. (Bilingual alerts, warning thresholds).
* **Multi-region deployment:** PLANNED/FUTURE. (Currently regional pilot).

---

## SECTION 3 — HARDWARE GROUND TRUTH
* **ESP32 model:** ESP32 WROOM-32.
* **Power arrangement:** 5V LM2596 buck converter powers relays/pumps. 3.3V rail powers sensors (to protect ADC).
* **Sensors:** PH4502C (pH), Generic TDS, NTC Thermistor (Temp), HC-SR04 (Ultrasonic).
* **ADC channels:** ADC1 *only*. ADC2 cannot be used concurrently with Wi-Fi. (Source: ESP32 architecture constraints / `AquaGuard_v2.ino`).
* **GPIO mappings:** 
  * pH: GPIO 34 (ADC1_CH6)
  * TDS: GPIO 35 (ADC1_CH7)
  * Temp: GPIO 32 (ADC1_CH4)
  * HC-SR04 Trig: GPIO 5
  * HC-SR04 Echo: GPIO 18 (with 5V->3.3V voltage divider)
* **Relay pins:** GPIO 25 (Drain Pump), GPIO 26 (Refill Pump). Active-LOW.
* **Servo pin:** GPIO 13.
* **Sampling interval:** 64-sample oversampling (top/bottom 10% discarded). Telemetry sent every 30 seconds.
* **Calibration materials:** Household Vinegar (~2.4 pH), Baking Soda (~8.3 pH). (Source: `PH_CALIBRATION_MANUAL.md`).
* **Offline behavior:** FSM evaluates sensor data locally every 30 seconds and actuates pumps even if Wi-Fi/Firebase is completely down. (Source: `AquaGuard_v2.ino`).

---

## SECTION 4 — CALIBRATION GROUND TRUTH
* **Method:** 2-point software calibration stored in ESP32 Non-Volatile Storage (NVS).
* **Reference Solutions:** Household Vinegar (acid) and Baking Soda solution (base). 
* **Lab Buffers:** NOT USED. (Due to rural budget constraints).
* **Workflow:** User accesses a web-based calibration wizard, dips probe, and clicks capture. Values sync via Firebase to ESP32 NVS. No firmware reflashing required.
* **Quirk:** The PH4502C outputs inverted voltage (vinegar gives higher voltage than baking soda), so the code reverses the logical mapping.

---

## SECTION 5 — ESP32 / OFFLINE CONTROL
* **FSM States:** Evaluates every 30 seconds.
* **Logic Rules:**
  * Level >= 85cm AND TDS < 600ppm -> Drain 10 mins.
  * Level <= 40cm -> Refill until 70cm.
  * TDS >= 600ppm -> Drain 15 mins.
  * Time = 08:00 or 16:00 -> Feed 3 seconds.
* **Connectivity:** If Wi-Fi/Firebase fails, local sensing and pump actuation continue uninterrupted. Only telemetry syncing and remote manual overrides are lost.

---

## SECTION 6 — CLOUD / FIREBASE
* **Firebase Usage:** Firebase Realtime Database.
* **Telemetry Structure:** Separated into `/sensor/*`, `/pumps/*`, `/history/*`.
* **Syncing:** ESP32 pushes sensor data and reads pump commands (for manual override). Dashboard reads sensor data and writes pump commands.

---

## SECTION 7 — BACKEND
* **FastAPI:** IMPLEMENTED in `api_combined.py`.
* **Port:** 8000.
* **Endpoints:**
  * `GET /api/v1/forecast` (Model 1: River WL)
  * `GET /api/v1/tds` (Model 2: Pond TDS)
  * `GET /api/v1/anomaly` (Model 3: Anomaly)
* **Model Loading:** `.pkl` and `.joblib` files loaded via relative paths.

---

## SECTION 8 — DASHBOARD
* **Live Features:** Live sensor dials, Chart.js trends, Composite Pond Health Index (0-100).
* **Controls:** Manual pump overrides, calibration wizard.
* **Alerts:** Bilingual (English/Bengali) alert banners with a 90-second debounce and 30-minute cooldown to prevent alert fatigue.
* **Simulation:** "Simulate Sensor Spike" button injects artificial extreme data to trigger Model 3 alerts during live defense demos.

---

## SECTION 9 — MODEL 1 COMPLETE GROUND TRUTH
* **Purpose:** Multi-horizon (+1, +3, +7, +14 days) river water-level forecasting.
* **Station:** Bahadurabad Transit (SW46.9L), Jamuna River. Coordinates: 25.1°N, 89.6°E.
* **Geographic Scope:** Regional pilot (Jamuna basin). NOT currently a national multi-station deployment.
* **Dataset:** 2008-2022 daily water levels (5,479 records). Provider: BWDB.
* **Missing Data:** 335 days (6.11%). Imputed using PCHIP interpolation (preserves peak shapes).
* **Rainfall Source:** ERA5-Land via Open-Meteo API. 6 specific catchment grid points (Tibet to Bangladesh).
* **Features:** WL lags (0-7), rolling means (3d, 7d), rate of change (delta), rainfall lags.
* **Algorithms Tested:** Persistence, LR, Ridge, Lasso, RF, XGBoost, SVR, LSTM.
* **Final Model:** Linear Regression.
* **Validation:** Leave-One-Year-Out (LOYO) CV on 2008-2019. Holdout on 2020-2022. 
* **Metrics (Holdout +3 day):** RMSE = 0.308m, NSE = 0.985.
* **Extreme Flood Behavior:** Linear Regression successfully extrapolated the 2020 record peaks; Tree models (RF, XGBoost) failed and hit a "ceiling".
* **Warning Threshold:** Alert triggers at 18.55m (a 0.5m safety buffer below the 19.05m Danger Level).

---

## SECTION 10 — MODEL 1 VALIDATION
* **K-Fold Used?** NO.
* **LOYO Used?** YES. Leave-One-Year-Out cross-validation.
* **Why?** Prevents temporal data leakage inherent in random K-Fold shuffling for time-series.
* **WRONG IN REPORT:** "K-Fold Cross Validation"
* **CORRECT PROJECT FACT:** LOYO CV for 2008-2019, Chronological Holdout for 2020-2022.
* **SOURCE:** `model_1_flood/DATA_ANALYSIS.md` & `config.yaml`.

---

## SECTION 11 — MODEL 1 MODEL SELECTION
* **Why Linear Regression?** It was selected SPECIFICALLY because it can extrapolate numerical values higher than its training data.
* **Tree Model Failure:** Random Forest and XGBoost performed well on normal days but completely failed to predict the record 2020 flood (20.63m) because tree models cannot predict values outside their training distribution envelope. 

---

## SECTION 12 — MODEL 2
* **Purpose:** Forecast Pond TDS +60 minutes.
* **Inputs:** Raw TDS, 6h/12h rolling means, lags.
* **Algorithm:** Linear Regression. (Outperformed XGBoost because pond chemistry drifts slowly, making rolling trend lines highly accurate).

---

## SECTION 13 — MODEL 3
* **Purpose:** Multivariate Anomaly Detection.
* **Features:** Absolute sensor values (pH, TDS, Temp, WL) AND rate-of-change deltas (ΔpH, ΔTDS, ΔTemp per hour).
* **Algorithm:** Isolation Forest (contamination=0.05).
* **Why Deltas?** Caught 12 extra multivariate anomalies that standard Z-scores missed (e.g., pH 8.2 + Temp 32°C combined creates toxic ammonia, even though neither alone triggers an absolute threshold).

---

## SECTION 14 — GEOGRAPHIC SCOPE
* **Overall Intended Scope:** Bangladesh-wide platform.
* **Current Implemented Scope:** Jamuna River Basin.
* **Current Model 1 Validated Scope:** Bahadurabad station ONLY.
* **Future Expansion Scope:** Padma (Hardinge Bridge), Surma (Kanaighat).
* **Rule:** Do NOT claim the ML model currently predicts floods for all of Bangladesh.

---

## SECTION 15 — THRESHOLDS
| THRESHOLD | VALUE | MEANING | SOURCE | IMPLEMENTED WHERE |
|---|---|---|---|---|
| AquaGuard Warning | 18.55 m | 0.5m buffer to give advance notice | `config.yaml` | Dashboard UI |
| Danger Level | 19.05 m | Official BWDB level (embankment overtop) | BWDB / `config.yaml` | Model 1 evaluation |
| Extreme Danger | 19.90 m | Severe regional inundation | BWDB | Model 1 evaluation |
| Record High (RHWL)| 20.63 m | 2020 peak flood | BWDB data | Model 1 dataset |

---

## SECTION 16 — FIGURES
The following figures have been generated and MUST be referenced in the report:
* `F01_full_wl_series.png` - 15-year dataset history.
* `F20_scatter_1to1_by_horizon.png` - Prediction accuracy.
* `F21_residual_diagnostics.png` - Error distribution.
* `FigD_warning_threshold_hydrograph.png` - 2020 Flood season showing the 18.55m warning line trigger.
* `FigG_model1_pipeline_diagram.png` - Flowchart from data to dashboard.
* `FigH_data_sources_diagram.png` - Showing BWDB (primary), ERA5 (live), JASON (cross-check).

---

## SECTION 17 — REFERENCES
Must explicitly include:
1. BWDB Hydrometric Data Portal (Station SW46.9L, Bahadurabad).
2. ERA5 global reanalysis (Hersbach et al., 2020).
3. Open-Meteo API (Zippenfenig, 2023).
4. JASON-2/3 Satellite Radar Altimetry via HydroWeb (ESA/CNES).

---

## SECTION 18 — HUMANIZED REPORT ERRORS
| REPORT CLAIM | STATUS | CORRECT FACT | ACTION |
|---|---|---|---|
| "AquaShield" | INCORRECT | AquaGuard | Global Find & Replace |
| "K-Fold Cross Validation" | INCORRECT | LOYO (Leave-One-Year-Out) | Replace text |
| "Lab buffers pH 4/7" | INCORRECT | Household vinegar / baking soda | Replace text in hardware section |
| "Protects entire Bangladesh" | OVERSIMPLIFIED | Validated regional pilot for Jamuna basin | Clarify scope in Intro/Methodology |
| "ADC2 used" | INCORRECT | ADC1 used (ADC2 breaks with Wi-Fi) | Correct hardware section |

---

## SECTION 19 — EXACT MANUAL EDITS
* **Ch 3 (Methodology):** Find "K-Fold". Replace with: "Leave-One-Year-Out (LOYO) cross-validation was used across 2008-2019 to prevent temporal data leakage, with 2020-2022 kept as a strict chronological holdout."
* **Ch 4 (Implementation):** Find GPIO/Sensors. Add: "Sensors were wired exclusively to ADC1 pins (GPIO 32, 34, 35) because ADC2 becomes disabled when the ESP32 Wi-Fi radio is active. The pH module was powered at 3.3V to protect the ESP32 inputs."
* **Ch 4 (Implementation):** Find "calibration". Replace with: "Due to cost constraints, calibration utilized household references: vinegar (pH ~2.4) and baking soda (pH ~8.3), mapped via a 2-point firmware equation stored in NVS."
* **Ch 5 (Results - Model 1):** Add: "Linear Regression was selected over tree-based ensembles (Random Forest, XGBoost) because tree models failed to extrapolate the record 2020 flood peaks (20.63m), whereas Linear Regression successfully extrapolated the trend."

---

## SECTION 20 — DO NOT CHANGE
* The overall 6-chapter structure.
* The descriptions of the HTML/JS dashboard UI.
* The Isolation Forest and Rolling Mean Linear Regression descriptions for Models 2 and 3 (they are fundamentally correct).
* The cost breakdown (~$55 / 6570 BDT).

---

## SECTION 21 — DO NOT CLAIM
* DO NOT claim the system uses LoRa (it uses Wi-Fi).
* DO NOT claim the system uses MQTT (it uses Firebase REST/WebSockets).
* DO NOT claim the system is solar powered (future work).
* DO NOT claim the flood model currently works for Sylhet/flash floods (they require hourly data, Bahadurabad uses daily).

---

## SECTION 22 — DEFENCE QUESTIONS
* **Q:** Why did you use Linear Regression instead of Deep Learning for the flood model? 
  * **A:** Linear regression can extrapolate values higher than its training data (critical for record-breaking floods). Tree models and standard ML hit a ceiling.
* **Q:** What happens if the pond Wi-Fi goes down?
  * **A:** The ESP32 runs a local Finite State Machine every 30 seconds. Pumps will still drain/refill the pond based on local sensor readings.
* **Q:** Why use vinegar for calibration?
  * **A:** Commercial lab buffers are too expensive and degrade quickly. Vinegar and baking soda provide accessible 2-point references for rural farmers.

---

## SECTION 23 — UNRESOLVED ISSUES
* **UNRESOLVED:** The exact physical location of the deployed prototype pond. 
* **WHY:** The codebase contains the hardware logic but does not state the geographical address of the test pond. 
* **WHAT WOULD RESOLVE IT:** Student input during defense.
"""

with open(r'D:\Projects\pred_flood\GPT_REPORT_EDITING_EVIDENCE.md', 'w', encoding='utf-8') as f:
    f.write(content)

print("Evidence document generated successfully.")
