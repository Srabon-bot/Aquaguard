// ============================================================================
// AquaGuard — analytics page.
//
// Reads Firebase's /history path (a snapshot pushed every ~5 minutes by
// hardware/AquaGuard_v2/AquaGuard_v2.ino: temp, tds, ph, level, timestamp)
// over plain REST, buckets it into Day/Week/Month views client-side, and
// draws 4 simple hand-rolled SVG charts (avg line + min/max dashed band) --
// no charting library, same "no build step" approach as the rest of this
// site.
// ============================================================================

const FIREBASE_BASE_URL = "https://aquasheild-2e2ca-default-rtdb.asia-southeast1.firebasedatabase.app";

// ---------------------------------------------------------------------------
// Theme (match whatever the user last picked on the main dashboard).
// ---------------------------------------------------------------------------
(function initTheme() {
  const saved = localStorage.getItem("aquaguard-theme");
  if (saved) document.documentElement.setAttribute("data-theme", saved);
})();

// ---------------------------------------------------------------------------
// Period definitions -- how many history records to fetch, how to bucket
// them, and how to label each bucket on the x-axis.
// ---------------------------------------------------------------------------
const HOUR_MS = 3600 * 1000;
const DAY_MS = 24 * HOUR_MS;

const PERIODS = {
  day: {
    limitToLast: 320,          // ~24h at one push every ~5 min, plus buffer
    bucketCount: 24,
    bucketMs: HOUR_MS,
    labelFor: (bucketIndex, bucketCount) => {
      const hourAgo = bucketCount - 1 - bucketIndex;
      const d = new Date(Date.now() - hourAgo * HOUR_MS);
      return d.getHours().toString().padStart(2, "0") + ":00";
    },
  },
  week: {
    limitToLast: 2100,         // ~7 days
    bucketCount: 7,
    bucketMs: DAY_MS,
    labelFor: (bucketIndex, bucketCount) => {
      const daysAgo = bucketCount - 1 - bucketIndex;
      const d = new Date(Date.now() - daysAgo * DAY_MS);
      return d.toLocaleDateString(undefined, { weekday: "short" });
    },
  },
  month: {
    limitToLast: 8800,         // ~30 days
    bucketCount: 30,
    bucketMs: DAY_MS,
    labelFor: (bucketIndex, bucketCount) => {
      const daysAgo = bucketCount - 1 - bucketIndex;
      const d = new Date(Date.now() - daysAgo * DAY_MS);
      return d.getDate().toString();
    },
  },
};

const SENSOR_KEYS = ["ph", "tds", "temp", "level"];
const FIREBASE_KEY_FOR = { ph: "ph", tds: "tds", temp: "temp", level: "level" };

let currentPeriod = "day";

// ---------------------------------------------------------------------------
// Fetch + bucket
// ---------------------------------------------------------------------------
async function fetchHistory(period) {
  const cfg = PERIODS[period];
  const orderBy = encodeURIComponent('"$key"');
  const url = `${FIREBASE_BASE_URL}/history.json?orderBy=${orderBy}&limitToLast=${cfg.limitToLast}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Firebase GET /history failed: HTTP ${res.status}`);
  const data = await res.json();
  if (!data) return [];
  // data is an object keyed by Firebase push IDs -- order doesn't matter
  // here, bucketing below places each record by its own timestamp.
  return Object.values(data).filter(r => typeof r?.timestamp === "number");
}

function aggregate(values) {
  if (!values.length) return null;
  return {
    avg: values.reduce((a, b) => a + b, 0) / values.length,
    min: Math.min(...values),
    max: Math.max(...values),
  };
}

function bucketRecords(records, period) {
  const cfg = PERIODS[period];
  const now = Date.now();
  const raw = Array.from({ length: cfg.bucketCount }, () => ({ ph: [], tds: [], temp: [], level: [] }));

  for (const rec of records) {
    const age = now - rec.timestamp;
    const bucketIndex = cfg.bucketCount - 1 - Math.floor(age / cfg.bucketMs);
    if (bucketIndex < 0 || bucketIndex >= cfg.bucketCount) continue;
    for (const key of SENSOR_KEYS) {
      const v = rec[FIREBASE_KEY_FOR[key]];
      if (typeof v === "number") raw[bucketIndex][key].push(v);
    }
  }

  return raw.map((bucket, i) => ({
    label: cfg.labelFor(i, cfg.bucketCount),
    stats: Object.fromEntries(SENSOR_KEYS.map(key => [key, aggregate(bucket[key])])),
  }));
}

