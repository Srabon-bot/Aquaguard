# Slide 1

AquaShield: Intelligent Aquaculture Monitoring and Adaptive Protection
System Using Machine Learning and Internet of Things (IoT)

Group Information (Group 11) 1. Md. Shahriar hossain srabon (ID:
0432310005101056) 2. Md. Mahfuz (ID: 0432310005101057) 3. Hrithik saha
(ID: 0432310005101071)

Supervisor Sultana Rokeya Naher Associate Professor Department of
Computer Science & Engineering University of Information Technology and
Sciences (UITS)

Department of Computer Science & Engineering

# Slide 2

Contents

• Introduction • Problem Statement • Objectives • Related Works & Gaps

• 5-Tier Methodology • Data Collection & Datasets • Hardware & Software
Tools • Outcome & Sustainability

• Result Analysis (Sensors/ML) • Contribution Table • System
Demonstration • Conclusion & Future Work • References & Q/A

Department of Computer Science & Engineering

# Slide 3

Introduction

• Aquaculture's Crucial Economic Role: Fisheries and aquaculture
contribute 3.5% to Bangladesh's national GDP, 26% to agricultural GDP,
and fulfill over 60% of national animal protein consumption (DoF 2023).
• High-Density Intensification: Major aquaculture districts (Mymensingh,
Bogura, Jamalpur) practice intensive culture of Pangasius and Tilapia
with dense stocking, causing heavy bio-waste accumulation. • Silent
Water Toxicity Catastrophes: Elevated water temperature and alkaline pH
transform harmless ammonium ions into toxic un-ionized ammonia gas
(NH3), which can kill an entire pond of fish overnight without prior
warning. • Monsoon River Surge Vulnerability: Low-lying fish farms in
the Jamuna River basin face recurrent monsoon flash floods that overtop
earthen perimeter dikes, washing away mature fish stocks in hours. •
AquaShield Innovation: An integrated cyber-physical solution combining
affordable (\<\$60 USD) IoT edge automation with 3 predictive Machine
Learning models for dual-horizon pond protection.

Department of Computer Science & Engineering

# Slide 4

Problem Statement

• 1. Water Quality Blindness: Small-scale farmers rely on weekly manual
water testing or visual pond inspection. This fails to detect rapid
nocturnal dissolved oxygen crashes and sudden chemical toxicity shifts
before mortality begins. • 2. No Automated Protective Action: Pond
operations rely on manual labor. When acute toxicity or low water levels
occur at night, farm hands are asleep or away, resulting in preventable
mass fish die-offs. • 3. Data Blindness & Overfeeding: Without
continuous sensor telemetry, farmers feed arbitrarily. Uneaten feed
settles on the pond floor, driving up Total Dissolved Solids (TDS) and
generating toxic hydrogen sulfide and ammonia. • 4. Devastating Monsoon
River Floods: Sudden Jamuna River surges submerge ponds without
localized advance warning. Farmers have zero time to raise perimeter
netting or conduct emergency harvesting, wiping out years of investment.

Department of Computer Science & Engineering

# Slide 5

Objectives

• Primary Goal: Develop and evaluate an affordable (\<\$60 USD),
dual-horizon cyber-physical aquaculture automation and early-warning
system tailored for Bangladeshi fish farmers. • 1. Multi-Sensor IoT Edge
Node: Interface an ESP32 microcontroller with analog pH, analog TDS,
DS18B20 digital temperature, and HC-SR04 ultrasonic depth sensors with
30-second continuous sampling. • 2. Local Edge FSM with Offline Buffer:
Program a Finite State Machine in C++ controlling 4 opto-isolated relays
(drain, refill, aerator, feeder) with SPIFFS flash buffering to
guarantee zero data loss during internet outages. • 3. Macro River Flood
Forecasting (Model 1): Develop multi-day river water-level forecasting
(+1 to +14 days) for Jamuna River at Bahadurabad using 23 years of BWDB
hydrometry and ERA5 rainfall, validated via Leave-One-Year-Out (LOYO)
CV. • 4. Micro Pond TDS Forecasting (Model 2): Build short-horizon (+60
min) TDS kinetics forecasting using rolling telemetry features,
explainable via SHAP (SHapley Additive exPlanations). • 5. Unsupervised
Anomaly Detection (Model 3): Deploy Isolation Forest to detect
multivariate toxic water combinations without requiring labeled failure
datasets.

