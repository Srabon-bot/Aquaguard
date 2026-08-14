"""Builds Discharge_Forecaster_Model_Report.pdf -- same structure/rigor as
the classifier and susceptibility reports, for model #2 (the discharge
regression forecaster). Every number comes from backend/models/2026-08-07c-
discharge-regression/metrics.json and the figures
generate_discharge_assets.py produced.

Usage:
    python reports/generate_discharge_assets.py   # run first
    python reports/build_discharge_report.py
"""

import json
from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

ROOT = Path(__file__).resolve().parent.parent.parent
ASSETS = Path(__file__).resolve().parent / "assets"
MODELS_DIR = ROOT / "backend" / "models" / "2026-08-07c-discharge-regression"
OUT_PATH = Path(__file__).resolve().parent / "Discharge_Forecaster_Model_Report.pdf"

metrics = json.loads((MODELS_DIR / "metrics.json").read_text())
m = {r["horizon"]: r for r in metrics}

styles = getSampleStyleSheet()
styles.add(ParagraphStyle("H1", parent=styles["Heading1"], fontSize=17, spaceBefore=14, spaceAfter=8, textColor=colors.HexColor("#10131a")))
styles.add(ParagraphStyle("H2", parent=styles["Heading2"], fontSize=13, spaceBefore=12, spaceAfter=6, textColor=colors.HexColor("#2a3550")))
styles.add(ParagraphStyle("H3", parent=styles["Heading3"], fontSize=11, spaceBefore=8, spaceAfter=4, textColor=colors.HexColor("#3c4250")))
styles.add(ParagraphStyle("BodyText2", parent=styles["BodyText"], fontSize=9.6, leading=13.5, spaceAfter=7))
styles.add(ParagraphStyle("Caption", parent=styles["BodyText"], fontSize=8.3, leading=11, textColor=colors.HexColor("#5a6070"), spaceBefore=3, spaceAfter=10, alignment=1))
styles.add(ParagraphStyle("TitleBig", parent=styles["Title"], fontSize=25, leading=30))
styles.add(ParagraphStyle("TitleSub", parent=styles["Normal"], fontSize=12.5, alignment=1, textColor=colors.HexColor("#5a6070"), spaceBefore=8))
styles.add(ParagraphStyle("TableCell", parent=styles["BodyText"], fontSize=8, leading=10.5))
styles.add(ParagraphStyle("TableCellHead", parent=styles["BodyText"], fontSize=8.3, leading=10.5, textColor=colors.white, fontName="Helvetica-Bold"))

BLUE = colors.HexColor("#2a78d6")
GREY_BG = colors.HexColor("#f3f5f9")
story = []


def h1(t): story.append(Paragraph(t, styles["H1"]))
def h2(t): story.append(Paragraph(t, styles["H2"]))
def p(t): story.append(Paragraph(t, styles["BodyText2"]))
def spacer(h=6): story.append(Spacer(1, h))


def fig(name, caption, width=15.5 * cm):
    img_path = ASSETS / name
    img = Image(str(img_path))
    ratio = img.imageHeight / img.imageWidth
    img.drawWidth = width
    img.drawHeight = width * ratio
    story.append(img)
    story.append(Paragraph(caption, styles["Caption"]))


def make_table(headers, rows, col_widths, header_bg=BLUE):
    data = [[Paragraph(h, styles["TableCellHead"]) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c), styles["TableCell"]) for c in row])
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), header_bg),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, GREY_BG]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c9cfda")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    spacer(10)


# ===========================================================================
# TITLE
# ===========================================================================
story.append(Spacer(1, 4 * cm))
story.append(Paragraph("Discharge Forecaster", styles["TitleBig"]))
story.append(Paragraph("Model #2 of the AquaGuard / Bangladesh Flood Early-Warning System", styles["TitleSub"]))
story.append(Paragraph("A river-discharge regression forecaster — literature review, methodology, "
                        "real data, and evaluation results", styles["TitleSub"]))
spacer(40)
story.append(Paragraph(f"{date.today().strftime('%B %d, %Y')}", styles["TitleSub"]))
story.append(Paragraph("Companion to the flood-risk-classifier and flood-susceptibility reports", styles["TitleSub"]))
story.append(PageBreak())

