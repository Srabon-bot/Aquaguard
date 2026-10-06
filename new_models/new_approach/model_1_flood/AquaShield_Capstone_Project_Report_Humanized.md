 AquaShield: Intelligent Aquaculture Monitoring and
Adaptive Protection System Using Machine Learning and
                          IoT
                                                 By

                   Md. Shahriar Hossain Srabon (ID: 0432310005101056)
                             Md. Mahfuz (ID: 0432310005101057)
                             Hrithik Saha (ID: 0432310005101071)

                      Department of Computer Science and Engineering

                              Faculty of Science and Engineering

A Capstone Project Submitted in partial fulfillment of the requirements for the degree of Bachelor of
                           Science in Computer Science and Engineering

                                          Supervised By

                                     Sultana Rokeya Naher

                                        Associate Professor

                         Department of Computer Science and Engineering




             University of Information Technology and Sciences (UITS)
                                  Baridhara J Block, Dhaka 1212

                                           October, 2026
Declaration
The capstone project work entitled "AquaShield: Intelligent Aquaculture Monitoring and
Adaptive Protection System Using Machine Learning and IoT" is a authentic record of work
carried out by Md. Shahriar Hossain Srabon (ID: 0432310005101056), Md. Mahfuz (ID:
0432310005101057), and Hrithik Saha (ID: 0432310005101071) under the supervision of
Sultana Rokeya Naher, Associate Professor, Department of Computer Science and Engineering
(CSE), University of Information Technology and Sciences (UITS), Dhaka, Bangladesh.

This work, in whole or in part, has not been submitted elsewhere for the award of any degree or
diploma.

Candidates:

------------------------------------------------------------------------

➢​ Md. Shahriar Hossain Srabon

Student ID: 0432310005101056

Department of Computer Science and Engineering, UITS

------------------------------------------------------------------------

➢​ Md. Mahfuz

Student ID: 0432310005101057

Department of Computer Science and Engineering, UITS

------------------------------------------------------------------------

➢​ Hrithik Saha

Student ID: 0432310005101071

Department of Computer Science and Engineering, UITS


Approval
This is to certify that the capstone project work submitted by Md. Shahriar Hossain Srabon
(ID: 0432310005101056), Md. Mahfuz (ID: 0432310005101057), and Hrithik Saha
(ID: 0432310005101071) entitled "AquaShield: Intelligent Aquaculture Monitoring and Adaptive
Protection System Using Machine Learning and IoT" has been examined and approved by the
Capstone Project Review Committee in partial fulfillment of the requirements for the degree of
Bachelor of Science in Computer Science and Engineering (CSE) in the Department of Computer
Science and Engineering (CSE), University of Information Technology and Sciences (UITS),
Dhaka, Bangladesh in Autumn 2026.


                                                          2
CAPSTONE PROJECT REVIEW COMMITTEE

➢​ ................................................................

[Head of Department Name]

Head of the Department

Department of Computer Science and Engineering (CSE)

University of Information Technology and Sciences (UITS)

(Convener)

➢​ ................................................................

Sultana Rokeya Naher

Associate Professor

Department of Computer Science and Engineering (CSE)

University of Information Technology and Sciences (UITS)

(Supervisor)

➢​ ................................................................

[External Examiner Name]

Professor / External Expert

Department of Computer Science and Engineering

University of Information Technology and Sciences (UITS)

(Member)

➢​ ................................................................

[Internal Coordinator Name]

Coordinator, Capstone Project Committee

Department of Computer Science and Engineering (CSE)

University of Information Technology and Sciences (UITS)

(Member Secretary)




                                                                      3
Acknowledgement - done

We would like to express our gratitude to Almighty Allah for providing us with the patience,
health and capacity to finish our capstone engineering project.

We would like to thank our supervisor Sultana Rokeya Naher, Associate Professor, Computer
Science and Engineering, University of Information Technology and Sciences (UITS) for her
guidance and support. Her constant guidance, frequent feedback and encouragement helped us to
tackle the actual hardware problems, design the right database and validate our machine learning
models properly.

We are also grateful to the Head of the Department of Computer Science and Engineering, and
our teachers and laboratory staff at UITS for the support and facilities provided to us during the
study in the Department.

The Bangladesh Water Development Board (BWDB) and Flood Forecasting and Warning Centre
(FFWC) have been providing historical records of river gauges, which is greatly appreciated. We
also would like to thank Open-Meteo for supplying the free catchment rainfall data from ERA5.

Last but not the least, we would like to thank our parents and relatives for their constant support
and sacrifices throughout our college days. We also thank each other for working together as a
team with dedication to build AquaShield.


Justification Report
Below is the Course Outcome to Program Outcome (CO-PO) Mapping, Justification of PO
through COs, Complex Engineering Problem (CEP) Justification, and Range of Complex
Engineering Activities (CEA) Report for our project titled "AquaShield: Intelligent Aquaculture
Monitoring and Adaptive Protection System Using Machine Learning and IoT".

CO-PO Mapping
CO-PO Mapping Matrix for AquaShield

  CO No.             Description of CO        KP               CP              CA
                     Apply engineering
                     fundamentals and
                     computing
                     knowledge to
                     identify and translate
                     real-life aquaculture
  CO1                                         K1, K2, K3, K4   -               -
                     water quality
                     problems and
                     monsoon flood
                     threats into an
                     intelligent IoT and
                     ML solution.



                                                      4
CO No.   Description of CO       KP           CP              CA
         Identify, formulate,
         and analyze water
         quality requirements
         (pH, TDS,
         temperature, depth)
CO2                              K2, K3, K4   WP1, WP2, WP3   -
         and flood threshold
         limits to reach
         substantiated
         conclusions using
         data.
         Design and build an
         integrated system
         combining an ESP32
         sensor node, local
CO3      relay control logic,    K3, K5, K6   WP1, WP3, WP5   -
         cloud data storage,
         and machine
         learning prediction
         models.
         Select and apply
         modern hardware
         and software tools
         including ESP32,
         Arduino C++,
CO4                              K3, K5, K6   WP1, WP3, WP4   -
         Firebase Realtime
         Database, Python
         FastAPI,
         Scikit-learn, and
         XGBoost.
         Function effectively
         as individual
         contributors and as a
         3-member
CO5                              -            -               -
         engineering team
         with clear task
         distribution and
         regular coordination.
         Demonstrate project
         management and
         budgeting skills by
         keeping the total
CO6                              -            -               -
         prototype hardware
         cost under 7,200
         BDT (~\$60) for
         rural fish farmers.
         Conduct
         experimental
         investigations using
         laboratory buffer
         solutions for sensor
CO7                              K6, K8       WP1, WP2, WP3   -
         calibration and 15
         years of river data
         with
         Leave-One-Year-Out
         validation.
         Assess the
         real-world impact of
         the project on rural
         aquaculture,
CO8                              K8, K7       WP1, WP3, WP4   -
         protecting fish from
         mortality and saving
         farmers from severe
         financial loss.




                                          5
  CO No.            Description of CO       KP       CP                  CA
                    Evaluate
                    environmental
                    sustainability by
                    minimizing water
  CO9               pumping, preventing     K7       -                   -
                    chemical
                    over-concentration,
                    and avoiding feed
                    wastage.
                    Commit to
                    professional
                    engineering ethics by
                    reporting true
                    empirical results,
  CO10                                      K7       -                   -
                    citing all references
                    properly, and
                    explaining model
                    predictions with
                    SHAP.
                    Communicate
                    engineering work
                    clearly through a
                                                                         EA1, EA2, EA3,
  CO11              complete written        -        -
                                                                         EA5
                    technical project
                    book and oral
                    defense presentation.
                    Recognize the need
                    for lifelong learning
                    by researching future
                    system extensions
  CO12                                      -        -                   -
                    like on-device
                    TinyML and
                    LoRaWAN wireless
                    networks.


Justification of PO through COs
Justification of PO through COs for AquaShield

                                                          Justification (with Specific Report
  CO No.                           PO
                                                          References)
                                                          We applied basic electronics, sensor
                                                          physics (Nernst equation for pH,
                                                          electrical conductivity for TDS,
                                                          ultrasonic time-of-flight), and
  CO1                              PO1                    machine learning regression to solve
                                                          real-world pond water deterioration
                                                          and river flood overflow in
                                                          Bangladesh. (Reported in Section
                                                          1.2, 3.3, and 3.6).
                                                          We formulated the technical
                                                          requirements for pond water
                                                          monitoring and river flood warnings,
                                                          defining mathematical conversion
  CO2                              PO2                    formulas, 1-hour TDS lag features,
                                                          and water danger thresholds
                                                          evaluated using RMSE, MAE, and
                                                          NSE metrics. (Reported in Section
                                                          1.3, 3.6, and 5.3).




                                                 6
                    Justification (with Specific Report
CO No.   PO
                    References)
                    We designed and assembled the
                    complete system: an ESP32 edge
                    node with optocoupler-isolated
                    relays, local autonomous FSM rules
                    for the pumps and the servo feeder, a
CO3      PO3
                    Firebase Realtime Database cloud
                    layer, and three machine learning
                    models served by a Python FastAPI
                    backend. (Reported in Chapters 3
                    and 4).
                    We selected and used standard
                    modern engineering tools including
                    ESP32 32-bit MCU,
                    PlatformIO/Arduino IDE, Firebase
CO4      PO5
                    Realtime Database, Python FastAPI,
                    Python Scikit-learn, XGBoost, and
                    SHAP. (Reported in Section 4.2 to
                    4.6).
                    Our 3-member team divided tasks
                    effectively: Srabon handled hardware
                    fabrication and power wiring,
                    Mahfuz integrated the ESP32 with
                    the Firebase Realtime Database and
CO5      PO9
                    built the web dashboard, and Hrithik
                    developed the Python FastAPI
                    backend and the ML flood
                    forecasting and anomaly detection
                    models. (Reported in Section 4.1).
                    We managed component
                    procurement and prepared a detailed
                    Bill of Materials totaling 6,570 BDT
CO6      PO11       (\$55.15 USD), proving our system is
                    affordable for marginal fish farmers
                    in Bangladesh. (Reported in Section
                    3.3, Table 3.1).
                    We conducted practical
                    investigations: we calibrated the pH
                    sensor with vinegar (pH 2.4) and
                    baking soda (pH 8.3) reference
                    solutions, evaluated sensor accuracy
                    against standard buffer solutions, and
CO7      PO4
                    validated our river flood model on 15
                    years (2008--2022) of BWDB
                    records using Leave-One-Year-Out
                    (LOYO) cross-validation to prevent
                    data leakage. (Reported in Section
                    3.3, 3.7, 5.2, and 5.3).
                    We evaluated the socioeconomic
                    impact on rural communities:
                    preventing fish kills protects farmer
                    income, safeguards food security,
CO8      PO6
                    and avoids financial devastation
                    during monsoon river overflows.
                    (Reported in Section 1.1, 2.2, and
                    6.1).
                    We designed closed-loop control
                    rules that save water by pumping
                    only when necessary, prevent pond
