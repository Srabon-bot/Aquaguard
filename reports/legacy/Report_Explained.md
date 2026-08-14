# Understanding Your Flood Model Report — Plain-Language Walkthrough

This is a companion to `Flood_Model_Report.pdf`. It goes through the report section by section and
explains every concept in plain language, using your own actual numbers as worked examples — not
textbook examples — so you can defend this in front of your advisor without needing me there.

Read it in order. Each section matches a section in the PDF report.

---

## The one-sentence version

We built two different AI models that both try to answer "is this river going to be dangerous soon,"
using free weather/satellite data instead of expensive gauges, and we're honest in the report about
where each model is strong and where it's weak.

---

## Section 1-2: Data Collection

### What "training data" actually means

Think of the model like a student cramming for an exam using old exam papers. The "old exam papers"
here are **839,340 rows** — each row is one river station, on one day, with: how much it rained, how
wet the soil was, how much water was flowing in the river, and (when we know it) whether a flood
happened. The model studies all these old rows to learn the pattern "when rainfall/soil/discharge look
like THIS, a flood tends to follow."

### Why we needed 8 different data sources, not just one

Here's the problem we had: the *one* source that tells us for sure "flood happened / no flood
happened" (NASA's GFMS satellite) only has clean records for two time windows — 2013-2016 and
2021-2026. Everywhere else in time (like the 1990s, or 2017-2020), we simply don't have a reliable
"no flood happened" signal.

So we found **4 more sources** (DFO, Global Flood Database, Copernicus satellite radar, and FFWC's own
government reports) that each independently confirm "yes, a flood happened here on this date." Think of
it like eyewitnesses: if 5 different reliable sources ever say "there was a flood in Sirajganj on July 5,
1995," we trust that. But if NONE of them mention Sirajganj on August 3, 1995 — that does **not** mean
we're sure it was dry. Maybe it flooded and nobody happened to record it. So we only treat GFMS's
window as strong enough evidence to say "definitely no flood" — everywhere else, silence just means
"we don't know," not "safe."

**This is the blue-vs-orange chart (Figure 2) in the report.** Blue years = we have BOTH real "yes" and
real "no" answers (reliable). Orange years = we only ever get "yes" answers from those years, never a
confirmed "no" (sparse, one-sided).

### Why we show 3 example data rows (the "good/incomplete/bad" page)

This page exists because your advisor's first instinct will be "how do you know your data is actually
correct?" So instead of just claiming it's clean, we show real proof:

- **(a) Good** — a totally normal row: on 2021-05-24 at Bahadurabad, it rained 10.8mm, the river was
  flowing at 23,119 m³/s, and yes, satellites directly saw a flood happen within 72 hours. Nothing
  missing, nothing guessed.
- **(b) Incomplete** — an *honest* gap: back in 1988, we don't have river-flow data (that data source
  only starts in 1997), so that field is literally marked "missing," not filled in with a fake guess
  like 0 or an average. This matters a lot — if we had secretly filled in a 0, the model would think
  "0 flow" is normal, which is completely wrong and would corrupt its understanding of real danger
  levels.
