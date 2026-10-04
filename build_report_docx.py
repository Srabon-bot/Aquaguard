"""
Build AquaGuard_Capstone_Final_Report.docx
Corrected draft — all faults fixed from original AquaShield report.
"""

from docx import Document
from docx.shared import Pt, Inches, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy

doc = Document()

# ── Page margins ─────────────────────────────────────────────────────────────
for section in doc.sections:
    section.top_margin    = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin   = Cm(3.0)
    section.right_margin  = Cm(2.0)

# ── Helper functions ──────────────────────────────────────────────────────────
def set_font(run, size=11, bold=False, italic=False, color=None):
    run.bold   = bold
    run.italic = italic
    run.font.size = Pt(size)
    if color:
        run.font.color.rgb = RGBColor(*color)

def h(text, level=1, center=False, color=None, size=None):
    """Add a heading paragraph."""
    p = doc.add_heading(text, level=level)
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in p.runs:
        if color:
            run.font.color.rgb = RGBColor(*color)
        if size:
            run.font.size = Pt(size)
    return p

def para(text, bold=False, italic=False, size=11, align=None, space_before=0, space_after=6):
    """Add a normal paragraph."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after  = Pt(space_after)
    if align == 'center':
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif align == 'justify':
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r = p.add_run(text)
    set_font(r, size=size, bold=bold, italic=italic)
    return p

def bullet(text, size=11):
    p = doc.add_paragraph(style='List Bullet')
    r = p.add_run(text)
    set_font(r, size=size)
    return p

def eq(label, formula):
    """Display an equation line."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = p.add_run(formula)
    set_font(r1, size=11, italic=True)
    r2 = p.add_run(f"  ... ({label})")
    set_font(r2, size=10)
    return p

def table_with_headers(headers, rows, col_widths=None):
    """Add a formatted table."""
    t = doc.add_table(rows=1+len(rows), cols=len(headers))
    t.style = 'Table Grid'
    # Header row
    hrow = t.rows[0]
    for i, h_text in enumerate(headers):
        cell = hrow.cells[i]
        cell.text = h_text
        for run in cell.paragraphs[0].runs:
            run.bold = True
            run.font.size = Pt(10)
        # Header shading
        shading = OxmlElement('w:shd')
        shading.set(qn('w:fill'), '1F3864')
        shading.set(qn('w:color'), 'FFFFFF')
        shading.set(qn('w:val'), 'clear')
        cell._tc.get_or_add_tcPr().append(shading)
        for run in cell.paragraphs[0].runs:
            run.font.color.rgb = RGBColor(255, 255, 255)
    # Data rows
    for ri, row_data in enumerate(rows):
        drow = t.rows[ri+1]
        for ci, cell_text in enumerate(row_data):
            cell = drow.cells[ci]
            cell.text = str(cell_text)
            for run in cell.paragraphs[0].runs:
                run.font.size = Pt(10)
        # Alternating row shading
        if ri % 2 == 0:
            for cell in drow.cells:
                shading = OxmlElement('w:shd')
                shading.set(qn('w:fill'), 'DCE6F1')
                shading.set(qn('w:val'), 'clear')
                cell._tc.get_or_add_tcPr().append(shading)
    if col_widths:
        for row in t.rows:
            for ci, cell in enumerate(row.cells):
                if ci < len(col_widths):
                    cell.width = Inches(col_widths[ci])
    doc.add_paragraph()  # spacing after table
    return t

def page_break():
    doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# TITLE PAGE
# ═══════════════════════════════════════════════════════════════════════════════
doc.add_paragraph()
doc.add_paragraph()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("UNIVERSITY OF INFORMATION TECHNOLOGY AND SCIENCES (UITS)")
set_font(r, size=13, bold=True)

para("Department of Computer Science & Engineering", bold=True, align='center', size=12)
doc.add_paragraph()
doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("AquaGuard")
set_font(r, size=28, bold=True, color=(31, 56, 100))

para("Intelligent Aquaculture Monitoring and Adaptive Protection System", italic=True, align='center', size=14)
doc.add_paragraph()

para("Capstone Project Report — Final Draft", bold=True, align='center', size=13)
para("Bachelor of Science in Computer Science & Engineering", align='center', size=12)
doc.add_paragraph()
doc.add_paragraph()

for name, sid in [("Srabon", "0432310005101056"),
                  ("Md. Mahfuz", "0432310005101057"),
                  ("Hrithik Saha", "0432310005101071")]:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(f"{name}   |   ID: {sid}")
    set_font(r, size=11)

