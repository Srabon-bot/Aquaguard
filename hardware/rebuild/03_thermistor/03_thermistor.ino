// ============================================================================
// AquaGuard rebuild -- Step 3 of 7: Thermistor ONLY (temperature)
// ============================================================================
// No WiFi, no Firebase, no other sensors -- just this one part. Add the next
// sensor only after this one prints sane, stable temperature numbers.
//
// WIRING (see hardware/Hardware_Wiring_Guide.pdf Part 3, Step 3.3 for the
// full writeup -- this is the same GPIO32 used there):
//
//   3.3V ---[ NTC Thermistor ]--- GPIO32 ---[ 4.7kOhm resistor ]--- GND
//
//   - One leg of the thermistor -> ESP32 3.3V
//   - Other leg of the thermistor -> ESP32 GPIO32, AND -> one leg of the 4.7k resistor
//   - Other leg of the 4.7k resistor -> ESP32 GND
//
// No voltage divider/safety concern here like the ultrasonic or pH sensors --
// this is a low-voltage passive component, nothing exceeds 3.3V.
//
// GETTING THE DIRECTION RIGHT: if the reading goes DOWN when the room gets
// warmer (or climbs when you'd expect it to drop), the thermistor and
// resistor are most likely swapped -- double check which leg goes to 3.3V
// vs GND.
// ============================================================================

#include <math.h>

#define THERM_PIN 32

const float SERIES_RESISTOR     = 4700.0;   // 4.7kOhm resistor, GPIO32 to GND
const float NOMINAL_RESISTANCE  = 10000.0;  // 10kOhm NTC at 25 C (check your thermistor's datasheet if unsure)
const float NOMINAL_TEMP        = 25.0;     // C
const float B_COEFFICIENT       = 3950.0;   // Beta value (check datasheet if unsure)

void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println();
  Serial.println("=== AquaGuard rebuild: Step 3 - Thermistor standalone test ===");
  Serial.println("Reading temperature once per second.");
  Serial.println("Sanity check: should read roughly room temperature (~20-30 C).");
  Serial.println("Hold the thermistor between two fingers -- it should climb within");
  Serial.println("a few seconds as body heat warms it.");
  Serial.println();
}

// Returns temperature in Celsius, or NAN if the ADC reading is out of a
// plausible range (0 or fully saturated usually means a wiring problem).
float readTemperatureC() {
  int thermRaw = analogRead(THERM_PIN);

  if (thermRaw <= 0 || thermRaw >= 4095) {
    return NAN;
  }

  // NOTE: numerator/denominator swapped vs. the original AquaGuard sketch --
  // that version's formula was only correct for the OPPOSITE wiring
  // (resistor->3.3V, thermistor->GND). For the wiring actually documented
  // here (thermistor->3.3V, resistor->GND), it must be inverted like this,
  // otherwise readings come out badly wrong (e.g. reporting ~57C at room
  // temperature). Verified against this sketch's own readings on 2026-08-12.
  float resistance = SERIES_RESISTOR * ((4095.0 - (float)thermRaw) / (float)thermRaw);

  float steinhart = resistance / NOMINAL_RESISTANCE;
  steinhart = log(steinhart);
  steinhart /= B_COEFFICIENT;
  steinhart += 1.0 / (NOMINAL_TEMP + 273.15);
  steinhart = 1.0 / steinhart;

  return steinhart - 273.15;
}

void loop() {
  float tempC = readTemperatureC();

  if (isnan(tempC)) {
    Serial.println("Temperature ADC out of range -- check wiring (thermistor/resistor legs, GPIO32 connection).");
  } else {
    Serial.print("Temperature: ");
    Serial.print(tempC, 2);
    Serial.println(" C");
  }

  delay(1000);
}
