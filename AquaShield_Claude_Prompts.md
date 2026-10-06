# AquaShield Capstone Diagram Prompts

**RECOMMENDED DIAGRAM SET**

| # | Diagram | Report Location | Why Needed | Source Evidence |
|---|---|---|---|---|
| 1 | ESP32 Local FSM | Chapter 4 / Hardware & Control | Clarifies how the edge node handles automation without the cloud. | Mentioned in report context; pumps/actuators exist in frontend `app.js`. |
| 2 | Hardware Wiring & Power | Chapter 3 / System Architecture | Visualizes exact GPIO connections and power isolation (3.3V vs 5V). | Report context and Arduino firmware constraints. |
| 3 | Software & Telemetry Data Flow | Chapter 3 / Data Pipeline | Shows how telemetry moves from ESP32 -> FastAPI/Firebase -> ML Models. | `api_combined.py` and `app.js` code architecture. |
| 4 | Dashboard Info Architecture | Chapter 5 / UI & Alerts | Explains how the user interacts with ML forecasts and live alerts. | `AquaGuard_Web_Bundle/frontend` structure. |
| 5 | High-Level System Overview | Chapter 1 / Introduction | Provides the 10,000-foot view of the entire 5-tier architecture. | Report context (Physical -> Edge -> Cloud -> ML -> UI). |


==================================================
MASTER INSTRUCTIONS FOR CLAUDE (PLEASE READ FIRST)
==================================================
You are the primary Frontend and Visualization Engineer for the AquaShield capstone project.

Instead of just returning raw Mermaid markdown blocks, **you must write a fully functioning HTML/CSS/JS website** (e.g., using a single-page app structure with a sidebar or navbar) that renders all of the requested diagrams live using `mermaid.js`.

For EVERY diagram requested below, you must code **TWO distinct Mermaid versions** rendered on the webpage:
1. **The Report Version:** Highly detailed, mathematically and technically rigorous, optimized for a vertical/A4 layout.
2. **The PPT Slide Version:** Simplified, bold, optimized for a wide 16:9 presentation layout. Omit granular details (like exact GPIO pins or minor thresholds) and focus on large, readable blocks.

**Styling & Theme Requirements:**
- The website and diagrams MUST use a strict **Light/Academic Theme** (white backgrounds, dark text, clean borders). It must be a color scheme matchable with white paper reports and light presentation slides (e.g., monochromatic, or subtle matcha/soft-green accents).
- Embed this Mermaid configuration into your JS initialization so the SVGs render cleanly: `mermaid.initialize({ theme: 'default', themeVariables: { primaryColor: '#ffffff', primaryBorderColor: '#333333', lineColor: '#333333', tertiaryColor: '#e8f5e9' } });`

Below are the 5 specific diagram prompts. Please generate the complete website code encompassing all 10 diagrams (5 Report + 5 PPT).


==================================================
CLAUDE PROMPT 1 — ESP32 LOCAL FSM
==================================================
A. Diagram Title: Edge Node Finite State Machine (Local Automation)
B. Recommended Location: Chapter 4 / Hardware & Control
C. Purpose: To illustrate the local control logic of the ESP32 that runs independently of cloud connectivity (Offline Edge Fail-Safe).
D. Exact Project Facts:
   - High Water Level (>= 85 cm) triggers the Drain Pump.
   - Low Water Level (<= 40 cm) triggers the Refill Pump.
   - High TDS (>= 600 ppm) triggers a Water Exchange (Drain + Refill).
   - Abnormal pH triggers a local alert state.
   - Feeder Servo operates on a scheduled FSM state.
E. Components: ESP32 (Controller), pH Sensor, TDS Sensor, HC-SR04 (Ultrasonic), Drain Pump, Refill Pump, Feeder Servo. States: IDLE, CHECK_WATER_LEVEL, CHECK_WATER_QUALITY, DRAIN_ACTIVE, REFILL_ACTIVE, WATER_EXCHANGE, FEEDING, ALERT.
F. Connections: Directional transitions between FSM states based on sensor threshold conditions.
G. Direction of Flow: Top-down state evaluation loop.
H. Important Distinctions: Must clearly state "Local Control Loop - No Internet Required".
I. Exact Labels: "Water Level >= 85cm", "Water Level <= 40cm", "TDS >= 600ppm".
J. Must NOT Appear: FastAPI, Firebase, Machine Learning models, cloud services.
K. Version Differences: 
   - Report Version: Use `stateDiagram-v2`. Include all exact threshold numbers, explicit transition logic, and exact sensor names.
   - PPT Version: Use `flowchart LR`. Group into high-level phases (Sensing -> Logic -> Action). Remove specific numbers, focus on visual flow and readability.
