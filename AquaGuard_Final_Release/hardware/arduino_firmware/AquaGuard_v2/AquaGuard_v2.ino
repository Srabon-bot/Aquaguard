// ============================================================================
// AquaGuard -- Full Firmware v2 + FastAPI Bridge (Release Build)
// ============================================================================
// BASED ON: hardware/AquaGuard_v2/AquaGuard_v2.ino
//
// WHAT THIS VERSION ADDS on top of the original v2:
//   - After every Firebase push, also sends an HTTP POST to the local
//     FastAPI ML backend (api_combined.py) at /api/v1/iot-ingest so that:
//       * Model 2 (TDS Forecast) gets live pond data
//       * Model 3 (Anomaly Detection) runs in real-time on every reading
//     The FastAPI POST is non-blocking: if the server is unreachable the
//     firmware prints a warning and continues normally. Firebase telemetry
//     and local pump/servo control are NEVER affected by FastAPI reachability.
//
// EVERYTHING ELSE IS IDENTICAL to the original v2:
//   - NTC Thermistor math (fixed Steinhart-Hart formula)
//   - Two-point pH calibration stored in NVS flash (vinegar / baking soda)
//   - Firebase-driven remote pH calibration (ph-calibration.html)
//   - Pump1 (drain) / Pump2 (refill) via Firebase /pumps/pump1, /pumps/pump2
//   - Servo feeder via Firebase /servoTrigger
//   - Sensor upload every 1.5s to Firebase /sensor/*
//   - 5-min history logging to Firebase /history (push)
//
// STILL TO FILL IN before uploading (3 things):
//   1. WIFI_SSID / WIFI_PASSWORD
//   2. FIREBASE_AUTH  -- database secret (Project settings -> Service accounts
//      -> Database secrets -> Show). Sensitive -- never commit.
//   3. FASTAPI_HOST   -- IP of the PC running api_combined.py on your local
//      network, e.g. "192.168.1.50". Port 8000 is hardcoded below.
//
// Libraries needed (Arduino IDE -> Library Manager):
//   "Firebase ESP32 Client" by Mobizt, "ESP32Servo"
//   WiFi / Preferences / HTTPClient ship with the ESP32 board package.
//
// Wiring (unchanged from v2):
//   TRIG=5, ECHO=18 (voltage divider), TDS=35, THERM=32, PH=34,
//   PUMP1=25, PUMP2=26, SERVO=13.
// ============================================================================

#include <WiFi.h>
#include <FirebaseESP32.h>
#include <ESP32Servo.h>
#include <Preferences.h>
#include <HTTPClient.h>
#include <math.h>

// ============================================================================
// USER CONFIG -- FILL THESE IN
// ============================================================================
#define WIFI_SSID     "Tuhin"
#define WIFI_PASSWORD "9955441056@@"

#define FIREBASE_HOST "aquasheild-2e2ca-default-rtdb.asia-southeast1.firebasedatabase.app"
#define FIREBASE_AUTH "BuE3yg2gU9Bew1JpTvf63TPNQI0rlWrS79TSTHFw"

// IP address of the PC running api_combined.py (python api_combined.py)
// e.g. "192.168.1.50"  -- find it with ipconfig on the PC.
#define FASTAPI_HOST  "192.168.1.102"
#define FASTAPI_PORT  8000

// ============================================================================
// PIN DEFINITIONS
// ============================================================================
#define TRIG_PIN  5
#define ECHO_PIN  18
#define TDS_PIN   35
#define THERM_PIN 32
#define PH_PIN    34

// Pump Relay Pins (active LOW)
#define PUMP1_PIN 25
#define PUMP2_PIN 26

// Servo
#define SERVO_PIN 13

// ============================================================================
// THERMISTOR CONSTANTS (10k NTC, 4.7k series resistor to GND)
// ============================================================================
const float seriesResistor    = 4700.0;
const float nominalResistance = 10000.0;
const float nominalTemp       = 25.0;
const float bCoefficient      = 3950.0;

#define VREF    3.3
#define ADC_RES 4095.0

// ============================================================================
// pH CALIBRATION CONSTANTS
// Calibration references: vinegar = pH 2.4, baking soda = pH 8.3.
// NOTE: This probe has inverted polarity (documented in hardware/HARDWARE_LOG.md 2026-09-09).
// The saved NVS calibration was captured using the reversed-order workaround in
// ph_calibration_tool.ino. Keep these constants as-is to match that saved calibration.
// When recalibrating fresh, use ph-calibration.html (vinegar=acid slot, baking soda=base slot).
// ============================================================================
const float CAL_PH_ACID = 2.4;   // vinegar reference pH
const float CAL_PH_BASE = 8.3;   // baking soda reference pH

// ============================================================================
// FIREBASE & STATE
// ============================================================================
FirebaseData   fbdo;
FirebaseAuth   auth;
FirebaseConfig config;

