# Round-6 Cascade Experiment — AGT Embeddings Experiment (AI-First Runbook v4)

> **Purpose**: Measure whether a four-stage detection pipeline — deterministic
> de-obfuscation (Gate 0), a trained calibrated classifier head (Gate 1),
> calibrated three-bucket routing, and a cross-modal governance Gate 2 with a
> tiered metadata ablation — widens the true-positive/false-positive gap beyond
> the round-4 single-dial kNN margin, with pre-registered accept/kill
> thresholds per stage.
> **Audience**: AI coding agents first, humans second.
> **Prerequisite reading**: [ARCHITECTURE.md](ARCHITECTURE.md), [README.md](../README.md),
> [reports/round4-youden-j-tuning.md](reports/round4-youden-j-tuning.md),
> [reports/round4-mac-embedding-sweep-evidence.md](reports/round4-mac-embedding-sweep-evidence.md),
> [methodology/source-to-agt-expected-action-mapping.md](methodology/source-to-agt-expected-action-mapping.md).
> **Template basis**: SLO runbook template v4. Global sections 4 (Carmack-style
> practices), 6–8 (global execution/entry/exit rules), and 11–16 (BDD rules,
> dependency policy, evidence/lessons/completion templates, self-review gate)
> of the v4 template apply verbatim and are not duplicated here.

---

## 1. Runbook Metadata

| Field | Value |
|---|---|
| Runbook ID | `r6c` |
| Project name | AGT-Embeddings-Experiment |
| Primary stack | Python 3.14 batch harness (fastembed/ONNX local, numpy, scikit-learn, psutil) |
| Primary package/app names | `meta/harness/round6-cascade/` (new), `artifacts/round6-cascade/` (new) |
| Prefix for tests and lesson files | `r6c` |
| Default unit test command | `python3 -m unittest discover -s meta/harness/round6-cascade -p "test_*.py"` |
| Default integration/BDD test command | same as unit (stdlib unittest; BDD Given/When/Then in test docstrings, repo convention) |
| Default E2E/runtime validation command | `python3 meta/harness/round6-cascade/validate-round6-cascade.py` (per-milestone validators) |
| Default build/boot command | `N/A — batch harness, no boot; smoke = harness `--dry-run` on 64-row sample` |
| Default formatter command | `python3 -m compileall meta/harness/round6-cascade` (no formatter pinned in repo; do not introduce one) |
| Default static analysis / lint command | `python3 -m py_compile <changed files>` + `corpus/round4/check-round4.py` untouched-green |
| Default dependency / security audit command | `pip list` recorded into artifact provenance (repo convention; no audit tool pinned) |
| Default debugger or state-inspection tool | `pdb` / `python3 -i` over harness functions on 64-row samples |
| Allowed new dependencies by default | `none` (fastembed/psutil env restore per `artifacts/embedding-sweep/provenance.json` is environment setup, not a new dependency) |
| Schema/config migration allowed by default | `no` (corpus is frozen; new artifacts only) |
| Public interfaces stable by default | `yes` |

### Public interfaces that must remain stable unless explicitly listed otherwise

- `corpus/round4/injection-round4-large.jsonl` and `manifest-large.json` — read-only, byte-identical.
- All existing `artifacts/embedding-sweep/` and `artifacts/governance-eval/` files — never regenerated or edited.
- `tools/agt-rules-baseline/` — untouched.
- Existing round-4/round-5 harnesses and validators — untouched.

### Experiment-wide red lines (inherited from repo conventions, see ARCHITECTURE.md)

- Frozen-test discipline: all selection on `validation`; one test-split scoring
  per frozen configuration, freeze record written first.
- Metadata-only artifacts: no `text`/`raw_text`/`prompt`/`content` fields in
  any committed artifact, including normalized text (hashes only).
- `expected_action` and `risk_level` are ground truth — forbidden as detector
  or Gate-2 inputs anywhere in this runbook.
- No production/real-traffic/default-blocking claims in any report text.

---

## 2. Milestone Tracker

| # | Milestone | Status | Started | Completed | Lessons File | Completion Summary |
|---|---|---|---|---|---|---|
| 1 | Gate 0 — deterministic de-obfuscation + bypass-class rescore | `done` | 2026-06-11 | 2026-06-11 | docs/slo/lessons/r6c-m1.md | docs/slo/completion/r6c-m1.md |
| 2 | Gate 1 — trained head vs kNN curve (TPR @ fixed FPR) + leave-one-family-out generalization | `done` | 2026-06-11 | 2026-06-11 | docs/slo/lessons/r6c-m2.md | docs/slo/completion/r6c-m2.md |
| 3 | Three-bucket routing — calibration + conformal benign-side coverage | `done` | 2026-06-11 | 2026-06-11 | docs/slo/lessons/r6c-m3.md | docs/slo/completion/r6c-m3.md |
| 4 | Gate 2 — tiered governance-metadata ablation (control/floor/ceiling) | `done` | 2026-06-11 | 2026-06-11 | docs/slo/lessons/r6c-m4.md | docs/slo/completion/r6c-m4.md |
| 5 | Reporting + closeout — per-family floors, hard-negative note, claims-ledger update | `done` | 2026-06-11 | 2026-06-11 | docs/slo/lessons/r6c-m5.md | docs/slo/completion/r6c-m5.md |

<!-- Lessons: docs/slo/lessons/r6c-m<N>.md · Completion: docs/slo/completion/r6c-m<N>.md -->

### Pre-registered accept/kill thresholds (the experiment contract)

| Stage | Accept | Kill / redirect |
|---|---|---|
| M1 Gate 0 | Obfuscated bypass classes (chunked, compact, letter-spaced, leet, rot13, homoglyph, encoding) reach ≥40% catch at the re-frozen FP-zero threshold AND benign obfuscation-control FPs stay 0 on test | <10-point catch movement on those classes → misses are not an encoding problem; drop Gate 0 claim |
| M2 Gate 1 head | ≥60% TPR @ 1% FPR on frozen test AND head ROC dominates the post-normalization kNN curve for all FPR ≤ 2% | Head ≤ kNN in the FPR ≤ 2% region → bottleneck is encoder/corpus, not decision rule; redirect to encoder upgrade, do not proceed to M3 on the head |
| M2 LOFO (generalization sub-gate) | Median held-out-family TPR @ 1% FPR ≥25% across all 8 LOFO folds AND ≤2 families below 5% | Worse → head generalizes by family memorization; surface to user before M3 starts (M3/M4 may proceed only with this warning recorded in their reports) |
| M3 Buckets | Promised benign-side coverage (α=1%) holds on frozen test within the Wilson 95% interval AND review-queue precision at 1:1000 prevalence ≥5% (attacks/(attacks+benign) among uncertain-lane items; lane size ≤2% of benign is reported but not gated — it is implied by coverage) | Coverage breaks between validation and test → calibration does not transfer; buckets revert to uncalibrated two-threshold status and M4 proceeds descriptively only |
| M4 Gate 2 | Floor arm materially beats control (≥5-point end-to-end catch gain at fixed FPR); error-overlap ratio ≤ 1.5 — applied to the **worse** of the miss-side and FP-side ratios, formulas pinned in M4's Contract Block; end-to-end ≥80% catch at ≤1% hard-action FPR | Conditional failure >50% on items Gate 1 failed → shared blind spots, cascade refuted; a kill verdict must cite M4's lane-shift diagnostic to rule out a protocol artifact before the negative result is published |
| M5 Reporting | No attack family at 0% catch in the success configuration (per-family floors); hard-negative robustness note recorded; multilingual bypass class at 0% is an **accepted residual** of this round (Gate 0 has no translation transform by design) and is stated as such in the report's caveats with a future-work pointer | N/A — M5 is measurement and reporting; it cannot pass/fail, only record |

These gates are independent: a kill at a later stage does not retroactively
invalidate an earlier accept (e.g., an M4 overlap-kill leaves the M2 head
result standing as a published finding feeding the pre-registered redirect),
and each verdict is reported in M5 on its own §2 row.

---