L. Academic Readability: Keep state names clean (e.g., `Idle`, not `STATE_IDLE`).
M. Visual Complexity: Avoid crossing lines where possible; use clear conditional branches.
N. Verification Checklist:
   - [ ] Did you generate both the Report and PPT versions in the HTML?
   - [ ] Are all pump threshold conditions exact in the Report version?
   - [ ] Is it completely isolated from the cloud?

==================================================
CLAUDE PROMPT 2 — HARDWARE / WIRING / POWER
==================================================
A. Diagram Title: Edge Node Hardware Wiring and Power Distribution
B. Recommended Location: Chapter 3 / System Architecture
C. Purpose: To show the physical connections, GPIO mappings, and dual power rails (5V and 3.3V) to protect the ESP32 ADC.
D. Exact Project Facts:
   - pH: GPIO34 (ADC1), powered via 3.3V (safety).
   - TDS: GPIO35 (ADC1), powered via 3.3V.
   - Temp: GPIO32.
   - HC-SR04: Trig=GPIO5, Echo=GPIO18, powered via 5V.
   - Drain Pump Relay: GPIO25.
   - Refill Pump Relay: GPIO26.
   - Feeder Servo: GPIO13.
E. Components: ESP32 WROOM-32, 5V Power Rail, 3.3V Power Rail, Sensors (pH, TDS, Temp, HC-SR04), Actuators (Drain Relay, Refill Relay, Servo).
F. Connections: Power lines (VCC/GND) and Data lines with GPIO labels.
G. Direction of Flow: Sensors -> ESP32 -> Actuators. Power -> All components.
H. Important Distinctions: Distinguish between the 5V power subsystem (Pumps, Ultrasonic) and the 3.3V logic subsystem (ESP32, pH, TDS) to highlight the voltage drop protection mentioned in the report.
I. Exact Labels: "GPIO34", "GPIO35", "GPIO32", "GPIO5", "GPIO18", "GPIO25", "GPIO26", "GPIO13", "5V Rail", "3.3V Rail".
J. Must NOT Appear: Generic Arduino models, ML pipelines.
K. Version Differences:
   - Report Version: Use `flowchart TD`. Use a distinct subgraph for Power and subgraph for ESP32. Label every single GPIO pin.
   - PPT Version: Use `flowchart LR`. Show just 3 big structural blocks (3.3V Sensors, ESP32 Controller, 5V Actuators). Omit specific GPIO numbers for presentation clarity.
L. Academic Readability: Use clear, technical node names.
M. Visual Complexity: Group sensors by power requirement to reduce line clutter.
N. Verification Checklist:
   - [ ] Are the exact GPIO numbers used in the Report version?
   - [ ] Is the pH sensor explicitly shown on the 3.3V rail?
   - [ ] Are the relays and actuators separated from the analog sensors?

==================================================
CLAUDE PROMPT 3 — SOFTWARE / TELEMETRY / ML DATA FLOW
==================================================
A. Diagram Title: Software Pipeline and Machine Learning Telemetry Flow
B. Recommended Location: Chapter 3 / Data Pipeline
C. Purpose: To detail how data moves from the edge, through cloud sync, to the ML models, and to the UI.
D. Exact Project Facts:
   - ESP32 sends telemetry to Firebase Realtime Database and FastAPI.
   - FastAPI serves three models:
     - Model 1: River Forecast (Linear Regression, Bahadurabad SW46.9L).
     - Model 2: Pond TDS Forecast (+60 min).
     - Model 3: Water-Quality Anomaly Detection (Isolation Forest, unsupervised).
E. Components: ESP32, Firebase RTDB, FastAPI Backend, Model 1 (River Forecast), Model 2 (TDS Forecast), Model 3 (Anomaly Detection), Web Dashboard.
F. Connections: ESP32 -> Firebase & FastAPI. FastAPI -> Models -> FastAPI. FastAPI & Firebase -> Web Dashboard.
G. Direction of Flow: Left to right (Edge -> Data Store -> ML -> Presentation).
H. Important Distinctions: Clearly show that Model 3 is UNSUPERVISED. Distinguish between live IoT data (feeding Models 2 & 3) and regional API data (feeding Model 1).
I. Exact Labels: "Firebase Realtime Database", "FastAPI backend", "Model 1: River Forecast (Linear Regression)", "Model 2: TDS Forecast", "Model 3: Anomaly Detection (Isolation Forest)".
J. Must NOT Appear: Training loops, cross-validation splits, accuracy metrics.
K. Version Differences:
   - Report Version: Detailed `flowchart LR` showing exact database splits, all 3 models mapped to their respective algorithms, and explicit data payloads.
   - PPT Version: High-level `flowchart LR` block diagram (Edge IoT -> Cloud Servers -> ML Services -> Web Dashboard). Group the 3 models into a single "ML Analytics" box.
L. Academic Readability: Group the 3 models inside a "Machine Learning Services" subgraph in the Report version.
M. Visual Complexity: Keep data flows generic (e.g., "Telemetry Payload" rather than listing all 5 JSON keys).
N. Verification Checklist:
   - [ ] Is Model 3 labeled as Isolation Forest?
   - [ ] Is Model 1 labeled as Linear Regression?
   - [ ] Does the ESP32 connect to Firebase/FastAPI?