doc.add_paragraph()
para("Supervisor: Sultana Rokeya Naher", bold=True, align='center', size=11)
para("Associate Professor, Department of CSE, UITS", align='center', size=11)
doc.add_paragraph()
para("Dhaka, Bangladesh — October 2026", align='center', size=11)
page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# ABSTRACT
# ═══════════════════════════════════════════════════════════════════════════════
h("Abstract", 1)
para(
    "Fish farming contributes over 3.5% to Bangladesh's national GDP and supplies 60% of dietary animal protein. "
    "Fish farmers in Bangladesh face two recurring threats: silent pond water deterioration that kills fish before "
    "farmers notice, and seasonal monsoon river floods that overtop pond dikes and wash away entire stocks. Most "
    "small-scale farmers rely on manual weekly inspection — a method that cannot detect early-stage toxicity.",
    align='justify'
)
para(
    "This capstone project presents AquaGuard, an integrated low-cost IoT monitoring system combined with a "
    "three-model predictive machine learning decision-support engine. The hardware edge node uses an ESP32 "
    "(WROOM-32) microcontroller connected to a pH probe (PH4502C, powered at 3.3V to protect the ESP32 ADC pins), "
    "a TDS probe, an NTC thermistor for temperature, and an HC-SR04 ultrasonic water-level sensor. An autonomous "
    "Finite State Machine (FSM) running every 30 seconds controls a 2-channel optoisolated relay module for a drain "
    "pump and a refill pump, plus a servo-based automated fish feeder. Live telemetry is pushed to a Firebase "
    "Realtime Database, which drives a web dashboard with alert banners.",
    align='justify'
)
para("Three machine learning models provide predictive protection:", align='justify')
bullet(
    "Model 1 — River Flood Forecast: Predicts Jamuna River water levels at Bahadurabad Transit 1 to 14 days ahead, "
    "trained on 15 years (2008–2022) of BWDB gauge data with Leave-One-Year-Out (LOYO) cross-validation. Linear "
    "Regression achieved NSE = 0.985 and RMSE = 0.308 m on the 2020–2022 test holdout, outperforming tree-based "
    "models because linear models extrapolate flood peaks without hitting a training-set ceiling."
)
bullet(
    "Model 2 — Pond TDS Forecast (+60 min): Linear Regression (R² = 0.888, MAE = 7.05 ppm) outperformed XGBoost "
    "(R² = 0.711) because pond chemistry drifts slowly over a 60-minute window. SHAP analysis confirmed physically "
    "expected lag features as dominant predictors."
)
bullet(
    "Model 3 — Multivariate Anomaly Detection: Isolation Forest trained on sensor rate-of-change deltas detected "
    "67 anomalies versus 55 by single-parameter Z-scores, catching dangerous multi-parameter conditions such as "
    "pH 8.2 combined with temperature 32°C that cause lethal ammonia spikes."
)
para("Total build cost: 6,570 BDT (~$55 USD).", bold=True, align='justify')
para(
    "Keywords: Internet of Things, Water Quality Monitoring, Flood Early Warning, Machine Learning, Explainable AI "
    "(SHAP), Isolation Forest, Bangladesh Aquaculture.",
    italic=True
)
page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# CHAPTER 1
# ═══════════════════════════════════════════════════════════════════════════════
h("Chapter 1: Introduction", 1)

h("1.1 Introduction", 2)
para(
    "Bangladesh is one of the world's leading aquaculture nations. Over 18 million people depend on fish farming "
    "as their primary livelihood [1]. The sector faces two specific threats that current technology does not address "
    "for small-scale farmers: pond water toxicity and monsoon river flooding.",
    align='justify'
)
bullet("Pond water toxicity develops gradually and silently. pH imbalances, TDS spikes from fertilizer runoff, "
       "and temperature-driven ammonia surges can kill an entire pond stock before a farmer notices any visible "
       "change in the water.")
bullet("Monsoon river flooding from the Jamuna catchment can overtop pond dikes within hours of reaching the "
       "Bahadurabad gauge, washing away an entire season's harvest.")
para(
    "AquaGuard addresses both threats with a single integrated system: an affordable IoT edge node that monitors "
    "and acts locally, and a cloud-backed machine learning engine that provides advance warning.",
    align='justify'
)

h("1.2 Motivation", 2)
para("Four specific gaps motivated this project:", align='justify')
bullet("No continuous water monitoring. Parameters like pH and TDS change throughout the day. Farmers visually "
       "check water color once a week. By the time a problem is visible, fish are already dying.")
bullet("No automated protective action. If a farmer is asleep or away when a TDS spike begins, no system turns "
       "on the drain pump in time.")
bullet("No local flood warning for farmers. National agency warnings cover entire basins. A fish farmer on the "
       "Jamuna floodplain needs 3–7 days advance warning at the Bahadurabad gauge specifically.")
bullet("No affordable solution. Commercial SCADA or PLC systems cost $2,000–$10,000 — completely unaffordable for "
       "a rural Bangladeshi farmer.")
para("AquaGuard was designed to cost under 7,200 BDT (~$60) using off-the-shelf components.", align='justify')

h("1.3 Aims and Objectives", 2)
para("The specific technical objectives were:", align='justify')
for obj in [
    "Assemble a multi-sensor IoT edge node using an ESP32 connected to pH, TDS, temperature, and ultrasonic "
    "water-level sensors, sampling every 30 seconds.",
    "Program a Finite State Machine in C++ to automatically control two pumps and a servo feeder based on local "
    "sensor readings, with rules that continue operating if internet drops.",
    "Set up Firebase Realtime Database for cloud telemetry and a Python FastAPI backend to serve three ML models.",
    "Train and evaluate Model 1: Jamuna River water-level forecasting (1–14 days) using LOYO cross-validation.",
    "Train and evaluate Model 2: Pond TDS forecasting (+60 minutes) with SHAP explainability.",
    "Train and evaluate Model 3: Unsupervised multivariate anomaly detection using Isolation Forest.",
    "Build a web dashboard with live sensor tiles, pump controls, alert banners, trend charts, and a browser-based "
    "pH calibration wizard."
]:
    bullet(obj)

h("1.4 Challenges", 2)
bullet("Hardware protection: The PH4502C module is typically powered at 5V. That risks burning out the ESP32 ADC "
       "pin. We operated it at 3.3V and compensated through two-point software calibration.")
bullet("Time-series data leakage: Standard K-Fold cross-validation shuffles data randomly and leaks future values "
       "into training. We designed LOYO validation to prevent this.")
bullet("Peak extrapolation failure: Tree-based models cannot predict water levels above the maximum in training data "
       "— a critical failure for record-breaking flood years.")
bullet("No labeled anomaly data: Fish ponds do not have historical logs of 'bad water' events, ruling out supervised "
       "classification for Model 3.")

h("1.5 Contributions", 2)
bullet("Built a sub-$60 multi-sensor ESP32 edge node with voltage dividers, 3.3V sensor operation, and 64-sample "
       "ADC oversampling for noise reduction.")
bullet("Proved through 15-year LOYO cross-validation that Linear Regression outperforms tree ensembles for extreme "
       "flood peak extrapolation.")
bullet("Delivered dual-horizon protection: 3–14 day river flood warning + 60-minute pond quality forecast + "
       "real-time anomaly detection.")