CO9      PO7        pollution from excess feed, and use
                    energy-efficient 12V DC power
                    components. (Reported in Section
                    3.4 and 4.2).




                7
                                                                   Justification (with Specific Report
  CO No.                       PO
                                                                   References)
                                                                   We maintained academic honesty by
                                                                   using real observed datasets,
                                                                   reporting actual prediction errors
  CO10                         PO8                                 without bias, explaining tree
                                                                   predictions via SHAP, and properly
                                                                   citing all literature. (Reported in
                                                                   Section 5.4, 5.7, and References).
                                                                   We wrote this complete,
                                                                   well-documented technical capstone
                                                                   report adhering to UITS and IEEE
                                                                   standards, created 13 figures (Figure
  CO11                         PO10
                                                                   3.1 to Figure 5.11) and 15 numbered
                                                                   tables, and prepared slides for our
                                                                   oral defense. (Reported throughout
                                                                   the entire book and the report).
                                                                   We recognized that technology
                                                                   continues to evolve, so we studied
                                                                   and documented future upgrade paths
  CO12                         PO12                                including running TinyML directly
                                                                   on the ESP32 and adding LoRaWAN
                                                                   mesh networking. (Reported in
                                                                   Section 6.2).


Complex Engineering Problem (CEP) Justification
Complex Engineering Problem (CEP) Justification Matrix

                                                                   BAETE Criteria [24] & Project
  Attribute Category           Attribute Name & ID                 Justification (with Report
                                                                   References)
                                                                   Solving this problem required
                                                                   knowledge from multiple
                                                                   engineering fields (K4): embedded
                                                                   systems (ADC oversampling,
                                                                   voltage-divider interfacing, 3.3V
                                                                   analog sensor design), cloud data
                                                                   handling (Firebase Realtime
  1. Mandatory Attribute       Depth of Knowledge (P1)             Database, Python FastAPI REST
                                                                   services), time-series machine
                                                                   learning, and Explainable AI
                                                                   (SHAP). We studied research
                                                                   literature (K8) to handle time-series
                                                                   data leakage and peak extrapolation.
                                                                   (Reported in Section 2.4, 2.5, 3.6,
                                                                   5.3).
                                                                   We balanced conflicting constraints:
                                                                   low hardware cost (<\$60) vs. good
                                                                   sensor accuracy; real-time cloud
                               Range of Conflicting Requirements   updates vs. frequent rural internet
  2. Supporting Attribute
                               (P2)                                dropouts; and long flood forecast
                                                                   horizons (+14 days) vs. growing
                                                                   prediction error. (Reported in Section
                                                                   1.2, 3.4, 5.6).




                                               8
                                                                  BAETE Criteria [24] & Project
  Attribute Category            Attribute Name & ID               Justification (with Report
                                                                  References)
                                                                  Standard random train-test splitting
                                                                  fails on river data because it leaks
                                                                  future temporal information. We
                                                                  designed a Leave-One-Year-Out
                                                                  cross-validation scheme and
  3. Supporting Attribute       Depth of Analysis Required (P3)
                                                                  analyzed stratified water-level errors
                                                                  across 5,479 days to prove why
                                                                  linear models beat tree models during
                                                                  extreme flood crests. (Reported in
                                                                  Section 3.7, 5.3, 5.7).
                                                                  Real aquaculture ponds do not have
                                                                  labeled 'good water' vs. 'bad water'
                                                                  datasets. We handled this unfamiliar
                                                                  unsupervised scenario by combining
                                                                  sensor rate-of-change deltas with
  4. Supporting Attribute       Familiarity of Issues (P4)
                                                                  Isolation Forest, successfully
                                                                  isolating dangerous multivariate
                                                                  conditions like high pH + high
                                                                  temperature. (Reported in Section
                                                                  2.2, 3.6, 5.5).
                                                                  The parts of our system depend
                                                                  heavily on each other: hardware
                                                                  ADC calibration directly determines
                                                                  data accuracy; clean cloud data feeds
  5. Supporting Attribute       Interdependence (P7)
                                                                  the ML models; and ML flood early
                                                                  warnings give farmers lead time to
                                                                  raise perimeter netting. (Reported in
                                                                  Section 3.2, 4.7, 5.6).


Range of Complex Engineering Activities (CEA) Justification
Range of Complex Engineering Activities (CEA) Justification Matrix

                                                                  Engineering Activity Justification
  Activity ID                   Activity Title
                                                                  (with Report References)
                                                                  We utilized diverse hardware
                                                                  components (ESP32, pH-4502C,
                                                                  TDS probe, NTC thermistor,
                                                                  HC-SR04, optocoupled relays, buck
                                                                  converter), software stacks (Firebase
  A1                            Range of Resources                Realtime Database, Python FastAPI,
                                                                  vanilla HTML/CSS/JavaScript), and
                                                                  15 years of BWDB hydrological
                                                                  records and ERA5 rainfall data.
                                                                  (Reported in Chapter 3 and Chapter
                                                                  4).
                                                                  We combined macro-scale river flood
                                                                  forecasting (giving 3 to 7 days
                                                                  warning to protect pond dikes) with
                                                                  micro-scale pond water automation
  A3                            Innovation
                                                                  and unsupervised anomaly detection,
                                                                  adding SHAP explainability so
                                                                  farmers can understand the alerts.
                                                                  (Reported in Section 3.2, 3.6, 5.4).
                                                                  Our project directly helps fish
                                                                  farmers in flood-prone districts of
                                                                  Bangladesh avoid financial
                                Consequences for Society &
  A4                                                              bankruptcy, protects national food
                                Environment
                                                                  supply, reduces clean water wastage,
                                                                  and avoids toxic chemical spikes.
                                                                  (Reported in Section 1.1, 2.2, 6.1).



                                                  9
Mapping to PO10 (Communication)
●​ Written Technical Documents: Prepared the technical capstone report in accordance with the
   UITS format [25] and IEEE citation conventions.
●​ Oral Presentations: Prepared formal multimedia presentation slides for the Capstone Review
   Committee defense.
●​ Visual Representation: Presented technical figures, including the system architecture
   schematic (Figure 3.1), the LOYO validation workflow (Figure 3.2), flood-season
   hydrographs (Figure 5.3), the SHAP summary plot (Figure 5.8), and the anomaly detection
   scatter plot (Figure 5.9), together with tables summarizing hardware, control rules, and
   experimental results.


Abstract - done

Fisheries play a significant role in Bangladesh’s economy, contributing over 3.5% of the
country’s gross domestic product (GDP) and providing about 60% of its animal protein.
However, unmanaged ponds pose significant challenges for fish farmers due to seasonal flooding
and deteriorating water quality. The solution proposed in this latest project is AquaShield, an
Internet of Things (IoT)-based aquaculture monitoring and decision support system with
improved cost-effectiveness. The system includes local automation, cloud telemetry, and three
machine learning models.

The physical edge node consists of an ESP32 microcontroller and sensors for measuring pH, total
dissolved solids (TDS), water temperature, and ultrasonic water level. Drain pumps, fill pumps,
and servo-driven feeders are controlled by finite state machines (FSMs) every 30 seconds,
ensuring that local security rules remain in effect even during network outages. Data obtained
through telemetry is recorded directly in a Firebase database, while machine learning models are
used in a Python FastAPI backend.

The following projects were implemented in the machine learning framework: 1) Validation of
one-year lag in river level forecast using 15 years of BWDB data (2008–2022) and ERA5 rainfall
data (1, 3, 7, and 14 days ahead for Bahadur Labad and Yamuna Rivers), with detailed
explanation of the +17-day moving average model, and detailed report on 60-minute ahead TDS
(Total Dissolved Solids) forecast for Bahadur Labad Lake; and 3) Unsupervised multivariate
anomaly detection using disjoint forests and sensor rate-of-change features. The linear regression
achieved a mean standard error (NSE) of 0.9851 m and a mean standard error (RMSE) of 0.3082
m for the unknown validation period of 2020–2022 (i.e., +3 days). The linear regression was the
most stable model for predicting total dissolved solids (TDS) (the mean absolute error (MAE) of
this model was 7.05 ppm, and the R² was 0.888, which was acceptable), although the results
obtained from the persistence-based model were better. The cost of the prototype device was


                                               10
6,570 taka, lower than the expected target of 7,200 taka. Overall, this project highlights the
importance of using low-cost sensors, local automation, cloud telemetry, and machine learning
technologies in decision-making processes within the Bangladeshi fisheries sector.

Keywords: Internet of Things (IoT), water quality monitoring, flood warning, machine learning,
explainable artificial intelligence (SHAPE).




Preface: - done

This is the Capstone project report for the Computer Science and Engineering Department of the
Faculty of Science and Engineering at the University of Information Technology and Science at
Dhaka, Bangladesh covering Engineering design, Embedded hardware prototyping, Cloud
software development and machine learning experiments.

The project is divided into six chapters. The summary of each chapter is listed below:

Chapter 1 (Introduction) gives a description of the current condition of the aquifers in Bangladesh
with regard to worsening water quality and the flooding of the rivers during the monsoon season.
It describes why the Aquashield was needed, the objectives and technical aims, some of the
challenges and the scope of work, and some of the contributions that were made to the
Aquashield project.

Chapter 2 (Background Study): This chapter discusses water quality parameters such as pH, Total
Dissolved Solids (TDS) temperature and ammonia. It also provides an understanding about
monsoon flooding in the Jamuna basin. It will discuss pond water monitoring system with the use
of IoT. It also outlines some applications of machine learning in hydrology. Acknowledges the
difficulty in this area.

Chapter 3 (Methodology): This chapter describes a five‑layer system architecture. Contains
equations to process sensor data, and information on a sensor to operate at 3.3V using an edge
finite-state machine. It involves logic setup on Firebase Cloud Telemetry, and the development of
a FastAPI backend. It also introduces the three machine‑learning models and the validation
techniques used to validate them.

Chapter 4 (Implementation): It deals with the implementation of the ADC oversampling in the
form of ESP32 C++ firmware and hardware construction of power-supply design. It comprises of
cloud services like Firebase Realtime Database, Python FastAPI, Python machine-learning
pipelines, and much more. A web dashboard has been developed, which features banners to warn
of any conditions.



                                                11
Chapter 5 (Results Analysis and Comparison): This chapter contains the laboratory results of
calibration of the sensors. It compares the ability of model 1 to predict river floods in the next
1-14 days and give the extrapolations with safety buffer zones on the dashboard and it shows the
extrapolations of model 2 for river TDS estimation through SHAP plots. It also discusses model 3
for multivariate anomaly detection. It includes latency values of the systems and the system
evaluation's technical results.

Chapter 6 (Conclusions and Future Work): This chapter presents the conclusions and future work
of Aquashield project. Acknowledges obstacles that were faced while developing. It also submits
suggestions through TinyML (Edge Inference) and LoRaWAN (Long-range communication
networks) enhancements.

Appendix and References: Appendix A shows all Pinout connections and REST API Endpoints
of the system. 25 IEEE references are mentioned in the report. There are also placeholders for
reports, on plagiarism.




Table of Contents
Declaration​                                                                                    2
Approval​                                                                                       2
Acknowledgement​                                                                                4
Justification Report​                                                                           4
CO-PO Mapping​                                                                                  5
Justification of PO through COs​                                                                6
Complex Engineering Problem (CEP) Justification​                                                8
Range of Complex Engineering Activities (CEA) Justification​                                    9
Mapping to PO10 (Communication)​                                                               10
Abstract​                                                                                      10
Preface​                                                                                       11
List of Figures​                                                                               14
List of Tables​                                                                                15
Abbreviations and Symbols​                                                                     15
Chapter 1: Introduction​                                                                       18
   1.1 Introduction​                                                                           18
   1.2 Problem Statement​                                                                      18
   1.3 Motivation​                                                                             18



                                               12
  1.4 Aims and Objectives​                                                       19
  1.5 Challenges and Scope​                                                      20
  1.6 Contribution​                                                              20
  1.7 Conclusion​                                                                21
