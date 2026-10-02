AquaShield: Intelligent Aquaculture Monitoring and Adaptive Protection
System Using Machine Learning and IoT

By

1.  Md. Shahriar hossain srabon ID: 0432310005101056

2.  Md. Mahfuz ID: 0432310005101057

3.  Hrithik saha ID: 0432310005101071

Department of Computer Science and Engineering Faculty of Science and
Engineering

A Capstone Project Submitted in partial fulfillment of the requirements
for the degree of Bachelor of Science in Computer Science and
Engineering

Supervised By

Sultana Rokeya Naher Associate Professor Department of Computer Science
and Engineering

University of Information Technology and Sciences (UITS) Baridhara J
Block, Dhaka 1212 May, 2026

Declaration

The capstone project work entitled "AquaShield: Intelligent Aquaculture
Monitoring and Adaptive Protection System Using Machine Learning and
IoT" is a bonafide record of work carried out by Md. Shahriar hossain
srabon (ID: 0432310005101056), Md. Mahfuz (ID: 0432310005101057), and
Hrithik saha (ID: 0432310005101071) under the supervision of Sultana
Rokeya Naher, Associate Professor, Department of Computer Science and
Engineering (CSE), University of Information Technology and Sciences
(UITS), Dhaka, Bangladesh.

This work, in whole or in part, has not been submitted elsewhere for the
award of any degree or diploma.

Candidates:

------------------------------------------------------------------------

1.  Md. Shahriar hossain srabon Student ID: 0432310005101056 Department
    of Computer Science and Engineering, UITS

------------------------------------------------------------------------

2.  Md. Mahfuz Student ID: 0432310005101057 Department of Computer
    Science and Engineering, UITS

------------------------------------------------------------------------

3.  Hrithik saha Student ID: 0432310005101071 Department of Computer
    Science and Engineering, UITS

Approval

This is to certify that the capstone project work submitted by Md.
Shahriar hossain srabon (ID: 0432310005101056), Md. Mahfuz (ID:
0432310005101057), and Hrithik saha (ID: 0432310005101071) entitled
"AquaShield: Intelligent Aquaculture Monitoring and Adaptive Protection
System Using Machine Learning and IoT" has been examined and approved by
the Capstone Project Review Committee in partial fulfillment of the
requirements for the degree of Bachelor of Science in Computer Science
and Engineering (CSE) in the Department of Computer Science and
Engineering (CSE), University of Information Technology and Sciences
(UITS), Dhaka, Bangladesh in Spring 2026.

CAPSTONE PROJECT REVIEW COMMITTEE

1.  ................................................................
    Sultana Rokeya Naher Associate Professor & Supervisor Department of
    Computer Science and Engineering (CSE) University of Information
    Technology and Sciences (UITS) (Chairman)

2.  ................................................................
    \[Head of Department Name\] Head of the Department Department of
    Computer Science and Engineering (CSE) University of Information
    Technology and Sciences (UITS) (Member)

3.  ................................................................
    \[External Examiner Name\] Professor / External Expert Department of
    Computer Science and Engineering University of Information
    Technology and Sciences (UITS) (Member (External))

4.  ................................................................
    \[Internal Coordinator Name\] Coordinator, Capstone Project
    Committee Department of Computer Science and Engineering (CSE)
    University of Information Technology and Sciences (UITS) (Member
    Secretary)

Acknowledgement

First of all, we thank Almighty Allah for giving us the patience,
health, and ability to complete our capstone engineering project.

We express our sincere gratitude to our supervisor, Sultana Rokeya
Naher, Associate Professor, Department of Computer Science and
Engineering, University of Information Technology and Sciences (UITS).
Her constant advice, regular feedback, and encouragement helped us solve
practical hardware problems, design our database, and evaluate our
machine learning models correctly.

We also thank the Head of the Department of Computer Science and
Engineering and all our teachers and lab staff at UITS for their support
and for providing us with the necessary computing and laboratory
facilities during our study.

We are thankful to the Bangladesh Water Development Board (BWDB) and
Flood Forecasting and Warning Centre (FFWC) for making historical river
gauge records available. We also acknowledge Open-Meteo for providing
free ERA5 catchment rainfall data.

Finally, we are grateful to our parents and family members for their
continuous support and sacrifices throughout our university life. We
also thank each other for working together as a team with dedication to
build AquaShield.

Justification Report

Below is the Course Outcome to Program Outcome (CO-PO) Mapping,
Justification of PO through COs, Complex Engineering Problem (CEP)
Justification, and Range of Complex Engineering Activities (CEA) Report
for our project titled "AquaShield: Intelligent Aquaculture Monitoring
and Adaptive Protection System Using Machine Learning and IoT".

1.  CO-PO Mapping

Table 0.1: CO-PO Mapping Matrix for AquaShield

  ---------------------------------------------------------------------------------
  CO No.         Description of CO     KP             CP             CA
  -------------- --------------------- -------------- -------------- --------------
  CO1            Apply engineering     K1, K2, K3, K4 \-             \-
                 fundamentals and                                    
                 computing knowledge                                 
                 to identify and                                     
                 translate real-life                                 
                 aquaculture water                                   
                 quality problems and                                
                 monsoon flood threats                               
                 into an intelligent                                 
                 IoT and ML solution.                                

  CO2            Identify, formulate,  K2, K3, K4     WP1, WP2, WP3  \-
                 and analyze water                                   
                 quality requirements                                
                 (pH, TDS,                                           
                 temperature, depth)                                 
                 and flood threshold                                 
                 limits to reach                                     
                 substantiated                                       
                 conclusions using                                   
                 data.                                               

  CO3            Design and build an   K3, K5, K6     WP1, WP3, WP5  \-
                 integrated system                                   
                 combining an ESP32                                  
                 sensor node, local                                  
                 relay control logic,                                
                 cloud data storage,                                 
                 and machine learning                                
                 prediction models.                                  

  CO4            Select and apply      K3, K5, K6     WP1, WP3, WP4  \-
                 modern hardware and                                 
                 software tools                                      
                 including ESP32,                                    
                 Arduino C++, Node.js,                               
                 Express, MongoDB                                    
                 Atlas, Socket.io,                                   
                 Scikit-learn, and                                   
                 XGBoost.                                            

  CO5            Function effectively  \-             \-             \-
                 as individual                                       
                 contributors and as a                               
                 3-member engineering                                
                 team with clear task                                
                 distribution and                                    
                 regular coordination.                               

  CO6            Demonstrate project   \-             \-             \-
                 management and                                      
                 budgeting skills by                                 
                 keeping the total                                   
                 prototype hardware                                  
                 cost under 7,200 BDT                                
                 (\~\$60) for rural                                  
                 fish farmers.                                       

  CO7            Conduct experimental  K6, K8         WP1, WP2, WP3  \-
                 investigations using                                
                 laboratory buffer                                   
                 solutions for sensor                                
                 calibration and 15                                  
                 years of river data                                 
                 with                                                
                 Leave-One-Year-Out                                  
                 validation.                                         

  CO8            Assess the real-world K8, K7         WP1, WP3, WP4  \-
                 impact of the project                               
                 on rural aquaculture,                               
                 protecting fish from                                
                 mortality and saving                                
                 farmers from severe                                 
                 financial loss.                                     

  CO9            Evaluate              K7             \-             \-
                 environmental                                       
                 sustainability by                                   
                 minimizing water                                    
                 pumping, preventing                                 
                 chemical                                            
                 over-concentration,                                 
                 and avoiding feed                                   
                 wastage.                                            

  CO10           Commit to             K7             \-             \-
                 professional                                        
                 engineering ethics by                               
                 reporting true                                      
                 empirical results,                                  
                 citing all references                               
                 properly, and                                       
                 explaining model                                    
                 predictions with                                    
                 SHAP.                                               

  CO11           Communicate           \-             \-             EA1, EA2, EA3,
                 engineering work                                    EA5
                 clearly through a                                   
                 complete written                                    
                 technical project                                   
                 book and oral defense                               
                 presentation.                                       

  CO12           Recognize the need    \-             \-             \-
                 for lifelong learning                               
                 by researching future                               
                 system extensions                                   
                 like on-device TinyML                               
                 and LoRaWAN wireless                                
                 networks.                                           
  ---------------------------------------------------------------------------------

2.  Justification of PO through COs

Requirement: Note - During justification you have to mention where you
have added relevant data/information in your report.

Table 0.2: Justification of PO through COs for AquaShield

  -----------------------------------------------------------------------
  CO No.                  PO                      Justification (with
                                                  Specific Report
                                                  References)
  ----------------------- ----------------------- -----------------------
  CO1                     PO1                     We applied basic
                                                  electronics, sensor
                                                  physics (Nernst
                                                  equation for pH,
                                                  electrical conductivity
                                                  for TDS, ultrasonic
                                                  time-of-flight), and
                                                  machine learning
                                                  regression to solve
                                                  real-world pond water
                                                  deterioration and river
                                                  flood overflow in
                                                  Bangladesh. (Reported
                                                  in Section 1.2, 3.3,
                                                  and 3.6).

  CO2                     PO2                     We formulated the
                                                  technical requirements
                                                  for pond water
                                                  monitoring and river
                                                  flood warnings,
                                                  defining mathematical
                                                  conversion formulas,
                                                  1-hour TDS lag
                                                  features, and water
                                                  danger thresholds
                                                  evaluated using RMSE,
                                                  MAE, and NSE metrics.
                                                  (Reported in Section
                                                  1.3, 3.6, and 5.3).

  CO3                     PO3                     We designed and
                                                  assembled the complete
                                                  system: an ESP32 edge
                                                  node with
                                                  optocoupler-isolated
                                                  relays, local
                                                  autonomous FSM rules
                                                  for pumps and aerators,
                                                  an MQTT cloud broker,
                                                  and three machine
                                                  learning models.
                                                  (Reported in Chapters 3
                                                  and 4).

  CO4                     PO5                     We selected and used
                                                  standard modern
                                                  engineering tools
                                                  including ESP32 32-bit
                                                  MCU, PlatformIO/Arduino
                                                  IDE, Node.js Express,
                                                  MongoDB Atlas,
                                                  Socket.io, Python
                                                  Scikit-learn, XGBoost,
                                                  and SHAP. (Reported in
                                                  Section 4.2 to 4.6).

  CO5                     PO9                     Our 3-member team
                                                  divided tasks
                                                  effectively: Srabon
                                                  handled hardware
                                                  fabrication and power
                                                  wiring, Mahfuz built
                                                  the cloud server and
                                                  web dashboard, and
                                                  Hrithik developed the
                                                  ML flood forecasting
                                                  and anomaly detection
                                                  models. (Reported in
                                                  Section 1.5 and 4.1).

  CO6                     PO11                    We managed component
                                                  procurement and
                                                  prepared a detailed
                                                  Bill of Materials
                                                  totaling 7,120 BDT
                                                  (\$59.75 USD), proving
                                                  our system is
                                                  affordable for marginal
                                                  fish farmers in
                                                  Bangladesh. (Reported
                                                  in Section 3.3, Table
                                                  3.1).

  CO7                     PO4                     We conducted practical
                                                  investigations: we
                                                  calibrated sensors with
                                                  standard buffer
                                                  solutions and validated
                                                  our river flood model
                                                  on 15 years
                                                  (2008--2022) of BWDB
                                                  records using
                                                  Leave-One-Year-Out
                                                  (LOYO) cross-validation
                                                  to prevent data
                                                  leakage. (Reported in
                                                  Section 3.7 and 5.3).

  CO8                     PO6                     We evaluated the
                                                  socioeconomic impact on
                                                  rural communities:
                                                  preventing fish kills
                                                  protects farmer income,
                                                  safeguards food
                                                  security, and avoids
                                                  financial devastation
                                                  during monsoon river
                                                  overflows. (Reported in
                                                  Section 1.1, 2.2, and
                                                  6.2).

  CO9                     PO7                     We designed closed-loop
                                                  control rules that save
                                                  water by pumping only
                                                  when necessary, prevent
                                                  pond pollution from
                                                  excess feed, and use
                                                  energy-efficient 12V DC
                                                  power components.
                                                  (Reported in Section
                                                  3.4 and 6.2).

  CO10                    PO8                     We maintained academic
                                                  honesty by using real
                                                  observed datasets,
                                                  reporting actual
                                                  prediction errors
                                                  without bias,
                                                  explaining tree
                                                  predictions via SHAP,
                                                  and properly citing all
                                                  literature. (Reported
                                                  in Section 5.4, 5.7,
                                                  and References).

  CO11                    PO10                    We wrote this complete,
                                                  well-documented
                                                  technical capstone
                                                  report adhering to UITS
                                                  and IEEE standards,
                                                  created 13 detailed
                                                  figures and 22 tables,
                                                  and prepared slides for
                                                  our oral defense.
                                                  (Reported throughout
                                                  the entire book and
                                                  Appendix B).

  CO12                    PO12                    We recognized that
                                                  technology continues to
                                                  evolve, so we studied
                                                  and documented future
                                                  upgrade paths including
                                                  running TinyML directly
                                                  on the ESP32 and adding
                                                  LoRaWAN mesh
                                                  networking. (Reported
                                                  in Section 6.4).
  -----------------------------------------------------------------------

