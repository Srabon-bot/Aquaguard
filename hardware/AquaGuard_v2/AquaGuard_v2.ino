// ============================================================================
// AquaGuard -- full firmware (v2), ready-to-flash copy
// ============================================================================
// This is the same sketch as hardware/rebuild/07_full_reintegration/
// AquaGuard_v2.ino, just copied into its own Arduino-IDE-friendly folder
// (Arduino requires the folder name to match the .ino file name to open it
// cleanly) with the real Firebase project's host already filled in below.
// The rebuild/07_full_reintegration/ copy stays where it is as the
// documented step-by-step build history -- this folder is the one to
// actually open in Arduino IDE and upload.
//
// STILL TO FILL IN before uploading (2 things, both below):
//   1. WIFI_SSID / WIFI_PASSWORD  -- your own WiFi network's name/password.
//   2. FIREBASE_AUTH              -- your database secret, see
//      hardware/FIREBASE_SETUP.md Step 5 (Project settings -> Service
//      accounts -> Database secrets -> Show). Sensitive -- only ever goes
//      here, on your own machine, never shared or committed for real.
// FIREBASE_HOST is already filled in (databaseURL is not a secret, safe to
// hardcode) -- matches the "AquaSheild" project's Realtime Database.
//
// FIXED vs. the original pre-teardown reference sketch
// (hardware/original_reference/AquaGuard_full_original.ino):
//   1. Thermistor resistance formula was inverted for this wiring (found
//      2026-08-12, see hardware/rebuild/03_thermistor/) -- fixed here to
//      `seriesResistor * ((4095.0 - thermRaw) / thermRaw)`.
//   2. pH now uses the real two-point calibration from
//      hardware/rebuild/01_ph_sensor/ (loaded from flash via Preferences)
//      instead of the original's crude `(3.5 * voltage) + offset` formula.
//
// Firebase-driven pH calibration (no more re-flashing ph_calibration_tool.ino
// over USB just to recalibrate):
//   The exact same two-point math as ph_calibration_tool.ino, but triggered
//   over Firebase instead of Serial, so it can be done from the dashboard's
//   pH calibration page (ph-calibration.html) on any phone/browser on the
//   same network. Fixed to vinegar (pH 2.4) / baking soda (pH 8.3) -- see
//   CAL_PH_ACID/CAL_PH_BASE below. Saves to the SAME NVS namespace/keys
//   ("phcal": v_acid/v_base/ph_acid/ph_base) that 01_ph_sensor.ino and
//   ph_calibration_tool.ino already use -- a calibration saved by any of the
//   three is readable by all three.
//
// STILL NOT included here (separate, not-yet-built future work -- see
// MODEL_BUILD_PLAN.md / the project's deferred hardware plan):
//   - Water-quality safety auto-cycling (drain+refill if pH/TDS/temp go out
//     of safe range).
//   - Water-level setpoint control (auto-drain toward a marked level).
//   - The raw ultrasonic `distance` is still published to /sensor/waterLevel
//     as-is (sensor-to-surface distance, smaller = more water) -- NOT yet
//     converted to a "cm of water, bigger = more full" value.
//   - The model-informed pump-suggestion panel on the dashboard.
// This sketch is the foundation those get added to later, not a final
// firmware.
//
// Libraries needed (Arduino IDE -> Library Manager): "Firebase ESP32
// Client" (by Mobizt), "ESP32Servo". WiFi/Preferences ship with the ESP32
// board package.
//
// Wiring (see hardware/Hardware_Wiring_Guide.pdf for the full diagram):
// TRIG=5, ECHO=18 (through the voltage divider), TDS=35, THERM=32, PH=34,
// PUMP1=25, PUMP2=26, SERVO=13.
// ============================================================================

#include <WiFi.h>
#include <FirebaseESP32.h>
#include <ESP32Servo.h>
#include <Preferences.h>
#include <math.h>

#define WIFI_SSID     "YOUR_WIFI_SSID"
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"

#define FIREBASE_HOST "aquasheild-2e2ca-default-rtdb.asia-southeast1.firebasedatabase.app"
#define FIREBASE_AUTH "YOUR_FIREBASE_DATABASE_SECRET"

// Sensor Pins
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
Servo myServo;
unsigned long servoTimer = 0;
bool servoIsActive = false;