## 3. End-to-End Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────────────┐
│ Round-6 cascade (all new components dashed; all batch, local-only)         │
│                                                                            │
│ corpus/round4 (frozen) ──▶ ┌ - - - - - - - - - - ┐                         │
│                            ┊ Gate 0  normalize.py ┊  M1                    │
│                            ┊ NFKC, zero-width,    ┊                        │
│                            ┊ homoglyph, de-leet,  ┊                        │
│                            ┊ spacing, rot13/b64   ┊                        │
│                            └ - - - - ┬ - - - - - ┘                         │
│                                      ▼                                     │
│ .cache/fastembed ═══▶ bge-small-en-v1.5 embeddings (existing runner shape) │
│                                      │                                     │
│            ┌─────────────────────────┼───────────────────────┐             │
│            ▼ (existing)              ▼ (new)                  │            │
│      kNN margin (round-4     ┌ - - - - - - - - ┐              │            │
│      reference curve)        ┊ Gate 1 head.py  ┊  M2          │            │
│                              ┊ LR / HistGB +   ┊              │            │
│                              ┊ isotonic calib  ┊              │            │
│                              └ - - - ┬ - - - - ┘              │            │
│                                      ▼                        │            │
│                        ┌ - - - - - - - - - - - ┐              │            │
│                        ┊ buckets.py  pass /    ┊  M3          │            │
│                        ┊ uncertain / flag      ┊              │            │
│                        └ - - - ┬ - - - - - - - ┘              │            │
│                                ▼ uncertain lane only          │            │
│                  ┌ - - - - - - - - - - - - - - - ┐            │            │
│                  ┊ Gate 2 gate2.py — 3 arms      ┊  M4        │            │
│                  ┊ control: no metadata          ┊            │            │
│                  ┊ floor: requires_tool_call +   ┊            │            │
│                  ┊        coarse trust (AGT      ┊            │            │
│                  ┊        input.source vocab)    ┊            │            │
│                  ┊ ceiling: + sensitive_sink +   ┊            │            │
│                  ┊        full source_type       ┊            │            │
│                  └ - - - - - - ┬ - - - - - - - - ┘            │            │
│                                ▼                              ▼            │
│              artifacts/round6-cascade/m<N>-*/  (metadata-only, provenance, │
│              freeze records, validators)                       M1–M5       │
│                                                                            │
│ Legend: ─── existing   - - - new   ═══ external (local model cache)        │
└────────────────────────────────────────────────────────────────────────────┘
```

| Component | Responsibility | Existing/New | Milestone | Key Interfaces |
|---|---|---|---|---|
| `meta/harness/round6-cascade/normalize.py` | Deterministic de-obfuscation (Gate 0) | new | M1 | `normalize(text) -> NormalizedResult` |
| `meta/harness/round6-cascade/run_m1_gate0_rescore.py` | Re-run kNN FP-zero protocol on normalized text | new | M1 | CLI → `artifacts/round6-cascade/m1-gate0/` |
| `meta/harness/round6-cascade/head.py` + `run_m2_head.py` | Trained calibrated classifier head (Gate 1) | new | M2 | CLI → `artifacts/round6-cascade/m2-head/` |
| `meta/harness/round6-cascade/buckets.py` + `run_m3_buckets.py` | Three-bucket conformal routing | new | M3 | CLI → `artifacts/round6-cascade/m3-buckets/` |
| `meta/harness/round6-cascade/gate2.py` + `run_m4_gate2.py` | Tiered governance ablation over uncertain lane | new | M4 | CLI → `artifacts/round6-cascade/m4-gate2/` |
| `meta/harness/round6-cascade/run_m5_generalization.py` | LOFO + per-family floors + final metrics | new | M5 | CLI → `artifacts/round6-cascade/m5-generalization/` |
| `meta/harness/round6-cascade/validate-round6-cascade.py` | Artifact structure/hash validator (extended per milestone) | new | M1–M5 | CLI, exit code |
| Round-4 sweep artifacts | Frozen reference curve and thresholds | existing | all | read-only |

| Flow | From | To | Mechanism | Bounded? | Failure Mode | Milestone |
|---|---|---|---|---|---|---|
| Corpus rows | `corpus/round4/*.jsonl` | harness runners | file read | yes (44,800 rows) | hard error, no partial artifacts | M1–M5 |
| Normalized text | `normalize.py` | embedding step (in-memory only) | function call | yes (output ≤ 4× input chars, decode depth ≤ 2) | structured error row, counted | M1 |
| Embeddings | fastembed local ONNX | scorers | batch 256 | yes (16 GiB psutil cap, round-4 convention) | abort with provenance note | M1–M5 |
| Metrics/decisions | runners | `artifacts/round6-cascade/m*-*/` | JSON/JSONL write | yes | validator fails closed | M1–M5 |

---

## 5. High-Level Design for State Modeling / Formal Verification

`N/A — single-process, single-threaded batch pipeline over a frozen corpus.`
No concurrency, no distributed state, no retries, no persistence beyond
write-once artifacts, no irreversible actions. Correctness is carried by (a)
the frozen-test protocol encoded as freeze records written before test
scoring, (b) deterministic, idempotent normalization with unit-tested
invariants, and (c) validators that fail closed on artifact structure. These
are enforced per-milestone via assertions and BDD tests rather than a state
model.

### 5.8 Kani proof obligations

`N/A — no Rust kernels are introduced or modified in this runbook.`

---

## 5A. Measurement Contract

`N/A — not a value-bearing feature.` This runbook introduces no user-facing
capability; it is a research-measurement harness. Measurement is itself the
deliverable and is contracted per-milestone in the pre-registered accept/kill
table (§2) and each milestone's Evidence Log, which is stricter than the
product telemetry contract this section normally carries.

---

## 5B. Secure Value and Security Contract

Security-relevant: the work evaluates AI-agent prompt-injection defenses and
publishes evidence intended for an upstream security toolkit (AGT).

### Value Wedge

| Field | Value |
|---|---|
| Value hypothesis | A staged pipeline with pre-registered thresholds either demonstrates a deployable-FPR detection layer for AGT or produces a documented negative result; both outcomes de-risk upstream PR2 |
| Smallest valuable wedge | M1 alone (Gate 0 bypass-class result) is independently publishable evidence |
| User-visible proof of value | Updated evidence tables in README/CLAIMS-LEDGER with per-stage ablations |
| Security-visible proof of safety | Metadata-only artifacts, frozen-test freeze records, ground-truth fields provably excluded from detector inputs (asserted in code + validator) |
| Too small to matter when | Only aggregate numbers move with no per-family/per-bypass breakdown — single headline numbers are exactly the single-dial trap this round exists to escape |

### Security Definition of Ready (Operator Readiness)

| Prerequisite | Owner | Needed by | Validation (executable proof) | Status |
|---|---|---|---|---|
| Harness env restored (fastembed, psutil pinned per `artifacts/embedding-sweep/provenance.json`) | agent | M1 | `python3 -c "import fastembed, psutil"` exits 0 | `partially_ready` (sklearn/numpy present; fastembed/psutil need install) |
| Model cache present or downloadable (`bge-small-en-v1.5`, SHA-256 `51f1bd0a…449f2431`) | agent | M1 | freeze record SHA matches round-4 value | `partially_ready` |
| Frozen corpus byte-identical | upstream | M1 | `corpus/round4/check-round4.py` green | `ready` |

`safe_to_continue_without_blockers: true` (remaining items are mechanical env
setup performed in M1 pre-flight; fail closed if SHA mismatches).

### Threat Model Summary

No `/slo-architect` threat model exists for this repo (research-corpus repo;
runbook-scoped summary below — do not re-derive elsewhere).

| Area | Summary |
|---|---|
| Assets | Frozen corpus integrity; evidence credibility (no leakage of ground truth into detector inputs); repo publishability (no raw attack text in artifacts) |
| Actors | Local agent/operator only; downstream readers of published artifacts |
| Trust boundaries | Corpus (trusted, frozen) → harness (trusted code) → committed artifacts (published) |
| Entry points | Harness CLIs reading corpus files; no network surface except model download |
| Abuse cases | `tm-r6c-abuse-1`: adversarially crafted corpus row (nested encodings) causes normalizer resource blow-up → bounded decode depth/output size. `tm-r6c-abuse-2`: ground-truth field (`expected_action`/`risk_level`) silently used as a feature, inflating results → runtime assertion + validator check on recorded feature lists. `tm-r6c-abuse-3`: raw prompt text leaks into a committed artifact → forbidden-field check in every writer + validator |
| Required controls | OWASP C8 Protect Data Everywhere (metadata-only outputs); C3 Validate Input (normalizer bounds); C9 Security Logging (structured error rows, provenance records) |
| Residual risks | Synthetic-corpus optimism — owner: experiment author; review at M5 readout |

### Security Test Plan

| Test | Required? | Command/tool | Evidence path | Waiver |
|---|---|---|---|---|
| SAST | no | — | — | `waived_with_reason: no service code; stdlib+numeric batch scripts; py_compile gate applies` |
| SCA/dependency audit | yes (env restore) | hash-pinned `requirements.lock` + `pip install --require-hashes` (F-SEC-1); `pip list` into provenance.json | `meta/harness/round6-cascade/requirements.lock` + `artifacts/round6-cascade/m1-gate0/provenance.json` | — |
| Secrets scan | yes | `git diff --staged` review per commit (repo convention) | Evidence Log row | — |
| IaC / container / DAST / authn | no | — | — | `not_applicable: no infra, no network service` |
| Abuse-case tests | yes | unittest cases for tm-r6c-abuse-1/2/3 | `meta/harness/round6-cascade/test_*.py` | — |
| Privacy/telemetry tests | yes | forbidden-field assertion test on every artifact writer | `test_artifact_hygiene.py` | — |
| Fuzz/property tests | yes (M1) | idempotency + bound property tests over random/adversarial strings | `test_normalize.py` | — |

### Detected Work Ledger

| ID | Finding | Severity | Disposition | Owner | Evidence/link | Due |
|---|---|---:|---|---|---|---|
| — | (filled during execution; no row may end undisposed) | | | | | |

---

## 9. Background Context

### Current State

Round 4 established: AGT rules-only ≈1% catch / ≈8% FP; kNN margin over
bge-small embeddings reaches 14.2% catch @ 0% observed FP (τ=0.08027) or 88.3%
@ 16.3% FP (Youden, τ=-0.0061); ROC-AUC 0.924. Governance eval: policy gate
alone prevents 65.2% of unsafe actions; policy+embedding 69.3%. Full detail in
[ARCHITECTURE.md](ARCHITECTURE.md) and `docs/reports/`.

### Problem

1. **Single-dial trade-off**: one threshold on one signal forces choosing
   between 14% catch and a 16% FP rate; the review pile at realistic
   prevalence collapses precision to ≤5%.
2. **Obfuscation blind spot**: bypass classes chunked/compact/letter-spaced/
   leet catch 0%, rot13 6.7%, encoding 13.6%, homoglyph 16.7%, multilingual
   0% — while plain-text equivalents catch 60%. The detector never sees the
   un-disguised text.
3. **kNN decision rule under-uses the corpus**: literature (PromptShield
   arXiv:2501.15145; embeddings+RF arXiv:2412.01547) shows trained heads over
   identical embeddings dominate cosine-threshold rules at deployable FPRs.
4. **Governance metadata unexploited per-request**: round-4 governance arms
   applied policy globally; no measurement exists of metadata as a *second
   gate over the uncertain lane*, nor of which fields (guaranteed vs
   integration-dependent in real AGT deployments) carry the value.

### Key Design Principles

1. **Pre-registered thresholds**: every stage's accept/kill bar is in §2
   before any code runs; reports cite the table, not post-hoc framing.
2. **Ablation over composition**: each milestone is measured against the
   previous stage as baseline; a component that fails its bar is dropped, not
   averaged in.
3. **AGT-realistic metadata vocabulary**: Gate-2 arms use only fields AGT can
   actually deliver at runtime (floor: tool-call presence + coarse
   `input.source`-style trust; ceiling: + operator-configured sink
   sensitivity + host IFC source labels), with the corpus fields explicitly
   coarsened to that vocabulary.
4. **Ground truth stays ground truth**: `expected_action`/`risk_level` never
   enter any feature set; enforced by assertion and validator.
5. **Everything inherits round-4 hygiene**: freeze records, metadata-only
   artifacts, provenance, validators.

### What to Keep / What to Change

Keep: everything that exists (corpus, round-4/5 harnesses and artifacts, Rust
tool, docs). Change: nothing existing. All work lands in two new directories
(`meta/harness/round6-cascade/`, `artifacts/round6-cascade/`) plus README/
CLAIMS-LEDGER evidence updates in M5 and `.gitignore` entries as needed.

### Global Red Lines

Template defaults apply (no unrelated refactors, no new deps beyond declared,
no schema migration, no placeholders, no silent failure, no secrets, no test
artifacts committed) **plus** the experiment-wide red lines in §1.

---

## 10. Carry-forward from prior retros

No retro-derived issues exist for prefix `r6c` (first runbook under this
prefix; `gh issue list --label retro-derived` fallback applies).

---

## 17. Milestone Plan

### Milestone 1 — Gate 0: deterministic de-obfuscation + bypass-class rescore

**Goal**: A deterministic, idempotent, bounded text normalizer exists, and the
round-4 FP-zero kNN protocol re-run on normalized text shows — with a fresh
validation-selected, frozen threshold — whether obfuscated bypass classes
converge toward plain-text catch rates without leaking benign obfuscation
controls.

**Context**: Round-4 results in `artifacts/embedding-sweep/test-metrics.json`
show plain/diacritics attacks catch at 60% while chunked/compact/letter-spaced
variants catch at 0% — the same attack content, disguised. The RFC under
discussion places de-obfuscation in Gate 2, but obfuscated attacks score *low*
and would never reach it; this milestone tests normalization in front of all
scoring instead. The scorer itself is deliberately unchanged round-4 kNN
(k=5, mean-top-k margin, exemplar bank embedded from normalized text too) so
the only variable is normalization.

**Carmack-style reliability goal**: bounded resource design (decode depth,
output size) + assertion-driven invariants (idempotency, determinism) on the
one component every later milestone depends on.

**Important design rule**: `normalize()` is a pure function with no I/O; the
runner owns all file access. Normalized text exists only in memory — artifacts
record per-row `normalization_applied` flags, transform tags, and hashes,
never text.

**Refactor budget**: `No refactor permitted beyond direct implementation`.

#### Contract Block

| Field | Value |
|---|---|
| Inputs | `corpus/round4/injection-round4-large.jsonl`, `manifest-large.json`; round-4 freeze record (reference only); model cache |
| Outputs | `artifacts/round6-cascade/m1-gate0/`: `freeze-record.json`, `validation-metrics.json`, `test-metrics.json`, `validation-per-row.jsonl`, `test-per-row.jsonl`, `provenance.json`, `report.md` |
| Interfaces touched | none existing; new module `normalize.py` (public: `normalize(text: str) -> NormalizedResult`) |
| Files allowed to change | only the new files below + `.gitignore` (add `artifacts/round6-cascade/**/.tmp/` if scratch needed) |
| Files to read before changing anything | `meta/harness/round4-embedding-sweep/run_round4_embedding_sweep.py`, `validate-embedding-sweep.py`, `artifacts/embedding-sweep/freeze-record.json`, `test-metrics.json`, `corpus/round4/manifest-large.json` |
| New files allowed | `meta/harness/round6-cascade/{normalize.py, run_m1_gate0_rescore.py, validate-round6-cascade.py, test_normalize.py, test_artifact_hygiene.py, README.md, requirements.lock}`, `artifacts/round6-cascade/m1-gate0/*` (generated), `docs/slo/lessons/r6c-m1.md`, `docs/slo/completion/r6c-m1.md` |
| New dependencies allowed | none (env restore of fastembed+psutil per round-4 provenance is setup, recorded in M1 provenance.json) |
| Migration allowed | no |
| Compatibility commitments | corpus byte-identical (`check-round4.py` green); all existing artifacts untouched (`git status` clean outside allowed paths); round-4 validator still green on round-4 artifacts |
| Resource bounds introduced/changed | decode-sniff depth ≤ 2; decode-acceptance rule (F-ENG-2): a sniffed decode is kept only if the output is valid UTF-8 with ≥90% printable characters, else the original text is kept with tag `decode_rejected`; normalized output ≤ 4× input chars (hard cap, truncate-with-flag at limit); homoglyph map applied single-pass; embed batch 256; 16 GiB psutil cap aborting cleanly (round-4 convention) |
| Invariants/assertions required | (1) idempotency: `normalize(normalize(x)).text == normalize(x).text` asserted in tests over corpus sample + random strings; (2) determinism: two runs produce identical per-row hashes; (3) plain-ASCII identity: rows with `bypass_class in {none, plain}` are character-identical after normalization except case-preserving NFKC no-ops (asserted ≥99.9% identical, deviations logged with transform tags); (4) ground-truth exclusion: runner asserts feature inputs ⊆ {text}; (5) forbidden output fields absent in every written artifact; (6) closed tag enum (F-SEC-2): transform tags are a declared enum in `normalize.py` — never constructed from input strings — membership asserted at artifact-write time and enforced by the validator and `test_artifact_hygiene.py` |
| Debugger / inspection expectation | `pdb` walk of `normalize()` over one row per bypass class (10 rows) before full run; transform-tag output inspected per class |
| Static analysis gates | `python3 -m py_compile` on all new files; `python3 -m unittest` green; round-4 + round-6 validators green |
| Exemplar code to copy | `run_round4_embedding_sweep.py`: freeze-record-before-test pattern, metadata-only writer, provenance block, batch embedding loop, Wilson-interval reporting |
| Anti-exemplar code not to copy | any pattern writing row text to artifacts; any threshold selection touching the test split; `tools/agt-rules-baseline/vendor/.../prompt_injection.rs` regex approach (Gate 0 is normalization, not detection — no attack-pattern matching in `normalize.py`) |
| Refactoring discipline | `N/A — no refactoring performed; all-new files` |
| AI tolerance contract | ai_component: true (eval harness for model-based detection). Accepted variance: none — ONNX inference is deterministic on fixed hardware; freeze record pins model SHA-256 `51f1bd0a…449f2431`; cross-host drift acknowledged as provenance note, not tolerance. Deterministic boundary: everything (no sampling, no API calls). Eval evidence: per-bypass-class catch tables validation+test. Retry/fallback: none — failures abort. Must-never: ground-truth fields as features; raw text in artifacts; test-split selection. Sample budget: full splits once; ≤3 validation re-scores during development (counted in provenance) |
| Forbidden shortcuts | no hand-tuned per-class normalization rules derived from peeking at attack rows in validation/test (rules must be generic Unicode/encoding transforms); no silent row skips (every undecodable row gets a structured error record); no threshold reuse from round-4 (re-select on validation post-normalization) |
| Data classification | `Public` (synthetic corpus, metadata-only outputs) |
| Proactive controls in play | C3 Validate Input (bounded decode, output caps), C8 Protect Data Everywhere (metadata-only artifacts), C9 Security Logging and Monitoring (structured error rows, provenance) |
| Abuse acceptance scenarios | `tm-r6c-abuse-1` (nested-encoding resource blow-up → bounded) and `tm-r6c-abuse-3` (text leakage → forbidden-field test) — rows in BDD table below |
| Measurement deliverables | `N/A — not value-bearing` in the §5A product sense; milestone evidence = per-bypass-class catch deltas + benign obfuscation-control FP counts against the §2 M1 accept/kill bar |

#### Out of Scope / Must Not Do

- No classifier head, no calibration, no buckets, no governance fields (M2–M4).
- No multilingual translation (multilingual bypass class is *measured* but no
  translation transform is built — record it as out of Gate 0's reach if so).
- No changes to k, margin formula, or exemplar-bank composition.
- No new attack-pattern regexes — Gate 0 normalizes, it does not detect.

#### Files Allowed To Change

| File | Planned Change |
|---|---|
| `meta/harness/round6-cascade/normalize.py` | NEW: pure normalization module (NFKC, zero-width/control strip, confusables/homoglyph map, leet de-substitution, letter-spacing collapse, chunk-joining, rot13/base64/hex sniff-and-decode depth ≤2, whitespace canonicalization), returning text + ordered transform tags |
| `meta/harness/round6-cascade/run_m1_gate0_rescore.py` | NEW: round-4-protocol runner over normalized corpus: embed exemplar bank + validation, select FP-zero τ′ on validation, write freeze record, score test once |
| `meta/harness/round6-cascade/validate-round6-cascade.py` | NEW: m1 artifact validator (structure, hashes, forbidden fields, freeze-before-test timestamps) |
| `meta/harness/round6-cascade/test_normalize.py` | NEW: BDD unit/property tests for normalize() |
| `meta/harness/round6-cascade/test_artifact_hygiene.py` | NEW: forbidden-field + ground-truth-exclusion tests against writer functions |
| `meta/harness/round6-cascade/README.md` | NEW: how to set up env and run M1 |
| `.gitignore` | Add `artifacts/round6-cascade/**/*.tmp` and any new scratch patterns |

#### Step-by-Step

1. Restore harness env with hash pinning (F-SEC-1): generate and commit `meta/harness/round6-cascade/requirements.lock` (`pip freeze` with `--require-hashes`-compatible hashes for fastembed, psutil + transitive deps), install via `pip install --require-hashes -r requirements.lock`, record the lock file's SHA-256 in `provenance.json`; verify model SHA.
2. Write `test_normalize.py` BDD stubs (table below) — confirm they fail for the right reason.
3. Write `test_artifact_hygiene.py` stubs — fail for the right reason.
4. Implement `normalize.py` smallest-safe: each transform a named, ordered, individually-testable function.
5. Make normalization tests pass; run property tests (idempotency/determinism/identity over 2,000-row sample + 500 random strings).
6. Implement `run_m1_gate0_rescore.py` copying the round-4 runner shape; `--dry-run` on 64 rows as smoke.
7. Full run: validation scoring → FP-zero τ′ selection → freeze record → single test scoring.
8. Implement + run `validate-round6-cascade.py`; round-4 validator re-run on round-4 artifacts (untouched check).
9. Write `report.md` (per-bypass-class before/after table, benign obfuscation-control FP table with `high_entropy_structured_data` as a named column (F-ENG-2), decode-rejection counts, accept/kill verdict vs §2).
10. Evidence Log, lessons, completion summary, tracker update.

#### BDD Acceptance Scenarios

**Feature: deterministic de-obfuscation (Gate 0)**

| Scenario | Category | Given | When | Then |
|---|---|---|---|---|
| Leet/spacing collapse | happy path | `"1gn0re a l l previous instructions"` | `normalize()` | text contains `"ignore all previous instructions"`; tags include `leet`,`spacing` |
| Homoglyph fold | happy path | Cyrillic-о/Greek-ο variants of "ignore" | `normalize()` | ASCII `"ignore"`; tag `confusables` |
| rot13 sniff | happy path | rot13 of an English imperative sentence | `normalize()` | decoded text; tag `rot13`; depth counter = 1 |
| base64 nested twice | resource bound | base64(base64(text)) | `normalize()` | decoded ≤ depth 2; depth-3 nesting stops with tag `decode_depth_capped`, no error |
| Output cap | resource bound / abuse `tm-r6c-abuse-1` | adversarial input expanding >4× under decode | `normalize()` | truncated at 4× with tag `output_capped`; bounded runtime |
| Plain text identity | compatibility | 2,000-row sample with `bypass_class∈{none,plain}` | `normalize()` | ≥99.9% character-identical; deviations all carry explaining tags |
| Idempotency | assertion/invariant | any corpus row or random string | `normalize(normalize(x))` | equals `normalize(x)` exactly |
| Empty input | empty state | `""` | `normalize()` | `""`, no tags, no error |
| Invalid bytes | invalid input | lone surrogates / unpaired combining marks | `normalize()` | safe replacement, tag `invalid_unicode`, no exception |
| Decode validity guard | invalid input (F-ENG-2) | benign base64-looking high-entropy data decoding to binary garbage | `normalize()` | decode rejected (<90% printable UTF-8), original text kept, tag `decode_rejected` |
| Tag enum closure | assertion violation (F-SEC-2) | writer handed a free-form string tag | artifact write | membership assertion fires; validator and hygiene test reject the artifact |
| Model cache missing | dependency failure | cache dir removed, `--no-download` | runner | clean abort, no partial artifacts, structured error |
| No text in artifacts | abuse `tm-r6c-abuse-3` | full m1 artifact set | hygiene test scans all JSON/JSONL | zero occurrences of forbidden fields or any corpus text ≥20 chars |
| Ground-truth exclusion | abuse `tm-r6c-abuse-2` | runner feature-input manifest | hygiene test | feature set == `{text}`; assertion fires if extended |
| Freeze before test | persistence/protocol | completed run | validator | freeze-record mtime/hash recorded before test artifacts; τ′ chosen on validation only |

Concurrency/retry: N/A — single-threaded batch, no retries (abort-on-failure
by design).

#### Regression Tests

- `corpus/round4/check-round4.py` green (corpus untouched).
- `meta/harness/round4-embedding-sweep/validate-embedding-sweep.py` green
  against existing `artifacts/embedding-sweep/` (nothing regenerated).
- `git diff --stat` empty outside the M1 allow-list.

#### Compatibility Checklist

- [ ] Corpus files byte-identical (hash check)
- [ ] Existing artifacts byte-identical
- [ ] Round-4 validator green on round-4 artifacts
- [ ] No existing harness file modified

#### E2E Runtime Validation

**File**: `meta/harness/round6-cascade/validate-round6-cascade.py` (+ `--dry-run` smoke)

| E2E Test | What It Proves | Pass Criteria |
|---|---|---|
| `runner --dry-run` (64 rows) | pipeline boots end-to-end: normalize → embed → score → write | exits 0; sample artifacts validate; runtime < 5 min |
| `validate-round6-cascade.py m1` | full artifact contract | structure, hashes, forbidden-fields, freeze-ordering all pass |
| Threshold protocol check | frozen-test discipline held | τ′ appears in freeze record with validation-only provenance; exactly one test scoring recorded |

#### Smoke Tests

- [ ] `python3 -m unittest discover -s meta/harness/round6-cascade -p "test_*.py"` passes
- [ ] `--dry-run` completes; spot-inspect transform tags for one row per bypass class (10 rows)
- [ ] `report.md` accept/kill verdict cites §2 M1 row verbatim
- [ ] `git status` clean outside allow-list; `.gitignore` covers scratch outputs

#### Evidence Log

| Step | Command / Check | Expected Result | Actual Result | Pass/Fail | Notes |
|---|---|---|---|---|---|
| Baseline tests | round-4 validators + check-round4 | green | | | |
| Env restore | `pip install` pinned; import check | imports succeed; versions recorded | | | |
| BDD tests created | `test_normalize.py`, `test_artifact_hygiene.py` | fail for expected reason | | | |
| Implementation | `normalize.py` + runner | contract satisfied | | | |
| Property tests | idempotency/determinism/identity | green over sample + random strings | | | |
| Static checks | `py_compile` all new files | clean | | | |
| Full run | `run_m1_gate0_rescore.py` | freeze → test once; artifacts written | | | |
| E2E validator | `validate-round6-cascade.py m1` | green | | | |
| Resource-bound verification | depth-cap + output-cap tests | bounds hold at limit | | | |
| Invariant verification | hygiene + protocol tests | green | | | |
| Debugger / state inspection | pdb over 10 bypass-class rows | transforms behave as designed | | | |
| **M1 verdict vs §2** | per-bypass-class Δcatch + benign-control FPs | accept (≥40% / 0 FP) or kill (<10pt) recorded | | | |
| Artifact cleanup + .gitignore | `git status` | clean | | | |
| Compatibility checks | checklist above | no regressions | | | |

#### Definition of Done

Standard v4 checklist (template §17) **plus**: the §2 M1 accept/kill verdict
is recorded in `report.md` and the Evidence Log with the per-bypass-class
table — *the milestone is done when the measurement is honestly recorded,
whether the verdict is accept or kill*.

#### Post-Flight

- **ARCHITECTURE.md**: add round-6 row to components table; note Gate 0 result in evidence baseline.
- **README.md**: no update until M5 (evidence snapshot updates land once, with the full picture).
- **Other docs**: lessons `docs/slo/lessons/r6c-m1.md`; completion `docs/slo/completion/r6c-m1.md`.

#### Notes

- Multilingual bypass class is expected to remain near 0% (Gate 0 has no
  translation transform by design); the report must state this explicitly so
  the miss is attributed to scope, not failure.
- If accept is reached but benign obfuscation-control FPs appear at τ′, the
  verdict is **partial**: record both numbers; M3's buckets become the
  designated mitigation and the report says so.

---

### Milestone 2 — Gate 1: trained head vs kNN curve + leave-one-family-out generalization

**Goal**: A trained classifier head (logistic regression and
HistGradientBoosting, scikit-learn only) over the same normalized-text
bge-small embeddings exists with a validation-frozen configuration, measured
as TPR at validation-frozen 0.1%/1%-FPR cutoffs on the frozen test split
against the post-normalization kNN margin curve — plus an 8-fold
leave-one-family-out (LOFO) generalization readout so family-memorization
surfaces before M3/M4 build on the head.

**Context**: M1's per-row outputs (`artifacts/round6-cascade/m1-gate0/*-per-row.jsonl`)
provide the post-normalization kNN margin ROC as the comparison curve — head
vs kNN on identical inputs isolates the decision rule as the only variable.
Literature basis for the bar: trained heads over identical embeddings
dominate cosine/kNN thresholds at deployable FPRs (arXiv:2412.01547;
PromptShield arXiv:2501.15145 reports 94.8% TPR @ 1% FPR). Embeddings are
recomputed via M1's `normalize.py` + the round-4 embedding loop and cached
locally (git-ignored) — M1 artifacts contain no vectors.

**Carmack-style reliability goal**: type/schema safety and determinism for
the model layer — pinned seeds, frozen hyperparameter records, auditable
coefficient export; make "which configuration produced this number"
unambiguous forever.

**Important design rule**: one model-selection pass on validation, then
freeze. LOFO folds retrain with the *frozen* hyperparameters only — no
per-fold tuning, ever. The LOFO sub-gate is a generalization alarm, not a
tuning loop.

**Refactor budget**: `Minimal local refactor permitted in listed files only`
(M1's runner may be split so embedding/scoring helpers become importable by
`run_m2_head.py` instead of duplicated; behavior-preserving, per
`skills/slo-plan/references/refactoring-discipline.md`: pre-test evidence —
M1 validator green before and after the split).

#### Contract Block

| Field | Value |
|---|---|
| Inputs | corpus (read-only); `normalize.py` (M1, unchanged); M1 per-row artifacts (kNN reference curve); model cache; local embedding cache |
| Outputs | `artifacts/round6-cascade/m2-head/`: `freeze-record.json`, `validation-metrics.json`, `test-metrics.json`, `validation-per-row.jsonl`, `test-per-row.jsonl` (id, label, head score, decision at frozen cutoffs — no vectors, no text), `lofo-metrics.json` (8 folds), `head-lr-coefficients.json`, `provenance.json`, `report.md` |
| Interfaces touched | new `head.py` (public: `train_head(X, y, spec) -> FrozenHead`, `FrozenHead.scores(X) -> np.ndarray`); M1 helpers imported, not modified in behavior |
| Files allowed to change | new files below; `run_m1_gate0_rescore.py` + new `common.py` (helper extraction only); `validate-round6-cascade.py` (add m2 checks); `.gitignore` (embedding-cache pattern) |
| Files to read before changing anything | M1 sources + artifacts; `artifacts/embedding-sweep/youden-j-tuning.json` (round-4 curve reference); `docs/slo/lessons/r6c-m1.md` |
| New files allowed | `meta/harness/round6-cascade/{head.py, run_m2_head.py, common.py, test_head.py}`, `artifacts/round6-cascade/m2-head/*` (generated), lessons/completion `r6c-m2` |
| New dependencies allowed | none (scikit-learn already in env; **xgboost explicitly not permitted** — HistGradientBoostingClassifier covers the boosted-tree slot) |
| Migration allowed | no |
| Compatibility commitments | M1 artifacts byte-identical; M1 validator green after helper extraction; corpus untouched; M1 unit tests still green |
| Resource bounds introduced/changed | embedding cache ≤ 200 MiB (44,800 × 384 float32 ≈ 66 MiB + index), git-ignored, keyed by (corpus manifest hash, SHA-256 of `normalize.py` file content — computed at runtime, never a manual tag (F-ENG-3)) and invalidated on key mismatch; training memory under the 16 GiB cap; hyperparameter grid ≤ 24 configurations (hard cap, enumerated in freeze record); LOFO exactly 8 retrains |
| Invariants/assertions required | (1) determinism: fixed `random_state`, two full runs → identical frozen cutoffs and test metrics; (2) ground-truth exclusion: feature matrix built from embeddings only, asserted feature-source manifest == `{normalized_text_embedding}`; (3) split discipline: training rows ⊆ exemplar_bank, selection rows ⊆ validation, asserted by row-id set checks; (4) LOFO purity: held-out family absent from that fold's exemplar bank AND training set, asserted per fold; (5) cutoff provenance: 0.1%/1% FPR cutoffs computed on validation only, recorded in freeze record before test scoring |
| Debugger / inspection expectation | inspect score distributions per class on validation before freezing (pdb/`python3 -i`); confirm no degenerate separation (all-zero or saturated scores) before test run |
| Static analysis gates | `py_compile` new files; full `unittest` suite green (M1 + M2 tests); round-6 validator green for m1 + m2 |
| Exemplar code to copy | M1 runner's freeze-record-before-test and provenance patterns; round-4 Wilson-interval reporting; `sklearn.metrics.roc_curve` usage as in round-4 sweep |
| Anti-exemplar code not to copy | per-fold or post-test hyperparameter adjustment (the cardinal sin of this milestone); committing model binaries or embedding vectors to artifacts; round-4's Youden-point framing as a headline (deployable-FPR framing only) |
| Refactoring discipline | helper extraction per `references/refactoring-discipline.md`: microstep, M1 tests + validator green before and after, no behavior change |
| AI tolerance contract | ai_component: true. Accepted variance: none — deterministic inference and training with pinned seeds; cross-host float drift acknowledged in provenance, tolerance on reported metrics ±0.1pt. Deterministic boundary: everything. Eval evidence: TPR @ frozen cutoffs + full ROC on test; 8-fold LOFO table. Retry/fallback: none, abort on failure. Must-never: ground-truth features; test-split selection; per-fold tuning. Sample budget: ≤24-config validation sweep; one test scoring for the frozen head; 8 LOFO test scorings (pre-registered here as part of the protocol, one per fold) |
| Forbidden shortcuts | no oversampling/SMOTE or augmentation (class imbalance handled by `class_weight='balanced'` only — keep the data story simple); no ensembling head+kNN in this milestone (that confounds the decision-rule comparison); no silent exclusion of rows that fail embedding |
| Data classification | `Public` |
| Proactive controls in play | C8 Protect Data Everywhere (no vectors/text in artifacts), C9 Security Logging and Monitoring (freeze records, per-fold provenance), C4 Address Security from the Start (pre-registered cutoffs) |
| Abuse acceptance scenarios | `tm-r6c-abuse-2` (ground-truth leakage into features — BDD row below); new-surface check: no new I/O surface beyond M1's (file read/write within allow-list), so no further abuse rows; see Notes |
| Measurement deliverables | `N/A — not value-bearing` in §5A product sense; evidence = TPR@{0.1%,1%} table vs kNN curve + LOFO 8-fold table against §2 M2 + M2-LOFO bars |

#### Out of Scope / Must Not Do

- No calibration (isotonic/Platt) — that is M3; raw scores suffice for ROC/TPR@FPR.
- No bucket thresholds, no governance fields, no Gate 2 logic.
- No encoder swap (bge-small stays; an encoder upgrade is the *kill-path
  redirect*, a new runbook, not a silent scope widening here).
- No xgboost or any new dependency.
- No kNN+head fusion.

#### Files Allowed To Change

| File | Planned Change |
|---|---|
| `meta/harness/round6-cascade/head.py` | NEW: model specs (LR `class_weight='balanced'`, HistGB), train/freeze/score API, LR coefficient export |
| `meta/harness/round6-cascade/run_m2_head.py` | NEW: runner — embed (cached) → ≤24-config validation sweep → freeze (model choice + hyperparams + 0.1%/1% validation cutoffs) → single test scoring → 8-fold LOFO loop with frozen config |
| `meta/harness/round6-cascade/common.py` | NEW: embedding/scoring helpers extracted from M1 runner (behavior-preserving) |
| `meta/harness/round6-cascade/run_m1_gate0_rescore.py` | Import from `common.py`; no behavior change (validator-verified) |
| `meta/harness/round6-cascade/test_head.py` | NEW: BDD tests below |
| `meta/harness/round6-cascade/validate-round6-cascade.py` | Add m2 artifact checks (structure, no-vector/no-text, freeze ordering, LOFO purity fields) |
| `.gitignore` | Add `.cache/round6-embeddings/` |

#### Step-by-Step

1. Pre-flight: M1 lessons read; baseline green (M1 tests + validators).
2. Extract `common.py` helpers; prove M1 unchanged (tests + validator + artifact hashes).
3. Write `test_head.py` BDD stubs; confirm expected failures.
4. Implement `head.py`; build embedding cache; inspect validation score distributions (debugger expectation).
5. Validation sweep (≤24 configs) → select head → compute 0.1%/1% validation-FPR cutoffs → write freeze record.
6. Single frozen test scoring; TPR table + ROC vs M1 kNN margin curve (dominance check FPR ≤ 2%).
7. LOFO: 8 folds, frozen config, purity assertions, per-family table.
8. Validator extension + run; `report.md` with §2 M2 + M2-LOFO verdicts.
9. Evidence Log, lessons, completion, tracker.

#### BDD Acceptance Scenarios

**Feature: trained head over frozen embeddings (Gate 1)**

| Scenario | Category | Given | When | Then |
|---|---|---|---|---|
| Head trains and scores | happy path | exemplar-bank embeddings + labels | `train_head` → `scores` on validation | finite scores in [0,1]-monotone order, AUC > 0.5, no NaN |
| Determinism | assertion/invariant | same inputs, same seed | two full train+score runs | identical frozen cutoffs and test metrics |
| Split discipline | assertion/invariant | row-id sets per split | runner builds train/selection sets | train ⊆ exemplar_bank, selection ⊆ validation; assertion fires on contamination |
| Ground-truth exclusion | abuse `tm-r6c-abuse-2` | feature-source manifest | hygiene test | features == embeddings only; adding a metadata column trips the assertion |
| LOFO purity | assertion/invariant | fold for family F | fold dataset assembled | zero rows of F in exemplar bank or training set; asserted per fold |
| Cutoff provenance | persistence/protocol | completed run | validator | cutoffs in freeze record cite validation row-count basis; recorded before test artifacts exist |
| Degenerate scores | invalid input | adversarial config producing constant scores | sweep evaluates config | config rejected with structured reason, not silently kept |
| Embedding cache invalidation | dependency failure | cache built under different normalize version tag | runner starts | cache rejected and rebuilt; mismatch logged |
| Empty fold guard | empty state | hypothetical family with 0 test rows | LOFO loop | structured skip record, no division-by-zero |
| Grid cap | resource bound | 25th config requested | sweep | hard error citing the 24-config cap |
| M1 compatibility | compatibility / backward compat | helper extraction done | M1 tests + validator re-run | green; M1 artifacts byte-identical |

Concurrency/retry: N/A — single-threaded batch, abort-on-failure.

#### Regression Tests

- All M1 unit/property tests green after `common.py` extraction.
- `validate-round6-cascade.py m1` green; M1 artifact hashes unchanged.
- `check-round4.py` + round-4 validator green (corpus/artifacts untouched).

#### Compatibility Checklist

- [ ] M1 artifacts byte-identical after refactor
- [ ] M1 test suite green
- [ ] Round-4 artifacts untouched
- [ ] No interface change to `normalize.py`

#### E2E Runtime Validation

**File**: `meta/harness/round6-cascade/validate-round6-cascade.py` (+ runner `--dry-run`)

| E2E Test | What It Proves | Pass Criteria |
|---|---|---|
| `run_m2_head.py --dry-run` (64 rows, 2 configs, 1 LOFO fold) | full pipeline boots: cache → sweep → freeze → score → LOFO | exits 0 < 10 min; sample artifacts validate |
| `validate-round6-cascade.py m2` | artifact contract incl. no-vector/no-text and freeze ordering | green |
| Dominance computation check | curve comparison is reproducible | recomputing TPR@FPR table from committed per-row scores matches `test-metrics.json` exactly |

#### Smoke Tests

- [ ] Full `unittest` suite green
- [ ] `--dry-run` completes; score distribution sanity-inspected
- [ ] `report.md` cites §2 M2 and M2-LOFO rows verbatim with accept/kill verdicts
- [ ] If LOFO sub-gate fails: user surfaced before M3 (explicit stop, per §2)
- [ ] `git status` clean outside allow-list

#### Evidence Log

| Step | Command / Check | Expected Result | Actual Result | Pass/Fail | Notes |
|---|---|---|---|---|---|
| Baseline tests | M1 suite + validators + check-round4 | green | | | |
| Refactor proof | M1 tests/validator/hashes pre+post extraction | identical | | | |
| BDD tests created | `test_head.py` | fail for expected reason | | | |
| Implementation | `head.py`, `run_m2_head.py`, `common.py` | contract satisfied | | | |
| Validation sweep | ≤24 configs, selection recorded | freeze record written before test | | | |
| Frozen test scoring | one run | TPR@{0.1%,1%} + ROC recorded | | | |
| Curve dominance | head vs M1 kNN, FPR ≤ 2% | dominance verdict recorded | | | |
| LOFO | 8 folds, frozen config | per-family table; purity assertions green | | | |
| **M2 verdict vs §2** | TPR@1% ≥60% AND dominance | accept/kill recorded | | | |
| **M2-LOFO verdict vs §2** | median ≥25%, ≤2 families <5% | pass/warn recorded; user surfaced on warn | | | |
| Static checks + validator | `py_compile`, unittest, validator m1+m2 | green | | | |
| Determinism check | second full run | identical metrics | | | |
| Artifact cleanup + .gitignore | `git status`; cache pattern present | clean | | | |
| Compatibility checks | checklist | no regressions | | | |

#### Definition of Done

Standard v4 checklist **plus**: both §2 verdicts (M2 head, M2 LOFO) recorded
in `report.md` and Evidence Log; if the LOFO sub-gate failed, the user was
explicitly surfaced and the warning text is staged for M3/M4 reports. Done
includes a kill verdict honestly recorded.

#### Post-Flight

- **ARCHITECTURE.md**: Gate 1 result row in evidence baseline.
- **README.md**: no update until M5.
- **Other docs**: lessons/completion `r6c-m2`.

#### Notes

- LOFO runs all 8 attack families (cheap with frozen config + cached
  embeddings), not just `tool_abuse`/`prompt_leakage`; those two are the
  headline rows since they sit at 0% today.
- The 8 LOFO test scorings are pre-registered protocol, not test-split
  reuse-for-selection: nothing is chosen based on them; they only gate
  whether a *warning* attaches to later milestones.
- HistGB model binaries stay out of git; LR coefficients are committed as
  JSON for auditability (384 floats + intercept is metadata, not data).

---

### Milestone 3 — Three-bucket routing: calibration + conformal benign-side coverage

**Goal**: The frozen M2 head score becomes a calibrated three-lane router
(pass / uncertain / flag) whose pass-lane boundary carries a finite-sample
conformal guarantee on the benign side, verified once on the frozen test
split, with review-lane cost quantified at 1:100 and 1:1000 attack
prevalence.

**Context**: M2 commits per-row head scores for validation and test
(`artifacts/round6-cascade/m2-head/*-per-row.jsonl`); this milestone operates
on those scores only — no embedding or training work. The conformal method is
split-conformal on the benign class: validation benign rows are split 50/50
by seeded hash into **cal-A** (isotonic calibration fit, with validation
attack rows) and **cal-B** (conformal quantiles, benign only, untouched by
any fitting). M2 used full validation for model selection, which makes
cal-B's exchangeability approximate — this is acknowledged in the report, and
the test-split coverage check (§2 M3 accept bar) is exactly the empirical
verification of whether the guarantee survives that reuse. Routing-on-
calibrated-uncertainty basis: GATEKEEPER arXiv:2502.19335; coverage guarantee
holds for the benign/FP side only, never against adaptive attackers (stated
verbatim in the report).

**Carmack-style reliability goal**: make invalid states unrepresentable in
the routing layer — a `Bucket` enum with total, mutually-exclusive assignment;
thresholds as a validated frozen pair (`t_low < t_high` enforced at
construction, violation = structured kill verdict, never a silent reorder).

**Important design rule**: pre-registered lane budgets, then thresholds —
α_pass = 1% (max benign fraction escaping the pass lane) and α_flag = 0.1%
(max benign fraction reaching the flag lane), both as conformal order
statistics over cal-B (`⌈(n+1)(1−α)⌉`-th order statistic). No threshold is
ever chosen by looking at attack-side numbers or at test.

**Refactor budget**: `No refactor permitted beyond direct implementation`.

#### Contract Block

| Field | Value |
|---|---|
| Inputs | `artifacts/round6-cascade/m2-head/{validation,test}-per-row.jsonl` (id, label, head score); M2 freeze record (provenance chain); corpus manifest (row-id ↔ label cross-check only) |
| Outputs | `artifacts/round6-cascade/m3-buckets/`: `freeze-record.json` (cal-A/cal-B split seed + row-id hashes, isotonic knots, t_low, t_high, α values), `test-metrics.json` (per-lane benign/attack counts, empirical benign escape rates + Wilson intervals, calibration Brier/ECE, prevalence-adjusted review-pile size and precision at 1:100 and 1:1000), `test-per-row.jsonl` (id, label, calibrated score, bucket), `provenance.json`, `report.md` |
| Interfaces touched | new `buckets.py` (public: `FrozenRouter.assign(scores) -> Bucket[]`, `Bucket ∈ {PASS, UNCERTAIN, FLAG}`) |
| Files allowed to change | new files below; `validate-round6-cascade.py` (add m3 checks); nothing else |
| Files to read before changing anything | M2 artifacts + freeze record; `docs/slo/lessons/r6c-m2.md`; round-4 base-rate precision section in `docs/reports/round4-youden-j-tuning.md` (reuse its prevalence math conventions) |
| New files allowed | `meta/harness/round6-cascade/{buckets.py, run_m3_buckets.py, test_buckets.py}`, `artifacts/round6-cascade/m3-buckets/*` (generated), lessons/completion `r6c-m3` |
| New dependencies allowed | none (`sklearn.isotonic.IsotonicRegression` already in env) |
| Migration allowed | no |
| Compatibility commitments | M1/M2 artifacts byte-identical; M1/M2 tests and validators green; corpus untouched |
| Resource bounds introduced/changed | trivially bounded (score arrays ≤ 9,408 rows); isotonic knots ≤ cal-A size; no caps needed beyond the global 16 GiB convention — stated, not waived silently |
| Invariants/assertions required | (1) `t_low < t_high` at router construction — violation aborts with structured kill verdict; (2) bucket assignment is total and mutually exclusive (every row exactly one lane, asserted over full test set); (3) cal-A ∩ cal-B = ∅ and cal-A ∪ cal-B = validation benign rows, asserted by row-id sets; (4) cal-B is benign-only and enters no fitting code path (assert no attack id in cal-B; isotonic fit function receives cal-A ids only); (5) isotonic map is monotone non-decreasing (asserted over knots); (6) determinism: fixed split seed; two runs → identical freeze record |
| Debugger / inspection expectation | inspect calibrated-score histogram per class and the two order-statistic positions on cal-B before freezing; confirm lanes are non-degenerate (no empty uncertain lane on validation) |
| Static analysis gates | `py_compile`; full unittest suite (M1+M2+M3); validator m1+m2+m3 green |
| Exemplar code to copy | round-4 Wilson-interval + base-rate precision reporting (`run_round4_embedding_sweep.py`, youden-j report conventions); M2 freeze-record pattern |
| Anti-exemplar code not to copy | any threshold derived from attack-side or test-side data; Youden-style "best J" threshold selection (the single-dial pattern this runbook exists to escape); silent threshold reordering when t_low ≥ t_high |
| Refactoring discipline | `N/A — no refactoring performed, all-new files` |
| AI tolerance contract | ai_component: true (routing layer over model scores). Accepted variance: none — deterministic transforms over committed scores. Deterministic boundary: everything. Eval evidence: per-lane test tables + coverage check + Brier/ECE. Retry/fallback: none. Must-never: attack-side or test-side threshold selection; cal-B contamination. Sample budget: one test evaluation of the frozen router |
| Forbidden shortcuts | no tuning α values after seeing test results (α_pass=1%, α_flag=0.1% are pre-registered here and in §2); no "soft" lane reassignment post hoc; no dropping rows lacking M2 scores (must be zero — asserted) |
| Data classification | `Public` |
| Proactive controls in play | C4 Address Security from the Start (pre-registered budgets), C9 Security Logging and Monitoring (freeze records, structured kill verdicts), C8 Protect Data Everywhere (id+score+bucket only in artifacts) |
| Abuse acceptance scenarios | `N/A — no new surface introduced`: M3 reads committed M2 artifacts and writes its own artifact directory; no new input class, no parsing of untrusted content (corpus text never enters this milestone). Ground-truth-exclusion hygiene test still extended to cover the router feature set (scores only) |
| Measurement deliverables | `N/A — not value-bearing` in §5A product sense; evidence = coverage verdict + lane-cost table against §2 M3 bar |

#### Out of Scope / Must Not Do

- No governance metadata, no Gate 2 logic (M4 consumes the uncertain lane).
- No re-scoring, re-training, or threshold changes to M2's head.
- No multi-α sweeps — exactly the two pre-registered budgets.
- No claims that the conformal guarantee applies to attack-side recall or
  adaptive adversaries.

#### Files Allowed To Change

| File | Planned Change |
|---|---|
| `meta/harness/round6-cascade/buckets.py` | NEW: cal-A/cal-B seeded split, isotonic fit (cal-A), conformal order statistics (cal-B), `FrozenRouter` with validated threshold pair and total bucket assignment |
| `meta/harness/round6-cascade/run_m3_buckets.py` | NEW: runner — load M2 scores → split → fit → freeze record → single test routing → metrics incl. prevalence-adjusted review-pile table |
| `meta/harness/round6-cascade/test_buckets.py` | NEW: BDD tests below |
| `meta/harness/round6-cascade/validate-round6-cascade.py` | Add m3 checks (structure, freeze ordering, cal-split disjointness fields, no forbidden fields) |

#### Step-by-Step

1. Pre-flight: M2 lessons; baseline green (full suite + validators m1+m2).
2. Write `test_buckets.py` BDD stubs; confirm expected failures.
3. Implement `buckets.py`: split → isotonic → conformal quantiles → `FrozenRouter`.
4. Unit-verify conformal order statistic against a brute-force reference on synthetic arrays (finite-sample correctness).
5. Run on validation: inspect histograms + lane sizes (debugger expectation); write freeze record.
6. Single frozen test routing; compute coverage verdict (Wilson), lane tables, Brier/ECE, prevalence-adjusted review-pile size and precision at 1:100 / 1:1000.
7. Validator extension + run; `report.md` with §2 M3 verdict and the exchangeability caveat stated.
8. Evidence Log, lessons, completion, tracker.

#### BDD Acceptance Scenarios

**Feature: calibrated three-bucket router**

| Scenario | Category | Given | When | Then |
|---|---|---|---|---|
| Total assignment | happy path | frozen router + full test scores | `assign()` | every row exactly one of PASS/UNCERTAIN/FLAG; counts sum to row total |
| Conformal quantile correctness | happy path | synthetic cal-B of known size n | quantile computed | equals brute-force `⌈(n+1)(1−α)⌉`-th order statistic for α ∈ {1%, 0.1%}, including small-n edge cases |
| Degenerate thresholds | assertion violation | cal-B where order statistics give t_low ≥ t_high | router construction | structured kill verdict artifact written; process exits non-zero; no router emitted |
| Cal-split purity | assertion/invariant | validation row ids | split performed | cal-A ∩ cal-B = ∅; union = validation benign; attack id injected into cal-B trips assertion |
| Monotone calibration | assertion/invariant | fitted isotonic map | knots inspected | non-decreasing; raw-score order preserved in calibrated order |
| Determinism | persistence/protocol | fixed seed | two full runs | identical freeze records and bucket assignments |
| Missing score guard | invalid input | test row id absent from M2 scores | runner load | hard error naming the id; no partial routing |
| Empty cal half | empty state | cal-B sized 0 (synthetic) | quantile request | structured error, no division/index error |
| Prevalence math | happy path | synthetic lane counts | 1:100 and 1:1000 tables computed | matches hand-computed reference values exactly |
| Coverage reproducibility | compatibility | committed `test-per-row.jsonl` | recompute escape rates from per-row file | matches `test-metrics.json` exactly |

Concurrency/retry/resource-limit: N/A — single-threaded pure transforms over
≤9,408-row arrays; dependency failure covered by missing-score guard.

#### Regression Tests

- M1 + M2 test suites green; validators m1 + m2 green; artifact hashes unchanged.
- `check-round4.py` + round-4 validator green.

#### Compatibility Checklist

- [ ] M1/M2 artifacts byte-identical
- [ ] M1/M2 tests green
- [ ] No change to `head.py` / `normalize.py` / `common.py`
- [ ] Corpus untouched

#### E2E Runtime Validation

**File**: `meta/harness/round6-cascade/validate-round6-cascade.py` (+ runner `--dry-run`)

| E2E Test | What It Proves | Pass Criteria |
|---|---|---|
| `run_m3_buckets.py --dry-run` (synthetic 200-score sample) | pipeline boots: load → split → fit → freeze → route | exits 0; sample artifacts validate |
| `validate-round6-cascade.py m3` | artifact contract incl. freeze ordering and split-purity fields | green |
| Coverage recompute | committed per-row file reproduces headline metrics | exact match |

#### Smoke Tests

- [ ] Full unittest suite green
- [ ] Calibrated-score histograms inspected; uncertain lane non-degenerate on validation
- [ ] `report.md` cites §2 M3 verbatim with verdict; exchangeability caveat and benign-side-only scope stated
- [ ] `git status` clean outside allow-list

#### Evidence Log

| Step | Command / Check | Expected Result | Actual Result | Pass/Fail | Notes |
|---|---|---|---|---|---|
| Baseline tests | full suite + validators m1+m2 + check-round4 | green | | | |
| BDD tests created | `test_buckets.py` | fail for expected reason | | | |
| Implementation | `buckets.py`, `run_m3_buckets.py` | contract satisfied | | | |
| Conformal correctness | brute-force comparison test | exact match incl. edge cases | | | |
| Freeze record | written before test routing | split seed, knots, t_low, t_high, α recorded | | | |
| Frozen test routing | one run | lane tables + coverage + Brier/ECE recorded | | | |
| **M3 verdict vs §2** | benign escape ≤1% within Wilson AND review-queue precision ≥5% at 1:1000 (lane size ≤2% reported, not gated) | accept/kill recorded | | | |
| Determinism check | second full run | identical freeze record | | | |
| Static checks + validator | `py_compile`, unittest, validator m1–m3 | green | | | |
| Artifact cleanup + .gitignore | `git status` | clean | | | |
| Compatibility checks | checklist | no regressions | | | |

#### Definition of Done

Standard v4 checklist **plus**: §2 M3 verdict recorded with the Wilson
interval shown; on kill (coverage breaks), the runbook's pre-registered
fallback is recorded in the report — buckets revert to descriptive
two-threshold status and M4 proceeds descriptively only (per §2).

#### Post-Flight

- **ARCHITECTURE.md**: bucket design note + coverage result.
- **README.md**: no update until M5.
- **Other docs**: lessons/completion `r6c-m3`.

#### Notes

- The review-pile tables at 1:100 / 1:1000 are the direct answer to the RFC's
  "how big is the review pile" question and feed M4's report verbatim.
- If M2 ended with a LOFO warning, this milestone's report carries the
  warning banner (per §2 M2-LOFO kill path).

---

### Milestone 4 — Gate 2: tiered governance-metadata ablation (control / floor / ceiling)

**Goal**: A frozen Gate 2 re-examines the uncertain lane using governance
metadata in three arms — control (calibrated score only), floor (score +
fields every AGT deployment has), ceiling (floor + integration-dependent
fields) — plus a zero-parameter deterministic rule arm, yielding the
experiment's headline: end-to-end catch at ≤1% hard-action FPR, the
floor-vs-control delta, the ceiling-vs-floor integration value, and the
error-overlap ratio testing the RFC's independence assumption.

**Context**: M3 commits bucket assignments; the uncertain lane is Gate 2's
input. Corpus governance fields are coarsened to what AGT actually exposes at
runtime (verified against microsoft/agent-governance-toolkit): floor =
`requires_tool_call` (AGT sees tool name/args at `pre_tool_call` by
construction) + `coarse_source ∈ {user, tool_result, other}` (AGT
`input.source` vocabulary + interception point); ceiling adds
`contains_sensitive_sink` (≈ operator-configured manifest
`clearance`/`security_labels`) and full 6-value `source_type` (≈ host-supplied
IFC labels). The mapping is a committed methodology note. `expected_action`
and `risk_level` remain forbidden everywhere. Gate 2 arms are small logistic
regressions trained with 5-fold cross-fitting on **validation** uncertain-lane
rows only (regularization grid C ∈ {0.1, 1, 10} — ≤3 configs), then frozen;
validation reuse is acknowledged in the report and the frozen-test run stays
the sole arbiter.

**Carmack-style reliability goal**: assertion-driven feature isolation — each
arm's feature set is declared, asserted at matrix-construction time, and
recorded in the freeze record; cross-arm contamination is structurally
impossible, not just unintended.

**Important design rule**: hard-action FPR budget is partitioned up front:
flag lane ≤0.1% benign (M3's α_flag) + Gate 2 ≤0.9% benign = ≤1% total. Each
arm's Gate-2 threshold is the conformal order statistic over
validation-uncertain benign rows at β = 0.9%. Missing-metadata semantics are
fail-closed, matching AGT's IFC behavior: absent trust → `other`, absent sink
label → sensitive.

**Pinned error-overlap formulas (F-ENG-5 — pre-registered, no post-hoc
variants)**: using shadow scoring of the frozen arm over all test rows at its
frozen β threshold — miss-side ratio = P(arm fails to flag | attack ∧ Gate-1
pass-lane) ÷ P(arm fails to flag | attack, all lanes); FP-side ratio =
P(arm flags | benign ∧ Gate-1 flag-lane) ÷ P(arm flags | benign, all lanes).
The §2 M4 independence bar applies to the **worse** (larger) of the two
ratios, computed for the floor arm. Both land in `test-metrics.json` as
`overlap_miss_side` and `overlap_fp_side`.

**Refactor budget**: `No refactor permitted beyond direct implementation`.

#### Contract Block

| Field | Value |
|---|---|
| Inputs | M3 per-row buckets + calibrated scores (validation + test); corpus governance fields (`requires_tool_call`, `trust_level`, `source_type`, `contains_sensitive_sink` — nothing else); M2/M3 freeze records (provenance chain) |
| Outputs | `artifacts/round6-cascade/m4-gate2/`: `freeze-record.json` (per-arm feature manifest, CV folds seed, chosen C, β-threshold per arm), `test-metrics.json` (per-arm: uncertain-lane confusion, end-to-end TPR/FPR with Wilson intervals, floor−control and ceiling−floor deltas, error-overlap ratios as the pinned named fields `overlap_miss_side` and `overlap_fp_side` (F-ENG-5), review-pile tables at 1:100/1:1000), `lane-shift-diagnostic.json` (F-ENG-1: validation-vs-test uncertain-lane composition — lane size, attack/benign mix, score-distribution distance), `test-per-row.jsonl` (id, label, bucket, per-arm gate2 score + decision), `arm-coefficients.json` (all four arms; LR weights are metadata), `provenance.json`, `report.md` |
| Interfaces touched | new `gate2.py` (public: `coarsen(row_meta, tier) -> features` (fail-closed), `train_arm`, `FrozenArm.decide(scores, features)`); new methodology doc (below) |
| Files allowed to change | new files below; `validate-round6-cascade.py` (add m4 checks); nothing else |
| Files to read before changing anything | M3 artifacts + lessons; `artifacts/governance-eval/metrics.json` + `policy-profile.json` (round-4 governance arms, for the report's comparison section); `docs/methodology/source-to-agt-expected-action-mapping.md` (vocabulary-boundary conventions to mirror) |
| New files allowed | `meta/harness/round6-cascade/{gate2.py, run_m4_gate2.py, test_gate2.py}`, `docs/methodology/round6-corpus-to-agt-field-mapping.md`, `artifacts/round6-cascade/m4-gate2/*` (generated), lessons/completion `r6c-m4` |
| New dependencies allowed | none |
| Migration allowed | no |
| Compatibility commitments | M1–M3 artifacts byte-identical; all prior tests/validators green; corpus untouched |
| Resource bounds introduced/changed | feature dims ≤ 12 per arm (asserted); CV grid ≤ 3 configs × 5 folds per arm; arms exactly 4; shadow scoring bounded by test size (9,408) |
| Invariants/assertions required | (1) per-arm feature manifest asserted at matrix build — control = {calibrated_score}, floor = control ∪ {requires_tool_call, coarse_source}, ceiling = floor ∪ {contains_sensitive_sink, source_type}, rule-arm = floor fields only, no model; (2) ground-truth exclusion — `expected_action`/`risk_level` anywhere in a feature path trips assertion + hygiene test; (3) coarsening totality — every corpus value maps or hard-errors (no silent default for *known* values; fail-closed applies to *absent* fields only, and emits a counted `fail_closed` tag); (4) Gate-2 training rows ⊆ validation uncertain lane, asserted by row-id sets; (5) β-thresholds computed on validation only, in freeze record before test scoring; (6) determinism — fixed seeds, two runs identical |
| Debugger / inspection expectation | inspect per-arm validation-uncertain score distributions and the four arms' coefficient signs before freezing (a negative weight on `contains_sensitive_sink` would indicate a wiring bug — inspect, don't rationalize) |
| Static analysis gates | `py_compile`; full unittest suite (M1–M4); validator m1–m4 green |
| Exemplar code to copy | M3's conformal order-statistic helper (reuse via import); M2 freeze-record and per-row writer patterns; vocabulary-boundary style of `source-to-agt-expected-action-mapping.md` for the new mapping doc |
| Anti-exemplar code not to copy | round-4 governance eval's *global* policy application (this milestone is per-request routing — do not copy its arm structure); any post-test threshold or arm adjustment; using `risk_level` "just as a sanity check" anywhere in runner code |
| Refactoring discipline | `N/A — no refactoring performed, all-new files` |
| AI tolerance contract | ai_component: true. Accepted variance: none — deterministic training/inference, pinned seeds. Deterministic boundary: everything. Eval evidence: per-arm end-to-end tables + error-overlap ratios + deltas. Retry/fallback: none. Must-never: ground-truth features; test-side selection; cross-arm feature leakage. Sample budget: ≤3×5 CV per arm on validation-uncertain; one frozen test evaluation covering all four arms + shadow scoring (pre-registered as a single protocol pass) |
| Forbidden shortcuts | no arm-specific FPR budgets (all arms get the same β so deltas are like-for-like); no dropping the rule arm if it embarrasses the trained arms (it ships regardless); no blending arms; no silent imputation — every fail-closed substitution is counted and reported |
| Data classification | `Public` |
| Proactive controls in play | C1 Implement Access Control (fail-closed missing-metadata semantics mirroring AGT IFC), C4 Address Security from the Start (partitioned FPR budget), C8/C9 as prior milestones |
| Abuse acceptance scenarios | `tm-r6c-abuse-2` (ground-truth leakage — BDD row); new input surface = corpus governance columns (trusted, frozen), with the realistic abuse analogue being *missing/hostile metadata at deployment*: covered by the fail-closed BDD rows (absent trust → `other`, absent sink → sensitive) |
| Measurement deliverables | `N/A — not value-bearing` in §5A product sense; evidence = the §2 M4 verdict set (floor−control ≥5pt, overlap ≤1.5×, end-to-end ≥80% @ ≤1%) |

#### Out of Scope / Must Not Do

- No AGT `AnnotatorDispatcher`/Rego implementation — measurement only (the
  integration shape is documented in the mapping note's appendix for PR2).
- No new metadata fields beyond the four; no `risk_level` rehabilitation.
- No per-family Gate-2 specialization.
- No re-touching M1–M3 frozen components.

#### Files Allowed To Change

| File | Planned Change |
|---|---|
| `meta/harness/round6-cascade/gate2.py` | NEW: fail-closed coarsening, per-arm feature manifests, CV training, `FrozenArm`, deterministic rule arm (`uncertain ∧ requires_tool_call ∧ coarse_source ≠ user → flag`) |
| `meta/harness/round6-cascade/run_m4_gate2.py` | NEW: runner — load M3 lanes → coarsen → train 3 LR arms on validation-uncertain (CV) → β-thresholds → freeze → single test pass (4 arms + shadow scoring over all test rows for error-overlap) → metrics |
| `meta/harness/round6-cascade/test_gate2.py` | NEW: BDD tests below |
| `meta/harness/round6-cascade/validate-round6-cascade.py` | Add m4 checks (feature manifests present, forbidden fields absent, freeze ordering) |
| `docs/methodology/round6-corpus-to-agt-field-mapping.md` | NEW: corpus→AGT field mapping with AGT code citations, fail-closed semantics, tier definitions, PR2 integration appendix (AnnotatorDispatcher + `confidence.rego` shape) |

#### Step-by-Step

1. Pre-flight: M3 lessons; baseline green (suite + validators m1–m3).
2. Write the mapping doc first (it is the contract for `coarsen()`).
3. Write `test_gate2.py` BDD stubs; confirm expected failures.
4. Implement `coarsen()` + feature manifests + rule arm; unit-green.
5. Train 3 LR arms (5-fold CV, C grid) on validation-uncertain; inspect coefficients (debugger expectation); compute β-thresholds; write freeze record.
6. Single frozen test pass: 4 arms over uncertain lane + shadow scoring over all test rows; compute end-to-end tables, deltas, pinned error-overlap ratios, lane-shift diagnostic (F-ENG-1), review-pile tables.
7. Validator extension + run; `report.md` with all §2 M4 verdicts + comparison section vs round-4 governance arms (metric-difference caveat stated) + LOFO warning banner if M2 raised it.
8. Evidence Log, lessons, completion, tracker.

#### BDD Acceptance Scenarios

**Feature: tiered cross-modal Gate 2**

| Scenario | Category | Given | When | Then |
|---|---|---|---|---|
| Coarsening totality | happy path | all 44,800 rows' metadata | `coarsen(·, tier)` per tier | every row maps; tier feature dims exactly as declared |
| Fail-closed trust | dependency failure / abuse-analogue | row with `trust_level` field removed | `coarsen()` | `coarse_source = other`, `fail_closed` tag counted; no exception |
| Fail-closed sink | dependency failure / abuse-analogue | row with `contains_sensitive_sink` removed | ceiling coarsen | treated as sensitive; tag counted |
| Unknown value | invalid input | `trust_level = "admin"` (not in corpus vocab) | `coarsen()` | hard error naming field and value — unknown ≠ absent |
| Arm isolation | assertion/invariant | control-arm matrix build | metadata column injected | assertion fires; freeze-record manifest mismatch detected by validator |
| Ground-truth exclusion | abuse `tm-r6c-abuse-2` | feature path with `expected_action` | hygiene test | assertion fires in build; validator rejects artifact |
| Rule arm determinism | happy path | floor-tier features for uncertain rows | rule arm decides | exactly `requires_tool_call ∧ coarse_source≠user`; zero trained parameters in freeze record |
| Training-set purity | assertion/invariant | Gate-2 training row ids | training set built | ⊆ validation uncertain lane; pass/flag-lane id injected trips assertion |
| Threshold provenance | persistence/protocol | completed run | validator | β-thresholds cite validation-uncertain benign counts; recorded before test artifacts |
| Empty uncertain lane | empty state | synthetic router flagging everything | runner | structured abort: "Gate 2 has no lane", no division errors |
| End-to-end reproducibility | compatibility | committed per-row file | recompute all per-arm headline metrics | exact match with `test-metrics.json` |
| Determinism | assertion/invariant | fixed seeds | two full runs | identical freeze records and metrics |

Concurrency/retry/resource-limit: N/A — single-threaded, bounded by test-split
size; abort-on-failure.

#### Regression Tests

- M1–M3 suites + validators green; artifact hashes unchanged.
- `check-round4.py` + round-4 validators green.

#### Compatibility Checklist

- [ ] M1–M3 artifacts byte-identical
- [ ] M1–M3 tests green
- [ ] No change to `normalize.py` / `head.py` / `buckets.py` / `common.py`
- [ ] Corpus untouched

#### E2E Runtime Validation

**File**: `meta/harness/round6-cascade/validate-round6-cascade.py` (+ runner `--dry-run`)

| E2E Test | What It Proves | Pass Criteria |
|---|---|---|
| `run_m4_gate2.py --dry-run` (synthetic 300-row lane) | full pipeline: coarsen → train → freeze → decide → metrics | exits 0; sample artifacts validate |
| `validate-round6-cascade.py m4` | artifact contract incl. feature manifests + forbidden-field absence | green |
| Headline recompute | per-row file reproduces every §2-cited number | exact match |

#### Smoke Tests

- [ ] Full unittest suite green
- [ ] Coefficient signs inspected for all arms; anomalies investigated before freeze
- [ ] `report.md` cites all three §2 M4 bars verbatim with verdicts; fail-closed substitution counts reported; rule-arm result included regardless of outcome
- [ ] `git status` clean outside allow-list

#### Evidence Log

| Step | Command / Check | Expected Result | Actual Result | Pass/Fail | Notes |
|---|---|---|---|---|---|
| Baseline tests | suite + validators m1–m3 + check-round4 | green | | | |
| Mapping doc | `round6-corpus-to-agt-field-mapping.md` | committed before `coarsen()` implementation | | | |
| BDD tests created | `test_gate2.py` | fail for expected reason | | | |
| Implementation | `gate2.py`, `run_m4_gate2.py` | contract satisfied | | | |
| Arm training + freeze | 3 LR arms CV + β-thresholds | freeze record before test | | | |
| Frozen test pass | 4 arms + shadow scoring, one run | all tables recorded | | | |
| **M4 verdict: floor−control** | ≥5pt end-to-end catch at fixed FPR | accept/kill recorded | | | |
| **M4 verdict: error overlap** | worse of `overlap_miss_side`/`overlap_fp_side` ≤1.5 | accept/kill recorded; kill cites lane-shift diagnostic | | | |
| **M4 verdict: headline** | ≥80% catch @ ≤1% hard-action FPR | accept/kill recorded | | | |
| Ceiling−floor delta | integration-value number | recorded (informational, no gate) | | | |
| Static checks + validator | `py_compile`, unittest, validator m1–m4 | green | | | |
| Determinism check | second full run | identical | | | |
| Artifact cleanup + .gitignore | `git status` | clean | | | |
| Compatibility checks | checklist | no regressions | | | |

#### Definition of Done

Standard v4 checklist **plus**: all three §2 M4 verdicts recorded; the
shared-blind-spot kill path (conditional failure >50%) — if triggered — is
recorded as the experiment's primary negative result with the same prominence
an accept would get.

#### Post-Flight

- **ARCHITECTURE.md**: Gate 2 ablation row in evidence baseline.
- **README.md**: no update until M5.
- **Other docs**: mapping methodology note (committed in-milestone); lessons/completion `r6c-m4`.

#### Notes

- The deterministic rule arm is the "what every deployment gets with zero
  training" reference — if it matches the trained floor arm, that is itself a
  publishable finding favoring Rego-only integration.
- Round-4 governance-arm comparison (69.3% prevention) is reported with an
  explicit metric-difference caveat: prevention-of-unsafe-action ≠ detection
  catch rate; the numbers contextualize, they do not gate.

---

### Milestone 5 — Reporting + closeout: per-family floors, hard-negative note, evidence publication

**Goal**: The round-6 evidence is consolidated and published inside the repo:
per-family and per-bypass-class end-to-end floors on the surviving
configuration, an in-corpus hard-negative robustness note, a final round-6
report carrying every §2 verdict (accepts and kills with equal prominence),
and README + CLAIMS-LEDGER + ARCHITECTURE.md updated so a reviewer can walk
from every public sentence to a committed artifact.

**Context**: M1–M4 committed per-row artifacts for every stage. M5 is pure
aggregation over those committed files plus corpus metadata joins — **no new
scoring, no new test-split evaluation, no model execution**. The per-family
floor check (§2 M5: no attack family at 0% in the success configuration) is
computed from `m4-gate2/test-per-row.jsonl` joined to corpus `attack_class`/
`bypass_class`. The hard-negative note reuses the corpus's adjacent-security
benign subclasses (`quoted_injection_example`, `benign_security_discussion`,
`security_training_material`, etc.) as the in-corpus NotInject analogue:
end-to-end FP rates on exactly the trigger-word-laden benign categories,
with an explicit limitation recommending the external NotInject benchmark
(arXiv:2410.22770) as future work — not built here.

**Carmack-style reliability goal**: evidence-over-claims as a checkable
property — every number in README/CLAIMS-LEDGER/report is recomputable from a
named committed artifact by the aggregation script, and the validator checks
the consistency.

**Important design rule**: the report's verdict table is a verbatim copy of
§2 with a verdict column appended — no reframing, no softened kill language,
no headline number that lacks a §2 row. The synthetic-corpus, validation-
reuse, and adaptive-attacker caveats appear in the report's first section,
not a footnote.

**Refactor budget**: `No refactor permitted beyond direct implementation`.

#### Contract Block

| Field | Value |
|---|---|
| Inputs | committed `artifacts/round6-cascade/m1–m4` per-row files + metrics + freeze records; corpus metadata (join keys + class fields only); `docs/CLAIMS-LEDGER.md`, `README.md`, `docs/ARCHITECTURE.md` (current text) |
| Outputs | `artifacts/round6-cascade/m5-summary/`: `summary-metrics.json` (per-family floors, per-bypass floors, hard-negative FP table, consolidated verdict table), `provenance.json`; `docs/reports/round6-cascade-report.md`; updated `README.md` Evidence Snapshot, `docs/CLAIMS-LEDGER.md`, `docs/ARCHITECTURE.md` |
| Interfaces touched | none — aggregation + docs |
| Files allowed to change | new files below; `README.md` (Evidence Snapshot section only), `docs/CLAIMS-LEDGER.md` (additive round-6 section), `docs/ARCHITECTURE.md` (evidence baseline + components), `docs/UPSTREAM-PR-PLAN.md` (evidence-pointer line only, F-CEO-1), `validate-round6-cascade.py` (add m5 consistency checks); nothing else |
| Files to read before changing anything | all m1–m4 `report.md` files + lessons; `docs/CLAIMS-LEDGER.md` in full (its claim-to-evidence mapping conventions are the format to follow) |
| New files allowed | `meta/harness/round6-cascade/run_m5_summary.py`, `meta/harness/round6-cascade/test_summary.py`, `artifacts/round6-cascade/m5-summary/*` (generated), `docs/reports/round6-cascade-report.md`, lessons/completion `r6c-m5` |
| New dependencies allowed | none |
| Migration allowed | no |
| Compatibility commitments | m1–m4 artifacts byte-identical; all prior tests/validators green; README changes confined to the Evidence Snapshot section (diff-checked); CLAIMS-LEDGER strictly additive (no existing round-4 claim rows edited) |
| Resource bounds introduced/changed | none new — aggregation over ≤9,408-row files; stated, not silently waived |
| Invariants/assertions required | (1) no-new-scoring: `run_m5_summary.py` imports no model, embedding, or training code (asserted import manifest); (2) every §2 row appears exactly once in the consolidated verdict table with a non-empty verdict (asserted); (3) every number written into README/report matches `summary-metrics.json` recomputation (validator cross-check on a marker-tagged number list); (4) join completeness — every m4 per-row id joins to corpus metadata; orphans hard-error |
| Debugger / inspection expectation | spot-inspect 3 per-family floor values against hand computation from per-row files before publishing |
| Static analysis gates | `py_compile`; full unittest suite (M1–M5); validator m1–m5 green |
| Exemplar code to copy | CLAIMS-LEDGER's existing claim→evidence row format; round-4 report structure in `docs/reports/round4-mac-embedding-sweep-evidence.md` (artifact-hash citation style) |
| Anti-exemplar code not to copy | README's pre-round-6 Evidence Snapshot framing if any §2 kill occurred (do not leave stale strong claims standing next to new negative results); any "production-ready"/"certified" language (repo red line) |
| Refactoring discipline | `N/A — no refactoring performed` |
| AI tolerance contract | `N/A — no AI component executed in this milestone` (aggregation of committed artifacts only; the no-new-scoring invariant enforces this) |
| Forbidden shortcuts | no selective reporting (every arm, every family, every bypass class appears — including zeros and kills); no rounding that crosses a §2 bar (report one decimal, verdicts computed on raw values); no editing round-4 claims to make round-6 look better |
| Data classification | `Public` |
| Proactive controls in play | C9 Security Logging and Monitoring (consistency validator), C8 Protect Data Everywhere (summary artifacts metadata-only) |
| Abuse acceptance scenarios | `N/A — no new surface introduced`: reads committed artifacts, writes docs + one summary artifact; hygiene (no-text) test extended to m5 outputs |
| Measurement deliverables | This milestone IS the measurement readout: consolidated §2 verdict table + review-pile economics + per-family floors, published in `docs/reports/round6-cascade-report.md` |

#### Out of Scope / Must Not Do

- No new scoring of any split; no model execution of any kind.
- No external benchmark runs (NotInject/PINT are documented as future work).
- No upstream PR drafting (that is the existing UPSTREAM-PR-PLAN track, which
  consumes this report; the PR2 integration appendix already lives in M4's
  mapping doc).
- No tuning, no "one more quick experiment" — kills stand as recorded.

#### Files Allowed To Change

| File | Planned Change |
|---|---|
| `meta/harness/round6-cascade/run_m5_summary.py` | NEW: aggregation — per-family/per-bypass end-to-end floors (m4 per-row ⋈ corpus classes), hard-negative benign-subclass FP table, consolidated §2 verdict table |
| `meta/harness/round6-cascade/test_summary.py` | NEW: BDD tests below |
| `meta/harness/round6-cascade/validate-round6-cascade.py` | Add m5 checks: number-consistency cross-check, verdict-table completeness, no-text hygiene |
| `docs/reports/round6-cascade-report.md` | NEW: final report — caveats first (incl. multilingual accepted residual, F-CEO-2), §2 verdict table verbatim+verdicts, ablation narrative (Gate 0 → head → buckets → Gate 2), review-pile economics, LOFO, floors, hard-negative note, **Decision hook section (F-CEO-1)**: verdict-combination → next-action table (all §2 accepts → PR2 proposal updated with round-6 artifacts; M4 overlap-kill → negative-result publication + encoder-upgrade runbook proposal; M2 head-kill → encoder-upgrade redirect, no PR2 detection claim; M3 coverage-kill → buckets demoted to descriptive, PR2 limited to Gate-0+head evidence), next steps |
| `docs/UPSTREAM-PR-PLAN.md` | One-line evidence-pointer update: round-6 report supersedes round-4 numbers for PR2 framing (F-CEO-1; additive, no plan restructuring) |
| `README.md` | Evidence Snapshot: add round-6 rows (keep round-4 rows; mark superseded operating points as such, never delete) |
| `docs/CLAIMS-LEDGER.md` | Additive round-6 section: every public claim → artifact path + §2 row |
| `docs/ARCHITECTURE.md` | Final evidence baseline + round-6 component rows |

#### Step-by-Step

1. Pre-flight: M4 lessons; baseline green (suite + validators m1–m4).
2. Write `test_summary.py` BDD stubs; confirm expected failures.
3. Implement `run_m5_summary.py`; run; hand-verify 3 floor values (debugger expectation).
4. Write `docs/reports/round6-cascade-report.md` from `summary-metrics.json`.
5. Update README Evidence Snapshot, CLAIMS-LEDGER (additive), ARCHITECTURE.md.
6. Extend + run validator m5 (number-consistency pass over the docs).
7. Evidence Log, lessons, completion, tracker — close the runbook.

#### BDD Acceptance Scenarios

**Feature: evidence consolidation and publication**

| Scenario | Category | Given | When | Then |
|---|---|---|---|---|
| Per-family floors | happy path | m4 per-row + corpus classes | aggregation | all 8 families present with end-to-end catch; sums match m4 totals |
| Per-bypass floors | happy path | same | aggregation | all bypass classes present incl. multilingual (even if 0%) |
| Hard-negative table | happy path | adjacent-security benign subclasses | aggregation | FP rate per subclass; zero rows silently dropped |
| Verdict completeness | assertion/invariant | §2 table (M4's three bars expanded — 8 verdict lines) | verdict table built | every line exactly once, verdict non-empty; missing verdict aborts |
| Number consistency | persistence/protocol | README/report marker-tagged numbers | validator m5 | every tagged number matches `summary-metrics.json` |
| Join orphan | invalid input | per-row id absent from corpus | aggregation | hard error naming the id |
| No-new-scoring | assertion/invariant | `run_m5_summary.py` import manifest | hygiene test | no model/embedding/training imports; injection of `head` import trips test |
| Empty input guard | empty state | missing m4 artifact dir | runner | structured abort, no partial docs written |
| Claims-ledger additivity | compatibility / backward compat | pre-M5 CLAIMS-LEDGER text | diff after update | existing rows byte-identical; only additions |

Concurrency/retry/resource-limit/dependency-failure beyond the above: N/A —
single-threaded aggregation of local committed files.

#### Regression Tests

- M1–M4 suites + validators green; artifact hashes unchanged.
- `check-round4.py` green; README diff confined to Evidence Snapshot section.

#### Compatibility Checklist

- [ ] m1–m4 artifacts byte-identical
- [ ] All prior tests green
- [ ] CLAIMS-LEDGER round-4 rows untouched
- [ ] README changes confined to Evidence Snapshot
- [ ] No harness module modified except the validator

#### E2E Runtime Validation

**File**: `meta/harness/round6-cascade/validate-round6-cascade.py`

| E2E Test | What It Proves | Pass Criteria |
|---|---|---|
| `run_m5_summary.py` (full) | aggregation completes over real m1–m4 artifacts | exits 0; `summary-metrics.json` validates |
| `validate-round6-cascade.py m5` | docs↔artifact number consistency + verdict completeness | green |
| Recompute spot-check | three §2-cited numbers recomputed from per-row files | exact match |

#### Smoke Tests

- [ ] Full unittest suite green
- [ ] Report reads correctly: caveats first, kills as prominent as accepts
- [ ] A reviewer can trace each README Evidence Snapshot number to an artifact path via CLAIMS-LEDGER
- [ ] `git status` clean outside allow-list

#### Evidence Log

| Step | Command / Check | Expected Result | Actual Result | Pass/Fail | Notes |
|---|---|---|---|---|---|
| Baseline tests | suite + validators m1–m4 + check-round4 | green | | | |
| BDD tests created | `test_summary.py` | fail for expected reason | | | |
| Implementation | `run_m5_summary.py` | contract satisfied | | | |
| Hand verification | 3 floor values vs per-row files | exact match | | | |
| **M5 check vs §2** | no family at 0% in success config | recorded (pass or documented miss) | | | |
| Report + docs updates | report, README, CLAIMS-LEDGER, ARCHITECTURE | written; additive where required | | | |
| Number-consistency validator | `validate-round6-cascade.py m5` | green | | | |
| Static checks | `py_compile`, unittest m1–m5 | green | | | |
| Artifact cleanup + .gitignore | `git status` | clean | | | |
| Compatibility checks | checklist | no regressions | | | |

#### Definition of Done

Standard v4 checklist **plus**: consolidated verdict table covers every §2
gate row, with M4's three bars (floor−control, error overlap, headline) as
separate verdict lines — eight verdicts total; report caveats (synthetic corpus, validation reuse, benign-side-only
guarantee, no adaptive-adversary claim) sit in the report's opening section;
Milestone Tracker shows all five milestones with honest terminal states.

#### Post-Flight

- **ARCHITECTURE.md**: final evidence baseline (done in-milestone).
- **README.md**: Evidence Snapshot (done in-milestone).
- **Other docs**: lessons/completion `r6c-m5`; runbook closed via `/slo-retro`.

#### Notes

- If M4 ended in the shared-blind-spot kill, this report is the negative-result
  publication — same structure, same prominence; the "next steps" section then
  leads with the pre-registered redirects (encoder upgrade; TaskTracker-style
  cross-modal evidence) rather than burying them.
- Real-traffic advisory-mode validation remains the explicit non-passable gate
  of this whole runbook and is restated in the report's closing section.

---

## 18. Documentation Update Table

| Milestone | ARCHITECTURE.md | README.md | .gitignore | Other Docs |
|---|---|---|---|---|
| 1 | components table + Gate 0 result | — | scratch patterns | lessons/completion r6c-m1 |
| 2 | Gate 1 result row | — | — | lessons/completion r6c-m2 |
| 3 | bucket design note | — | — | lessons/completion r6c-m3 |
| 4 | Gate 2 ablation row | — | — | corpus→AGT field-mapping methodology note; lessons/completion r6c-m4 |
| 5 | final evidence baseline | Evidence Snapshot tables | review staleness | round-6 report; CLAIMS-LEDGER; lessons/completion r6c-m5 |