Department of Computer Science & Engineering

# Slide 6

Related Works

Key Studies in Literature: • Saha et al. (2018) \[Arduino Uno\]:
Monitored pH, Temp & DO with SMS alerts; lacked automated relay control,
offline buffer, and flood warning (\$120). • Raju et al. (2020)
\[Raspberry Pi\]: Pumps automated; high power consumption, partial
offline resilience, no river flood modeling (\$180). • Chen et
al. (2023) \[Industrial PLC\]: Optical DO probe with deep LSTM
forecasting; highly capable but cost-prohibitive for rural farms
(\$1,500+). • Ahmed et al. (2024) \[ESP32\]: Basic threshold relay
actuation; lacked multivariate anomaly detection and predictive flood
forecasting (\$85). Identified Technical Gaps Resolved by AquaShield: •
Dual-Horizon Integration: Linked macro river flood forecasting (+1 to
+14d) with micro pond automated dike pump protection. • Edge Resilience
& Zero Loss: Local FreeRTOS FSM operates pumps and buffers 2,000
readings in SPIFFS flash during Wi-Fi outages. • Leakage-Free Flood
Validation: Replaced leaky random K-Fold CV with Leave-One-Year-Out
(LOYO) cross-validation. • Multivariate Anomaly Detection: Isolation
Forest catches lethal interactions (pH 8.4 at 32°C) that pass static
univariate thresholds.

Department of Computer Science & Engineering

# Slide 7

Methodology

Department of Computer Science & Engineering

Figure 7.1: AquaShield 5-Tier Cyber-Physical Architecture & Data Flow
Pipeline

# Slide 8

Data Collection/System Architecture

• 1. Macro River Hydrometric Dataset (Model 1): Source: Bangladesh Water
Development Board (BWDB) Hydrology Division for Station SW46.9L (Jamuna
River at Bahadurabad Transit). Covers 23 Hydrological Years (2000--2022
daily water levels, 8,401 observations). • Meteorological Catchment
Forcing: ECMWF ERA5 atmospheric reanalysis daily precipitation data over
the Brahmaputra-Jamuna upstream basin. Features include 3-day and 7-day
cumulative rainfall momentum. • 2. Micro Pond IoT Telemetry Dataset
(Models 2 & 3): Continuous 30-second multi-parameter telemetry stream
from our physical hardware sensor node deployed in experimental
aquaculture tanks: pH (0--14), TDS (0--1000 ppm), Temperature (°C), and
Water Depth (cm). • Engineered Telemetry Features: Temporal rolling
statistics (1-hour, 6-hour, and 24-hour moving averages), rate-of-change
deltas (ΔTDS/Δt, ΔpH/Δt), and temperature-compensated conductivity. • 3.
Cloud Ingestion Pipeline & Storage: MQTT broker (Mosquitto) receives
30-sec JSON payloads with QoS 1. Stored in MongoDB Atlas Time-Series
Collections indexed by device ID and UTC timestamp for sub-second
retrieval.

Department of Computer Science & Engineering

# Slide 9

Use of Tools (Software/Hardware)

Department of Computer Science & Engineering