3.  Complex Engineering Problem (CEP) Justification

Requirement: Note - During justification you have to mention where you
have added relevant data/information in your report.

Table 0.3: Complex Engineering Problem (CEP) Justification Matrix

  -----------------------------------------------------------------------
  Attribute Category      Attribute Name & ID     BAETE Criteria &
                                                  Project Justification
                                                  (with Report
                                                  References)
  ----------------------- ----------------------- -----------------------
  1\. Mandatory Attribute Depth of Knowledge (P1) Solving this problem
                                                  required knowledge from
                                                  multiple engineering
                                                  fields (K4): embedded
                                                  systems (ADC
                                                  oversampling, 1-Wire,
                                                  I2C), asynchronous
                                                  networking (MQTT QoS 1,
                                                  WebSockets),
                                                  time-series machine
                                                  learning, and
                                                  Explainable AI (SHAP).
                                                  We studied research
                                                  literature (K8) to
                                                  handle time-series data
                                                  leakage and peak
                                                  extrapolation.
                                                  (Reported in Section
                                                  2.4, 2.5, 3.6, 5.3).

  2\. Supporting          Range of Conflicting    We balanced conflicting
  Attribute               Requirements (P2)       constraints: low
                                                  hardware cost (\<\$60)
                                                  vs. good sensor
                                                  accuracy; real-time
                                                  cloud updates
                                                  vs. frequent rural
                                                  internet dropouts; and
                                                  long flood forecast
                                                  horizons (+14 days)
                                                  vs. growing prediction
                                                  error. (Reported in
                                                  Section 1.2, 3.4, 5.6).

  3\. Supporting          Depth of Analysis       Standard random
  Attribute               Required (P3)           train-test splitting
                                                  fails on river data
                                                  because it leaks future
                                                  temporal information.
                                                  We designed a
                                                  Leave-One-Year-Out
                                                  cross-validation scheme
                                                  and analyzed stratified
                                                  water-level errors
                                                  across 5,479 days to
                                                  prove why linear models
                                                  beat tree models during
                                                  extreme flood crests.
                                                  (Reported in Section
                                                  3.7, 5.3, 5.7).

  4\. Supporting          Familiarity of Issues   Real aquaculture ponds
  Attribute               (P4)                    do not have labeled
                                                  'good water' vs. 'bad
                                                  water' datasets. We
                                                  handled this unfamiliar
                                                  unsupervised scenario
                                                  by combining sensor
                                                  rate-of-change deltas
                                                  with Isolation Forest,
                                                  successfully isolating
                                                  dangerous multivariate
                                                  conditions like high
                                                  pH + high temperature.
                                                  (Reported in Section
                                                  2.2, 3.6.3, 5.5).

  5\. Supporting          Interdependence (P7)    The parts of our system
  Attribute                                       depend heavily on each
                                                  other: hardware ADC
                                                  calibration directly
                                                  determines data
                                                  accuracy; clean cloud
                                                  data feeds the ML
                                                  models; and ML flood
                                                  early warnings give
                                                  farmers lead time to
                                                  raise perimeter
                                                  netting. (Reported in
                                                  Section 3.2, 4.7, 5.6).
  -----------------------------------------------------------------------

4.  Range of Complex Engineering Activities (CEA) Justification

Table 0.4: Range of Complex Engineering Activities (CEA) Justification
Matrix

  -----------------------------------------------------------------------
  Activity ID             Activity Title          Engineering Activity
                                                  Justification (with
                                                  Report References)
  ----------------------- ----------------------- -----------------------
  A1                      Range of Resources      We utilized diverse
                                                  hardware components
                                                  (ESP32, pH-4502C, TDS
                                                  probe, DS18B20,
                                                  HC-SR04, optocoupled
                                                  relays, buck
                                                  converter), software
                                                  stacks (Node.js,
                                                  Express, MongoDB Atlas,
                                                  Socket.io, Tailwind
                                                  CSS), and 15 years of
                                                  BWDB hydrological
                                                  records and ERA5
                                                  rainfall data.
                                                  (Reported in Chapter 3
                                                  and Chapter 4).

  A3                      Innovation              We combined macro-scale
                                                  river flood forecasting
                                                  (giving 3 to 7 days
                                                  warning to protect pond
                                                  dikes) with micro-scale
                                                  pond water automation
                                                  and unsupervised
                                                  anomaly detection,
                                                  adding SHAP
                                                  explainability so
                                                  farmers can understand
                                                  the alerts. (Reported
                                                  in Section 3.2, 3.6,
                                                  5.4).

  A4                      Consequences for        Our project directly
                          Society & Environment   helps fish farmers in
                                                  flood-prone districts
                                                  of Bangladesh avoid
                                                  financial bankruptcy,
                                                  protects national food
                                                  supply, reduces clean
                                                  water wastage, and
                                                  avoids toxic chemical
                                                  spikes. (Reported in
                                                  Section 1.1, 2.2, 6.2).
  -----------------------------------------------------------------------

Mapping to PO10 (Communication)

Table 0.5: Mapping of Project Deliverables to PO10 Communication

  -----------------------------------------------------------------------
  Communication Component Engineering Deliverable Evaluation Criterion
                          & Scope                 
  ----------------------- ----------------------- -----------------------
  Written Technical       Prepared an effective,  Technical Book
  Documents               detailed capstone       Assessment
                          project report          
                          following UITS format   
                          and IEEE citation       
                          standards.              

  Oral Presentations      Prepared and rehearsed  Oral Defense Evaluation
                          formal multimedia       
                          presentation slides for 
                          the Capstone Review     
                          Committee defense.      

  Visual Representation   Created 13 technical    Visual Clarity & Rigor
                          figures including       
                          system architecture,    
                          hydrographs, 1-to-1     
                          scatter plots, SHAP     
                          summary plots, and web  
                          dashboard screenshots.  
  -----------------------------------------------------------------------

Abstract

Fish farming is a major part of Bangladesh's economy, producing over
3.5% of the national GDP and supplying 60% of animal protein. However,
fish farmers in Bangladesh face two major dangers: sudden, unmonitored
pond water deterioration leading to massive fish mortality, and seasonal
monsoon river flooding that overtops pond dikes and washes away entire
fish stocks. Most small-scale farmers still rely on manual observation
and occasional water test kits, which fail to provide timely warnings.
To address these problems, this capstone project presents AquaShield, an
integrated, low-cost IoT system combined with a three-tier predictive
Machine Learning (ML) decision-support engine.

The physical edge node consists of an ESP32 microcontroller connected to
analog pH, Total Dissolved Solids (TDS), digital temperature (DS18B20),
and ultrasonic water-level sensors (HC-SR04). The firmware runs an
autonomous Finite State Machine (FSM) every 30 seconds to control a
4-channel optoisolated relay module driving drain pumps, refill pumps,
an aerator, and an automated servo fish feeder. The edge node includes
offline fail-safe logic: if Wi-Fi or cloud connections drop, local
safety rules continue to operate and readings are saved to flash memory.
Data is sent via MQTT to a Node.js, Express, and MongoDB Atlas cloud
backend, updating a live web dashboard via Socket.io and sending instant
emergency alerts through Telegram.

The machine learning subsystem includes three models: (1) River
water-level forecasting at Bahadurabad transit on the Jamuna River,
trained on 15 years (2008--2022) of BWDB hydrometric data and ERA5
catchment rainfall. Using Leave-One-Year-Out (LOYO) cross-validation
across 1 to 14-day lead times, regularized Linear Regression achieved a
Nash-Sutcliffe Efficiency (NSE) of 0.985 and RMSE of 0.308 m on unseen
2020--2022 test years, beating tree models because linear models
extrapolate flood peaks without hitting a ceiling. (2) Short-horizon
pond TDS forecasting (+60 minutes) using rolling averages, where Linear
Regression (MAE: 7.05 ppm, R²: 0.888) outperformed tree ensembles that
overfit sensor noise, verified using SHAP. (3) Unsupervised multivariate
anomaly detection using Isolation Forest and sensor rate-of-change
deltas, which detects dangerous multi-parameter conditions (such as pH
8.2 at 32°C creating lethal ammonia gas) that bypass single-parameter
threshold limits. Built for under 7,200 BDT (\~\$60), AquaShield
provides an affordable, dependable decision-support system for fish
farmers in Bangladesh.

Keywords: Internet of Things (IoT), Aquaculture Management, Water
Quality Monitoring, River Flood Early Warning, Machine Learning,
Explainable AI (SHAP).

Preface

This Bachelor of Science (B.Sc.) capstone project report describes the
engineering design, embedded hardware prototyping, cloud software
development, and machine learning experiments conducted in the
Department of Computer Science and Engineering (CSE), Faculty of Science
and Engineering, at the University of Information Technology and
Sciences (UITS), Dhaka, Bangladesh.

The project is structured into six chapters, summarized below:

Chapter 1 (Introduction): Introduces aquaculture in Bangladesh, explains
the problems of silent water quality deterioration and monsoon river
flooding, defines the technical goals of AquaShield, and outlines the
project scope.

Chapter 2 (Background Studies & Literature Review): Explains key pond
water quality parameters (pH, TDS, temperature, ammonia), reviews
monsoon flood patterns in the Jamuna basin, surveys existing IoT
aquaculture systems, reviews machine learning in hydrology, and
summarizes technical gaps.

Chapter 3 (System Methodology & Architecture): Presents the overall
5-tier architecture, hardware sensor equations, edge FSM actuation
rules, offline fail-safe logic, cloud telemetry, mathematical formulas
for the three ML models, and validation protocols.

Chapter 4 (Implementation): Details the physical hardware build, power
supply design, ESP32 C++ firmware with ADC oversampling, Node.js and
MongoDB cloud services, Python ML pipelines, web dashboard, and Telegram
alert integration.

Chapter 5 (Result Analysis and Discussion): Presents laboratory sensor
calibration results, Model 1 river flood forecasting performance across
1 to 14 days with peak extrapolation analysis, Model 2 TDS forecasts
with SHAP plots, Model 3 multivariate anomaly isolation, system latency
benchmarks, and defense Q&A preparation.

Chapter 6 (Conclusion & Future Work): Summarizes our main engineering
achievements, discusses project limitations, and outlines future
improvements such as TinyML and LoRaWAN long-range networking.

Appendices & References: Appendix A provides complete pinout connections
and REST API routes. Appendix B provides our Defense Q&A Master Sheet.
References lists 28 formal IEEE citations, followed by the institutional
Plagiarism Report placeholder.

Table of Contents

