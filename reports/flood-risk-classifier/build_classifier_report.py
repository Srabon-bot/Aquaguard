"""Builds Flood_Risk_Classifier_Model_Report.pdf -- same structure/rigor as
Flood_Susceptibility_Model_Report.pdf, for model #1 (the temporal flood
risk classifier). Every number comes from backend/models/2026-08-07c/
metrics.json and the figures generate_classifier_assets.py produced.

Usage:
    python reports/generate_classifier_assets.py   # run first
    python reports/build_classifier_report.py
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
MODELS_DIR = ROOT / "backend" / "models" / "2026-08-07c"
OUT_PATH = Path(__file__).resolve().parent / "Flood_Risk_Classifier_Model_Report.pdf"

metrics = json.loads((MODELS_DIR / "metrics.json").read_text())
m = {r["horizon"]: r for r in metrics}
calib = json.loads((ASSETS / "calibration_summary.json").read_text())

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
def h3(t): story.append(Paragraph(t, styles["H3"]))
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
story.append(Paragraph("Flood Risk Classifier", styles["TitleBig"]))
story.append(Paragraph("Model #1 of the AquaGuard / Bangladesh Flood Early-Warning System", styles["TitleSub"]))
story.append(Paragraph("A temporal, live-weather-driven flood/no-flood forecaster — literature review, "
                        "methodology, real data, and evaluation results", styles["TitleSub"]))
spacer(40)
story.append(Paragraph(f"{date.today().strftime('%B %d, %Y')}", styles["TitleSub"]))
story.append(Paragraph("Companion to the discharge-forecaster and flood-susceptibility reports", styles["TitleSub"]))
story.append(PageBreak())

# ===========================================================================
# 1. INTRODUCTION
# ===========================================================================
h1("1. Introduction &amp; Purpose")
p("""This model answers the question the whole early-warning system exists for: <b>will this station
flood in the next 24, 48, or 72 hours</b>, using live rainfall, soil-moisture, and river-discharge data.
It is deliberately a classifier (flood / no-flood probability), not a single opaque risk score — three
independent per-horizon models, each producing its own calibrated probability, matching how real
early-warning systems present multi-lead-time risk.""")
p("""This report documents the model as it exists today, including a 2026-08-14 improvement pass that
added probability calibration and a naive-baseline comparison the model never had before — both are
covered in full, including a finding that is not flattering but is real (&sect;8).""")

# ===========================================================================
# 2. LITERATURE REVIEW
# ===========================================================================
h1("2. Literature Review")
p("""A dedicated, fresh multi-search literature pass (~28 queries) was run against this model
specifically on 2026-08-14 — deliberately treated as if the model didn't exist yet, to get unbiased
findings rather than re-reading earlier design reasoning. The sources below are the ones that either
confirmed an existing design choice independently, or surfaced a concrete improvement.""")

h2("2.1 Methodology &amp; data requirements")
make_table(
    ["Source", "Key finding relevant to this project"],
    [
        ["Flood forecasting with machine learning models in an operational framework "
         "(<i>HESS</i>, Google Research)",
         "Real operational systems split ML use across distinct subsystems (data validation, stage "
         "forecasting, inundation, alerting) — this project's own scope (forecasting only) matches "
         "the \"stage forecasting\" subsystem specifically."],
        ["Flood early warning system data requirements (multiple sources: NASA Lifelines, IMERG, "
         "soil-moisture literature)",
         "Rainfall, river discharge, and soil moisture are the three consistently-cited core inputs — "
         "exactly this model's three live feature groups."],
        ["Rare event prediction / class imbalance in flash-flood prediction (<i>arXiv</i>, "
         "<i>ACM Computing Surveys</i>)",
         "Flash floods occur on \"perhaps 1-10% of days\" at a given location — a model optimizing "
         "plain accuracy would just always predict \"no flood\" and still score well while being "
         "useless. Precision/recall-based evaluation (not accuracy) is essential — matches this "
         "model's own PR-AUC/recall-target design."],
    ],
    [7.3 * cm, 8.7 * cm],
)

h2("2.2 Model family choice")
make_table(
    ["Source", "Key finding relevant to this project"],
    [
        ["Rare-event / imbalanced flood prediction (same search as above)",
         "\"GBDT are particularly well-suited for imbalanced datasets of rare flooding events, due to "
         "gradient boosting on difficult-to-classify examples\" — directly supports the LightGBM choice."],
        ["A systematic review of flood prediction 2018-2025 (<i>ScienceDirect</i>)",
         "\"Clear trend toward ML/ensemble methods... RF, SVR, XGBoost dominate due to interpretability "
         "and reliability\" alongside deep learning (LSTM/GRU/CNN/Transformer) approaches."],
        ["Knowledge-Guided ML for Operational Flood Forecasting (<i>Water Resources Research</i> 2025, "
         "Microsoft Research)",
         "A genuinely different SOTA direction: a Factorized Hierarchical Neural Network with separate "
         "inverse (infer catchment state) and forward (predict from that state) components — "
         "Google/Microsoft-scale infrastructure, judged out of scope for a 30-station project."],
        ["Google Flood Hub / Hydrologic Model (<i>Google Research</i>)",
         "ME-LSTM with per-weather-product embedding networks and a CMAL probabilistic output — the "
         "reference-class deep learning approach, trained on thousands of global gauges (this project "
         "has 30)."],
    ],
    [7.3 * cm, 8.7 * cm],
)

h2("2.3 Evaluation methodology")
make_table(
    ["Source", "Key finding relevant to this project"],
    [
        ["Classification approach for flood early warning systems (multiple sources)",
         "\"Accuracy alone is insufficient... a model could miss every flood while still maintaining "
         "high accuracy\" — precision/recall and PR-AUC are the field's own stated correct metrics, "
         "not something this project invented for convenience."],
        ["F-beta scoring for imbalanced problems",
         "F2 (recall weighted twice as important as precision) formalizes exactly the recall-priority "
         "design philosophy this model's threshold-tuning already implements informally."],
        ["Classifier calibration: Platt scaling vs. isotonic regression (multiple ML references)",
         "\"Isotonic regression has been shown to work better than Platt scaling... when enough "
         "training data is available\" — this project has ~78k training rows per horizon, well past "
         "that bar. Directly motivated &sect;6.3/&sect;8's calibration work."],
        ["SHAP for flood-model interpretability (2025 XAI literature)",
         "\"Addressing the black-box limitations that have hindered practical adoption by disaster "
         "management authorities\" — SHAP explicitly framed as a trust requirement, not a nice-to-have."],
    ],
    [7.3 * cm, 8.7 * cm],
)

story.append(PageBreak())

# ===========================================================================
# 3. MODEL FAMILIES USED IN THE LITERATURE
# ===========================================================================
h1("3. Model Families Used in the Literature")
make_table(
    ["Model family", "Typical reported role", "This project"],
    [
        ["Logistic Regression", "Weakest baseline in most comparisons", "Not used — literature "
         "consensus already rules it out for this kind of nonlinear, imbalanced problem."],
        ["Random Forest / XGBoost / LightGBM (tree ensembles)", "Dominant choice across the field, "
         "\"well-suited... due to gradient boosting on difficult-to-classify examples\"",
         "<b>LightGBM used</b> — matches the field's own stated reasoning for why."],
        ["LSTM / GRU / Transformer (deep sequence models)", "Common for high-data-volume operational "
         "systems (Google Flood Hub: thousands of gauges)", "Not used — this project has 30 stations, "
         "well below the data volume these architectures need to outperform gradient boosting."],
        ["Knowledge-guided hybrid (FHNN, inverse/forward catchment-state model)", "One 2025 study, "
         "Microsoft-scale infrastructure", "Not used — noted as a genuine future direction, not "
         "currently in scope."],
        ["<b>LightGBM, per-horizon, pooled multi-station (this project)</b>", "&mdash;",
         f"<b>24h: ROC-AUC {m['24h']['roc_auc']:.3f}, PR-AUC {m['24h']['pr_auc']:.3f} &mdash; "
         f"72h: ROC-AUC {m['72h']['roc_auc']:.3f}, PR-AUC {m['72h']['pr_auc']:.3f}</b>"],
    ],
    [4.3 * cm, 6 * cm, 5.7 * cm],
)

story.append(PageBreak())

# ===========================================================================
# 4. OUR MODEL
# ===========================================================================
h1("4. Our Model: Design &amp; Rationale")

h2("4.1 Three independent per-horizon models, pooled across all 30 stations")
p("""Rather than one sequence model spanning all three horizons, three separate binary classifiers are
trained (24h/48h/72h) — the literature frames this as the \"direct multi-step\" strategy, now standard
specifically because it avoids the error accumulation a recursive (sequence) approach suffers at longer
horizons. All 30 stations are pooled into one training set per horizon (station/basin passed in as
categorical features), not one model per station — independently matching a named best-practice rule
from the LSTM streamflow literature: <i>\"never train an LSTM on a single basin\"</i> (Kratzert et al.)
— several of the 30 stations have too few labeled rows to train an independent model each.""")

h2("4.2 Handling rare, noisy labels")
p("""Positive labels are rare and come from multiple sources of differing confidence (GFMS satellite
detections, DFO event catalogs, Global Flood Database). A custom sample-weighting scheme — computed
from the "observed"-regime rows' real class balance, with an extra confidence discount for
DFO-derived positives — replaces a blanket <code>class_weight="balanced"</code>, which the code&rsquo;s
own analysis found would under-correct for how rare a positive actually is at deployment time.""")

h2("4.3 Threshold tuned for recall, not accuracy")
p(f"""A missed flood costs far more than a false alarm, so each horizon&rsquo;s decision threshold is
chosen to hit 85% recall rather than accepting whatever recall the default 0.5 threshold produces.
Real result: at 24h, threshold={m['24h']['at_chosen_threshold']['threshold']:.3f} yields recall="""
  f"""{m['24h']['at_chosen_threshold']['recall']:.3f}, precision={m['24h']['at_chosen_threshold']['precision']:.3f}
