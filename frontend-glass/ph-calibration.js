// ============================================================================
// AquaGuard — pH calibration page.
//
// Talks directly to the Firebase Realtime Database over plain REST calls (no
// SDK, no build step — same "no bundler" philosophy as app.js), reading and
// writing the /phCalibration/* paths that
// hardware/rebuild/07_full_reintegration/AquaGuard_v2.ino's handlePhCalibration()
// polls and updates. See that sketch's header comment for the full protocol.
//
// FIREBASE_BASE_URL is NOT a secret (Firebase client config is meant to be
// public — the Realtime Database's security RULES are what protect it, see
// hardware/FIREBASE_SETUP.md) — safe to fill in directly here.
// ============================================================================

const FIREBASE_BASE_URL = "https://aquasheild-2e2ca-default-rtdb.asia-southeast1.firebasedatabase.app";

const POLL_INTERVAL_MS = 2000;

// ---------------------------------------------------------------------------
// Theme (match whatever the user last picked on the main dashboard --
// this page has no toggle of its own, just follows the saved preference).
// ---------------------------------------------------------------------------
(function initTheme() {
  const saved = localStorage.getItem("aquaguard-theme");
  if (saved) document.documentElement.setAttribute("data-theme", saved);
})();

// ---------------------------------------------------------------------------
// Plain Firebase REST helpers
// ---------------------------------------------------------------------------
async function fbGet(path) {
  const res = await fetch(`${FIREBASE_BASE_URL}/${path}.json`);
  if (!res.ok) throw new Error(`Firebase GET ${path} failed: HTTP ${res.status}`);
  return res.json();
}

async function fbPut(path, value) {
  const res = await fetch(`${FIREBASE_BASE_URL}/${path}.json`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(value),
  });
  if (!res.ok) throw new Error(`Firebase PUT ${path} failed: HTTP ${res.status}`);
  return res.json();
}

function isConfigured() {
  return !FIREBASE_BASE_URL.includes("YOUR_PROJECT");
}

// ---------------------------------------------------------------------------
// Status rendering
// ---------------------------------------------------------------------------
const STATUS_LABEL = {
  uncalibrated: "Not calibrated yet",
  idle: "Ready",
  acid_captured: "Acid point captured — now capture the base point",
  base_captured: "Base point captured — now capture the acid point",
  both_captured: "Both points captured — ready to save",
  saved: "Calibration saved ✓",
  calibrated: "Calibrated (loaded from flash)",
  error: "Error — see message below",
};
const STATUS_CLASS = {
  uncalibrated: "warning",
  idle: "warning",
  acid_captured: "warning",
  base_captured: "warning",
  both_captured: "good",
  saved: "good",
  calibrated: "good",
  error: "critical",
};

function renderStatus(data) {
  const out = document.getElementById("calStatusResult");
  if (!data) {
    out.innerHTML = `<div class="empty-state">No data yet — waiting for the ESP32 to publish its first reading.</div>`;
    return;
  }

  const status = data.status || "uncalibrated";
  const statusClass = STATUS_CLASS[status] ?? "warning";
  const statusLabel = STATUS_LABEL[status] ?? status;

  const liveV = typeof data.liveVoltage === "number" ? `${data.liveVoltage.toFixed(3)} V` : "—";
  const acidV = typeof data.capturedAcidV === "number" ? `${data.capturedAcidV.toFixed(4)} V` : "not captured";
  const baseV = typeof data.capturedBaseV === "number" ? `${data.capturedBaseV.toFixed(4)} V` : "not captured";

  out.innerHTML = `
    <div class="horizon-row">
      <span class="horizon-label">status</span>
      <span class="status-chip ${statusClass}">${escapeHtml(statusLabel)}</span>
    </div>
    <div class="horizon-row">
      <span class="horizon-label">live voltage</span>
      <span class="horizon-detail">${liveV}</span>
    </div>
    <div class="horizon-row">
      <span class="horizon-label">acid point (vinegar)</span>
      <span class="horizon-detail">${acidV} → pH 2.4</span>
    </div>
    <div class="horizon-row">
      <span class="horizon-label">base point (baking soda)</span>
      <span class="horizon-detail">${baseV} → pH 8.3</span>
    </div>`;

  const msg = document.getElementById("calActionMessage");
  if (data.lastError) {
    msg.textContent = data.lastError;
    msg.style.display = "block";
  } else {
    msg.style.display = "none";
  }

  // Save is only meaningful once both points are captured this session.
  document.getElementById("saveCalBtn").disabled = status !== "both_captured";
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

// ---------------------------------------------------------------------------
// Polling
// ---------------------------------------------------------------------------
let pollFailures = 0;

async function poll() {
  try {
    const data = await fbGet("phCalibration");
    renderStatus(data);
    pollFailures = 0;
  } catch (e) {
    pollFailures += 1;
    if (pollFailures === 1) {
      // Only replace the panel on the FIRST failure, not every failed poll --
      // avoids the display flickering back to an error message between two
      // otherwise-successful reads if one single request happens to drop.
      document.getElementById("calStatusResult").innerHTML =
        `<div class="error-box">Couldn't reach Firebase: ${escapeHtml(e.message)}. Retrying…</div>`;
    }
  }
}

// ---------------------------------------------------------------------------
// Actions
// ---------------------------------------------------------------------------
async function sendCommand(command, button) {
  const original = button.textContent;
  button.disabled = true;
  button.textContent = "Sending…";
  try {
    await fbPut("phCalibration/command", command);
    // The ESP32 polls every ~500ms and clears the command once handled;
    // the next regular poll() (every 2s) will pick up the resulting status.
  } catch (e) {
    document.getElementById("calActionMessage").textContent = `Couldn't send command: ${e.message}`;
    document.getElementById("calActionMessage").style.display = "block";
  } finally {
    button.textContent = original;
    button.disabled = false;
  }
}

document.getElementById("captureAcidBtn").addEventListener("click", (e) => sendCommand("capture_acid", e.currentTarget));
document.getElementById("captureBaseBtn").addEventListener("click", (e) => sendCommand("capture_base", e.currentTarget));
document.getElementById("saveCalBtn").addEventListener("click", (e) => sendCommand("save", e.currentTarget));
document.getElementById("clearCalBtn").addEventListener("click", (e) => sendCommand("clear", e.currentTarget));

// ---------------------------------------------------------------------------
// Boot
// ---------------------------------------------------------------------------
if (!isConfigured()) {
  document.getElementById("calStatusResult").innerHTML = `
    <div class="error-box">
      This page isn't wired up yet — open <code>ph-calibration.js</code> and set
      <code>FIREBASE_BASE_URL</code> to your Firebase project's databaseURL.
      See <code>hardware/FIREBASE_SETUP.md</code>.
    </div>`;
} else {
  ["captureAcidBtn", "captureBaseBtn", "clearCalBtn"].forEach(id => {
    document.getElementById(id).disabled = false;
  });
  poll();
  setInterval(poll, POLL_INTERVAL_MS);
}
