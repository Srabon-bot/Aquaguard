// Saved as-is from before the hardware was taken apart, for reference only.
// This is the END GOAL once every sensor has been re-added and tested one at a
// time (see hardware/rebuild/). Do not upload this yet -- start with
// hardware/rebuild/01_ph_sensor/ instead.
//
// KNOWN BUG (found 2026-08-12 while testing the thermistor standalone, see
// hardware/rebuild/03_thermistor/): readTemperature()'s resistance formula
// below is inverted for the wiring described in its own comment (thermistor
// ->3.3V, resistor->GND) -- it was silently reporting ~57C at a real ~31C
// room temperature. Apply the same fix used in
// hardware/rebuild/03_thermistor/03_thermistor.ino before reintegrating this
// sketch: swap to `seriesResistor * ((4095.0 - thermRaw) / thermRaw)`.
//
// REDACTED (2026-08-14): the real WiFi/Firebase credentials that were
// hardcoded here (an old, now-retired Firebase project) were replaced with
// placeholders below before this project went to a public GitHub repo -- fill
// in your own values, never commit real ones. See hardware/FIREBASE_SETUP.md
// for how to get a WIFI_SSID/PASSWORD and FIREBASE_HOST/AUTH for a new
// project. Prefer a build flag / untracked local header over editing this
// value in place, so a future commit can't accidentally re-expose it.

#include <WiFi.h>
#include <FirebaseESP32.h>
#include <ESP32Servo.h>
#include <math.h>

#define WIFI_SSID     "YOUR_WIFI_SSID"
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"

#define FIREBASE_HOST "YOUR_PROJECT-default-rtdb.firebaseio.com"
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
float ph_offset = 0.0;

FirebaseData   fbdo;
FirebaseAuth   auth;
FirebaseConfig config;

unsigned long lastUpload = 0;
#define UPLOAD_INTERVAL 1500

unsigned long lastHistoryUpload = 0;
#define HISTORY_INTERVAL 300000  // 5 minutes

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

  Serial.println("Aquaculture Sensor Suite V1 Online");
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

  float resistance =
    seriesResistor * ((float)thermRaw / (4095.0 - thermRaw));

  float steinhart = resistance / nominalResistance;
  steinhart = log(steinhart);
  steinhart /= bCoefficient;
  steinhart += 1.0 / (nominalTemp + 273.15);
  steinhart = 1.0 / steinhart;

  float tempC = steinhart - 273.15;

  return tempC;
}

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

    float phSum = 0;
    for (int i = 0; i < 30; i++) {
      phSum += analogRead(PH_PIN);
      delay(10);
    }

    float phAvg = phSum / 30.0;
    float phVoltage = phAvg * (3.3 / 4095.0);
    float phValue = (3.5 * phVoltage) + ph_offset;

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
    Serial.println(phValue, 2);
    Serial.println("-------------------------------");

    if (!isnan(tempC)) {
      Firebase.setFloat(fbdo, "/sensor/temp", tempC);
    }

    Firebase.setFloat(fbdo, "/sensor/tds", tdsValue);
    Firebase.setFloat(fbdo, "/sensor/waterLevel", distance);
    Firebase.setFloat(fbdo, "/sensor/ph", phValue);

    if (millis() - lastHistoryUpload >= HISTORY_INTERVAL ||
        lastHistoryUpload == 0) {

      lastHistoryUpload = millis();

      FirebaseJson jsonHistory;
      if (!isnan(tempC)) {
        jsonHistory.set("temp", tempC);
      }
      jsonHistory.set("tds", tdsValue);
      jsonHistory.set("ph", phValue);
      jsonHistory.set("level", distance);
      jsonHistory.set("timestamp/.sv", "timestamp");

      Firebase.pushJSON(fbdo, "/history", jsonHistory);
      Serial.println("5-Minute History Data Logged!");
    }
  }
}
