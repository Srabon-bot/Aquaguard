// ============================================================================
// AquaGuard rebuild -- Step 6 of 7: Servo ONLY
// ============================================================================
// No WiFi, no Firebase, no other sensors -- just this one part, same pattern
// as every other step in this folder. New sketch (the servo step didn't have
// a standalone test yet -- see hardware/HARDWARE_LOG.md, "Servo -- not yet
// built").
//
// This sweeps the servo back and forth automatically (0 degrees -> 180
// degrees -> 0 degrees, repeating) so you can confirm it's wired correctly
// and moves smoothly across its full range, before wiring it into the main
// combined sketch (../AquaGuard_v2.ino), where it's instead triggered by a
// Firebase boolean (/servoTrigger) rather than sweeping automatically.
//
// WIRING (see hardware/Hardware_Wiring_Guide.pdf for the full reference --
// same GPIO13 used there):
//   Servo signal (usually orange/yellow wire) -> ESP32 GPIO 13
//   Servo power (red)                          -> 5V (NOT the ESP32's 3.3V --
//                                                 most hobby servos need 5V
//                                                 and more current than the
//                                                 3.3V rail can supply)
//   Servo ground (brown/black)                 -> ESP32 GND (shared ground,
//                                                 even though power comes
//                                                 from a separate 5V source)
//
// !! If the servo twitches or resets the ESP32 when it moves, that's a
// power-supply/current problem, not a wiring-position problem -- most small
// hobby servos draw a brief current spike when starting to move that a
// USB-only power source can't always supply cleanly. Power the servo from
// the same external 5V supply the pumps use (see hardware/rebuild/
// 05_relay_pumps/), not from the ESP32 board itself, if you see this.
// ============================================================================

#include <ESP32Servo.h>

#define SERVO_PIN 13

Servo myServo;

void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println();
  Serial.println("=== AquaGuard rebuild: Step 6 - Servo standalone test ===");
  Serial.println("Sweeping 0 -> 180 -> 0 degrees, repeating.");
  Serial.println();

  myServo.setPeriodHertz(50);
  myServo.attach(SERVO_PIN, 500, 2400);
  myServo.write(0);
  delay(1000);  // let it settle at the start position before sweeping
}

void sweepTo(int targetAngle, int stepDelayMs) {
  static int currentAngle = 0;
  int step = (targetAngle > currentAngle) ? 1 : -1;

  while (currentAngle != targetAngle) {
    currentAngle += step;
    myServo.write(currentAngle);
    delay(stepDelayMs);
  }

  Serial.print("Reached ");
  Serial.print(targetAngle);
  Serial.println(" degrees.");
}

void loop() {
  sweepTo(180, 15);
  delay(800);
  sweepTo(0, 15);
  delay(800);
}
