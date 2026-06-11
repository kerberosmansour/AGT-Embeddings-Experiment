# Two-Inspector Ensemble — findings & two recommendations

**Exploratory sandbox result. Existing data only. Synthetic, labels-perfect —
every number is a ceiling that will move on real traffic.**

## The idea (founder's framing)

Two inspectors look at the same request. One is precision-first (rarely cries
wolf), one is recall-first (catches lots, but noisy). When they **agree**, it's
easy. When they **disagree**, that's where you spend extra effort — bring in
independent structural facts to break the tie. We tested this on the data we have.

## What "two inspectors" means here

- **Precision inspector** = the Gate-0 + kNN margin at its zero-FP line (43% catch, 0% FP).
- **Recall inspector** = the same margin at the aggressive Youden line (catches more, ~7% FP alone).
- The **disagreement band** = requests scoring *between* the two lines: 406 benign, 1,293 attacks.
- **Genuine second model**: we also have the round-6 **trained head** — a
  *different* detector that disagrees with the kNN by family (the head catches
  prompt_leakage, which the kNN scores 0% on). That is the truest form of "two
  inspectors," and it does the heavy lifting in Recommendation B.

## The two recommendations

Baseline to beat = **Experiment 1: 81% catch @ 0% false-positives.**

| | Rule (in the disagreement band, block if…) | Catch | False-positives |
|---|---|---:|---:|
| **Experiment 1 (baseline)** | — | 81.0% | 0.00% |
| **Rec B — keep 0% FP** | the **second model (head)** is independently confident | **87.2%** | **0.00%** |
| **Rec B+ — keep 0% FP** | second model confident **OR** it's a tool call | **90.7%** | **0.00%** |
| **Rec A — spend a little FP** | **any** structural fact agrees (untrusted / tool / sink) | **99.9%** | **0.26%** |

Both recommendations beat 81%. You pick the trade-off:

- **Rec A (you'll accept ~0.3% FP):** ~**99.9% catch** — every attack family near
  100%. This is the "sacrifice a little, gain a lot" option.
- **Rec B (you refuse to add *any* FP):** **87–91% catch**, still at a measured
  **0%**. This is the "push the needle for free" option.

## Why Rec B works at zero added FP

In the disagreement band, **0 of the 406 benign rows** are flagged by the second
model's own high-confidence line (verified, validation-frozen) — but hundreds of
attacks are. So "the two models *agree* it's bad" is a tie-breaker that, on this
data, never fires on a benign row. The standout: the head **rescues
prompt_leakage**, which the kNN inspector misses entirely — exactly the
"informative disagreement" the founder described.

## Robustness: Rec B vs Rec B+ (higher catch ≠ more robust)

Both hold 0% FP on this data — but for different reasons, and that decides which
one survives real traffic.

| | Tie-breaker | Why 0 benign in the band | Robustness |
|---|---|---|---|
| **Rec B** | 2nd model agrees | a benign must **fool two different models at once** | mechanism-based → **robust** |
| **Rec B+** | *or* it's a tool call | the corpus has **no benign tool-use in the band** | artifact-based → **fragile** |

Rec B+'s extra catch (461 attacks, +3.5 pts) comes **only** from the tool-call
predicate, whose 0% FP is the same empty-quadrant artifact as the earlier R1
rule. In production, legitimate tool-use that scores mid-range lands exactly in
this band and would become false positives — so Rec B+'s zero is borrowed against
the synthetic data. **Rec B's** zero rests on independence (two different models
agreeing on a mistake is genuinely hard) and should degrade gracefully. Rec B is
also more *adversarially* robust: evading it means scoring low on two independent
models at once.

**Verdict: Rec B (87%) is the bankable 0%-FP choice; Rec B+ (91%) trades
robustness for catch.** The clean way to recover B+'s catch *with* robustness is
to replace the bare tool predicate with a **third independent signal** (another
model, or requiring the 2nd model to at least lean attack) — a thread for the
next round.

## Honest caveats (what the data does *not* tell us)

- **Rec A's 99.9% is inflated.** It leans on a corpus artifact: "has a structural
  handle" ≈ "is an attack," because nearly every synthetic attack is
  untrusted-sourced and nearly every high-scoring benign row is trusted. Real web
  agents act on untrusted content constantly — that breaks the correlation, so the
  real FP will be higher and catch lower.
- **Rec B is more robust but still synthetic.** Its zero-FP rests on the second
  model having **0 benign** in the band on *this* split. That's a genuinely
  independent agreement signal (two different models), which is the strongest
  version of the idea — but real benign traffic could put benign rows in that
  region. The tool-call predicate in Rec B+ carries the same empty-quadrant
  caveat as the earlier R1 rule.
- **Single margin ≠ two models for the precision/recall split.** The
  precision/recall inspectors are two *thresholds on one margin* (perfectly
  correlated). Only the head-vs-kNN pairing is a true two-model ensemble. The
  full strength of the founder's idea wants two *genuinely different* detectors;
  we have one such pair (kNN + head) and it already helps.
- **Prompt injection only**, single-input, single-agent — same scope limits as
  Experiment 1. One of six *AI Agent Traps* categories.

## The follow-up this points to (the real ask)

**Get more realistic benign data** — legitimate "untrusted content triggers an
action" flows, and benign requests that score mid-range on the detectors. That is
the one thing that would turn these ceilings into believable numbers. Until then:
the architecture is promising and clearly better than what we have, but the exact
figures need that data plus independent review.

## Verdict (Definition of Learned)

- **Learned:** resolving inspector-disagreement with an independent signal is real
  and measurable — **+6 to +10 points of catch at 0% added FP** (Rec B), or near-
  total catch at ~0.3% FP (Rec A). The two-model (kNN + head) version is the most
  defensible and rescues a family neither structural rules nor the kNN could.
- **Not yet known:** the true false-positive cost, because the benign data lacks
  the hard cases. **Disposition: promote to a real experiment _gated on new benign
  data_.** Promising; better than current; get more data before believing the
  headline.
