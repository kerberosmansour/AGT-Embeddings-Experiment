# AGT Red Team Benchmark Harness and Agent Traps Scenario Schema — AGT-Embeddings-Experiment (AI-First Runbook v4)

> **Purpose**: Turn the validated Innovation-Sandbox spike evidence (EXP-agt-redteam-agent-traps-opencre, exit state `promote_to_runbook`) into a small, reproducible, stdlib-only **agent-control benchmark** — scenario schema + validator, a deterministic mock behavioural harness, an Agent-Traps smoke suite, an evidence-level (non-certification) reporter, and raw-free upstream-ready packaging — staged under `benchmarks/agent-redteam/` in this repo before any upstream contribution.
> **Audience**: AI coding agents first, humans second.
> **Core philosophy**: Prefer automated guardrails over intention; direct inspection over guessing; executable assumptions over comments; bounded design over silent growth; evidence over claims.
> **How to use**: Work milestones sequentially. Complete the Global Entry/Exit Protocols around each. Never skip ahead. Treat this document as an execution contract.
> **Prerequisite reading**: [EXPERIMENT.md](slo/experiments/agt-redteam-agent-traps-opencre/EXPERIMENT.md) (the authoritative Experiment Book — §6 PrecisionModel carries the falsifiable thresholds; §10 is the handoff seed this runbook implements), [handoff.md](slo/experiments/agt-redteam-agent-traps-opencre/handoff.md), [demo.md](slo/experiments/agt-redteam-agent-traps-opencre/demo.md), [README.md](../README.md), `.github/workflows/readiness.yml`.

> **Provenance**: Authored by `/slo-plan` from the `promote_to_runbook` handoff. The scratch evidence (`experiments/agt-redteam-agent-traps-opencre/s1..s8`) is the seed material; this runbook re-implements that evidence as durable benchmark code under `benchmarks/agent-redteam/`. **Authored autonomously on a founder-greenlit loop; the outcome-first contract and M6-M8 expansion were critiqued before milestone execution, and M1/M2 are now merged on this branch.**

---

## 0. How To Use This Template

1. Fill Runbook Metadata, Architecture, and Milestone Plan before implementation (done — this document).
2. Work milestones sequentially (M1 → M8).
3. Before each milestone, complete the Global Entry Protocol (§7).
4. During implementation, follow §4 (Carmack-Style Best Practices) and the milestone Contract Block literally.
5. After each milestone, complete the Global Exit Protocol (§8) and fill the Evidence Log.
6. Do not mark a milestone done until its Definition of Done is objectively satisfied.

---

## 1. Runbook Metadata

| Field | Value |
|---|---|
| Runbook ID | `agt-redteam` |
| Project name | `AGT-Embeddings-Experiment` (benchmark staged under `benchmarks/agent-redteam/`) |
| Primary stack | Python 3.12, standard library only (mirrors `meta/harness/**` convention) |
| Primary package/app names | `benchmarks/agent-redteam/` (schema, scenarios, harness, controls, reporters, adapters, tests) |
| Prefix for tests and lesson files | `agtrt` |
| Default unit test command | `python -m unittest discover -s benchmarks/agent-redteam -p "test_*.py"` |
| Default integration/BDD test command | `python -m unittest discover -s benchmarks/agent-redteam -p "test_*.py" -v` |
| Default E2E/runtime validation command | `bash benchmarks/agent-redteam/run-smoke.sh` |
| Default build/boot command | `python -c "import importlib,glob,sys; [importlib.import_module(p) for p in []]"` (library — boot = imports + validators succeed; see smoke) |
| Default formatter command | `N/A — repo defines no formatter; whitespace/hygiene gate is git diff --check (used in readiness.yml)` |
| Default static analysis / lint command | `python -m py_compile $(git ls-files 'benchmarks/agent-redteam/**/*.py')` + `git diff --check` |
| Default dependency / security audit command | `N/A — stdlib only; audit = grep for non-stdlib imports must return empty (enforced in M1 test)` |
| Default debugger or state-inspection tool | `python -m pdb` / `breakpoint()` / `python -m json.tool` for artifact inspection |
| Allowed new dependencies by default | `none` (stdlib only; any exception requires an explicit Contract Block entry + license/security rationale) |
| Schema/config migration allowed by default | `no` |
| Public interfaces stable by default | `yes` |

### Public interfaces that must remain stable unless explicitly listed otherwise

- `benchmarks/agent-redteam/schema/scenario.schema.json` (scenario contract — frozen field set once M1 closes; additive-only after)
- `benchmarks/agent-redteam/schema/result.schema.json` and `benchmarks/agent-redteam/harness/tool_trace.schema.json` (result/trace contracts)
- The validator CLI surface: `python benchmarks/agent-redteam/schema/validate_scenarios.py <paths...>` (exit code + JSON-on-stdout contract)
- `benchmarks/agent-redteam/run-smoke.sh` (the reproducible demo path; referenced by CI)
- The AGT-AC control-id namespace (`AGT-AC-NNN`) and the OpenCRE relation vocabulary (`exact|broad|narrow|related|candidate`)
- The evidence-level ladder `L0_declared | L1_static | L2_mock | L3_live` and the reporter invariant `certification_claim: false`

### Existing repo interfaces this runbook MUST NOT touch

- `.github/workflows/readiness.yml` is **read-and-extend-only**: M3 appends one job; it must not modify or reorder existing readiness steps.
- `corpus/**`, `meta/harness/**`, `tools/**`, `rust/**`, `experiments/agt-redteam-agent-traps-opencre/**` (the latter is mac-owned experiment scratch — **read-only seed; never edited by this runbook**).

---

## 2. Milestone Tracker

Single source of truth for progress. Update as each milestone completes.

| # | Milestone | Status | Started | Completed | Lessons File | Completion Summary |
|---|---|---|---|---|---|---|
| 1 | Scenario schema + validator (productionize s1) | `done` | 2026-06-19 | 2026-06-19 | `docs/slo/lessons/agtrt-m1.md` | `docs/slo/completion/agtrt-m1.md` |
| 2 | Mock behavioural harness + trace schema (productionize s4) | `done` | 2026-06-19 | 2026-06-19 | `docs/slo/lessons/agtrt-m2.md` | `docs/slo/completion/agtrt-m2.md` |
| 3 | Agent-Traps deterministic smoke suite + CI integration | `done` | 2026-06-19 | 2026-06-19 | `docs/slo/lessons/agtrt-m3.md` | `docs/slo/completion/agtrt-m3.md` |
| 4 | Control-linked evidence-level reporter (productionize s6) | `done` | 2026-06-19 | 2026-06-19 | `docs/slo/lessons/agtrt-m4.md` | `docs/slo/completion/agtrt-m4.md` |
| 5 | Upstream-ready docs + raw-free hygiene gate + PR-boundary packaging (productionize s8) | `not_started` | | | | |
| 6 | Live Goose adapter — real-agent (L3) assessment in a hermetic sandbox (productionize s7) | `not_started` | | | | |
| 7 | OpenCRE relation research + relation-quality validator | `not_started` | | | | |
| 8 | Shareable evidence scorecard product (productionize the scorecard wedge) | `not_started` | | | | |

<!-- Status values: not_started | in_progress | blocked | done -->
<!-- Honest exit states (optional): human_review_required | blocked_by_operator | blocked_by_upstream | issue_filed | accepted_risk -->
<!-- Fail-safe: any unrecognised status MUST be treated as `blocked`, never silently `done`. -->
<!-- Lessons files: docs/slo/lessons/agtrt-m<N>.md   Completion summaries: docs/slo/completion/agtrt-m<N>.md -->

### Scope reconciliation (raw §10 seed → runbook milestones)

The §10 handoff listed 7 raw milestone candidates. **Founder directive (2026-06-19): the milestone cap is lifted for this runbook** — the previously-routed-out Goose adapter, OpenCRE research, and scorecard-product are pulled **IN** as full milestones (M6/M7/M8), each outcome-first with a stage-level front-to-end test, so the benchmark is delivered end-to-end (not deferred to separate tickets). Only the content-injection **fixture pack** stays routed out (DW-001). Updated dispositions:

| Raw §10 candidate | Curated disposition | Where it lives in this plan |
|---|---|---|
| Agent Traps scenario schema | `promote_to_runbook` | **M1** |
| Mock behavioural harness | `promote_to_runbook` | **M2** |
| Agent Traps smoke suite | (connective) | **M3** |
| Control-linked reporter | (connective, with §6/scorecard evidence) | **M4** |
| Upstream PR boundary draft | `promote_to_runbook` | **M5** |
| Content-injection fixture pack | `promote_to_ticket` | **OUT → `/slo-ticket-plan`** (M5 files it; harness leaves a typed seam) |
| Goose adapter dry-run | now `promote_to_runbook` (founder) | **IN → M6** (real sandboxed L3 live adapter; s7 contract is the spec) |
| OpenCRE-backed AGT-AC catalog | now `promote_to_runbook` (founder) | **IN → M7** (relation research + relation-quality validator; M4 consumes verified relations) |
| Evidence-level scorecard (as product) | now `promote_to_runbook` (founder) | **IN → M8** (shareable scorecard product built on M4's internal reporter) |

---

## 3. End-to-End Architecture Diagram

### Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                 benchmarks/agent-redteam/  (staged in this repo)               │
│                                                                                │
│  ┌────────────┐    ┌──────────────┐    ┌───────────────┐   ┌────────────────┐  │
│  │ scenarios/ │───▶│   schema/    │───▶│   harness/    │──▶│  reporters/    │  │
│  │ *.json     │ M1 │ validate_    │ M1 │ runner +      │M2 │ evidence-level │  │
│  │ (24 seed)  │    │ scenarios.py │    │ mock tools +  │   │ scorecard      │  │
│  └────────────┘    │ *.schema.json│    │ trace schema  │M3 │ (L0..L3,       │  │
│        ║           └──────────────┘    └───────┬───────┘   │  cert=false)   │M4│
│        ║ seed evidence                          │          └───────┬────────┘  │
│  - - - - - - - - - - - - - - - - - - - - - -    │ attempted/executed │          │
│  experiments/.../s1..s8 (mac-owned, READ-ONLY) │ traces (JSONL)     │          │
│                                                 ▼                    ▼          │
│  ┌────────────┐   reads (read-only)     ┌───────────────┐   ┌────────────────┐  │
│  │ controls/  │◀────────────────────────│ smoke suite   │   │ docs + raw-free │ │
│  │ AGT-AC ids │   M4 maps results→ctrl  │ run-smoke.sh  │M3 │ hygiene gate +  │M5│
│  │ (from s5)  │                         │ + CI job      │   │ PR boundaries   │  │
│  └────────────┘                         └───────────────┘   └────────────────┘  │
│                                                                                │
│   adapters/  (M5 leaves a typed seam only — Goose dry-run is a SEPARATE ticket) │
│                                                                                │
│  Legend:  ─── built by this runbook   - - - existing seed (read-only)          │
│           ║ trust/ownership boundary   ▶ data flow   M# = milestone            │
│  External (NOT in this runbook): live Goose/providers, OpenCRE API, upstream PR │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Component Summary Table

| Component | Responsibility | Existing/New/Changed | Milestone | Key Interfaces |
|---|---|---|---|---|
| `schema/scenario.schema.json` + `result.schema.json` | Frozen scenario/result contract (six trap classes, controls, views, session model, success conditions) | New (from s1) | M1 | JSON Schema files |
| `schema/validate_scenarios.py` | Validate scenarios; report trap-class coverage; exit non-zero on gap | New (from s1) | M1 | CLI: `validate_scenarios.py <paths>` → JSON stdout + exit code |
| `scenarios/*.json` | 24 seed scenarios (4 per trap class) | New (from s1) | M1 | Data |
| `harness/runner.py` + `harness/mock_tools.py` | Deterministic mock tools (shell/email/memory/mcp_registry/audit + A2A) emitting attempted/executed traces | New (from s4) | M2 | `tool_trace.schema.json`; JSONL traces |
| `harness/tool_trace.schema.json` | Trace contract: `attempted`, `executed`, `blocked_at`, `audit_event_present`, `canary_leaked` | New (from s4) | M2 | JSON Schema |
| `run-smoke.sh` + CI job | Reproducible end-to-end smoke (validate → harness → report) | New + CI extend | M3 | `readiness.yml` job (append-only) |
| `controls/agt-ac.csv` (+ relation vocab) | AGT-AC control catalog seed, read-only mapping target | New (from s5, read-only copy) | M4 | `AGT-AC-NNN` ids + relation status |
| `reporters/scorecard.py` | Aggregate results by trap class / control / evidence level; `certification_claim:false` | New (from s6) | M4 | JSON + Markdown report |
| `docs/` + hygiene gate + `PROMOTION.md` | Raw-free scan gate; upstream PR-boundary doc; deferred-route ticket/research/idea filings | New (from s8) | M5 | hygiene test + GH issues |

### Data Flow Summary

| Flow | From | To | Protocol/Mechanism | Bounded? | Failure Mode | Milestone |
|---|---|---|---|---|---|---|
| scenario validation | `scenarios/*.json` | validator | file read → JSON | yes (≤ few hundred files) | non-zero exit + stderr listing | M1 |
| mock tool trace | harness runner | `*.jsonl` trace | in-process function call | yes (≤ tools×scenarios) | trace records `blocked_at`; never executes real side effect | M2 |
| result aggregation | trace + scenario | scorecard | file read → JSON/MD | yes | missing field → structured error, no silent default | M4 |
| smoke pipeline | all of the above | CI status | `bash` script + exit codes | yes (60s/script hard cap) | first non-zero exit fails the job | M3 |
| raw-free scan | all generated artifacts | hygiene gate | regex/heuristic scan | yes | any raw-payload/secret heuristic hit → fail closed | M5 |

---

## 4. Carmack-Style Development Best Practices

The universal v4 reliability rules apply to every milestone (full text in the canonical template `docs/slo/templates/runbook-template_v_4_template.md`). The load-bearing ones for this benchmark:

- **4.1 Inspect state, don't guess** — use `python -m pdb` / `python -m json.tool` on generated artifacts before editing extractor/validator logic. (s3's first run was a real bug found by inspecting the report, not by guessing.)
- **4.2 Static analysis is mandatory** — `python -m py_compile` over all changed `.py` + `git diff --check` must pass every milestone. A grep gate proves stdlib-only.
- **4.3 Assertions are executable comments** — encode the load-bearing invariants (a mock tool that is `executed:false` must have `blocked_at != null`; a validated scenario must carry ≥1 `AGT-AC-` control; a generated artifact must contain no raw payload).
- **4.4 Bounded resources** — scenario/trace/report sizes are bounded by input counts; the harness must cap turns/timeout (`max_turns`, `timeout_seconds`) and never loop unboundedly.
- **4.5 Make invalid states unrepresentable** — trap class is a closed enum; relation status is a closed enum; evidence level is a closed enum; `certification_claim` is a literal `false`, never a computed truthy value.
- **4.6 Preserve compatibility** — schema field sets are additive-only after M1 freezes them.
- **4.7 / 4.8 Small reviewable changes; no silent failure** — validators exit non-zero with a reason; nothing swallows a gap into a green result.

