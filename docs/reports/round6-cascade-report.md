# Round-6 — two-gate cascade experiment report

> **Caveats first.** All numbers are on the frozen **synthetic** round-4 corpus
> (44,800 templated rows); they are research evidence, not real-traffic or
> production-safety claims. Selection chained through one validation split
> (M2 head selection → M3 calibration → M4 arm training), so calibration
> guarantees are approximate; the frozen-test scoring is the arbiter. The
> conformal coverage guarantee is **benign-side only** and holds under
> exchangeability — it gives **no** protection against an adaptive adversary.
> Detection here is defense-in-depth, never the security boundary.

## What was tested

A four-stage cascade, each stage with **pre-registered** accept/kill thresholds
fixed before any data was seen (runbook §2):

```
Gate 0 normalize → Gate 1 score (head vs kNN) → 3-bucket conformal route → Gate 2 governance adjudication
```

## Consolidated verdict table (the pre-registered §2 gates)

| gate | result | verdict |
|---|---|---|
| M1 Gate 0 (de-obfuscation) | zero-FP recall 14.2% → **43.3%**; obf-control FP = 0 | **PARTIAL ACCEPT** (kill not triggered; word-boundary + multilingual residual) |
| M2 Gate 1 head (TPR@1%FPR + dominance) | head TPR@1%FPR 0.609; does **not** dominate kNN (kNN wins all FPR ≤ 1%) | **NOT SUPPORTED** (head ≈ kNN; normalization was the lever) |
| M2 LOFO (generalization) | median held-out TPR@1%FPR **0.716**; 0 families < 5% | **PASS** |
| M3 buckets (coverage) | benign escape 1.20% (1% inside Wilson [0.95%, 1.52%]) | **ACCEPT** |
| M3 buckets (queue precision @1:1000) | **5.07%** (≥ 5%) | **ACCEPT** (marginal) |
| M4 Gate 2 (floor beats control ≥5pt) | floor − control **+3.78pt** | **NOT MET** (real but < 5pt) |
| M4 Gate 2 (error independence ≤1.5) | miss-side overlap **2.76** | **NOT MET** — independence refuted |
| M4 Gate 2 (end-to-end ≥80% @ ≤1% FPR) | max **64.4%** @ 0.80% FPR | **NOT MET** — structural ceiling |
| M5 per-family floors (no family at 0%) | families at 0%: **none** | **PASS** |

Tally: 4 accept/pass, 1 partial, 4 not-met. The cascade's grand claims fail; the
component that mattered succeeds decisively; every question got a clean answer.

## The decisive positive: normalization (Gate 0)

Putting deterministic de-obfuscation **in front of all scoring** tripled the
zero-FP catch rate (14.2% → 43.3%) with the unchanged round-4 scorer and **zero**
benign-control false positives. End-to-end, the two attack families that sat at
**0%** in round 4 are now caught:

| family | round-4 @ FP-zero | round-6 cascade end-to-end |
|---|---:|---:|
| tool_abuse | 0% | 37.7% |
| prompt_leakage | 0% | 100% |
| direct_override | 22% | 99.1% |
| indirect_injection | 1.7% | 88.9% |
| output_exfiltration | 14% | 41.9% |

**No attack family is at 0%.** This directly fixes round-4's worst blind spots
and is the result most worth carrying upstream.

Residual (documented, not hidden): the word-boundary-destruction bypass cluster
(compact / chunked / separator-spaced) and multilingual attacks stay at 0% under
Gate 0 — both need transforms Gate 0 deliberately lacks (word segmentation,
translation). Future-round work.

## The decisive negatives

1. **A trained head does not beat kNN at deployable FPR** (M2). The literature's
   head-beats-kNN result did not reproduce on this corpus; kNN dominates every
   FPR ≤ 1%. The decision rule was never the bottleneck — normalization was.
2. **The two-gate independence assumption is refuted** (M4). Attacks Gate 1
   missed are missed by a shadow Gate 2 at 2.76× the base rate — the gates share
   blind spots because Gate 2's dominant feature is the same embedding-derived
   score. Real independence needs a genuinely cross-modal Gate 2 (e.g.
   activation-based task-drift detection), not a classifier over the same score.
3. **80% catch at ≤1% FPR is structurally unreachable here** (M4). M3's conformal
   pass lane sheds 35.6% of attacks to guarantee benign coverage, capping
   end-to-end recall at 64.4% regardless of Gate 2.

## The useful deployment finding (M4)

- **Free metadata ≈ full metadata.** The floor tier — fields every AGT
  deployment has for free (`requires_tool_call`, coarse source) — adds +3.8pt
  over score-only; the ceiling tier (operator-configured sink sensitivity, full
  source type) adds only **+0.1pt**. Ship the floor tier; skip the expensive
  integration.
- **Gate 2 works as a false-positive reducer**: it holds 64.4% recall while
  cutting uncertain-lane benign flags 69 → 46 (hard FPR 1.20% → 0.80%).
- A zero-parameter Rego-style rule on the same two fields reaches only 16.7% — a
  trained arm is needed.

## Review-pile economics (answers the RFC's cost question)

At 1:1000 attack prevalence the uncertain/review lane carries **5.07%** real
attacks — vs **0.54%** for the round-4 single-dial Youden point. The review pile
is ~9× more precise, though still mostly false alarms at realistic rarity.

## Method caveats recorded

- The §2 "worse of miss/fp overlap ≤1.5" bar is unsatisfiable by construction
  when the flag lane is empty: the fp-side ratio (83) is a structural artifact
  (Gate 1 produces zero independent hard FPs), so the **miss-side ratio (2.76)**
  is the meaningful independence number.
- The flag fast-path was empty (α_flag = 0.1% finer than the calibration
  resolution); the router ran effectively two-lane.

## Decision hook (what each outcome drives)

- **Ship now (high confidence):** Gate 0 normalization as an AGT preprocessing
  step — 3× catch at zero FP, fixes the 0% families, no benign-control FPs.
- **Ship as advisory (medium):** floor-tier Gate 2 for uncertain-lane FP
  reduction, off by default, validated on real benign traffic first.
- **Do not ship / drop:** the trained head over kNN (no deployable-FPR gain) and
  the expensive ceiling-tier metadata integration (+0.1pt).
- **Reframe upstream:** the cascade is a detection/triage layer **inside** AGT's
  deterministic governance boundary, not a path to 80%/1% on its own; and do not
  claim gate independence — it is refuted.
- **Next round:** word-segmentation + multilingual transforms (recover the 0%
  bypass cluster); a genuinely cross-modal Gate 2 (task-drift) if independence is
  wanted; a stronger encoder if a head is to beat kNN.

## The non-passable gate

Real benign traffic at scale, advisory-only, with FP re-measured before anything
blocks. This experiment validates the **architecture and its limits**; it does
not certify production behavior.