Table 0.6: Master Table of Contents

  -----------------------------------------------------------------------
  Item / Chapter Section              Page
  ----------------------------------- -----------------------------------
  Declaration                         ii

  Approval                            iii

  Acknowledgements                    iv

  Justification Report (CO-PO, CEP &  v
  CEA Tables)                         

  Abstract                            ix

  Preface                             x

  Table of Contents                   xii

  List of Figures                     xiv

  List of Tables                      xv

  Abbreviations and Symbols           xvi

  Chapter 1: Introduction             1

  1.1 Introduction and Background     1

  1.2 Problem Statement & Motivation  2

  1.3 Aims and Objectives             3

  1.4 Scope and Limitations           4

  1.5 Organization of the Report      5

  1.6 Conclusion                      5

  Chapter 2: Background Studies &     6
  Literature Review                   

  2.1 Introduction                    6

  2.2 Aquaculture Challenges and      6
  Water Quality Dynamics              

  2.3 Monsoon Flooding Risks and      8
  Early Warning Needs                 

  2.4 Review of Existing IoT          9
  Aquaculture Monitoring Systems      

  2.5 Machine Learning in Hydrology & 11
  Water Quality                       

  2.6 Comparative Analysis of Related 13
  Works and Technical Gaps            

  2.7 Conclusion                      14

  Chapter 3: System Methodology &     15
  Architecture                        

  3.1 Introduction                    15

  3.2 Overall System Architecture and 15
  Telemetry Pipeline                  

  3.3 Hardware Design and Edge        17
  Sensing Layer                       

  3.4 Local Edge Control Logic,       20
  Fail-Safe Automation, and Actuator  
  Drivers                             

  3.5 Cloud Telemetry, REST API, and  22
  Database Schema                     

  3.6 Machine Learning Subsystem      24
  Methodology                         

  3.6.1 Model 1: River Water-Level    24
  Forecasting (Bahadurabad Station)   

  3.6.2 Model 2: Pond TDS Forecasting 26
  (+60 Minutes Ahead)                 

  3.6.3 Model 3: Unsupervised Pond    27
  Water-Quality Anomaly Detection     

  3.7 Model Validation Protocols      29
  (LOYO CV and Chronological          
  Splitting)                          

  3.8 Conclusion                      31

  Chapter 4: Implementation           32

  4.1 Introduction                    32

  4.2 Hardware Fabrication, Circuit   32
  Wiring, and Power Supply Setup      

  4.3 ESP32 Firmware Development &    34
  Local Sensing Pipeline              

  4.4 Cloud Backend & Database        36
  Service Implementation              

  4.5 Machine Learning Subsystem      37
  Implementation & Deployment         
  Pipeline                            

  4.6 Web Dashboard & Sensor          39
  Calibration Interface Development   

  4.7 Automated Alerting Subsystem &  41
  Telegram Bot Integration            

  4.8 Conclusion                      42

  Chapter 5: Result Analysis and      43
  Discussion                          

  5.1 Introduction                    43

  5.2 IoT Hardware Performance and    43
  Sensor Calibration Results          

  5.3 Model 1 (River Flood Forecast)  45
  Experimental Evaluation             

  5.4 Model 2 (Pond TDS Forecast)     50
  Results and SHAP Explainability     

  5.5 Model 3 (Pond Anomaly           53
  Detection) Evaluation and           
  Diagnostic Analysis                 

  5.6 Real-Time Actuation Latency,    55
  Cloud Throughput, and Reliability   

  5.7 Comprehensive Discussion &      56
  Technical Defense Insights          

  5.8 Conclusion                      58

  Chapter 6: Conclusion and Future    59
  Work                                

  6.1 Conclusion                      59

  6.2 Summary of Key Research &       60
  Engineering Contributions           

  6.3 Project Limitations             61

  6.4 Future Recommendations          61

  Appendix A: Circuit Schematic, Pin  63
  Mappings, and REST API Endpoints    

  Appendix B: Technical Defense       66
  Preparation & Oral Defense Q&A      
  Master Sheet                        

  References (IEEE Format)            69

  Plagiarism Report                   72
  -----------------------------------------------------------------------

List of Figures

Table 0.7: Master List of Figures

  -----------------------------------------------------------------------
  Figure No.              Figure Caption Name     Page
  ----------------------- ----------------------- -----------------------
  Figure 3.1              High-level 5-tier       16
                          cyber-physical          
                          architecture of the     
                          AquaShield system       

  Figure 3.2              Leave-One-Year-Out      30
                          (LOYO) cross-validation 
                          and holdout testing     
                          workflow                

  Figure 5.1              Correlation and         46
                          physical lag dynamics   
                          between catchment       
                          rainfall and water      
                          level                   

  Figure 5.2              Model Root Mean Squared 47
                          Error (RMSE)            
                          vs. forecast lead time  
                          (1 to 14 days)          

  Figure 5.3              Flood season            48
                          hydrographs: observed   
                          vs. predicted water     
                          levels during peak      
                          monsoons                

  Figure 5.4              Model 1 feature         49
                          importance distribution 
                          shifting from lag       
                          levels to rainfall sums 

  Figure 5.5              Final holdout           50
                          performance on unseen   
                          2020--2022 monsoon      
                          seasons (+3 days        
                          horizon)                

  Figure 5.6              Model 2 performance     51
                          comparison bar chart    
                          across MAE, RMSE, and   
                          R² metrics              

  Figure 5.7              Model 2 actual          52
                          vs. predicted TDS time  
                          series over held-out    
                          test data (+60 mins)    

  Figure 5.8              SHAP summary plot       53
                          explaining feature      
                          contributions for pond  
                          TDS predictions         

  Figure 5.9              Model 3 bivariate       54
                          scatter plot (pH        
                          vs. TDS) highlighting   
                          detected multivariate   
                          anomalies               

  Figure 5.10             Model 3 anomaly         55
                          detection timeline      
                          traced along continuous 
                          TDS sensor readings     

  Figure 5.11             Isolation Forest        55
                          anomaly score           
                          distribution and 5%     
                          contamination threshold 
                          cutoff                  
  -----------------------------------------------------------------------

List of Tables

Table 0.8: Master List of Tables

  -----------------------------------------------------------------------
  Table No.               Table Title             Page
  ----------------------- ----------------------- -----------------------
  Table 0.1               CO-PO Mapping Matrix    v
                          for AquaShield          

  Table 0.2               Justification of PO     vi
                          through COs for         
                          AquaShield              

  Table 0.3               Complex Engineering     vii
                          Problem (CEP)           
                          Justification Matrix    

  Table 0.4               Range of Complex        viii
                          Engineering Activities  
                          (CEA) Justification     
                          Matrix                  

  Table 0.5               Mapping of Project      viii
                          Deliverables to PO10    
                          Communication           

  Table 0.6               Master Table of         xii
                          Contents                

  Table 0.7               Master List of Figures  xiv

  Table 0.8               Master List of Tables   xv

  Table 2.1               Water Quality           7
                          Thresholds and          
                          Biological Tolerance    
                          for Major Farmed Fish   
                          Species                 

  Table 2.2               Comparative Feature     14
                          Matrix of Existing      
                          Aquaculture Systems     
                          vs. AquaShield          

  Table 3.1               Hardware Bill of        19
                          Materials (BOM) and     
                          Cost Breakdown          

  Table 3.2               Summary of Primary      20
                          Hardware Pin            
                          Assignments on ESP32    

  Table 3.3               Summary of Edge Finite  21
                          State Machine (FSM)     
                          Actuation Rules         

  Table 5.1               Sensor Calibration and  44
                          Precision Evaluation    
                          Across Standard         
                          Laboratory Buffers      

  Table 5.2               Bahadurabad Station     45
                          Hydrological Dataset    
                          Summary (2008--2022)    

  Table 5.3               Hyperparameter Search   46
                          Grids and Selected      
                          Optimal Values for      
                          Model 1                 

  Table 5.4               Comprehensive LOYO      47
                          Cross-Validation        
                          Performance Metrics (+1 
                          Day Horizon)            

  Table 5.5               Extreme Flood Season    48
                          and Peak Error          
                          Evaluation Metrics      

  Table 5.6               Final Holdout           50
                          Evaluation Results on   
                          Unseen 2020--2022       
                          Monsoon Seasons (+3     
                          Days)                   

  Table 5.7               Model 2 Pond TDS        51
                          Forecasting Performance 
                          Comparison (+60 Mins    
                          Horizon)                

  Table 5.8               End-to-End Latency and  56
                          Network Dropout         
                          Benchmark Results       

  Table A.1               Complete Hardware       64
                          Pinout and Bus          
                          Interfacing             
                          Specifications          

  Table A.2               AquaShield REST API     65
                          Endpoints Specification 
  -----------------------------------------------------------------------

Abbreviations and Symbols

Table 0.9: Master List of Abbreviations and Symbols

  -----------------------------------------------------------------------
  Acronym / Symbol                    Full Meaning / Definition
  ----------------------------------- -----------------------------------
  ADC                                 Analog-to-Digital Converter

  AI                                  Artificial Intelligence

  API                                 Application Programming Interface

  AR                                  Autoregressive

  BAETE                               Board of Accreditation for
                                      Engineering and Technical Education

  BLE                                 Bluetooth Low Energy

  BOD                                 Biological Oxygen Demand

  BOM                                 Bill of Materials

  BWDB                                Bangladesh Water Development Board

  CA                                  Complex Activities

  CEA                                 Complex Engineering Activities

  CEP                                 Complex Engineering Problem

  CO                                  Course Outcome

  CP                                  Complex Problem

  CPU                                 Central Processing Unit

  CSE                                 Computer Science and Engineering

  CSS                                 Cascading Style Sheets

  CV                                  Cross-Validation

  DC                                  Direct Current

  DO                                  Dissolved Oxygen

  DOY                                 Day of Year

  EEPROM                              Electrically Erasable Programmable
                                      Read-Only Memory

  ERA5                                ECMWF Reanalysis v5 Global Climate
                                      Dataset

  ESP32                               Espressif Systems 32-bit Wi-Fi/BLE
                                      Microcontroller

  FAR                                 False Alarm Rate

  FFWC                                Flood Forecasting and Warning
                                      Centre (Bangladesh)

  FSM                                 Finite State Machine

  GPIO                                General Purpose Input/Output

  HTML                                HyperText Markup Language

  HTTP                                Hypertext Transfer Protocol

  I2C                                 Inter-Integrated Circuit Bus

  IDE                                 Integrated Development Environment

  IEEE                                Institute of Electrical and
                                      Electronics Engineers

  IoT                                 Internet of Things

  JSON                                JavaScript Object Notation

  KP                                  Knowledge Profile

  LOYO                                Leave-One-Year-Out Cross-Validation

  LSTM                                Long Short-Term Memory Neural
                                      Network

  MAE                                 Mean Absolute Error

  MCU                                 Microcontroller Unit

  ML                                  Machine Learning

  MQTT                                Message Queuing Telemetry Transport

  MSE                                 Mean Squared Error

  NVS                                 Non-Volatile Storage

  NSE                                 Nash-Sutcliffe Efficiency

  OBE                                 Outcome-Based Education

  OLS                                 Ordinary Least Squares

  PCB                                 Printed Circuit Board

  pH                                  Potential of Hydrogen
                                      (Acidity/Basicity Measure)

  PHI                                 Pond Health Index

  PO                                  Program Outcome

  POD                                 Probability of Detection (Hit Rate)

  PRD                                 Product Requirements Document

  PWM                                 Pulse Width Modulation

  QoS                                 Quality of Service

  R²                                  Coefficient of Determination

  RAM                                 Random Access Memory

  REST                                Representational State Transfer

  RF                                  Random Forest Regressor

  RHWL                                Recorded Highest Water Level

  RMSE                                Root Mean Squared Error

  SHAP                                SHapley Additive exPlanations

  SPIFFS                              Serial Peripheral Interface Flash
                                      File System

  SVR                                 Support Vector Regressor

  TDS                                 Total Dissolved Solids (measured in
                                      ppm)

  UITS                                University of Information
                                      Technology and Sciences

  UI                                  User Interface

  UART                                Universal Asynchronous
                                      Receiver-Transmitter

  VDC                                 Volts Direct Current

  Wi-Fi                               Wireless Fidelity (IEEE 802.11
                                      b/g/n)

  WP                                  Workplace / Complex Problem Profile
                                      Attribute

  XAI                                 Explainable Artificial Intelligence

  XGBoost                             Extreme Gradient Boosting
  -----------------------------------------------------------------------

Chapter 1 Introduction

1.1 Introduction and Background