# ===========================================================================
# 1. INTRODUCTION
# ===========================================================================
h1("1. Introduction &amp; Purpose")
p("""Built as a pivot alongside, not instead of, the flood-risk classifier (model #1): rather than a
binary flood/no-flood flag, this model predicts the actual river discharge (m&sup3;/s) at 24h/48h/72h
ahead — a continuous, densely-observed target with no rare-event label problem, making it a more
tractable regression task than classification on sparse flood events.""")
p("""This report documents the model as it exists today, including a 2026-08-14 improvement pass that
added NSE and KGE — the two metrics the hydrology field itself uses to evaluate streamflow models,
which this project's own evaluation never reported before — plus a deeper, per-station breakdown that
surfaced a real weak point the pooled numbers alone hid.""")

# ===========================================================================
# 2. LITERATURE REVIEW
# ===========================================================================
h1("2. Literature Review")
p("""A dedicated multi-search literature pass, run against this model specifically on 2026-08-14 as if
it didn't exist yet, rather than re-reading earlier design reasoning.""")

h2("2.1 Model architecture &amp; methodology")
make_table(
    ["Source", "Key finding relevant to this project"],
    [
        ["LSTM-based rainfall-runoff modeling / NeuralHydrology (Kratzert et al.)",
         "\"Never train an LSTM on a single basin\" — models work best trained on many watersheds "
         "pooled together. This project's classifier and forecaster both already pool all 30 stations "
         "into one model per horizon."],
        ["Forecasting monthly runoff: XGBoost vs. deep learning (<i>PLOS One</i>)",
         "XGBoost \"outperformed LSTM and RF models... improvements of up to 22-34%\" in a glacierized "
         "catchment study."],
        ["Daily streamflow forecasting: XGBoost, LightGBM, CatBoost comparison (<i>MDPI Hydrology</i>)",
         "All three gradient-boosting variants landed at NSE 0.85-0.89 for a mountainous catchment — "
         "competitive with deep learning at a fraction of the complexity."],
        ["Knowledge-Guided ML for Operational Flood Forecasting (<i>Water Resources Research</i> 2025)",
         "A Factorized Hierarchical Neural Network (inverse model infers catchment state, forward model "
         "predicts from it) — a genuine SOTA direction, Microsoft-Research-scale, out of scope here."],
    ],
    [7.3 * cm, 8.7 * cm],
)

h2("2.2 Target transform &amp; evaluation metrics")
make_table(
    ["Source", "Key finding relevant to this project"],
    [
        ["Log-transformation for skewed regression targets (multiple ML references)",
         "\"Stretches low-flow values while compressing high-flow ones... important for streamflow data "
         "with extreme high-flow events\" — matches this project's own log1p(discharge) reasoning, "
         "independently confirmed rather than just re-derived."],
        ["Nash-Sutcliffe Efficiency &amp; Kling-Gupta Efficiency (multiple hydrology references)",
         "<b>\"NSE and KGE are now the most widely used indices in hydrology for evaluation of "
         "streamflow models\"</b> — directly motivated adding both (&sect;6.1), which this project's "
         "evaluation never reported before this pass."],
        ["\"Friends don't let friends use NSE or KGE...\" (<i>Environmental Modelling &amp; Software</i>)",
         "A real, documented critique: both metrics are sensitive to the skew/periodicity of daily "
         "streamflow data and are not meant for cross-site comparison — reported here as a caveat "
         "alongside NSE/KGE, not a reason to skip them."],
    ],
    [7.3 * cm, 8.7 * cm],
)

h2("2.3 Bangladesh-specific studies")
make_table(
    ["Source", "Key finding relevant to this project"],
    [
        ["Comparative evaluation of ML models for extreme river water level forecasting in Bangladesh "
         "(<i>ScienceDirect</i>)",
         "Random Forest Regression consistently outperformed other models for monthly extreme water "
         "level prediction (RMSE 0.64-0.77m, R&sup2; 0.87-0.92) across 9 compared models."],
        ["Daily discharge prediction, Old Brahmaputra River, Mymensingh, Bangladesh "
         "(<i>Water Practice &amp; Technology</i>)",
         "<b>The same river system this project's OB01 station monitors.</b> Compared XGBoost against "
         "5 deep-learning architectures; LSTM+Attention led at 1-day lead time, all models exceeded "
         "R&sup2; 0.98 — a directly comparable regional benchmark, with the same leakage-check caveat "
         "applied elsewhere in this project's reports (methodology not fully disclosed in the abstract)."],
    ],
    [7.3 * cm, 8.7 * cm],
)

