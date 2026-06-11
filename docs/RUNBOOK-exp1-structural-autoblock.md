# Experiment 1 — Structural Auto-Block Ceiling (AI-First Runbook v4)

> **Purpose**: Measure the fully-automated, no-human-review detection+containment
> stack — round-6 Gate-0 normalizer + kNN embedding at the zero-FP point, OR'd
> with four deterministic structural block rules — and report the breakdown **by
> control** and **by attack technique** on the frozen test split.
> **Prerequisite reading**: [proposals/experiment-1-structural-autoblock.md](proposals/experiment-1-structural-autoblock.md),
> [reports/round6-cascade-report.md](reports/round6-cascade-report.md),
> [methodology/round6-corpus-to-agt-field-mapping.md](methodology/round6-corpus-to-agt-field-mapping.md),
> [ARCHITECTURE.md](ARCHITECTURE.md).
> **Template basis**: SLO v4. Global sections 4, 6–8, 11–16 apply verbatim.

---

## 1. Runbook Metadata

| Field | Value |
|---|---|
| Runbook ID | `e1sab` |
| Project name | AGT-Embeddings-Experiment |
| Primary stack | Python 3.13 batch harness (numpy; reuses round-6 `common.py`; NO embedding model run) |
| Prefix for tests and lesson files | `e1sab` |
| Default unit/BDD test command | `python3 -m unittest discover -s meta/harness/exp1-structural -p "test_*.py"` |
| Default E2E validation command | `python3 meta/harness/exp1-structural/validate-exp1.py` |
| Default static analysis | `python3 -m py_compile <changed files>` |
| Allowed new dependencies by default | `none` |
| Schema/config migration allowed by default | `no` |
| Public interfaces stable by default | `yes` |

### Public interfaces that must remain stable

- `corpus/round4/injection-round4-large.jsonl` and manifest — read-only, byte-identical.
- All `artifacts/round6-cascade/**` and `artifacts/embedding-sweep/**` — read-only, never regenerated.
- Round-6 harness modules — imported read-only (`common.py`); not modified.

### Experiment-wide red lines

- Frozen-test discipline: rules are defined from the proposal (fixed before the run); the test split is evaluated once.
- Metadata-only artifacts: no `text`/`raw_text`/`prompt`/`content` fields in outputs.
- `expected_action` and `risk_level` are ground truth — **forbidden** as rule inputs (the rules use only `requires_tool_call`, `contains_sensitive_sink`, `source_type`, `trust_level`).
- No new corpus data; no embedding model execution (reuse committed M1 per-row decisions).
- No production/real-traffic claims; this is a labels-perfect ceiling result.

---

## 2. Milestone Tracker

| # | Milestone | Status | Started | Completed | Lessons | Completion |
|---|---|---|---|---|---|---|
| 1 | Structural rules + combined-stack evaluation (by control × by technique) | `done` | 2026-06-11 | 2026-06-11 | docs/slo/lessons/e1sab-m1.md | docs/slo/completion/e1sab-m1.md |
| 2 | Report + claims-ledger/README update | `done` | 2026-06-11 | 2026-06-11 | docs/slo/lessons/e1sab-m2.md | docs/slo/completion/e1sab-m2.md |

### Pre-registered accept/kill bars (from the accepted proposal)

| Bar | Accept | Kill / flag |
|---|---|---|
| Rule safety (auto-block) | each kept rule's false-block rate ≤1% on **every** benign subcategory | any subcategory >1% → rule flagged too-broad, narrowed or dropped |
| Containment value | structural containment lifts tool_abuse AND output_exfiltration by ≥30 points over round-6 detection-only | <30pt → containment story not real on this data |
| Combined floor | no attack family below 60% combined (detect∨block) | any family <60% → named open residual |
| Honesty gate | handle-rate (coverage) reported for every family regardless of outcome | — (cannot fail; must be recorded) |

---