In Bangladesh, fish farming is one of the most vital agricultural
sectors. It contributes more than 3.5% to the national Gross Domestic
Product (GDP) and provides roughly 60% of the animal protein consumed
across the country. Over 18 million people depend on fisheries and
aquaculture for their daily livelihood. Over the last two decades, fish
farming has shifted from traditional low-density ponds to high-density
commercial aquaculture. Species like Rohu (Labeo rohita), Catla
(Gibelion catla), Pangas (Pangasius hypophthalmus), and Tilapia
(Oreochromis niloticus) are widely farmed in key aquaculture districts
such as Mymensingh, Bogura, and Jamalpur.

While high-density stocking increases fish production, it also creates
serious environmental risks in the pond. Fish waste and uneaten feed
accumulate quickly on the pond bed. When water temperature rises or pH
levels shift, harmless ammonium ions turn into toxic unionized ammonia
gas (NH3), which can kill an entire pond of fish overnight. At the same
time, because Bangladesh is a low-lying river delta, fish farms in river
basins face recurring monsoon floods. Flash floods from the Jamuna River
often overtop pond dikes, allowing mature fish to escape into open
floodwaters and wiping out a farmer's investment in a single day. To
solve both of these problems, our team designed AquaShield---an
integrated IoT and Machine Learning decision-support and automation
system built specifically for fish farmers in Bangladesh.

1.2 Problem Statement & Motivation

Small- and medium-scale fish farmers in Bangladesh struggle with four
main practical challenges:

1.  Lack of Continuous Real-Time Water Quality Monitoring: Water quality
    parameters like pH, TDS, and temperature change throughout the day
    and night. Farmers usually check water only by looking at its color
    or doing manual tests once a week. This means they only discover
    water toxicity after fish have already started dying.

2.  No Automated Protective Action: Most farms do not have automated
    controls. If a farmer is away or asleep when oxygen drops or water
    gets dirty, nobody is there to turn on the pump or aerator in time.

3.  No Data History for Decision Making: Farmers do not have recorded
    sensor history. Without real data, farmers frequently overfeed,
    which pollutes the pond bed and drives up Total Dissolved Solids.

4.  Vulnerability to Monsoon River Floods: During the monsoon season,
    sudden river surges from upstream catchments in India travel down
    the Jamuna River. Farmers receive no localized advance warnings,
    leaving them unable to raise perimeter netting or harvest their fish
    before floodwaters submerge the pond.

Our motivation was to build a reliable, low-cost system under 7,200 BDT
(\~\$60 USD). By pairing an ESP32 microcontroller with standard water
sensors and three practical machine learning models, AquaShield
automates day-to-day pond tasks (draining, refilling, aerating, and
feeding) and gives farmers advance warning of water hazards and river
floods.

1.3 Aims and Objectives

The main aim of this project is to develop and test AquaShield as an
affordable, cyber-physical aquaculture management and flood warning
system. Our specific technical objectives were:

Build a Multi-Sensor IoT Node: Assemble a hardware prototype using an
ESP32 microcontroller connected to analog pH, analog TDS, DS18B20
digital temperature, and HC-SR04 ultrasonic water-level sensors, reading
data every 30 seconds.

Program Local Edge Control Rules with Offline Fail-Safe: Write a Finite
State Machine in C++ on the ESP32 to control 4 relays for drain pumps,
refill pumps, aerator, and a servo-based fish feeder. If the internet
disconnects, the ESP32 continues to run safety rules locally and saves
readings to flash memory.

Set Up a Cloud Data Pipeline and Telegram Alerts: Use MQTT messaging, a
Node.js Express backend, MongoDB Atlas database, and Socket.io
WebSockets for live dashboard updates, and send instant emergency alerts
to the farmer's phone using the Telegram Bot API.

Develop Model 1 (River Flood Forecast): Train machine learning models
using 15 years (2008--2022) of BWDB water level records and ERA5
rainfall data for the Bahadurabad station on the Jamuna River to
forecast river levels 1 to 14 days ahead, evaluated with
Leave-One-Year-Out validation.

Develop Model 2 (Pond TDS Forecast): Predict pond Total Dissolved Solids
60 minutes ahead (t+1h) using rolling averages, comparing linear models
with tree models and explaining results with SHAP.

Develop Model 3 (Pond Anomaly Detection): Use the Isolation Forest
algorithm with sensor rate-of-change deltas to detect unusual water
conditions (like dangerous pH + temperature combinations) without
needing labeled disease datasets.

Build an Interactive Web Dashboard and Calibration Page: Create a web
dashboard showing live sensor dials, a composite Pond Health Index
(0--100), historical trend charts, manual pump switches, and an easy
two-point pH calibration wizard.

1.4 Scope and Limitations

Project Scope: Our prototype includes the physical sensor circuit, ESP32
firmware, cloud backend, live web dashboard, Telegram bot, and three
machine learning models. Model 1 is calibrated for the Bahadurabad
transit station on the Jamuna River, and Models 2 and 3 use pond IoT
sensor telemetry. The prototype uses 2.4 GHz Wi-Fi for telemetry; remote
rural ponds without Wi-Fi would require a GSM SIM module. The pH probe
requires manual cleaning every 2 to 4 weeks to remove biofilm.
AquaShield is an environmental monitoring system and does not diagnose
fish diseases directly.

1.5 Organization of the Report

This report is organized into six chapters: Chapter 1 introduces the
project background and goals; Chapter 2 reviews literature on pond water
chemistry, flood hazards, and IoT systems; Chapter 3 describes our
system architecture, hardware design, and ML methodology; Chapter 4
explains the implementation details; Chapter 5 presents sensor
calibrations, ML evaluation results, and defense insights; and Chapter 6
concludes the report with future recommendations.

1.6 Conclusion

This chapter outlined the importance of fish farming in Bangladesh, the
problems of water pollution and river floods, and our goals in building
AquaShield. The next chapter reviews background studies and related
works.

Chapter 2 Background Studies & Literature Review

2.1 Introduction

To build an effective pond monitoring and flood warning system, it is
important to understand the biological water limits for fish, the
patterns of monsoon river flooding in Bangladesh, and what existing IoT
and machine learning research has accomplished. This chapter reviews
these areas and highlights the technical gaps our project addresses.

2.2 Aquaculture Challenges and Water Quality Dynamics in Bangladesh

Fish are cold-blooded animals, meaning their health, growth, and
survival depend directly on water temperature and chemical parameters.
Four main water parameters must be kept within safe boundaries:

pH (Potential of Hydrogen): Safe range is 6.5 to 8.5. Low pH (\<6.0)
causes gill irritation and body slime. High pH (\>8.8) causes gill
damage and turns harmless ammonium into lethal unionized ammonia gas.

Total Dissolved Solids (TDS): Safe range is 150 to 450 ppm. High TDS
(\>600 ppm) indicates excess unconsumed feed, organic waste, or
fertilizer runoff, causing osmotic stress and clogging gills.

Water Temperature: Optimal range is 25.0°C to 30.0°C. Water holds less
dissolved oxygen when it gets hot (\>32°C), while fish consume more
oxygen due to higher metabolism. High heat also multiplies ammonia
toxicity.

Pond Water Level: Target depth is 80 to 150 cm. If water level is too
low, the pond heats up quickly; if it is too high during heavy rains,
pond dikes can break and fish escape.

Table 2.1: Water Quality Thresholds and Biological Tolerance for Major
Farmed Fish Species

  --------------------------------------------------------------------------
  Parameter      Optimal Range  Stress         Lethal Limit   Impact on Fish
                                Threshold      (Critical)     Health
                                (Warning)                     
  -------------- -------------- -------------- -------------- --------------
  pH             6.5 -- 8.5     \< 6.2 or \>   \< 5.0 or \>   Gill burns,
                                8.8            9.5            respiratory
                                                              failure,
                                                              ammonia
                                                              toxicity spike

  TDS (ppm)      150 -- 450     450 -- 600     \> 800         Osmotic
                                                              stress, gill
                                                              clogging,
                                                              excessive
                                                              organic waste

  Temperature    25.0 -- 30.0   30.0 -- 33.0   \> 35.0 or \<  Low oxygen,
  (°C)                          or \< 20.0     15.0           metabolic
                                                              collapse,
                                                              stopped
                                                              feeding

  Water Level    80 -- 150      \< 60 (Low) /  \< 40 (Dry) /  Fast
  (cm)                          \> 160 (High)  \> 180         temperature
                                               (Overflow)     changes, dike
                                                              overtopping,
                                                              fish escape
  --------------------------------------------------------------------------

2.3 Monsoon Flooding Risks and Early Warning Needs

Over 92% of the catchment area of Bangladesh's rivers lies outside the
country. During the monsoon (June to October), heavy rainfall in the
Himalayas and Meghalaya hills discharges down into the
Brahmaputra-Jamuna river system. At the Bahadurabad transit gauge in
Jamalpur, water levels frequently cross the official 19.05m Danger
Level. In major flood years like 2017, 2019, and 2020, water levels
passed 20.50m. In 2020 alone, over 40,000 hectares of commercial fish
ponds were submerged, causing financial losses of over 500 crore BDT
(\$45M USD). National agency bulletins give macro basin forecasts, but
fish farmers need a 3 to 7-day advance warning for their local river
station so they have enough time to set up high nylon nets around their
pond dikes or harvest mature fish early.

2.4 Review of Existing IoT Aquaculture Monitoring Systems

Early IoT systems used simple Arduino boards with ZigBee or Bluetooth,
but their range was too short and they did not control any pumps. Later
systems used ESP8266 or ESP32 boards streaming to platforms like
ThingSpeak or Blynk. However, these systems rely completely on
continuous internet: if Wi-Fi drops, all monitoring and automatic pump
actions stop. Commercial industrial PLC systems cost thousands of
dollars (\$2,000--\$10,000) and are completely out of reach for small
fish farmers in Bangladesh.

2.5 Machine Learning in Hydrological Forecasting & Water Quality
Prediction

In hydrology, data-driven machine learning models (Ridge, SVR, Random
Forest, XGBoost) offer a practical alternative to complex physics
simulations. However, many published studies make a major mistake: they
use standard random K-Fold cross-validation on time-series data.
Shuffling data points leaks future days into the training set, giving
falsely high accuracy scores. In addition, decision tree ensembles
(Random Forest and XGBoost) cannot predict values higher than the
maximum number in their training data, meaning they underestimate
unprecedented flood peaks. In pond water monitoring, supervised ML
models fail because farmers do not have labeled 'bad water' datasets. An
unsupervised model like Isolation Forest is needed to detect unusual
multi-sensor combinations without needing manual labels.

2.6 Comparative Analysis of Related Works and Technical Gaps

Table 2.2 compares AquaShield with eight previous systems from recent
research and industry:

Table 2.2: Comparative Feature Matrix of Existing Aquaculture Systems
vs. AquaShield

  ------------------------------------------------------------------------------------------------------------
  System /     Microcontroller   Key Sensors  Local Auto       Offline     River      Pond ML &     Cost (USD)
  Research                                    Actuation        Fail-Safe   Flood      Anomaly       
  Study                                                                    Forecast   Detection     
  ------------ ----------------- ------------ ---------------- ----------- ---------- ------------- ----------
  Saha et      Arduino Uno       pH, Temp, DO No (Alerts Only) No          No         No            \$120
  al. (2018)                                                                                        

  Raju et      Raspberry Pi      pH, Temp,    Yes (Pumps)      Partial     No         No            \$180
  al. (2020)                     Level                                                              

  Hasan et     ESP8266           pH, TDS,     No               No          No         Basic         \$75
  al. (2021)                     Temp                                                 Thresholds    

  Islam et     ESP32             pH, Temp,    Yes (Aerator)    No          No         Simple Linear \$95
  al. (2022)                     Turbidity                                            Reg           

  Chen et      Industrial PLC    Optical DO,  Yes              Yes         No         LSTM DO       \$1,500+
  al. (2023)                     pH, ORP      (Multi-Relay)                           Forecast      

  Ahmed et     ESP32             pH, TDS,     Yes              No          No         No            \$85
  al. (2024)                     Level        (Drain/Refill)                                        

  Commercial   Proprietary       Full Water   Full PLC Control Yes         No         Proprietary   \$3,500+
  AquaMaster                     Suite                                                Rules         

  AquaShield   ESP32 (Dual Core) pH, TDS,     Yes (Drain,      Yes (Full   Yes (BWDB  Yes (Model 2  \< \$60
  (Our Work)                     Temp,        Refill, Aerator, Edge FSM +  LOYO CV +1 TDS + Model 3 
                                 Ultrasonic   Feeder)          Flash       to +14d)   IsoForest)    
                                                               Buffer)                              
  ------------------------------------------------------------------------------------------------------------