bullet("Designed a browser-based pH calibration wizard requiring no firmware re-flashing.")
page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# CHAPTER 2
# ═══════════════════════════════════════════════════════════════════════════════
h("Chapter 2: Background Studies", 1)

h("2.1 Water Quality Parameters and Fish Biology", 2)
para(
    "Fish health depends directly on four measurable water parameters [5], [6].",
    align='justify'
)
bullet("pH (6.5–8.5 safe range): Below pH 6.0, gill irritation begins. Above pH 8.8, harmless ammonium (NH4+) "
       "converts to unionized ammonia (NH3), which is acutely toxic. At pH 9.5 combined with 32°C, lethal "
       "concentrations form within hours.")
bullet("TDS — Total Dissolved Solids (150–450 ppm safe): High TDS signals excess unconsumed feed, organic waste, "
       "or fertilizer runoff. Above 600 ppm it causes osmotic stress and clogs gill filaments.")
bullet("Temperature (25–30°C safe): Warm water holds less dissolved oxygen while fish metabolism speeds up. "
       "Temperature also multiplies ammonia toxicity — the same ammonia level is 10× more toxic at 30°C than at 20°C.")
bullet("Pond Water Level (80–150 cm safe): Levels below 40 cm cause rapid temperature swings. Levels above 160 cm "
       "risk embankment overtopping.")

table_with_headers(
    ["Parameter", "Safe Range", "Warning", "Critical", "Biological Effect"],
    [
        ["pH", "6.5 – 8.5", "< 6.2 or > 8.8", "< 5.0 or > 9.5", "Gill burns, ammonia toxicity"],
        ["TDS (ppm)", "150 – 450", "450 – 600", "> 800", "Osmotic stress, gill clogging"],
        ["Temperature (°C)", "25 – 30", "30 – 33 or < 20", "> 35 or < 15", "Low oxygen, metabolic collapse"],
        ["Water Level (cm)", "80 – 150", "< 60 or > 160", "< 40 or > 180", "Dike overtopping, fish escape"],
    ],
    col_widths=[1.2, 1.0, 1.3, 1.2, 2.1]
)
para("Table 2.1. Water Quality Safety Thresholds for Cultured Fish Species", italic=True, align='center', size=10)

h("2.2 Monsoon Flooding in the Jamuna Basin", 2)
para(
    "Over 92% of the Jamuna catchment lies outside Bangladesh, in the Himalayas and Meghalaya hills of India. "
    "Heavy monsoon rainfall from June to October creates large discharge pulses that travel downstream. At the "
    "Bahadurabad Transit gauge in Jamalpur, water levels regularly exceed the 19.05 m official Danger Level. "
    "In 2020, the level reached 20.63 m, submerging over 40,000 hectares of fish ponds and causing losses "
    "exceeding 500 crore BDT ($45M USD) [3]. Fish farmers need a 3–7 day advance warning at the Bahadurabad "
    "gauge specifically — enough time to raise perimeter netting or harvest marketable fish before floodwater "
    "arrives.",
    align='justify'
)

h("2.3 Related IoT Aquaculture Systems", 2)
para(
    "Prior IoT systems each have specific gaps [7]–[12]: early Arduino + ZigBee systems had no pump control; "
    "ESP8266/ESP32 systems on ThingSpeak or Blynk fully depended on continuous internet; and commercial PLC "
    "systems cost $2,000–$10,000, completely unaffordable for rural farmers. No existing affordable system combines "
    "local offline-safe pump control, flood early warning, and unsupervised anomaly detection in a single "
    "platform under $60.",
    align='justify'
)

h("2.4 Machine Learning for Flood Forecasting", 2)
para(
    "Linear regression and tree ensembles trained on historical gauge data can achieve strong NSE values on "
    "multi-day forecast horizons [4]. A critical and often unreported limitation of tree models is that they "
    "cannot extrapolate beyond the maximum water level seen in training data — a fatal failure mode for "
    "record-breaking flood seasons. Leave-One-Year-Out (LOYO) cross-validation, borrowed from hydrology "
    "literature [19], prevents the temporal data leakage that standard K-Fold cross-validation would introduce.",
    align='justify'
)
page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# CHAPTER 3
# ═══════════════════════════════════════════════════════════════════════════════
h("Chapter 3: Methodology", 1)

h("3.1 System Architecture Overview", 2)
para("AquaGuard is organized into five tiers:", align='justify')
bullet("Sensor Tier: Physical sensors on the ESP32 (pH, TDS, Temperature, Water Level)")
bullet("Edge Control Tier: Local FSM rules on the ESP32 — controls pumps and feeder independently of internet")
bullet("Cloud Data Tier: Firebase Realtime Database for live telemetry and pump command states")
bullet("ML Prediction Tier: Python FastAPI backend (api_combined.py) serving all three models on Port 8000")
bullet("User Interface Tier: Vanilla HTML/JS/CSS web dashboard with live dials, charts, alert banners, and pH calibration page")

h("3.2 Hardware Sensor Equations", 2)
para(
    "The PH4502C module was powered at 3.3V (not the standard 5V) to protect the ESP32 ADC pins, which have "
    "a maximum input of 3.3V. The analog voltage output is converted to pH using the two-point calibration formula:",
    align='justify'
)
eq("3.1", "pH  =  7.0  +  (V_cal  −  V_out) / S")
para(
    "where V_cal is the voltage at pH 7.0, V_out is the measured voltage, and S is the probe slope (mV per pH unit).",
    align='justify'
)
para("Temperature compensation adjusts the raw ADC reading:", align='justify')
eq("3.2", "V_comp  =  V_adc  /  [ 1.0 + 0.02 × (T − 25.0) ]")
para(
    "Calibration reference points: vinegar (~pH 2.4) as the acid reference and baking soda solution (~pH 8.3) as "
    "the base reference. Because the sensor output voltage is inverted (vinegar gives a higher voltage), the "
    "calibration order in firmware was reversed — vinegar stored as 'base', baking soda as 'acid'. Both values "
    "are saved to ESP32 Non-Volatile Storage (NVS) and survive power cycles.",
    italic=True, align='justify'
)
para("Water level from the HC-SR04 ultrasonic sensor:", align='justify')
eq("3.3", "Water Level  =  Pond Depth  −  ( t_echo × v_sound ) / 2")
para(
    "The HC-SR04 ECHO pin outputs 5V logic. A 1 kΩ / 2 kΩ resistor voltage divider steps this down to 3.3V "
    "before reaching GPIO 18 on the ESP32.",
    align='justify'
)

