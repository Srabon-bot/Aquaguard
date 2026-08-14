// ============================================================================
// AquaGuard rebuild -- Step 4 of 7: TDS sensor ONLY (water quality)
// ============================================================================
// No WiFi, no Firebase, no other sensors -- just this one part. Add the next
// sensor only after this one prints sane, stable TDS numbers.
//
// WIRING (see hardware/Hardware_Wiring_Guide.pdf Part 3, Step 3.4 for the
// full writeup -- this is the same GPIO35 used there):
//   TDS module VCC        -> ESP32 3.3V   <-- NOT 5V, see warning below
//   TDS module GND        -> ESP32 GND
//   TDS module Signal/AOUT -> ESP32 GPIO 35
//
// !! SAFETY: power this module from 3.3V, not 5V !!
// Same reasoning as the pH sensor: GPIO35 is an ESP32 "input-only" pin with
// no built-in over-voltage protection. Most of these TDS modules support a
// 3.3-5V supply range -- using 3.3V keeps the analog output physically
// incapable of exceeding 3.3V, which is what GPIO35 can safely read.
//
// TEMPERATURE COMPENSATION: TDS readings drift with water temperature, so
// real TDS meters correct for it. This standalone sketch assumes a fixed
// 25C (a reasonable room-temperature default) since the thermistor isn't
// necessarily wired at the same time. Once both the thermistor (Step 3) and
// this sensor are wired together in the final combined sketch, the real
// measured temperature will be used instead -- see
// hardware/original_reference/AquaGuard_full_original.ino.
// ============================================================================

#include <math.h>

#define TDS_PIN 35
const float VREF    = 3.3;
const float ADC_RES = 4095.0;
const float ASSUMED_TEMP_C = 25.0;  // see temperature compensation note above

void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println();
  Serial.println("=== AquaGuard rebuild: Step 4 - TDS sensor standalone test ===");
  Serial.println("Reading TDS once per second (assumes 25C for temperature compensation).");
  Serial.println("Sanity check: dry probe in air should read low/noisy near-zero.");
  Serial.println("Dip in plain tap water -- number should rise and settle within a");
  Serial.println("few seconds. Add a pinch of salt to the water and stir -- it should");
  Serial.println("rise noticeably further (more dissolved solids = higher reading).");
  Serial.println();
}

float readTdsPpm() {
  long sum = 0;
  for (int i = 0; i < 30; i++) {
    sum += analogRead(TDS_PIN);
    delay(10);
  }
  float avgRaw = sum / 30.0;
  float voltage = avgRaw * VREF / ADC_RES;

  // Standard temperature compensation for this class of TDS sensor module
  // (0.02 = 2% per degree C, referenced to 25C) -- this is the module
  // manufacturer's published formula, not something derived for this project.
  float compCoeff = 1.0 + 0.02 * (ASSUMED_TEMP_C - 25.0);
  float compVoltage = voltage / compCoeff;

  // Manufacturer's calibration polynomial (Gravity-style analog TDS sensor).
  float tds = (133.42 * pow(compVoltage, 3)
             - 255.86 * pow(compVoltage, 2)
             + 857.39 * compVoltage) * 0.5;

  return tds;
}

void loop() {
  float tds = readTdsPpm();

  Serial.print("TDS: ");
  Serial.print(tds, 0);
  Serial.println(" ppm");

  delay(1000);
}
