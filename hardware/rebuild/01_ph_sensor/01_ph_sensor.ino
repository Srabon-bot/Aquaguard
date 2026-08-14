// ============================================================================
// AquaGuard rebuild -- Step 1 of 7: pH sensor ONLY (normal-use sketch)
// ============================================================================
// No WiFi, no Firebase, no other sensors -- just this one part, so a wiring
// or calibration mistake is obvious immediately instead of hiding inside the
// full multi-sensor sketch. Add the next sensor only after this one prints
// sane, stable pH numbers.
//
// CALIBRATION: this sketch does NOT calibrate itself. Run
// ph_calibration_tool/ph_calibration_tool.ino FIRST (see that file's header,
// or README.md) -- it saves the calibration to the ESP32's flash, and this
// sketch reads it automatically on boot. If you re-upload this sketch later,
// the saved calibration is still there; you only need to rerun the
// calibration tool if you want to recalibrate.
//
// WIRING (see hardware/Hardware_Wiring_Guide.pdf Part 3 for the full pin
// reference table -- this is the same GPIO34 used there):
//   pH module "-"  (GND)  -> ESP32 GND
//   pH module "+"  (VCC)  -> ESP32 3.3V   <-- NOT 5V, see warning below
//   pH module "Po" (out)  -> ESP32 GPIO 34
//   pH module "Do" and "To" pins -> leave unconnected
//
// !! SAFETY: do NOT power this module from 5V while Po is wired to GPIO34 !!
// GPIO34 is an ESP32 "input-only" pin with no built-in over-voltage
// protection. At 5V supply the module's Po output can approach 5V, which can
// permanently damage that pin. Powering the module from 3.3V keeps Po
// physically incapable of exceeding 3.3V.
// ============================================================================

#include <Preferences.h>

#define PH_PIN 34
const float VREF    = 3.3;
const float ADC_RES = 4095.0;

Preferences prefs;

float calVoltageAcid = NAN;
float calPhAcid       = NAN;
float calVoltageBase  = NAN;
float calPhBase        = NAN;
bool calibrated = false;

void loadCalibration() {
  prefs.begin("phcal", true);  // read-only
  calibrated = prefs.isKey("v_acid") && prefs.isKey("v_base");
  if (calibrated) {
    calVoltageAcid = prefs.getFloat("v_acid", NAN);
    calVoltageBase = prefs.getFloat("v_base", NAN);
    calPhAcid      = prefs.getFloat("ph_acid", NAN);
    calPhBase      = prefs.getFloat("ph_base", NAN);
  }
  prefs.end();
}

float readPhVoltage() {
  long sum = 0;
  for (int i = 0; i < 30; i++) {
    sum += analogRead(PH_PIN);
    delay(10);
  }
  float avgRaw = sum / 30.0;
  return avgRaw * (VREF / ADC_RES);
}

float voltageToPh(float voltage) {
  // straight line through the two calibration points (y = pH, x = voltage)
  float slope = (calPhBase - calPhAcid) / (calVoltageBase - calVoltageAcid);
  return calPhAcid + slope * (voltage - calVoltageAcid);
}

void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println();
  Serial.println("=== AquaGuard rebuild: Step 1 - pH sensor standalone test ===");

  loadCalibration();

  if (calibrated) {
    Serial.println("Status: CALIBRATED (loaded from flash) - showing live pH below.");
    Serial.print("  Acid point : "); Serial.print(calVoltageAcid, 4);
    Serial.print(" V -> pH "); Serial.println(calPhAcid, 2);
    Serial.print("  Base point : "); Serial.print(calVoltageBase, 4);
    Serial.print(" V -> pH "); Serial.println(calPhBase, 2);
  } else {
    Serial.println("Status: NOT CALIBRATED YET - showing raw voltage only.");
    Serial.println("Upload and run ph_calibration_tool/ph_calibration_tool.ino first,");
    Serial.println("then come back to this sketch -- it will pick up the saved");
    Serial.println("calibration automatically.");
  }
  Serial.println();
}

void loop() {
  float voltage = readPhVoltage();

  Serial.print("Raw voltage: ");
  Serial.print(voltage, 3);
  Serial.print(" V");

  if (calibrated) {
    float ph = voltageToPh(voltage);
    Serial.print("   ->   pH: ");
    Serial.println(ph, 2);
  } else {
    Serial.println("   (not calibrated yet -- see ph_calibration_tool/)");
  }

  delay(1000);
}