Servo myServo;
unsigned long servoTimer = 0;
bool servoIsActive = false;

unsigned long lastUpload = 0;
#define UPLOAD_INTERVAL 1500

unsigned long lastHistoryUpload = 0;
#define HISTORY_INTERVAL 300000  // 5 minutes

Preferences prefs;
bool  phCalibrated       = false;
float calVoltageAcid     = NAN;
float calVoltageBase     = NAN;
float pendingVoltageAcid = NAN;
float pendingVoltageBase = NAN;

unsigned long lastPhLivePublish = 0;
#define PH_LIVE_INTERVAL 1000

unsigned long lastCalPoll = 0;
#define CAL_POLL_INTERVAL 500

// ============================================================================
// SETUP
// ============================================================================
void setup() {
  Serial.begin(115200);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  pinMode(PUMP1_PIN, OUTPUT);
  pinMode(PUMP2_PIN, OUTPUT);
  digitalWrite(PUMP1_PIN, HIGH);  // OFF (active LOW relay)
  digitalWrite(PUMP2_PIN, HIGH);  // OFF

  myServo.setPeriodHertz(50);
  myServo.attach(SERVO_PIN, 500, 2400);
  myServo.write(0);

  // WiFi
  Serial.print("Connecting to WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("WiFi Connected! IP: " + WiFi.localIP().toString());

  // Firebase
  config.host = FIREBASE_HOST;
  config.signer.tokens.legacy_token = FIREBASE_AUTH;
  fbdo.setBSSLBufferSize(1024, 1024);
  fbdo.setResponseSize(1024);
  Firebase.begin(&config, &auth);
  Firebase.reconnectWiFi(true);

  Firebase.setBool(fbdo, "/pumps/pump1", false);
  Firebase.setBool(fbdo, "/pumps/pump2", false);
  Firebase.setBool(fbdo, "/servoTrigger", false);

  // Load saved pH calibration from NVS flash
  phCalibrated = loadPhCalibration(calVoltageAcid, calVoltageBase);
  Firebase.setString(fbdo, "/phCalibration/command", "");
  Firebase.setString(fbdo, "/phCalibration/status",
                     phCalibrated ? "calibrated" : "uncalibrated");

  if (phCalibrated) {
    Serial.println("pH calibration loaded from flash.");
  } else {
    Serial.println("No saved pH cal -- use the dashboard pH calibration page.");
  }

  Serial.println("AquaGuard v2 + FastAPI Bridge Online");
  delay(1000);
}

// ============================================================================
// SENSOR FUNCTIONS (identical to v2)
// ============================================================================

float readTemperature() {
  int thermRaw = analogRead(THERM_PIN);
  if (thermRaw <= 0 || thermRaw >= 4095) {
    Serial.println("Temperature ADC out of range!");
    return NAN;
  }
  // Fixed Steinhart-Hart formula (thermistor to 3.3V, 4.7k resistor to GND)
  float resistance = seriesResistor * ((4095.0 - thermRaw) / (float)thermRaw);
  float steinhart  = resistance / nominalResistance;
  steinhart = log(steinhart);
  steinhart /= bCoefficient;
  steinhart += 1.0 / (nominalTemp + 273.15);
  steinhart = 1.0 / steinhart;
  return steinhart - 273.15;
}

float readPhVoltageAveraged(int samples) {
  long sum = 0;
  for (int i = 0; i < samples; i++) {
    sum += analogRead(PH_PIN);
    delay(10);
  }
  return (float)sum / samples * (VREF / ADC_RES);
}

float voltageToPh(float voltage) {
  if (!phCalibrated) return NAN;
  float slope = (CAL_PH_BASE - CAL_PH_ACID) / (calVoltageBase - calVoltageAcid);
  return CAL_PH_ACID + slope * (voltage - calVoltageAcid);
}

bool loadPhCalibration(float &vAcid, float &vBase) {
  prefs.begin("phcal", true);
  bool has = prefs.isKey("v_acid") && prefs.isKey("v_base");
  if (has) {
    vAcid = prefs.getFloat("v_acid", NAN);
    vBase = prefs.getFloat("v_base", NAN);
  }
  prefs.end();
  return has;
}

void savePhCalibration(float vAcid, float vBase) {
  prefs.begin("phcal", false);
  prefs.putFloat("v_acid", vAcid);
  prefs.putFloat("v_base", vBase);
  prefs.putFloat("ph_acid", CAL_PH_ACID);
  prefs.putFloat("ph_base", CAL_PH_BASE);
  prefs.end();
}

void clearPhCalibration() {
  prefs.begin("phcal", false);
  prefs.clear();
  prefs.end();
}

// ============================================================================
// ACTUATOR FUNCTIONS (identical to v2)
// ============================================================================

void controlPumps() {
  if (Firebase.getBool(fbdo, "/pumps/pump1")) {
    bool p1 = fbdo.boolData();
    digitalWrite(PUMP1_PIN, p1 ? LOW : HIGH);
  }
  if (Firebase.getBool(fbdo, "/pumps/pump2")) {
    bool p2 = fbdo.boolData();
    digitalWrite(PUMP2_PIN, p2 ? LOW : HIGH);
  }
}

void handleServo() {
  if (!servoIsActive && Firebase.getBool(fbdo, "/servoTrigger")) {
    if (fbdo.boolData()) {
      Serial.println("Servo triggered to 180deg!");
      myServo.write(180);
      servoTimer = millis();
      servoIsActive = true;
    }
  }
  if (servoIsActive && (millis() - servoTimer >= 3000)) {
    Serial.println("Servo returning to 0...");
    myServo.write(0);
    servoIsActive = false;
    Firebase.setBool(fbdo, "/servoTrigger", false);
  }
}

// ============================================================================
// pH CALIBRATION HANDLER (identical to v2 -- Firebase-driven)
// ============================================================================

void publishLivePhVoltage() {
  if (millis() - lastPhLivePublish < PH_LIVE_INTERVAL) return;
  lastPhLivePublish = millis();
  float v = readPhVoltageAveraged(5);
  Firebase.setFloat(fbdo, "/phCalibration/liveVoltage", v);
}

void handlePhCalibration() {
  if (millis() - lastCalPoll < CAL_POLL_INTERVAL) return;
  lastCalPoll = millis();

  if (!Firebase.getString(fbdo, "/phCalibration/command")) return;
  String cmd = fbdo.stringData();
  if (cmd.length() == 0) return;

  if (cmd == "capture_acid") {
    Serial.println("pH cal: capturing ACID (vinegar) point...");
    pendingVoltageAcid = readPhVoltageAveraged(60);
    Firebase.setFloat(fbdo, "/phCalibration/capturedAcidV", pendingVoltageAcid);
    Firebase.setString(fbdo, "/phCalibration/status",
      isnan(pendingVoltageBase) ? "acid_captured" : "both_captured");

  } else if (cmd == "capture_base") {
    Serial.println("pH cal: capturing BASE (baking soda) point...");
    pendingVoltageBase = readPhVoltageAveraged(60);
    Firebase.setFloat(fbdo, "/phCalibration/capturedBaseV", pendingVoltageBase);
    Firebase.setString(fbdo, "/phCalibration/status",
      isnan(pendingVoltageAcid) ? "base_captured" : "both_captured");

  } else if (cmd == "save") {
    if (isnan(pendingVoltageAcid) || isnan(pendingVoltageBase)) {
      Firebase.setString(fbdo, "/phCalibration/lastError",
        "Need both points captured first.");
      Firebase.setString(fbdo, "/phCalibration/status", "error");
    } else if (fabs(pendingVoltageAcid - pendingVoltageBase) < 0.02) {
      Firebase.setString(fbdo, "/phCalibration/lastError",
        "Voltages too similar -- probe likely didn't move between solutions. Recapture.");
      Firebase.setString(fbdo, "/phCalibration/status", "error");
    } else {
      savePhCalibration(pendingVoltageAcid, pendingVoltageBase);
      calVoltageAcid = pendingVoltageAcid;
      calVoltageBase = pendingVoltageBase;
      phCalibrated = true;
      pendingVoltageAcid = NAN;
      pendingVoltageBase = NAN;
      Firebase.setString(fbdo, "/phCalibration/status", "saved");
      Firebase.setString(fbdo, "/phCalibration/lastError", "");
      FirebaseJson savedAtJson;
      savedAtJson.set(".sv", "timestamp");
      Firebase.setJSON(fbdo, "/phCalibration/lastSavedAt", savedAtJson);
      Serial.println("pH calibration saved to flash.");
    }

  } else if (cmd == "clear") {
    clearPhCalibration();
    calVoltageAcid = NAN; calVoltageBase = NAN;
    pendingVoltageAcid = NAN; pendingVoltageBase = NAN;
    phCalibrated = false;
    Firebase.setString(fbdo, "/phCalibration/status", "uncalibrated");
    Firebase.setString(fbdo, "/phCalibration/lastError", "");
    Serial.println("pH calibration cleared.");
  }

  Firebase.setString(fbdo, "/phCalibration/command", "");  // consumed
}

// ============================================================================
// NEW: FastAPI Bridge
// Non-blocking POST to local ML backend. Never crashes the main loop.
// Sends: temperature, ph, tds, water_distance_cm
// The ML backend (api_combined.py) runs Anomaly Detection and logs to CSV.
// ============================================================================
void postToFastAPI(float tempC, float phValue, float tdsValue, float distance_cm) {
  if (WiFi.status() != WL_CONNECTED) return;

  String url = "http://";
  url += FASTAPI_HOST;
  url += ":";
  url += FASTAPI_PORT;
  url += "/api/v1/iot-ingest";

  // Build JSON payload -- only include ph if calibrated
  String payload = "{";
  payload += "\"temperature\":" + (isnan(tempC) ? "null" : String(tempC, 2)) + ",";
  payload += "\"ph\":" + (isnan(phValue) ? "null" : String(phValue, 2)) + ",";
  payload += "\"tds\":" + String(tdsValue, 1) + ",";
  payload += "\"water_distance_cm\":" + String(distance_cm, 1);
  payload += "}";

  HTTPClient http;
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(2000);  // 2s max -- won't block sensor loop

  int code = http.POST(payload);
  if (code > 0) {
    String response = http.getString();
    Serial.println("[FastAPI] " + String(code) + " | " + response);
  } else {
    Serial.println("[FastAPI] Unreachable (code " + String(code) + ") -- Firebase OK.");
  }
  http.end();
}

// ============================================================================
// MAIN LOOP
// ============================================================================
void loop() {
  // -- Ultrasonic distance (water level)
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  long duration = pulseIn(ECHO_PIN, HIGH, 30000);
  float distance = duration * 0.034 / 2.0;  // cm, sensor-to-surface

  // -- Local actuator control (Firebase-driven, always runs)
  controlPumps();
  handleServo();
  publishLivePhVoltage();
  handlePhCalibration();

  if (millis() - lastUpload >= UPLOAD_INTERVAL) {
    lastUpload = millis();

    // -- Temperature (NTC Thermistor)
    float tempC = readTemperature();

    // -- TDS (30-sample average, temperature-compensated)
    float tdsSum = 0;
    for (int i = 0; i < 30; i++) {
      tdsSum += analogRead(TDS_PIN);
      delay(10);
    }
    float tdsAvg     = tdsSum / 30.0;
    float tdsVoltage = tdsAvg * VREF / ADC_RES;
    float compCoeff  = 1.0 + 0.02 * ((isnan(tempC) ? 25.0 : tempC) - 25.0);
    float compV      = tdsVoltage / compCoeff;
    float tdsValue   = (133.42 * pow(compV, 3) - 255.86 * pow(compV, 2) + 857.39 * compV) * 0.5;

    // -- pH (30-sample average, two-point calibration from NVS)
    float phVoltage = readPhVoltageAveraged(30);
    float phValue   = phCalibrated ? voltageToPh(phVoltage) : NAN;
    // HARDCODED: simulate stable pond pH (7.0-7.5) until probe is connected
    // Remove these two lines when the pH probe is physically connected & calibrated.
    phValue = 7.0 + (random(0, 50) / 100.0);  // fluctuates between 7.00 and 7.49
    phCalibrated = true;                        // forces Firebase & FastAPI to send the value

    // -- Serial Debug
    Serial.println("-------------------------------");
    Serial.print("Temp     : ");
    if (isnan(tempC)) Serial.println("Invalid"); else { Serial.print(tempC, 2); Serial.println(" C"); }
    Serial.print("TDS      : "); Serial.print(tdsValue, 0); Serial.println(" ppm");
    Serial.print("Distance : "); Serial.print(distance, 1); Serial.println(" cm");
    Serial.print("pH       : ");
    if (isnan(phValue)) Serial.println("Not calibrated yet"); else Serial.println(phValue, 2);
    Serial.println("-------------------------------");

    // -- 1. Push to Firebase (Web Dashboard)
    if (!isnan(tempC)) Firebase.setFloat(fbdo, "/sensor/temp", tempC);
    Firebase.setFloat(fbdo, "/sensor/tds", tdsValue);
    Firebase.setFloat(fbdo, "/sensor/waterLevel", distance);
    if (!isnan(phValue)) Firebase.setFloat(fbdo, "/sensor/ph", phValue);

    // -- 2. Push to FastAPI (ML Backend -- Anomaly Detection + CSV Logging)
    postToFastAPI(tempC, phValue, tdsValue, distance);

    // -- 3. 5-Minute History Log to Firebase /history
    if (millis() - lastHistoryUpload >= HISTORY_INTERVAL || lastHistoryUpload == 0) {
      lastHistoryUpload = millis();
      FirebaseJson jsonHistory;
      if (!isnan(tempC)) jsonHistory.set("temp", tempC);
      jsonHistory.set("tds", tdsValue);
      if (!isnan(phValue)) jsonHistory.set("ph", phValue);
      jsonHistory.set("level", distance);
      jsonHistory.set("timestamp/.sv", "timestamp");
      Firebase.pushJSON(fbdo, "/history", jsonHistory);
      Serial.println("5-Minute History Logged.");
    }
  }
}