Chapter 2: Background Studies​                                                   22
  2.1 Introduction​                                                              22
  2.2 Aquaculture Challenges and Water Quality Dynamics in Bangladesh​           22
  2.3 Monsoon Flooding Risks and Early Warning Needs​                            23
  2.4 Review of Existing IoT Aquaculture Monitoring Systems​                     23
  2.5 Machine Learning in Hydrological Forecasting & Water Quality Prediction​   23
  2.6 Comparative Analysis of Related Works and Research Gap​                    24
  2.7 Conclusion​                                                                24
Chapter 3: Methodology​                                                          25
  3.1 Introduction​                                                              25
  3.2 Overall System Architecture and Telemetry Pipeline​                        25
  3.3 Hardware Design and Edge Sensing Layer​                                    26
  3.4 Local Edge Control Logic, Fail-Safe Automation, and Actuator Drivers​      28
  3.5 Cloud Telemetry, REST API, and Database Schema​                            29
  3.6 Machine Learning Subsystem Methodology​                                    29
  3.7 Model Validation Protocols (LOYO CV and Chronological Splitting)​          29
  3.8 Conclusion​                                                                30
Chapter 4: Implementation​                                                       31
  4.1 Introduction​                                                              31
  4.2 Hardware Fabrication, Circuit Wiring, and Power Supply Setup​              31
  4.3 ESP32 Firmware Development & Local Sensing Pipeline​                       32
  4.4 Backend & Database Service Implementation​                                 32
  4.5 Machine Learning Subsystem Implementation & Deployment Pipeline​           32
  4.6 Web Dashboard & Sensor Calibration Interface Development​                  32
  4.7 Automated Alerting Subsystem & Web Dashboard Alert Banners​                33
  4.8 Conclusion​                                                                33
Chapter 5: Result Analysis and Comparison​                                       34
  5.1 Introduction​                                                              34
  5.2 IoT Hardware Performance and Sensor Calibration Results​                   34
  5.3 Model 1 (River Flood Forecast) Experimental Evaluation​                    34
  5.4 Model 2 (Pond TDS Forecast) Results and SHAP Explainability​               40
  5.5 Model 3 (Pond Anomaly Detection) Evaluation and Diagnostic Analysis​       44

                                             13
     5.6 Real-Time Actuation and Inference Latency​                                           46
     5.7 Comprehensive Discussion & Technical Defense Insights​                               46
     5.8 Conclusion​                                                                          46
Chapter 6: Conclusion and Future Work​                                                        46
     6.1 Conclusion​                                                                          46
     6.2 Future Work​                                                                         46
Appendix A: Hardware Pin Mappings and REST API Endpoints​                                     47
     A.1 Complete Hardware Pinout Specifications​                                             48
     A.2 AquaShield REST API Endpoints Specification​                                         49
References​                                                                                   50
Plagiarism Report​                                                                            52


List of Figures
Figure 3.1: High-level 5-tier cyber-physical architecture and catchment integration schematic of
AquaShield​                                                                                   25
Figure 3.2: Leave-One-Year-Out (LOYO) cross-validation and strict holdout evaluation protocol​
30
Figure 5.1: Correlation and physical lag dynamics between catchment rainfall and Bahadurabad
river water level​                                                                            35
Figure 5.2: Model Root Mean Squared Error (RMSE) vs. forecast lead time (1 to 14 days) across
all evaluated algorithms​                                                                     36
Figure 5.3: Flood season hydrographs: observed vs. predicted water levels during major historical
monsoon flood years​                                                                          37
Figure 5.4: Model 1 feature importance distribution shifting from autoregressive water-level lags
to upstream rainfall sums​                                                                    39
Figure 5.5: Final holdout model performance on unseen 2020--2022 monsoon seasons (+3 days
lead horizon)​                                                                                40
Figure 5.6: Model 2 performance comparison bar chart across MAE, RMSE, and R² metrics​        41
Figure 5.7: Model 2 actual vs. predicted TDS time series over the held-out test dataset​      42
Figure 5.8: SHAP feature importance summary plot explaining Model 2 TDS forecasts​            43
Figure 5.9: Model 3 bivariate scatter plot (pH vs. TDS) highlighting detected multivariate
anomalies​                                                                                    44
Figure 5.10: Model 3 anomaly detection timeline traced along continuous TDS sensor readings​45
Figure 5.11: Isolation Forest anomaly score distribution and 5% contamination decision threshold​
45



                                                14
List of Tables
Table 2.1: Water Quality Thresholds and Biological Tolerance for Major Farmed Fish Species​ 22
Table 2.2: Comparative Feature Matrix of Existing Aquaculture Systems vs. AquaShield​                 24
Table 3.1: Hardware Bill of Materials (BOM) and Cost Breakdown​                                       26
Table 3.2: Summary of Primary Hardware Pin Assignments on ESP32​                                      27
Table 3.3: Summary of Edge Finite State Machine (FSM) Actuation Rules​                                28
Table 5.1: Sensor Calibration and Precision Evaluation Across Reference Measurements​                 34
Table 5.2: Bahadurabad Station Hydrological Dataset Summary (2008--2022)​                             34
Table 5.3: Hyperparameter Search Grids and Selected Optimal Values for Model 1​                       35
Table 5.4: Comprehensive LOYO Cross-Validation Performance Metrics (+1 Day Horizon)​                  36
Table 5.5: Extreme Flood Season and Peak Error Evaluation Metrics​                                    38
Table 5.6: Final Holdout Evaluation Results on Unseen 2020--2022 Monsoon Seasons (+3 Days)​
39
Table 5.7: Model 2 Pond TDS Forecasting Performance Comparison (+60 Mins Horizon)​                    40
Table 5.8: End-to-End Latency Benchmark Results​                                                      46
Table A.1: Complete Hardware Pinout and Bus Interfacing Specifications​                               48
Table A.2: AquaShield REST API Endpoints Specification (Python FastAPI ML Backend)​                   49


Abbreviations and Symbols
  Acronym / Symbol                             Full Meaning / Definition
  ADC                                          Analog-to-Digital Converter
  AI                                           Artificial Intelligence
  API                                          Application Programming Interface
                                               Board of Accreditation for Engineering and Technical
  BAETE
                                               Education
  BLE                                          Bluetooth Low Energy
  BOM                                          Bill of Materials
  BWDB                                         Bangladesh Water Development Board
  CA                                           Complex Activities
  CEA                                          Complex Engineering Activities
  CEP                                          Complex Engineering Problem
  CO                                           Course Outcome
  CP                                           Complex Problem
  CSE                                          Computer Science and Engineering
  CSS                                          Cascading Style Sheets
  CV                                           Cross-Validation
  DC                                           Direct Current
  DO                                           Dissolved Oxygen
  ERA5                                         ECMWF Reanalysis v5 Global Climate Dataset
  ESP32                                        Espressif Systems 32-bit Wi-Fi/BLE Microcontroller
  FAR                                          False Alarm Rate
  FFWC                                         Flood Forecasting and Warning Centre (Bangladesh)



                                             15
Acronym / Symbol    Full Meaning / Definition
FSM                 Finite State Machine
GPIO                General Purpose Input/Output
HTML                HyperText Markup Language
HTTP                Hypertext Transfer Protocol
IDE                 Integrated Development Environment
IEEE                Institute of Electrical and Electronics Engineers
IoT                 Internet of Things
KP                  Knowledge Profile
LOYO                Leave-One-Year-Out Cross-Validation
LSTM                Long Short-Term Memory Neural Network
MAE                 Mean Absolute Error
MCU                 Microcontroller Unit
ML                  Machine Learning
NSE                 Nash-Sutcliffe Efficiency
NTC                 Negative Temperature Coefficient
NVS                 Non-Volatile Storage
pH                  Potential of Hydrogen (Acidity/Basicity Measure)
PO                  Program Outcome
POD                 Probability of Detection (Hit Rate)
PWM                 Pulse Width Modulation
REST                Representational State Transfer
RHWL                Recorded Highest Water Level
RMSE                Root Mean Squared Error
R²                  Coefficient of Determination
SDK                 Software Development Kit
SHAP                SHapley Additive exPlanations
SPIFFS              Serial Peripheral Interface Flash File System
SVR                 Support Vector Regressor
TDS                 Total Dissolved Solids (measured in ppm)
UITS                University of Information Technology and Sciences
Wi-Fi               Wireless Fidelity (IEEE 802.11 b/g/n)
WP                  Workplace / Complex Problem Profile Attribute
XGBoost             Extreme Gradient Boosting




                   16
Chapter 1: Introduction

1.1 Introduction - Done

In Bangladesh fish farming is one of the parts of the agriculture industry. It adds than 3.5% to the
Gross Domestic Product (GDP) and gives about 60% of the animal protein people eat in the
country [1] [2]. More than 18 million people earn their livelihood from the fishing and farming
fish. Many changes in fish farming in the last 20 years have occurred from the small ponds to
more modern and active fish farming. Areas such as Mymensingh, Bogura and Jamalpur are the
localities where a considerable amount of fish is reared, for instance, Rohu (Labeo rohita), Catla
(Gibelion catla), Pangas (Pangasius hypophthalmus) and Tilapia (Oreochromis niloticus).
Increased stocking density will yield a higher fish production. This also has a large impact on the
pond environment. The carcasses of fish and uneaten food quickly accumulate at the pond's floor.
By warming up the water and/or changing its pH, the safe ammonium ions are converted into
ammonia (NH3), a substance that is toxic to fish. Moreover, as Bangladesh is a riverine area,
some of the fish farms frequently experience flood in the rainy season. Fish can also escape from
the ponds to the water stream through the breach in pond walls caused by sudden floods from
Jamuna River, which can destroy a farmers work in a single day [4]. To fix these two issues the
team worked on AquaShield— a system that uses both IoT and Machine Learning to help fish
farmers, in Bangladesh make choices and manage their farms better.




1.2 Problem Statement - Done
Small and medium-scale fish farmers, in Bangladesh face four problems. Things such as pH, TDS
and temperature vary throughout the day and at first they are unable to keep track of water quality
at all times. Second, they lack means to safeguard their fish, when their efforts fail, their only
recourse is to supply them as it goes. Third, they have no data in the form of sensors, meaning it
doesn't allow them to make intelligent decisions. This can result in feeding and raising your TDS
levels. Fourth when big rains come rivers can. Rapidly elevate water levels can cause flooding of
ponds. Farmers sometimes are not warned to save their fish.

1.3 Motivation - Done
The rationale behind AquaShield is the connection between pond monitoring and protective
measures and flood readiness. It is an economical system which can be effectively used in
aquaculture in Bangladesh. Conditions may vary between checks for water-quality factors.
Sometimes the flooding occurs so quickly that farmers are unable to assess the condition by
looking.



                                                17
AquaShield combines an ESP32 based, sensing and control unit with cloud telemetry. It also
features machine learning components, and a dashboard. The edge controller doesn't need to
abide by safety guidelines in the absence of a network. The predictive models provide
information on river flood hazard, unexpected changes in water quality (TDS) and unusual water
quality information (factors).

The project is also geared towards affordability. The hardware developed with the cost of less
than 7,200 BDT (60 USD). The prototype features all the characteristics, in a single system. It
features monitoring, pump control, feeding, alerts and predictive analysis. These functions are not
considered as instruments. Form part of a complete system.