Hardware Components & Sensors: • ESP32 NodeMCU-32S: 240 MHz Dual-Core
MCU, 4MB Flash, Wi-Fi 802.11 b/g/n, FreeRTOS. • pH-4502C Sensor: Analog
glass-bulb probe with signal conditioning board (±0.05 pH). • Analog TDS
Sensor: Waterproof probe measuring dissolved solids (0--1000 ppm,
±2.8%). • DS18B20 Temp Probe: Waterproof 1-Wire digital temperature
probe with 4.7kΩ pullup (±0.15°C). • HC-SR04 Ultrasonic: Water depth
sensor (2--400 cm) with 1kΩ/2kΩ voltage divider protecting GPIO. •
4-Channel Relay Module: 5V opto-isolated triggers for Drain Pump, Refill
Pump, Aerator, Feeder. • Dual-Rail Power Circuit: 12V 5A adapter +
LM2596 step-down buck converter + 1N4007 diodes.

Software, Backend & ML Stack: • Embedded Firmware: Arduino C++, FreeRTOS
Core 0/1 tasks, SPIFFS flash buffer. • Cloud Telemetry Broker: Mosquitto
MQTT Broker handling 30-sec sensor JSON packets. • REST API &
Microservices: Node.js and Express.js REST API for data validation and
actuation. • Database Engine: MongoDB Atlas Time-Series Collections for
efficient telemetry storage. • Real-Time WebSockets: Socket.io engine
powering the live zero-refresh web dashboard. • Machine Learning Core:
Python 3.11, Scikit-learn, XGBoost, SHAP (SHapley Explanations). •
Farmer Notification: Telegram Bot API with push alerts and interactive
override buttons.

# Slide 10

Outcome/Impact of the Project (Economic/Environmental/Sustainability)

• 1. Economic Affordability: Total system cost is under 7,200 BDT
(\~\$58 USD). Delivers a 98% cost reduction compared to commercial PLC
systems (\$3,500), making cyber-physical protection affordable for rural
smallholders. • 2. Preventing Catastrophic Fish Loss: Eliminates silent
nighttime mass fish die-offs and provides 72-hour advance flood warning,
safeguarding 50,000 to 300,000 BDT of fish stock per acre. • 3.
Environmental Sustainability: Automated aeration and water circulation
prevents toxic eutrophication and reduces dependence on harsh chemical
treatments. • 4. Operational Autonomy: Automated feeding prevents
decomposing feed overload on the pond bed, while local edge FSM operates
continuously without internet dependency.

Department of Computer Science & Engineering

# Slide 11

Result Analysis: Sensor Precision & River Flood Model

Department of Computer Science & Engineering

• Sensor Precision Findings: pH error reduced by 88.1% (±0.05 pH,
R²=0.994); TDS error reduced by 67.1% (±2.8%); Temp ±0.15°C; Depth
±0.4cm. Local FSM relay actuation latency \<500 ms with 100% SPIFFS
recovery. • Model 1 Flood Forecasting (LOYO CV): Linear Regression
outperforms Random Forest & XGBoost at extreme flood stages! Trees
saturate at training maximums, while linear models extrapolate rising
trajectories. At +3d lead horizon: RMSE=0.3082m, NSE=0.9851 (+21.19%
skill over baseline).

# Slide 12

Result Analysis: Pond ML & Multivariate Anomaly Detection

Department of Computer Science & Engineering

• Model 2 Pond TDS Kinetics (SHAP): Evaluated +60m ahead: Linear model
achieved RMSE 6.70 ppm (R²=0.963), outperforming complex trees that
overfitted ADC noise. SHAP confirms physical kinetics: 6h rolling mean
(62.4%) and lag-1 TDS (24.1%) dominate predictions. • Model 3 Isolation
Forest Anomaly Detection: Isolates anomalous contamination with shallow
tree cuts. Successfully flags multivariate toxicity (e.g., pH 8.4 at
32°C triggering lethal un-ionized ammonia) that pass univariate Z-score
thresholds unnoticed.

# Slide 13