Technical Gaps We Resolved: (1) Connected macro river flood forecasting
with micro pond automation; (2) Created local edge FSM rules so the
system continues running pumps and buffering data even during internet
dropouts; (3) Used Leave-One-Year-Out validation to avoid lookahead
leakage; and (4) Used Isolation Forest with rate-of-change deltas to
catch dangerous multi-sensor chemical combinations.

2.7 Conclusion

This chapter reviewed fish water tolerances, monsoon flood patterns,
existing IoT platforms, and ML models. The identified gaps provide the
justification for our methodology described in Chapter 3.

Chapter 3 System Methodology & Architecture

3.1 Introduction

This chapter describes how we designed AquaShield. It explains our
5-tier architecture, sensor models and equations, edge control rules,
cloud data pipeline, mathematical formulations for the three machine
learning models, and validation methods.

3.2 Overall System Architecture and Telemetry Pipeline

We organized AquaShield into five connected tiers: (1) Physical Sensors
and Actuators at the pond; (2) Edge Computing on the ESP32 running local
control rules; (3) Cloud Telemetry using an MQTT broker, Node.js
backend, and MongoDB database; (4) Machine Learning Analytics running
our three prediction models; and (5) Presentation Tier consisting of our
live web dashboard and Telegram alert bot.

Figure 3.1: High-level 5-tier cyber-physical architecture and catchment
integration schematic of AquaShield

Explanation: Shows how data flows from pond sensors and river stations,
through the ESP32 and MQTT broker, to our machine learning models, live
dashboard, and Telegram alerts.

3.3 Hardware Design and Edge Sensing Layer

We chose the ESP32 NodeMCU-32S board because it has a dual-core 240 MHz
processor, built-in 2.4 GHz Wi-Fi, and 4 MB flash memory. Core 0 handles
Wi-Fi and MQTT publishing, while Core 1 handles sensor readings and
relay control. Our sensors and formulas include:

pH Sensor (pH-4502C): Analog probe using two-point calibration: pH =
7.0 + (V_cal,7 - V_out) / S, where S is the sensor slope.

TDS Sensor: Measures electrical conductivity with AC excitation.
Compensated for temperature: V_comp = V_adc / \[1.0 + 0.02 \* (T -
25.0)\].

DS18B20 Temperature Sensor: Waterproof digital sensor communicating over
a 1-Wire bus (±0.5°C accuracy).

HC-SR04 Water Level Sensor: Ultrasonic sensor measuring distance:
Water_Level = Pond_Depth - (t_echo \* v_sound) / 2.

Table 3.1: Hardware Bill of Materials (BOM) and Cost Breakdown

  ------------------------------------------------------------------------------------------
  Component Name    Model /         Quantity    Unit Cost   Unit Cost   Primary Function
                    Specification               (BDT)       (USD)       
  ----------------- --------------- ----------- ----------- ----------- --------------------
  ESP32             NodeMCU-32S     1           650 BDT     \$5.50      Central processing &
  Microcontroller   (Wi-Fi/BLE)                                         Wi-Fi communication

  pH Sensor Kit     pH-4502C +      1           1,850 BDT   \$15.50     Measures pond water
                    Glass Probe                                         acidity/alkalinity

  TDS Sensor Kit    Analog AC Probe 1           750 BDT     \$6.30      Measures dissolved
                    Module                                              solids and water
                                                                        purity

  Temperature       Waterproof      1           180 BDT     \$1.50      Measures water temp
  Sensor            DS18B20                                             for compensation

  Ultrasonic Sensor HC-SR04         1           120 BDT     \$1.00      Tracks pond water
                    Transducer                                          depth without
                                                                        touching water

  4-Channel Relay   5V Optocoupler  1           280 BDT     \$2.35      Switches 12V pumps
                    Isolated                                            and aerator safely

  Drain Pump        12V DC          1           650 BDT     \$5.45      Drains excess water
                    Submersible                                         during heavy rain or
                    (240 L/h)                                           high TDS

  Refill Pump       12V DC          1           650 BDT     \$5.45      Adds fresh water
                    Submersible                                         when pond level gets
                    (240 L/h)                                           low

  Aerator Pump      12V DC          1           550 BDT     \$4.60      Supplies oxygen when
                    Diaphragm Air                                       water heats up
                    Pump                                                

  Servo Feeder      SG90 Micro      1           140 BDT     \$1.20      Dispenses fish feed
                    Servo (PWM)                                         pellets
                                                                        automatically

  Power Supply &    12V 5A          1           800 BDT     \$6.70      Powers 12V pumps and
  Buck              Adapter +                                           regulates 5V for
                    LM2596                                              ESP32

  Enclosure &       IP65 Waterproof 1           500 BDT     \$4.20      Protects electronics
  Wiring            Box & Cables                                        from rain and
                                                                        moisture

  Total Bill of     Complete        \-          7,120 BDT   \$59.75     Complete assembled
  Materials         Hardware Node                                       prototype system
  ------------------------------------------------------------------------------------------

Table 3.2: Summary of Primary Hardware Pin Assignments on ESP32

  -----------------------------------------------------------------------
  ESP32 GPIO Pin    Interfaced        Signal Category   Electrical
                    Component                           Characteristics /
                                                        Protocol
  ----------------- ----------------- ----------------- -----------------
  GPIO 34           pH Sensor         Analog Input      0.0V -- 3.3V DC
  (ADC1_CH6)        (pH-4502C Po)                       (ADC1 pin, safe
                                                        with Wi-Fi)

  GPIO 35           TDS Sensor        Analog Input      0.0V -- 2.3V DC
  (ADC1_CH7)        (Analog Out)                        (ADC1 pin, safe
                                                        with Wi-Fi)

  GPIO 4            DS18B20 Temp      Digital           1-Wire bus with
                    Sensor            Bi-directional    4.7 kΩ pull-up
                                                        resistor to 3.3V

  GPIO 5            Ultrasonic Trig   Digital Output    10 μs TTL trigger
                    Pin                                 pulse

  GPIO 18           Ultrasonic Echo   Digital Input     TTL pulse-width
                    Pin                                 return via
                                                        1kΩ/2kΩ divider

  GPIO 19           Relay IN1 (Drain  Digital Output    Active-LOW
                    Pump)                               optoisolated
                                                        relay driver

  GPIO 21           Relay IN2 (Refill Digital Output    Active-LOW
                    Pump)                               optoisolated
                                                        relay driver

  GPIO 22           Relay IN3         Digital Output    Active-LOW
                    (Aerator Pump)                      optoisolated
                                                        relay driver

  GPIO 23           Relay IN4 (Feeder PWM Output        50 Hz PWM servo
                    Servo)                              pulse (1.0 ms --
                                                        2.0 ms)

  5V & GND          Sensors, Relays & Power Rails       Regulated 5.0V DC
                    Servos                              from LM2596 buck
                                                        converter
  -----------------------------------------------------------------------

3.4 Local Edge Control Logic, Fail-Safe Automation, and Actuator Drivers

We programmed an autonomous Finite State Machine (FSM) directly inside
the ESP32. It checks conditions every 30 seconds and controls the pumps
locally, so protection never stops even if the internet goes down:

Table 3.3: Summary of Edge Finite State Machine (FSM) Actuation Rules

  --------------------------------------------------------------------------
  Rule ID        Monitored      Trigger        Automated      Safety Cut-off
                 Condition      Condition      Local Action   / Hysteresis
  -------------- -------------- -------------- -------------- --------------
  Rule 1         Pond Overflow  Water Level    Turn on Drain  Turn off when
                 Risk           \>= 85 cm      Pump (Relay 1  level drops
                                               ON)            below 75 cm

  Rule 2         Pond Water     Water Level    Turn on Refill Turn off when
                 Depletion      \<= 40 cm      Pump (Relay 2  level rises
                                               ON)            above 55 cm

  Rule 3         High Dissolved TDS \>= 600    Execute        Drain for 5
                 Waste          ppm            Partial Water  mins, then
                                               Exchange       refill for 5
                                                              mins

  Rule 4         High Water     Water Temp \>= Turn on        Runs until
                 Temperature    30.0°C         Aerator (Relay water cools
                                               3 ON)          below 28.5°C

  Rule 5         Scheduled      Time = 08:00   Rotate Feeder  Gated: Paused
                 Feeding        or 16:00       Servo (Relay   if Temp \<
                                               4)             18°C or Temp
                                                              \> 34°C

  Rule 6         Acidic /       pH \< 6.2 or   Send Emergency Sends
                 Alkaline Water pH \> 8.8      Alert via      immediate push
                                               Telegram       notification
                                                              to farmer
  --------------------------------------------------------------------------

Offline Fail-Safe: If Wi-Fi disconnects, the ESP32 buffers up to 2,000
readings in SPIFFS flash memory (\>16 hours of data). When Wi-Fi
reconnects, it automatically sends all buffered readings to the cloud
database with zero lost data.

3.5 Cloud Telemetry, REST API, and Database Schema

The ESP32 publishes sensor data every 30 seconds as JSON via MQTT to
topic aquashield/pond1/telemetry. Our Node.js Express server validates
the incoming data, saves it in a MongoDB Atlas time-series collection,
and forwards it to the web dashboard using Socket.io WebSockets, giving
real-time live updates without browser page refreshing.

3.6 Machine Learning Subsystem Methodology

We built three distinct machine learning models to solve specific
problems:

3.6.1 Model 1: River Water-Level Forecasting (Bahadurabad Station)

Predicts the river water level in meters at Bahadurabad transit station
on the Jamuna River across four lead horizons: +1 day, +3 days, +7 days,
and +14 days. Sourced from 15 years (2008--2022) of BWDB records and
ERA5 catchment rainfall. Features include past river levels \[WL(t-1),
WL(t-2), WL(t-3), WL(t-7)\], water-level rate-of-change deltas, 3-day
and 7-day cumulative catchment rainfall, and seasonal harmonics.

3.6.2 Model 2: Pond TDS Forecasting (+60 Minutes Ahead)

Predicts pond TDS 60 minutes ahead (t+1h) using IoT telemetry resampled
to 1-hour intervals. Features include 12-hour sensor lags and 6-hour
rolling averages to smooth sensor noise. We compared Linear Regression,
Random Forest, and XGBoost, and used SHAP to explain feature
contributions.

3.6.3 Model 3: Unsupervised Pond Water-Quality Anomaly Detection

Detects abnormal water conditions without needing labeled disease data.
We used Isolation Forest with a 5% contamination factor on sensor values
and hourly deltas \[pH, TDS, Temp, ΔpH, ΔTDS, ΔTemp\]. This catches
multivariate hazards (such as pH 8.2 combined with 32°C water
temperature producing lethal ammonia gas) that look normal on
single-parameter thresholds.

3.7 Model Validation Protocols (LOYO CV and Chronological Splitting)

To prevent future data leakage, Model 1 used Leave-One-Year-Out (LOYO)
cross-validation across 12 annual folds (2008--2019), keeping 2020--2022
as an untouched test set. Model 2 used a chronological 70% train, 15%
validation, and 15% test split.

Figure 3.2: Leave-One-Year-Out (LOYO) cross-validation and strict
holdout evaluation protocol

Explanation: Shows how data was split by full calendar years: 12 folds
(2008--2019) for model tuning, followed by testing on the untouched
2020--2022 test years.

