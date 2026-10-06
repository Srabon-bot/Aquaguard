# AquaShield/AquaGuard: COMPLETE FORENSIC AUDIT REPORT
**Target:** `AquaShield_Capstone_Project_Report_Humanized.md` vs. **Actual Project Repository**
**Date of Audit:** October 2026
**Auditor:** Automated Project Analysis Engine

---

## 1. Executive Summary
This forensic audit investigated the alignment between the current "Humanized Defence Report" (`AquaShield_Capstone_Project_Report_Humanized.md`) and the actual implementation of the AquaGuard/AquaShield project. 

**Key Findings:**
1. **Name Inconsistency:** The actual project and code use "AquaGuard", but the report still uses "AquaShield".
2. **Geographic Scope Oversell:** The report implies the ML models provide Bangladesh-wide protection. The actual Model 1 is strictly a regional pilot trained exclusively on Bahadurabad (Jamuna River).
3. **Hardware Hallucinations:** The report claims standard 5V lab buffer calibration (pH 4.01/6.86), while the actual physical build used 3.3V protection, vinegar, and baking soda due to budget constraints.
4. **Missing Threshold Details:** The humanized report misses the critical 18.55m safety buffer threshold used in the dashboard.
5. **Technical Accuracy:** The ML pipeline descriptions in the report are generally correct, but lack the specific diagnostic evidence (e.g., LOYO cross-validation) needed to defend *why* Linear Regression beat Random Forest.

**Overall Verdict:** The Humanized Report reads well but is **technically dangerous for defense**. An examiner looking at the actual code or hardware will find contradictions. It requires immediate technical corrections (P0) before submission.

---

## 2. Project Ground Truth
Based on the direct inspection of the codebase, here is what the project *actually* is:
* **IoT Hardware:** ESP32 WROOM-32 edge device, powered by 5V buck converter. Sensors connected to ADC1 only (Wi-Fi safe). Sensors: pH (PH4502C at 3.3V), TDS, Temp (NTC), Level (HC-SR04).
* **Control:** Autonomous FSM evaluating every 30s. 2x 5V Relays for Drain/Refill pumps, 1x Servo for feeder. Works offline.
* **Backend/Cloud:** Firebase Realtime Database for telemetry. Python FastAPI backend (`api_combined.py`) running on localhost:8000.
* **ML Model 1:** River WL forecasting (+1 to +14 days). Trained on BWDB SW46.9L (Bahadurabad) & ERA5 catchment rainfall. Model: Linear Regression (extrapolates better than trees). Validation: LOYO (2008-2019), Holdout (2020-2022).
* **ML Model 2:** Pond TDS forecast (+60 min). Model: Linear Regression on rolling means.
* **ML Model 3:** Anomaly detection. Model: Isolation Forest on multi-variate delta features.
* **Frontend:** HTML/JS/CSS dashboard with live tiles, chart.js, and calibration wizard.

---

## 3. Complete File Inventory
| File / Location | Type | Relevance | Status / Findings |
|---|---|---|---|
| `AquaShield_Capstone_Project_Report_Humanized.md` | Target Report | High | Contains multiple AI-hallucinated details and scope inaccuracies. |
| `hardware/AquaGuard_v2/AquaGuard_v2.ino` | Source Code | High | **Ground Truth.** Proves offline FSM rules, ADC1 pins, and calibration math. |
| `backend/api_combined.py` | Source Code | High | Proves FastAPI routing and relative model loading. |
| `model_1_flood/DATA_ANALYSIS.md` | Documentation | High | Proves Bahadurabad station usage and LOYO CV usage. |
| `model_1_flood/outputs/predictions/*` | Data | High | Proves exact test dates and Linear Regression performance. |
| `hardware/PH_CALIBRATION_MANUAL.md` | Documentation | High | Proves use of vinegar/baking soda, not lab buffers. |

---

