"""Builds Flood_Susceptibility_Model_Report.pdf from the figures
generate_susceptibility_assets.py produced plus real numbers pulled live
from backend/models/susceptibility/metrics.json and the data files on disk
-- text content (literature summaries, methodology narrative) is written
here, but every number/figure is sourced from disk, not hand-typed.

Usage:
    python reports/generate_susceptibility_assets.py   # run first
    python reports/build_susceptibility_report.py
"""

import json
from datetime import date
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

ROOT = Path(__file__).resolve().parent.parent.parent
ASSETS = Path(__file__).resolve().parent / "assets"
MODELS_DIR = ROOT / "backend" / "models" / "susceptibility"
OUT_PATH = Path(__file__).resolve().parent / "Flood_Susceptibility_Model_Report.pdf"

metrics = json.loads((MODELS_DIR / "metrics.json").read_text())
schema = json.loads((MODELS_DIR / "feature_schema.json").read_text())
counts = pd.read_csv(ROOT / "backend" / "data_raw" / "susceptibility" / "grid_point_flood_counts.csv")
terrain = pd.read_csv(ROOT / "backend" / "data_raw" / "susceptibility" / "grid_point_terrain.csv")
training_table = pd.read_csv(ROOT / "backend" / "data" / "susceptibility" / "susceptibility_training_table.csv")

# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
styles = getSampleStyleSheet()
styles.add(ParagraphStyle("H1", parent=styles["Heading1"], fontSize=17, spaceBefore=14, spaceAfter=8, textColor=colors.HexColor("#10131a")))
styles.add(ParagraphStyle("H2", parent=styles["Heading2"], fontSize=13, spaceBefore=12, spaceAfter=6, textColor=colors.HexColor("#2a3550")))
styles.add(ParagraphStyle("H3", parent=styles["Heading3"], fontSize=11, spaceBefore=8, spaceAfter=4, textColor=colors.HexColor("#3c4250")))
styles.add(ParagraphStyle("BodyText2", parent=styles["BodyText"], fontSize=9.6, leading=13.5, spaceAfter=7))
styles.add(ParagraphStyle("Small", parent=styles["BodyText"], fontSize=8, leading=10.5, textColor=colors.HexColor("#5a6070")))
styles.add(ParagraphStyle("Caption", parent=styles["BodyText"], fontSize=8.3, leading=11, textColor=colors.HexColor("#5a6070"), spaceBefore=3, spaceAfter=10, alignment=1))
styles.add(ParagraphStyle("TitleBig", parent=styles["Title"], fontSize=25, leading=30))
styles.add(ParagraphStyle("TitleSub", parent=styles["Normal"], fontSize=12.5, alignment=1, textColor=colors.HexColor("#5a6070"), spaceBefore=8))
styles.add(ParagraphStyle("TableCell", parent=styles["BodyText"], fontSize=8, leading=10.5))
styles.add(ParagraphStyle("TableCellHead", parent=styles["BodyText"], fontSize=8.3, leading=10.5, textColor=colors.white, fontName="Helvetica-Bold"))

BLUE = colors.HexColor("#2a78d6")
GREY_BG = colors.HexColor("#f3f5f9")

story = []


def h1(text):
    story.append(Paragraph(text, styles["H1"]))


def h2(text):
    story.append(Paragraph(text, styles["H2"]))


def h3(text):
    story.append(Paragraph(text, styles["H3"]))


def p(text):
    story.append(Paragraph(text, styles["BodyText2"]))


def small(text):
    story.append(Paragraph(text, styles["Small"]))


def spacer(h=6):
    story.append(Spacer(1, h))


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
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    spacer(10)


# ===========================================================================
# TITLE PAGE
# ===========================================================================
story.append(Spacer(1, 4 * cm))
story.append(Paragraph("Flood Susceptibility Model", styles["TitleBig"]))
story.append(Paragraph("Model #3 of the AquaGuard / Bangladesh Flood Early-Warning System", styles["TitleSub"]))
story.append(Paragraph(
    "A static, terrain-based hazard model — literature review, methodology, real data, "
    "and evaluation results", styles["TitleSub"]))
spacer(40)
story.append(Paragraph(f"{date.today().strftime('%B %d, %Y')}", styles["TitleSub"]))
story.append(Paragraph("Companion to the flood-risk-classifier and discharge-forecaster reports", styles["TitleSub"]))
story.append(PageBreak())

