// ============================================================================
// AquaGuard rebuild -- pH sensor CALIBRATION TOOL
// ============================================================================
// Interactive two-point calibration over Serial. Run this once (or whenever
// you want to recalibrate). It saves the result to the ESP32's internal
// flash (NVS via the Preferences library), so it survives power cycles and
// re-uploading other sketches -- 01_ph_sensor.ino (the normal-use sketch)
// reads it automatically on boot, no manual editing/reflashing needed.
//
// WIRING: identical to 01_ph_sensor.ino -- see that sketch's header comment
// or hardware/rebuild/01_ph_sensor/README.md before running this. Same
// warning applies: pH module VCC -> ESP32 3.3V, NOT 5V.
//
// HOW TO USE
//   1. Upload this sketch. Open Serial Monitor, baud 115200, line ending set
//      to "Newline" (so typed commands are actually sent when you hit Enter).
//   2. Rinse the probe, dip it in the ACID reference (plain white vinegar).
//      Watch the "[live] raw voltage" lines settle (stop drifting), then
//      type  a  and press Enter.
//   3. Rinse the probe, dip it in the BASE reference (~1 tsp baking soda
//      dissolved in 1 cup water). Wait for it to settle, then type  b  and
//      press Enter.
//   4. Type  s  and press Enter to compute and save the calibration.
//   5. Optional sanity check: rinse the probe, dip it in a third liquid
//      (e.g. plain tap water), and type  t  to see live pH using the
//      calibration you just saved -- should land somewhere between your two
//      reference points.
//   6. When done, upload 01_ph_sensor.ino for normal use -- it will load this
//      saved calibration automatically.
// ============================================================================

#include <Preferences.h>
#include <math.h>

#define PH_PIN 34
const float VREF    = 3.3;
const float ADC_RES = 4095.0;

// Reference pH of each kitchen solution -- see README.md for why these values
// and how to prepare them. Change these two lines if you use different
// reference liquids, before capturing points.
const float CAL_PH_ACID = 2.4;   // plain white vinegar, 5% acidity
const float CAL_PH_BASE = 8.3;   // ~1 tsp baking soda dissolved in 1 cup water

Preferences prefs;

float capturedVoltageAcid = NAN;
float capturedVoltageBase = NAN;

unsigned long lastPrint = 0;
const unsigned long PRINT_INTERVAL = 700;

String inputLine = "";

float readPhVoltageAveraged(int samples) {
  long sum = 0;
  for (int i = 0; i < samples; i++) {
    sum += analogRead(PH_PIN);
    delay(20);
  }
  float avgRaw = (float)sum / samples;
  return avgRaw * (VREF / ADC_RES);
}

void printHelp() {
  Serial.println();
  Serial.println("=== pH calibration commands ===");
  Serial.println("  a  -> capture current reading as the ACID (vinegar) point");
  Serial.println("  b  -> capture current reading as the BASE (baking soda) point");
  Serial.println("  s  -> compute + save calibration to flash (needs both points captured)");
  Serial.println("  t  -> show live pH using whatever calibration is currently saved");
  Serial.println("  c  -> clear saved calibration from flash");
  Serial.println("  h  -> show this help again");
  Serial.println("================================");
  Serial.println();
}

bool loadSavedCalibration(float &vAcid, float &vBase) {
  prefs.begin("phcal", true);  // read-only
  bool has = prefs.isKey("v_acid") && prefs.isKey("v_base");
  if (has) {
    vAcid = prefs.getFloat("v_acid", NAN);
    vBase = prefs.getFloat("v_base", NAN);
  }
  prefs.end();
  return has;
}

void saveCalibration(float vAcid, float vBase) {
  prefs.begin("phcal", false);  // read-write
  prefs.putFloat("v_acid", vAcid);
  prefs.putFloat("v_base", vBase);
  prefs.putFloat("ph_acid", CAL_PH_ACID);
  prefs.putFloat("ph_base", CAL_PH_BASE);
  prefs.end();
}

void clearCalibration() {
  prefs.begin("phcal", false);
  prefs.clear();
  prefs.end();
}

float voltageToPh(float voltage, float vAcid, float phAcid, float vBase, float phBase) {
  float slope = (phBase - phAcid) / (vBase - vAcid);
  return phAcid + slope * (voltage - vAcid);
}

