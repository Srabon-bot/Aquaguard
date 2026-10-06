# AquaGuard Hardware Assembly & Testing To-Do List

This document outlines the remaining steps to fully assemble and test the AquaGuard hardware project, continuing from the completed pH sensor calibration.

## Phase 1: Sensor & Component Wiring (ESP32 Pinout)
*Note: Make sure your ESP32 is unplugged from power/USB before wiring. Reference `hardware/AquaGuard_v2/AquaGuard_v2.ino`.*

- [ ] **Step 1: Connect pH Sensor**
  - **VCC:** Connect to ESP32 **3.3V** (or 5V if using a logic level converter).
  - **GND:** Connect to ESP32 **GND**.
  - **Signal (PO/A0):** Connect to ESP32 **Pin 34**.
  - **Expectation:** pH sensor module board lights up when powered.

- [ ] **Step 2: Connect TDS Sensor**
  - **VCC:** Connect to ESP32 **3.3V**.
  - **GND:** Connect to ESP32 **GND**.
  - **Signal (A):** Connect to ESP32 **Pin 35**.
  - **Expectation:** TDS probe is securely attached to its module board.

- [ ] **Step 3: Connect NTC Thermistor (Temperature)**
  - **Wiring:** Connect one leg of the 10kΩ NTC Thermistor to ESP32 **3.3V**. Connect the other leg to ESP32 **Pin 32**.
  - **Pull-down Resistor:** Connect a **4.7kΩ resistor** from **Pin 32** to **GND** (creating a voltage divider).
  - **Expectation:** Securely wired; thermistor is ready for ADC reading.

- [ ] **Step 4: Connect HC-SR04 Ultrasonic Sensor (Water Level)**
  - **VCC:** Connect to ESP32 **5V (VIN)**.
  - **GND:** Connect to ESP32 **GND**.
  - **TRIG:** Connect to ESP32 **Pin 5**.
  - **ECHO:** Connect to ESP32 **Pin 18**. *(Note: Use a voltage divider: place a 1kΩ resistor from Echo to Pin 18, and a 2kΩ resistor from Pin 18 to GND to protect the 3.3V ESP32 pin).*
  - **Expectation:** Sensor is wired safely without risking 5V logic damage.

## Phase 2: Actuator & Power Wiring
- [ ] **Step 5: Connect Pump Relays**
  - **Drain Pump (PUMP1):** Connect the relay signal pin to ESP32 **Pin 25**.
  - **Refill Pump (PUMP2):** Connect the relay signal pin to ESP32 **Pin 26**.
  - **Expectation:** Both relays click when pulled LOW by the ESP32.

- [ ] **Step 6: Connect Feeder Servo**
  - **Signal:** Connect to ESP32 **Pin 13**.
  - **Power:** Connect to the 5V rail (VIN or separate step-down).
  - **Expectation:** Servo is ready for 50Hz PWM control.

- [ ] **Step 7: Connect Power Supply**
  - **Details:** Ensure the 5V rail powers the Pumps, Servo, and HC-SR04, while the ESP32 internally regulates 3.3V for the pH and TDS sensors.
  - **Expectation:** System boots stably without resetting when pumps activate.

## Phase 3: Firmware & Unit Testing
- [ ] **Step 8: Upload Firmware**
  - **Details:** Flash `hardware/AquaGuard_v2/AquaGuard_v2.ino` to the ESP32.
  - **Pre-requisite:** Update `WIFI_SSID`, `WIFI_PASSWORD`, and `FIREBASE_AUTH` inside the `.ino` file.
  - **Expectation:** MCU connects to WiFi and authenticates with Firebase.

- [ ] **Step 9: Sensor & Actuator Unit Testing**
  - **Details:** Submerge probes. Trigger pump and feeder functions via the Firebase dashboard (`ph-calibration.html` and `index.html`).
  - **Expectation:** Live telemetry uploads to Firebase every 1.5s, and actuators respond to Firebase commands.

## Phase 4: Final Deployment
- [ ] **Step 10: Enclosure & Waterproofing**
  - **Details:** Secure the ESP32 and relays inside an IP67 enclosure. Route cables through waterproof glands.
  - **Expectation:** System is watertight and safe for field deployment.