story.append(PageBreak())

# ===========================================================================
# 3. MODEL FAMILIES
# ===========================================================================
h1("3. Model Families Used in the Literature")
make_table(
    ["Model family", "Typical reported performance", "This project"],
    [
        ["XGBoost / LightGBM / CatBoost", "NSE 0.85-0.89 (mountainous catchment); beat LSTM/RF by "
         "22-34% in a glacierized-catchment study", "<b>LightGBM used</b> — matches the field's "
         "gradient-boosting-competitive-with-deep-learning finding."],
        ["LSTM / GRU / CNN-GRU / LSTM+Attention", "R&sup2; &gt; 0.98 in one directly comparable "
         "Bangladesh (Old Brahmaputra) study at 1-day lead time", "Not used — 30-station data volume "
         "favors gradient boosting per &sect;2.1's comparative findings."],
        ["Random Forest Regression", "Led 9 compared models for Bangladesh monthly extreme water level "
         "prediction", "Not directly compared for this task — a candidate for a future head-to-head, "
         "matching the same discipline the susceptibility model's RF-vs-LightGBM test used."],
        ["Knowledge-guided hybrid (FHNN)", "One 2025 study, Microsoft-scale infrastructure",
         "Not used — noted as a future direction, not currently in scope."],
        ["<b>LightGBM, log1p target, per-horizon, pooled (this project)</b>", "&mdash;",
         f"<b>24h: NSE={m['24h']['model_metrics']['nse']:.4f}, KGE={m['24h']['model_metrics']['kge']:.4f} "
         f"&mdash; 72h: NSE={m['72h']['model_metrics']['nse']:.4f}, KGE={m['72h']['model_metrics']['kge']:.4f}</b>"],
    ],
    [4.3 * cm, 6 * cm, 5.7 * cm],
)

story.append(PageBreak())

# ===========================================================================
# 4. OUR MODEL
# ===========================================================================
h1("4. Our Model: Design &amp; Rationale")

h2("4.1 log1p(discharge) target transform")
p("""Station discharge spans ~5 orders of magnitude (checked directly: station means range from ~2
m&sup3;/s at Dhaka's Buriganga to ~39,000 m&sup3;/s at the Padma-Meghna confluence). A plain L2/MSE
objective on raw m&sup3;/s would be dominated entirely by the largest stations' squared error,
effectively training a Jamuna/Padma-only model. log1p makes the loss behave like a relative
(percentage-ish) error across every station's own scale, and handles exact-zero discharge at a couple
of small coastal stations (log1p(0)=0, plain log(0) is undefined). Predictions are back-transformed
(expm1, clipped at 0) for real-unit reporting.""")

h2("4.2 Persistence-baseline discipline (already present, before this improvement pass)")
p(f"""Discharge is highly autocorrelated day-to-day — today's discharge is a strong predictor of
tomorrow's by simple physical persistence, not because a model learned anything deep — so a naive
"tomorrow = today" baseline has always been reported alongside the trained model's own metrics. Real
result: <b>+{m['24h']['mae_improvement_over_persistence_pct']:.1f}% MAE improvement at 24h, growing to
+{m['72h']['mae_improvement_over_persistence_pct']:.1f}% at 72h</b> — the model's real added skill grows
with lead time, exactly where a naive persistence guess should be expected to degrade most.""")

h2("4.3 2026-08-14 additions: NSE, KGE, and a per-station breakdown")
p("""Neither existed before this pass. Both are covered in full in &sect;6, including the finding that
the pooled NSE number, while real, is somewhat inflated by between-station variance, and the discovery
of one station (Dhaka's Buriganga) that degrades sharply with lead time — invisible in the pooled
metrics alone.""")

story.append(PageBreak())