## 4. Current Humanized Report Structure
* Chapter 1: Introduction (1.1 - 1.7)
* Chapter 2: Background Studies (2.1 - 2.7)
* Chapter 3: Methodology (3.1 - 3.8)
* Chapter 4: Implementation (4.1 - 4.8)
* Chapter 5: Result Analysis (5.1 - 5.8)
* Chapter 6: Conclusion (6.1 - 6.2)

**Audit:** The structure is standard and acceptable. It logically flows from hardware to cloud to ML. No structural redesign is needed, only content fixes.

---

## 5. Whole-Project Coverage Audit
| Component | Actually implemented? | Evidence | Present in Report? | Accuracy |
|---|---|---|---|---|
| ESP32 Local Control | YES | `AquaGuard_v2.ino` | YES | [PARTIALLY CORRECT] - misses offline behavior |
| Cloud Telemetry | YES | Firebase JSON / code | YES | [CORRECT] |
| FastAPI Backend | YES | `api_combined.py` | YES | [CORRECT] |
| Model 1 (Flood) | YES | `model_1_flood/` | YES | [INCORRECT] - oversells geographic scope |
| Model 2 (TDS) | YES | `model_2/` | YES | [CORRECT] |
| Model 3 (Anomaly) | YES | `model_3/` | YES | [OVERSIMPLIFIED] - misses delta features |

---

## 6. IoT/Hardware Audit
* **Claim:** Used standard pH calibration buffers (4.01 / 6.86).
  * **Ground Truth:** Used household vinegar and baking soda.
  * **Status:** [INCORRECT]. This is a critical defense failure if an examiner asks to see the buffers.
* **Claim:** Sensors connected to ADC2.
  * **Ground Truth:** ADC1 was deliberately used because ADC2 fails when Wi-Fi is on.
  * **Status:** [MISSING]. This was a major technical challenge solved by the team, but it's missing from the report.
* **Claim:** GPIO Pins 19, 21, 23.
  * **Ground Truth:** GPIO 25, 26, 13 (verified in `.ino`).
  * **Status:** [INCORRECT].

---

## 7. Cloud/Backend Audit
* **Claim:** Data stored in Firebase.
  * **Status:** [CORRECT].
* **Claim:** API routes for prediction.
  * **Ground Truth:** Routes are `/api/v1/forecast`, `/api/v1/tds`, `/api/v1/anomaly`.
  * **Status:** [NEEDS CLARIFICATION] - The report vaguely mentions APIs without listing the actual deployed routes.

---

## 8. Dashboard Audit
* **Claim:** Dashboard shows warnings.
  * **Ground Truth:** Warning triggers at 18.55m (0.5m safety buffer below 19.05m Danger Level).
  * **Status:** [MISSING]. The specific threshold mathematics are crucial to defending the safety system.

---

## 9. ML Audit & 10. Model 1 Deep Audit
**Model 1 Ground Truth:**
* **Station:** Bahadurabad (SW46.9L).
* **Data:** 15 years (2008-2022).
* **Validation:** Leave-One-Year-Out (LOYO) cross-validation to prevent temporal leakage.
* **Algorithm:** Linear Regression (R² 0.998, RMSE 0.308m). Tree models failed at extreme peak extrapolation.

**Humanized Report Claims:**
* **Claim:** The ML model protects Bangladesh aquaculture.
  * **Status:** [OVERSIMPLIFIED]. It protects the *Jamuna floodplain*. Extending it requires new data.
* **Claim:** K-Fold cross-validation was used.
  * **Status:** [INCORRECT]. K-Fold causes data leakage in time-series. The project specifically used LOYO.

---

## 11. Geographic Scope Audit
**Intended Scope:** Bangladesh-wide platform.
**Implemented Scope:** Bahadurabad / Jamuna Basin only.
**Future Work:** Hardinge Bridge, Kanaighat, Dalia.
**Audit Finding:** The humanized report conflates intended scope with implemented scope. 
**Required Action:** Chapter 3 must explicitly state: *"While AquaGuard is a national platform, Model 1 was implemented as a regional pilot for the Jamuna basin due to the availability of historical BWDB data at Bahadurabad."*