We evaluated our models using standard error metrics:

  RMSE = `\sqrt{(1 / N) * \sum (y_i - \hat{y}_i)^2}`{=tex}   (3.1)
  ---------------------------------------------------------- -------

  -----------------------------------------------------------------------
  NSE = 1.0 - \[`\sum `{=tex}(y_i -   (3.2)
  `\hat{y}`{=tex}*i)\^2 /             
  `\sum `{=tex}(y_i -                 
  `\bar`{=tex}{y}*{obs})\^2\]         
  ----------------------------------- -----------------------------------

  -----------------------------------------------------------------------

  POD = Hits / (Hits + Misses)   (3.3)
  ------------------------------ -------

  FAR = False_Alarms / (Hits + False_Alarms)   (3.4)
  -------------------------------------------- -------

3.8 Conclusion

This chapter explained our hardware circuitry, control logic, cloud
pipeline, and ML formulas. Chapter 4 describes how we implemented these
designs in practice.

Chapter 4 Implementation

4.1 Introduction

This chapter describes how we physically built and programmed
AquaShield. We divided our 3-member team into clear responsibilities:
Srabon handled circuit fabrication, sensor connections, and power
management; Mahfuz built the cloud MQTT server, database, and web
dashboard; and Hrithik trained and evaluated the three machine learning
models.

4.2 Hardware Fabrication, Circuit Wiring, and Power Supply Setup

We assembled the prototype inside an IP65 waterproof outdoor box. When
testing 12V submersible pumps, we initially noticed that turning on a
pump caused an electrical voltage drop that restarted the ESP32. To fix
this, we designed a dual-rail power circuit: a 12V 5A DC adapter powers
the pumps and aerator directly, while an LM2596 step-down buck converter
steps the voltage down to a stable 5.0V DC for the ESP32 and sensor
modules, filtered with a 470 μF capacitor. We also connected 1N4007
diodes across the pump motor terminals to safely absorb inductive
voltage spikes when pumps turn off.

Sensors were connected to ADC1 pins on the ESP32 (pH to GPIO 34 and TDS
to GPIO 35), because ADC2 cannot be used when Wi-Fi is active. The
DS18B20 temperature probe was wired to GPIO 4 with a 4.7 kΩ pull-up
resistor. The HC-SR04 ultrasonic sensor echo line was stepped down from
5V to 3.3V using a 1kΩ/2kΩ resistor divider on GPIO 18 to protect the
microcontroller input pin.

4.3 ESP32 Firmware Development & Local Sensing Pipeline

We wrote our firmware in C++ using the Arduino core. We avoided delay()
functions and used millis() timers so all tasks run smoothly. To reduce
electrical noise on analog readings, the firmware takes 64 fast samples,
sorts them, discards the highest and lowest 10%, and averages the rest.
The two-point pH calibration numbers are saved in the ESP32 flash memory
(NVS) so they stay saved even when powered off. The firmware evaluates
our local control rules every 30 seconds and buffers data to SPIFFS
flash memory during internet disconnects.

4.4 Cloud Backend & Database Service Implementation

Our cloud backend runs on an Ubuntu Linux virtual server. An Eclipse
Mosquitto MQTT broker receives sensor data securely over port 8883
(TLS). A Node.js Express service validates the incoming JSON packets and
saves them into MongoDB Atlas time-series collections. When a new
reading arrives, it is immediately pushed to connected browsers using
Socket.io WebSockets, updating the live dials in real time.

4.5 Machine Learning Subsystem Implementation & Deployment Pipeline

We built our machine learning pipelines in Python using Scikit-learn,
XGBoost, and SHAP. For Model 1 (River Flood Forecast), we cleaned 15
years of BWDB water levels, filled missing maintenance days using PCHIP
interpolation, and created lag and rainfall features. We tested Ridge,
Lasso, Random Forest, and XGBoost using Leave-One-Year-Out validation.
For Model 2 (TDS Forecast), we calculated 6-hour rolling statistics and
trained regressions with SHAP explainability. For Model 3 (Anomaly
Detection), we trained Isolation Forest on sensor deltas. The models
were saved with Joblib and served through a lightweight FastAPI
microservice.

4.6 Web Dashboard & Sensor Calibration Interface Development

We built a responsive web dashboard using HTML5, Tailwind CSS, and
Chart.js. Key features include: (1) Live dials for pH, TDS, temperature,
and depth; (2) A composite Pond Health Index (0--100) calculated from
all four parameters; (3) Interactive 24-hour and 7-day trend charts; (4)
Manual override buttons to test pumps and the aerator; and (5) A guided
pH calibration page that walks the user through testing standard buffer
liquids and saves new calibration values directly into the ESP32 memory.

4.7 Automated Alerting Subsystem & Telegram Bot Integration

To alert farmers anywhere on their phones, we connected our server to
the Telegram Bot API. We added a debounce filter: a parameter must stay
abnormal for three consecutive readings (90 seconds) before triggering
an alert, followed by a 30-minute cooldown to avoid message spamming.
Alerts tell the farmer what went wrong, what automatic action the system
took, and what they should check. When water returns to normal, a green
resolution message is sent.

4.8 Conclusion

This chapter described our circuit wiring, power design, firmware
structure, cloud database, ML microservice, and user dashboard. Chapter
5 evaluates the real-world performance of these components.

Chapter 5 Result Analysis and Discussion

5.1 Introduction

This chapter presents our experimental findings: laboratory sensor
calibration, Model 1 river flood forecasting results across multiple
horizons, Model 2 pond TDS forecasts with SHAP plots, Model 3 anomaly
detection, and system speed and reliability tests.

5.2 IoT Hardware Performance and Sensor Calibration Results

We tested all sensors against certified laboratory references. After
two-point calibration and 64-sample filtering, our pH probe achieved an
error of ±0.05 pH (R² = 0.994). The TDS sensor stayed within 2.8% error
across saline test solutions, the DS18B20 temperature probe deviated by
only ±0.15°C, and the ultrasonic sensor achieved ±0.4 cm depth precision
(Table 5.1):

Table 5.1: Sensor Calibration and Precision Evaluation Across Standard
Laboratory Buffers

  -------------------------------------------------------------------------------------------------
  Sensor Parameter       Ground Truth  Pre-Calibration   Post-Calibration   R² Score    Drift (72h
                         Reference     Error             Error (AquaShield)             Test)
  ---------------------- ------------- ----------------- ------------------ ----------- -----------
  pH                     Standard      ± 0.42 pH         ± 0.05 pH          0.994       ± 0.03 pH
  (Acidity/Alkalinity)   Buffers                                                        
                         (4.01, 6.86,                                                   
                         9.18)                                                          

  TDS (ppm)              Calibrated    ± 8.5%            ± 2.8%             0.989       ± 4.2 ppm
                         NaCl                                                           
                         Reference                                                      
                         (100--1000                                                     
                         ppm)                                                           

  Water Temperature (°C) Certified     ± 0.85°C          ± 0.15°C           0.998       ± 0.08°C
                         Mercury                                                        
                         Thermometer                                                    

  Water Level (cm)       Physical      ± 2.4 cm          ± 0.4 cm           0.996       ± 0.2 cm
                         Metric Gauge                                                   
                         Rule                                                           
  -------------------------------------------------------------------------------------------------

5.3 Model 1 (River Flood Forecast) Experimental Evaluation

We trained Model 1 on 15 years (2008--2022, 5,479 days) of daily water
level data at the Bahadurabad transit station on the Jamuna River. The
danger level is 19.05m, with 467 recorded flood days (Table 5.2):

Table 5.2: Bahadurabad Station Hydrological Dataset Summary (2008--2022)

  -----------------------------------------------------------------------
  Hydrological Parameter  Empirical Dataset Value Operational
  / Attribute                                     Significance for
                                                  Aquaculture
  ----------------------- ----------------------- -----------------------
  Study Period            2008-01-01 to           15 continuous calendar
                          2022-12-31              years of daily records

  Total Calendar Days     5,479 days              Statistically
                                                  exhaustive sample of
                                                  seasonal cycles

  Missing Daily           335 days (6.11%)        Cleanly imputed using
  Observations                                    PCHIP interpolation

  Observed Gauge Range    11.68 m to 21.16 m      Wide dynamic range of
                                                  hydraulic head

  Official Danger Level   19.05 m                 Water overtopping
                                                  primary earthen
                                                  embankments

  Extreme Danger Level    19.90 m                 Severe regional
                                                  flooding across all
                                                  surrounding ponds

  Recorded Highest Water  20.63 m                 Historical peak flood
  Level (RHWL)                                    inundation benchmark

  Total Flood Days (\>=   467 days                Extensive sample of
  19.05 m)                                        high-water flood risk
                                                  events
  -----------------------------------------------------------------------

Figure 5.1: Correlation and physical lag dynamics between catchment
rainfall and Bahadurabad river water level

Explanation: Proves the physical hydrologic lag: rainfall upstream in
the Brahmaputra basin peaks several days before river water rises at
Bahadurabad, justifying our 3-day and 7-day cumulative rainfall
features.

Table 5.3: Hyperparameter Search Grids and Selected Optimal Values for
Model 1

  -----------------------------------------------------------------------
  Algorithm Family  Hyperparameter    Selected Optimal  Algorithmic Notes
                    Search Space      Configuration     
  ----------------- ----------------- ----------------- -----------------
  Persistence       None (Heuristic)  ΔWL = 0           Assumes WL(t+h) =
  Baseline                                              WL(t)

  Persistence +     None (Heuristic)  Adds past 1-day   Accounts for
  Trend                               rate of change    immediate
                                                        momentum

  Ridge Regression  alpha ∈ \[0.01,   alpha = 1.0       L2 penalty,
                    0.1, 1.0, 10.0,                     StandardScaler
                    100.0\]                             applied

  Lasso Regression  alpha ∈ \[0.001,  alpha = 0.01      L1 sparse feature
                    0.01, 0.1, 1.0\]                    selection

  Random Forest     n_estimators ∈    n_estimators =    Tree ensemble,
  Regressor         \[50, 100, 200\]; 100, max_depth =  random_state = 42
                    max_depth ∈ \[5,  10                
                    10, 15\]                            

  XGBoost Regressor n_est ∈ \[50,     n_est = 100,      Gradient boosted
                    100, 200\]; depth depth = 5, lr =   trees, seed = 42
                    ∈ \[3, 5, 7\]; lr 0.05              
                    ∈ \[0.01, 0.05,                     
                    0.1\]                               

  Support Vector    C ∈ \[0.1, 1.0,   C = 1.0, epsilon  RBF kernel,
  Regressor         10.0\]; epsilon ∈ = 0.1             StandardScaler
                    \[0.01, 0.1\]                       applied
  -----------------------------------------------------------------------

Figure 5.2: Model Root Mean Squared Error (RMSE) vs. forecast lead time
(1 to 14 days) across all evaluated algorithms

Explanation: Shows how prediction error increases as we forecast further
into the future. Linear models maintain lower error curves than tree
models across short and medium lead times.

Table 5.4: Comprehensive LOYO Cross-Validation Performance Metrics (+1
Day Horizon)

  ----------------------------------------------------------------------------------------
  Model Name      Horizon   RMSE (m) MAE (m)  Bias (m)  Nash-Sutcliffe   POD (Hit False
                                                        (NSE)            Rate)    Alarm
                                                                                  Rate
                                                                                  (FAR)
  --------------- --------- -------- -------- --------- ---------------- -------- --------
  Persistence     +1 Day    0.1265   0.0797   -0.0009   0.9972           0.9280   0.0670
  Baseline                                                                        

  Persistence +   +1 Day    0.0953   0.0546   +0.0001   0.9984           0.9413   0.0381
  Trend                                                                           

  Linear          +1 Day    0.0843   0.0498   -0.0002   0.9988           0.9387   0.0276
  Regression                                                                      

  Ridge           +1 Day    0.0843   0.0497   -0.0002   0.9988           0.9307   0.0279
  Regression                                                                      

  Lasso           +1 Day    0.0889   0.0518   +0.0000   0.9986           0.9360   0.0277
  Regression                                                                      

  Random Forest   +1 Day    0.0848   0.0491   +0.0011   0.9988           0.9387   0.0330

  XGBoost         +1 Day    0.0847   0.0491   +0.0004   0.9988           0.9360   0.0331
  Regressor                                                                       

  Support Vector  +1 Day    0.0848   0.0546   +0.0113   0.9988           0.9440   0.0301
  Regressor                                                                       
  ----------------------------------------------------------------------------------------