---

## 5. High-Level Design for State Modeling / Formal Verification

### 5.1 System Goal
The benchmark must produce **honest, reproducible, raw-free evidence** about which agent-control layer a scenario exercises and whether an unsafe action was *attempted* vs *executed*, without ever executing a real side effect, leaking a raw payload, or asserting certification. Correctness = determinism + raw-free + no-overclaim, not throughput.

### 5.2 Main Components

| Component | Protocol Role | Key State (durable / volatile) | Visible Actions |
|---|---|---|---|
| validator | gatekeeper | durable: schema + scenarios; volatile: coverage counts | accept/reject scenario set |
| mock-tool harness | simulator | durable: trace JSONL; volatile: per-call attempted/executed | emit trace; block unsafe |
| reporter | aggregator | durable: scorecard JSON/MD | summarize by trap/control/evidence-level |
| hygiene gate | inspector | volatile: scan result | fail closed on raw/secret heuristic |

### 5.3 Abstract State

| Variable | Abstract Type | Why Needed | Bound | Explosion Risk |
|---|---|---|---|---|
| `trap_class` | enum(6) | coverage correctness | 6 | low |
| `attempted` / `executed` | bool × bool | the load-bearing behavioural distinction | 4 combos | low |
| `evidence_level` | enum(L0..L3) | no-overclaim correctness | 4 | low |
| `relation_status` | enum(5) | honest mapping | 5 | low |

### 5.4 Actions / Transitions

| Action | Preconditions | State Updates | Failure / Interleaving Notes |
|---|---|---|---|
| validate(scenario) | file parses | coverage++ for trap_class | reject on missing/extra field or unknown enum |
| simulate(tool, unsafe) | tool known | trace.attempted=true; executed=¬unsafe; blocked_at set iff blocked | mock NEVER performs a real effect |
| aggregate(results) | traces+scenarios present | scorecard rows | missing field ⇒ structured error, not default |
| scan(artifact) | artifact exists | pass/fail | any raw/secret heuristic ⇒ fail closed |

### 5.5 Safety Properties (the invariants tests must encode)

- **No real side effect**: for every trace, `executed == true` implies the action was a declared-benign dry-run; an unsafe-marked action MUST have `executed == false` AND `blocked_at != null`.
- **No lost unsafe attempt**: a blocked unsafe action MUST still appear with `attempted == true` (it must never disappear from evidence).
- **No invalid scenario accepted**: a scenario missing a required field, carrying an extra field, or using an unknown enum value MUST be rejected (non-zero exit).
- **No overclaim**: every generated report MUST carry `certification_claim == false` and contain zero certification-language terms; no L3/live evidence is produced by this runbook.
- **Raw-free**: no generated artifact contains a raw attack payload, secret, or PII — only synthetic placeholders, ids, and aggregate counts.

### 5.6 Liveness / Progress Assumptions
- Every validator/harness/reporter run terminates within the per-script 60s hard cap (no unbounded loops/retries; `max_turns` bounds the harness).

### 5.7 Simplifications

| Simplification | Why It Still Catches Relevant Bugs |
|---|---|
| Mock tools instead of live agents | The behavioural distinction (attempted vs executed, blocked-at-boundary) is representable deterministically; live execution is explicitly out of scope (L3 deferred). |
| Synthetic placeholder payloads | Raw-free hygiene is itself under test; placeholders exercise the parser-divergence logic without real danger. |

### 5.8 Kani proof obligations
`N/A — Python target, no Rust kernels.` (Formal verification here is property/contract tests in §11, not Kani or TLA+. The invariants in §5.5 are the contract-test obligations.)

---

## 5A. Measurement Contract

**Reframed per founder directive (2026-06-19): the user IS the assessing engineer.** The persona is the **engineer responsible for the AI agent being assessed** (see §5C). They run this benchmark — a **CLI + scripts**, not a hosted product — to learn, reproducibly and raw-free, which agent-control layer each scenario exercises and whether an unsafe action was *attempted-but-blocked* vs *executed*. Product-grade telemetry/hosted-behavioural-event instrumentation stays out of scope (the external scorecard *product* remains the `/slo-ideate` route), but **"did the engineer get an actionable result?" is a first-class, measured success signal**: every front-to-end run either emits a complete, parseable, raw-free evidence report (exit 0) or **fails closed with a named reason** — never a silent, partial, or ambiguous result. That signal is asserted by the §5C front-to-end outcome test and by each milestone's stage-level front-to-end outcome test.

---

## 5B. Secure Value and Security Contract

**Required** — this runbook is **security-relevant** and value-bearing for the assessing engineer: it models AI-agent red-team flows, simulates dangerous tools (shell/email/memory/registry), produces artifacts intended for a public/upstream boundary and CI/CD, and gives the engineer actionable front-to-end evidence. Therefore §5A, §5B, and §5C all apply.

### Value Wedge

| Field | Value |
|---|---|
| Value hypothesis | A benchmark maintainer can see, reproducibly and raw-free, which agent-control layer a scenario exercises and whether an unsafe action was attempted vs executed — replacing prose claims with replayable evidence. |
| Smallest valuable wedge | M1+M2: a frozen scenario schema + validator and a deterministic mock harness that distinguishes attempted vs executed. Everything else (reporter, packaging) compounds value but the wedge proves the core. |
| User-visible proof of value | `bash run-smoke.sh` reproduces: 24 scenarios validated across all six trap classes; ≥5 mock traces with ≥4 unsafe attempts blocked-but-recorded; an evidence-level report with `certification_claim:false`. |
| Security-visible proof of safety | The hygiene gate (M5) + invariants (§5.5) prove no real side effect, no raw payload/secret in any artifact, and no certification overclaim. |
| What would make this wedge too small to matter? | If the schema cannot represent ≥4 of the six trap classes without ad-hoc fields, or if mock traces cannot separate attempted from executed — both are explicit kill criteria from the Experiment Book §3. |

### Security Definition of Ready (Operator Readiness)

| Prerequisite | Owner | Needed by | Validation (executable proof) | Status |
|---|---|---|---|---|
| Python 3.12 available | agent | M1 | `python --version` shows 3.12.x | ready |
| Seed evidence readable (s1..s8) | agent | M1 | `git show origin/slo/agt-redteam-agent-traps-opencre:experiments/.../s1-schema/scenario.schema.json` succeeds | ready |
| No live providers/credentials configured | human/agent | M2 | grep finds no provider keys; harness has no network import | ready (fail-closed by design) |
| Raw-free corpus discipline understood | agent | M5 | hygiene-gate test exists and fails on a planted synthetic secret | needed by M5 |

`safe_to_continue_without_blockers: true`

### Threat Model Summary

> Seeded from the Experiment Book §6 Security Invariants and §10 threat-model starter rows (no separate `/slo-architect` model exists yet; M5 may promote these rows into `docs/slo/design/agt-redteam-threat-model.md` if upstreaming proceeds).

| Area | Summary |
|---|---|
| Assets | The corpus' raw-free reputation; the benchmark's honesty (no-overclaim); CI integrity |
| Actors | Benchmark maintainer (trusted); contributor of new scenarios (semi-trusted); downstream reader of reports (trusted-consumer) |
| Trust boundaries | scenario file → validator; generated artifact → public/upstream boundary; mock tool → (never) real OS/network |
| Entry points | scenario JSON files; new fixtures; CI job input |
| Abuse cases | `tm-agtrt-abuse-1`: raw attack payload smuggled into a scenario/report leaks to a public artifact. `tm-agtrt-abuse-2`: a fixture/extractor hides agent-visible content, producing false comfort. `tm-agtrt-abuse-3`: a mock tool is made to perform a real side effect (subprocess/network/file-outside-scratch). `tm-agtrt-abuse-4`: a report asserts or implies official OWASP/OpenCRE certification. `tm-agtrt-abuse-5`: an unsafe attempt blocked at the boundary disappears from evidence (false negative). `tm-agtrt-abuse-6`: a hard-benign input is auto-classified unsafe (false positive). `tm-agtrt-abuse-7` (M6): a live run leaks a real secret/raw payload into an L3 trace. `tm-agtrt-abuse-8` (M8): a crafted scenario/control field renders as executable HTML in the shareable scorecard — stored XSS (CWE-79). `tm-agtrt-abuse-9` (M6): a live agent escapes the OS sandbox / reaches cloud-metadata `169.254.169.254` to exfiltrate host credentials — sandbox-escape + SSRF (CWE-918). |
| Required controls | Closed enums (§4.5); raw-free hygiene gate (M5); stdlib-only import gate; `certification_claim:false` literal; attempted-recorded-even-if-blocked invariant; hard-benign must-not-block cases. |
| Residual risks | Mock evidence is L2 only — it never proves live-agent safety (owner: runbook; review-by: before any L3/Goose ticket starts). Heuristic raw-free scan can miss novel encodings (owner: M5; mitigated by synthetic-only discipline + review). |

### Security Test Plan

| Test | Required? | Command/tool | Evidence path | Waiver if not applicable |
|---|---|---|---|---|
| SAST | partial | `python -m py_compile` + custom invariant tests | M1–M5 Evidence Logs | full SAST tool not in repo; py_compile + contract tests substitute |
| SCA/dependency audit | yes (as no-dep proof) | stdlib-only grep gate (`test_no_third_party_imports`) | M1 Evidence Log | — |
| Secrets scan | yes | hygiene-gate raw-free scan (M5) + `git diff --check` | M5 Evidence Log | — |
| IaC scan | not_applicable | — | — | no IaC in this runbook |
| Container/image scan | not_applicable | — | — | no container built |
| DAST/API security | not_applicable | — | — | no network service; harness is in-process mock |
| Authn/authz negative tests | not_applicable | — | — | no auth surface |
| Abuse-case tests | yes | BDD abuse rows `tm-agtrt-abuse-1..6` across M1/M2/M4/M5 | per-milestone BDD | — |
| Privacy/telemetry tests | not_applicable | — | — | no PII, no telemetry collected |
| Fuzz/property/formal tests | yes | property/contract tests encoding §5.5 invariants | M1/M2/M4 Evidence Logs | — |

### Detected Work Ledger

> Every finding during execution gets exactly one disposition (`fix_now | file_github_issue | operator_action | upstream_feedback | accepted_risk`). `/slo-execute` refuses to mark a milestone done while any row is undisposed.

| ID | Finding | Severity | Disposition | Owner | Evidence/link | Due |
|---|---|---:|---|---|---|---|
| DW-001 | Content-injection fixture pack deferred from this runbook (curated `promote_to_ticket`) | low | file_github_issue | win/mac | M5 files `/slo-ticket-plan` issue | M5 |
| DW-002 | Goose live adapter — **now BUILT as M6** (founder pulled it in; sandboxed L3) | low | built_in_milestone | win/mac | M6 (was: file issue) | M6 |
| DW-003 | OpenCRE relation quality — **now BUILT as M7** (founder pulled it in; relation-quality validator) | med | built_in_milestone | win/mac | M7 (was: file issue) | M7 |
| DW-004 | `python3` vs `python` + shell-glob portability (Windows) — Win audit Finding 2 | low | fix_now | win | split: M1 validator CLI takes explicit path args (no bare glob) — DONE in M1; M3 `run-smoke.sh` uses a portable invocation (`python`, Git-Bash-documented) | M1 (validator) + M3 (smoke script) |

---

## 5C. Outcome Validation Contract

**Required — founder directive 2026-06-19.** This benchmark HAS a user and a real front-to-end outcome; the earlier "N/A — not value-bearing" was wrong and is corrected here. The interface is a **CLI + scripts (not a web app)**, but the capability must be exercised in **FULL, front-to-end**, and validated **as an outcome at every milestone** — not by component/unit checks alone.

### Persona

**Agent Assessment Engineer** — the engineer responsible for the AI agent (or the agent-control policy set) that is being assessed. They need honest, reproducible, raw-free evidence about how their agent behaves against the six Agent-Traps classes: which control layer each scenario exercises, and whether an unsafe action was *attempted but blocked* vs *executed*. They are not a UI end-user; their "front end" is the benchmark **CLI and the report files it emits**, run locally or in their CI.

### Front-to-End Outcomes (the capability, end to end)

| # | Engineer-facing outcome | Front-to-end path (input → … → result) | Interface | Lands |
|---|---|---|---|---|
| oc-1 | "Validate my scenario set" | scenario JSON → `validate_scenarios.py <paths>` → pass/fail + per-trap-class coverage (JSON + exit code) | CLI | M1 |
| oc-2 | "See attempted-vs-executed for my scenarios" | validated scenarios → harness runner → per-tool JSONL traces with `attempted`/`executed`/`blocked_at` | CLI | M2 |
| oc-3 | "Run the whole assessment in one command" | scenarios → `run-smoke.sh` (validate → harness → report) → single pass/fail + summaries | script | M3 |
| oc-4 | "Get an evidence-level scorecard I can act on" | traces + controls → reporter → JSON+Markdown scorecard by trap-class / AGT-AC control / evidence-level, `certification_claim:false` | CLI | M4 |
| oc-5 | "Trust it's safe to share / upstream" | all artifacts → raw-free hygiene gate → pass (no raw payload/secret/PII) + `PROMOTION.md` boundary | CLI | M5 |
| oc-6 | "Assess my real Goose agent safely" | engineer-configured Goose agent → hermetic sandbox live run → `L3_live` traces with containment proof | CLI + sandbox | M6 |
| oc-7 | "Trust the control relation quality" | AGT-AC controls + OpenCRE snapshot → relation validator → verified/candidate relation report with provenance | CLI + research artifact | M7 |
| oc-8 | "Share an honest scorecard" | run results → static Markdown/HTML scorecard → offline, raw-free, no-certification stakeholder artifact | CLI + generated file | M8 |