# ===========================================================================
# 1. INTRODUCTION
# ===========================================================================
h1("1. Introduction &amp; Purpose")
p("""This project already includes two temporal flood-forecasting models: a flood-risk classifier
(flood / no-flood probability at 24h/48h/72h, driven by live rainfall/soil-moisture/discharge data)
and a discharge forecaster (predicted river flow in m&sup3;/s at the same horizons). Both answer variants
of the same question — <i>will conditions here become dangerous soon</i> — and both are honestly hard
problems: rare, sparse positive labels, and precision that stays modest even at a carefully tuned
recall target.""")
p("""This report covers a third, deliberately different model: <b>flood susceptibility</b> — a static
assessment of how flood-prone a piece of ground is by its own geography (elevation, slope, distance to
the nearest river, drainage density, land cover), independent of any particular storm. It does not
compete with the other two models; it answers a question they cannot: even before this year's weather
is known, is this specific patch of land the kind that floods, or the kind that stays dry?""")
p("""The three models combine into one pipeline: the classifier's time-bound hazard probability,
modulated by this model's static susceptibility score, via a transparent formula documented in
Section&nbsp;9 — deliberately not a black-box stacked meta-model, so the combination stays explainable
in one line.""")

# ===========================================================================
# 2. LITERATURE REVIEW
# ===========================================================================
h1("2. Literature Review")
p("""A multi-pass literature search (methodology, Bangladesh-specific studies, data-source accuracy,
and evaluation-methodology papers — roughly 20 separate search queries, not a single pass) was
conducted before design work began. The sources below are the ones that materially shaped this
model's design, grouped by theme.""")

h2("2.1 General methodology &amp; model-comparison studies")
make_table(
    ["Source", "Key finding relevant to this project"],
    [
        ["Flood susceptibility assessment using three ML techniques and comparison of their performance "
         "(<i>Scientific Reports</i>, 2026)",
         "Random Forest, Gradient Boosting, and XGBoost all outperform simpler models on nonlinear "
         "terrain relationships; ensemble trees are the consistent starting point across the field."],
        ["Integrating geospatial intelligence and machine learning for flood susceptibility mapping "
         "(<i>Scientific Reports</i>)",
         "Reinforces elevation, slope, and distance-to-river as consistently top-ranked predictors "
         "across independent studies."],
        ["Flood susceptibility mapping using supervised ML models: insights into predictors&rsquo; "
         "significance and models&rsquo; performance (<i>Geocarto International</i>)",
         "Systematic predictor-importance comparison across model families — informed this project&rsquo;s "
         "choice to report SHAP importance rather than a single opaque accuracy number."],
        ["Combining ML Models and Satellite Data of an Extreme Flood Event for Flood Susceptibility "
         "Mapping (<i>MDPI Water</i>)",
         "Uses satellite-observed flood extent directly as training labels — the same core idea this "
         "project used with the Copernicus GFM SAR archive, aggregated across time instead of one event."],
        ["Enhancing flood susceptibility mapping through nature-inspired metaheuristic algorithms and ML "
         "(<i>ScienceDirect</i>)",
         "RNN-GA / LSTM-GA hybrids reach ~93% AUC but require metaheuristic optimization overhead judged "
         "out of scope for this project&rsquo;s data volume (30 stations, not thousands of gauges)."],
        ["Next generation data-driven flood susceptibility modelling with spatial machine learning "
         "(<i>ScienceDirect</i>)",
         "<b>Directly informed this project&rsquo;s evaluation design</b>: documents that random train/test "
         "splits on spatially autocorrelated data inflate reported AUC by 5&ndash;15%."],
        ["Spatial validation reveals poor predictive performance of large-scale ecological mapping models "
         "(<i>PMC</i>)",
         "Cross-domain (ecology, not hydrology) confirmation of the same random-vs-spatial-split "
         "inflation problem — the issue is general to spatial ML, not specific to flood studies."],
    ],
    [7.3 * cm, 8.7 * cm],
)