h("3.3 Bill of Materials", 2)
table_with_headers(
    ["Component", "Qty", "Unit (BDT)", "Total (BDT)", "Function"],
    [
        ["ESP32 WROOM-32", "1", "650", "650", "Main microcontroller"],
        ["pH Sensor (PH4502C)", "1", "1,850", "1,850", "Pond pH measurement"],
        ["TDS Sensor Module", "1", "185", "185", "Dissolved solids measurement"],
        ["NTC Thermistor", "1", "40", "40", "Water temperature"],
        ["HC-SR04 Ultrasonic", "1", "120", "120", "Water depth measurement"],
        ["2-Channel Relay Module", "1", "645", "645", "Pump control"],
        ["Submersible Pump ×2", "2", "325", "650", "Drain and refill"],
        ["Servo Motor", "1", "500", "500", "Automated feeder"],
        ["LM2596 Buck Converter", "1", "150", "150", "Voltage regulation"],
        ["Resistors, capacitors, wire", "–", "130", "130", "Voltage dividers, filtering"],
        ["Breadboard / PCB", "1", "250", "250", "Circuit assembly"],
        ["Miscellaneous", "–", "400", "400", "Connectors, cable"],
        ["TOTAL", "", "", "6,570 BDT (~$55 USD)", ""],
    ],
    col_widths=[2.2, 0.5, 1.0, 1.1, 2.0]
)
para("Table 3.1. AquaGuard Hardware Bill of Materials", italic=True, align='center', size=10)

h("3.4 Edge FSM Control Rules", 2)
table_with_headers(
    ["Rule", "Trigger Condition", "Automatic Action"],
    [
        ["Water too high", "Level ≥ 85 cm AND TDS < 600 ppm", "Activate Drain Pump for 10 minutes"],
        ["Water too low", "Level ≤ 40 cm", "Activate Refill Pump until 70 cm"],
        ["TDS overflow", "TDS ≥ 600 ppm", "Activate Drain Pump for 15 minutes"],
        ["Scheduled feeding", "Time = 08:00 or 16:00", "Rotate Servo Feeder for 3 seconds"],
    ],
    col_widths=[1.5, 2.5, 2.8]
)
para("Table 3.2. Autonomous Edge Control Rules (operate without internet)", italic=True, align='center', size=10)

h("3.5 Cloud and Backend Architecture", 2)
para(
    "Sensor readings and pump states are synchronized to the Firebase Realtime Database using the Firebase ESP32 "
    "Client SDK. The database structure separates live sensor telemetry (/sensor/*), pump command states "
    "(/pumps/*), and historical logs (/history/*). The Python FastAPI backend (api_combined.py) runs on Port 8000 "
    "and serves three endpoints — one per ML model. It uses relative paths throughout, making the entire backend "
    "fully portable across machines.",
    align='justify'
)

h("3.6 Machine Learning Methodology", 2)

p = doc.add_paragraph()
r = p.add_run("Model 1 — River Water-Level Forecasting")
set_font(r, size=11, bold=True)

para(
    "Dataset: 15 years (2008–2022, 5,479 days) of daily BWDB Bahadurabad water levels. Missing values "
    "(335 days, 6.11%) were imputed using PCHIP interpolation, which preserves monotonic flood peak shapes. "
    "Features include water level at time t, ERA5 catchment rainfall at 1-day, 3-day, and 7-day cumulative "
    "windows, and lag features WL_t-1 through WL_t-7.",
    align='justify'
)
para(
    "Validation: Leave-One-Year-Out (LOYO) cross-validation. For each test year from 2009 to 2019, the model "
    "trained on all other available years. The 2020–2022 period was held out as a final unseen test set, "
    "never touched during model selection. This scheme prevents temporal data leakage.",
    align='justify'
)
para("Evaluation metrics:", align='justify')
eq("3.4", "RMSE  =  √[ (1/N) × Σ(y_i − ŷ_i)² ]")
eq("3.5", "NSE  =  1.0  −  [ Σ(y_i − ŷ_i)²  /  Σ(y_i − ȳ)² ]")
eq("3.6", "POD  =  Hits  /  ( Hits + Misses )")
eq("3.7", "FAR  =  False Alarms  /  ( Hits + False Alarms )")

p = doc.add_paragraph()
r = p.add_run("Model 2 — Pond TDS Forecasting (+60 minutes)")
set_font(r, size=11, bold=True)

para(
    "Dataset: 1,327 continuous hourly IoT sensor records from 2023. Features: raw TDS at time t, rolling "
    "6-hour and 12-hour mean TDS, and lag features TDS_t-1 through TDS_t-12. Validation: 80/20 chronological "
    "train/test split preserving temporal order. No random shuffling.",
    align='justify'
)

p = doc.add_paragraph()
r = p.add_run("Model 3 — Multivariate Anomaly Detection")
set_font(r, size=11, bold=True)

para(
    "Algorithm: Isolation Forest (contamination = 0.05). Features: absolute sensor values (pH, TDS, Temp, "
    "Water Level) PLUS rate-of-change deltas (ΔpH, ΔTDS, ΔTemp per hour). Delta features are critical — "
    "they catch rapid deteriorations that may not yet have crossed an absolute threshold.",
    align='justify'
)
page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# CHAPTER 4
# ═══════════════════════════════════════════════════════════════════════════════
h("Chapter 4: Implementation", 1)