Contribution

  --------------------------------------------------------------------------
  Student ID & Name                      Role & Technical Contribution
  -------------------------------------- -----------------------------------
  0432310005101056`<br>`{=html}Md.       • Hardware Circuit Fabrication &
  Shahriar hossain srabon                Power Rail
                                         Engineering:`<br>`{=html} Designed
                                         dual-rail 12V/5V LM2596 buck
                                         circuit and 1N4007 inductive
                                         snubber protection to eliminate
                                         ESP32 brownouts.`<br>`{=html}•
                                         Sensor Interfacing & Laboratory
                                         Calibration:`<br>`{=html} Wired and
                                         calibrated pH-4502C (buffer slope
                                         tuning), analog TDS probe, DS18B20
                                         digital temp, and HC-SR04
                                         ultrasonic sensor.`<br>`{=html}•
                                         Actuation Layer & Mechanical
                                         Prototype Assembly:`<br>`{=html}
                                         Integrated opto-isolated 4-channel
                                         relay drivers (drain/refill pumps,
                                         aerator) and IP65 waterproof
                                         outdoor enclosure fabrication.

  0432310005101057`<br>`{=html}Md.       • ESP32 Firmware Development & Edge
  Mahfuz                                 Finite State Machine:`<br>`{=html}
                                         Engineered non-blocking C++
                                         FreeRTOS tasks (Core 0 telemetry,
                                         Core 1 control) and SPIFFS flash
                                         buffer for zero data
                                         loss.`<br>`{=html}• Cloud Telemetry
                                         & Microservices
                                         Backend:`<br>`{=html} Configured
                                         Mosquitto MQTT broker, Node.js &
                                         Express.js REST API endpoints, and
                                         MongoDB Atlas time-series
                                         schema.`<br>`{=html}• User
                                         Presentation & Notification
                                         Pipeline:`<br>`{=html} Built the
                                         responsive real-time web dashboard
                                         using Socket.io and Chart.js, and
                                         implemented the automated Telegram
                                         alert bot.

  0432310005101071`<br>`{=html}Hrithik   • Data Acquisition & Hydrometric
  saha                                   Data Preprocessing:`<br>`{=html}
                                         Collected and preprocessed 23 years
                                         (2000--2022) of BWDB Jamuna River
                                         water levels and ERA5 catchment
                                         precipitation data.`<br>`{=html}•
                                         Machine Learning Engineering
                                         (Models 1, 2, and 3):`<br>`{=html}
                                         Trained and benchmarked Model 1
                                         (LOYO flood forecasting), Model 2
                                         (TDS rolling kinetics with SHAP),
                                         and Model 3 (Isolation
                                         Forest).`<br>`{=html}• Model
                                         Validation & Performance
                                         Benchmarking:`<br>`{=html}
                                         Conducted feature ablation,
                                         residual diagnostics, and holdout
                                         cross-validation proving linear
                                         extrapolation superiority.
  --------------------------------------------------------------------------

\*Note: Each row corresponds to individual member IDs and their specific
technical responsibilities.

Department of Computer Science & Engineering

# Slide 14

Conclusion

• Full-Stack Cyber-Physical System: AquaShield successfully bridges the
gap between low-cost IoT edge automation and predictive machine
learning, built entirely under \$58 USD (\~6,950 BDT). • Dual-Horizon
Protection: Provides micro-level pond protection (\<500 ms automated
pump/aerator response) and macro-level flood protection (3 to 7 days
advance river surge warning). • Methodological Rigor: Proved that
regularized linear regression outperforms complex decision tree
ensembles (RF/XGBoost) during record flood events due to continuous
linear extrapolation without step-function saturation. • Explainable &
Unsupervised Analytics: SHAP feature importance verified physical
kinetics for pond TDS forecasting, while Isolation Forest detected
multivariate ammonia toxicity without labeled failure datasets. • Edge
Resilience & Zero Data Loss: Dual-core FreeRTOS firmware and SPIFFS
flash buffer ensure 100% operational continuity and data preservation
during rural internet dropouts.

Department of Computer Science & Engineering

# Slide 15

Future Work