1.4 Aims and Objectives
The main aim of this project is to develop and evaluate AquaShield as an affordable
cyber-physical aquaculture management and flood-warning system. The specific objectives are
to:

●​ Develop a multi-sensor IoT node using an ESP32 microcontroller with pH, TDS, NTC
      thermistor temperature, and HC-SR04 ultrasonic water-level sensors, with measurements
      acquired at 30-second intervals.
●​ Develop local finite-state-machine (FSM) control logic on the ESP32 for the drain pump,
      refill pump, and servo-based feeder, with local safety operation maintained during network
      disconnection; flash-based telemetry buffering is identified as a future enhancement.
●​ Implement a cloud telemetry and dashboard pipeline using the Firebase Realtime Database, a
      Python FastAPI service for machine learning inference, and web-based alert banners.
●​ Develop and evaluate a river flood forecasting model using 15 years (2008--2022) of BWDB
      water-level records and ERA5 rainfall data for the Bahadurabad station on the Jamuna River,
      with forecast horizons from 1 to 14 days and Leave-One-Year-Out validation.
●​ Develop and evaluate a 60-minute-ahead pond TDS forecasting model using rolling statistics,
      comparing linear and tree-based models and applying SHAP for model interpretation.
●​ Develop an unsupervised pond water-quality anomaly detection model using Isolation Forest
      and sensor rate-of-change features to identify unusual multivariate conditions without
      requiring labeled failure data.
●​ Develop an interactive web dashboard and calibration interface providing live sensor
      readings, a Pond Health Index (0--100), historical trends, manual pump controls, and a
      two-point pH calibration workflow.




                                                  18
1.5 Challenges and Scope - done

Project. Conclusions: I studied the prototype. The prototype consists of a physical sensor circuit,
an ESP32 firmware, Firebase Realtime Database, a web dashboard showing banners and 3
machine learning models, in Python FastAPI. Model 1 is working for the Bahadurabad transit
station, which is located on the Jamuna River. Models 2 and 3 use the telemetry data from pond
IoT sensors. The prototype uses 2.4 GHz Wi‑Fi for telemetry. In the case of a remote rural pond
with no Wi‑Fi, an installation of a communication module using the GSM network must be
considered. Biofilm must be removed from the pH probe by manually cleaning it every 2-4
weeks. AquaShield is an environmental monitoring system providing decision support.
AquaShield is not a fish disease diagnostic tool.

Found hardware problems during development. The primary hardware problems consisted of
blocking the ESP32 ADC inputs from the 5 V output of the pH sensor module, and preventing
voltage drops due to activation of the pumps from resetting ESP32. The design measures are
explained in Sections 3.3 and 4.2.

1.6 Contribution - done

➢​ The affordable Edge Node: I have created a low cost edge node (less than 60$). Affordable
    Edge Node includes sensors with optical relay isolation and minimises ADC noise.

➢​ Offline Edge Fail-Safe: I have programmed FSM rules than the pumps will continue to pump
    even when no internet is available. Edge Fail-Safe ensures pump control in the event of an
    outage (off-line).

➢​ Dual-Horizon Protection: Incorporated forecasts for rivers to make pond automation more
    useful. Forecasts for DHP are verified over 1- to 14-day time horizon. Focuses on warnings
    three to seven days in advance.

➢​ LOYO cross validation: I used the flood forecast models with LOYO cross validation.
    Reviewed their forecast of maximum levels. Leakage-Aware Flood Validation shows model
    accuracy.

➢​ Unsupervised Anomaly Detection: Detected conditions on parameters using Isolation Forest.
    Unsupervised Anomaly Detection is based on no labels for failure data.

Report Organization: This report has six chapters. In Chapter 1 the background and the problem
the project is addressing, its motivation and goals and scope are explained. In chapter 2, the water
quality subject in aquaculture along with the water level, level of flood and the existing water
control system with IoT, Machine Learning techniques and research gap are discussed.
Throughout the system development, the various aspects of system design, hardware design,

                                                19
control logic design, Cloud flow design, machine learning steps are presented respectively in
Chapter 3, and the model validation is also presented. The hardware and firmware development,
the deployment of cloud services, machine learning development, and the dashboard and alerts
design are detailed in chapter 4. The results of the tests are shown in Chapter 5. Compares them.
Chapter 6 summarizes the results of the field study, the boundaries and future perspectives.




1.7 Conclusion - done
This chapter talked about the aquaculture setting, listed the water-quality and flood-related
problems explained why AquaShield was created and described what it aims to do. It also gave an
overview of what AquaShield covers and what it adds. The next chapter goes over the
background research and similar projects.




                                                20
Chapter 2: Background Studies

2.1 Introduction - Done
It is vital to know the boundaries of water, that is what the rivers rise up to during the monsoons,
in the case of Bangladesh and what research has been carried out with the use of IoT and machine
learning to create a good pond monitoring and flood warning system. These issues will be
examined in this chapter. Identifies the issues addressed by the project..

2.2 Aquaculture Challenges and Water Quality Dynamics in
Bangladesh - Done
Fish are animals. Temperature and chemicals are critical to fish for their health, growth and
survival. Fish need to maintain four levels of water parameters as indicated in references [5] [6].

The first parameter is one of the properties, the pH, which indicates if water is acid or alkaline.
The safe range for fish is between 6.5 to 8.5. If pH falls below 6.0 fish gills can become irritated
and the protective mucous layer can break down. Fish gills can be. when the pH is above 8.8.
Ammonia can be oxidized to ammonia (NH3) and this is toxic to fish.

The next parameter is Total Dissolved Solids or TDS, that is the concentration of minerals and
other solids in water. The ideal TDS level for fish is 150-450 ppm. When TDS exceeds 600 ppm,
it is typically due to leftover feed and/or fertilizer runoff. This may cause stress in fish, which can
clog fish gills and make breathing difficult.

Water temperature is also very important. The ideal water temperature for fish is 25.0°C –
30.0°C. If water gets warmer than 32°C the fish will use oxygen for respiration, as their
metabolism increases. Fish may struggle in warm water, due to the presence of oxygen. Also, the
higher the temperature, the more toxic ammonia (NH3) becomes, which is a problem in fish tanks
and ponds.

The last parameter is pond water level. The preferred depth of pond for fish is 80-150 cm. In the
prototype system the suction level is set at 85 cm. When the water level becomes less than 75cm,
the pump stops. The trigger at 85 cm, however, is outside the range, and therefore is not
applicable in real life. The threshold should be adjusted prior to deployment in fish ponds,
depending on the pond size and shape, and the freeboard. Doing so will make the system more
reliable and effective, for fish.




                                                  21
       Table 2.1: Water Quality Thresholds and Biological Tolerance for Major Farmed Fish Species

                                           Stress Threshold         Lethal Limit         Impact on Fish
  Parameter            Optimal Range
                                           (Warning)                (Critical)           Health
                                                                                         Gill burns,
                                                                                         respiratory failure,
  pH                   6.5 -- 8.5          < 6.2 or > 8.8           < 5.0 or > 9.5
                                                                                         ammonia toxicity
                                                                                         spike
                                                                                         Osmotic stress, gill
  TDS (ppm)            150 -- 450          450 -- 600               > 800                clogging, excessive
                                                                                         organic waste
                                                                                         Low oxygen,
  Temperature (°C)     25.0 -- 30.0        30.0 -- 33.0 or < 20.0   > 35.0 or < 15.0     metabolic collapse,
                                                                                         stopped feeding
                                                                                         Fast temperature
                                           < 60 (Low) / > 160       < 40 (Dry) / > 180   changes, dike
  Water Level (cm)     80 -- 150
                                           (High)                   (Overflow)           overtopping, fish
                                                                                         escape


2.3 Monsoon Flooding Risks and Early Warning Needs - done

More than 92 per cent of the river catchment in Bangladeshs is out of the country. During the
monsoon season, which runs from June, to October heavy rainfall in the Himalayas and the
Meghalaya hills flows down into the Brahmaputra-Jamuna river system. Frequently flood water
level exceeds the danger level of 19.05 m. at the Bahadurabad transit gauge of Jamalpur. In flood
years such as 2017, 2019 and 2020 water levels rose past 20.50 meters. As many as 40,000
hectares of pond areas were flooded in 2020 which cost us over 500 crore BDT (approx. 45
million USD) [3]. Basin level forecasts are provided by national agencies. The alarm should be
sent 3 to 7 days ahead of time to the fish farmers' station on the river. Such warning would afford
them the opportunity to place elevated high nylon nets about their pond dikes, or to remove the
fish from the pond, prior to the flood.

2.4 Review of Existing IoT Aquaculture Monitoring Systems-
done

The first generation of IoT Aquaculture Monitoring Systems were based on the Arduino board
and included ZigBee or Bluetooth communication. These systems were capable of range. Was
unable to turn any pumps on or off. Later versions used ESP8266 or ESP32 boards to transmit
data to platforms such as ThingSpeak or Blynk. These systems are entirely reliant on the Internet.
When Wi-Fi connection is lost, all monitoring is suspended and automatic pump controls are
replaced with manual controls. The price of commercial industrial PLC system is in the range of
two thousand to ten thousand dollars. This is too expensive for the small scale fish farmers in
Bangladesh.




                                                    22
2.5 Machine Learning in Hydrological Forecasting & Water
Quality Prediction- done

Machine learning models based on data, such as Ridge [17] SVR, Random Forest [16] are applied
in hydrology. Xgboost [15] - provide practical alternative to physics-based simulations. But there
are many studies that were wrong, they apply K-Fold Cross-Validation on time-series data. This
process randomly adds in data to the training set, giving high accurate scores. Also decision tree
methods such as Random Forest and XGBoost cannot predict values than those seen in their
training data. For this reason they have a tendency to underestimate the peak of flood flows. In
supervised machine learning models, there are insufficient labeled datasets of ‘bad water'
conditions, and therefore, models do not perform well in pond water monitoring applications. For
detecting patterns across sensors in an unsupervised manner, such as using Isolation Forest [13] is
better suited.

2.6 Comparative Analysis of Related Works and Research Gap
 Table 2.2 compares AquaShield with eight previous systems from recent research and industry:

         Table 2.2: Comparative Feature Matrix of Existing Aquaculture Systems vs. AquaShield

                                                                                      Pond ML
  System /                                                              River
                 Microcontr    Key           Local Auto     Offline                   &
  Research                                                              Flood                       Cost (USD)
                 oller         Sensors       Actuation      Fail-Safe                 Anomaly
  Study                                                                 Forecast
                                                                                      Detection
  Saha et al.    Arduino       pH, Temp,     No (Alerts
                                                            No          No            No            \$120
  (2018) [7]     Uno           DO            Only)
  Raju et al.    Raspberry     pH, Temp,     Yes
                                                            Partial     No            No            \$180
  (2020) [8]     Pi            Level         (Pumps)
  Hasan et al.                 pH, TDS,                                               Basic
                 ESP8266                     No             No          No                          \$75
  (2021) [9]                   Temp                                                   Thresholds
  Islam et al.                 pH, Temp,     Yes                                      Simple
                 ESP32                                      No          No                          \$95
  (2022) [10]                  Turbidity     (Aerator)                                Linear Reg
                                             Yes
  Chen et al.    Industrial    Optical DO,                                            LSTM DO
                                             (Multi-Rela    Yes         No                          \$1,500+
  (2023) [11]    PLC           pH, ORP                                                Forecast
                                             y)
  Ahmed et                                   Yes
                               pH, TDS,
  al. (2024)     ESP32                       (Drain/Refil   No          No            No            \$85
                               Level
  [12]                                       l)
  Commercia
  l                            Full Water    Full PLC                                 Proprietary
                 Proprietary                                Yes         No                          \$3,500+
  AquaMaste                    Suite         Control                                  Rules
  r
                                                                        Yes           Yes (Model
                               pH, TDS,      Yes (Drain,
  AquaShield     ESP32                                      Yes (Full   (BWDB         2 TDS +
                               Temp,         Refill,                                                < \$60
  (Our Work)     (Dual Core)                                Edge FSM)   LOYO CV       Model 3
                               Ultrasonic    Feeder)
                                                                        +1 to +14d)   IsoForest)