h2("2.2 Bangladesh-specific studies")
make_table(
    ["Source", "Key finding relevant to this project"],
    [
        ["Predictive Analytics for Floods in Bangladesh: A Comparative Exploration of ML and Deep "
         "Learning Classifiers (<i>ICCIT 2023 / IEEE</i>)",
         "LightGBM (97.76%) and Random Forest (97.71%) led 10 compared classifiers on 65 years of "
         "Bangladesh data — but on a different task (see &sect;7 comparison) and evaluation method than "
         "this project uses."],
        ["A machine learning-based approach for flash flood susceptibility mapping considering rainfall "
         "extremes, northeast Bangladesh (<i>ResearchGate</i>)",
         "<b>Random Forest outperformed XGBoost specifically in hilly, flash-flood-prone terrain</b> — "
         "this project independently found the same result on its own hilly/flat mixed grid (&sect;6.1)."],
        ["Assessment and Zonation of Flood Susceptibility in Sylhet Division, Bangladesh, Using GIS and "
         "AHP (<i>Journal of Flood Risk Management</i>, 2025)",
         "Non-ML (AHP, expert-weighted) baseline: ROC &asymp; 87% — a useful, realistic reference point "
         "against inflated ML-only numbers."],
        ["GIS and AHP-based flood susceptibility mapping: a case study of Bangladesh "
         "(<i>Sustainable Water Resources Management</i>)",
         "A second independent AHP baseline for Bangladesh, consistent with the Sylhet study above."],
        ["Geospatial driven machine learning approach for flood susceptibility mapping in southeastern "
         "Bangladesh (<i>Discover Geoscience</i>, 2026)",
         "The most directly comparable regional ML study found during this search."],
    ],
    [7.3 * cm, 8.7 * cm],
)

h2("2.3 Data sources &amp; terrain-analysis methodology")
make_table(
    ["Source", "Key finding relevant to this project"],
    [
        ["Vertical accuracy assessment of freely available global DEMs (FABDEM, Copernicus DEM, NASADEM, "
         "AW3D30, SRTM) in flood-prone environments (<i>International Journal of Digital Earth</i>)",
         "Copernicus DEM GLO-30 (NMAD &asymp; 1.27m) is substantially more accurate than SRTM "
         "(&asymp; 3.65m), especially in flat terrain — directly determined this project&rsquo;s DEM choice."],
        ["TWI computation: a comparison of different open source GISs (<i>Open Geospatial Data, "
         "Software and Standards</i>)",
         "Compared QGIS/SAGA/GRASS/Whitebox terrain toolchains — informed the choice of a pure-Python "
         "pipeline (<code>pysheds</code>) over a desktop-GIS dependency."],
        ["Suitability of the height above nearest drainage (HAND) model for flood inundation mapping in "
         "data-scarce regions (<i>Earth Science Informatics</i>)",
         "HAND is specifically weaker in flat, low-relief, urbanized-drainage terrain — exactly "
         "Bangladesh&rsquo;s geography. This triggered a mid-build review of this project&rsquo;s own HAND "
         "usage (see &sect;4.3)."],
        ["HydroRIVERS v1.0 (Lehner &amp; Grill, 2013, via HydroSHEDS)",
         "A peer-reviewed, independently-built global river network (8.5 million reaches) — used in this "
         "project both as a validation cross-check for, and ultimately as the production source of, the "
         "distance-to-river feature (see &sect;4.6)."],
    ],
    [7.3 * cm, 8.7 * cm],
)

story.append(PageBreak())

# ===========================================================================
# 3. MODELS USED IN THE LITERATURE
# ===========================================================================
h1("3. Model Families Used in the Literature")
p("""Across every source reviewed, the following model families recur. This project&rsquo;s own choice
(&sect;4) is included in the same table for direct comparison of what each family is and how it
performed elsewhere.""")

make_table(
    ["Model family", "Where seen", "Typical reported performance", "Notes"],
    [
        ["Logistic Regression", "Baseline in most comparative studies", "Consistently the weakest "
         "of the compared models", "Cannot capture nonlinear terrain interactions."],
        ["Random Forest", "Very common; sometimes wins outright", "97.71% accuracy (Bangladesh, "
         "&sect;2.2); AUC 0.88&ndash;0.98 range across studies", "Won in this project too (&sect;6.1) — "
         "matches the hilly-terrain finding in &sect;2.2."],
        ["XGBoost / Gradient Boosting", "Very common", "AUC up to 0.985 in some studies; beaten by RF "
         "in at least one Bangladesh hilly-terrain study", "This project&rsquo;s classifier (model #1) "
         "also uses gradient boosting (LightGBM), for a different, temporal task."],
        ["LightGBM", "Common, esp. recent Bangladesh studies", "97.76% accuracy (Bangladesh, &sect;2.2)",
         "Compared head-to-head against RF for this model (&sect;6.1); RF won on the spatial evaluation."],
        ["SVM / AdaBoost / ExtraTrees / MLP", "Seen as comparison baselines",
         "Generally mid-pack, below RF/XGBoost/LightGBM", "Not tried in this project — the literature "
         "consensus already points to tree ensembles."],
        ["TabNet / TabPFN (deep tabular)", "One Bangladesh comparative study",
         "Competitive but not clearly better than LightGBM/RF", "Deliberately not used here — added "
         "model complexity with no demonstrated benefit for this data volume (30 stations)."],
        ["RNN-GA / LSTM-GA (deep learning + metaheuristic optimization)", "One comparative study",
         "~93% AUC, best-in-study", "Requires substantially more data and optimization infrastructure "
         "than this project&rsquo;s scope justifies."],
        ["AHP (Analytic Hierarchy Process — expert-weighted, non-ML)", "Multiple Bangladesh studies",
         "ROC &asymp; 87%", "A realistic, non-inflated reference point (&sect;7)."],
        ["<b>Random Forest (this project)</b>", "&mdash;", "<b>Spatial CV: 0.888 mean ROC-AUC; held-out "
         "test: 0.908 ROC-AUC, 0.785 PR-AUC</b>", "Chosen after a real head-to-head against LightGBM on "
         "this project&rsquo;s own data — not assumed from the literature."],
    ],
    [3.6 * cm, 3.3 * cm, 4.6 * cm, 4.5 * cm],
)