// ---------------------------------------------------------------------------
// Chart rendering -- plain SVG, no library. Avg as a solid line, min/max as
// thin dashed lines around it. X-axis labels are thinned out so they don't
// overlap on narrow screens; y-axis just shows the range's min/max value.
// ---------------------------------------------------------------------------
const CHART_FORMAT = {
  ph:    v => v.toFixed(2),
  tds:   v => Math.round(v).toString(),
  temp:  v => `${v.toFixed(1)}°C`,
  level: v => `${v.toFixed(1)}cm`,
};

function renderChart(key, buckets) {
  const svg = document.getElementById(`chart-${key}`);
  const statsEl = document.getElementById(`stats-${key}`);
  const W = 600, H = 180, padL = 40, padR = 12, padT = 14, padB = 22;
  const plotW = W - padL - padR, plotH = H - padT - padB;

  const withData = buckets.map((b, i) => ({ i, stats: b.stats[key] })).filter(b => b.stats);

  if (!withData.length) {
    svg.innerHTML = `<text x="${W / 2}" y="${H / 2}" text-anchor="middle" class="chart-empty-text">No data yet for this period</text>`;
    statsEl.textContent = "";
    return;
  }

  const allVals = withData.flatMap(b => [b.stats.min, b.stats.max]);
  let lo = Math.min(...allVals), hi = Math.max(...allVals);
  if (lo === hi) { lo -= 1; hi += 1; }
  const pad = (hi - lo) * 0.12;
  lo -= pad; hi += pad;

  const xFor = i => padL + (buckets.length === 1 ? plotW / 2 : (i / (buckets.length - 1)) * plotW);
  const yFor = v => padT + plotH - ((v - lo) / (hi - lo)) * plotH;

  const fmt = CHART_FORMAT[key];
  const line = (field) => withData.map(b => `${xFor(b.i).toFixed(1)},${yFor(b.stats[field]).toFixed(1)}`).join(" ");

  const xLabelStep = Math.max(1, Math.ceil(buckets.length / 8)); // avoid label crowding
  const xLabels = buckets
    .map((b, i) => (i % xLabelStep === 0 ? `<text x="${xFor(i).toFixed(1)}" y="${H - 6}" text-anchor="middle" class="chart-axis-text">${escapeHtml(b.label)}</text>` : ""))
    .join("");

  svg.innerHTML = `
    <text x="${padL - 6}" y="${yFor(hi) + 3}" text-anchor="end" class="chart-axis-text">${fmt(hi)}</text>
    <text x="${padL - 6}" y="${yFor(lo) + 3}" text-anchor="end" class="chart-axis-text">${fmt(lo)}</text>
    <polyline class="chart-max-line" points="${line("max")}" />
    <polyline class="chart-min-line" points="${line("min")}" />
    <polyline class="chart-avg-line" points="${line("avg")}" />
    ${xLabels}`;

  const latest = withData[withData.length - 1].stats;
  statsEl.textContent = `latest avg ${fmt(latest.avg)} · range ${fmt(latest.min)}–${fmt(latest.max)}`;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

// ---------------------------------------------------------------------------
// Boot / period switching
// ---------------------------------------------------------------------------
async function loadPeriod(period) {
  currentPeriod = period;
  ["day", "week", "month"].forEach(p => {
    document.getElementById(`period${p[0].toUpperCase()}${p.slice(1)}`).classList.toggle("primary", p === period);
  });

  const status = document.getElementById("analyticsStatus");
  status.textContent = "Loading history…";

  try {
    const records = await fetchHistory(period);
    const buckets = bucketRecords(records, period);
    SENSOR_KEYS.forEach(key => renderChart(key, buckets));
    status.textContent = records.length
      ? `${records.length} history record(s) loaded.`
      : "No history yet — the device needs to run for a while before charts have data (a snapshot is pushed every 5 minutes).";
  } catch (e) {
    status.textContent = `Couldn't load history: ${e.message}`;
  }
}

["day", "week", "month"].forEach(period => {
  document.getElementById(`period${period[0].toUpperCase()}${period.slice(1)}`)
    .addEventListener("click", () => loadPeriod(period));
});

loadPeriod(currentPeriod);