---

## 12. Figures & 13. Tables Audit
* **Missing from Report:** Figure D (Warning Threshold Hydrograph), Figure G (Model 1 Pipeline), Figure H (Data Sources).
* **Recommendation:** Insert these newly generated figures into Chapter 3 and Chapter 5. They provide instant visual proof of the methodology.

---

## 14. References/Citations Audit
* **Status:** The report references generic machine learning papers.
* **Missing:** Explicit citations for BWDB (gauge data), ESA/HydroWeb (altimetry), and Open-Meteo/ERA5 (rainfall).
* **Action:** Must append the exact dataset citations (detailed in `MODEL_1_FULL_REFERENCE.md`).

---

## 15, 16, 17. Content Audits (Removed, Added, Missing)
* **Missing (Critical):** The explanation of *why* Linear Regression was chosen over XGBoost/Random Forest (peak extrapolation failure).
* **Added/Unsupported:** Vague AI buzzwords ("paradigm shift", "delves into"). Must be stripped.

---

## 18. Technical Inconsistencies
* "AquaShield" vs "AquaGuard"
* pH calibration methodology
* GPIO pin mappings
* Cross-validation methodology (K-Fold vs LOYO)

---

## 19. Defence Question Audit
* **Q:** What happens if the internet goes down?
  * **Report Answer:** Fails to mention.
  * **Ground Truth:** The ESP32 local FSM evaluates rules every 30s offline.
  * **Action:** Must be added to Chapter 4.

---

## 20. Final Scorecard
* Technical accuracy: 60/100
* Completeness: 75/100
* Whole-project coverage: 85/100
* Defence readiness: 50/100
* **OVERALL SCORE: 68 / 100**
* **Reasoning:** The report looks complete structurally, but contains fatal technical flaws regarding hardware implementation, geographic scope, and ML validation methodologies.

---

## 21. Prioritized Fix List (P0 / P1 / P2 / P3)
### P0 — MUST FIX BEFORE SUBMISSION
* **Ch 4:** Change GPIO pins to 25, 26, 13.
* **Ch 4:** Remove "lab buffers" and explain vinegar/baking soda calibration.
* **Ch 3 & 5:** Replace "K-Fold" with "LOYO cross-validation".
* **Ch 1 & 6:** Clarify Model 1 is a regional Bahadurabad pilot, not a national model.

### P1 — SHOULD FIX
* **All Chapters:** Find and replace "AquaShield" with "AquaGuard".
* **Ch 5:** Explain *why* Linear Regression beat tree models (peak extrapolation).
* **Ch 3:** Add Figure G (Model Pipeline) and Figure H (Data Sources).

### P2 — ENRICHMENT
* **Ch 5:** Add Figure D (Warning Threshold Hydrograph) to prove safety buffer logic.

### P3 — OPTIONAL
* Add actual API route table (`/api/v1/forecast`, etc.).

---

## 22. Exact Recommended Editing Map
1. **Global Replace:** `AquaShield` -> `AquaGuard`.
2. **Section 1.5 Scope:** Insert: "Model 1 is scoped to the Jamuna basin (Bahadurabad) as a pilot, with architecture ready for national scaling."
3. **Section 3.4 Edge Control:** Insert: "The FSM operates independently of the cloud connection, ensuring local pump actuation during Wi-Fi outages."
4. **Section 3.7 Validation:** Delete K-Fold mentions. Insert: "Leave-One-Year-Out (LOYO) cross-validation was used to prevent temporal leakage."
5. **Section 4.2 Hardware:** Update GPIO table. Pin 25=Drain, Pin 26=Refill, Pin 13=Servo. State 3.3V power was used for pH to protect ADC1 pins.
6. **Section 5.3 Results:** Insert text: "Tree-based models failed to extrapolate extreme flood peaks seen in 2020. Linear Regression was deployed because it successfully extrapolated these peaks."
7. **References:** Add BWDB and ERA5 citations.