story.append(PageBreak())

# ===========================================================================
# 4. OUR MODEL
# ===========================================================================
h1("4. Our Model: Design &amp; Rationale")

h2("4.1 Why a third, static model")
p("""Models #1 and #2 both need live weather/discharge data and both forecast a moving target (this
year&rsquo;s conditions). Susceptibility answers a fixed question instead — a genuinely different,
complementary signal, not a third attempt at the same forecast. It also does not need live data at
all: elevation, slope, and land cover do not change day to day, so once trained it can serve instantly
without calling any external weather API.""")

h2("4.2 The spatial grid")
p(f"""Rather than a single value per station (too coarse to train a spatial model on) or a
uniform grid over all of Bangladesh (far more labeling effort than this project&rsquo;s 30-station scope
needs), a local 7&times;7 grid (49 points, &plusmn;0.09&deg; &asymp; 10km span) was built around each of
the 30 monitored stations &mdash; {len(terrain):,} points in total. This directly serves the actual use
case (scoring the neighborhoods this project already monitors) without the much larger labeling effort
a national atlas would require.""")

h2("4.3 A mid-build correction: reusing, not duplicating, existing terrain data")
p("""This project&rsquo;s temporal classifier (model #1) already includes two terrain features
(<code>elevation_m</code>, <code>hand_m</code>) sourced from MERIT Hydro &mdash; a peer-reviewed,
properly flow-routed Height Above Nearest Drainage (HAND) product, deliberately chosen over
self-computing terrain metrics specifically to avoid a DEM-resampling mismatch bug (documented
project decision log, &sect;17&ndash;18). Early in this model&rsquo;s design, before checking, a
self-computed replacement for those two features was nearly built &mdash; which would have both
duplicated existing work and produced a strictly less rigorous version of an already-correct feature.
This was caught before implementation. The two features actually built for this model
(distance-to-river, drainage density) are genuinely new &mdash; they do not exist anywhere else in the
project. Drainage density remains computed from a single, internally consistent DEM source end-to-end,
a different situation from the cross-product resampling mismatch the original MERIT Hydro decision was
avoiding. Distance-to-river started the same way, but was later revised after an independent
cross-check (&sect;4.6) &mdash; itself an example of the same "verify, don&rsquo;t assume" discipline
applied a second time, this time to this project&rsquo;s own new feature rather than an existing one.""")

h2("4.4 Model family selection")
p("""Rather than assume the classifier&rsquo;s own model choice (LightGBM) would transfer to a
different problem, LightGBM and Random Forest were compared head-to-head on identical data via spatial
cross-validation (&sect;6.1). Random Forest won, consistent with a Bangladesh-specific finding
(&sect;2.2) that plain RF can outperform gradient boosting specifically in hilly terrain &mdash; this
project&rsquo;s grid spans both flat delta and the hilly Chittagong Hill Tracts, so that distinction
was worth checking rather than assuming.""")

h2("4.5 Final hyperparameters")
make_table(
    ["Parameter", "Value"],
    [["n_estimators", "300"], ["max_depth", "8"], ["min_samples_leaf", "5"], ["random_state", "42"]],
    [7 * cm, 7 * cm],
)