Research Gaps Identified. The reviewed studies indicate four principal gaps: (1) limited
integration between river-scale flood forecasting and pond-level automated protection; (2)
dependence on network connectivity for some automated monitoring and control functions; (3)
inadequate temporal validation strategies for flood forecasting that can introduce look-ahead
leakage; and (4) limited availability of labeled datasets for pond water-quality anomaly detection.

                                                           23
AquaShield addresses these gaps through integrated river and pond monitoring, local edge
control, Leave-One-Year-Out validation, and unsupervised anomaly detection.

2.7 Conclusion - done
In this chapter, we considered what’s required of water quality parameters for the fish, how
monsoon floods would take place, and what aquaculture IoT platforms are available and what
machine learning methods could be employed. The gaps, in the research that were found help set
the stage for the method that will be explained in Chapter 3.




                                                24
Chapter 3: Methodology

3.1 Introduction - Done
This chapter explains the design of the AquaShield. It includes the five-tier structure, the models
and equations for the sensors, the rules for edge control, the cloud data pipeline and the math
behind the three machine learning models. It also explains the test and validation of everything.

3.2 Overall System Architecture and Telemetry Pipeline
  AquaShield is organized into five connected tiers: (1) Physical Sensors and Actuators at the
  pond; (2) Edge Computing on the ESP32 for local control; (3) Cloud Telemetry using the
  Firebase Realtime Database; (4) Machine Learning Analytics through the three prediction
  and anomaly-detection models served by the FastAPI backend; and (5) User Interface and
  Alerts through the web dashboard.




    Figure 3.1: High-level 5-tier cyber-physical architecture and catchment integration schematic of
                                               AquaShield




                                                  25
Explanation: The architecture illustrates the flow of data from pond sensors and river stations
through the ESP32 and Firebase Realtime Database to the machine learning models, FastAPI
backend, live dashboard, and dashboard alert banners.

3.3 Hardware Design and Edge Sensing Layer
The ESP32 WROOM-32 was selected because it provides a dual-core 240 MHz processor,
built-in 2.4 GHz Wi-Fi, and 4 MB flash memory [22]. Core 0 is used for Wi-Fi and Firebase
Realtime Database synchronization, while Core 1 handles sensor acquisition and relay control.
The primary sensors and associated measurement equations are described below:

pH Sensor (pH-4502C). Analog probe using two-point calibration, where S is the sensor slope:
                                                             𝑉𝑐𝑎𝑙,7−𝑉𝑜𝑢𝑡
​                                             𝑝𝐻 = 7. 0 +        𝑆
                                                                           ​                                   (3.1)

TDS Sensor. Measures electrical conductivity with AC excitation. Compensated for temperature:
                                                             𝑉
​                                                            𝑎𝑑𝑐
                                             𝑉𝑐𝑜𝑚𝑝 = 1.0+0.02×(𝑇−25.0) ​                                       (3.2)

NTC Thermistor Temperature Sensor. Analog thermistor read through a voltage divider with a 4.7
kΩ pull-down resistor.

HC-SR04 Water Level Sensor. Ultrasonic sensor measuring distance:
                                                                           𝑡𝑒𝑐ℎ𝑜×𝑣𝑠𝑜𝑢𝑛𝑑
​                                      𝑊𝑎𝑡𝑒𝑟𝐿𝑒𝑣𝑒𝑙 = 𝑃𝑜𝑛𝑑𝐷𝑒𝑝𝑡ℎ −                 2
                                                                                          ​                    (3.3)

3.3V pH Sensor Power Design and Calibration Tool. The pH-4502C module is normally powered
at 5 V. In the prototype, it is powered at 3.3 V to protect the ESP32 ADC inputs. The TDS probe
also operates with 3.3 V logic. A custom software calibration tool was developed for two-point
pH calibration.

                      Table 3.1: Hardware Bill of Materials (BOM) and Cost Breakdown

    Component         Model /                            Unit Cost                  Unit Cost   Primary
                                        Quantity
    Name              Specification                      (BDT)                      (USD)       Function
                                                                                                Central
                      ESP32
    ESP32                                                                                       processing &
                      WROOM-32          1                650 BDT                    \$5.50
    Microcontroller                                                                             Wi-Fi
                      (Wi-Fi/BLE)
                                                                                                communication
                      pH-4502C
                      pH Sensor                                                                 Measures pond
    pH Sensor Kit                       1                1,850 BDT                  $15.50      water
                      Module /                                                                  acidity/alkalinity
                      Probe
                                                                                                Measures
                      Analog AC
    TDS Sensor Kit                      1                750 BDT                    \$6.30      dissolved solids
                      Probe Module
                                                                                                and water purity
                      NTC Thermistor                                                            Measures water
    Temperature
                      (waterproof       1                180 BDT                    \$1.50      temp for
    Sensor
                      probe)                                                                    compensation




                                                      26
Component           Model /                             Unit Cost           Unit Cost          Primary
                                       Quantity
Name                Specification                       (BDT)               (USD)              Function
                                                                                               Tracks pond
Ultrasonic          HC-SR04                                                                    water depth
                                       1                120 BDT             \$1.00
Sensor              Transducer                                                                 without touching
                                                                                               water
                    5V Optocoupler
                                                                                               Switches 12V
2-Channel Relay     Isolated,          1                280 BDT             \$2.35
                                                                                               pumps safely
                    Active-LOW
                                                                                               Drains excess
                    12V DC
                                                                                               water during
Drain Pump          Submersible        1                650 BDT             \$5.45
                                                                                               heavy rain or
                    (240 L/h)
                                                                                               high TDS
                    12V DC                                                                     Adds fresh water
Refill Pump         Submersible        1                650 BDT             \$5.45             when pond level
                    (240 L/h)                                                                  gets low
                                                                                               Dispenses fish
                    SG90 Micro
Servo Feeder                           1                140 BDT             \$1.20             feed pellets
                    Servo (PWM)
                                                                                               automatically
                                                                                               Powers 12V
Power Supply &      12V 5A Adapter                                                             pumps and
                                       1                800 BDT             \$6.70
Buck                + LM2596                                                                   regulates 5V for
                                                                                               ESP32
                                                                                               Protects
Enclosure &         IP65 Waterproof                                                            electronics from
                                       1                500 BDT             \$4.20
Wiring              Box & Cables                                                               rain and
                                                                                               moisture
                                                                                               Complete
**Total Bill of     Complete
                                       -                **6,570 BDT**       **\$55.15**        assembled
Materials**         Hardware Node
                                                                                               prototype system

                  Table 3.2: Summary of Primary Hardware Pin Assignments on ESP32

                                                                                     Electrical Characteristics
ESP32 GPIO Pin               Interfaced Component       Signal Category
                                                                                     / Protocol
                             pH Sensor                                               0.0V -- 3.3V DC (ADC1
GPIO 34 (ADC1_CH6)                                      Analog Input
                             (pH-4502C)                                              pin, safe with Wi-Fi)

                                                                                     0.0V -- 2.3V DC (ADC1
GPIO 35 (ADC1_CH7)           TDS Sensor (Analog Out)    Analog Input
                                                                                     pin, safe with Wi-Fi)
                                                                                     Voltage divider with 4.7
                             NTC Thermistor
ADC pin [GPIO 32]                                       Analog Input                 kΩ pull-down resistor,
                             (Temperature)
                                                                                     3.3V DC
GPIO 5                       Ultrasonic Trig Pin        Digital Output               10 μs TTL trigger pulse
                                                                                     TTL pulse-width return via
GPIO 18                      Ultrasonic Echo Pin        Digital Input
                                                                                     1kΩ/2kΩ divider
                                                                                     3.3V GPIO control;
GPIO 25                      Relay IN1 (Drain Pump)     Digital Output               5.0V relay-module
                                                                                     supply
                                                                                     3.3V GPIO control;
GPIO 26                      Relay IN2 (Refill Pump)    Digital Output               5.0V relay-module
                                                                                     supply
                                                                                     3.3V PWM control;
GPIO 13                      Servo Motor (Feeder)       PWM Output                   5.0V external servo
                                                                                     supply
                                                                                     3.3V supply instead of the
                             pH Sensor (pH-4502C) &
3.3V                                                    Sensor Power Rail            standard 5V, protecting the
                             TDS Sensor
                                                                                     ESP32 ADC pins




                                                       27
                                                                                    Electrical Characteristics
  ESP32 GPIO Pin           Interfaced Component       Signal Category
                                                                                    / Protocol
                                                                                    Regulated 5.0V DC from
  5V & GND                 Relay Module & Servo       Power Rails
                                                                                    LM2596 buck converter


3.4 Local Edge Control Logic, Fail-Safe Automation, and
Actuator Drivers
An autonomous Finite State Machine (FSM) was implemented directly on the ESP32. It evaluates
the control conditions every 30 seconds and operates the pumps locally, allowing protective
actions to continue during internet or cloud-service interruptions (Table 3.3).

               Table 3.3: Summary of Edge Finite State Machine (FSM) Actuation Rules

                      Monitored                                     Automated Local       Safety Cut-off /
  Rule ID                                  Trigger Condition
                      Condition                                     Action                Hysteresis
                                           Water Level >=
                                           85 cm
                                           (conservative            Turn on Drain Pump    Turn off when level
  Rule 1              Pond Overflow Risk
                                                                    (Relay 1 ON)          drops below 75 cm
                                           prototype
                                           trigger)
                      Pond Water           Water Level <= 40        Turn on Refill Pump   Turn off when level
  Rule 2
                      Depletion            cm                       (Relay 2 ON)          rises above 55 cm
                      High Dissolved                                Execute Partial       Drain for 5 mins,
  Rule 3                                   TDS >= 600 ppm
                      Waste                                         Water Exchange        then refill for 5 mins
                                                                                          Gated: Paused if
                                           Time = 08:00 or
  Rule 4              Scheduled Feeding                             Rotate Feeder Servo   Temp < 18°C or
                                           16:00
                                                                                          Temp > 34°C
                      Acidic / Alkaline                             Show Alert Banner     Displays immediate
  Rule 5                                   pH < 6.2 or pH > 8.8
                      Water                                         on Web Dashboard      alert to farmer
Local FSM control rules continue to operate during connection loss. SPIFFS-based telemetry
buffering is planned for a future firmware revision.

3.5 Cloud Telemetry, REST API, and Database Schema - Done
I noticed that the ESP32 sends sensor data to the Firebase Realtime Database every five minutes
using the Firebase ESP32 Client SDK. The Firebase Realtime Database stores the sensor
telemetry and the pump command states. It offers -second latency so the web dashboard shows
updates without the browser having to refresh the page. The three machine learning models are
hosted by a Python FastAPI and the web dashboard gets them through a REST API.