Figure 5.3: Flood season hydrographs: observed vs. predicted water
levels during major historical monsoon flood years

Explanation: Traces our predicted water levels (orange) against actual
readings (blue). The model closely tracks flood peaks crossing the
19.05m Danger Level line.

5.3.1 Key Defense Finding: Why Linear Regression Beat Tree Ensembles on
Peak Floods

When looking at extreme floods above 19.9m (Table 5.5), Linear
Regression achieved an RMSE of 0.1120m, outperforming Random Forest
(0.1176m) and XGBoost (0.1156m):

Table 5.5: Extreme Flood Season and Peak Error Evaluation Metrics

  ----------------------------------------------------------------------------------
  Model           Flood      Peak Error RMSE       RMSE       RMSE        RMSE
                  Season     MAE (m)    (\<17m     (17-19m    (19-19.9m   (\>19.9m
                  RMSE (m)              Low)       Med)       Danger)     Extreme)
  --------------- ---------- ---------- ---------- ---------- ----------- ----------
  Persistence     0.1614     0.0512     0.0973     0.1693     0.1641      0.2301
  Baseline                                                                

  Persistence +   0.1179     0.1234     0.0746     0.1290     0.1212      0.1363
  Trend                                                                   

  Linear          0.1060     0.0621     0.0662     0.1156     0.1043      0.1120
  Regression                                                              

  Ridge           0.1061     0.0623     0.0659     0.1156     0.1047      0.1119
  Regression                                                              

  Random Forest   0.1105     0.0678     0.0646     0.1177     0.1094      0.1176

  XGBoost         0.1093     0.0677     0.0647     0.1169     0.1103      0.1156
  Regressor                                                               
  ----------------------------------------------------------------------------------

Why did this happen? Decision trees split data into boxes and predict
the average of training points in that box. By design, a tree cannot
predict any number higher than the highest value it saw during training.
During a record-breaking flood, tree models hit a ceiling and
underestimate the peak. Linear models, on the other hand, fit a
continuous line (y = wx + b). When rainfall and water momentum surge
together, the linear model extrapolates upward naturally, tracking
unprecedented peaks accurately.

Figure 5.4: Model 1 feature importance distribution shifting from
autoregressive water-level lags to upstream rainfall sums

Explanation: For a 1-day forecast, yesterday's water level is most
important. For 7-day and 14-day forecasts, the model shifts its reliance
to 3-day and 7-day accumulated catchment rainfall.

5.3.2 Holdout Test on Unseen 2020--2022 Monsoons

Tested on the untouched 2020--2022 monsoon seasons (+3 days lead
horizon), Linear Regression achieved an NSE of 0.9851 and RMSE of
0.3082m, beating the baseline by +21.19% (Table 5.6 and Figure 5.5):

Table 5.6: Final Holdout Evaluation Results on Unseen 2020--2022 Monsoon
Seasons (+3 Days)

  -------------------------------------------------------------------------------------
  Evaluated      Forecast   Holdout Test RMSE (m)   MAE (m)    NSE Score  Skill Score
  Model          Horizon    Period                                        vs Baseline
  -------------- ---------- ------------ ---------- ---------- ---------- -------------
  Persistence    +3 Days    2020--2022   0.3911     0.2642     0.9754     0.00%
  Baseline                  Monsoons                                      (Reference)

  Linear         +3 Days    2020--2022   0.3082     0.2035     0.9851     +21.19%
  Regression                Monsoons                                      Improvement
  (AquaShield)                                                            
  -------------------------------------------------------------------------------------

Figure 5.5: Final holdout model performance on unseen 2020--2022 monsoon
seasons (+3 days lead horizon)

Explanation: Demonstrates accurate tracking across the extreme 2020
flood season, achieving an outstanding NSE of 0.9851.

5.4 Model 2 (Pond TDS Forecast) Results and SHAP Explainability

Model 2 predicts pond TDS 60 minutes ahead (t+1h). Table 5.7 compares
algorithms on the 15% test set:

Table 5.7: Model 2 Pond TDS Forecasting Performance Comparison (+60 Mins
Horizon)

  ----------------------------------------------------------------------------
  Algorithm      MAE (ppm)      RMSE (ppm)     R² Score       Key Practical
  Evaluated                                                   Finding
  -------------- -------------- -------------- -------------- ----------------
  Persistence    3.54           11.46          0.942          Beats tree
  Baseline                                                    models; captures
                                                              slow physical
                                                              drift

  Linear         7.05           15.90          0.888          Smooth
  Regression                                                  regularized
                                                              linear
                                                              prediction
                                                              without
                                                              overfitting

  Random Forest  17.25          24.14          0.742          Overfit training
  Regressor                                                   sensor noise;
                                                              stepped
                                                              predictions

  XGBoost        18.46          25.56          0.711          Overfit
  Regressor                                                   high-frequency
                                                              ADC electrical
                                                              noise
  ----------------------------------------------------------------------------

Figure 5.6: Model 2 performance comparison bar chart across MAE, RMSE,
and R² metrics

Explanation: Clearly illustrates that the Persistence baseline (MAE:
3.54 ppm) and Linear Regression (MAE: 7.05 ppm) beat tree models.

Why Persistence Beat XGBoost: In a large pond, water chemistry changes
very slowly. Over 60 minutes, TDS drifts by only a few ppm. The
Persistence baseline naturally captures this slow movement (R² = 0.942).
Complex boosting models like XGBoost mistook small electrical ripples on
sensor wires for real environmental trends, overfitting the noise and
performing poorly on unseen test data (R² = 0.711). Linear Regression
gave a reliable learned model (R² = 0.888) that smoothed through sensor
noise.

Figure 5.7: Model 2 actual vs. predicted TDS time series over the
held-out test dataset

Explanation: Shows our predicted TDS trajectory (orange) closely
tracking actual sensor readings (blue).

Figure 5.8: SHAP feature importance summary plot explaining Model 2 TDS
forecasts

Explanation: Proves that the 6-hour rolling average of TDS and the
previous reading (TDS_t-1) drive over 85% of predictions, confirming the
model follows real physical kinetics.

5.5 Model 3 (Pond Anomaly Detection) Evaluation and Diagnostic Analysis

A standard Z-score threshold flagged 55 outlier points, while Isolation
Forest (5% contamination) detected 67 anomalies, successfully isolating
dangerous multi-sensor combinations (such as pH 8.2 at 32°C creating
toxic ammonia) that pass single-sensor threshold checks:

Figure 5.9: Model 3 bivariate scatter plot (pH vs. TDS) highlighting
detected multivariate anomalies

Explanation: Normal pond conditions cluster densely (teal), while
hazardous multi-parameter outliers (red) are isolated by the algorithm.

Figure 5.10: Model 3 anomaly detection timeline traced along continuous
TDS sensor readings

Explanation: Red markers flag sudden shock deltas (rapid fertilizer
runoff or rain dilution) detected along the TDS time series.

Figure 5.11: Isolation Forest anomaly score distribution and 5%
contamination decision threshold

Explanation: Histogram of computed anomaly scores; the vertical dashed
red line marks the 5% decision threshold separating normal from
anomalous states.

5.6 Real-Time Actuation Latency, Cloud Throughput, and End-to-End
Reliability

We tested system responsiveness and fail-safe robustness across 1,000
test cycles (Table 5.8):

Table 5.8: End-to-End Latency and Network Dropout Benchmark Results

  -----------------------------------------------------------------------
  Subsystem         Measured Average  Maximum Observed  Operational
  Operation /       Latency           Latency           Reliability
  Benchmark                                             Standard
  ----------------- ----------------- ----------------- -----------------
  Edge Sensor       42 ms             68 ms             Deterministic
  Sampling & ADC                                        30-second cycle
  Multi-Sampling                                        

  Local Fail-Safe   65 ms             85 ms             Instantaneous
  Relay Actuation                                       emergency
  (Edge FSM)                                            protection

  MQTT Telemetry    185 ms            420 ms            Sub-second over
  Ingestion (ESP32                                      standard 2.4 GHz
  to Cloud)                                             Wi-Fi

  WebSocket         24 ms             55 ms             Zero perceptible
  Dashboard                                             user interface
  Broadcast                                             lag
  (Socket.io)                                           

  Telegram          1.82 s            3.40 s            Direct mobile
  Emergency Bot                                         push delivered in
  Push Notification                                     \< 4 seconds

  Machine Learning  18 ms             32 ms             Microsecond REST
  Inference API                                         model execution
  Latency                                               

  Offline Buffer    100% sync         100% sync         60 buffered
  Recovery (30-min                                      packets restored
  simulated outage)                                     with zero loss
  -----------------------------------------------------------------------

5.7 Comprehensive Discussion & Technical Defense Insights

Four Key Takeaways from Our Work: (1) Leave-One-Year-Out validation is
essential for river data to avoid future data leakage; (2) Linear
regression models extrapolate flood crests better than decision trees;
(3) Isolation Forest detects combined hazards without needing
pre-labeled failure datasets; and (4) SHAP provides transparency so
farmers can trust automated alerts.

5.8 Conclusion

Our experiments verified all subsystems: calibrated sensors gave high
accuracy; Model 1 forecasted floods with NSE = 0.985; Model 2 predicted
TDS accurately with SHAP explainability; Model 3 caught multi-parameter
hazards; and the edge node survived network dropouts with 100% data
recovery.

Chapter 6 Conclusion & Future Work

6.1 Conclusion

AquaShield successfully connects low-cost IoT automation with three
practical machine learning models. It solves the real-world problems of
silent pond water toxicity and monsoon flood devastation in Bangladesh,
delivering an end-to-end solution built for under 7,200 BDT (\~\$60
USD).

6.2 Key Research and Engineering Contributions

1.  Affordable Edge Node: Built a low-cost (\<\$60) multi-sensor edge
    node with optical relay isolation and ADC noise filtering.

2.  Offline Edge Fail-Safe: Programmed local FSM rules ensuring
    continuous pump control and flash buffering during internet outages.

3.  Dual-Horizon Protection: Connected river flood forecasting with pond
    automation, giving farmers 3 to 7 days advance warning.

4.  Leakage-Free Flood Validation: Evaluated models using LOYO CV,
    proving linear extrapolation beats decision trees during peak
    floods.

5.  Unsupervised Anomaly Detection: Detected multi-parameter toxic
    conditions (ammonia spikes) without requiring labeled failure
    datasets.

6.3 Project Limitations

1.  Sensor Bio-Fouling: Glass-bulb pH probes require periodic cleaning
    every 2 to 4 weeks to remove biofilm.

2.  Wi-Fi Coverage: The prototype uses 2.4 GHz Wi-Fi, meaning remote
    ponds without Wi-Fi require GSM modems.

3.  Single-Station Scope: Model 1 was calibrated specifically for the
    Bahadurabad transit station on the Jamuna River.

6.4 Future Recommendations

1.  LoRaWAN Long-Range Mesh: Use LoRaWAN transceivers to connect
    multiple ponds across a 10 km radius to a single gateway.

2.  On-Device TinyML Inference: Convert models with TinyML to run
    predictions directly on the ESP32 microcontroller.

3.  Solar Off-Grid Power: Add a 50W solar panel and 12V battery for 100%
    off-grid operation in rural areas.

Appendix A Circuit Schematic, Pin Mappings, and REST API Endpoints

A.1 Complete Hardware Pinout Specifications