// Thermistor Constants
const float seriesResistor    = 4700.0;   // 4.7kΩ resistor from GPIO32 to GND
const float nominalResistance = 10000.0;  // 10kΩ NTC at 25°C
const float nominalTemp       = 25.0;     // °C
const float bCoefficient      = 3950.0;   // Beta value

#define VREF    3.3
#define ADC_RES 4095.0

FirebaseData   fbdo;
FirebaseAuth   auth;
FirebaseConfig config;

unsigned long lastUpload = 0;
#define UPLOAD_INTERVAL 1500

unsigned long lastHistoryUpload = 0;
#define HISTORY_INTERVAL 300000  // 5 minutes

// ---------------------------------------------------------------------------
// pH calibration -- fixed to vinegar (acid point) / baking soda (base point),
// the user's stated standard reference solutions. Same reference pH values
// already sourced/used in hardware/rebuild/01_ph_sensor/ph_calibration_tool/
// -- change these two lines (and re-flash) if you ever switch reference
// liquids; not exposed as a web input on purpose, since the user always uses
// the same two solutions.
// ---------------------------------------------------------------------------
const float CAL_PH_ACID = 2.4;   // plain white vinegar, 5% acidity
const float CAL_PH_BASE = 8.3;   // ~1 tsp baking soda dissolved in 1 cup water

Preferences prefs;

bool  phCalibrated       = false;
float calVoltageAcid     = NAN;   // in-memory, loaded from flash at boot
float calVoltageBase     = NAN;

float pendingVoltageAcid = NAN;   // captured-but-not-yet-saved points, this session
float pendingVoltageBase = NAN;

unsigned long lastPhLivePublish = 0;
#define PH_LIVE_INTERVAL 1000  // how often the live voltage is pushed to Firebase

unsigned long lastCalPoll = 0;
#define CAL_POLL_INTERVAL 500  // how often we check for a pending web command

// ---------------------------------------------------------------------------

void setup() {
  Serial.begin(115200);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  pinMode(PUMP1_PIN, OUTPUT);
  pinMode(PUMP2_PIN, OUTPUT);
  digitalWrite(PUMP1_PIN, HIGH);  // OFF
  digitalWrite(PUMP2_PIN, HIGH);  // OFF

  myServo.setPeriodHertz(50);
  myServo.attach(SERVO_PIN, 500, 2400);
  myServo.write(0);

  // Connect WiFi
  Serial.print("Connecting to WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("WiFi Connected!");
  Serial.println(WiFi.localIP());

  // Firebase Setup
  config.host = FIREBASE_HOST;
  config.signer.tokens.legacy_token = FIREBASE_AUTH;

  fbdo.setBSSLBufferSize(1024, 1024);
  fbdo.setResponseSize(1024);

  Firebase.begin(&config, &auth);
  Firebase.reconnectWiFi(true);

  // Initialize Firebase states
  Firebase.setBool(fbdo, "/pumps/pump1", false);
  Firebase.setBool(fbdo, "/pumps/pump2", false);
  Firebase.setBool(fbdo, "/servoTrigger", false);

  // Load any previously-saved pH calibration from flash (survives reboots
  // and re-uploading this same sketch -- same NVS keys as
  // ph_calibration_tool.ino, so a calibration saved from either place works).
  phCalibrated = loadPhCalibration(calVoltageAcid, calVoltageBase);
  Firebase.setString(fbdo, "/phCalibration/command", "");
  Firebase.setString(fbdo, "/phCalibration/status", phCalibrated ? "calibrated" : "uncalibrated");
  if (phCalibrated) {
    Serial.println("pH calibration loaded from flash.");
  } else {
    Serial.println("No saved pH calibration yet -- use the dashboard's pH calibration page.");
  }

  Serial.println("Aquaculture Sensor Suite V2 Online");
  delay(1000);
}

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
      Serial.println("Servo Triggered to 180!");
      myServo.write(180);
      servoTimer = millis();
      servoIsActive = true;
    }
  }

  if (servoIsActive && (millis() - servoTimer >= 3000)) {
    Serial.println("Servo Returning to 0...");
    myServo.write(0);
    servoIsActive = false;
    Firebase.setBool(fbdo, "/servoTrigger", false);
  }
}