==================================================
CLAUDE PROMPT 4 — DASHBOARD INFORMATION ARCHITECTURE
==================================================
A. Diagram Title: Web Dashboard Information Architecture
B. Recommended Location: Chapter 5 / UI & Alerts
C. Purpose: To show how the frontend UI organizes live telemetry, manual controls, and ML insights.
D. Exact Project Facts:
   - Dashboard internal warning threshold for floods is 18.55 m (Operational safety buffer).
   - Dashboard shows live pH, TDS, Temp, and Water Level (tank percentage).
   - Dashboard provides pump controls (fetched via `app.js` fbGet("pumps")).
   - Dashboard renders Anomaly Alerts from Model 3 and River Forecasts from Model 1.
E. Components: Main UI, Live Sensor Tiles, Pump Control Panel, Flood Forecast View, Anomaly Alert Banner.
F. Connections: Hierarchy from the Main UI down to specific dashboard components, showing data sources.
G. Direction of Flow: Top-down hierarchical tree.
H. Important Distinctions: Separate physical telemetry UI (Sensor Tiles, Pump Controls) from predictive ML UI (Forecasts, Anomaly Alerts).
I. Exact Labels: "18.55m Dashboard Warning Threshold", "Live Sensor Tiles (pH, TDS, Temp, Level)", "Pump Overrides".
J. Must NOT Appear: Code-level implementations, CSS frameworks.
K. Version Differences:
   - Report Version: Deep hierarchical `flowchart TD` showing exactly what ML model or database feeds into what UI panel.
   - PPT Version: Simple 4-box mindmap or flattened `flowchart TD` (Dashboard -> Live Sensors, Manual Controls, AI Forecasts, Anomaly Alerts).
L. Academic Readability: Use rectangular nodes with clear structural alignment.
M. Visual Complexity: Limit to 3 depth levels.
N. Verification Checklist:
   - [ ] Is the 18.55m warning threshold explicitly mentioned in the Report version?
   - [ ] Are both telemetry and ML components represented?

==================================================
CLAUDE PROMPT 5 — HIGH-LEVEL SYSTEM OVERVIEW
==================================================
A. Diagram Title: 5-Tier Cyber-Physical System Architecture
B. Recommended Location: Chapter 1 / Introduction
C. Purpose: To provide the 10,000-foot view of the AquaShield project framework.
D. Exact Project Facts:
   - 5 Tiers: Physical Sensors/Actuators, Edge Computing, Cloud Telemetry, ML Analytics, User Interface.
   - Pilot regional focus for Model 1: Bahadurabad Transit (SW46.9L) on the Jamuna River.
E. Components: The 5 discrete tiers, summarizing the technologies inside them (ESP32, Firebase, FastAPI, Models, Web Dashboard).
F. Connections: Vertical or horizontal flow representing the cyber-physical stack.
G. Direction of Flow: Bottom-up (Physical to UI) or Left-to-Right.
H. Important Distinctions: Must clearly identify the Bahadurabad station as a "Regional Pilot" within the ML Analytics tier, not a country-wide deployment.
I. Exact Labels: "Tier 1: Physical", "Tier 2: Edge (ESP32)", "Tier 3: Cloud Telemetry (Firebase)", "Tier 4: ML Analytics (FastAPI)", "Tier 5: User Interface".
J. Must NOT Appear: Specific GPIO pins, exact HTTP/MQTT packet structures, training parameters.
K. Version Differences:
   - Report Version: Vertical OSI-like stack (`flowchart TD`) with clear descriptions and sub-technologies listed inside each tier.
   - PPT Version: Clean, horizontal pipeline (`flowchart LR`) showing the 5 tiers simply from Physical to UI with minimal text.
L. Academic Readability: Align subgraphs logically to represent the OSI-like stack of the system.
M. Visual Complexity: Keep intra-tier connections minimal; focus on inter-tier data flow.
N. Verification Checklist:
   - [ ] Are exactly 5 tiers explicitly labeled?
   - [ ] Is Bahadurabad SW46.9L mentioned as a regional pilot in the Report version?

==================================================
FINAL CROSS-DIAGRAM CONSISTENCY CHECK
==================================================
- **Project Name:** AquaShield
- **ESP32 Terminology:** Edge Node / ESP32 WROOM-32
- **GPIO Mappings:** Defaults to the report's authoritative mapping (e.g. Temp on GPIO32).
- **FSM Terminology:** Local Control Loop / Offline Edge Fail-Safe
- **ML Models:** Model 1 (Linear Regression), Model 2 (TDS Forecast), Model 3 (Isolation Forest).
- **Scope:** Model 1 is strictly a Regional Pilot for Bahadurabad Transit (SW46.9L).