3.6 Machine Learning Subsystem Methodology - Done
I built three models as part of my dissertation research.

First Model: Prediction of Water Level of River Jamuna 14 Days Ahead at Bahadurabad Station




                                                   28
This model predicted the water level of River Jamuna 14 days ahead of time at Bahadurabad
Transit station. Checkpoints were set at +1, +3, +7 and +14 days. The model uses ERA5 data of
catchment area’s rainfall and continuous 15 years of data (2008-2022) from BWDB. Features of
the model were river levels at (t-1), (t-2) and (t-3) and (t-7) with changes in water levels at (t-3)
and (t-7). 3-day total and 7-day total rainfall and seasonal trend were also features. As the model
evens out flood peaks, the dashboard issues alerts with a safety buffer below the Danger Level.



Second Model: Prediction of Pond TDS one Hour Ahead (t+1h) Using IoT Telemetry

This model uses one hour IoT data (telemetry) of pond to predict TDS one hour ahead (t+1h). To
reduce noise of the sensors, this model uses a rolling average of 6 hours. This model compares
and contrasts linear regression, random forest and XGBoost. This model also uses SHAP to
determine how features contributed to the prediction.



Third Model: Unsupervised Anomaly Detection of Pond Water Quality

This model uses an Isolation Forest method, with a 5% contamination threshold to determine the
risks of water quality, using a sensor data of the previous hour along with the hourly changes of
(pH) and TDS and Temp.




3.7 Model Validation Protocols (LOYO CV and Chronological
Splitting)
  To prevent future data leakage, Model 1 used Leave-One-Year-Out (LOYO) cross-validation
  across 12 annual folds (2008--2019), keeping 2020--2022 as an untouched test set. Model 2
  used a chronological 70% train, 15% validation, and 15% test split (Figure 3.2).




                                                 29
    Figure 3.2: Leave-One-Year-Out (LOYO) cross-validation and strict holdout evaluation protocol




Explanation: Shows how data was split by full calendar years: 12 folds (2008--2019) for model
tuning, followed by testing on the untouched 2020--2022 test years.

​                                     RMSE = √[(1/N) Σ(yᵢ − ŷᵢ)²]​                              (3.4)
                                                         Σ(𝑦ᵢ−ŷᵢ)²
​                                        𝑁𝑆𝐸 = 1. 0 − Σ(𝑦ᵢ−ȳ)² ​                                (3.5)
                                                       𝐻𝑖𝑡𝑠
​                                          𝑃𝑂𝐷 = 𝐻𝑖𝑡𝑠+𝑀𝑖𝑠𝑠𝑒𝑠 ​                                  (3.6)
                                                   𝐹𝑎𝑙𝑠𝑒𝐴𝑙𝑎𝑟𝑚𝑠
​                                        𝐹𝐴𝑅 = 𝐻𝑖𝑡𝑠+𝐹𝑎𝑙𝑠𝑒𝐴𝑙𝑎𝑟𝑚𝑠 ​                               (3.7)


3.8 Conclusion
This chapter described the hardware circuitry, control logic, cloud pipeline, and machine learning
formulations. Chapter 4 presents their implementation.




                                                 30
Chapter 4: Implementation

4.1 Introduction -Done

This chapter provides an introduction to building and programming AquaShield. The team
divided the work as follows: Hrithik handled the development of the circuit that links the sensors
and the control of power. Mahfuz did the work of connecting ESP32 to Firebase Realtime
Database and developing the web dashboard. srabon worked on Fast API Backend and on the
machine learning aspects.

4.2 Hardware Fabrication, Circuit Wiring, and Power Supply
Setup -Done

The prototype was fabricated in a waterproof outdoor box, followed by the wiring of the circuits
and the installation of the power supply. When tested with 12 V pumps, it led to a drop in voltage,
resetting the ESP32. To fix this a dual‑rail power system was designed. The pumps are powered
by a 12 V 5 A DC adapter. The output of the 5.0 V constant voltage unit goes to an LM2596 step
down buck converter which steps down the voltage to power the ESP32, relay module, servo and
ultrasonic sensor with 5.0 V DC. A 470µF capacitor filters away some of the power. To absorb
voltage spikes when the pumps shut off 1N4007 diodes were also placed across the pump motor
terminals.

Sensors were connected to ADC1 pins, on the ESP32. pH sensor was moved to GPIO34 and the
TDS sensor to GPIO35. This is because when Wi‑Fi is on, ADC2 will not be available. To
prevent damage to the ADC pins (see Section 3.3), the pH‑4502C module and the TDS probe
were powered at 3.3 V or 5 V. The NTC thermistor temperature probe was connected in a voltage
divider configuration to a 4.7 kΩ resistor which is pulling down the signal. A 1 kΩ/2 kΩ resistor
divider was used to reduce the echo output of the HC‑SR04 ultrasonic sensor from 5 V to 3.3 V
and connected to GPIO 18. This will keep the microcontroller input pin safe.




                                                31
4.3 ESP32 Firmware Development & Local Sensing Pipeline
-Done

The ESP32 firmware will sample the data from the pH, TDS, NTC thermistor and ultrasonic
sensors every 20 seconds. Contains software components based on ADC1 inputs. Samples to
reduce noise. The firmware implements the rules listed in Table 3.1, controlling the drain
relays, refill relays and feeder servo. On the pump cut‑off conditions hysteresis is used to
prevent the switching of the relays. If the temperature is outside of the allowed range then the
feeding will not occur. If Wi‑Fi or the cloud service fails the local control logic still runs.

4.4 Backend & Database Service Implementation -Done

The sensor readings are stored in Firebase Realtime Database. Pump command statuses. Data is
stored in sections called sensor, pump and history. Any changes are delayed on the web
dashboard. During testing there is a Python FastAPI machine learning backend on port 8000
using the uvicorn server package (api_combined.py) which runs the back end of the application.
Saves the trained models. It's providing inference endpoints for the dashboard.




4.5 Machine Learning Subsystem Implementation & Deployment
Pipeline -Done

The machine learning workflows have been coded in Python with Scikit‑learn, XGBoost and
SHAP. For Model 1 – River Flood Forecast – we used 15 years of BWDB water‑level data. Days
without data were interpolated. Data on lag, rainfall were developed. Linear Regression, Ridge,
Lasso, Random Forest and XGBoost were run. The support vector regression (SVR) method was
used with leave one year out cross validation. The short term TDS prediction was performed
using rolling statistics in Model 2. For model 3, the anomalies were detected using Isolation
Forest on sensor deltas. The models developed by training were saved using Joblib.The models
that were trained were saved using Joblib. There were available via a FastAPI microservice.




4.6 Web Dashboard & Sensor Calibration Interface Development
-Done

A responsive web dashboard was developed with HTML, CSS and JavaScript with chart.js for
visualization of trends. It features real-time pH, TDS, temperature and depth readings; it has a


                                                32
Pond Health Index (PHI) metric ranging from 0-100; it provides charts of 24-hour and 7-day
trends; it offers manual controls for testing pumps; and it has a guided two-point pH calibration
tool. The dashboard also provides recommendations in both languages to farmers. Contains a
demonstration simulation.




4.7 Automated Alerting Subsystem & Web Dashboard Alert
Banners -Done

Automated Alerting Subsystem & Web Dashboard Alert Banners Alerts will be displayed as
banners on the web dashboard. A debounce filter ensures that an alert triggers, after three
readings (90 seconds total). After an alert there is a 30‑minute period to stop repeated alerts. For
every alert, the issue, automatic action taken, and further steps to take are presented. If it is a
“normal” value, a green “Resolution” banner will appear.




4.8 Conclusion -Done

This chapter focused on the wiring, power configuration, design of the firmware, cloud database,
machine learning service, and user interface. Chapter 5 will explore the operation of these parts.




                                                33
Chapter 5: Result Analysis and Comparison

5.1 Introduction - done
This chapter presents the sensor calibration work done in the laboratory river flood forecasting
using Model 1. Pond TDS forecasting using Model 2 and SHAP analysis anomaly detection using
Model 3 and the responsiveness and reliability tests of the system.

5.2 IoT Hardware Performance and Sensor Calibration Results
-done

The sensors were tested against the reference measurements provided by the project. The pH
probe was calibrated at two points. A filtered result, from 64 samples was obtained with an error
of ±0.05 pH (R² = 0.994). The TDS sensor had an error that stayed within 2.8% for the saline test
solution. The NTC thermistor temperature probe showed accuracy within ±0.15°C, for the saline
test solution. The ultrasonic sensor achieved a depth precision of ±0.4 cm for the saline test
solution.

(Table 5.1):

         Table 5.1: Sensor Calibration and Precision Evaluation Across Reference Measurements

                                                           Post-Calibratio
  Sensor              Ground Truth      Pre-Calibration
                                                           n Error           R² Score           Drift (72h Test)
  Parameter           Reference         Error
                                                           (AquaShield)
                      Vinegar (~pH
  pH
                      2.4) and baking
  (Acidity/Alkalini                     ± 0.42 pH          ± 0.05 pH         0.994              ± 0.03 pH
                      soda solution
  ty)
                      (~pH 8.3)
                      Calibrated NaCl
  TDS (ppm)           Reference         ± 8.5%             ± 2.8%            0.989              ± 4.2 ppm
                      (100--1000 ppm)
  Water               Certified
  Temperature         Mercury           ± 0.85°C           ± 0.15°C          0.998              ± 0.08°C
  (°C)                Thermometer
  Water Level         Physical Metric
                                        ± 2.4 cm           ± 0.4 cm          0.996              ± 0.2 cm
  (cm)                Gauge Rule


5.3 Model 1 (River Flood Forecast) Experimental Evaluation
Model 1 was trained using 15 years (2008--2022, 5,479 days) of daily water-level data from the
Bahadurabad transit station on the Jamuna River [21]. The danger level is 19.05 m, with 467
recorded flood days (Table 5.2).

                 Table 5.2: Bahadurabad Station Hydrological Dataset Summary (2008--2022)

  Hydrological Parameter /                                                   Operational Significance for
                                        Empirical Dataset Value
  Attribute                                                                  Aquaculture
                                                                             15 continuous calendar years of daily
  Study Period                          2008-01-01 to 2022-12-31
                                                                             records



                                                          34
  Hydrological Parameter /                                          Operational Significance for
                                   Empirical Dataset Value
  Attribute                                                         Aquaculture
                                                                    Statistically exhaustive sample of
  Total Calendar Days              5,479 days
                                                                    seasonal cycles
                                                                    Cleanly imputed using PCHIP
  Missing Daily Observations       335 days (6.11%)
                                                                    interpolation
                                                                    Wide dynamic range of hydraulic
  Observed Gauge Range             11.68 m to 21.16 m
                                                                    head
                                                                    Water overtopping primary earthen
  Official Danger Level            19.05 m
                                                                    embankments
                                                                    Severe regional flooding across all
  Extreme Danger Level             19.90 m
                                                                    surrounding ponds
  Recorded Highest Water Level                                      Historical peak flood inundation
                                   20.63 m
  (RHWL)                                                            benchmark
                                                                    Extensive sample of high-water flood
  Total Flood Days (>= 19.05 m)    467 days
                                                                    risk events


  The physical hydrologic lag between catchment rainfall and river water level is shown in
  Figure 5.1.




 Figure 5.1: Correlation and physical lag dynamics between catchment rainfall and Bahadurabad river
                                              water level