h("4.1 Team Work Division", 2)
table_with_headers(
    ["Member", "Responsibilities"],
    [
        ["Srabon", "Hardware fabrication, circuit wiring, voltage divider protection, pH/TDS calibration, relay integration"],
        ["Mahfuz", "Firebase Realtime DB configuration, web dashboard (HTML/CSS/JS), pH calibration page, analytics charts, remote pump control UI"],
        ["Hrithik Saha", "Python FastAPI backend (api_combined.py), all three ML pipelines, LOYO cross-validation, SHAP analysis"],
    ],
    col_widths=[1.5, 5.3]
)
para("Table 4.1. Team Work Distribution", italic=True, align='center', size=10)

h("4.2 Hardware Build", 2)
para(
    "Sensors were connected to ADC1 pins (GPIO 34 for pH, GPIO 35 for TDS) because ADC2 pins share hardware "
    "with the Wi-Fi radio and become unavailable when Wi-Fi is active. Both the pH and TDS sensors were "
    "powered from the ESP32's 3.3V rail to protect ADC inputs. A separate 5V regulated rail from an LM2596 "
    "buck converter (filtered with 470 μF + 0.1 μF capacitors) powers the relay module and pumps, "
    "preventing motor switching from resetting the ESP32.",
    align='justify'
)
table_with_headers(
    ["GPIO Pin", "Component", "Signal", "Voltage", "Interface"],
    [
        ["GPIO 34", "pH Sensor (PH4502C)", "Analog Input", "0–3.3V", "ADC1 Ch6, Wi-Fi safe"],
        ["GPIO 35", "TDS Sensor", "Analog Input", "0–2.3V", "ADC1 Ch7, Wi-Fi safe"],
        ["GPIO 32", "NTC Thermistor", "Analog Input", "3.3V", "4.7 kΩ pull-down divider"],
        ["GPIO 5", "HC-SR04 TRIG", "Digital Output", "3.3V/5V", "10 μs trigger pulse"],
        ["GPIO 18", "HC-SR04 ECHO", "Digital Input", "3.3V logic", "1 kΩ/2 kΩ voltage divider"],
        ["GPIO 25", "Relay 1 — Drain Pump", "Digital Output", "5V opto-isolated", "Active-LOW"],
        ["GPIO 26", "Relay 2 — Refill Pump", "Digital Output", "5V opto-isolated", "Active-LOW"],
        ["GPIO 13", "Servo Motor (Feeder)", "PWM Output", "5V external", "50 Hz, 1–2 ms duty"],
        ["3.3V rail", "pH + TDS sensor supply", "Power", "3.3V DC", "Protects ADC inputs"],
        ["VIN/5V", "Relay + pump supply", "Power", "5V regulated", "LM2596 buck output"],
        ["GND", "Common ground", "Ground", "0V", "Shared ground plane"],
    ],
    col_widths=[0.9, 1.8, 1.2, 1.2, 1.7]
)
para("Table 4.2. Corrected GPIO Pin Assignments (AquaGuard_v2.ino)", italic=True, align='center', size=10)

h("4.3 ESP32 Firmware", 2)
bullet("Non-blocking design: millis() timers replace all delay() calls so sensing, FSM evaluation, cloud sync, and serial logging run concurrently.")
bullet("ADC oversampling: 64 fast samples per reading; top and bottom 10% discarded; remaining values averaged — reduces AC noise from pump motors.")
bullet("NVS calibration storage: Two-point pH calibration values saved to ESP32 Non-Volatile Storage, surviving power cycles. Updated wirelessly from the dashboard without re-flashing.")
bullet("Local FSM safety: The four control rules in Table 3.2 evaluate every 30 seconds using local sensor data and continue working during internet outages.")

h("4.4 Cloud Backend", 2)
para(
    "The Firebase Realtime Database stores /sensor/ph, /sensor/tds, /sensor/temp, /sensor/level, /pumps/pump1, "
    "/pumps/pump2, and a rolling 24-hour history under /history/. State changes propagate to connected "
    "browsers in under one second. The Python FastAPI backend (api_combined.py) runs on localhost:8000 with uvicorn.",
    align='justify'
)
table_with_headers(
    ["Method", "Route", "Parameters", "Description"],
    [
        ["GET", "/api/v1/forecast", "horizon=1..14", "River water-level forecast + bilingual advice"],
        ["GET", "/api/v1/tds", "device_id", "Predicted pond TDS +60 min with SHAP scores"],
        ["GET", "/api/v1/anomaly", "pH, tds, temp (optional)", "Isolation Forest score and status"],
        ["GET", "/docs", "—", "Auto-generated Swagger API documentation"],
    ],
    col_widths=[0.8, 1.7, 1.8, 2.5]
)
para("Table 4.3. REST API Endpoints (Python FastAPI, Port 8000)", italic=True, align='center', size=10)

h("4.5 Web Dashboard", 2)
bullet("Live sensor tiles reading from Firebase in real time")
bullet("Composite Pond Health Index (0–100) calculated from all four parameters")
bullet("24-hour and 7-day trend charts (Chart.js)")
bullet("Manual pump override toggle buttons")
bullet("Bilingual (English + Bengali) actionable farmer advice based on AI predictions")
bullet("'Simulate Sensor Spike' button — injects pH 9.5 / TDS 450 / Temp 33°C into Model 3 and turns the dashboard card RED for 5 seconds (used for live defense demonstrations)")
bullet("Alert banners with 3-reading debounce (90 seconds) and 30-minute cooldown to prevent false alarm fatigue")

h("4.6 pH Calibration Page", 2)
para(
    "A separate browser page (ph-calibration.html) walks the user through two-point calibration in three steps "
    "with no hardware re-flashing. The user dips the probe in vinegar (pH 2.4) and clicks 'Capture Acid Point', "
    "then dips it in baking soda solution (pH 8.3) and clicks 'Capture Base Point'. The page writes new "
    "calibration values into Firebase; the ESP32 reads and saves them to NVS on the next telemetry cycle.",
    align='justify'
)
page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# CHAPTER 5
# ═══════════════════════════════════════════════════════════════════════════════
h("Chapter 5: Results and Discussion", 1)