### Critical User Journeys (assessing engineer)

- **cuj-1 Assess**: the engineer points the benchmark at a scenario set and gets back a complete, raw-free evidence report — which layer each scenario hit, and whether unsafe actions were blocked — in one command, with zero real side effect.
- **cuj-2 Extend**: the engineer adds a new scenario; the validator accepts it, or rejects it with a clear, actionable reason, without hand-editing internals.
- **cuj-3 Regression-watch**: a weakening in the agent's controls surfaces as a changed scorecard / a newly-`executed` unsafe action — the benchmark *surfaces* the regression instead of hiding it.
- **cuj-4 Share**: the engineer exports a presentable static scorecard and shares it; it renders offline, raw-free, and prominently states `certification_claim:false`.

### How the outcome is validated

- **Top-level front-to-end test** — `run-smoke.sh` run exactly as the engineer would run it (the real validate→harness→report→hygiene chain, not mocks of itself), asserting observable engineer-facing outputs: trap-class coverage counts, ≥4 blocked-but-recorded unsafe attempts, `certification_claim:false`, and a raw-free pass.
- **Stage-level front-to-end outcome test in EVERY milestone (M1..M8)** — each milestone adds/extends a `#### Front-to-End Outcome Test (stage-level)` that drives the engineer-facing capability available *so far* from its CLI/script entrypoint, end-to-end, and asserts the engineer-visible result.
- **Outcome-first DoD (founder law #1634)**: a milestone is DONE only when its stage-level front-to-end outcome works for the assessing engineer **AND** all prior stages' front-to-end outcomes still pass — never on unit/component green alone.

---

## 6. Global Execution Rules

The standard v4 global rules (§6.1–§6.12 of the canonical template) apply verbatim. Milestone-salient emphasis:

- **6.1 Stay in scope** — only touch files in the current milestone's allow-list. `experiments/agt-redteam-agent-traps-opencre/**` is **read-only seed** (mac-owned); never edit it.
- **6.2 Tests define the contract** — write the invariant/contract tests (§5.5) before the production module they constrain; confirm they fail first.
- **6.4 Bounded resources** — declare `max_turns`/`timeout_seconds` for the harness; no unbounded retry/loop.
- **6.5 Static analysis must pass** — `py_compile` + `git diff --check` + stdlib-only grep gate every milestone.
- **6.7 No placeholders in production paths** — but note: *synthetic placeholder payloads in scenario/fixture DATA are the intended design*, not forbidden "production placeholders". The forbidden kind is TODO/stub logic in the validator/harness/reporter code.
- **6.11 .gitignore + artifact cleanup** — generated `__pycache__`, scratch report outputs, and any non-committed run artifacts must be gitignored and cleaned; tests write only to tempdirs.

---

## 7. Global Entry Rules (Pre-Milestone Protocol)

Standard v4 entry protocol (§7 of the canonical template). Per-milestone: read the previous lessons file; run the baseline test command and confirm green before starting; set the tracker row to `in_progress`; write BDD/contract test stubs first; restate constraints (goal, allowed files, forbidden changes, resource bounds, invariants, static gates, DoD) before coding.

---

## 8. Global Exit Rules (Post-Milestone Protocol)

Standard v4 exit protocol (§8 of the canonical template). Per-milestone: run `py_compile` + `git diff --check` + full unittest discovery + `run-smoke.sh`; verify §5.5 invariants are encoded and tested; confirm `git status` clean (no stray artifacts); review `.gitignore`; update README/ARCHITECTURE per §18; write `docs/slo/lessons/agtrt-m<N>.md` and `docs/slo/completion/agtrt-m<N>.md`; update the tracker to `done`.

---

## 9. Background Context

### Current State
The Innovation-Sandbox experiment `EXP-agt-redteam-agent-traps-opencre` is **complete** (exit `promote_to_runbook`), published on `origin/slo/agt-redteam-agent-traps-opencre`. Its scratch evidence under `experiments/agt-redteam-agent-traps-opencre/s1..s8` proved (Windows + Mac audited): a 24-scenario schema across all six Agent-Traps classes (s1), a metadata-only gap map (s2), 6/6 divergent content fixtures (s3), deterministic mock tools with attempted/executed traces (s4), a 15-control AGT-AC/OpenCRE-compatible mapping pack (s5), an evidence-level scorecard with `certification_claim:false` (s6), a Goose dry-run adapter contract (s7), and a promotion split (s8). The repo convention for such work is **stdlib-only Python under `meta/harness/**` with `test_*.py` unittest files + `validate_*.py` scripts wired into `.github/workflows/readiness.yml` and gated by `git diff --check`.**

### Problem
The spike evidence is scratch — it is not a durable, importable, CI-gated benchmark, and it must never be promoted to production as-is (Experiment hard rule). The gaps:

1. **No durable schema/validator package**: s1 lives in scratch; the scenario contract is not frozen or importable as `benchmarks/agent-redteam/schema/`.
2. **No reusable harness**: s4's mock tools are a one-file demo, not a runner with a frozen trace schema and encoded safety invariants.
3. **No reproducible smoke/CI path**: the demo commands exist only in §9 of the Book; nothing fails CI if the benchmark regresses.
4. **No control-linked reporting that is CI-safe and non-overclaiming**: s6 is a demo, not a guarded reporter with a `certification_claim:false` invariant test.
5. **No raw-free hygiene gate or upstream PR boundary**: s8 is a plan; the deferred routes (fixtures/Goose/OpenCRE/scorecard-idea) are not filed.

### Target Architecture
See §3. End state: `benchmarks/agent-redteam/{schema,scenarios,harness,controls,reporters}` + `run-smoke.sh` + one appended CI job + raw-free hygiene gate + `PROMOTION.md` with deferred routes filed as GH issues. Live Goose, OpenCRE API, and any upstream PR remain **out**.

### Key Design Principles
1. **Evidence levels, not badges** — L0..L3 ladder; this runbook produces L1 (static) and L2 (mock) only; `certification_claim` is a hard `false`.
2. **Attempted ≠ executed** — the load-bearing behavioural distinction; blocked unsafe attempts must remain visible.
3. **Raw-free by construction** — synthetic placeholders, ids, and aggregate counts only; a gate enforces it.
4. **Map controls before standards** — scenarios link to `AGT-AC-` controls; OpenCRE relations stay `candidate`-honest and are research, not contribution.
5. **Stdlib-only, repo-native** — mirror `meta/harness/**`; zero new deps; `git diff --check`-clean.

### What to Keep
- `experiments/agt-redteam-agent-traps-opencre/**` (read-only seed), `corpus/**`, `meta/harness/**`, `tools/**`, `rust/**`, existing `readiness.yml` steps.

### What to Change
- **NEW** `benchmarks/agent-redteam/**` (all milestones).
- **APPEND-ONLY** one job to `.github/workflows/readiness.yml` (M3).
- **NEW** `docs/slo/lessons/agtrt-m*.md`, `docs/slo/completion/agtrt-m*.md`, and `docs/RUNBOOK-...` tracker updates.

### Global Red Lines
No unrelated refactors; no new dependencies; no schema migrations; no edits to mac-owned experiment scratch; no live agents/providers/network; no certification claims; no raw payloads/secrets in any artifact; no unbounded growth; no silent gap-swallowing. **M6 carve-out (founder-approved):** M6 introduces a sandboxed live Goose agent + one isolated, security/license-reviewed dependency under `adapters/goose/` ONLY — egress-denied, no prod credentials, opt-in (`--live`); the DEFAULT path (M1–M5) stays stdlib-only / no-live / no-network. Every other red line (raw-free, no certification, no edits to experiment scratch, bounded resources) holds across **all** milestones including M6–M8.

---

## 10. Carry-forward from prior retros

No `/slo-retro` issues exist for prefix `agtrt` yet (this is the first runbook off the experiment). `/slo-execute` Step 1.5 falls back to a live `gh issue list --label retro-derived` query. The Detected Work Ledger (§5B) carries the four known deferrals (DW-001..004).

| Issue | Title | Suggested lane | Suggested milestone | Status |
|---|---|---|---|---|
| (none yet) | — | — | — | — |

---

## 11. BDD and Runtime Validation Rules

Standard v4 rules (§11 of the canonical template). Project specifics:

- **Test framework**: stdlib `unittest`; files named `test_*.py` co-located under `benchmarks/agent-redteam/**`, discovered by `python -m unittest discover`.
- **Required categories per milestone**: happy path, invalid input, empty/first-run, dependency/partial failure, resource-bound, **invariant/assertion violation** (§5.5), backward-compat (schema additive-only), and **abuse case** (`tm-agtrt-abuse-N`) for every new surface (new file write, subprocess potential, public artifact boundary).
- **Cleanup**: tests write only to `tempfile.TemporaryDirectory`; `git status` must be clean after the suite.
- **E2E/runtime**: `run-smoke.sh` is the cross-component runtime validation — it must exercise the real validate→harness→report chain (not mocks of itself) and assert observable outputs (counts, `certification_claim:false`).

---

## 12. Dependency, Migration, and Refactor Policy

- **12.1 Dependencies**: none. Any exception requires a full Contract Block entry (name, version, why-stdlib-insufficient, security/license/cost rationale, tests, rollback). The stdlib-only grep gate enforces this.
- **12.2 Migration**: schema field sets freeze at M1 close; changes after are **additive-only** with a compatibility test proving old scenarios still validate.
- **12.3 Refactor budget**: declared per milestone below.

---

## 13. Evidence Log Template

(Standard v4 Evidence Log table — copied into each milestone's Evidence Log section.)

---

## 14. Self-Review Gate

(Standard v4 Self-Review questions — answered before each milestone is marked done. The benchmark-salient additions: "Did any generated artifact gain a raw payload/secret?" must be **no**; "Does every report still carry `certification_claim:false`?" must be **yes"; "Does the stdlib-only gate still pass?" must be **yes**.)

---

## 15. Lessons-Learned File Template

Path: `docs/slo/lessons/agtrt-m<N>.md` — standard v4 lessons template.

---

## 16. Completion Summary Template

Path: `docs/slo/completion/agtrt-m<N>.md` — standard v4 completion template.

---

## 17. Milestone Plan

### Milestone 1 — `Scenario schema + validator (productionize s1)`

**Goal**: A frozen, importable `benchmarks/agent-redteam/schema/` (scenario + result JSON Schemas + `validate_scenarios.py`) and 24 seed scenarios that validate across all six Agent-Traps classes — replacing the s1 scratch with a durable, CI-ready contract.

**Context**: s1 (`experiments/.../s1-schema/`) proved the schema with 24 examples (4 per class) and a stdlib validator returning `{"validated":24,"trap_counts":{...}}` exit 0. This milestone re-homes that under `benchmarks/agent-redteam/` with the field set frozen, an explicit JSON Schema, and invariant tests — and fixes the Win-audit portability note (`python3`/glob).

**Carmack-style reliability goal**: Make invalid states unrepresentable (closed `trap_class` enum, required-field set, `AGT-AC-` control format) + static-analysis gate (stdlib-only).

**Important design rule**: The scenario field set is the public contract; freeze it here. Validation is fail-closed: unknown enum / missing / extra field ⇒ non-zero exit. No network, no new deps.

**Refactor budget**: `No refactor permitted beyond direct implementation` (greenfield under new path).

#### Contract Block

| Field | Value |
|---|---|
| Inputs | scenario JSON files (paths as CLI args) |
| Outputs | JSON coverage summary on stdout; exit code; `result.schema.json` for downstream |
| Interfaces touched | NEW `schema/scenario.schema.json`, `schema/result.schema.json`, `schema/validate_scenarios.py`, `scenarios/*.json` |
| Files allowed to change | `benchmarks/agent-redteam/schema/**`, `benchmarks/agent-redteam/scenarios/**`, `benchmarks/agent-redteam/tests/test_schema.py`, `.gitignore` |
| Files to read before changing anything | `experiments/.../s1-schema/scenario.schema.json`, `experiments/.../s1-schema/validate_scenarios.py`, `experiments/.../s1-schema/examples/*.json` (read-only seed); `meta/harness/open-source-readiness/test_*.py` (test-style exemplar) |
| New files allowed | yes — under the allow-list paths above |
| New dependencies allowed | `none` |
| Migration allowed | `no` |
| Compatibility commitments | None pre-exist; this milestone *establishes* the frozen contract for all later milestones |
| Resource bounds introduced/changed | Validator reads ≤ a few hundred files; per-run < 60s hard cap; O(files) memory |
| Invariants/assertions required | unknown `trap_class` rejected; every scenario has ≥1 `AGT-AC-` control + ≥1 success_condition; `views=={human_visible,agent_visible}`; missing/extra field rejected; all six classes represented across the 24 seeds |
| Debugger / inspection expectation | `python -m json.tool` over each scenario; `python -m pdb` if a validation result is surprising |
| Static analysis gates | `python -m py_compile schema/validate_scenarios.py`; `git diff --check`; stdlib-only grep gate |
| Exemplar code to copy | `experiments/.../s1-schema/validate_scenarios.py` (logic shape); `meta/harness/**/test_*.py` (unittest style) |
| Anti-exemplar code not to copy | The s3 first-draft extractor over-stripping bug (don't silently drop a channel and report success); do not copy the `python3`+bare-glob invocation (Win-audit Finding 2 — use `python` + explicit arg list) |
| Refactoring discipline | `N/A — no refactoring performed (greenfield)` |
| AI tolerance contract | `N/A — no AI component` (the validator is deterministic; scenarios are static data) |
| Forbidden shortcuts | no TODO/stub validator logic; no swallowing a coverage gap into exit 0; no new deps; no edits to s1 scratch |
| Data classification | `Internal` (synthetic scenarios only) |
| Proactive controls in play | OWASP `C4 Address Security from the Start` (closed enums, fail-closed validation), `C3 Validate all Input` (strict field/enum validation) |
| Abuse acceptance scenarios | `tm-agtrt-abuse-1` (raw payload in a scenario) and `tm-agtrt-abuse-4` (certification term in a scenario) — see BDD rows |
| Measurement deliverables | actionable-result signal (§5A): the validator emits a complete coverage report OR fails closed with a named reason — never a silent/partial result |
| Outcome Validation deliverables | **oc-1** front-to-end (validate a scenario set → coverage report); see the stage-level F2E Outcome Test below |
| Critical user journeys | **cuj-2 Extend** (engineer adds/rejects a scenario with an actionable reason) |

#### Out of Scope / Must Not Do
- No harness, reporter, fixtures, adapters, or CI changes (later milestones).
- No editing the s1 scratch; copy/re-implement under the new path only.
- No content-injection fixtures (deferred ticket DW-001).

#### Files Allowed To Change

| File | Planned Change |
|---|---|
| `benchmarks/agent-redteam/schema/scenario.schema.json` | NEW: frozen JSON Schema (required fields, closed enums) |
| `benchmarks/agent-redteam/schema/result.schema.json` | NEW: result contract for downstream harness/reporter |
| `benchmarks/agent-redteam/schema/validate_scenarios.py` | NEW: stdlib validator, fail-closed, JSON stdout |
| `benchmarks/agent-redteam/scenarios/*.json` | NEW: 24 seed scenarios (4 per class), raw-free |
| `benchmarks/agent-redteam/tests/test_schema.py` | NEW: invariant + abuse-case tests |
| `.gitignore` | Add `benchmarks/agent-redteam/**/__pycache__/` |

#### Step-by-Step
1. Write `tests/test_schema.py` first (invariants §5.5 + abuse rows); confirm they fail (no schema yet).
2. Author `scenario.schema.json` + `result.schema.json` with closed enums and required-field sets.
3. Re-implement `validate_scenarios.py` (stdlib) reading explicit path args; emit JSON coverage; exit non-zero on any gap/violation.
4. Port the 24 seed scenarios (raw-free; synthetic placeholders only).
5. Make all tests pass; run `py_compile` + `git diff --check` + stdlib-only grep.
6. Run validator over the 24 seeds; confirm `validated=24`, six classes × 4.
7. Self-Review Gate; write lessons + completion; update tracker.

#### BDD Acceptance Scenarios

**Feature: scenario validation**

| Scenario | Category | Given | When | Then |
|---|---|---|---|---|
| 24 seeds validate | happy path | 24 raw-free seed scenarios | run validator | exit 0; `validated=24`; each of 6 classes count=4 |
| unknown trap class | invalid input | a scenario with `trap_class:"Nonsense"` | run validator | exit ≠0; stderr names the file + reason |
| missing required field | invalid input | a scenario without `success_conditions` | run validator | exit ≠0 with reason |
| extra field | invalid input | a scenario with an undeclared field | run validator | exit ≠0 (closed field set) |
| no scenarios passed | empty state | no path args | run validator | exit 2 + usage message |
| unreadable file | dependency failure | a path that doesn't parse as JSON | run validator | structured error, non-zero exit, no traceback swallow |
| class coverage gap | assertion violation | 23 scenarios missing one class | run validator | exit ≠0 naming the uncovered class |
| raw payload smuggled | abuse `tm-agtrt-abuse-1` | a scenario whose field contains a raw-payload heuristic hit | run the raw-free check in test | the test flags it (proves the gate concept; full gate is M5) |
| certification term | abuse `tm-agtrt-abuse-4` | a scenario containing "OWASP-certified" | run the no-overclaim check | flagged by test |

#### Outcome Scenarios
- **oc-1 (M1 delivers it)**: the assessing engineer runs the validator over a folder of scenario JSON and gets, front-to-end, a pass/fail + per-trap-class coverage report — the first usable engineer-facing capability.

#### Critical User Journeys
- **cuj-2 Extend (stage-level)**: the engineer adds a scenario and it is accepted, or rejected with a clear, actionable reason (named file + reason) — no internals hand-edited.

#### Front-to-End Outcome Test (stage-level)
Drive **oc-1** exactly as the assessing engineer would, from the CLI entrypoint, end-to-end:

| F2E step | Engineer action | Engineer-visible outcome (assert) |
|---|---|---|
| valid set | `python benchmarks/agent-redteam/schema/validate_scenarios.py benchmarks/agent-redteam/scenarios/*.json` | exit 0; stdout JSON `validated=24`; each of 6 trap classes count=4 |
| bad scenario | run the validator on a malformed / unknown-enum scenario | non-zero exit; stderr names the file + the actionable reason |
| empty invocation | run the validator with no path args | exit 2 + usage message (never a silent pass) |

**Outcome gate (founder-first):** M1 is not `done` until this stage-level F2E outcome passes — i.e. the engineer can validate a scenario set front-to-end and get an actionable result.

#### Core Capability Regression Matrix

| Capability | Must still pass | Evidence path | Resolution |
|---|---|---|---|
| Existing readiness CI | yes | `.github/workflows/readiness.yml` unchanged this milestone | not_applicable (no CI change in M1) |
| Experiment scratch intact | yes | `git status` shows no edits under `experiments/**` | pass (verified at exit) |
| Repo builds (Rust/tools) | yes | unaffected (no edits outside `benchmarks/`) | not_applicable |

#### Regression Tests
- `git diff --check` clean. `git status` shows changes confined to `benchmarks/agent-redteam/**` + `.gitignore`.
- Existing `meta/harness/**` tests still pass (untouched).

#### Compatibility Checklist
- [ ] No edits under `experiments/agt-redteam-agent-traps-opencre/**`.
- [ ] No edits to `readiness.yml`.
- [ ] Validator CLI contract (JSON stdout + exit code) documented for downstream.

#### E2E Runtime Validation
**File**: `benchmarks/agent-redteam/tests/test_schema.py` (acts as runtime validator for M1)

| E2E Test | What It Proves | Pass Criteria |
|---|---|---|
| `test_24_seeds_validate` | full validate path runs at runtime | exit 0, counts correct |
| `test_failclosed_on_unknown_enum` | fail-closed works at runtime | non-zero exit, reason emitted |

#### Smoke Tests
- [ ] `python benchmarks/agent-redteam/schema/validate_scenarios.py benchmarks/agent-redteam/scenarios/*.json` → `validated=24`
- [ ] `python -m unittest benchmarks.agent-redteam.tests.test_schema` (or discovery) green
- [ ] `python -m py_compile` clean; `git diff --check` clean
- [ ] `git status` shows no untracked artifacts (no `__pycache__`)

#### Evidence Log

| Step | Command / Check | Expected Result | Actual Result | Pass/Fail | Notes |
|---|---|---|---|---|---|
| Baseline | `python -m unittest discover -s benchmarks/agent-redteam -p "test_*.py"` | no tests yet / green | | | |
| BDD created | `tests/test_schema.py` | fail (no schema) | | | |
| Implementation | schema + validator + 24 seeds | contract satisfied | | | |
| Static | `py_compile` + `git diff --check` + stdlib grep | clean | | | |
| Full tests | unittest discovery | green | | | |
| Smoke | validator over seeds | `validated=24` | | | |
| Invariant | unknown-enum rejected | non-zero exit | | | |
| Cleanup | `git status` | clean | | | |

#### Definition of Done
Standard v4 DoD (all BDD pass; static gates clean; stdlib-only proven; 24 seeds validate across six classes; invariants §5.5 encoded+tested; `git status` clean; lessons + completion written; tracker updated) **AND the stage-level Front-to-End Outcome Test (oc-1) passes** — the engineer can validate a scenario set front-to-end (outcome-first gate, not optional).

#### Post-Flight
- **ARCHITECTURE.md**: add `benchmarks/agent-redteam/` schema component.
- **README.md**: add a one-line pointer to the benchmark (validator command).

---

### Milestone 2 — `Mock behavioural harness + trace schema (productionize s4)`

**Goal**: A deterministic `benchmarks/agent-redteam/harness/` (runner + mock shell/email/memory/mcp_registry/audit + A2A tools + frozen `tool_trace.schema.json`) that emits attempted/executed traces and **provably never performs a real side effect** — productionizing s4 with the §5.5 safety invariants encoded.

**Context**: s4 proved 5 mock traces / 4 blocked unsafe attempts as a one-file demo. This milestone makes it an importable runner with a frozen trace schema, bounded turns/timeout, and tests that assert the no-real-side-effect and attempt-still-recorded invariants.

**Carmack-style reliability goal**: Bounded resources (`max_turns`, `timeout_seconds`) + assertions for the load-bearing behavioural invariants.

**Important design rule**: A mock tool must be structurally incapable of a real side effect — no `subprocess`, no `socket`/network import, no file write outside a passed-in tempdir. An unsafe-marked action is always `executed:false` + `blocked_at` set, and always `attempted:true`.

**Refactor budget**: `No refactor permitted beyond direct implementation`.

#### Contract Block

| Field | Value |
|---|---|
| Inputs | a scenario (validated by M1) + tool invocation intents |
| Outputs | JSONL traces conforming to `tool_trace.schema.json`; a result conforming to `result.schema.json` |
| Interfaces touched | NEW `harness/runner.py`, `harness/mock_tools.py`, `harness/tool_trace.schema.json`, `tests/test_harness.py` |
| Files allowed to change | `benchmarks/agent-redteam/harness/**`, `benchmarks/agent-redteam/tests/test_harness.py`, `.gitignore` |
| Files to read before changing anything | `experiments/.../s4-mock-tools/mock_tools.py`, `.../tool_trace.schema.json`, `.../sample_trace.jsonl` (read-only seed); M1 `result.schema.json` |
| New files allowed | yes (allow-list paths) |
| New dependencies allowed | `none` |
| Migration allowed | `no` |
| Compatibility commitments | Consumes M1 schema unchanged; trace schema is additive-only after this milestone |
| Resource bounds introduced/changed | `max_turns` (default 4, hard cap configurable), `timeout_seconds` (default 30); traces bounded by tools×scenarios; no retries |
| Invariants/assertions required | `executed==False` ⇒ `blocked_at!=None`; unsafe action ⇒ `executed==False` and `attempted==True`; `audit_event_present==True` for every trace; no `subprocess`/`socket` import present (asserted by a source-scan test) |
| Debugger / inspection expectation | `python -m json.tool` over emitted JSONL; pdb on any trace that violates an invariant |
| Static analysis gates | `py_compile` + `git diff --check` + stdlib-only grep + **no-dangerous-import grep** (`subprocess`, `socket`, `requests`, `urllib.request`) |
| Exemplar code to copy | `experiments/.../s4-mock-tools/mock_tools.py` (trace fields, block-at-boundary logic) |
| Anti-exemplar code not to copy | Any pattern that performs a real OS/network action; any tool that drops a blocked attempt from the trace |
| Refactoring discipline | `N/A — greenfield` |
| AI tolerance contract | `N/A — no AI component` (mock tools are deterministic simulators; no live model/agent is invoked — that is the explicit out-of-scope, L3-deferred boundary) |
| Forbidden shortcuts | no real subprocess/network "just for realism"; no swallowing a blocked attempt; no unbounded turn loop |
| Data classification | `Internal` |
| Proactive controls in play | OWASP `C5 Validate All Inputs / Handle Errors` and `C9 Implement Security Logging and Monitoring` (every trace has an audit event); `C4 Address Security from the Start` (structurally side-effect-free) |
| Abuse acceptance scenarios | `tm-agtrt-abuse-3` (mock made to perform a real effect) and `tm-agtrt-abuse-5` (blocked unsafe attempt disappears) — BDD rows |
| Measurement deliverables | actionable-result signal (§5A): the harness emits complete attempted/executed traces or fails closed with a named reason |
| Outcome Validation deliverables | **oc-2** front-to-end (validated scenario → traces showing attempted/executed/blocked); stage-level F2E Outcome Test below |
| Critical user journeys | **cuj-1 Assess (partial)** + **cuj-3 Regression-watch** (a newly-`executed` unsafe action stays visible, not hidden) |

#### Out of Scope / Must Not Do
- No live Goose/provider/network (DW-002 ticket). No content fixtures (DW-001). No reporter (M4). No CI change (M3).

#### Files Allowed To Change

| File | Planned Change |
|---|---|
| `benchmarks/agent-redteam/harness/tool_trace.schema.json` | NEW: frozen trace contract |
| `benchmarks/agent-redteam/harness/mock_tools.py` | NEW: deterministic, side-effect-free mock tools |
| `benchmarks/agent-redteam/harness/runner.py` | NEW: bounded runner emitting traces + result |
| `benchmarks/agent-redteam/tests/test_harness.py` | NEW: invariant + abuse tests incl. source-scan |
| `.gitignore` | ensure trace/scratch outputs ignored |

#### Step-by-Step
1. Write `tests/test_harness.py` first (invariants §5.5 + `tm-agtrt-abuse-3/5` + dangerous-import source scan); confirm fail.
2. Author `tool_trace.schema.json`.
3. Implement `mock_tools.py` (5 tools + A2A) — no subprocess/socket; block-at-boundary records attempt.
4. Implement `runner.py` with `max_turns`/`timeout_seconds` bounds.
5. Make tests pass; run static gates incl. dangerous-import grep.
6. Generate sample traces to tempdir; `json.tool` inspect; confirm ≥5 traces / ≥4 blocked.
7. Self-Review; lessons + completion; tracker.

#### BDD Acceptance Scenarios

**Feature: mock behavioural harness**

| Scenario | Category | Given | When | Then |
|---|---|---|---|---|
| traces emitted | happy path | 5 mock tools | run harness | ≥5 traces; ≥4 unsafe `executed:false,blocked_at` set |
| benign dry-run allowed | happy path | a declared-benign action | run | `executed:true`, no `blocked_at` |
| unknown tool | invalid input | invoke an unregistered tool | run | structured error, non-zero, no crash |
| empty scenario set | empty state | no scenarios | run | exits cleanly with zero traces, documented |
| turn cap hit | resource bound | `max_turns=1` with multi-turn intent | run | stops at cap; bound recorded; no unbounded loop |
| no real side effect | abuse `tm-agtrt-abuse-3` | source scan of harness | run test | zero `subprocess`/`socket`/network imports |
| blocked attempt visible | abuse `tm-agtrt-abuse-5` | an unsafe action that is blocked | inspect trace | `attempted:true` present (not dropped) |
| trace schema conformance | compatibility | every emitted trace | validate vs `tool_trace.schema.json` | all conform |

#### Outcome Scenarios / Critical User Journeys
- **oc-2 (M2 delivers it)**: the assessing engineer runs the harness over a validated scenario and gets, front-to-end, per-tool traces showing whether each unsafe action was *attempted but blocked* vs *executed* — with no real side effect.
- **cuj-3 Regression-watch (stage-level)**: an unsafe action that becomes `executed` (a weakened control) shows up in the trace instead of disappearing.

#### Front-to-End Outcome Test (stage-level)
Drive **oc-2** as the assessing engineer would, from the runner entrypoint, end-to-end:

| F2E step | Engineer action | Engineer-visible outcome (assert) |
|---|---|---|
| run harness | `python benchmarks/agent-redteam/harness/runner.py` over a validated scenario | ≥5 JSONL traces; ≥4 unsafe actions `executed:false` with `blocked_at` set AND `attempted:true` (blocked attempts stay visible) |
| benign action | run a declared-benign action | `executed:true`, no `blocked_at` |
| safety proof | inspect harness source / traces | zero real side effects (no subprocess/socket) — the engineer's result is trustworthy |

**Outcome gate:** M2 is not `done` until oc-2 passes front-to-end — the engineer can see attempted-vs-executed for a scenario.

#### Core Capability Regression Matrix

| Capability | Must still pass | Evidence path | Resolution |
|---|---|---|---|
| M1 validator still green | yes | unittest discovery | pass |
| Experiment scratch intact | yes | `git status` | pass |
| No network during tests | yes | dangerous-import scan + no socket | pass |

#### Regression Tests
- M1 `test_schema.py` still green. `git diff --check` clean. Changes confined to `harness/**` + tests + `.gitignore`.

#### Compatibility Checklist
- [ ] M1 schemas unchanged. [ ] Trace schema documented as additive-only. [ ] No edits to `experiments/**`.

#### E2E Runtime Validation
**File**: `benchmarks/agent-redteam/tests/test_harness.py`

| E2E Test | What It Proves | Pass Criteria |
|---|---|---|
| `test_traces_attempted_executed` | attempted/executed distinction at runtime | ≥4 blocked-but-recorded |
| `test_no_dangerous_imports` | structural side-effect-freedom | scan finds none |

#### Smoke Tests
- [ ] `python benchmarks/agent-redteam/harness/runner.py` → ≥5 traces / ≥4 blocked
- [ ] dangerous-import grep returns empty
- [ ] unittest discovery green; `git status` clean

#### Evidence Log
| Step | Command / Check | Expected | Actual | Pass/Fail | Notes |
|---|---|---|---|---|---|
| Baseline | unittest discovery (M1 green) | green | | | |
| BDD created | `test_harness.py` | fail | | | |
| Implementation | harness + trace schema | contract satisfied | | | |
| Static + import scan | `py_compile` + grep | clean / empty | | | |
| Full tests | unittest | green | | | |
| Smoke | runner | ≥5/≥4 | | | |
| Cleanup | `git status` | clean | | | |

#### Definition of Done
Standard v4 DoD; invariants §5.5 (no-real-side-effect, attempt-recorded, audit-present) encoded + tested; bounds encoded; stdlib-only + no-dangerous-import proven; lessons + completion; tracker; **AND the stage-level Front-to-End Outcome Test (oc-2) passes** — the engineer can see attempted-vs-executed front-to-end (outcome-first gate).

#### Post-Flight
- **ARCHITECTURE.md**: add harness + trace schema. **README.md**: add harness command.

---

### Milestone 3 — `Agent-Traps deterministic smoke suite + CI integration`

**Goal**: `benchmarks/agent-redteam/run-smoke.sh` chains validate → harness → (placeholder reporter check) deterministically, and one **append-only** job in `.github/workflows/readiness.yml` runs it — so a regression fails CI.

**Context**: The demo path exists only in EXPERIMENT.md §9. This milestone makes it an executable, CI-gated smoke that proves the M1+M2 chain reproducibly (and fixes the Win-audit `python3`/glob portability via a portable invocation documented for Git-Bash + native).

**Carmack-style reliability goal**: Compatibility + evidence — CI is the automated guardrail that the benchmark still works.

**Important design rule**: The CI job is **append-only**; it must not modify or reorder existing `readiness.yml` steps. The smoke script is the single reproducible entrypoint and must fail on the first non-zero step.

**Refactor budget**: `Minimal local refactor permitted in listed files only` (only to make M1/M2 entrypoints script-invokable, e.g. a `__main__` guard — behavior-preserving).

#### Contract Block

| Field | Value |
|---|---|
| Inputs | M1 scenarios + M2 harness |
| Outputs | smoke exit code; CI job status |
| Interfaces touched | NEW `run-smoke.sh`; APPEND one job to `.github/workflows/readiness.yml` |
| Files allowed to change | `benchmarks/agent-redteam/run-smoke.sh`, `.github/workflows/readiness.yml` (append-only), `benchmarks/agent-redteam/tests/test_smoke.py`, optional `__main__` guards in M1/M2 entrypoints |
| Files to read before changing anything | `.github/workflows/readiness.yml` (full), `corpus/round4/run-smoke.sh` (script-style exemplar), M1+M2 entrypoints |
| New files allowed | `run-smoke.sh`, `tests/test_smoke.py` |
| New dependencies allowed | `none` |
| Migration allowed | `no` |
| Compatibility commitments | All existing `readiness.yml` jobs unchanged and still pass |
| Resource bounds introduced/changed | smoke ≤ 60s/script; CI job time-bounded |
| Invariants/assertions required | smoke fails on first non-zero step; existing CI steps untouched (diff shows only an appended job) |
| Debugger / inspection expectation | run smoke locally under `bash -x` if a step fails |
| Static analysis gates | `bash -n run-smoke.sh`; `python -m py_compile`; `git diff --check`; YAML lints via existing CI |
| Exemplar code to copy | `corpus/round4/run-smoke.sh`; the existing `readiness.yml` job shape |
| Anti-exemplar code not to copy | Any change that reorders/edits existing readiness steps; bare `python3 .../*.json` glob (use a portable, explicit invocation) |
| Refactoring discipline | cite `skills/slo-plan/references/refactoring-discipline.md` — only behavior-preserving `__main__` guards, with M1/M2 tests proving unchanged behavior before+after |
| AI tolerance contract | `N/A — no AI component` |
| Forbidden shortcuts | no editing existing CI steps; no `|| true` masking a failing step |
| Data classification | `Internal` |
| Proactive controls in play | OWASP `C9 Security Logging and Monitoring` (CI is the monitoring guardrail) |
| Abuse acceptance scenarios | `N/A — no new runtime surface introduced` (CI runs the same in-process, side-effect-free benchmark; the new "surface" is a CI job, covered by the append-only invariant test) |
| Measurement deliverables | actionable-result signal (§5A): one-command run prints validate+harness summaries or fails fast with the named failing step |
| Outcome Validation deliverables | **oc-3** front-to-end (scenarios → `run-smoke.sh` → single pass/fail) — the integrated front-to-end milestone; stage-level F2E Outcome Test below |
| Critical user journeys | **cuj-1 Assess** (engineer runs the whole assessment in one command) |

#### Out of Scope / Must Not Do
- No reporter logic (M4). No new CI for unrelated areas. No reordering existing `readiness.yml`.

#### Files Allowed To Change

| File | Planned Change |
|---|---|
| `benchmarks/agent-redteam/run-smoke.sh` | NEW: portable validate→harness chain, fail-fast |
| `.github/workflows/readiness.yml` | APPEND one `agt-redteam-smoke` job only |
| `benchmarks/agent-redteam/tests/test_smoke.py` | NEW: asserts smoke exit semantics + append-only diff guard |
| M1/M2 entrypoints | OPTIONAL: add `if __name__=="__main__"` guards (behavior-preserving) |

#### Step-by-Step
1. Write `tests/test_smoke.py` (fail-fast semantics; existing-CI-unchanged guard); confirm fail.
2. Author `run-smoke.sh` (portable: explicit file args, `python` with `python3` fallback note; `set -euo pipefail`).
3. Append the CI job (copy existing job shape; setup-python 3.12; run smoke).
4. Add `__main__` guards if needed; re-run M1/M2 tests to prove unchanged behavior.
5. `bash -n`, `py_compile`, `git diff --check`; confirm `readiness.yml` diff = one added job.
6. Run smoke locally; confirm green and fail-fast on an injected bad step.
7. Self-Review; lessons + completion; tracker.

#### BDD Acceptance Scenarios

**Feature: reproducible smoke + CI**

| Scenario | Category | Given | When | Then |
|---|---|---|---|---|
| smoke green | happy path | M1+M2 healthy | `bash run-smoke.sh` | exit 0; prints validate + harness summaries |
| fail-fast | dependency failure | a step returns non-zero | run smoke | smoke stops, non-zero exit, names failing step |
| empty/first run | empty state | fresh checkout | run smoke | works without pre-generated artifacts (generates to tempdir) |
| CI append-only | compatibility | `readiness.yml` diff | inspect | exactly one job added; existing steps byte-identical |
| portability | invalid input | run under Git-Bash on Windows | run smoke | `python` resolves; no bare-glob dependency |

#### Outcome Scenarios / Critical User Journeys
- **oc-3 (M3 delivers it — the integrated front-to-end)**: the assessing engineer runs the WHOLE assessment in one command (`run-smoke.sh`: validate → harness → report-check) and gets a single pass/fail plus validate+harness summaries — and CI runs the same chain so a regression is caught automatically.
- **cuj-1 Assess (stage-level)**: one command, raw-free, no real side effect, fail-fast with a named step if anything breaks.

#### Front-to-End Outcome Test (stage-level)
Drive **oc-3** as the engineer would, from the single script entrypoint, end-to-end:

| F2E step | Engineer action | Engineer-visible outcome (assert) |
|---|---|---|
| one-command run | `bash benchmarks/agent-redteam/run-smoke.sh` | exit 0; prints validate summary (24 / 6 classes) + harness summary (≥5 traces / ≥4 blocked) |
| fail-fast | a step returns non-zero | smoke stops, non-zero exit, names the failing step (no false green) |
| CI parity | the appended `readiness.yml` job | same smoke runs in CI; existing jobs byte-identical (append-only) |

**Outcome gate:** M3 is not `done` until oc-3 passes front-to-end — the engineer can run the whole assessment in one command, locally and in CI.

#### Core Capability Regression Matrix

| Capability | Must still pass | Evidence path | Resolution |
|---|---|---|---|
| Existing readiness CI jobs | yes | `readiness.yml` diff = append-only | pass |
| M1 validator | yes | smoke step 1 | pass |
| M2 harness | yes | smoke step 2 | pass |

#### Regression Tests
- All existing `readiness.yml` jobs still defined and unchanged (diff guard test). M1+M2 unittests green.

#### Compatibility Checklist
- [ ] Existing CI steps unchanged. [ ] Smoke runs on Linux CI + Windows Git-Bash. [ ] No edits to `experiments/**`.

#### E2E Runtime Validation
**File**: `benchmarks/agent-redteam/tests/test_smoke.py`

| E2E Test | What It Proves | Pass Criteria |
|---|---|---|
| `test_smoke_green` | full chain runs at runtime | exit 0 |
| `test_smoke_failfast` | fail-fast semantics | injected failure ⇒ non-zero, named step |

#### Smoke Tests
- [ ] `bash benchmarks/agent-redteam/run-smoke.sh` green
- [ ] `readiness.yml` diff shows one appended job
- [ ] `git status` clean

#### Evidence Log
| Step | Command / Check | Expected | Actual | Pass/Fail | Notes |
|---|---|---|---|---|---|
| Baseline | M1+M2 unittests | green | | | |
| BDD created | `test_smoke.py` | fail | | | |
| Implementation | smoke + CI job | chain runs | | | |
| Static | `bash -n` + `py_compile` + `git diff --check` | clean | | | |
| CI diff guard | inspect `readiness.yml` | append-only | | | |
| Smoke | run-smoke.sh | exit 0 | | | |
| Cleanup | `git status` | clean | | | |

#### Definition of Done
Standard v4 DoD; smoke reproducible + fail-fast; CI append-only proven; portability fixed; M1/M2 behavior unchanged (refactor discipline evidence); lessons + completion; tracker; **AND the stage-level Front-to-End Outcome Test (oc-3) passes** — the engineer can run the whole assessment in one command front-to-end (outcome-first gate).

#### Post-Flight
- **ARCHITECTURE.md**: add smoke + CI guardrail. **README.md**: add `run-smoke.sh` as the reproducible entrypoint.

---

### Milestone 4 — `Control-linked evidence-level reporter (productionize s6)`

**Goal**: `benchmarks/agent-redteam/reporters/scorecard.py` aggregates harness results by trap class, `AGT-AC-` control (read-only from a committed s5-derived `controls/agt-ac.csv`), and evidence level (L0..L3), emitting JSON + Markdown with a hard `certification_claim:false` and zero certification language — productionizing s6 with a no-overclaim invariant test.

**Context**: s6 proved the evidence-level report concept. This milestone makes it a guarded reporter wired into the smoke chain, consuming M2 traces and the read-only control catalog, and proving (by test) it never overclaims.

**Carmack-style reliability goal**: Make invalid states unrepresentable (`certification_claim` is the literal `False`; evidence level is a closed enum) + no silent failure (missing field ⇒ structured error, not default).

**Important design rule**: The reporter never computes or implies certification; it produces evidence-level coverage only. A missing control mapping is reported as a `candidate`/`unmapped` gap, not silently dropped.

**Refactor budget**: `Minimal local refactor permitted in listed files only` (wire the reporter step into `run-smoke.sh`).

#### Contract Block

| Field | Value |
|---|---|
| Inputs | M2 result/traces + `controls/agt-ac.csv` (read-only) |
| Outputs | `scorecard_report.json` + `scorecard_report.md` (to a passed-in/tempdir path), `certification_claim:false` |
| Interfaces touched | NEW `reporters/scorecard.py`, `controls/agt-ac.csv`, `tests/test_reporter.py`; EDIT `run-smoke.sh` (add report step) |
| Files allowed to change | `benchmarks/agent-redteam/reporters/**`, `benchmarks/agent-redteam/controls/**`, `benchmarks/agent-redteam/tests/test_reporter.py`, `benchmarks/agent-redteam/run-smoke.sh` |
| Files to read before changing anything | `experiments/.../s6-scorecard/*` and `.../s5-opencre/agt-agentic-controls.csv` (read-only seed); M2 `result.schema.json` |
| New files allowed | reporter, control csv, test |
| New dependencies allowed | `none` (stdlib `csv`, `json`) |
| Migration allowed | `no` |
| Compatibility commitments | M1/M2 schemas + smoke chain unchanged except the appended report step |
| Resource bounds introduced/changed | report size O(results × controls), bounded; < 60s |
| Invariants/assertions required | `certification_claim is False` (literal); evidence_level ∈ {L0_declared,L1_static,L2_mock,L3_live} and no L3 produced here; no certification term in output; missing field ⇒ structured error |
| Debugger / inspection expectation | `python -m json.tool scorecard_report.json` |
| Static analysis gates | `py_compile` + `git diff --check` + stdlib-only grep + **no-certification-term grep** over generated samples |
| Exemplar code to copy | `experiments/.../s6-scorecard/*` (aggregation shape, `certification_claim:false`) |
| Anti-exemplar code not to copy | Badge-first / single-aggregate-score framing (composted in §8); any default that hides a missing mapping |
| Refactoring discipline | cite `skills/slo-plan/references/refactoring-discipline.md` — the only refactor is adding a report step to `run-smoke.sh`, behavior-preserving for prior steps (M3 smoke test must still pass) |
| AI tolerance contract | `N/A — no AI component` (reporter aggregates deterministic mock results; no model output) |
| Forbidden shortcuts | no certification language; no single mystery score; no silent default for a missing control |
| Data classification | `Internal` |
| Proactive controls in play | OWASP `C7 Enforce Encoding/Output` discipline (raw-free output), `C9 Logging/Monitoring` (evidence trail) |
| Abuse acceptance scenarios | `tm-agtrt-abuse-4` (report implies certification) and `tm-agtrt-abuse-6` (hard-benign auto-classified unsafe) — BDD rows |
| Measurement deliverables | actionable-result signal (§5A): the engineer gets a complete evidence-level scorecard (JSON+MD) or a structured error — never a silent default. (The external scorecard *product* is now built as **M8**, not routed out.) |
| Outcome Validation deliverables | **oc-4** front-to-end (full chain → evidence-level scorecard, `certification_claim:false`) — the headline engineer outcome; stage-level F2E Outcome Test below |
| Critical user journeys | **cuj-1 Assess** (engineer gets an actionable scorecard) + **cuj-3 Regression-watch** (scorecard change surfaces a control regression) |

#### Out of Scope / Must Not Do
- No OpenCRE relation *quality* work (that is `/slo-research`, DW-003 — consume control ids read-only only). No L3/live evidence. No badge/score.

#### Files Allowed To Change

| File | Planned Change |
|---|---|
| `benchmarks/agent-redteam/controls/agt-ac.csv` | NEW: read-only copy of the 15 AGT-AC control ids (raw-free) |
| `benchmarks/agent-redteam/reporters/scorecard.py` | NEW: evidence-level aggregator, cert=false |
| `benchmarks/agent-redteam/tests/test_reporter.py` | NEW: no-overclaim + hard-benign + missing-field tests |
| `benchmarks/agent-redteam/run-smoke.sh` | EDIT: append report step |

#### Step-by-Step
1. Write `tests/test_reporter.py` first (cert-false literal; no-cert-term scan; hard-benign must-not-block; missing-field error); confirm fail.
2. Commit `controls/agt-ac.csv` (read-only ids from s5, raw-free).
3. Implement `scorecard.py` aggregating by trap/control/evidence-level; `certification_claim=False`.
4. Append report step to `run-smoke.sh`; re-run M3 smoke test (unchanged prior steps).
5. Static gates incl. no-certification-term grep over generated sample.
6. Inspect `scorecard_report.json` via `json.tool`.
7. Self-Review; lessons + completion; tracker.

#### BDD Acceptance Scenarios

**Feature: evidence-level reporter**

| Scenario | Category | Given | When | Then |
|---|---|---|---|---|
| report generated | happy path | M2 results + controls | run reporter | JSON+MD with `certification_claim:false`, evidence levels per row |
| no certification term | abuse `tm-agtrt-abuse-4` | generated report | scan text | zero certification terms |
| hard-benign not failed | abuse `tm-agtrt-abuse-6` | a hard-benign result with no unsafe success condition | run reporter | not counted as a failure; reported as must-not-block pass |
| missing field | invalid input | a result missing `evidence_level` | run reporter | structured error, non-zero, no default |
| empty results | empty state | zero results | run reporter | empty-but-valid report, documented |
| unmapped control | partial failure | a result citing an id absent from csv | run reporter | reported as `candidate`/`unmapped` gap, not dropped |
| evidence-level closed enum | assertion violation | a result with `evidence_level:"L9"` | run reporter | rejected |

#### Outcome Scenarios / Critical User Journeys
- **oc-4 (M4 delivers it — the headline outcome)**: the assessing engineer runs the full chain and gets an evidence-level scorecard (JSON + Markdown) grading by trap class / AGT-AC control / evidence level (L0–L3), with a hard `certification_claim:false` — they can read which layer each scenario exercised and act on it.
- **cuj-3 Regression-watch (stage-level)**: a control regression shows up as a changed scorecard / a newly-`executed` row; a hard-benign input is NOT mis-flagged.

#### Front-to-End Outcome Test (stage-level)
Drive **oc-4** as the engineer would, end-to-end via the full chain:

| F2E step | Engineer action | Engineer-visible outcome (assert) |
|---|---|---|
| full run | `bash run-smoke.sh` (now ending in the reporter) | `scorecard_report.json` + `.md` produced; rows per trap-class / control / evidence-level; `certification_claim:false` |
| no overclaim | scan the generated report | zero certification-language terms (tm-agtrt-abuse-4) |
| no false positive | a hard-benign result | reported as must-not-block pass, not a failure (tm-agtrt-abuse-6) |
| missing field | a result missing `evidence_level` | structured error, non-zero — no silent default |

**Outcome gate:** M4 is not `done` until oc-4 passes front-to-end — the engineer gets an actionable, honest, raw-free scorecard.

#### Core Capability Regression Matrix

| Capability | Must still pass | Evidence path | Resolution |
|---|---|---|---|
| M3 smoke (prior steps) | yes | `test_smoke.py` still green | pass |
| M1/M2 suites | yes | unittest discovery | pass |
| Raw-free controls csv | yes | no-payload scan | pass |

#### Regression Tests
- M1/M2/M3 suites green. Smoke chain still fail-fast. Changes confined to allow-list.

#### Compatibility Checklist
- [ ] M1/M2 schemas unchanged. [ ] Smoke prior steps unchanged (only report step appended). [ ] No edits to `experiments/**`.

#### E2E Runtime Validation
**File**: `benchmarks/agent-redteam/tests/test_reporter.py`

| E2E Test | What It Proves | Pass Criteria |
|---|---|---|
| `test_certification_claim_false` | no-overclaim at runtime | literal `false` + zero cert terms |
| `test_hard_benign_not_failed` | false-positive guard | must-not-block result passes |

#### Smoke Tests
- [ ] `python benchmarks/agent-redteam/reporters/scorecard.py ...` → `certification_claim:false`
- [ ] no-certification-term grep over report empty
- [ ] full smoke green; `git status` clean

#### Evidence Log
| Step | Command / Check | Expected | Actual | Pass/Fail | Notes |
|---|---|---|---|---|---|
| Baseline | M1–M3 suites | green | | | |
| BDD created | `test_reporter.py` | fail | | | |
| Implementation | reporter + controls csv | cert=false | | | |
| Static + cert grep | `py_compile` + grep | clean / empty | | | |
| Full tests | unittest | green | | | |
| Smoke | full chain | exit 0 | | | |
| Cleanup | `git status` | clean | | | |

#### Definition of Done
Standard v4 DoD; `certification_claim:false` invariant + no-cert-term + hard-benign + missing-field encoded/tested; smoke chain extended without breaking prior steps; lessons + completion; tracker; **AND the stage-level Front-to-End Outcome Test (oc-4) passes** — the engineer gets an actionable evidence-level scorecard front-to-end (outcome-first gate).

#### Post-Flight
- **ARCHITECTURE.md**: add reporter + controls. **README.md**: add report command + "evidence levels, not certification" note.

---

### Milestone 5 — `Upstream-ready docs + raw-free hygiene gate + PR-boundary packaging (productionize s8)`

**Goal**: A raw-free hygiene gate (test + smoke step) over all generated/committed benchmark artifacts, a `benchmarks/agent-redteam/PROMOTION.md` PR-boundary doc (from s8), and the one remaining deferred route (DW-001 content-fixtures) filed as a GitHub issue — so the benchmark is upstream-ready without a monolithic PR and without leaking raw content. (DW-002 Goose and DW-003 OpenCRE are now **BUILT in M6/M7** per the founder pull-in; DW-004 portability is fixed across M1+M3 — none of these are filed out.)

**Context**: s8 proved a clean promotion split. This milestone makes the hygiene enforceable and files the deferred work, closing the runbook with the experiment's safety posture intact (raw-free, no certification, no monolithic upstream PR).

**Carmack-style reliability goal**: No silent failure — the hygiene gate fails closed on any raw-payload/secret heuristic hit; the Detected Work Ledger is fully disposed.

**Important design rule**: Nothing here opens an upstream PR or claims certification. The hygiene gate is the last line: any generated artifact containing a raw attack payload, secret, or PII heuristic hit fails the build. The gate scans **all committed AND generated artifacts under `benchmarks/agent-redteam/**` — explicitly including the committed `scenarios/*.json` and `controls/*.csv`, not only generated reports** (tm-agtrt-abuse-1 is a payload smuggled into a committed scenario, so the scan must cover scenario inputs).

**Refactor budget**: `Minimal local refactor permitted in listed files only` (add hygiene step to `run-smoke.sh`).

#### Contract Block

| Field | Value |
|---|---|
| Inputs | all committed/generated benchmark artifacts |
| Outputs | hygiene gate pass/fail; `PROMOTION.md`; filed GH issue for DW-001 (content-fixtures) only (DW-002/003 are built in M6/M7) |
| Interfaces touched | NEW `benchmarks/agent-redteam/hygiene/raw_free_scan.py`, `PROMOTION.md`, `tests/test_hygiene.py`; EDIT `run-smoke.sh` (add hygiene step) |
| Files allowed to change | `benchmarks/agent-redteam/hygiene/**`, `benchmarks/agent-redteam/PROMOTION.md`, `benchmarks/agent-redteam/tests/test_hygiene.py`, `benchmarks/agent-redteam/run-smoke.sh` |
| Files to read before changing anything | `experiments/.../s8-promotion/*` (read-only seed); all `benchmarks/agent-redteam/**` artifacts to scan |
| New files allowed | hygiene scanner, PROMOTION.md, test |
| New dependencies allowed | `none` (stdlib `re`) |
| Migration allowed | `no` |
| Compatibility commitments | Whole prior chain still green; hygiene step appended to smoke |
| Resource bounds introduced/changed | scan O(artifacts × patterns), bounded; < 60s |
| Invariants/assertions required | any raw-payload/secret/PII heuristic hit ⇒ fail closed; a planted synthetic secret is detected (anti-vacuity); Detected Work Ledger fully disposed |
| Debugger / inspection expectation | run scanner with `--verbose` to see which artifact/line tripped |
| Static analysis gates | `py_compile` + `git diff --check` + stdlib-only grep; hygiene gate itself |
| Exemplar code to copy | `meta/harness/round6-cascade/test_artifact_hygiene.py` (hygiene-test exemplar); `experiments/.../s8-promotion/*` (PR-boundary content) |
| Anti-exemplar code not to copy | Any scan that passes vacuously (must fail on a planted secret); any upstream-PR automation |
| Refactoring discipline | cite `skills/slo-plan/references/refactoring-discipline.md` — only appends a hygiene step to smoke; prior smoke steps behavior-preserved (M3/M4 smoke tests still pass) |
| AI tolerance contract | `N/A — no AI component` |
| Forbidden shortcuts | no opening an upstream PR; no certification claim; no vacuous scan; no leaving a DW row undisposed |
| Data classification | `Internal` (scans for would-be `Confidential`/raw leakage) |
| Proactive controls in play | OWASP `C8 Protect Data Everywhere` (raw-free/secret scan), `C9 Logging/Monitoring`, `C2 Leverage Security Frameworks` (reuse repo hygiene patterns) |
| Abuse acceptance scenarios | `tm-agtrt-abuse-1` (raw payload leaks to public artifact) and `tm-agtrt-abuse-2` (fixture hides agent-visible content → references the deferred fixtures ticket) — BDD rows |
| Measurement deliverables | actionable-result signal (§5A): the hygiene gate passes a clean tree or fails closed naming the artifact/line — the engineer knows it is safe to share |
| Outcome Validation deliverables | **oc-5** front-to-end (all artifacts → raw-free gate → shareable, packaged benchmark) — stage-level F2E Outcome Test below |
| Critical user journeys | **cuj-1 Assess** end-to-end, ending in a raw-free, shareable result |

#### Out of Scope / Must Not Do
- No upstream PR. No certification claim. No implementation of the deferred fixtures/Goose/OpenCRE work (only **file** them). No edits to `experiments/**`.

#### Files Allowed To Change

| File | Planned Change |
|---|---|
| `benchmarks/agent-redteam/hygiene/raw_free_scan.py` | NEW: fail-closed raw/secret/PII heuristic scan |
| `benchmarks/agent-redteam/tests/test_hygiene.py` | NEW: anti-vacuity (planted secret) + clean-pass tests |
| `benchmarks/agent-redteam/PROMOTION.md` | NEW: PR-boundary sequence + deferred routes + safety posture |
| `benchmarks/agent-redteam/run-smoke.sh` | EDIT: append hygiene step |

#### Step-by-Step
1. Write `tests/test_hygiene.py` first (planted-secret must fail; clean tree must pass); confirm fail.
2. Implement `raw_free_scan.py` (regex heuristics: secret-like, raw-payload markers, PII shapes), fail-closed.
3. Author `PROMOTION.md` from s8 (schema→harness→smoke→reporter sequence; deferred routes; "no monolithic PR, no certification").
4. Append hygiene step to `run-smoke.sh`; re-run M3/M4 smoke tests.
5. File GH issue: DW-001 (content-fixtures `/slo-ticket-plan`); link it in `PROMOTION.md`; mark the Detected Work Ledger disposed. (DW-002 Goose → built in M6, DW-003 OpenCRE → built in M7, DW-004 portability → fixed in M1+M3 — none filed out.)
6. Static gates; run full smoke (now ending in hygiene).
7. Self-Review; lessons + completion; tracker → all done.

#### BDD Acceptance Scenarios

**Feature: raw-free hygiene + packaging**

| Scenario | Category | Given | When | Then |
|---|---|---|---|---|
| clean tree passes | happy path | only synthetic raw-free artifacts | run hygiene gate | pass (exit 0) |
| planted secret fails | abuse `tm-agtrt-abuse-1` | a synthetic secret planted in an artifact | run gate | fail closed, names artifact/line |
| fixtures ticket filed | partial | content-fixtures deferral (DW-001) | run M5 | GH issue exists, linked in PROMOTION.md |
| no upstream PR | compatibility | M5 complete | inspect | no PR opened; only issues filed |
| anti-vacuity | assertion violation | gate run on a known-bad fixture | run test | the gate is proven to actually detect (not pass-vacuously) |
| hidden-channel note | abuse `tm-agtrt-abuse-2` | the deferred fixtures ticket | inspect | PROMOTION.md notes the extractor-hides-content risk for the fixtures ticket |

#### Outcome Scenarios / Critical User Journeys
- **oc-5 (M5 delivers it)**: the assessing engineer runs the full chain ending in the raw-free hygiene gate and gets a benchmark they can trust to share — no raw payload/secret/PII in any artifact — plus a `PROMOTION.md` boundary doc.
- **cuj-1 Assess (full, stage-level)**: the complete engineer journey — validate → harness → scorecard → hygiene — runs front-to-end, raw-free, in one command.

#### Front-to-End Outcome Test (stage-level)
Drive **oc-5** as the engineer would, end-to-end via the full chain ending in hygiene:

| F2E step | Engineer action | Engineer-visible outcome (assert) |
|---|---|---|
| clean tree | `bash run-smoke.sh` (now ending in the hygiene gate) | exit 0; full chain green; hygiene passes on synthetic raw-free artifacts |
| planted secret | run the gate over an artifact with a synthetic secret | fail closed; names the artifact/line (anti-vacuity; tm-agtrt-abuse-1) |
| shareable | inspect outputs | `PROMOTION.md` present; no upstream PR opened, no certification claim |

**Outcome gate:** M5 is not `done` until oc-5 passes front-to-end — the engineer has a raw-free, shareable, packaged benchmark.

#### Core Capability Regression Matrix

| Capability | Must still pass | Evidence path | Resolution |
|---|---|---|---|
| Full M1–M4 chain | yes | full smoke green | pass |
| All prior unittests | yes | unittest discovery | pass |
| Detected Work Ledger disposed | yes | §5B ledger + filed issues | pass |

#### Regression Tests
- Entire `benchmarks/agent-redteam/**` suite green; smoke chain (validate→harness→report→hygiene) fail-fast; existing repo CI unchanged.

#### Compatibility Checklist
- [ ] Prior smoke steps unchanged. [ ] No edits to `experiments/**`. [ ] No upstream PR / certification claim anywhere.

#### E2E Runtime Validation
**File**: `benchmarks/agent-redteam/tests/test_hygiene.py`

| E2E Test | What It Proves | Pass Criteria |
|---|---|---|
| `test_planted_secret_fails` | gate is non-vacuous | planted secret ⇒ non-zero |
| `test_clean_tree_passes` | gate doesn't false-positive on synthetic data | clean ⇒ exit 0 |

#### Smoke Tests
- [ ] `python benchmarks/agent-redteam/hygiene/raw_free_scan.py benchmarks/agent-redteam` → pass
- [ ] full `run-smoke.sh` green (ends in hygiene)
- [ ] GH issue DW-001 (content-fixtures) filed + linked; `git status` clean

#### Evidence Log
| Step | Command / Check | Expected | Actual | Pass/Fail | Notes |
|---|---|---|---|---|---|
| Baseline | M1–M4 suites + smoke | green | | | |
| BDD created | `test_hygiene.py` | fail | | | |
| Implementation | scanner + PROMOTION.md | gate works | | | |
| Anti-vacuity | planted secret | non-zero exit | | | |
| Static | `py_compile` + `git diff --check` | clean | | | |
| Full smoke | run-smoke.sh | exit 0 | | | |
| Issue filed | `gh issue list` | DW-001 present | | | |
| Cleanup | `git status` | clean | | | |

#### Definition of Done
Standard v4 DoD; hygiene gate fail-closed + anti-vacuity proven; `PROMOTION.md` complete; DW-001 (content-injection fixtures) filed as an issue and that ledger row disposed — **DW-002 (Goose) / DW-003 (OpenCRE) / the scorecard product are now BUILT in M6/M7/M8, not filed-out**; no premature upstream PR / no certification; full chain green; lessons + completion; tracker M1–M5 `done`; **AND the stage-level Front-to-End Outcome Test (oc-5) passes** — the engineer has a raw-free, shareable, packaged benchmark front-to-end (outcome-first gate). Before starting M6, refresh `/slo-critique` only if M1–M5 execution changed the M6–M8 assumptions.

#### Post-Flight
- **ARCHITECTURE.md**: add hygiene gate + packaging. **README.md**: add "raw-free, evidence-level, not certified" benchmark summary + PROMOTION.md pointer.

---

### Milestone 6 — `Live Goose adapter — real-agent (L3) assessment in a hermetic sandbox (productionize s7, was DW-002)`

**Goal**: `benchmarks/agent-redteam/adapters/goose/` — a CLI adapter that runs the scenarios through a **real Goose agent inside a hermetic, egress-blocked sandbox**, captures real tool-call traces into the SAME `tool_trace.schema.json`, and produces **`L3_live`** evidence — so the assessing engineer can assess **their actual agent**, not just the mock.

**Context**: s7 proved a Goose adapter *contract* only (pseudocode, `status=not_run`, `L0_declared`). This is the first crossing from L2_mock to L3_live, so it is **security-critical**: a live agent can attempt real side effects, and the sandbox is the load-bearing control.

**Carmack-style reliability goal**: Make invalid states unrepresentable (no prod credential reachable; network egress default-DENY) + bounded resources (turn/time/token caps) + no silent failure (a sandbox-escape or a missing trace fails closed — never a false-green L3).

**Important design rule**: The live agent runs **only** in a hermetic sandbox — no production credentials, egress default-deny (allowlist only the engineer-configured model endpoint), filesystem confined to a throwaway tempdir, hard turn/time/token kill-switch. The sandbox MUST be **OS-enforced** (a network namespace / container with egress default-deny at the firewall layer, a **scrubbed environment**, and **NO host filesystem mounts** — so host credential stores such as `~/.aws/credentials` or the OS keychain are not even visible), **not** a Python-level allowlist or an env-var scan — a real agent subprocess would bypass an in-process guard (sandbox escape / SSRF, incl. the cloud-metadata endpoint `169.254.169.254`). `evidence_level:L3_live` is tagged ONLY for actions actually executed under the sandbox; everything else stays L2/L0. Still raw-free (ids/aggregates, never raw payloads/real secrets). The default benchmark path (M1–M5) stays stdlib-only and mock/L2; the live deps live only under `adapters/goose/` and are never imported unless `--live` is passed.

**Refactor budget**: `Minimal local refactor permitted in listed files only` (add an opt-in `--live` branch to `run-smoke.sh`).

#### Contract Block

| Field | Value |
|---|---|
| Inputs | validated scenarios (M1) + an engineer-supplied agent/runtime config (model endpoint, sandbox profile) |
| Outputs | real tool-call traces (`tool_trace.schema.json`, `evidence_level:L3_live`) + an L3 scorecard via the M4 reporter |
| Interfaces touched | NEW `adapters/goose/adapter.py`, `adapters/goose/sandbox.py`, `tests/test_goose_adapter.py`; EDIT `run-smoke.sh` (opt-in `--live`, default OFF) |
| Files allowed to change | `benchmarks/agent-redteam/adapters/**`, `benchmarks/agent-redteam/tests/test_goose_adapter.py`, `benchmarks/agent-redteam/run-smoke.sh` |
| New dependencies allowed | **EXCEPTION (this milestone's purpose)**: the Goose runtime + provider SDK — pinned, security/license-reviewed in this Contract Block, **isolated to `adapters/goose/`** and never imported by the default path. Core benchmark stays stdlib-only. |
| Migration allowed | `no` |
| Resource bounds | `max_turns`, `timeout_seconds`, `max_tokens` hard caps with a kill-switch; one agent per run |
| Invariants/assertions required | **OS-level** egress default-deny proven (a real subprocess attempt to a non-allowlisted host — incl. metadata `169.254.169.254` — is blocked at the network layer, not just in-process); no host credential reachable (scrubbed env + no host fs mount; refuse to start otherwise); caps enforced; real effects confined to the sandbox tempdir; `L3_live` tag only on sandbox-executed actions; raw-free; **if the OS-enforced sandbox cannot be established (e.g. no netns/container privileges on the host or CI runner), the adapter REFUSES to run `--live` and exits with a named reason — it NEVER falls back to an in-process guard or emits L3 evidence** (resolves F-SEC-5; no false-trusted L3) |
| Static analysis gates | `py_compile` + `git diff --check` + **OS-layer sandbox-egress test** (real subprocess egress blocked) + **no-host-credential scan** + **stdlib-only gate scoped to the default path (excludes `adapters/goose/`)** + **dependency-audit gate for `adapters/goose/`** (pinned Goose dep + provider SDK, license + CVE checked) |
| Forbidden shortcuts | no run against production systems; no real-credential targets; no L3 tag on un-exercised actions; no live deps in the default path |
| Data classification | `Internal`; live traces scanned for would-be `Confidential` leakage |
| Abuse acceptance scenarios | `tm-agtrt-abuse-3` escalates to "LIVE agent performs a real effect OUTSIDE the sandbox" (must be impossible) + NEW `tm-agtrt-abuse-7` "a live run leaks a real secret/raw payload into an L3 trace" |
| Measurement deliverables | actionable-result signal (§5A): a live run yields honest L3 evidence or refuses to start / fails closed with a named reason |
| Outcome Validation deliverables | **oc-6** front-to-end (engineer's real agent → sandboxed live run → L3 evidence) |
| Critical user journeys | **cuj-1 Assess (L3 escalation)** — the engineer sees their real agent's behavior, safely |

#### Out of Scope / Must Not Do
- No assessment against production systems or real-credential targets. The default path stays mock/L2 — live is opt-in `--live` only. No upstream PR.

#### BDD Acceptance Scenarios

**Feature: live Goose adapter (sandboxed L3)**

| Scenario | Category | Given | When | Then |
|---|---|---|---|---|
| live L3 traces | happy path | a sandboxed Goose agent + a scenario | run `--live` | ≥1 real trace `evidence_level:L3_live`; attempted/executed/blocked_at from REAL behavior |
| egress blocked (OS layer) | abuse `tm-agtrt-abuse-3` (CWE-918) | the live agent's real subprocess attempts a non-allowlisted call (incl. metadata `169.254.169.254`) | run | call fails at the network layer; recorded `blocked_at`; no real external effect |
| no host creds reachable | abuse | a prod credential sits in `~/.aws/credentials` (not env) | run | sandbox runs scrubbed-env + no host fs mount → credential not visible; refuses to start if any host cred path is mountable |
| caps enforced | resource bound | a scenario that would loop | run | stops at turn/time/token cap; bounded; recorded |
| raw-free L3 | abuse `tm-agtrt-abuse-7` | a live trace | scan | no raw payload / real secret (ids + aggregates only) |
| default unchanged | compatibility | `run-smoke.sh` without `--live` | run | mock/L2 chain only; live deps not imported |

#### Outcome Scenarios
- **oc-6 (M6 delivers it)**: the assessing engineer points the benchmark at their REAL Goose agent (sandboxed) and gets honest `L3_live` evidence — which unsafe actions their actual agent attempted vs executed vs got blocked — replacing "the mock says" with "your agent did".

#### Critical User Journeys
- **cuj-1 Assess (L3 escalation)**: the engineer runs `--live` and safely (sandboxed, raw-free) sees their real agent's behavior.

#### Front-to-End Outcome Test (stage-level)

| F2E step | Engineer action | Engineer-visible outcome (assert) |
|---|---|---|
| live assess | `bash run-smoke.sh --live` (or `python adapters/goose/adapter.py --scenario ...`) with a sandbox profile | real `L3_live` traces produced; scorecard shows L3 rows for exercised scenarios |
| sandbox proof | trigger an egress / real-effect attempt | blocked + recorded; nothing escapes the sandbox (no external call, no write outside the tempdir) |
| opt-in safety | run without `--live` | mock/L2 path only; live deps not loaded |

**Outcome gate:** M6 is not `done` until oc-6 passes front-to-end — the engineer gets honest L3 evidence about THEIR agent, with the sandbox proven to contain real effects.

#### Core Capability Regression Matrix

| Capability | Must still pass | Evidence path | Resolution |
|---|---|---|---|
| Full M1–M5 mock chain | yes | `run-smoke.sh` (no `--live`) green | pass |
| Stdlib-only default path | yes | import-scan on the non-live path | pass |
| Raw-free across L2+L3 | yes | hygiene gate over all traces | pass |

#### Definition of Done
Standard v4 DoD; sandbox egress-deny + no-prod-cred + caps + raw-free-L3 invariants encoded/tested; live deps isolated + security/license-reviewed; default mock path unchanged; **AND the stage-level Front-to-End Outcome Test (oc-6) passes** — the engineer gets honest, safely-sandboxed L3 evidence about their agent (outcome-first gate). Lessons + completion; tracker.

#### Post-Flight
- **ARCHITECTURE.md**: add the live adapter + sandbox boundary. **README.md**: add the `--live` opt-in + its safety contract.

---

### Milestone 7 — `OpenCRE relation research + relation-quality validator (productionize DW-003)`

**Goal**: `benchmarks/agent-redteam/controls/opencre/` — verified AGT-AC ↔ OpenCRE relation mappings plus a `validate_relations.py` CLI that checks each relation claim against the OpenCRE source and **downgrades any unproven relation to `candidate`** — so the engineer's scorecard control mappings are honest (research-grade), not asserted.

**Context**: s5 produced a 15-control AGT-AC/OpenCRE-compatible mapping, but the relation *quality* (`exact|broad|narrow|related|candidate`) was never verified (DW-003). This milestone does that research and makes it machine-checkable.

**Carmack-style reliability goal**: Evidence over claims — a relation is only as strong as its verified backing; unverified ⇒ `candidate` (fail-honest).

**Important design rule**: No relation may claim a stronger status than its evidence supports; the validator is **fail-honest** (unknown ⇒ `candidate`). OpenCRE data is consumed **read-only** from a pinned snapshot committed under `controls/opencre/` with its **source URL + retrieval date + license recorded** (OpenCRE content is CC-licensed); no live OpenCRE API dependency in the default path.

**Refactor budget**: `Minimal local refactor permitted in listed files only` (the M4 reporter consumes the verified relations file).

#### Contract Block

| Field | Value |
|---|---|
| Inputs | AGT-AC control ids (M4 `controls/agt-ac.csv`) + a pinned OpenCRE relation snapshot |
| Outputs | a verified relations file (`controls/opencre/relations.verified.csv`) + a relation-quality report + a short research write-up (methodology) |
| Interfaces touched | NEW `controls/opencre/validate_relations.py`, `controls/opencre/relations.verified.csv`, `docs/slo/research/agtrt-opencre-relations.md`, `tests/test_relations.py` |
| Files allowed to change | `benchmarks/agent-redteam/controls/opencre/**`, `benchmarks/agent-redteam/tests/test_relations.py`, `docs/slo/research/agtrt-opencre-relations.md`, the M4 reporter (consume verified relations) |
| New dependencies allowed | `none` (stdlib `csv`/`json` over a committed snapshot; a live fetch is an optional, documented, non-default step) |
| Migration allowed | `no` |
| Invariants/assertions required | every relation carries a backing reference OR is `candidate`; no relation overclaims; report + write-up are raw-free; validator fail-honest on unknown |
| Static analysis gates | `py_compile` + `git diff --check` + stdlib-only grep + **no-endorsement-term grep** over the report |
| Forbidden shortcuts | no asserting `exact`/`broad` without backing; no implying official OpenCRE endorsement; no live API in the default path |
| Abuse acceptance scenarios | `tm-agtrt-abuse-4` extends — "a relation implies official OpenCRE endorsement" must be impossible (relations stay candidate-honest) |
| Measurement deliverables | actionable-result signal (§5A): the engineer can see exactly which mappings are evidence-backed vs `candidate` |
| Outcome Validation deliverables | **oc-7** front-to-end (control ids + OpenCRE snapshot → verified, honest relation mappings) |
| Critical user journeys | **cuj-3 (mapping honesty)** — no false authority in the control mappings |

#### Out of Scope / Must Not Do
- No upstream contribution to OpenCRE. No live API dependency in the default path. No relation strength beyond verified evidence.

#### BDD Acceptance Scenarios

**Feature: honest relation mapping**

| Scenario | Category | Given | When | Then |
|---|---|---|---|---|
| verified relations | happy path | AGT-AC ids + OpenCRE snapshot | run validator | each relation labeled with status + backing; report raw-free |
| downgrade unproven | assertion violation | a relation asserting `exact` without backing | run validator | downgraded to `candidate` / flagged (no false strength) |
| no endorsement | abuse `tm-agtrt-abuse-4` | the generated report | scan | zero "OpenCRE-certified/official" terms |
| unknown id | invalid input | a control id absent from the snapshot | run validator | reported as `candidate`/unmapped, not dropped |

#### Outcome Scenarios
- **oc-7 (M7 delivers it)**: the engineer's scorecard control mappings carry **honest, verified relation quality** — they can trust "scenario → AGT-AC-N relates (narrow) to OpenCRE-X" because it was checked; unverified relations are visibly `candidate`.

#### Critical User Journeys
- **cuj-3 (mapping honesty)**: the engineer runs the relation validator and sees exactly which mappings are evidence-backed vs `candidate` — no false authority.

#### Front-to-End Outcome Test (stage-level)

| F2E step | Engineer action | Engineer-visible outcome (assert) |
|---|---|---|
| relation check | `python benchmarks/agent-redteam/controls/opencre/validate_relations.py` | report lists each relation with status + backing; unverified ⇒ `candidate` |
| no overclaim | a relation asserting `exact` without backing | downgraded/flagged; zero endorsement terms |
| integrated | an M4 scorecard run consuming the verified relations | scorecard mappings are honest end-to-end |

**Outcome gate:** M7 is not `done` until oc-7 passes front-to-end — the engineer's control mappings are honest (verified, candidate-where-unproven).

#### Core Capability Regression Matrix

| Capability | Must still pass | Evidence path | Resolution |
|---|---|---|---|
| M4 scorecard still green | yes | `run-smoke.sh` green with verified relations | pass |
| Raw-free | yes | hygiene gate over report + write-up | pass |

#### Definition of Done
Standard v4 DoD; relation-honesty + no-endorsement-overclaim invariants encoded/tested; OpenCRE consumed read-only; research methodology write-up committed; **AND the stage-level Front-to-End Outcome Test (oc-7) passes** — the engineer's control mappings are honest front-to-end (outcome-first gate). Lessons + completion; tracker.

#### Post-Flight
- **ARCHITECTURE.md**: add the relation validator + verified mappings. **README.md**: add the "candidate-honest relations" note.

---

### Milestone 8 — `Shareable evidence scorecard product (productionize the /slo-ideate wedge)`

**Goal**: `benchmarks/agent-redteam/product/` — a **shareable, presentable scorecard** the assessing engineer can hand to stakeholders: a self-contained report (Markdown + static HTML, no server) generated from a run, rendering the evidence-level results honestly with a hard `certification_claim:false` disclaimer — the external-facing wedge built on M4's internal reporter.

**Context**: the evidence-level scorecard *product* was curated `promote_to_idea`; the founder has elected to build it. It is the engineer's "show my stakeholders" surface — it must present evidence without ever drifting into a certification/badge claim. This is the milestone where the §5A Measurement Contract is most real: success = a stakeholder reads it and correctly understands "evidence at level L_n, not a certification".

**Carmack-style reliability goal**: Make invalid states unrepresentable (no single "score"/badge; `certification_claim:false` literal rendered) + raw-free, self-contained output.

**Important design rule**: The product renders **evidence levels, never a single mystery score or a pass/cert badge**; every rendered artifact carries the no-certification disclaimer **rendered at the TOP of the report as a visually-distinct banner (not buried in a footer)** so a skimming stakeholder cannot misread it as a certification (tm-agtrt-abuse-4; resolves design finding F-DES-1); output is raw-free, self-contained (opens offline, no external calls, no telemetry).

**Refactor budget**: `No refactor permitted beyond direct implementation` (greenfield product layer over the M4 JSON).

#### Contract Block

| Field | Value |
|---|---|
| Inputs | the M4 `scorecard_report.json` |
| Outputs | `product/out/scorecard.html` (static, offline) + `product/out/scorecard.md` (shareable); `certification_claim:false` rendered prominently |
| Interfaces touched | NEW `product/render.py`, `product/templates/*`, `tests/test_product.py` |
| Files allowed to change | `benchmarks/agent-redteam/product/**`, `benchmarks/agent-redteam/tests/test_product.py` |
| New dependencies allowed | `none` (stdlib string templating; no JS framework, no server) |
| Migration allowed | `no` |
| Invariants/assertions required | rendered artifact carries `certification_claim:false` + zero certification-language; no single mystery score/badge; raw-free; self-contained (renders with no network); **every interpolated field (scenario id/name, control id) is HTML-escaped — no unescaped data in the rendered HTML (XSS via a crafted scenario name, CWE-79)** |
| Static analysis gates | `py_compile` + `git diff --check` + **no-certification-term grep over rendered output** + **no-external-reference grep** (no remote scripts/styles) |
| Forbidden shortcuts | no certification/badge framing; no single aggregate "score"; no external CDN/script; no telemetry |
| Data classification | `Internal`/shareable; output scanned raw-free before share |
| Abuse acceptance scenarios | `tm-agtrt-abuse-4` (the **product** implies certification) — the headline risk; the product MUST visibly disclaim |
| Measurement deliverables | **stakeholder-comprehension signal (§5A)**: the rendered scorecard makes "evidence level L_n, not certification" unambiguous (disclaimer present + no badge) |
| Outcome Validation deliverables | **oc-8** front-to-end (a run → a shareable, honest scorecard artifact) |
| Critical user journeys | **cuj-4 Share** — the engineer exports + shares a presentable scorecard |

#### Out of Scope / Must Not Do
- No hosted service / server / telemetry. No certification or single-score framing. No external CDN/script. No upstream PR.

#### BDD Acceptance Scenarios

**Feature: shareable scorecard product**

| Scenario | Category | Given | When | Then |
|---|---|---|---|---|
| product generated | happy path | an M4 scorecard JSON | `python product/render.py ...` | `scorecard.html` + `.md` produced; evidence-level rows rendered |
| no certification | abuse `tm-agtrt-abuse-4` | the rendered artifact | scan | `certification_claim:false` shown; zero cert terms; no badge/single-score |
| html injection (XSS) | abuse `tm-agtrt-abuse-4` / CWE-79 | a scenario name containing `<script>` | render | the field is HTML-escaped in `scorecard.html`; no executable injection |
| offline + raw-free | compatibility | open the HTML with no network | render | renders fully; no external call; no raw payload/secret |
| empty run | empty state | a scorecard with zero results | render | empty-but-valid, documented; still carries the disclaimer |

#### Outcome Scenarios
- **oc-8 (M8 delivers it)**: the engineer generates a shareable scorecard (HTML + MD) from a run and hands it to a stakeholder, who correctly reads it as **honest evidence-level results, not a certification** — the product wedge.

#### Critical User Journeys
- **cuj-4 Share**: the engineer exports a presentable scorecard and shares it; it renders offline, raw-free, with the no-certification disclaimer prominent.

#### Front-to-End Outcome Test (stage-level)

| F2E step | Engineer action | Engineer-visible outcome (assert) |
|---|---|---|
| generate | `python benchmarks/agent-redteam/product/render.py scorecard_report.json -o out/` | `out/scorecard.html` + `.md` produced; renders evidence-level rows |
| no overclaim | open/scan the rendered artifact | `certification_claim:false` shown; zero cert terms; no single badge/score (tm-agtrt-abuse-4) |
| offline + raw-free | open the HTML with no network | renders fully; no external calls; no raw payload/secret |

**Outcome gate:** M8 is not `done` until oc-8 passes front-to-end — the engineer has a shareable, honest, raw-free scorecard product.

#### Core Capability Regression Matrix

| Capability | Must still pass | Evidence path | Resolution |
|---|---|---|---|
| M4 internal reporter | yes | `run-smoke.sh` green | pass |
| Raw-free output | yes | hygiene gate over `product/out/**` | pass |
| No-overclaim across reporter + product | yes | no-cert-term grep on both | pass |

#### Definition of Done
Standard v4 DoD; no-certification + no-mystery-score + offline + raw-free invariants encoded/tested; §5A stakeholder-comprehension deliverable recorded; **AND the stage-level Front-to-End Outcome Test (oc-8) passes** — the engineer has a shareable, honest scorecard product front-to-end (outcome-first gate). Lessons + completion; **tracker all `done`** (M8 is the terminal milestone). Then run final `/slo-critique` before any external publication or upstream proposal.

#### Post-Flight
- **ARCHITECTURE.md**: add the product render layer. **README.md**: add the shareable-scorecard pointer + "evidence, not certification" disclaimer.

---

## 18. Documentation Update Table

| Milestone | ARCHITECTURE.md Update | README.md Update | .gitignore Update | Other Docs |
|---|---|---|---|---|
| 1 | schema component | validator command | `benchmarks/agent-redteam/**/__pycache__/` | lessons/completion agtrt-m1 |
| 2 | harness + trace schema | harness command | trace/scratch outputs | agtrt-m2 |
| 3 | smoke + CI guardrail | `run-smoke.sh` entrypoint | — | agtrt-m3 |
| 4 | reporter + controls | report command + evidence-levels note | report outputs | agtrt-m4 |
| 5 | hygiene gate + packaging | raw-free/evidence-level summary + PROMOTION.md | — | agtrt-m5; PROMOTION.md; GH issue DW-001 (fixtures) |
| 6 | live Goose adapter + sandbox boundary | `--live` opt-in + safety contract | `adapters/goose` scratch | agtrt-m6 |
| 7 | relation validator + verified mappings | candidate-honest relations note | — | agtrt-m7; research write-up |
| 8 | product render layer | shareable scorecard + "evidence, not certification" | `product/out` outputs | agtrt-m8 |

---

## 19. Optional Fast-Fail Review Prompt for Agents

> Restate the milestone goal, allowed files, forbidden changes, compatibility requirements, dependency/migration rules, required tests, runtime validation, resource bounds, invariants/assertions (§5.5), static-analysis gates, debugger expectation, and the exact Definition of Done. Then list the smallest implementation that satisfies the contract without widening scope, and confirm: no new deps, no edits to `experiments/**`, no live agents/network, no certification claim, no raw payload in any artifact.

---

## 20. Source Basis

v4 runbook produced by `/slo-plan` from `EXP-agt-redteam-agent-traps-opencre` (exit `promote_to_runbook`). Seed evidence: `experiments/agt-redteam-agent-traps-opencre/s1..s8` (audited PASS on Windows + Mac). Curation §8 dispositions are authoritative for what is in-runbook vs routed out. `/slo-critique` has run for the outcome-first reframe; M1 and M2 are merged. Next execution step: `/slo-execute M3` after a fresh AgentBus ownership check.