float readTemperature() {
  int thermRaw = analogRead(THERM_PIN);

  if (thermRaw <= 0 || thermRaw >= 4095) {
    Serial.println("Temperature ADC out of range!");
    return NAN;
  }

  // FIXED (2026-08-12): was `seriesResistor * (thermRaw / (4095.0 - thermRaw))`
  // in the original reference sketch -- inverted for this wiring (thermistor
  // -> 3.3V, resistor -> GND). Silently reported ~57C at a real ~31C before
  // this fix. See hardware/rebuild/03_thermistor/.
  float resistance =
    seriesResistor * ((4095.0 - thermRaw) / (float)thermRaw);

  float steinhart = resistance / nominalResistance;
  steinhart = log(steinhart);
  steinhart /= bCoefficient;
  steinhart += 1.0 / (nominalTemp + 273.15);
  steinhart = 1.0 / steinhart;

  float tempC = steinhart - 273.15;

  return tempC;
}

// ---------------------------------------------------------------------------
// pH calibration -- Firebase-driven version of ph_calibration_tool.ino's
// 'a'/'b'/'s'/'c' commands. Same math, same flash format, different trigger
// (a /phCalibration/command string this sketch polls, instead of Serial).
// ---------------------------------------------------------------------------

float readPhVoltageAveraged(int samples) {
  long sum = 0;
  for (int i = 0; i < samples; i++) {
    sum += analogRead(PH_PIN);
    delay(10);
  }
  return (float)sum / samples * (VREF / ADC_RES);
}

bool loadPhCalibration(float &vAcid, float &vBase) {
  prefs.begin("phcal", true);  // read-only
  bool has = prefs.isKey("v_acid") && prefs.isKey("v_base");
  if (has) {
    vAcid = prefs.getFloat("v_acid", NAN);
    vBase = prefs.getFloat("v_base", NAN);
  }
  prefs.end();
  return has;
}

void savePhCalibration(float vAcid, float vBase) {
  prefs.begin("phcal", false);  // read-write
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

float voltageToPh(float voltage) {
  if (!phCalibrated) return NAN;  // caller must check phCalibrated first
  float slope = (CAL_PH_BASE - CAL_PH_ACID) / (calVoltageBase - calVoltageAcid);
  return CAL_PH_ACID + slope * (voltage - calVoltageAcid);
}

// Non-blocking: publishes the live raw pH voltage on a timer, so the
// dashboard's calibration page can show a live-updating reading while the
// probe is being moved between vinegar/baking soda -- same idea as
// ph_calibration_tool.ino's Serial "[live] raw voltage" line, just over
// Firebase instead.
void publishLivePhVoltage() {
  if (millis() - lastPhLivePublish < PH_LIVE_INTERVAL) return;
  lastPhLivePublish = millis();

  float v = readPhVoltageAveraged(5);  // light/quick, just for display
  Firebase.setFloat(fbdo, "/phCalibration/liveVoltage", v);
}

// Non-blocking: polls for a command written by the dashboard's pH
// calibration page and acts on it once, then clears the command so it
// doesn't re-trigger. Commands: "capture_acid", "capture_base", "save",
// "clear". Mirrors ph_calibration_tool.ino's a/b/s/c commands exactly.
void handlePhCalibration() {
  if (millis() - lastCalPoll < CAL_POLL_INTERVAL) return;
  lastCalPoll = millis();

  if (!Firebase.getString(fbdo, "/phCalibration/command")) return;
  String cmd = fbdo.stringData();
  if (cmd.length() == 0) return;  // nothing pending

  if (cmd == "capture_acid") {
    Serial.println("pH cal: capturing ACID (vinegar) point...");
    pendingVoltageAcid = readPhVoltageAveraged(60);  // heavier average, matches ph_calibration_tool.ino
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
        "Need both points captured first -- capture acid, then base, before saving.");
      Firebase.setString(fbdo, "/phCalibration/status", "error");
    } else if (fabs(pendingVoltageAcid - pendingVoltageBase) < 0.02) {
      Firebase.setString(fbdo, "/phCalibration/lastError",
        "The two captured voltages are almost identical -- probe likely didn't "
        "move between solutions, or wasn't rinsed/settled. Recapture both points.");
      Firebase.setString(fbdo, "/phCalibration/status", "error");
    } else {
      savePhCalibration(pendingVoltageAcid, pendingVoltageBase);
      // Update in-memory calibration immediately, so normal /sensor/ph
      // readings use it right away -- no reboot needed.
      calVoltageAcid = pendingVoltageAcid;
      calVoltageBase = pendingVoltageBase;
      phCalibrated = true;
      pendingVoltageAcid = NAN;
      pendingVoltageBase = NAN;
      Firebase.setString(fbdo, "/phCalibration/status", "saved");
      Firebase.setString(fbdo, "/phCalibration/lastError", "");
      // Same ".sv" (server value) trick already used for /history's
      // timestamp field below, just applied as the whole value here instead
      // of one nested field -- this is the proven pattern in this codebase,
      // not a separate/unverified API.
      FirebaseJson savedAtJson;
      savedAtJson.set(".sv", "timestamp");
      Firebase.setJSON(fbdo, "/phCalibration/lastSavedAt", savedAtJson);
      Serial.println("pH calibration saved to flash.");
    }

  } else if (cmd == "clear") {
    clearPhCalibration();
    calVoltageAcid = NAN;
    calVoltageBase = NAN;
    pendingVoltageAcid = NAN;
    pendingVoltageBase = NAN;
    phCalibrated = false;
    Firebase.setString(fbdo, "/phCalibration/status", "uncalibrated");
    Firebase.setString(fbdo, "/phCalibration/lastError", "");
    Serial.println("pH calibration cleared.");
  }

  Firebase.setString(fbdo, "/phCalibration/command", "");  // consumed
}

