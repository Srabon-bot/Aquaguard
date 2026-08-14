// ============================================================================
// AquaGuard rebuild -- Step 5 of 7: Relay module (2 pumps/motors) ONLY
// ============================================================================
// No WiFi, no Firebase, no other sensors -- just this one part.
//
// This test deliberately does NOT require real pumps wired up yet. It just
// cycles both relays on/off automatically so you can see the relay LEDs
// light and hear them click. Only connect real pumps to the relay's output
// side (COM/NO/NC terminals) AFTER you've confirmed this basic clicking
// behaves correctly -- see Part 2 of the README before wiring pumps.
//
// WIRING (see hardware/Hardware_Wiring_Guide.pdf Part 3, Step 3.6 for the
// full writeup -- this is the same GPIO25/GPIO26 used there):
//   Relay module VCC -> ESP32 5V   (most relay modules need 5V to reliably switch)
//   Relay module GND -> ESP32 GND
//   Relay IN1        -> ESP32 GPIO 25   (controls pump/motor 1)
//   Relay IN2        -> ESP32 GPIO 26   (controls pump/motor 2)
//
// !! DO NOT connect pump motors to the ESP32's 5V/3.3V pins, ever !!
// Pumps draw far more current than the ESP32 can safely supply. They connect
// through the relay's OTHER side (COM/NO/NC screw terminals) to their own
// external power supply, sharing only a common GND with the ESP32. See the
// README for the full pump-wiring diagram once you get to that stage.
//
// ACTIVE LOW: this code assumes GPIO LOW = relay ON, which is the default
// for most hobbyist relay modules. If the relay LEDs light up when this code
// thinks it's turning them OFF (and vice versa), your module is active-HIGH
// instead -- swap HIGH/LOW in the two digitalWrite() calls below.
// ============================================================================

#define PUMP1_PIN 25
#define PUMP2_PIN 26

const unsigned long ON_TIME_MS  = 2000;
const unsigned long OFF_TIME_MS = 2000;

void setup() {
  Serial.begin(115200);
  delay(500);

  pinMode(PUMP1_PIN, OUTPUT);
  pinMode(PUMP2_PIN, OUTPUT);
  digitalWrite(PUMP1_PIN, HIGH);  // OFF (active LOW)
  digitalWrite(PUMP2_PIN, HIGH);  // OFF (active LOW)

  Serial.println();
  Serial.println("=== AquaGuard rebuild: Step 5 - Relay standalone test ===");
  Serial.println("No pumps should be connected to the relay outputs yet.");
  Serial.println("Cycling relay 1, then relay 2, on/off automatically.");
  Serial.println("Watch/listen for each relay's LED and click.");
  Serial.println();
}

void pulseRelay(int pin, const char *label) {
  Serial.print(label);
  Serial.println(": ON");
  digitalWrite(pin, LOW);   // active LOW = ON
  delay(ON_TIME_MS);

  Serial.print(label);
  Serial.println(": OFF");
  digitalWrite(pin, HIGH);  // active LOW = OFF
  delay(OFF_TIME_MS);
}

void loop() {
  pulseRelay(PUMP1_PIN, "Relay 1 (pump 1)");
  pulseRelay(PUMP2_PIN, "Relay 2 (pump 2)");
}