h("5.1 Sensor Calibration Results", 2)
para(
    "After two-point calibration and 64-sample oversampling, all four sensors met engineering accuracy targets. "
    "Note: pH calibration used vinegar (~pH 2.4) and baking soda solution (~pH 8.3) as the two reference points.",
    align='justify'
)
table_with_headers(
    ["Sensor", "Pre-Cal Error", "Post-Cal Error", "R²", "72h Drift"],
    [
        ["pH (PH4502C)", "±0.42 pH", "±0.05 pH", "0.994", "±0.03 pH"],
        ["TDS Probe", "±8.5%", "±2.8%", "0.989", "±4.2 ppm"],
        ["NTC Thermistor", "±0.85°C", "±0.15°C", "0.998", "±0.08°C"],
        ["HC-SR04 Ultrasonic", "±2.4 cm", "±0.4 cm", "0.996", "±0.2 cm"],
    ],
    col_widths=[1.8, 1.3, 1.4, 0.8, 1.5]
)
para("Table 5.1. Sensor Calibration Accuracy Results", italic=True, align='center', size=10)

h("5.2 Model 1: River Flood Forecasting Results", 2)
table_with_headers(
    ["Attribute", "Value", "Significance"],
    [
        ["Study Period", "2008-01-01 to 2022-12-31", "15 continuous years"],
        ["Total Days", "5,479", "Full seasonal cycles"],
        ["Missing Days", "335 (6.11%)", "Imputed via PCHIP"],
        ["Gauge Range", "11.68 m – 21.16 m", "Wide dynamic range"],
        ["Official Danger Level", "19.05 m", "Embankment overtopping"],
        ["Extreme Danger Level", "19.90 m", "Severe regional flooding"],
        ["Record High Water Level", "20.63 m", "2020 peak flood"],
        ["Flood Days (≥ 19.05 m)", "467 days", "Training flood events"],
    ],
    col_widths=[2.2, 1.8, 2.8]
)
para("Table 5.2. Bahadurabad Station Dataset Summary (2008–2022)", italic=True, align='center', size=10)

table_with_headers(
    ["Model", "RMSE (m)", "MAE (m)", "NSE", "R²"],
    [
        ["Persistence Baseline", "0.412", "0.298", "0.921", "0.921"],
        ["Persistence + Trend", "0.389", "0.271", "0.933", "0.933"],
        ["Linear Regression ★", "0.075", "0.051", "0.998", "0.998"],
        ["Ridge Regression", "0.078", "0.054", "0.997", "0.997"],
        ["Lasso Regression", "0.081", "0.057", "0.997", "0.997"],
        ["Random Forest", "0.104", "0.073", "0.994", "0.994"],
        ["XGBoost", "0.118", "0.081", "0.992", "0.992"],
        ["SVR", "0.143", "0.098", "0.988", "0.988"],
    ],
    col_widths=[2.4, 1.0, 1.0, 1.0, 1.0]
)
para("Table 5.3. LOYO Cross-Validation Results — +1 Day Forecast Horizon  (★ = Deployed model)", italic=True, align='center', size=10)

para(
    "Key Finding — Peak Extrapolation Failure: Tree-based models (Random Forest, XGBoost) are bounded by the "
    "maximum water level in their training data. During the 2020 and 2022 flood seasons, both of which produced "
    "levels near 20.50 m, tree models predicted a flat ceiling of ~19.80 m. Linear Regression correctly "
    "extrapolated the upward trend with low error. This is the structural reason Linear Regression was deployed.",
    bold=False, align='justify'
)

table_with_headers(
    ["Model", "RMSE (m)", "NSE", "Flood Days Missed", "False Alarms"],
    [
        ["Persistence Baseline", "0.523", "0.898", "8", "8"],
        ["Linear Regression ★", "0.308", "0.985", "11", "3"],
        ["Random Forest", "0.412", "0.951", "12", "5"],
        ["XGBoost", "0.438", "0.944", "13", "2"],
    ],
    col_widths=[2.4, 1.1, 1.0, 1.5, 1.2]
)
para("Table 5.4. Final Holdout Test Results — 2020–2022 Test Years (3-Day Horizon)", italic=True, align='center', size=10)

para(
    "Safety Buffer: All ML models missed more flood days than the Persistence Baseline due to peak-smoothing. "
    "The dashboard alert threshold was set to 18.55 m — 0.5 m below the 19.05 m Danger Level — to give "
    "farmers earlier warning that compensates for this known limitation.",
    align='justify', italic=True
)

h("5.3 Model 2: Pond TDS Forecasting Results", 2)
table_with_headers(
    ["Model", "MAE (ppm)", "RMSE (ppm)", "R²", "Notes"],
    [
        ["Persistence Baseline", "6.14", "8.92", "0.942", "Best R²; no trend info"],
        ["Linear Regression ★", "7.05", "10.11", "0.888", "Deployed; uses rolling trend"],
        ["Random Forest", "9.43", "13.77", "0.781", "Overfit to sensor noise"],
        ["XGBoost", "11.28", "16.33", "0.711", "Worst; most overfit"],
    ],
    col_widths=[2.0, 1.1, 1.2, 0.9, 2.1]
)
para("Table 5.5. Model 2 Performance Comparison (+60 min Horizon)  (★ = Deployed model)", italic=True, align='center', size=10)

para(
    "SHAP analysis confirmed the 6-hour rolling mean TDS and the 3-hour lag feature (TDS_t-3) as the two dominant "
    "predictors — validating the model's physical interpretability. It is learning real chemical kinetics, not noise.",
    align='justify'
)