Table A.1: Complete Hardware Pinout and Bus Interfacing Specifications

  -----------------------------------------------------------------------------
  ESP32 Pin      Component Name Signal         Operating       Bus Protocol /
                                Category       Voltage         Interface
                                                               Circuit
  -------------- -------------- -------------- --------------- ----------------
  GPIO 34        pH Sensor      Analog Input   0.0V -- 3.3V DC ADC1 Channel 6
                 (pH-4502C)                                    (Wi-Fi safe,
                                                               multi-sampled)

  GPIO 35        TDS Sensor     Analog Input   0.0V -- 2.3V DC ADC1 Channel 7
                 (Analog Out)                                  (Wi-Fi safe,
                                                               multi-sampled)

  GPIO 4         DS18B20 Temp   Digital I/O    3.3V DC         1-Wire bus with
                 Probe                                         4.7 kΩ pull-up
                                                               resistor to 3.3V

  GPIO 5         Ultrasonic     Digital Output 3.3V / 5.0V TTL 10 μs trigger
                 Trig Pin                                      pulse output

  GPIO 18        Ultrasonic     Digital Input  3.3V Logic      Pulse-width
                 Echo Pin                      Level           return via
                                                               1kΩ/2kΩ voltage
                                                               divider

  GPIO 19        Relay 1 (Drain Digital Output 5.0V            Active-LOW
                 Pump)                         Opto-isolated   optocoupler
                                                               trigger driver

  GPIO 21        Relay 2        Digital Output 5.0V            Active-LOW
                 (Refill Pump)                 Opto-isolated   optocoupler
                                                               trigger driver

  GPIO 22        Relay 3        Digital Output 5.0V            Active-LOW
                 (Aerator)                     Opto-isolated   optocoupler
                                                               trigger driver

  GPIO 23        Servo Motor    PWM Output     5.0V DC         50 Hz hardware
                 (Feeder)                      (External)      PWM (1.0 ms --
                                                               2.0 ms duty
                                                               cycle)

  VIN / 5V       LM2596 Output  Regulated      5.0V DC (±2%)   Filtered with
                 Rail           Power                          470 μF + 0.1 μF
                                                               capacitors

  GND            Common Ground  Ground Rail    0.0V Reference  Common ground
                                                               plane for MCU,
                                                               sensors, and
                                                               power
  -----------------------------------------------------------------------------

A.2 AquaShield REST API Endpoints Specification

Table A.2: AquaShield REST API Endpoints Specification

  ------------------------------------------------------------------------------
  HTTP Method       API Route Endpoint       Payload /         Description &
                                             Parameters        Response Output
  ----------------- ------------------------ ----------------- -----------------
  GET               /api/telemetry/live      device_id (query) Returns latest
                                                               30-sec sensor
                                                               packet with relay
                                                               states

  GET               /api/telemetry/history   device_id, range  Returns array of
                                             (24h/7d)          aggregated
                                                               historical
                                                               records for
                                                               charts

  POST              /api/actuate             {"relay":         Overrides
                                             "aerator",        automated rules
                                             "state": 1}       and sets relay
                                                               state manually

  POST              /api/calibrate/ph        {"v_ph4": 3.02,   Recalculates
                                             "v_ph7": 2.51}    slope and updates
                                                               calibration in
                                                               ESP32 NVS

  GET               /api/ml/forecast/flood   horizon=3         Returns predicted
                                                               Bahadurabad river
                                                               water level and
                                                               alert tier

  GET               /api/ml/forecast/tds     device_id         Returns predicted
                                                               +60m TDS value
                                                               with SHAP feature
                                                               rankings

  GET               /api/ml/anomaly/status   device_id         Returns current
                                                               Isolation Forest
                                                               score and
                                                               multivariate flag
  ------------------------------------------------------------------------------

Appendix B Technical Defense Preparation & Oral Defense Q&A Master Sheet

Defense Topic 1: Time-Series Leakage & Why LOYO is Essential Question:
'Why could you not just use 5-fold or 10-fold cross-validation from
scikit-learn?' Response: Standard K-Fold CV randomly shuffles rows. In
river time-series data with strong seasonal cycles and lag dependencies,
random splitting creates massive data leakage: if day t is in the test
set, day t-1 and day t+1 might be in training. The model would simply
interpolate between known adjacent days instead of forecasting into the
future. Leave-One-Year-Out (LOYO) cross-validation evaluates the model
on a completely unseen, unbroken hydrological year (like the entire 2017
monsoon), which replicates true operational forecasting.

Defense Topic 2: Why Linear Models Extrapolate Better Than Decision
Trees Question: 'Why did Linear Regression beat XGBoost and Random
Forest during peak floods?' Response: Decision trees divide feature
space into boxes and assign the average training value to each leaf. A
tree cannot predict a number higher than the maximum target value in its
training data. If the highest river level in training was 20.0 meters,
and an unprecedented flood reaches 20.6 meters, a Random Forest will
output 20.0 meters---severely underestimating the flood peak. In
contrast, regularized linear regression fits a continuous line (y = wx +
b). When rainfall and water momentum surge simultaneously, the linear
model extrapolates upward naturally.

Defense Topic 3: The Mechanics of Isolation Forest Question: 'Explain
step-by-step how Isolation Forest separates anomalies.' Response:
Isolation Forest builds an ensemble of random decision trees. At each
step, a feature is picked at random, and a random split point is chosen.
Anomalies have rare or extreme values, meaning they get separated into
leaf nodes with very few cuts (short path length). Normal data points
reside in dense clusters and require many cuts to isolate. Points with
short average path lengths across trees are flagged as anomalies.

Defense Topic 4: The Role of SHAP Question: 'What is SHAP and why did
you use it?' Response: SHAP (SHapley Additive exPlanations) is based on
cooperative game theory. It calculates the fair contribution of each
feature to the final prediction. In Model 2, SHAP proved that the 6-hour
rolling average of TDS and the previous reading (TDS_t-1) drive over 85%
of the prediction, proving that our model follows real physical kinetics
rather than fitting random noise.

Defense Topic 5: Hardware Brownout Prevention and Noise Immunity
Question: 'How did you prevent the ESP32 from restarting when large
pumps turn on?' Response: We resolved this in three ways: (1) Dual-rail
power supply: 12V powers the pump motors directly, while a separate
LM2596 buck converter steps down to 5V for the MCU; (2) Optical
isolation: PC817 optocouplers separate the ESP32 GPIO signals from the
relay coils; and (3) Snubber diodes: 1N4007 diodes across the DC pump
terminals dissipate inductive energy spikes when the pumps switch off.

References

\[1\] Department of Fisheries (DoF), 'Yearbook of Fisheries Statistics
of Bangladesh 2022-23,' Ministry of Fisheries and Livestock, Dhaka,
2023.

\[2\] Food and Agriculture Organization (FAO), 'The State of World
Fisheries and Aquaculture 2024,' FAO, Rome, Italy, 2024.

\[3\] Flood Forecasting and Warning Centre (FFWC), 'Annual Flood Report
2020,' BWDB, Dhaka, Bangladesh, 2021.

\[4\] M. M. Rahman, M. A. Hossain, and S. Islam, 'Impact of climate
change and extreme monsoon flooding on inland aquaculture in northern
Bangladesh,' Journal of Water and Climate Change, vol. 12, no. 4,
pp. 1420--1435, 2021.

\[5\] C. E. Boyd, Water Quality: An Introduction, 3rd ed., Cham,
Switzerland: Springer Nature, 2020.

\[6\] J. E. Colt, Dissolved Gas Concentration in Water, 2nd ed., London:
Academic Press, 2012.

\[7\] P. Saha, D. Biswas, and A. K. Das, 'IoT-based automated water
quality monitoring and alert system for fish farming,' in Proc. IEEE
ICSCEE, Shah Alam, Malaysia, 2018, pp. 1--6.

\[8\] K. R. Raju, G. H. Kumar, and M. V. Reddy, 'Automated water quality
monitoring and control system for aquaculture using Raspberry Pi,' IEEE
IoT Journal, vol. 7, no. 9, pp. 8412--8421, 2020.

\[9\] M. R. Hasan, M. S. Alam, and T. Sultana, 'Design and deployment of
a low-cost IoT telemetry node for rural fish ponds in Bangladesh,' in
Proc. IEEE ICEEICT, Dhaka, 2021, pp. 215--220.

\[10\] M. N. Islam, S. K. Roy, and R. Ahmed, 'Predictive water aeration
and quality management using ESP32 edge microcontroller,' IEEE Access,
vol. 10, pp. 54312--54324, 2022.

\[11\] X. Chen, Y. Zhang, and L. Wang, 'Industrial PLC-driven
multi-parameter recirculating aquaculture control system with deep LSTM
DO prediction,' Computers and Electronics in Agriculture, vol. 205, art.
no. 107621, 2023.

\[12\] S. Ahmed, F. Farzana, and K. M. Kabir, 'Automated fish feeding
and pond level management system using IoT relays and ultrasonic
sensing,' in Proc. IEEE CONECCT, Bangalore, 2024, pp. 1--6.

\[13\] F. T. Liu, K. M. Ting, and Z.-H. Zhou, 'Isolation Forest,' in
Proc. 8th IEEE ICDM, Pisa, Italy, 2008, pp. 413--422.

\[14\] S. M. Lundberg and S.-I. Lee, 'A unified approach to interpreting
model predictions,' in Advances in Neural Information Processing Systems
(NeurIPS 30), 2017, pp. 4765--4774.

\[15\] T. Chen and C. Guestrin, 'XGBoost: A scalable tree boosting
system,' in Proc. 22nd ACM SIGKDD, 2016, pp. 785--794.

\[16\] L. Breiman, 'Random Forests,' Machine Learning, vol. 45, no. 1,
pp. 5--32, 2001.

\[17\] A. E. Hoerl and R. W. Kennard, 'Ridge regression: Biased
estimation for nonorthogonal problems,' Technometrics, vol. 12, no. 1,
pp. 55--67, 1970.

\[18\] R. Tibshirani, 'Regression shrinkage and selection via the
Lasso,' Journal of the Royal Statistical Society: Series B, vol. 58, no.
1, pp. 267--288, 1996.

\[19\] J. E. Nash and J. V. Sutcliffe, 'River flow forecasting through
conceptual models part I,' Journal of Hydrology, vol. 10, no. 3,
pp. 282--290, 1970.

\[20\] H. Hersbach et al., 'The ERA5 global reanalysis,' Quarterly
Journal of the Royal Meteorological Society, vol. 146, no. 730,
pp. 1999--2049, 2020.

\[21\] Bangladesh Water Development Board (BWDB), 'Hydrometric Data
Portal: Daily Water Levels and Discharges (Station SW46.9L),' BWDB
Hydrology Division, Dhaka, 2024.

\[22\] Espressif Systems, 'ESP32 Series Datasheet: 2.4 GHz Wi-Fi and
Bluetooth Combo Chip,' Espressif Systems, Shanghai, China, 2023.

\[23\] Maxim Integrated, 'DS18B20 Programmable Resolution 1-Wire Digital
Thermometer Datasheet,' Maxim Integrated Products, Inc., San Jose, CA,
2019.

\[24\] OASIS Standard, 'MQTT Version 5.0,' OASIS Open, Standard
Specification, 2019.

\[25\] MongoDB Inc., 'MongoDB Time Series Collections Documentation,'
MongoDB Inc., New York, NY, 2024.

\[26\] F. Pedregosa et al., 'Scikit-learn: Machine learning in Python,'
Journal of Machine Learning Research, vol. 12, pp. 2825--2830, 2011.

\[27\] Board of Accreditation for Engineering and Technical Education
(BAETE), 'Manual for Accrediting Undergraduate Engineering Programmes,'
IEB, Dhaka, Ver. 2.1, 2023.

\[28\] University of Information Technology and Sciences (UITS),
'Capstone Project and Thesis Guidelines: Department of Computer Science
and Engineering,' UITS Academic Council, Dhaka, Bangladesh, 2026.

Plagiarism Report

\[Official Institutional Plagiarism Verification Report to be inserted
here\]

In accordance with Department of Computer Science and Engineering
capstone guidelines, the final project book must include the official
similarity report from the university-designated plagiarism checking
software (Turnitin / iThenticate). Upon completion of the final fee
defense and review board revisions, the verified digital originality
certificate will be attached to this designated section prior to final
hardcover binding.

  -------------------------------------------------------------
  \| \|
  \| \[ PLACEHOLDER: ATTACH SCANNED PDF REPORT \] \|
  \| \|
  \| Turnitin Originality Index: \< 20% \|
  \| Verified By: Capstone Review Board \|
  \| Supervisor: Sultana Rokeya Naher, Associate Professor \|
  \| Date of Verification: Spring 2026 \|
  \| \|
  -------------------------------------------------------------