// ---------------------------------------------------------------------------

void loop() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH, 30000);
  float distance = duration * 0.034 / 2.0;

  controlPumps();
  handleServo();
  publishLivePhVoltage();
  handlePhCalibration();

  if (millis() - lastUpload >= UPLOAD_INTERVAL) {
    lastUpload = millis();

    float tempC = readTemperature();

    float tdsSum = 0;
    for (int i = 0; i < 30; i++) {
      tdsSum += analogRead(TDS_PIN);
      delay(10);
    }

    float tdsAvg = tdsSum / 30.0;
    float tdsVoltage = tdsAvg * VREF / ADC_RES;
    float compCoeff = 1.0 + 0.02 * ((isnan(tempC) ? 25.0 : tempC) - 25.0);
    float compV = tdsVoltage / compCoeff;

    float tdsValue =
        (133.42 * pow(compV, 3)
       - 255.86 * pow(compV, 2)
       + 857.39 * compV) * 0.5;

    float phVoltage = readPhVoltageAveraged(30);
    float phValue = phCalibrated ? voltageToPh(phVoltage) : NAN;

    Serial.println("-------------------------------");
    Serial.print("Temp     : ");
    if (isnan(tempC)) Serial.println("Invalid");
    else {
      Serial.print(tempC, 2);
      Serial.println(" C");
    }

    Serial.print("TDS      : ");
    Serial.print(tdsValue, 0);
    Serial.println(" ppm");

    Serial.print("Distance : ");
    Serial.print(distance, 1);
    Serial.println(" cm");

    Serial.print("pH       : ");
    if (isnan(phValue)) Serial.println("Not calibrated yet");
    else Serial.println(phValue, 2);
    Serial.println("-------------------------------");

    if (!isnan(tempC)) {
      Firebase.setFloat(fbdo, "/sensor/temp", tempC);
    }

    Firebase.setFloat(fbdo, "/sensor/tds", tdsValue);
    Firebase.setFloat(fbdo, "/sensor/waterLevel", distance);
    if (!isnan(phValue)) {
      Firebase.setFloat(fbdo, "/sensor/ph", phValue);
    }

    if (millis() - lastHistoryUpload >= HISTORY_INTERVAL ||
        lastHistoryUpload == 0) {

      lastHistoryUpload = millis();

      FirebaseJson jsonHistory;
      if (!isnan(tempC)) {
        jsonHistory.set("temp", tempC);
      }
      jsonHistory.set("tds", tdsValue);
      if (!isnan(phValue)) {
        jsonHistory.set("ph", phValue);
      }
      jsonHistory.set("level", distance);
      jsonHistory.set("timestamp/.sv", "timestamp");

      Firebase.pushJSON(fbdo, "/history", jsonHistory);
      Serial.println("5-Minute History Data Logged!");
    }
  }
}