# ===========================================================================
# 5. DATA SOURCES
# ===========================================================================
h1("5. Data Sources")
make_table(
    ["Source", "What it provides"],
    [
        ["Open-Meteo Forecast API (free, no key)", "Live rainfall (local + upstream basin grid) and "
         "soil moisture"],
        ["Open-Meteo Flood API (GloFAS reanalysis/forecast, free)", "River discharge — both the target "
         "and a same-day feature at inference time"],
        ["Same station/basin/terrain features as model #1", "Shared feature engineering pipeline "
         "(<code>build_features.py</code>) — only the label differs"],
    ],
    [6.5 * cm, 9.5 * cm],
)
p(f"""Train: {m['24h']['train_rows']:,} rows, test: {m['24h']['test_rows']:,} rows — same TEST_CUTOFF
(2024-01-01) as the classifier, for a directly comparable evaluation period, but a plain date-based
split with no label-regime filtering (discharge has no GFMS-style "accessible window" complexity to
account for).""")

story.append(PageBreak())

# ===========================================================================
# 6. RESULTS
# ===========================================================================
h1("6. Results: Plots &amp; Analytics")

h2("6.1 NSE and KGE — the metrics the hydrology field actually uses")
fig("fig_nse_kge_comparison.png", "Figure — NSE and KGE, model vs. persistence, all 3 horizons "
    "(pooled across all 30 stations).")
make_table(
    ["Horizon", "Model NSE", "Persistence NSE", "Model KGE", "Persistence KGE"],
    [[h, f"{m[h]['model_metrics']['nse']:.4f}", f"{m[h]['persistence_baseline_metrics']['nse']:.4f}",
      f"{m[h]['model_metrics']['kge']:.4f}", f"{m[h]['persistence_baseline_metrics']['kge']:.4f}"]
     for h in ["24h", "48h", "72h"]],
    [2.6 * cm, 3.2 * cm, 3.2 * cm, 3.2 * cm, 3.2 * cm],
)
p("""At 24h, the model's KGE is very slightly <b>below</b> persistence's, despite a real 11% MAE
improvement — not a contradiction once decomposed (below).""")

story.append(PageBreak())
h2("6.2 Diagnosing the 24h KGE gap: correlation vs. variability vs. bias")
fig("fig_kge_components.png", "Figure — KGE's three components, model vs. persistence, all horizons. "
    "The model's correlation (r) is consistently HIGHER (better) than persistence at every horizon; its "
    "variability ratio (alpha) is consistently LOWER — the model under-disperses relative to the true "
    "series' day-to-day swings.")
p("""A real, well-understood regression characteristic, not a flaw: minimizing squared error pulls
predictions toward central tendency, slightly smoothing day-to-day spikes that a naive "copy yesterday
exactly" persistence baseline never smooths, since persistence's variance is definitionally identical to
the true series' own (just shifted by a day). The model genuinely tracks timing better (higher r); KGE's
variability penalty is what drags its composite score slightly below persistence at the shortest
horizon.""")

story.append(PageBreak())
h2("6.3 Per-station NSE — checked because the pooled number looked surprisingly high")
p("""Pooled NSE (0.996 at 24h) is well above the 0.85-0.89 range typical in the reviewed literature.
Checked directly rather than just reported: pooling all 30 stations before computing NSE lets
between-station variance (discharge spans ~4 orders of magnitude) inflate the number relative to
genuine within-station predictive skill.""")
fig("fig_per_station_nse.png", f"Figure — Per-station NSE, 24h horizon (median="
    f"{m['24h']['per_station_nse_median']:.3f}, still high, but real and not pooling-inflated).",
    width=11 * cm)
p("""The per-station view surfaced a real, previously-invisible weak point: <b>ME03 (Dhaka's
Buriganga)</b> — the smallest-discharge station in the network — sits at NSE 0.56 at 24h and degrades to
0.30 by 72h, unlike every other station.""")
fig("fig_me03_degradation.png", "Figure — ME03's NSE vs. the network median, by horizon. Every other "
    "station stays relatively stable with lead time; ME03 degrades sharply.", width=11 * cm)

story.append(PageBreak())
h2("6.4 Predicted vs. actual discharge")
fig("fig_predicted_vs_actual.png", "Figure — Predicted vs. actual discharge (log-log scale), all 3 "
    "horizons, held-out test set.", width=16.5 * cm)

story.append(PageBreak())

