# Experiment 3 — Two-Inspector Ensemble

**Key finding:** two ways to push prompt-injection catch past Experiment 1's
**81% @ 0% false-positives**, using only data we already have — **87% while
staying at a genuine 0% false-positives**, or **~99.9% if you'll accept ~0.3%**.
The robust win comes from making **two different detectors agree** before acting
on a borderline case.

*Exploratory sandbox result on a frozen synthetic test set. Every number is a
labels-perfect ceiling that will move on real traffic — see caveats.*

## The idea (in one picture)

Two inspectors look at the same request:

- a **precision inspector** — the Gate-0 + kNN detector at its zero-false-positive
  line (rarely wrong, lower catch), and
- a **recall inspector** — the same signal at an aggressive line (higher catch,
  noisier).

When they **agree**, the call is easy. The interesting cases are the
**disagreement band** between the two lines — here, **1,293 attacks and 406
benign**. The whole experiment is about how to resolve that band *without* adding
false-positives. The best resolver turns out to be a genuinely **independent
second model** — the round-6 trained head — voting on the same request.

## The two recommendations

Baseline to beat = **Experiment 1: 81% catch @ 0% false-positives.**

| | In the disagreement band, block if… | Catch | False-positives | Robustness |
|---|---|---:|---:|---|
| Experiment 1 (baseline) | — | 81.0% | 0.00% | — |
| **Rec B — keep 0% FP** | the **2nd model** independently agrees | **87.2%** | **0.00%** | **robust** |
| Rec B+ — keep 0% FP | 2nd model agrees **or** it's a tool call | 90.7% | 0.00% | fragile (see below) |
| **Rec A — spend a little FP** | **any** structural fact agrees | **99.9%** | **0.26%** | inflated (see below) |

- **If you refuse to add any false-positives:** **Rec B** lifts catch 81% → **87%**
  for free. It specifically rescues `prompt_leakage` — a family the precision
  inspector scores 0% on but the second model nails.
- **If you'll accept ~0.3% false-positives:** **Rec A** reaches **~99.9%**, every
  attack family near 100%.

## Robustness — higher catch is *not* more robust

Rec B+ shows a bigger number (91%) than Rec B (87%), but it is **less robust**,
and that matters more than the headline:

| Tie-breaker | Why it has 0 benign in the band | Holds on real traffic? |
|---|---|---|
| **Rec B** — 2nd model agrees | a benign must **fool two different models at once** | **yes — mechanism (independence)** |
| Rec B+ — *or* a tool call | the corpus has **no benign tool-use in the band** | **no — synthetic artifact** |

Rec B+'s extra catch (461 attacks) comes *only* from the tool-call predicate,
whose zero false-positives is the same empty-quadrant artifact we flagged in
Experiment 1. In production, legitimate tool-use that scores mid-range lands in
exactly this band and would become false-positives. **Rec B's** zero rests on
independence — two different detectors agreeing on a mistake is genuinely hard —
so it should degrade gracefully, and it's harder to evade (an attacker must beat
both models at once).

**Bank Rec B.** Rec B+'s extra points are real catch, but its zero is borrowed
against the synthetic data.

## Caveats (what the data does *not* tell us)

- **Rec A's 99.9% is inflated** by a corpus artifact: "has a structural handle" ≈
  "is an attack," because almost every synthetic attack is untrusted-sourced.
  Real web agents act on untrusted content constantly — that breaks the
  correlation, raising FP and lowering catch.
- **Rec B is the most defensible but still synthetic.** Its zero rests on the
  second model having no benign in the band on *this* split.
- **Prompt injection only**, single-input, single-agent — one of six *AI Agent
  Traps* categories (Google DeepMind). Same scope as Experiment 1.
- **Not independently verified.** Every number is ours, on our data.

## What this points to

1. **Get realistic benign data** — legitimate "untrusted content triggers an
   action" flows and mid-scoring benign requests. This is the one thing that
   turns these ceilings into believable numbers.
2. **Recover Rec B+'s catch *with* robustness** by replacing the bare tool fact
   with a **third independent signal** (another model, or requiring the second
   model to at least lean attack) rather than a structural shortcut.
3. **Independent review** before any deployment claim.

**Disposition:** promising, and clearly better than the current stack. Promote to
a funded experiment **gated on new benign data**.

## Reproduce

`meta/harness/exp3-two-inspector/play.py` recomputes every number from committed
artifacts (round-6 kNN margins + trained-head scores + corpus governance fields).
No model run, no new data. Process record: `docs/slo/experiments/two-inspector-ensemble/`.