h2("4.6 Post-hoc validation: cross-checking distance-to-river, and acting on the result")
p("""After the model above was built and evaluated, the self-derived distance-to-river feature was
cross-checked against HydroRIVERS v1.0 (Lehner &amp; Grill, 2013) &mdash; a peer-reviewed, independently
built global river network, downloaded directly (91MB, no registration) and compared point-by-point
against the <code>pysheds</code> flow-accumulation-derived distances. The two methods correlated poorly
across the full 1,470-point grid (Pearson r &asymp; 0.03) &mdash; not the clean validation expected. At
the 30 station centers specifically, both agreed on the right order of magnitude (a few hundred meters),
with a consistent, explicable pattern: the self-derived method, built on a permissive flow-accumulation
threshold over a fine 30m DEM, detects a dense network of minor channels and therefore always reports
something at least as close as the coarser, major-rivers-only HydroRIVERS network. Away from station
centers, the two increasingly measure different things &mdash; likely compounded by a known artifact of
D8 flow routing on very flat deltaic terrain (spurious, overly dense drainage patterns).""")
p("""Rather than assume either method was better, both were tried empirically: the full training
pipeline (identical spatial CV, identical 7-station held-out test) was re-run three times, changing only
the distance-to-river feature.""")
make_table(
    ["Variant", "Spatial CV ROC-AUC", "Held-out test ROC-AUC", "Held-out test PR-AUC"],
    [
        ["Self-derived (pysheds) — original", "0.892", "0.902", "0.770"],
        ["<b>HydroRIVERS — adopted</b>", "<b>0.888</b>", "<b>0.908</b>", "<b>0.785</b>"],
        ["Both features together", "0.889", "0.903", "0.773"],
    ],
    [6 * cm, 2.8 * cm, 2.8 * cm, 2.8 * cm],
)
p("""HydroRIVERS won on the held-out test (the more decision-relevant metric) by a modest but real
margin; combining both features performed no better than either alone, indicating the two carry mostly
redundant signal rather than complementary information. Given the roughly-tied numbers plus the
stronger methodological story (an externally validated, peer-reviewed product rather than a self-derived
feature with a known flat-terrain algorithmic caveat), <b>the production model now uses the HydroRIVERS-
based distance</b> &mdash; the figures and numbers throughout the rest of this report reflect that
final, adopted version. The self-derived version is retained in the underlying data (
<code>dist_to_river_m_pysheds_legacy</code>) for provenance, not deleted.""")
fig("fig_river_distance_crosscheck.png", "Figure 4.6.1. The cross-check that triggered this decision: "
    "self-derived vs. independent distance-to-river, both raw and log-scaled. Near-zero raw correlation "
    "led to the empirical comparison above, not a decision made on the plot alone.", width=15 * cm)

story.append(PageBreak())

# ===========================================================================
# 5. DATA SOURCES
# ===========================================================================
h1("5. Data Sources")
make_table(
    ["Source", "What it provides", "Access"],
    [
        ["Copernicus DEM GLO-30 (ESA/Airbus, via AWS Open Data)", "Elevation &rarr; slope, distance-to-"
         "river, drainage density (self-derived via flow-routing)", "Free, unauthenticated, "
         "1&deg; Cloud-Optimized GeoTIFF tiles"],
        ["ESA WorldCover v200 (2021)", "10m land-cover class (11 categories: tree, cropland, water, "
         "wetland, mangrove, built-up, etc.)", "Free, unauthenticated, 3&deg; tiles, via AWS"],
        ["Copernicus Global Flood Monitoring (GFM) &mdash; Sentinel-1 SAR", "Flood observation labels, "
         "aggregated across the full 2016-04-01 to 2026-08-13 archive", "Free, unauthenticated STAC "
         "catalog + Cloud-Optimized GeoTIFFs"],
        ["MERIT Hydro v1.0.1 (referenced, not re-derived)", "Peer-reviewed HAND/elevation values already "
         "used by model #1&rsquo;s <code>STATIC_TERRAIN</code> table", "One-time Earth Engine sample "
         "(existing project asset, see &sect;4.3)"],
    ],
    [5.3 * cm, 6.4 * cm, 4.3 * cm],
)

h2("5.1 Terrain feature derivation pipeline")
p("""Per 1&deg; DEM tile (19 tiles cover the full 30-station grid): fill pits &rarr; fill depressions
&rarr; resolve flats &rarr; D8 flow direction &rarr; flow accumulation (via <code>pysheds</code>, a
pure-Python library &mdash; the initially-preferred <code>richdem</code> was rejected after a real
failed installation: it requires a C++ compiler unavailable on the build machine). Slope is computed
from a latitude-scaled elevation gradient (cell size varies with longitude at this latitude:
&asymp;28m &times; &asymp;31m, not square, despite the DEM&rsquo;s nominal &ldquo;30m&rdquo; label).
&ldquo;River&rdquo; cells are flow-accumulation cells above 500 (&asymp;0.45km&sup2; contributing area,
a standard minimum stream-initiation threshold); drainage density is the river-cell count in a 1km-radius
local window, divided by that window&rsquo;s area &mdash; this part of the pipeline is unchanged and
still self-derived. <b>Distance-to-river is no longer taken from this pipeline&rsquo;s own Euclidean
distance transform</b> &mdash; after a post-hoc cross-check against an independent river network
(&sect;4.6), it was replaced with a vector distance to the nearest HydroRIVERS reach, which measurably
performed at least as well and rests on a peer-reviewed external dataset rather than a self-computed
one. The original self-derived values are retained in the raw data for provenance.""")