## 3. End-to-End Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────────┐
│ Experiment 1 — fully automated, no human review                          │
│                                                                          │
│  corpus/round4 test split ──┐                                            │
│  (governance fields)        │                                            │
│                             ▼                                            │
│   ┌─────────────── COMBINED GATE (OR) ───────────────┐                   │
│   │                                                  │                   │
│   │  (A) round-6 Gate-0 + kNN @ zero-FP   ──flag?──▶ │                   │
│   │      (reuse m1-gate0 pred_attack)                │── flag → BLOCK    │
│   │                                                  │                   │
│   │  (B) structural rules R1..R4 (facts)  ──flag?──▶ │── none → ALLOW    │
│   │      from requires_tool_call,                    │                   │
│   │      contains_sensitive_sink,                    │                   │
│   │      source_type, trust_level                    │                   │
│   └──────────────────────────────────────────────────┘                  │
│                             │                                            │
│                             ▼                                            │
│  artifacts/exp1-structural/  (metadata-only: per-row decisions,          │
│  by-control × by-technique tables, handle-rate, verdicts)                │
│                                                                          │
│  Legend: (A) probabilistic but zero-FP (quiet-but-certain);             │
│          (B) deterministic structural; decision = A OR B                 │
└──────────────────────────────────────────────────────────────────────────┘
```

| Component | Responsibility | Existing/New | Milestone |
|---|---|---|---|
| `rules.py` | Deterministic structural rules R1–R4 over governance fields | new | M1 |
| `run_exp1_eval.py` | Combine reused embedding decision OR rules; compute by-control × by-technique tables | new | M1 |
| `validate-exp1.py` | Artifact + number-consistency validator | new | M1/M2 |
| round-6 `m1-gate0/test-per-row.jsonl` | Embedding zero-FP decision (`pred_attack`) | existing (read-only) | M1 |
| `report.md` + doc updates | Plain-English results, by-control + by-technique | new | M2 |

---

## 5. Formal Verification

`N/A — single-process deterministic batch over a frozen corpus.` No concurrency,
persistence, or irreversible actions. Correctness carried by: rules fixed before
the run (proposal), ground-truth-field exclusion asserted in code, unit tests on
each rule's truth table, and a validator that recomputes every reported number
from the per-row file.

### 5.8 Kani proof obligations
`N/A — no Rust.`

---

## 5A. Measurement Contract

`N/A — not a value-bearing feature.` Research-measurement harness; the
measurement is the deliverable, contracted in §2 bars and the M1 Evidence Log.

---

## 5B. Secure Value and Security Contract

Security-relevant: evaluates automated prompt-injection blocking for an upstream
security toolkit.

### Value Wedge
| Field | Value |
|---|---|
| Value hypothesis | A no-human-review stack (zero-FP embedding ∨ structural rules) prevents a measurable, per-family share of attacks at near-zero false-block cost; the residual is quantified |
| Smallest valuable wedge | The by-control × by-technique table alone is the deliverable |
| User-visible proof | Tables showing block rate per technique per control + false-block per benign category |
| Security-visible proof | Ground-truth fields provably excluded from rules (asserted + validated); metadata-only artifacts |
| Too small to matter when | Only aggregate numbers reported with no per-family / per-control / handle-rate breakdown |

### Security Definition of Ready (Operator Readiness)
| Prerequisite | Owner | Needed by | Validation | Status |
|---|---|---|---|---|
| Round-6 m1-gate0 artifacts present + byte-identical | agent | M1 | `validate-round6-cascade.py m1` green | `ready` |
| Frozen corpus byte-identical | upstream | M1 | `check-round4.py` green | `ready` |

`safe_to_continue_without_blockers: true`

### Threat Model Summary (runbook-scoped)
| Area | Summary |
|---|---|
| Assets | Evidence credibility (no ground-truth leakage into rules); corpus integrity; metadata-only artifacts |
| Actors | Local agent/operator; downstream readers |
| Trust boundaries | Corpus (frozen) → rule eval (trusted code) → published artifacts |
| Abuse cases | `tm-e1sab-abuse-1`: ground-truth field used as a rule input, inflating prevention → assertion + validator. `tm-e1sab-abuse-2`: raw text in an artifact → forbidden-field check |
| Required controls | C8 Protect Data Everywhere (metadata-only), C9 Security Logging (validator, freeze of rule defs) |
| Residual risks | Synthetic labels-perfect optimism — owner: author; reviewed at M2 |

### Security Test Plan
| Test | Required? | Command/tool | Evidence | Waiver |
|---|---|---|---|---|
| SAST | no | — | — | `waived: stdlib batch script` |
| Abuse-case tests | yes | unittest tm-e1sab-abuse-1/2 | `test_rules.py`, `test_hygiene.py` | — |
| Privacy/telemetry tests | yes | forbidden-field + ground-truth-exclusion test | `test_hygiene.py` | — |
| Dependency audit | no | — | — | `not_applicable: no new deps` |

### Detected Work Ledger
| ID | Finding | Severity | Disposition | Owner | Evidence | Due |
|---|---|---|---|---|---|---|
| — | (filled during execution) | | | | | |

---

## 9. Background Context

### Current State
Round 6 measured detection only. tool_abuse and output_exfiltration are capped
under detection (~38–42% no matter the FP budget); their detection ceiling is
flat. The governance fields needed for structural rules are present on every
corpus row. Round-6 `m1-gate0/test-per-row.jsonl` already carries the
zero-FP embedding decision (`pred_attack`) per row.

### Problem
No measurement exists of the **automated containment** half: deterministic block
rules on structural facts, OR'd with the zero-FP embedding, broken down by
control and by attack technique, with the false-block cost and the handle-rate.

### Key Design Principles
1. Rules fire on structural facts only; never on text meaning (auto-blockable).
2. Ground truth (`expected_action`/`risk_level`) never enters a rule.
3. Decision = (zero-FP embedding flag) OR (any structural rule) — no human lane.
4. Report by-control and by-technique, plus the honest residual (handle-rate).
5. Labels are perfect on synthetic data → this is a ceiling, stated as such.

### Global Red Lines
Template defaults + the experiment-wide red lines in §1.

---

## 17. Milestone Plan

### Milestone 1 — Structural rules + combined-stack evaluation

**Goal**: A deterministic rule module (R1–R4) and an evaluation runner exist that
combine the reused zero-FP embedding decision with the rules and emit
metadata-only artifacts giving, on the frozen test split: per-family block rate
**per control**, combined detect∨block per family, per-benign-subcategory
false-block per control, handle-rate/coverage, and improvement vs round-6
detection-only.

**Context**: Pure evaluation over committed data — corpus governance fields +
`artifacts/round6-cascade/m1-gate0/test-per-row.jsonl` (embedding `pred_attack`).
No embedding model is run. Rules are the four from the accepted proposal.

**Carmack-style reliability goal**: assertion-driven feature isolation — each
rule's input set is asserted (governance fields only; ground-truth excluded),
and every reported number is recomputable from the per-row artifact.

**Important design rule**: `rules.py` is pure (dict-in → bool-out per rule), no
I/O; the runner owns all file access and the OR-combination.

**Refactor budget**: `No refactor permitted beyond direct implementation`.

#### Contract Block

| Field | Value |
|---|---|
| Inputs | corpus test rows (governance fields + attack_class/benign_subclass/bypass_class); `m1-gate0/test-per-row.jsonl` (embedding pred_attack, joined by id) |
| Outputs | `artifacts/exp1-structural/`: `rule-definitions.json` (frozen R1–R4 truth tables), `by-technique.json` (per-family × per-control block + combined), `by-benign.json` (per-subcategory false-block per control), `handle-rate.json`, `test-per-row.jsonl` (id, label, technique, per-control flags, combined), `provenance.json` |
| Interfaces touched | new `rules.py` (`R1..R4(meta)->bool`, `coarse_source(meta)`); new runner |
| Files allowed to change | new files below; nothing existing |
| Files to read before changing anything | `meta/harness/round6-cascade/common.py`, `gate2.py` (coarsen vocab), `artifacts/round6-cascade/m1-gate0/test-per-row.jsonl`, the proposal |
| New files allowed | `meta/harness/exp1-structural/{rules.py, run_exp1_eval.py, validate-exp1.py, test_rules.py, test_hygiene.py, README.md}`, `artifacts/exp1-structural/*` (generated), `docs/slo/lessons/e1sab-m1.md`, `docs/slo/completion/e1sab-m1.md` |
| New dependencies allowed | none |
| Migration allowed | no |
| Compatibility commitments | corpus + round-6 artifacts byte-identical; round-6 + round-4 validators still green; git clean outside allow-list |
| Resource bounds | bounded by test size (9,408 rows); no growth; arrays only |
| Invariants/assertions required | (1) rule inputs ⊆ {requires_tool_call, contains_sensitive_sink, source_type, trust_level} — asserted; ground-truth field in a rule path trips it; (2) join completeness — every test id present in m1 per-row, orphan = hard error; (3) determinism — two runs identical; (4) forbidden output fields absent; (5) combined = embedding OR (R1∨R2∨R3) by construction, asserted on a sample |
| Debugger / inspection expectation | inspect each rule's truth table over the 4-field cartesian product before the full run |
| Static analysis gates | `py_compile`; full unittest; round-6 + round-4 validators green |
| Exemplar code to copy | round-6 `common.py` loaders + metadata-only writers; `gate2.py` `coarsen` for `coarse_source` |
| Anti-exemplar code not to copy | any use of `expected_action`/`risk_level`; any probabilistic threshold in a "structural" rule; reading raw text into outputs |
| Refactoring discipline | `N/A — all-new files` |
| AI tolerance contract | ai_component: true (reuses an embedding decision). Accepted variance: none — reuses committed deterministic decisions; no model run. Deterministic boundary: everything. Eval evidence: by-control × by-technique tables. Retry/fallback: none. Must-never: ground-truth in rules; raw text in artifacts. Sample budget: one pass over the committed test split |
| Forbidden shortcuts | no ground-truth fields; no re-running the embedding; no silent row drops; no rule that inspects text |
| Data classification | `Public` |
| Proactive controls in play | C8 Protect Data Everywhere, C9 Security Logging and Monitoring |
| Abuse acceptance scenarios | `tm-e1sab-abuse-1` (ground-truth in rule) and `tm-e1sab-abuse-2` (text leakage) — BDD rows below |
| Measurement deliverables | `N/A — not value-bearing (research)`; evidence = the four §2 bars computed |

#### Out of Scope
- No Gate 0++ / markup (Experiment 2, needs data).
- No new rules beyond R1–R4; no probabilistic/meaning-based rules.
- No human-review lane.

#### Files Allowed To Change
| File | Planned change |
|---|---|
| `meta/harness/exp1-structural/rules.py` | NEW: R1–R4 + coarse_source, pure functions, frozen truth tables |
| `meta/harness/exp1-structural/run_exp1_eval.py` | NEW: join corpus + m1 decision; OR-combine; by-control × by-technique + handle-rate + false-block tables |
| `meta/harness/exp1-structural/validate-exp1.py` | NEW: structure, forbidden-field, ground-truth-exclusion, number-consistency checks |
| `meta/harness/exp1-structural/test_rules.py` | NEW: truth-table BDD tests |
| `meta/harness/exp1-structural/test_hygiene.py` | NEW: forbidden-field + ground-truth-exclusion tests |
| `meta/harness/exp1-structural/README.md` | NEW |
| `.gitignore` | add exp1 scratch patterns if any |

#### Step-by-Step
1. Read round-6 `common.py`, `gate2.py` coarsen, m1 per-row, proposal.
2. Write `test_rules.py` + `test_hygiene.py` stubs; confirm failing.
3. Implement `rules.py`; inspect each rule's 4-field truth table (debugger expectation).
4. Implement runner: join, OR-combine, compute all tables.
5. Implement validator; run round-6 + round-4 validators (untouched check).
6. Full suite green; write artifacts; spot-verify 2 cells by hand.
7. Evidence log, lessons, completion, tracker.

#### BDD Acceptance Scenarios

**Feature: structural rules + combined stack**

| Scenario | Category | Given | When | Then |
|---|---|---|---|---|
| R1 truth | happy path | `trust_level=untrusted, requires_tool_call=True` | R1 | True; flips False if either condition off |
| R2 truth | happy path | `contains_sensitive_sink=True, coarse_source=other` | R2 | True; False when coarse_source=user |
| R3 trifecta | happy path | untrusted ∧ tool ∧ sink | R3 | True; False if any leg missing |
| R4 union | happy path | R1 or R2 true | R4 | True iff R1∨R2 |
| coarse_source map | happy path | source/trust combos | coarse_source | user/tool_result/other per mapping doc |
| Combined OR | happy path | embedding flag OR any rule | runner | combined True iff (pred_attack ∨ R1∨R2∨R3) |
| Ground-truth exclusion | abuse `tm-e1sab-abuse-1` | a rule references expected_action | hygiene test | assertion fires; rule rejected |
| Join orphan | invalid input | test id missing from m1 per-row | runner | hard error naming id |
| No text in artifacts | abuse `tm-e1sab-abuse-2` | full artifact set | hygiene test | zero forbidden fields / raw text |
| Determinism | invariant | same inputs | two runs | identical artifacts |
| Empty subcategory | empty state | benign subcategory with 0 rows | tables | structured zero, no divide error |

Concurrency/retry: N/A — single-threaded batch.

#### Regression Tests
- `validate-round6-cascade.py m1` green; m1 artifacts byte-identical.
- `check-round4.py` green; round-4 artifacts untouched.

#### Compatibility Checklist
- [ ] Corpus + round-6 artifacts byte-identical
- [ ] Round-6 + round-4 validators green
- [ ] No existing harness file modified

#### E2E Runtime Validation
**File**: `meta/harness/exp1-structural/validate-exp1.py`

| E2E test | Proves | Pass criteria |
|---|---|---|
| `validate-exp1.py` | artifact contract + number consistency | every by-technique/by-benign number recomputed from `test-per-row.jsonl` matches; forbidden fields absent |
| recompute spot-check | reproducibility | 2 hand-computed cells match artifacts |

#### Smoke Tests
- [ ] full unittest green
- [ ] each rule truth table inspected
- [ ] `git status` clean outside allow-list

#### Evidence Log
| Step | Command / Check | Expected | Actual | Pass/Fail | Notes |
|---|---|---|---|---|---|
| Baseline | round-6 + round-4 validators | green | | | |
| BDD created | test_rules/test_hygiene | fail for right reason | | | |
| Implementation | rules.py + runner | contract satisfied | | | |
| Rule safety bar | per-benign false-block | ≤1% all subcats (or flag) | | | |
| Containment bar | tool_abuse + exfil Δ vs detection | ≥30pt (or kill) | | | |
| Combined floor | per-family detect∨block | ≥60% (or residual) | | | |
| Handle-rate | coverage per family | recorded | | | |
| Validator | validate-exp1 | green | | | |
| Determinism | second run | identical | | | |
| Compatibility | checklist | no regressions | | | |

#### Definition of Done
Standard v4 checklist **plus**: all four §2 bars computed and recorded; the
by-control × by-technique tables and handle-rate written; labels-perfect caveat
noted for M2.

#### Post-Flight
- ARCHITECTURE.md: add exp1 row in M2.
- Lessons `e1sab-m1`, completion `e1sab-m1`.

---

### Milestone 2 — Report + claims-ledger/README update

**Goal**: A plain-English report presents the by-control and by-technique
results, the false-block cost, the handle-rate residual, and the four §2
verdicts; README/CLAIMS-LEDGER/ARCHITECTURE get additive updates.

**Context**: Aggregation/writeup only over M1 artifacts; no new computation
beyond formatting. Caveat-first (labels-perfect ceiling).

**Refactor budget**: `No refactor permitted beyond direct implementation`.

#### Contract Block (abbreviated — docs milestone)

| Field | Value |
|---|---|
| Inputs | `artifacts/exp1-structural/*` |
| Outputs | `docs/reports/exp1-structural-autoblock-report.md`; additive README/CLAIMS-LEDGER/ARCHITECTURE updates |
| Files allowed to change | the report (new); `README.md` (Evidence Snapshot, additive), `docs/CLAIMS-LEDGER.md` (additive section), `docs/ARCHITECTURE.md` (additive row); lessons/completion `e1sab-m2` |
| New dependencies allowed | none |
| Migration allowed | no |
| Compatibility commitments | existing claims/rows unedited; README change confined to Evidence Snapshot |
| Invariants/assertions required | every number in the report matches `artifacts/exp1-structural/*` (validator number-consistency pass) |
| Exemplar code to copy | round-6 report structure (`docs/reports/round6-cascade-report.md`) |
| Anti-exemplar | any "production-ready" language; editing round-4/round-6 claims |
| AI tolerance contract | `N/A — no AI component executed` |
| Forbidden shortcuts | no selective reporting (every family, every control, every benign subcat shown incl. zeros) |
| Data classification | `Public` |
| Proactive controls in play | C9 Security Logging and Monitoring |
| Abuse acceptance scenarios | `N/A — no new surface; docs over committed artifacts` |
| Measurement deliverables | the report IS the readout |

#### BDD Acceptance Scenarios
| Scenario | Category | Given | When | Then |
|---|---|---|---|---|
| Report completeness | happy path | M1 artifacts | report built | every family, control, benign subcat present incl. zeros |
| Number consistency | invariant | report numbers | validator | match artifacts exactly |
| Caveat present | compatibility | report §1 | read | labels-perfect ceiling caveat first |
| Ledger additive | backward compat | CLAIMS-LEDGER | diff | existing rows byte-identical |

#### Definition of Done
Report carries the by-control + by-technique tables, false-block, handle-rate,
the four §2 verdicts, and the caveat; docs updated additively; tracker closed.

#### Post-Flight
- README Evidence Snapshot, CLAIMS-LEDGER, ARCHITECTURE additive; lessons/completion `e1sab-m2`.

---

## 18. Documentation Update Table
| Milestone | ARCHITECTURE.md | README.md | Other |
|---|---|---|---|
| 1 | — | — | lessons/completion e1sab-m1 |
| 2 | exp1 evidence row | Evidence Snapshot row | report; CLAIMS-LEDGER; lessons/completion e1sab-m2 |