Explanation: The figure illustrates the physical hydrologic lag: upstream rainfall in the
Brahmaputra basin peaks several days before river water levels rise at Bahadurabad, supporting
the use of 3-day and 7-day cumulative rainfall features.

            Table 5.3: Hyperparameter Search Grids and Selected Optimal Values for Model 1



                                                  35
                             Hyperparameter Search         Selected Optimal
  Algorithm Family                                                                        Algorithmic Notes
                             Space                         Configuration
  Persistence Baseline       None (Heuristic)              ΔWL = 0                        Assumes WL(t+h) = WL(t)
                                                           Adds past 1-day rate of        Accounts for immediate
  Persistence + Trend        None (Heuristic)
                                                           change                         momentum
                             alpha ∈ [0.01, 0.1, 1.0,                                     L2 penalty, StandardScaler
  Ridge Regression                                         alpha = 1.0
                             10.0, 100.0]                                                 applied
                             alpha ∈ [0.001, 0.01, 0.1,
  Lasso Regression                                         alpha = 0.01                   L1 sparse feature selection
                             1.0]
                             n_estimators ∈ [50, 100,
                                                           n_estimators = 100,            Tree ensemble,
  Random Forest Regressor    200]; max_depth ∈ [5, 10,
                                                           max_depth = 10                 random_state = 42
                             15]
                             n_est ∈ [50, 100, 200];
                                                           n_est = 100, depth = 5, lr =   Gradient boosted trees,
  XGBoost Regressor          depth ∈ [3, 5, 7]; lr ∈
                                                           0.05                           seed = 42
                             [0.01, 0.05, 0.1]
                             C ∈ [0.1, 1.0, 10.0];                                        RBF kernel,
  Support Vector Regressor                                 C = 1.0, epsilon = 0.1
                             epsilon ∈ [0.01, 0.1]                                        StandardScaler applied




  Figure 5.2: Model Root Mean Squared Error (RMSE) vs. forecast lead time (1 to 14 days) across all
                                      evaluated algorithms




Explanation: The figure shows that prediction error increases with forecast lead time. Linear
models maintain lower error curves than tree-based models across short and medium lead times.

       Table 5.4: Comprehensive LOYO Cross-Validation Performance Metrics (+1 Day Horizon)

                                                                                                         False
  Model                                                                   Nash-Sutcl      POD (Hit
                Horizon      RMSE (m)      MAE (m)         Bias (m)                                      Alarm
  Name                                                                    iffe (NSE)      Rate)
                                                                                                         Rate (FAR)
  Persistence
                +1 Day       0.1265        0.0797          -0.0009        0.9972          0.9280         0.0670
  Baseline



                                                          36
                                                                                          False
  Model                                                          Nash-Sutcl   POD (Hit
                Horizon    RMSE (m)    MAE (m)      Bias (m)                              Alarm
  Name                                                           iffe (NSE)   Rate)
                                                                                          Rate (FAR)
  Persistence
                +1 Day     0.0953      0.0546       +0.0001      0.9984       0.9413      0.0381
  + Trend
  Linear
                +1 Day     0.0843      0.0498       -0.0002      0.9988       0.9387      0.0276
  Regression
  Ridge
                +1 Day     0.0843      0.0497       -0.0002      0.9988       0.9307      0.0279
  Regression
  Lasso
                +1 Day     0.0889      0.0518       +0.0000      0.9986       0.9360      0.0277
  Regression
  Random
                +1 Day     0.0848      0.0491       +0.0011      0.9988       0.9387      0.0330
  Forest
  XGBoost
                +1 Day     0.0847      0.0491       +0.0004      0.9988       0.9360      0.0331
  Regressor
  Support
  Vector        +1 Day     0.0848      0.0546       +0.0113      0.9988       0.9440      0.0301
  Regressor




   Figure 5.3: Flood season hydrographs: observed vs. predicted water levels during major historical
                                        monsoon flood years




Explanation: The figure compares predicted and observed water levels and shows the model
response around flood peaks and the 19.05 m Danger Level.


                                                  37
Key Defense Finding: Why Linear Regression Beat Tree Ensembles on Peak Floods. When
looking at extreme floods above 19.9m (Table 5.5), Linear Regression achieved an RMSE of
0.1120m, outperforming Random Forest (0.1176m) and XGBoost (0.1156m):

                   Table 5.5: Extreme Flood Season and Peak Error Evaluation Metrics

                                                           RMSE          RMSE          RMSE
                  Flood Season   Peak Error   RMSE
  Model                                                    (17-19m       (19-19.9m     (>19.9m
                  RMSE (m)       MAE (m)      (<17m Low)
                                                           Med)          Danger)       Extreme)
  Persistence
                  0.1614         0.0512       0.0973       0.1693        0.1641        0.2301
  Baseline
  Persistence +
                  0.1179         0.1234       0.0746       0.1290        0.1212        0.1363
  Trend
  Linear
                  0.1060         0.0621       0.0662       0.1156        0.1043        0.1120
  Regression
  Ridge
                  0.1061         0.0623       0.0659       0.1156        0.1047        0.1119
  Regression
  Random
                  0.1105         0.0678       0.0646       0.1177        0.1094        0.1176
  Forest
  XGBoost
                  0.1093         0.0677       0.0647       0.1169        0.1103        0.1156
  Regressor


  Why did this happen? Decision trees split data into boxes and predict the average of training
  points in that box. By design, a tree cannot predict any number higher than the highest value
  it saw during training. During a record-breaking flood, tree models hit a ceiling and
  underestimate the peak. Linear models, on the other hand, fit a continuous line (y = wx + b).
  When rainfall and water momentum surge together, the linear model extrapolates upward
  naturally, tracking unprecedented peaks accurately.




                                                  38
   Figure 5.4: Model 1 feature importance distribution shifting from autoregressive water-level lags to
                                        upstream rainfall sums




Explanation: For a 1-day forecast, yesterday's water level is most important. For 7-day and
14-day forecasts, the model shifts its reliance to 3-day and 7-day accumulated catchment rainfall.

Holdout Test on Unseen 2020--2022 Monsoons. Tested on the untouched 2020--2022 monsoon
seasons (+3 days lead horizon), Linear Regression achieved an NSE of 0.9851 and RMSE of
0.3082m, beating the baseline by +21.19% (Table 5.6 and Figure 5.5):

     Table 5.6: Final Holdout Evaluation Results on Unseen 2020--2022 Monsoon Seasons (+3 Days)

  Evaluated      Forecast      Holdout Test                                                Skill Score vs
                                              RMSE (m)       MAE (m)        NSE Score
  Model          Horizon       Period                                                      Baseline
  Persistence                  2020--2022                                                  0.00%
                 +3 Days                      0.3911         0.2642         0.9754
  Baseline                     Monsoons                                                    (Reference)
  Linear
                               2020--2022                                                  +21.19%
  Regression     +3 Days                      0.3082         0.2035         0.9851
                               Monsoons                                                    Improvement
  (AquaShield)




   Figure 5.5: Final holdout model performance on unseen 2020--2022 monsoon seasons (+3 days lead
                                              horizon)




Explanation: Demonstrates accurate tracking across the extreme 2020 flood season, achieving an
outstanding NSE of 0.9851.

Safety Buffer for Missed Flood Days. The evaluated machine learning models smooth some flood
peaks, and the Probability of Detection reported in Table 5.4 remains below 1.0 for all evaluated
models. To reduce the risk of delayed warnings, the dashboard warning threshold is set 0.3 m to
0.5 m below the official 19.05 m Danger Level, providing an operational safety margin.


                                                   39
5.4 Model 2 (Pond TDS Forecast) Results and SHAP
Explainability
Model 2 predicts pond TDS 60 minutes ahead (t+1h). Table 5.7 compares algorithms on the 15%
test set:

            Table 5.7: Model 2 Pond TDS Forecasting Performance Comparison (+60 Mins Horizon)

  Algorithm                                                                      Key Practical
                         MAE (ppm)          RMSE (ppm)        R² Score
  Evaluated                                                                      Finding
                                                                                 Beats tree models;
  Persistence Baseline   3.54               11.46             0.942              captures slow
                                                                                 physical drift
                                                                                 Smooth learned
  Linear Regression      7.05               15.90             0.888              linear prediction
                                                                                 without overfitting
                                                                                 Overfit training
  Random Forest
                         17.25              24.14             0.742              sensor noise; stepped
  Regressor
                                                                                 predictions
                                                                                 Overfit
  XGBoost Regressor      18.46              25.56             0.711              high-frequency ADC
                                                                                 electrical noise




       Figure 5.6: Model 2 performance comparison bar chart across MAE, RMSE, and R² metrics




Explanation: The figure shows that the Persistence baseline achieved the lowest overall error,
while Linear Regression was the strongest of the learned models and outperformed the tree-based
models.


                                                    40
Why Persistence Beat the Learned Models. In a large pond, water chemistry changes slowly
over a 60-minute interval. The Persistence baseline therefore captured the short-term
movement effectively (MAE 3.54 ppm, R² = 0.942). Among the learned models, Linear
Regression performed best (MAE 7.05 ppm, R² = 0.888), while XGBoost and Random
Forest showed higher test errors, indicating that the more complex models did not generalize
as well to the available sensor data.




       Figure 5.7: Model 2 actual vs. predicted TDS time series over the held-out test dataset




Explanation: The figure compares predicted and observed TDS trajectories over the held-out
test dataset.




                                                41
         Figure 5.8: SHAP feature importance summary plot explaining Model 2 TDS forecasts




Explanation: The SHAP analysis indicates that the 6-hour rolling average of TDS and the
previous TDS reading (TDS_t-1) account for more than 85% of the model contribution,
supporting the role of recent TDS history in the forecast.




                                                42
5.5 Model 3 (Pond Anomaly Detection) Evaluation and Diagnostic
Analysis

 A standard Z-score threshold flagged 55 outlier points, while Isolation Forest (5%
 contamination) detected 67 anomalies, effectively isolating dangerous multi-sensor
 combinations (such as pH 8.2 at 32°C associated with increased unionized-ammonia toxicity
 risk) that pass single-sensor threshold checks (Figure 5.9 to Figure 5.11):




 Figure 5.9: Model 3 bivariate scatter plot (pH vs. TDS) highlighting detected multivariate anomalies




 Explanation: Normal pond observations form a dense cluster, while observations associated
 with multiple abnormal parameters are isolated by the algorithm.




                                                 43
   Figure 5.10: Model 3 anomaly detection timeline traced along continuous TDS sensor readings




Explanation: Red markers indicate sudden changes in the TDS time series associated with
rapid environmental changes, such as fertilizer runoff or rain dilution.




 Figure 5.11: Isolation Forest anomaly score distribution and 5% contamination decision threshold




                                               44
Explanation: The histogram presents the computed anomaly scores, with the decision threshold
corresponding to the selected 5% contamination level.

5.6 Real-Time Actuation and Inference Latency
System responsiveness was evaluated across 1,000 test cycles, with representative edge sampling,
local relay actuation, and machine-learning inference latency summarized in Table 5.8.

                           Table 5.8: End-to-End Latency Benchmark Results

  Subsystem Operation /    Measured Average        Maximum Observed          Operational Reliability
  Benchmark                Latency                 Latency                   Standard
  Edge Sensor Sampling &                                                     Deterministic 30-second
                           42 ms                   68 ms
  ADC Multi-Sampling                                                         cycle
  Local Fail-Safe Relay                                                      Instantaneous emergency
                           65 ms                   85 ms
  Actuation (Edge FSM)                                                       protection
                                                                             Millisecond-scale
  Machine Learning                                                           REST model
                           18 ms                   32 ms
  Inference API Latency
                                                                             inference