- **(c) Bad — data we caught and threw away** — this is the most important one to be able to explain,
  because it shows *judgment*, not just data collection. Two real examples:
  1. A government report sentence said a river was **2cm BELOW** the danger line — but it still
     mentioned a date. A lazy script would see "date mentioned" and wrongly log it as a flood day. We
     specifically built a check for the word "below" (and similar phrases) so sentences like this get
     thrown out instead of poisoning our data. We found **73 of these** in our first attempt (12% of
     everything we'd grabbed) — a real bug we caught before it did damage, not a hypothetical.
  2. We found a public dataset online claiming to have real flood data for 34 stations. We didn't just
     trust it — we plotted its values and found it was secretly just a monsoon-season calendar (high
     every June-October, low every other month, every single year, with **no connection to whether an
     actual flood happened** that year). We rejected the whole dataset rather than let the model
     "cheat" by learning to predict the calendar instead of real weather.

**If your teacher asks "how do you know your data is trustworthy?" — this page is your answer.**

---

## Section 3: Model 1 — The Classification Model

### What "classification" means here

This model looks at today's conditions and answers a yes/no question 3 separate times: "will there be a
flood in the next 24 hours? the next 48? the next 72?" It doesn't give one number — it gives 3
independent risk levels, like a 3-day weather forecast that gets a little less certain the further out
it looks.

### What LightGBM is (in plain terms)

Imagine 1,000 very simple decision-makers, each one only asking a few basic yes/no questions like "is
14-day rainfall above 150mm?" or "is it currently monsoon season?" Each one alone is a weak guesser.
LightGBM trains all 1,000 of them one after another, where each new one focuses specifically on fixing
the mistakes the previous ones made. Combined together, their votes make a much stronger prediction
than any single one. This is called "gradient boosting" — it's one of the most common, reliable methods
for this kind of tabular (spreadsheet-like) prediction problem, which is why we picked it over something
fancier like a neural network.

### The most important concept to understand cold: Precision vs. Recall

This is almost certainly what your advisor will ask about, so let's really nail it using your own
numbers from the 72-hour model:

- **Recall = 85%** means: out of every 100 REAL floods that actually happened, our model successfully
  raised an alarm for 85 of them (and missed 15).
- **Precision = 18.4%** means: out of every 100 times our model says "HIGH RISK," only about 18 of those
  times does a flood actually follow. The other 82 times are false alarms.

Why would we deliberately accept so many false alarms? Because of **which mistake is worse**. Think
about it like a smoke detector: a smoke detector that goes off a bit too often (false alarms) is
annoying but safe. A smoke detector that stays silent during a real fire (a missed flood) can kill
someone. We tuned our model the same way — we told it "I'd rather you cry wolf sometimes than stay
silent during a real flood," which is exactly what setting `recall = 85%` as our target does.

**The exact math, using your 72h confusion matrix (Figure 5):**

| | Model said "Flood" | Model said "No Flood" |
|---|---|---|
| **Actually flooded** | 1,440 (caught it ✅) | 254 (missed it ❌) |
| **Actually fine** | 6,400 (false alarm) | 14,736 (correctly quiet) |

- Recall = 1,440 ÷ (1,440 + 254) = **85%** ✅ (we catch 85 out of every 100 real floods)
- Precision = 1,440 ÷ (1,440 + 6,400) = **18.4%** (only 18 out of every 100 "flood" alerts are real)

**If your teacher asks "why is your precision so low, isn't that bad?"** — your answer: "We deliberately
chose that tradeoff. Floods are rare events (only ~7% of days), and for a warning system, a missed flood
is far more costly than an extra false alarm, so we tuned the alert threshold to prioritize catching
real floods over minimizing false alarms — the same logic real weather-warning systems use."

### What ROC-AUC actually measures (and why it's a DIFFERENT, better-looking number than precision)

ROC-AUC (0.85-0.88 for us) answers a different question than precision: "if I show the model one day
that really flooded and one day that didn't, how often does it correctly rank the flood day as riskier?"
Our answer: about 85-88% of the time. This is a genuinely good score (0.5 would mean random guessing,
1.0 would mean perfect). It's a fair test that the model has actually learned something real, separate
from the precision/recall threshold argument above.

**Why we show BOTH ROC-AUC (good-looking) and precision (not-so-good-looking) instead of just
picking the flattering one** — because that would be dishonest, and any advisor experienced with ML
will ask about precision anyway if you only show ROC-AUC. Showing both, with the honest explanation
above, is what makes the report credible.

### What SHAP feature importance means (Figure 6)

SHAP tells you which inputs the model actually leans on to make its decision — like asking "which
ingredients most decide whether this recipe tastes good?" Our #1 feature is **14-day cumulative local
rainfall** — makes complete physical sense (heavy sustained rain → flooding). This is a good sanity
check: if the #1 feature had been something nonsensical (like "day of the week"), that would be a red
flag that the model learned a fake pattern instead of real hydrology. Ours makes sense, which is
reassuring evidence the model is learning real physics, not a coincidence in the data.

---

## Section 4: Model 2 — The Discharge Regression Model

### "Regression" vs "Classification" — the key difference

Classification (Model 1) answers yes/no. **Regression (Model 2) predicts an actual number** — in our
case, "how many cubic meters of water per second will be flowing through this river in 3 days?" instead
of just "flood yes/no."

### Why we built a second, totally different model

The honest reason: Model 1's biggest weakness is that real confirmed flood days are rare and our
"definitely no flood" data only covers certain years. River flow (discharge), on the other hand, has a
real number recorded on almost every single day since 1997 — no rare-event problem at all. So instead
of asking a hard question (rare yes/no) we asked an easier, more data-rich question (a number that's
almost always available) as a second angle on the same problem.

### Why we used `log(1 + discharge)` instead of the raw number

This one sounds technical but the idea is simple. Imagine trying to measure both an ant and an elephant
with the same ruler, and you care equally about being accurate for both. Our rivers range from **~2
cubic meters/second** (a small drainage canal) to **~39,000 cubic meters/second** (the biggest river
confluence) — that's a 20,000x difference! If we trained the model without adjusting for this, it would
basically ignore the small rivers entirely, because getting the giant river's number slightly wrong
"costs" way more in the math than getting every small river completely wrong. Taking the logarithm
levels the playing field, so the model tries equally hard on every river regardless of its size.

### Why we compare to a "persistence baseline" — and why this is the most important idea in this whole model

Here's a trap that's very easy to fall into: river flow tomorrow is usually pretty close to river flow
today (rivers don't change drastically overnight). So if you just guessed "tomorrow = same as today"
with ZERO machine learning, you'd already look pretty accurate. This naive guess is called the
**persistence baseline**.

If we had only reported "R² = 0.996" (Figure/Table 4.3), that would be almost meaningless bragging,
because a naive guess would ALSO score close to that. What actually proves our model learned something
is comparing it against that naive guess directly:

| Horizon | Naive guess error | Our model's error | Real improvement |
|---|---|---|---|
| 24h ahead | 361 m³/s off | 321 m³/s off | **11% better** |
| 48h ahead | 675 m³/s off | 534 m³/s off | **21% better** |
| 72h ahead | 937 m³/s off | 672 m³/s off | **28% better** |

**And notice the pattern**: our advantage over the naive guess GROWS the further ahead we predict. That
makes physical sense — "just assume nothing changes" gets worse and worse the further into the future
you push it, while our model keeps learning from rainfall/soil/upstream signals. This growing gap is the
real evidence of skill.

**If your teacher asks "why is R² not your headline number?"** — your answer: "R² looks artificially
high because of the huge size difference between rivers — a model that just gets each river's rough
scale right already scores well on R². The persistence comparison is a fairer test because it's
measured against a real naive alternative, not against zero."

---

## Section 5: Live Serving

This section is just saying: it's not only a research exercise sitting in a notebook — we built an
actual working pipeline that, right now, can take a real location, pull today's real weather data from
free live APIs, and spit out a real prediction. We also tested it against failure cases on purpose (bad
internet responses, wrong coordinates, etc.) to make sure it doesn't crash — that's normal, expected
software engineering practice, not an ML concept.

The finding that our live predictions sometimes disagree with FFWC's official real-time map is directly
connected to the precision discussion above — it's the "18% precision" limitation showing up in a real,
live example, not a new/different problem.

---

## Section 6: Limitations & Questions — how to talk about this page

This page is deliberately **not** "here's everything wrong with our project." Every point is framed as
"here's a real, honest tradeoff we made, and here's what we want your advice on." That framing matters
a lot in how you present it — don't apologize for these limitations, explain them as informed decisions
you're now seeking guidance on refining.

A simple way to introduce this page out loud: *"We want to be upfront about where the model's limits
are, because we think a realistic self-assessment is more useful to you than us just claiming it's
perfect. We've also turned each limitation into a specific question so you can help us decide what to
prioritize with our remaining time."*

---

## Quick-Reference Glossary

| Term | Plain meaning |
|---|---|
| **Feature** | One input the model looks at (e.g. today's rainfall) |
| **Label** | The real, true answer we're trying to teach the model (e.g. "yes, it flooded") |
| **Training data / test data** | Training = the "old exam papers" the model studies. Test = "new exam papers" it's never seen, used to fairly check how well it actually learned |
| **Classification** | Predicting a category (yes/no, flood/no-flood) |
| **Regression** | Predicting a number (e.g. river flow in m³/s) |
| **ROC-AUC** | How well the model ranks risky days above safe days (0.5=random, 1.0=perfect) |
| **Precision** | Of all the times we said "flood," what % were actually real floods |
| **Recall** | Of all the real floods that happened, what % did we catch |
| **Threshold** | The cutoff probability where we switch from saying "low risk" to "high risk" |
| **Confusion matrix** | A 2x2 table showing correct catches, misses, false alarms, and correct quiet days |
| **SHAP value** | A score showing how much one input feature actually influenced the model's decision |
| **Persistence baseline** | The naive "assume tomorrow = today" guess, used as a fair comparison point |
| **Overfitting** | When a model memorizes the training data instead of learning a real pattern (we guard against this with the strict time-based train/test split — the model is always tested on data from AFTER its training period, which it could not possibly have memorized) |

---

## A short script you could actually say out loud in your defense

*"We built two models on the same underlying dataset. The first predicts flood risk directly but has
low precision because true flood events are rare in our data — we accepted that tradeoff on purpose
because missing a real flood is worse than a false alarm. The second model sidesteps that rare-event
problem by predicting river discharge instead, which we can measure on almost every day, and we proved
it adds real value by beating a naive 'no change' guess by 11-28%, growing the further ahead we predict.
Both models are honestly evaluated, and we're here today specifically to get your guidance on which
direction to prioritize with our remaining time."*

That's genuinely everything in the report, in your own words. If you can explain the precision/recall
table above from memory, and the persistence-baseline table above from memory, you can defend this
whole report.