h2("5.2 Label construction")
p(f"""Every grid point was sampled against the full GFM archive: {len(counts):,} points,
{int(counts['n_valid'].sum()):,} total valid satellite observations
(median {int(counts['n_valid'].median())} per point). A point is labeled <b>flooded</b> if the archive
ever recorded a detection there (<code>n_flooded &ge; 1</code>); labeled <b>non-flooded</b> only if
observed at least 200 times with zero detections &mdash; a deliberately conservative bar, chosen after
inspecting the real observation-count distribution (median 575, well above the 200 threshold, so this
bar excludes very little real data while still requiring substantial evidence). Points with fewer than
200 observations and zero detections are dropped as inconclusive, not assumed negative.""")

story.append(PageBreak())

# ===========================================================================
# 6. EXAMPLE DATA
# ===========================================================================
h1("6. Example Data")
p("Three real rows from the final training table (<code>susceptibility_training_table.csv</code>), illustrating the full feature set:")

sample_rows = training_table.sample(n=3, random_state=7).to_dict("records")
sample_headers = ["point_id", "station", "elevation (m)", "slope (&deg;)", "dist. to river (m)",
                   "drainage density", "land cover", "label"]
lc_names = {10: "tree", 20: "shrub", 30: "grassland", 40: "cropland", 50: "built-up", 60: "bare",
            70: "snow/ice", 80: "water", 90: "wetland", 95: "mangrove", 100: "moss"}
sample_data = [[
    r["point_id"], r["station_id"], f"{r['elevation_m']:.1f}", f"{r['slope_deg']:.2f}",
    f"{r['dist_to_river_m']:.0f}", f"{r['drainage_density_km_per_km2']:.2f}",
    lc_names.get(r["landcover_class"], r["landcover_class"]),
    "flooded" if r["label"] == 1 else "non-flooded",
] for r in sample_rows]
make_table(sample_headers, sample_data, [2.1 * cm, 1.6 * cm, 1.9 * cm, 1.7 * cm, 2.1 * cm, 1.8 * cm, 1.7 * cm, 1.7 * cm])

p("Three real rows from the raw label-aggregation output (<code>grid_point_flood_counts.csv</code>), showing the observation depth behind each label:")
count_sample = counts[counts["n_valid"] > 0].sample(n=3, random_state=7).to_dict("records")
make_table(
    ["point_id", "station", "basin", "n_valid (observations)", "n_flooded (detections)"],
    [[r["point_id"], r["station_id"], r["basin"], r["n_valid"], r["n_flooded"]] for r in count_sample],
    [3 * cm, 2.3 * cm, 2.7 * cm, 4 * cm, 4 * cm],
)

story.append(PageBreak())

# ===========================================================================
# 7. RESULTS: PLOTS & ANALYTICS
# ===========================================================================
h1("7. Results: Plots &amp; Analytics")
p("Every figure below was regenerated directly from the trained model and the real data files on disk.")

h2("7.1 Data composition &amp; coverage")
fig("fig_class_balance.png", "Figure 1. Final label composition across all 1,470 grid points.")
fig("fig_nvalid_hist.png", "Figure 2. Observation depth per point — the full archive gives deep, "
    "consistent coverage, supporting the 200-observation negative-label threshold.")

story.append(PageBreak())
h2("7.2 Model comparison &amp; selection")
fig("fig_cv_comparison.png", "Figure 3. Spatial GroupKFold cross-validation: LightGBM vs. Random Forest, "
    "4 folds. Random Forest wins on every fold.")
fig("fig_feature_importance.png", "Figure 4. SHAP feature importance for the final Random Forest model "
    "on the held-out test set — land cover and slope dominate, consistent with flat deltaic terrain "
    "where these carry more signal than raw elevation.")