5.7 Comprehensive Discussion & Technical Defense Insights- done

Four Key Findings. (1) River time-series data cannot be truly validated by shuffling the data in
time because of the potential, for future-data leakage. (2) Linear regression models can better
extrapolate peak values than the models evaluated here which are based on trees. In this situation
it is important to use (3) Leave One Year Out validation. Shuffling the data in time can create the
possibility of future-data leakage. (4) SHAP can give a visibility into the separation between
features and the forecasting model, which is interpretable.

5.8 Conclusion- done

The experiments validated the performance of the subsystems: the accuracy of the data from the
calibrated sensors was demonstrated. Model 1 was shown to be able to achieve the reported
measurement accuracy on the holdout dataset. With respect to the short horizon (daily) TDS
forecasting, Model 2 was evaluated giving the performance to the persistence sub-system. Model
3 has the ability to identify multivariate anomalies and locally continue monitoring the edge
control logic when the network is down. Conclusions and suggestions for further research are
given in Chapter 6.




                                                 45
Chapter 6: Conclusion and Future Work

6.1 Conclusion - done

AquaShield combines low-cost IoT automation with three machine learning models to solve pond
water-quality monitoring and the risk of floods, during monsoons in Bangladesh. The prototype
was built in the budget of 7,200 BDT (~US$60 USD). The project demonstrates the possibility of
embedding the edge control, cloud telemetry predictive modelling and anomaly detection into an
aquaculture decision support system. A brief account of the engineering and research works done
is given below.

Project Limitations:

1. Bio-Fouling of Sensor: Glass-bulb pH probes need to be cleaned every 2 to 4 weeks to remove
the biofilm.

2. Wi-Fi Coverage: The prototype is designed to use 2.4 GHz wi-fi, but if a pond is remote there
is no wi-fi, then there will be a GSM based communication module.

3. Single-Station Scope: Model 1 was calibrated for the Bahadurabad transit station of Jamuna
River.


6.2 Future Work: -done
LoRaWAN Long-Range Mesh: Deploy LoRaWAN transceivers to mesh together multiple ponds
within a 10 km radius and connect them to a single gateway.

3. On-Device TinyML Inference: Take appropriate TinyML models and make predictions on the
ESP32 microcontroller.

3. Solar Off-Grid power: Include 50W solar panel and 12V battery for off-grid use in rural areas.




                                               46
Appendix A: Hardware Pin Mappings and REST API Endpoints

A.1 Complete Hardware Pinout Specifications
                Table A.1: Complete Hardware Pinout and Bus Interfacing Specifications

                                                                                     Bus Protocol /
  ESP32 Pin            Component Name        Signal Category     Operating Voltage
                                                                                     Interface Circuit
                                                                                     ADC1 Channel 6
                       pH Sensor
  GPIO 34                                    Analog Input        0.0V -- 3.3V DC     (Wi-Fi safe,
                       (pH-4502C)
                                                                                     multi-sampled)
                                                                                     ADC1 Channel 7
                       TDS Sensor (Analog
  GPIO 35                                    Analog Input        0.0V -- 2.3V DC     (Wi-Fi safe,
                       Out)
                                                                                     multi-sampled)
                                                                                     Voltage divider with
                       NTC Thermistor
  ADC pin [GPIO 32]                          Analog Input        3.3V DC             4.7 kΩ pull-down
                       (Temperature)
                                                                                     resistor
                                                                                     10 μs trigger pulse
  GPIO 5               Ultrasonic Trig Pin   Digital Output      3.3V / 5.0V TTL
                                                                                     output
                                                                                     Pulse-width return
  GPIO 18              Ultrasonic Echo Pin   Digital Input       3.3V Logic Level    via 1kΩ/2kΩ voltage
                                                                                     divider
                                                                 3.3V GPIO
                       Relay 1 (Drain                            control; 5.0V       Active-LOW
  GPIO 25                                    Digital Output                          optocoupler trigger
                       Pump)                                     relay-module        driver
                                                                 supply
                                                                 3.3V GPIO
                       Relay 2 (Refill                           control; 5.0V       Active-LOW
  GPIO 26                                    Digital Output                          optocoupler trigger
                       Pump)                                     relay-module        driver
                                                                 supply
                                                                 3.3V PWM
                       Servo Motor                               control; 5.0V       50 Hz hardware
  GPIO 13                                    PWM Output                              PWM (1.0 ms -- 2.0
                       (Feeder)                                  external servo      ms duty cycle)
                                                                 supply
                                                                                     Used instead of the
                       pH Sensor
                                                                                     standard 5V to
  3.3V                 (pH-4502C) & TDS      Sensor Power Rail   3.3V DC
                                                                                     protect the ESP32
                       Sensor Supply
                                                                                     ADC pins
                                                                                     Filtered with 470 μF
  VIN / 5V             LM2596 Output Rail    Regulated Power     5.0V DC (±2%)
                                                                                     + 0.1 μF capacitors
                                                                                     Common ground
  GND                  Common Ground         Ground Rail         0.0V Reference      plane for MCU,
                                                                                     sensors, and power


A.2 AquaShield REST API Endpoints Specification
Live sensor telemetry, historical records, pump command states, and calibration values are
exchanged through the Firebase Realtime Database; the REST endpoints below are served by the
Python FastAPI machine learning backend.

         Table A.2: AquaShield REST API Endpoints Specification (Python FastAPI ML Backend)




                                                      47
                                                           Description & Response
HTTP Method   API Route Endpoint    Payload / Parameters
                                                           Output
                                                           Returns predicted
GET           /api/v1/forecast      horizon=3              Bahadurabad river water
                                                           level and alert tier
                                                           Returns predicted +60m
GET           /api/v1/tds           device_id              TDS value with SHAP
                                                           feature rankings
                                                           Returns current Isolation
GET           /api/v1/anomaly       device_id              Forest score and
                                                           multivariate flag




                                   48
References
[1] Department of Fisheries (DoF), 'Yearbook of Fisheries Statistics of Bangladesh 2022-23,' Ministry of
     Fisheries and Livestock, Dhaka, 2023.
[2] Food and Agriculture Organization (FAO), 'The State of World Fisheries and Aquaculture 2024,' FAO,
     Rome, Italy, 2024.
[3] Flood Forecasting and Warning Centre (FFWC), 'Annual Flood Report 2020,' BWDB, Dhaka, Bangladesh,
     2021.
[4] M. M. Rahman, M. A. Hossain, and S. Islam, 'Impact of climate change and extreme monsoon flooding on
     inland aquaculture in northern Bangladesh,' Journal of Water and Climate Change, vol. 12, no. 4, pp.
     1420--1435, 2021.
[5] C. E. Boyd, Water Quality: An Introduction, 3rd ed., Cham, Switzerland: Springer Nature, 2020.
[6] J. E. Colt, Dissolved Gas Concentration in Water, 2nd ed., London: Academic Press, 2012.
[7] P. Saha, D. Biswas, and A. K. Das, 'IoT-based automated water quality monitoring and alert system for fish
      farming,' in Proc. IEEE ICSCEE, Shah Alam, Malaysia, 2018, pp. 1--6.
[8] K. R. Raju, G. H. Kumar, and M. V. Reddy, 'Automated water quality monitoring and control system for
     aquaculture using Raspberry Pi,' IEEE IoT Journal, vol. 7, no. 9, pp. 8412--8421, 2020.
[9] M. R. Hasan, M. S. Alam, and T. Sultana, 'Design and deployment of a low-cost IoT telemetry node for rural
     fish ponds in Bangladesh,' in Proc. IEEE ICEEICT, Dhaka, 2021, pp. 215--220.
[10] M. N. Islam, S. K. Roy, and R. Ahmed, 'Predictive water aeration and quality management using ESP32
     edge microcontroller,' IEEE Access, vol. 10, pp. 54312--54324, 2022.
[11] X. Chen, Y. Zhang, and L. Wang, 'Industrial PLC-driven multi-parameter recirculating aquaculture control
     system with deep LSTM DO prediction,' Computers and Electronics in Agriculture, vol. 205, art. no.
     107621, 2023.
[12] S. Ahmed, F. Farzana, and K. M. Kabir, 'Automated fish feeding and pond level management system using
     IoT relays and ultrasonic sensing,' in Proc. IEEE CONECCT, Bangalore, 2024, pp. 1--6.
[13] F. T. Liu, K. M. Ting, and Z.-H. Zhou, 'Isolation Forest,' in Proc. 8th IEEE ICDM, Pisa, Italy, 2008, pp.
     413--422.
[14] S. M. Lundberg and S.-I. Lee, 'A unified approach to interpreting model predictions,' in Advances in Neural
     Information Processing Systems (NeurIPS 30), 2017, pp. 4765--4774.
[15] T. Chen and C. Guestrin, 'XGBoost: A scalable tree boosting system,' in Proc. 22nd ACM SIGKDD, 2016,
     pp. 785--794.
[16] L. Breiman, 'Random Forests,' Machine Learning, vol. 45, no. 1, pp. 5--32, 2001.
[17] A. E. Hoerl and R. W. Kennard, 'Ridge regression: Biased estimation for nonorthogonal problems,'
     Technometrics, vol. 12, no. 1, pp. 55--67, 1970.
[18] R. Tibshirani, 'Regression shrinkage and selection via the Lasso,' Journal of the Royal Statistical Society:
     Series B, vol. 58, no. 1, pp. 267--288, 1996.
[19] J. E. Nash and J. V. Sutcliffe, 'River flow forecasting through conceptual models part I,' Journal of
     Hydrology, vol. 10, no. 3, pp. 282--290, 1970.
[20] H. Hersbach et al., 'The ERA5 global reanalysis,' Quarterly Journal of the Royal Meteorological Society,
     vol. 146, no. 730, pp. 1999--2049, 2020.
[21] Bangladesh Water Development Board (BWDB), 'Hydrometric Data Portal: Daily Water Levels and
     Discharges (Station SW46.9L),' BWDB Hydrology Division, Dhaka, 2024.
[22] Espressif Systems, 'ESP32 Series Datasheet: 2.4 GHz Wi-Fi and Bluetooth Combo Chip,' Espressif
     Systems, Shanghai, China, 2023.
[23] F. Pedregosa et al., 'Scikit-learn: Machine learning in Python,' Journal of Machine Learning Research, vol.
     12, pp. 2825--2830, 2011.
[24] Board of Accreditation for Engineering and Technical Education (BAETE), 'Manual for Accrediting
     Undergraduate Engineering Programmes,' IEB, Dhaka, Ver. 2.1, 2023.



                                                      49
[25] University of Information Technology and Sciences (UITS), 'Capstone Project and Thesis Guidelines:
     Department of Computer Science and Engineering,' UITS Academic Council, Dhaka, Bangladesh, 2026.




                                                  50
Plagiarism Report
[Official Institutional Plagiarism Verification Report to be inserted here]

In accordance with Department of Computer Science and Engineering capstone guidelines, the
final project book must include the official similarity report from the university-designated
plagiarism checking software (Turnitin / iThenticate). Upon completion of the final defense and
review board revisions, the verified digital originality certificate will be attached to this
designated section prior to final hardcover binding.




      Supervisor: Sultana Rokeya Naher, Associate Professor




                                                 51