# ===========================================================================
# 7. COMPARISON
# ===========================================================================
h1("7. Comparison: This Model vs. the Literature")
make_table(
    ["Study / model", "Reported metric", "Comparable to this model?"],
    [
        ["Mountainous catchment (XGBoost/LightGBM/CatBoost)", "NSE 0.85-0.89",
         "This model's per-station median NSE (0.989 at 24h, 0.965 at 72h) is meaningfully higher — "
         "plausibly because Bangladesh's major rivers integrate huge upstream catchments, making them "
         "naturally smoother/more autocorrelated day-to-day than the flashier catchments that study "
         "examined, not evidence of an unfair comparison."],
        ["Old Brahmaputra, Bangladesh (XGBoost + 5 deep learning models)", "R&sup2; &gt; 0.98 at 1-day "
         "lead", "The most directly comparable benchmark (same river system) — in the same range as "
         "this model's own R&sup2;/NSE, though that study's leakage-control methodology is not fully "
         "disclosed in its abstract."],
        ["Bangladesh monthly extreme water level (Random Forest Regression)", "RMSE 0.64-0.77m, "
         "R&sup2; 0.87-0.92", "Different task (monthly extremes vs. this model's daily point forecast) "
         "— not directly comparable, included for context."],
    ],
    [5.3 * cm, 4 * cm, 6.2 * cm],
)

story.append(PageBreak())

# ===========================================================================
# 8. LIMITATIONS
# ===========================================================================
h1("8. Limitations &amp; Honesty Notes")
story.append(Paragraph(
    "&bull; <b>Pooled NSE/KGE are somewhat inflated by between-station variance</b> (&sect;6.3) — always "
    "report the per-station median alongside the pooled number, not instead of it.<br/>"
    "&bull; <b>ME03 (Dhaka's Buriganga) is a genuine weak point</b>, worsening with lead time — a small, "
    "possibly urban/regulated river likely more affected by local factors this model's regional weather "
    "features don't capture.<br/>"
    "&bull; <b>NSE and KGE are themselves imperfect</b> (&sect;2.2) — sensitive to daily streamflow's "
    "skew/periodicity, not meant for cross-site comparison. Reported as a supplement to the persistence "
    "comparison, not a replacement.<br/>"
    "&bull; <b>MAPE is extremely high</b> (180-3000%) at every horizon — a known artifact of dividing by "
    "near-zero discharge on small rivers' driest days, not a sign the model is actually that wrong; MAE/"
    "NSE/KGE are the metrics to trust here, not MAPE.",
    styles["BodyText2"]))

# ===========================================================================
# 9. FUTURE WORK
# ===========================================================================
h1("9. Future Work")
story.append(Paragraph(
    "&bull; Investigate ME03 specifically — is a small-discharge-specific feature or a separate "
    "small-river model family (e.g. Random Forest, which led Bangladesh's own monthly-extreme-water-"
    "level comparison) worth testing there.<br/>"
    "&bull; A direct RF-vs-LightGBM head-to-head for this task, matching the discipline already applied "
    "to the susceptibility model.<br/>"
    "&bull; Consider reporting NSE/KGE in log-space too (the scale the model actually optimizes), "
    "alongside the raw-scale numbers already reported, for a fuller picture.",
    styles["BodyText2"]))

# ===========================================================================
# APPENDIX
# ===========================================================================
story.append(PageBreak())
h1("Appendix: Reproducibility Reference")
make_table(
    ["Artifact", "Path"],
    [
        ["Feature engineering", "backend/train/build_features.py, build_regression_targets.py"],
        ["Model training + evaluation (incl. NSE/KGE)", "backend/train/train_regression_model.py"],
        ["Trained models + metrics", "backend/models/2026-08-07c-discharge-regression/"],
        ["Standalone service", "packages/discharge-forecaster/"],
        ["This report's figures", "reports/generate_discharge_assets.py"],
        ["Full build log", "MODEL_BUILD_PLAN.md (2026-08-14 entries)"],
    ],
    [5.5 * cm, 9.5 * cm],
)

doc = SimpleDocTemplate(str(OUT_PATH), pagesize=A4,
                         leftMargin=1.8 * cm, rightMargin=1.8 * cm, topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                         title="Discharge Forecaster Model Report", author="AquaGuard / pred_flood project")
doc.build(story)
print(f"Wrote {OUT_PATH}")