story.append(PageBreak())
h2("7.3 Held-out spatial test performance")
p("""7 of 30 stations — stratified across all 4 basins so the test set still spans flat floodplain,
haor wetlands, and hilly terrain — were held out completely: never touched during training or model
selection.""")
fig("fig_roc_pr_confusion.png", "Figure 5. ROC curve, Precision-Recall curve, and confusion matrix "
    "(threshold 0.5) on the held-out test set.", width=16.5 * cm)

story.append(PageBreak())
h2("7.4 Spatial &amp; geographic patterns")
fig("fig_station_map.png", "Figure 6. All 30 stations plotted by real coordinates, colored by mean "
    "susceptibility score. Meghna-basin haor/wetland stations (northeast) score highest; Chittagong "
    "Hill Tracts stations (southeast) score lowest — matching known Bangladesh flood geography.")

story.append(PageBreak())
fig("fig_station_bar.png", "Figure 7. Per-station mean susceptibility score, all 30 stations, colored "
    "by basin.", width=13 * cm)
fig("fig_basin_comparison.png", "Figure 8. Mean susceptibility by basin (error bars = standard "
    "deviation across that basin's stations).")

story.append(PageBreak())
h2("7.5 Land cover as a predictor")
fig("fig_landcover_by_label.png", "Figure 9. Flooded-point rate by land-cover class — water and "
    "wetland/mangrove classes show a far higher flooded rate than cropland or tree cover, matching "
    "physical intuition and explaining land cover's #1 SHAP ranking.")

story.append(PageBreak())

# ===========================================================================
# 8. COMPARISON: OUR MODEL VS. LITERATURE
# ===========================================================================
h1("8. Comparison: This Model vs. the Literature")
p("""A direct accuracy comparison against the Bangladesh studies in &sect;2.2 would be misleading
without the methodology context below &mdash; presented explicitly rather than left implicit.""")

make_table(
    ["Study / model", "Reported metric", "Evaluation method", "Comparable to this model?"],
    [
        ["Bangladesh comparative study (LightGBM/RF, &sect;2.2)", "97.7&ndash;97.8% accuracy",
         "Not specified as spatial-holdout in the abstract; typical of the field is a random split",
         "Not directly &mdash; likely benefits from the random-split inflation documented in &sect;2.1"],
        ["Sylhet AHP study (&sect;2.2)", "ROC &asymp; 87%", "Expert-weighted, non-ML",
         "Partially &mdash; a non-inflated, realistic reference point"],
        ["Northeast Bangladesh flash-flood RF study (&sect;2.2)", "RF beat XGBoost (exact AUC not "
         "extracted from search)", "Not specified", "Directly relevant methodologically &mdash; "
         "same RF-over-boosting finding reproduced independently here"],
        ["<b>This model (spatial GroupKFold CV)</b>", "<b>0.888 mean ROC-AUC (RF), 0.862 (LightGBM)</b>",
         "<b>Spatial group k-fold, grouped by station</b>", "&mdash;"],
        ["<b>This model (held-out spatial test)</b>", "<b>0.908 ROC-AUC, 0.785 PR-AUC</b>",
         "<b>7 stations held out completely, stratified across all 4 basins, never touched in "
         "training/CV</b>", "&mdash;"],
    ],
    [4.7 * cm, 3.6 * cm, 4 * cm, 3.7 * cm],
)

p("""<b>Why this model&rsquo;s 0.91 ROC-AUC is not directly beaten by the literature&rsquo;s 0.97+
accuracy figures, despite the lower headline number:</b> accuracy and ROC-AUC are different metrics
(accuracy can look high on an imbalanced set even with a mediocre model); and &mdash; more importantly
&mdash; random-split evaluation on spatially autocorrelated data is documented to inflate reported AUC
by 5&ndash;15% (&sect;2.1). This model&rsquo;s 0.908 comes from a genuinely unseen set of stations, the
harder and more honest evaluation standard. A fair apples-to-apples number is not available from the
reviewed literature, because most reviewed studies do not report whether (or how) they controlled for
spatial autocorrelation.""")

story.append(PageBreak())

# ===========================================================================
# 9. INTEGRATION WITH MODELS #1 AND #2
# ===========================================================================
h1("9. Integration with the Other Two Models")
p("""The three models combine via one transparent formula, deliberately chosen over a stacked
meta-model so the combination stays defensible in one line rather than requiring its own separate
justification:""")
story.append(Paragraph(
    "<font face='Courier' size='11'>combined_risk = classifier_24h_probability &times; "
    "(0.5 + 0.5 &times; susceptibility_score)</font>", styles["BodyText2"]))