void handleCommand(String cmd) {
  cmd.trim();
  cmd.toLowerCase();

  if (cmd == "a") {
    Serial.println("Capturing ACID point... hold the probe steady in the vinegar.");
    capturedVoltageAcid = readPhVoltageAveraged(60);
    Serial.print("Captured ACID voltage: ");
    Serial.print(capturedVoltageAcid, 4);
    Serial.println(" V");

  } else if (cmd == "b") {
    Serial.println("Capturing BASE point... hold the probe steady in the baking soda solution.");
    capturedVoltageBase = readPhVoltageAveraged(60);
    Serial.print("Captured BASE voltage: ");
    Serial.print(capturedVoltageBase, 4);
    Serial.println(" V");

  } else if (cmd == "s") {
    if (isnan(capturedVoltageAcid) || isnan(capturedVoltageBase)) {
      Serial.println("Need BOTH points captured first -- use 'a' then 'b'.");
      return;
    }
    if (fabs(capturedVoltageAcid - capturedVoltageBase) < 0.02) {
      Serial.println("WARNING: the two captured voltages are almost identical.");
      Serial.println("That usually means the probe didn't actually move between");
      Serial.println("solutions, or wasn't rinsed/settled. Not saving -- recapture");
      Serial.println("both points before trying again.");
      return;
    }

    saveCalibration(capturedVoltageAcid, capturedVoltageBase);

    Serial.println();
    Serial.println("Saved to flash. Calibration summary:");
    Serial.print("  Acid point : "); Serial.print(capturedVoltageAcid, 4);
    Serial.print(" V  ->  pH "); Serial.println(CAL_PH_ACID, 2);
    Serial.print("  Base point : "); Serial.print(capturedVoltageBase, 4);
    Serial.print(" V  ->  pH "); Serial.println(CAL_PH_BASE, 2);
    Serial.println("01_ph_sensor.ino will pick this up automatically on next boot.");
    Serial.println("Try 't' now to preview live pH with a third liquid (e.g. tap water).");
    Serial.println();

  } else if (cmd == "t") {
    float vAcid, vBase;
    if (!loadSavedCalibration(vAcid, vBase)) {
      Serial.println("No saved calibration yet -- run 'a', 'b', then 's' first.");
      return;
    }
    float v = readPhVoltageAveraged(30);
    float ph = voltageToPh(v, vAcid, CAL_PH_ACID, vBase, CAL_PH_BASE);
    Serial.print("Live voltage: "); Serial.print(v, 3);
    Serial.print(" V  ->  pH: "); Serial.println(ph, 2);

  } else if (cmd == "c") {
    clearCalibration();
    capturedVoltageAcid = NAN;
    capturedVoltageBase = NAN;
    Serial.println("Saved calibration cleared from flash.");

  } else if (cmd == "h" || cmd == "") {
    printHelp();

  } else {
    Serial.print("Unknown command: '");
    Serial.print(cmd);
    Serial.println("' -- type 'h' for the command list.");
  }
}

void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println();
  Serial.println("=== AquaGuard pH sensor calibration tool ===");

  float vAcid, vBase;
  if (loadSavedCalibration(vAcid, vBase)) {
    Serial.println("Found an existing saved calibration:");
    Serial.print("  Acid point : "); Serial.print(vAcid, 4); Serial.println(" V");
    Serial.print("  Base point : "); Serial.print(vBase, 4); Serial.println(" V");
    Serial.println("(Running 'a' + 'b' + 's' again below will overwrite this.)");
  } else {
    Serial.println("No saved calibration found yet.");
  }

  printHelp();
}

void loop() {
  // Non-blocking: keep printing live raw voltage while also listening for commands.
  if (millis() - lastPrint >= PRINT_INTERVAL) {
    lastPrint = millis();
    float v = readPhVoltageAveraged(5);
    Serial.print("[live] raw voltage: ");
    Serial.print(v, 3);
    Serial.println(" V");
  }

  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (inputLine.length() > 0) {
        handleCommand(inputLine);
        inputLine = "";
      }
    } else {
      inputLine += c;
    }
  }
}