• 1. LoRaWAN Long-Range Mesh Network: Transition from Wi-Fi to LoRaWAN
(868/915 MHz). This enables a single central gateway to monitor 50+
distributed rural fish ponds across a 10 km radius with minimal battery
power consumption. • 2. On-Device TinyML Inference: Quantize the machine
learning models using TensorFlow Lite for Microcontrollers (TFLM) to run
inference directly on the ESP32, achieving 100% offline intelligence
without any cloud dependency. • 3. Solar & Battery Off-Grid Power Unit:
Integrate a 50W monocrystalline solar panel, MPPT charge controller, and
a 12V LiFePO4 battery pack to allow complete self-sufficient deployment
in remote river chars and rural areas without grid electricity. • 4.
Computer Vision Disease Diagnosis: Incorporate an underwater camera node
with Edge AI to detect early visual symptoms of fungal infections
(Saprolegniasis), fin rot, and abnormal swimming kinetics before mass
mortality occurs.

Department of Computer Science & Engineering

# Slide 16

Demonstration

• Step 1: Multi-Sensor Live Stream: The ESP32 samples pH, TDS, temp, and
water depth every 30 seconds. Readings are filtered via 64-sample moving
average and transmitted via MQTT to the cloud backend with sub-second
latency. • Step 2: Autonomous Edge Protection: If water depth drops
below 30 cm or pH exceeds safety limits, the local C++ FSM triggers the
refill or drain relay in \<500 ms without waiting for cloud commands. •
Step 3: Real-Time Telegram Alerts: The Telegram Bot dispatches push
notifications to the farmer's mobile device with color-coded severity
badges (Normal, Advisory, Warning, Critical) and one-touch override
controls. • Step 4: Machine Learning Analytics: The cloud dashboard
displays live +3-day flood forecasts, +60-minute TDS projection curves,
and multivariate Isolation Forest anomaly scores to assist farmer
decision-making. • Physical Demonstration Ready: Hardware prototype with
active sensor probes, 4-channel relay switches, and live web dashboard
ready for examination committee inspection.

Department of Computer Science & Engineering

# Slide 17

Reference

\[1\] Department of Fisheries (DoF), 'Yearbook of Fisheries Statistics
of Bangladesh 2022-23,' Ministry of Fisheries and Livestock, Dhaka,
Bangladesh, 2023. \[2\] Food and Agriculture Organization (FAO), 'The
State of World Fisheries and Aquaculture 2024,' FAO, Rome, Italy, 2024.
\[3\] Bangladesh Water Development Board (BWDB), 'Hydrometric Data
Portal: Daily Water Levels for Station SW46.9L (Jamuna River at
Bahadurabad),' BWDB Hydrology Division, Dhaka, 2024. \[4\] C. E. Boyd,
'Water Quality: An Introduction,' 3rd ed., Cham, Switzerland: Springer
Nature, 2020. \[5\] F. T. Liu, K. M. Ting, and Z.-H. Zhou, 'Isolation
Forest,' in Proc. 8th IEEE International Conference on Data Mining
(ICDM), Pisa, Italy, 2008, pp. 413--422. \[6\] S. M. Lundberg and S.-I.
Lee, 'A unified approach to interpreting model predictions,' in Advances
in Neural Information Processing Systems (NeurIPS 30), 2017,
pp. 4765--4774. \[7\] P. Saha, D. Biswas, and A. K. Das, 'IoT-based
automated water quality monitoring and alert system for fish farming,'
in Proc. IEEE ICSCEE, 2018, pp. 1--6.

Department of Computer Science & Engineering

# Slide 18

Q & A

Thank You! Question & Answer Session We welcome questions, suggestions,
and valuable feedback from the respected Examination Committee.
AquaShield: Intelligent Aquaculture Monitoring and Adaptive Protection
System Candidates: Srabon (056) \| Mahfuz (057) \| Hrithik (071)
Supervisor: Sultana Rokeya Naher, Associate Professor Department of
Computer Science & Engineering, UITS

Department of Computer Science & Engineering
