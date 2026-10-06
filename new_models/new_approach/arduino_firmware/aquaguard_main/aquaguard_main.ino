#include <WiFi.h>
#include <HTTPClient.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// ==========================================
// CONFIGURATION & PINOUT (ESP32 Example)
// ==========================================

// WiFi Credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// API Settings
const char* fast_api_endpoint = "http://YOUR_SERVER_IP:8000/api/v1/iot-ingest";
const char* firebase_endpoint = "https://aquasheild-2e2ca-default-rtdb.asia-southeast1.firebasedatabase.app/sensor.json";

// Pin Definitions
#define PH_PIN 34           // Analog pin for pH Sensor
#define TDS_PIN 35          // Analog pin for TDS Sensor
#define ONE_WIRE_BUS 4      // Digital pin for DS18B20 Temp Sensor
#define TRIG_PIN 5          // Digital pin for Ultrasonic Trig
#define ECHO_PIN 18         // Digital pin for Ultrasonic Echo

// Calibration Variables
float ph_calib_value = 21.34;
float tds_factor = 0.5;
float total_tank_height_cm = 100.0; // Adjust for your tank/pond depth

// Initialization
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

// ==========================================
// SETUP
// ==========================================
void setup() {
  Serial.begin(115200);
  
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  sensors.begin();
  
  setup_wifi();
}

void setup_wifi() {
  delay(10);
  Serial.println("\nConnecting to WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
}

// ==========================================
// SENSOR READING FUNCTIONS
// ==========================================

float read_ph() {
  int sensorValue = analogRead(PH_PIN);
  float voltage = sensorValue * (3.3 / 4095.0);
  return 3.5 * voltage + ph_calib_value; 
}

float read_tds(float temperature) {
  int sensorValue = analogRead(TDS_PIN);
  float voltage = sensorValue * (3.3 / 4095.0);
  float compCoeff = 1.0 + 0.02 * (temperature - 25.0);
  float compVolt = voltage / compCoeff;
  return (133.42 * pow(compVolt, 3) - 255.86 * pow(compVolt, 2) + 857.39 * compVolt) * tds_factor;
}

float read_temperature() {
  sensors.requestTemperatures(); 
  return sensors.getTempCByIndex(0);
}

float read_water_level() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  long duration = pulseIn(ECHO_PIN, HIGH);
  float distance_cm = duration * 0.034 / 2;
  
  // Frontend expects waterLevel, meaning how full it is
  float waterLevel = total_tank_height_cm - distance_cm;
  return max(0.0f, waterLevel);
}

// ==========================================
// MAIN LOOP
// ==========================================
void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    setup_wifi();
  }

  // 1. Read Sensors
  float tempC = read_temperature();
  float ph = read_ph();
  float tds = read_tds(tempC);
  float water_level = read_water_level();
  float distance_cm = total_tank_height_cm - water_level;

  // 2. Format JSON for FastAPI (ML Models expect these keys)
  String fastApiPayload = "{";
  fastApiPayload += "\"temperature\":" + String(tempC) + ",";
  fastApiPayload += "\"ph\":" + String(ph) + ",";
  fastApiPayload += "\"tds\":" + String(tds) + ",";
  fastApiPayload += "\"water_distance_cm\":" + String(distance_cm);
  fastApiPayload += "}";

  // 3. Format JSON for Firebase (Frontend Dashboard expects these keys)
  String firebasePayload = "{";
  firebasePayload += "\"temp\":" + String(tempC) + ",";
  firebasePayload += "\"ph\":" + String(ph) + ",";
  firebasePayload += "\"tds\":" + String(tds) + ",";
  firebasePayload += "\"waterLevel\":" + String(water_level);
  firebasePayload += "}";

  HTTPClient http;

  // --- SEND TO FASTAPI (Machine Learning Backend) ---
  Serial.println("Sending to FastAPI...");
  http.begin(fast_api_endpoint);
  http.addHeader("Content-Type", "application/json");
  int code1 = http.POST(fastApiPayload);
  Serial.println("FastAPI Code: " + String(code1));
  http.end();

  // --- SEND TO FIREBASE (Web Dashboard) ---
  Serial.println("Sending to Firebase...");
  http.begin(firebase_endpoint);
  http.addHeader("Content-Type", "application/json");
  int code2 = http.PUT(firebasePayload); // PUT replaces the /sensor object
  Serial.println("Firebase Code: " + String(code2));
  http.end();

  // Wait 60 seconds
  delay(60000);
}
