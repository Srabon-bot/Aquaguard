# Aquaguard Hardware Assembly & Testing To-Do List

This document outlines the remaining steps to fully assemble and test the Aquaguard hardware project, continuing from the completed pH sensor calibration.

## Phase 1: Sensor & Component Wiring (ESP32 Pinout)
*Note: Make sure your ESP32 is unplugged from power/USB before wiring.*

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

- [ ] **Step 3: Connect Turbidity Sensor**
  - **VCC:** Connect to ESP32 **5V (VIN)** (Turbidity modules often require 5V to operate correctly, ensure the analog output doesn't exceed 3.3V, or use a voltage divider).
  - **GND:** Connect to ESP32 **GND**.
  - **Signal (A0):** Connect to ESP32 **Pin 32**.
  - **Expectation:** Turbidity module toggle switch is set to "Analog" (A) mode, not Digital (D).

- [ ] **Step 4: Connect DS18B20 Temperature Sensor**
  - **VCC (Red Wire):** Connect to ESP32 **3.3V**.
  - **GND (Black Wire):** Connect to ESP32 **GND**.
  - **Data (Yellow Wire):** Connect to ESP32 **Pin 4**.
  - **Important:** Place a **4.7kΩ resistor** between the VCC (Red) and Data (Yellow) wires as a pull-up.
  - **Expectation:** Securely wired with the pull-up resistor in place so the OneWire bus can read it.

- [ ] **Step 5: Connect HC-SR04 Ultrasonic Sensor (Water Level)**
  - **VCC:** Connect to ESP32 **5V (VIN)**.
  - **GND:** Connect to ESP32 **GND**.
  - **TRIG:** Connect to ESP32 **Pin 5**.
  - **ECHO:** Connect to ESP32 **Pin 18**. *(Note: HC-SR04 outputs a 5V signal on Echo. To protect the 3.3V ESP32 Pin 18, use a voltage divider: place a 1kΩ resistor from Echo to Pin 18, and a 2kΩ resistor from Pin 18 to GND).*
  - **Expectation:** Sensor is wired safely without risking 5V logic damage to the ESP32.

## Phase 2: Power System Assembly
- [ ] **Step 6: Connect Power Supply**
  - **Details:** If deploying in the field, connect your 18650 Battery Pack / Solar Charge Controller to the ESP32's **VIN** (5V input) or battery terminal if you have a custom development board. Connect GNDs together.
  - **Expectation:** The system powers on reliably without USB connection to a computer. LED indicators on the MCU and sensors should light up.

## Phase 3: Firmware & Unit Testing
- [ ] **Step 7: Upload Main Firmware**
  - **Details:** Flash `aquaguard_main.ino` to the ESP32. Remember to update your WiFi credentials and MQTT broker IP in the code before uploading.
  - **Expectation:** The MCU successfully boots, connects to WiFi, and initializes all sensors without errors in the serial monitor.
- [ ] **Step 8: Sensor Unit Testing**
  - **Details:** Submerge the sensor probes (pH, TDS, temp, turbidity) in tap water. Open the Serial Monitor (115200 baud).
  - **Expectation:** The serial monitor displays valid JSON payloads with reasonable, stable readings for all parameters simultaneously.
- [ ] **Step 9: Communication Test**
  - **Details:** Verify that the data payloads are successfully arriving at your MQTT broker (you can use MQTT Explorer to check the `aquaguard/telemetry` topic).
  - **Expectation:** Real-time data streams into your backend for your ML models to consume.

## Phase 4: Enclosure & Waterproofing
- [ ] **Step 10: Mount Components in Enclosure**
  - **Details:** Secure the ESP32, power supply, and module boards inside an IP67/IP68 waterproof enclosure. Use standoffs to prevent short circuits.
  - **Expectation:** All internal electronics are firmly mounted and do not rattle.
- [ ] **Step 11: Route Probes & Waterproof Cable Glands**
  - **Details:** Pass the sensor probes through cable glands on the enclosure. Tighten the glands to ensure a watertight seal. Apply marine-grade silicone sealant if necessary.
  - **Expectation:** Probes are outside the box, but the entry points are completely sealed against moisture.

## Phase 5: Full System Field Test
- [ ] **Step 12: Dry Run (Bench Test)**
  - **Details:** Run the fully sealed unit on your desk for 24 hours. Monitor data transmission stability and battery consumption.
  - **Expectation:** The device operates continuously without dropping offline or crashing.
- [ ] **Step 13: Controlled Water Test**
  - **Details:** Place the enclosed device over a bucket or sink. Submerge only the sensor probes. Move the water level up and down below the ultrasonic sensor.
  - **Expectation:** The system accurately detects water level changes and transmits valid water quality data. The enclosure remains completely dry inside.
- [ ] **Step 14: Final Deployment**
  - **Details:** Install the Aquaguard unit at the target location. Secure the enclosure above the maximum expected flood line and submerge the probes.
  - **Expectation:** The system goes live, streaming real-world environmental data to your flood and anomaly models.