h("5.4 Model 3: Multivariate Anomaly Detection Results", 2)
table_with_headers(
    ["Method", "Anomalies Detected", "Estimated True Positives", "Type"],
    [
        ["Standard Z-Score (single parameter)", "55", "38", "Univariate"],
        ["Isolation Forest (AquaGuard) ★", "67", "51", "Multivariate"],
    ],
    col_widths=[2.6, 1.5, 1.8, 1.0]
)
para("Table 5.6. Anomaly Detection Comparison  (★ = Deployed)", italic=True, align='center', size=10)

para(
    "The 12 additional anomalies caught by Isolation Forest are multivariate events — conditions where no "
    "individual parameter crossed its danger threshold but the combination was harmful. Most common example: "
    "pH 8.2 (within safe range) combined with temperature 32°C (within safe range), which together produce "
    "lethal ammonia concentrations.",
    align='justify'
)

h("5.5 System Latency", 2)
table_with_headers(
    ["Metric", "Measured Value"],
    [
        ["Firebase read → dashboard update", "< 1 second (WebSocket push)"],
        ["FSM local rule evaluation cycle", "Every 30 seconds"],
        ["ML API response time (all 3 models)", "< 250 ms on local Python server"],
        ["Pump relay trigger → action", "< 500 ms from FSM evaluation"],
    ],
    col_widths=[3.0, 3.8]
)
para("Table 5.7. System Latency Benchmarks", italic=True, align='center', size=10)
page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# CHAPTER 6
# ═══════════════════════════════════════════════════════════════════════════════
h("Chapter 6: Conclusion and Future Work", 1)

h("6.1 Conclusion", 2)
para(
    "AquaGuard demonstrates that a capable, multi-model aquaculture protection system can be built for under "
    "7,200 BDT using commodity hardware and free cloud services. The key findings from this project are:",
    align='justify'
)
bullet("Linear models beat tree models during extreme flood events because they extrapolate beyond their training "
       "range. Deploying tree models alone for flood warning risks failing precisely during the most dangerous floods.")
bullet("Pond TDS is slow-moving over short windows. A rolling-average linear model outperforms XGBoost for "
       "60-minute predictions. Algorithmic complexity is not always beneficial.")
bullet("Unsupervised anomaly detection with multivariate delta features catches 22% more hazards than "
       "single-parameter threshold checks.")
bullet("A browser-based calibration architecture requiring no firmware re-flashing is critical for real-world "
       "deployment to non-technical rural farmers.")

h("Known Limitations", 3)
bullet("Model 1 covers the Bahadurabad/Jamuna station only. The Surma-Kushiyara basin (Sylhet) flash floods are not modeled.")
bullet("pH probes require physical cleaning every 2–4 weeks to prevent biofilm drift.")
bullet("Wi-Fi dependency limits deployment to ponds within router range. Remote ponds need a GSM module.")
bullet("The AquaGuard_v2.ino firmware is ready to flash but has not yet been deployed to a production fish pond for longitudinal field testing.")

h("6.2 Future Work", 2)
bullet("Multi-basin expansion: Add the Surma-Kushiyara system for Sylhet flash flood early warning (requires hourly, not daily, data).")
bullet("Automated SMS / WhatsApp alerts: Integrate Twilio to push anomaly and flood warnings to farmers' phones when they are offline.")
bullet("Closed-loop firmware automation: Automatically trigger relay pumps when Model 3 detects a severe anomaly score without manual dashboard clicks.")
bullet("LoRaWAN mesh: Connect multiple ponds across a 10 km radius to a single gateway for cooperative-scale monitoring.")
bullet("Solar off-grid power: A 50W panel and 12V LiFePO4 battery would make the device fully self-powered in areas without grid electricity.")
page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# APPENDIX A
# ═══════════════════════════════════════════════════════════════════════════════
h("Appendix A: Hardware Pinout and API Endpoints", 1)

h("A.1 Complete Hardware Pinout Specifications", 2)
table_with_headers(
    ["ESP32 Pin", "Component", "Signal", "Voltage", "Interface / Notes"],
    [
        ["GPIO 34", "pH Sensor (PH4502C)", "Analog Input", "0–3.3V", "ADC1 Ch6, Wi-Fi safe"],
        ["GPIO 35", "TDS Sensor", "Analog Input", "0–2.3V", "ADC1 Ch7, Wi-Fi safe"],
        ["GPIO 32", "NTC Thermistor", "Analog Input", "3.3V", "4.7 kΩ pull-down divider"],
        ["GPIO 5", "HC-SR04 TRIG", "Digital Output", "3.3V/5V TTL", "10 μs trigger pulse"],
        ["GPIO 18", "HC-SR04 ECHO", "Digital Input", "3.3V logic", "1 kΩ/2 kΩ voltage divider (5V→3.3V)"],
        ["GPIO 25", "Relay 1 — Drain Pump", "Digital Output", "5V opto-isolated", "Active-LOW optocoupler"],
        ["GPIO 26", "Relay 2 — Refill Pump", "Digital Output", "5V opto-isolated", "Active-LOW optocoupler"],
        ["GPIO 13", "Servo Motor (Feeder)", "PWM Output", "5V external", "50 Hz, 1.0–2.0 ms duty cycle"],
        ["3.3V rail", "pH + TDS sensor supply", "Power", "3.3V DC", "Used instead of 5V — protects ADC pins"],
        ["VIN/5V", "Relay + pump supply", "Power", "5V regulated", "LM2596 DC-DC buck converter output"],
        ["GND", "Common ground", "Ground", "0V", "Shared ground plane for MCU, sensors, power"],
    ],
    col_widths=[0.9, 1.8, 1.1, 1.2, 2.3]
)
para("Table A.1. Complete Hardware Pinout Specifications (verified against AquaGuard_v2.ino)", italic=True, align='center', size=10)

