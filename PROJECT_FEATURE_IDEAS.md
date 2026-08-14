# Overall Project — Software Feature Ideas Backlog

Scope note: this file tracks feature ideas for the **whole capstone project** (the IoT pond-management
system: pH/turbidity/temp/ultrasonic water-level/soil sensors + 2 water-exchange motors, plus the
flood-risk model in this repo). `MODEL_BUILD_PLAN.md`/`DECISIONS.md` stay scoped to the flood model
specifically — this file is where broader system-level ideas live so they don't get mixed in.

Status as of 2026-08-09: **discussion/planning stage only, nothing built yet.** The flood-model work
itself is paused pending advisor feedback (see `MODEL_BUILD_PLAN.md`'s last entry) — these are ideas to
have ready for when that conversation happens, not a commitment to build them.

## Candidate features (researched 2026-08-09, see citations)

Researched what real smart-aquaculture/IoT pond systems actually include — both published research and
commercial products — before proposing anything, rather than brainstorming from scratch. Sources:
[ResearchGate — Smart Aquaculture cost-effective IoT model](https://www.researchgate.net/publication/390418643_Smart_Aquaculture_A_Cost_Effective_IoT_Integrated_Model_for_Monitoring_Environmental_and_Pond_Parameters),
[Springer — IoT ensemble ML for dissolved oxygen prediction](https://link.springer.com/article/10.1007/s43926-025-00201-w),
[ScienceDirect — real-time water quality monitoring with DO/ammonia sensors](https://www.sciencedirect.com/science/article/pii/S0144860925001098),
[Agrinovo — commercial IoT aquaculture monitoring](https://agrinovo.io/solutions/iot-aquaculture-monitoring/).

Ranked by fit for this project's remaining time/skills, not just novelty:

1. **Local water-quality forecasting model** (highest recommended priority) — reuse the exact same
   pipeline built for the flood model (feature engineering, honest time-based evaluation, threshold
   tuning, SHAP explanation) but trained on the pond's own sensor history to predict tomorrow's
   pH/turbidity/DO trend *before* it crosses a dangerous line. Mirrors the flood model's "proactive vs.
   reactive" story; near-zero new skills needed since it's the same methodology applied to different data.
2. **A real dashboard/web app** — live sensor readings + flood risk + historical trends + active alerts
   in one place. Currently the flood side has a backend API but no user-facing view. Matters a lot for a
   live defense demo.
3. **Historical sensor data logging** — groundwork for #1 and #2; without it there's only live snapshots,
   no real trend evidence to show.
4. **SMS/push alerting** — cheap once a backend + thresholds exist; well-precedented across every real
   system found; useful for a farmer not watching a screen.
5. **Lightweight anomaly detection on the raw sensor stream** — flags a physically implausible sudden
   jump (sensor fault or genuine crisis), complementing the existing threshold-triggered motors with
   something smarter than a single noisy reading.

**Flagged but explicitly not decided (hardware/budget call, not software):** dissolved oxygen (DO)
sensing. It showed up as the single most consistently-cited critical parameter across every source
checked (most-common direct cause of fish kills) and is the one major parameter the current sensor list
doesn't cover. Worth raising with the advisor alongside the software questions, not something to
silently add or silently ignore.

## Discussion log

### #1 (local water-quality forecasting model) — scoped in detail, 2026-08-09

Discussed in depth rather than just approved. Two real constraints surfaced that change how/when this
can be built, not whether it's a good idea:

- **Testbed is an aquarium, not a real pond** — clarified this is a deliberate, reasonable choice: no
  access to a real pond to test on, so the aquarium is a lab-safe physical stand-in/prototype. The
  actual target deployment is still real outdoor aquaculture ponds, so the flood-risk model's whole
  framing stays valid and unchanged — nothing about the flood side needs to shift because of this.
- **No real historical sensor data exists yet, and won't accumulate on its own** — the aquarium isn't
  run continuously; it's only assembled for demo sessions, not left running as a standing testbed. This
  isn't a power/hardware blocker (it's mains-powered, indoors) — it's simply that nothing has been
  logging data over time yet.

**Decision: do not build the forecasting model on fabricated/simulated data** — same standard this
project has held throughout (see e.g. the rejected GitHub "flood index" dataset, `DECISIONS.md`). A
model built without real data would not be defensible and isn't worth pretending otherwise.

**Two honest paths identified, decision deferred to the user (time/schedule call, not a technical one):**
1. Deliberately run the aquarium continuously as a standing data-collection testbed (separate from demo
   sessions) for some real stretch of time (2-3+ weeks as a starting point) — then build the real,
   honestly-evaluated forecasting model once that data exists. Same rigor as the flood model.
2. If there isn't time before the defense: build a **rule-based (not learned) safety layer** instead —
   real published safe/danger ranges for pH/turbidity/temperature, deployable immediately with no data-
   history requirement, honestly presented as rule-based now / upgradeable to a learned model later once
   field data exists. Offered to research real threshold values for this next — not yet done as of this
   entry, pending the user's choice of path.

Not resolved yet: which path the user wants to take. Revisit this file's status when they decide.
