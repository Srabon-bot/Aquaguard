// ============================================================================
// AquaGuard rebuild -- Step 2 of 7: Ultrasonic sensor ONLY (water level)
// ============================================================================
// No WiFi, no Firebase, no other sensors -- just this one part. Add the next
// sensor only after this one prints sane, stable distance numbers.
//
// WIRING (see hardware/Hardware_Wiring_Guide.pdf Part 3, Step 3.2 for the
// full writeup -- this is the same GPIO5/GPIO18 used there):
//   HC-SR04 VCC  -> ESP32 5V   (this sensor needs 5V, not 3.3V, to work reliably)
//   HC-SR04 GND  -> ESP32 GND
//   HC-SR04 TRIG -> ESP32 GPIO 5
//   HC-SR04 ECHO -> ESP32 GPIO 18   <-- THROUGH A VOLTAGE DIVIDER, see below
//
// !! SAFETY: do NOT wire ECHO straight to GPIO18 !!
// ECHO outputs a 5V pulse, but ESP32 GPIOs only tolerate 3.3V. Put a 1kOhm
// resistor in series between ECHO and GPIO18, then a 2kOhm resistor from
// that same GPIO18 point down to GND:
//
//   ECHO ---[1k]---+--- GPIO18
//                   |
//                 [2k]
//                   |
//                  GND
//
// This drops the 5V pulse to roughly 3.3V before it reaches the ESP32.
// ============================================================================

#define TRIG_PIN 5
#define ECHO_PIN 18

const unsigned long ECHO_TIMEOUT_US = 30000;  // ~30ms round trip == ~5m max range

void setup() {
  Serial.begin(115200);
  delay(500);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  digitalWrite(TRIG_PIN, LOW);

  Serial.println();
  Serial.println("=== AquaGuard rebuild: Step 2 - Ultrasonic sensor standalone test ===");
  Serial.println("Reading distance once per second.");
  Serial.println("Sanity check: hold a hand/object at a KNOWN distance (use a ruler or");
  Serial.println("tape measure) directly in front of the sensor and confirm the reading");
  Serial.println("roughly matches -- within a centimeter or two is normal.");
  Serial.println();
}

// Returns distance in cm, or -1 if no echo was received (out of range,
// nothing to reflect off, or a wiring problem).
float readDistanceCm() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH, ECHO_TIMEOUT_US);
  if (duration == 0) {
    return -1;
  }
  return duration * 0.034 / 2.0;  // speed of sound ~0.034 cm/us, round trip halved
}

void loop() {
  float distance = readDistanceCm();

  if (distance < 0) {
    Serial.println("No echo received -- object may be out of range (>~4-5m),");
    Serial.println("angled away from the sensor, or check the TRIG/ECHO wiring.");
  } else {
    Serial.print("Distance: ");
    Serial.print(distance, 1);
    Serial.println(" cm");
  }

  delay(500);
}