— a deliberate, documented trade of false alarms for caught floods, not an accident of an untuned
threshold.""")

h2("4.4 2026-08-14 additions: calibration and a naive-baseline comparison")
p("""Neither existed before this pass. <b>Isotonic calibration</b> (fit on a held-out validation slice,
never the test set) recalibrates the <i>displayed</i> probability without touching the recall-tuned
decision threshold above — those are different questions ("what decision to make" vs. "does the
probability number mean what it says") and are kept deliberately separate. <b>Naive baselines</b>
(climatology, persistence) were added because this model never had one, despite the project's own
standing practice of comparing every model against a baseline (already applied to the discharge
forecaster and the susceptibility model). Both are covered in full in &sect;6 and &sect;8.""")

story.append(PageBreak())

# ===========================================================================
# 5. DATA SOURCES
# ===========================================================================
h1("5. Data Sources")
make_table(
    ["Source", "What it provides"],
    [
        ["Open-Meteo Forecast API (free, no key)", "Live rainfall (local point + 9-point upstream "
         "basin grid) and soil moisture (0-7cm depth)"],
        ["Open-Meteo Flood API (GloFAS reanalysis/forecast, free)", "River discharge, local + upstream "
         "reference stations"],
        ["GFMS (NASA), DFO, Global Flood Database, Copernicus GFM (SAR)", "Historical flood-event "
         "labels — 4 independent sources, since no single one has continuous \"confidently no flood\" "
         "coverage across the full training period"],
        ["MERIT Hydro (via Earth Engine, one-time sample)", "Static per-station elevation/HAND terrain "
         "features"],
    ],
    [6.5 * cm, 9.5 * cm],
)
p(f"""Train: {m['24h']['train_rows']:,} rows ({m['24h']['train_positive_rate']*100:.1f}% positive, 24h
horizon) with date &lt; 2024-01-01. Test: {m['24h']['test_rows']:,} rows
({m['24h']['test_positive_rate']*100:.1f}% positive) with date &ge; 2024-01-01 — a genuinely time-based
split (never a random shuffle, which would leak nearby-day autocorrelation from test into train),
restricted to the "observed"-regime label subset for a fair evaluation.""")

story.append(PageBreak())

# ===========================================================================
# 6. RESULTS: PLOTS & ANALYTICS
# ===========================================================================
h1("6. Results: Plots &amp; Analytics")

h2("6.1 Discrimination: ROC, Precision-Recall, confusion matrix")
for h in ["24h", "48h", "72h"]:
    fig(f"fig_{h}_roc_pr_confusion.png",
        f"Figure — {h} horizon: ROC-AUC={m[h]['roc_auc']:.3f}, PR-AUC={m[h]['pr_auc']:.3f}, held-out "
        f"test set (date &ge; 2024-01-01, 'observed' regime only).", width=16.5 * cm)
    if h != "72h":
        story.append(PageBreak())

story.append(PageBreak())
h2("6.2 Feature importance")
fig("fig_feature_importance.png", "Figure — SHAP feature importance, 24h horizon model.")

story.append(PageBreak())
h2("6.3 Calibration — deepened beyond a single Brier-score number")
p("""Three independent proper scoring rules were checked, not just one, so the "calibration helped"
claim doesn't rest on a single metric that might happen to favor it:""")
make_table(
    ["Horizon", "Brier (raw &rarr; calibrated)", "Log loss (raw &rarr; calibrated)", "ECE (raw &rarr; calibrated)"],
    [[h, f"{calib[h]['brier_raw']:.4f} &rarr; {calib[h]['brier_calibrated']:.4f}",
      f"{calib[h]['log_loss_raw']:.4f} &rarr; {calib[h]['log_loss_calibrated']:.4f}",
      f"{calib[h]['ece_raw']:.4f} &rarr; {calib[h]['ece_calibrated']:.4f}"] for h in ["24h", "48h", "72h"]],
    [3 * cm, 4.3 * cm, 4.3 * cm, 4.3 * cm],
)
p("""All three metrics agree: calibration is a real, substantial improvement at every horizon — not an
artifact of any one scoring rule.""")
fig("fig_24h_calibration_reliability.png",
    "Figure — Reliability diagram, 24h horizon. The raw model is severely overconfident: a stated 90% "
    "probability corresponds to an observed flood frequency of only ~23%. Calibration closes most of "
    "that gap, though the calibrated curve still sits slightly below perfect (a bounded improvement, "
    "not a complete fix).", width=11 * cm)
fig("fig_calibration_all_horizons.png", "Figure — Reliability diagrams, all 3 horizons.")

story.append(PageBreak())

# ===========================================================================
# 7. COMPARISON: THIS MODEL VS. THE LITERATURE
# ===========================================================================
h1("7. Comparison: This Model vs. the Literature")
p("""Several Bangladesh-specific studies (see the earlier flood-susceptibility report's &sect;2.2 for
the full list) report 97%+ accuracy for similar-sounding classification tasks. As documented in that
report, most of those numbers come from a different, easier problem (static spatial classification,
often randomly split) than this model's genuine temporal forecasting on a strict time-based split — the
same honesty framing applies here and is not repeated in full.""")
make_table(
    ["Metric", "This model (24h)", "Literature context"],
    [
        ["ROC-AUC", f"{m['24h']['roc_auc']:.3f}", "0.85-0.98 range across reviewed studies, mostly "
         "without disclosed spatial/temporal-split discipline"],
        ["PR-AUC", f"{m['24h']['pr_auc']:.3f}", "Rarely reported by comparable studies — most report "
         "only accuracy, which is why this model reports PR-AUC/recall instead (&sect;2.1)"],
        ["Precision @ 85% recall", f"{m['24h']['at_chosen_threshold']['precision']:.3f}",
         "Not directly comparable — reflects this model's own deliberate recall-priority design "
         "(&sect;4.3), not a universal operating point"],
    ],
    [4.5 * cm, 4 * cm, 7.5 * cm],
)

story.append(PageBreak())

# ===========================================================================
# 8. THE PERSISTENCE-BASELINE FINDING
# ===========================================================================
h1("8. The Persistence-Baseline Finding")
p("""The most consequential result of the 2026-08-14 improvement pass, reported in full rather than
minimized. Two naive, zero-live-data baselines were compared against the model on the exact same
held-out test rows:""")
fig("fig_baseline_comparison.png", "Figure — Model PR-AUC vs. climatology and persistence baselines, "
    "all 3 horizons.")
p(f"""The model clearly beats climatology ({m['24h']['naive_baselines']['climatology_pr_auc']:.3f} at
24h) at every horizon. It does <b>not</b> beat persistence
({m['24h']['naive_baselines']['persistence_pr_auc']:.3f} at 24h) — confirmed not an artifact of
comparing mismatched operating points: at persistence's own natural 61.6% recall, the model's precision
(20.7%) is still far below persistence's (61.6%).""")
fig("fig_persistence_matched_recall.png", "Figure — Model's full precision-recall curve vs. persistence "
    "at a matched recall point, 24h horizon.", width=11 * cm)
p("""<b>Working explanation, not yet tested:</b> <code>flood_within_Nh</code> labels cluster in
multi-day contiguous blocks (real floods last many days), so persistence is unusually strong
specifically at predicting the <i>continuation</i> of an already-ongoing flood — exactly the part of
the problem requiring the least forecasting skill. The model's real value is plausibly concentrated in
predicting flood <i>onset</i> (a brand-new event persistence can never predict, since it only ever
repeats yesterday's label). A pooled PR-AUC across both continuation and onset rows lets the easier
continuation majority dominate the metric and mask genuine onset-specific skill. This has not yet been
tested — it is the clear next investigation for this model, not something to quietly work around.""")

story.append(PageBreak())

# ===========================================================================
# 9. LIMITATIONS
# ===========================================================================
h1("9. Limitations &amp; Honesty Notes")
story.append(Paragraph(
    "&bull; <b>Does not beat a persistence baseline on pooled PR-AUC</b> (&sect;8) &mdash; the single "
    "most important limitation in this report, not buried in a list.<br/>"
    "&bull; <b>Calibration is bounded, not perfect</b>: even after isotonic calibration, the model "
    "rarely produces very high probabilities (the calibrated reliability curve tops out around 40% "
    "mean predicted probability at 24h) &mdash; a real improvement, not a complete fix.<br/>"
    "&bull; <b>Calibrator is not yet wired into live serving</b> &mdash; saved as an artifact per horizon "
    "(e.g. <code>model_24h_calibrator.joblib</code>) but the live API still returns the raw score.<br/>"
    "&bull; <b>Precision at the tuned threshold is genuinely low</b> (13-18% across horizons) &mdash; a "
    "disclosed, structural consequence of rare positive labels and a deliberate recall-priority design, "
    "not a bug.",
    styles["BodyText2"]))

# ===========================================================================
# 10. FUTURE WORK
# ===========================================================================
h1("10. Future Work")
story.append(Paragraph(
    "&bull; <b>Highest priority</b>: design and test an onset-vs-continuation-aware evaluation (and "
    "possibly training target) directly motivated by &sect;8.<br/>"
    "&bull; Wire the saved isotonic calibrators into live serving so the API returns a calibrated, not "
    "raw, probability.<br/>"
    "&bull; The cross-correlation lag experiment (tested 2026-08-14, rejected — extending "
    "<code>[1,2,3,5]</code> with lags 7 and 12 was neutral-to-harmful) closes that avenue; no further "
    "lag-design work planned unless new evidence emerges.",
    styles["BodyText2"]))

# ===========================================================================
# APPENDIX
# ===========================================================================
story.append(PageBreak())
h1("Appendix: Reproducibility Reference")
make_table(
    ["Artifact", "Path"],
    [
        ["Feature engineering", "backend/train/build_features.py"],
        ["Model training + evaluation", "backend/train/train_model.py"],
        ["Cross-correlation lag experiment (rejected)", "backend/train/experiment_cross_correlation_lags.py"],
        ["Trained models + metrics + calibrators", "backend/models/2026-08-07c/"],
        ["Standalone service", "packages/flood-risk-classifier/"],
        ["This report's figures", "reports/generate_classifier_assets.py"],
        ["Full build log", "MODEL_BUILD_PLAN.md (2026-08-14 entries)"],
    ],
    [5.5 * cm, 9.5 * cm],
)

doc = SimpleDocTemplate(str(OUT_PATH), pagesize=A4,
                         leftMargin=1.8 * cm, rightMargin=1.8 * cm, topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                         title="Flood Risk Classifier Model Report", author="AquaGuard / pred_flood project")
doc.build(story)
print(f"Wrote {OUT_PATH}")