h("A.2 REST API Endpoints", 2)
table_with_headers(
    ["Method", "Route", "Parameters", "Response"],
    [
        ["GET", "/api/v1/forecast", "horizon=1..14", "River water level forecast + bilingual farmer advice + hydrograph data"],
        ["GET", "/api/v1/tds", "device_id", "Predicted pond TDS +60 min, trend direction, SHAP feature scores"],
        ["GET", "/api/v1/anomaly", "pH, tds, temp (optional)", "Isolation Forest anomaly status, score, severity message"],
        ["GET", "/docs", "—", "Auto-generated Swagger API documentation (FastAPI built-in)"],
    ],
    col_widths=[0.8, 1.6, 1.9, 2.5]
)
para("Table A.2. REST API Endpoints (Python FastAPI Backend, localhost:8000)", italic=True, align='center', size=10)
page_break()

# ═══════════════════════════════════════════════════════════════════════════════
# REFERENCES
# ═══════════════════════════════════════════════════════════════════════════════
h("References", 1)

refs = [
    "Department of Fisheries (DoF), 'Yearbook of Fisheries Statistics of Bangladesh 2022-23,' Ministry of Fisheries and Livestock, Dhaka, Bangladesh, 2023.",
    "Food and Agriculture Organization (FAO), 'The State of World Fisheries and Aquaculture 2024,' FAO, Rome, Italy, 2024.",
    "Flood Forecasting and Warning Centre (FFWC), 'Annual Flood Report 2020,' BWDB, Dhaka, Bangladesh, 2021.",
    "M. M. Rahman, M. A. Hossain, and S. Islam, 'Impact of climate change and extreme monsoon flooding on inland aquaculture in northern Bangladesh,' Journal of Water and Climate Change, vol. 12, no. 4, pp. 1420–1435, 2021.",
    "C. E. Boyd, Water Quality: An Introduction, 3rd ed., Cham, Switzerland: Springer Nature, 2020.",
    "J. E. Colt, Dissolved Gas Concentration in Water, 2nd ed., London: Academic Press, 2012.",
    "P. Saha, D. Biswas, and A. K. Das, 'IoT-based automated water quality monitoring and alert system for fish farming,' in Proc. IEEE ICSCEE, Shah Alam, Malaysia, 2018, pp. 1–6.",
    "K. R. Raju, G. H. Kumar, and M. V. Reddy, 'Automated water quality monitoring and control system for aquaculture using Raspberry Pi,' IEEE IoT Journal, vol. 7, no. 9, pp. 8412–8421, 2020.",
    "M. R. Hasan, M. S. Alam, and T. Sultana, 'Design and deployment of a low-cost IoT telemetry node for rural fish ponds in Bangladesh,' in Proc. IEEE ICEEICT, Dhaka, 2021, pp. 215–220.",
    "M. N. Islam, S. K. Roy, and R. Ahmed, 'Predictive water aeration and quality management using ESP32 edge microcontroller,' IEEE Access, vol. 10, pp. 54312–54324, 2022.",
    "X. Chen, Y. Zhang, and L. Wang, 'Industrial PLC-driven multi-parameter recirculating aquaculture control system with deep LSTM DO prediction,' Computers and Electronics in Agriculture, vol. 205, art. no. 107621, 2023.",
    "S. Ahmed, F. Farzana, and K. M. Kabir, 'Automated fish feeding and pond level management system using IoT relays and ultrasonic sensing,' in Proc. IEEE CONECCT, Bangalore, 2024, pp. 1–6.",
    "F. T. Liu, K. M. Ting, and Z.-H. Zhou, 'Isolation Forest,' in Proc. 8th IEEE ICDM, Pisa, Italy, 2008, pp. 413–422.",
    "S. M. Lundberg and S.-I. Lee, 'A unified approach to interpreting model predictions,' in Advances in Neural Information Processing Systems (NeurIPS 30), 2017, pp. 4765–4774.",
    "T. Chen and C. Guestrin, 'XGBoost: A scalable tree boosting system,' in Proc. 22nd ACM SIGKDD, 2016, pp. 785–794.",
    "L. Breiman, 'Random Forests,' Machine Learning, vol. 45, no. 1, pp. 5–32, 2001.",
    "A. E. Hoerl and R. W. Kennard, 'Ridge regression: Biased estimation for nonorthogonal problems,' Technometrics, vol. 12, no. 1, pp. 55–67, 1970.",
    "R. Tibshirani, 'Regression shrinkage and selection via the Lasso,' Journal of the Royal Statistical Society: Series B, vol. 58, no. 1, pp. 267–288, 1996.",
    "J. E. Nash and J. V. Sutcliffe, 'River flow forecasting through conceptual models part I,' Journal of Hydrology, vol. 10, no. 3, pp. 282–290, 1970.",
    "H. Hersbach et al., 'The ERA5 global reanalysis,' Quarterly Journal of the Royal Meteorological Society, vol. 146, no. 730, pp. 1999–2049, 2020.",
    "Bangladesh Water Development Board (BWDB), 'Hydrometric Data Portal: Daily Water Levels — Station SW46.9L,' BWDB Hydrology Division, Dhaka, 2024.",
    "Espressif Systems, 'ESP32 Series Datasheet: 2.4 GHz Wi-Fi and Bluetooth Combo Chip,' Espressif Systems, Shanghai, China, 2023.",
    "F. Pedregosa et al., 'Scikit-learn: Machine learning in Python,' Journal of Machine Learning Research, vol. 12, pp. 2825–2830, 2011.",
    "Board of Accreditation for Engineering and Technical Education (BAETE), 'Manual for Accrediting Undergraduate Engineering Programmes,' IEB, Dhaka, Ver. 2.1, 2023.",
    "University of Information Technology and Sciences (UITS), 'Capstone Project and Thesis Guidelines: Department of CSE,' UITS Academic Council, Dhaka, Bangladesh, 2026.",
]
for i, ref in enumerate(refs):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(f"[{i+1}]  ")
    set_font(r, size=10, bold=True)
    r2 = p.add_run(ref)
    set_font(r2, size=10)

# Save
out = "D:/Projects/pred_flood/AquaGuard_Capstone_Final_Report.docx"
doc.save(out)
print(f"Saved: {out}")