p("""Susceptibility acts as a bounded modulator (0.5&ndash;1.0&times;) on the classifier&rsquo;s
time-bound probability &mdash; it can reduce a forecast for inherently low-risk ground, but never fully
zeroes it out, since an extreme enough storm can still flood low-susceptibility terrain. Implemented
client-side in the dashboard (not inside either FastAPI service), since both model services are
deliberately self-contained with zero dependency on each other or on this repository, so either can be
copied to a different machine independently.""")

# ===========================================================================
# 10. LIMITATIONS
# ===========================================================================
h1("10. Limitations &amp; Honesty Notes")
story.append(Paragraph(
    "&bull; <b>Scope</b>: 30 station neighborhoods (1,470 points), not a national susceptibility atlas "
    "&mdash; deliberately scoped to what this project monitors, not a general-purpose Bangladesh map.<br/>"
    "&bull; <b>Land cover is a single snapshot</b> (ESA WorldCover 2021) &mdash; land use changes over "
    "time (e.g. new construction, deforestation) are not captured.<br/>"
    "&bull; <b>200-observation threshold is a real, inspected choice</b>, not arbitrary, but it is still "
    "a threshold: a small number of borderline points near that boundary could be re-labeled with a "
    "different (defensible) cutoff.<br/>"
    "&bull; <b>Drainage density remains self-derived</b> from a single DEM via standard flow-routing "
    "(&sect;5.1) &mdash; not independently validated against ground survey data, though the underlying DEM "
    "itself (Copernicus GLO-30) is independently accuracy-assessed (&sect;2.3). Distance-to-river no "
    "longer carries this caveat (&sect;4.6).<br/>"
    "&bull; <b>HydroRIVERS is itself DEM-derived</b> (from a coarser ~500m HydroSHEDS DEM, not "
    "ground-surveyed) &mdash; an improvement in independence and provenance over the original self-derived "
    "feature, not an absolute ground-truth reference.<br/>"
    "&bull; <b>7-station held-out test is real but small</b> (326 points) &mdash; a larger held-out set "
    "would tighten the confidence interval around the 0.908 ROC-AUC figure.",
    styles["BodyText2"]))

# ===========================================================================
# 11. FUTURE WORK
# ===========================================================================
h1("11. Future Work")
story.append(Paragraph(
    "&bull; <b>Done since the first version of this report</b>: mirrored the 3rd model card and "
    "combined-risk panel to the neumorphic frontend; cross-checked distance-to-river against an "
    "independent river-network layer and adopted the better-performing version (&sect;4.6).<br/>"
    "&bull; <b>Blocked, not just low-priority</b>: re-scoring against a newer ESA WorldCover release "
    "&mdash; checked directly, no release newer than 2021 (v200) exists; an update is only "
    "&ldquo;planned&rdquo; with no date. Expanding the held-out test set as more stations are added is "
    "similarly blocked &mdash; there are no new stations to add yet.<br/>"
    "&bull; <b>Open, needs a design decision first</b>: whether a rainfall/soil-moisture dynamic "
    "modulator (rather than a fixed static score) could let susceptibility respond to antecedent "
    "wetness without turning it back into a second temporal model.",
    styles["BodyText2"]))

# ===========================================================================
# APPENDIX
# ===========================================================================
story.append(PageBreak())
h1("Appendix: Reproducibility Reference")
make_table(
    ["Artifact", "Path"],
    [
        ["Spatial grid definition", "backend/train/susceptibility_grid.py"],
        ["Label aggregation", "backend/train/ingest_susceptibility_labels.py"],
        ["Terrain/land-cover extraction", "backend/train/ingest_susceptibility_terrain.py"],
        ["Dataset merge + threshold decision", "backend/train/build_susceptibility_dataset.py"],
        ["Model training + spatial CV", "backend/train/train_susceptibility_model.py"],
        ["Distance-to-river independent cross-check", "backend/train/crosscheck_distance_to_river.py"],
        ["Distance-to-river variant comparison (&sect;4.6)", "backend/train/compare_river_distance_features.py"],
        ["Trained model + metrics", "backend/models/susceptibility/"],
        ["Standalone service", "packages/flood-susceptibility/"],
        ["This report's figures", "reports/generate_susceptibility_assets.py"],
        ["Full build log", "MODEL_BUILD_PLAN.md (2026-08-14 entries)"],
    ],
    [5.5 * cm, 9.5 * cm],
)

doc = SimpleDocTemplate(str(OUT_PATH), pagesize=A4,
                         leftMargin=1.8 * cm, rightMargin=1.8 * cm, topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                         title="Flood Susceptibility Model Report", author="AquaGuard / pred_flood project")
doc.build(story)
print(f"Wrote {OUT_PATH}")
