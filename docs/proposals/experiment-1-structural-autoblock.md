# Experiment 1 — Structural Auto-Block Ceiling (proposal, plain English)

Status: **DRAFT for review.** Not started. No new data required.

## The one-paragraph version

Round 6 measured *detection* (a probabilistic embedding signal). It showed two
attack families — tool_abuse and output_exfiltration — are essentially
**uncatchable by detection** (catch flat at ~38–42% no matter how much false-
positive budget you spend). This experiment measures the other half of the
defense: **deterministic containment** — block rules that fire on structural
facts (who sent it, what it touches, what it's calling) and never on what the
text *means*. Because they don't read meaning, they can be set to auto-block
with no human review. We run them on the data we already have, and we measure,
per attack family: how much each rule prevents, how many legitimate requests it
wrongly blocks, and — the number nobody usually reports — what fraction of
attacks even *have* a structural handle for automation to grab.

## Why this is the right experiment to run now

- **It needs no new data.** The corpus already carries the four governance
  fields the rules use (`requires_tool_call`, `contains_sensitive_sink`,
  `source_type`, `trust_level`).
- **It answers a real deployment question:** "Which attack families can I hand
  to fully-automated blocking, with what prevention and what false-block cost,
  and what's left over?"
- **It complements round 6 honestly:** detection owns the text-manipulation
  families; containment should own the action/exfiltration families. This
  measures whether that's true and by how much.

## The "captain obvious" rule set (deterministic, auto-blockable)

Every rule fires on a structural fact only. If a rule needs to judge the meaning
of the text, it is **excluded by design** (the "iffy → discard" filter). We test
four rules individually and combined.

| Rule | Condition (structural only) | Targets |
|---|---|---|
| **R1 — Untrusted-drives-tool** | `trust_level = untrusted` AND `requires_tool_call` | indirect injection, tool_abuse |
| **R2 — Sensitive-exfil** | `contains_sensitive_sink` AND `coarse_source ≠ user` | output_exfiltration, prompt_leakage, data_boundary |
| **R3 — Lethal-trifecta (strict)** | `trust_level = untrusted` AND `requires_tool_call` AND `contains_sensitive_sink` | highest-precision subset of the above |
| **R4 — Any-rule (R1 ∨ R2)** | union of R1 and R2 | broad-coverage view |

`coarse_source` = the AGT-realistic 3-value collapse (user / tool_result /
other) defined in `docs/methodology/round6-corpus-to-agt-field-mapping.md`.
Excluded as not-auto-blockable: the embedding score (probabilistic), semantic
framing (meaning), and anything routed to a human (human review is itself an
attack surface — *AI Agent Traps*, HITL category).

## What we measure — the granular result tables

These are the table **shapes** we will fill once the run completes. Every cell
is a count + rate with a Wilson 95% interval, on the frozen test split.

### Table 1 — Per-family prevention (block rate), by rule

| Attack family | Rows | R1 block% | R2 block% | R3 block% | R4 (any) block% | Round-6 detection% @1%FP | **Combined (detect ∨ block)%** |
|---|---:|---:|---:|---:|---:|---:|---:|
| direct_override | | | | | | | |
| prompt_leakage | | | | | | | |
| indirect_injection | | | | | | | |
| tool_abuse | | | | | | | |
| tool_result_injection | | | | | | | |
| output_exfiltration | | | | | | | |
| memory_poisoning | | | | | | | |
| data_boundary_abuse | | | | | | | |
| **All attacks** | | | | | | | |

The headline cell is the last column: **does adding deterministic containment to
detection close the gaps detection capped on** (tool_abuse, output_exfiltration)?

### Table 2 — Per-benign-subcategory false blocks (the real false-positive)

| Benign subcategory | Rows | R1 FP% | R2 FP% | R3 FP% | R4 FP% |
|---|---:|---:|---:|---:|---:|
| benign_tool_use | | | | | |
| legitimate_imperative_request | | | | | |
| benign_security_discussion | | | | | |
| tool_policy_documentation | | | | | |
| high_entropy_structured_data | | | | | |
| quoted_injection_example | | | | | |
| … (all benign subcategories) | | | | | |
| **All benign** | | | | | |

A rule with a non-trivial false-block rate on any legitimate subcategory is
**too broad → discard or narrow it**. This table is how we enforce the
"captain obvious only" bar with evidence rather than opinion.

### Table 3 — Handle-rate / coverage (the number usually missing)

| Attack family | % with a structural handle (touches sink, tool, or untrusted source) | % uncontainable (no handle) |
|---|---:|---:|
| … per family … | | |
| **All attacks** | | |

"Uncontainable" attacks have no structural chokepoint — automation literally
cannot block them, so they are the **residual that detection must carry** (or
that needs a new control). This sets the ceiling of pure-automation defense.

### Table 4 — Improvement summary & control ownership

| Attack family | Detection-only (round 6) | + Structural containment | Δ | Owner verdict |
|---|---:|---:|---:|---|
| … per family … | | | | detection / containment / both / uncovered |

## Pre-registered accept/kill bars (set before the run)

1. **Rule precision (auto-block safety):** each kept rule must have a false-block
   rate **≤ 1%** on every legitimate benign subcategory (ideally ~0). A rule
   that exceeds this on any subcategory is reported as **too broad** and either
   narrowed or dropped — it failed the "captain obvious" test.
2. **Containment value:** for tool_abuse and output_exfiltration (detection's
   capped families), structural containment must lift catch by **≥ 30 points**
   over detection-only — otherwise the containment story is not real on this
   data.
3. **Combined floor:** no attack family below a stated end-to-end floor (target
   to be fixed at review; suggested **≥ 60%** combined) — or it is named as an
   open residual.
4. **Honesty gate:** the handle-rate (Table 3) is reported regardless of
   outcome; a low handle-rate is a finding, not a failure.

## The honest caveat (must be in the writeup)

On this synthetic corpus the governance labels are **perfect by construction**.
So Experiment 1 measures the **ceiling of structural defense when labels are
correct**. The real-world number depends on labeling coverage — the integration
cost discussed in the round-6 analysis (unlabeled tool = treat as sensitive;
unknown source = untrusted, fail-closed). This is a ceiling/validation result,
**not** a production guarantee, and the report will say so in the first section.

## Relationship to prior work

Refines the round-4 governance evaluation (policy-gate-only prevented ~65% of
unsafe actions) with three things it lacked: **per-family** breakdown,
**per-benign-subcategory false-block** measurement, and the **handle-rate**
coverage metric — all under the strict "block-only, no human review,
structural-facts-only" constraint.

## Deliverables
- New harness milestone under `meta/harness/` (reuses round-6 `common.py` load
  + metadata-only artifact discipline; no embedding model needed — pure rule
  evaluation over the corpus fields).
- Metadata-only artifacts + validator, frozen-test discipline.
- Report with Tables 1–4 filled, accept/kill verdicts, and the labels caveat.

## Out of scope
- Gate 0++ delivery-layer normalization (Experiment 2 — needs new data).
- Any probabilistic / meaning-based blocking.
- Multi-agent, systemic, and human-in-the-loop trap categories.
