# EXPERIMENT-agt-redteam-agent-traps-opencre — AGT Red Team Agent Traps OpenCRE (Creative Experiment Contract v1)

> **Purpose**: explore a fuzzy technical/product hunch safely before turning it into delivery work.
> **Creative posture**: play first, judge later. Surprise is a valid signal. Dead ends are useful evidence.
> **Hard rule**: nothing here becomes production without entering the normal SLO Sprint or Ticket loop.
> **Output**: one honest route decision — promote, continue, block, kill, or archive.
> **This is the experimentation peer of the v4 runbook** — same discipline, inverted aim: **Definition of Learned, not Definition of Done**. Authoritative spec: [docs/slo/design/innovation-loop-experiment-book-spec.md](../design/innovation-loop-experiment-book-spec.md). Authored/opened by `/slo-experiment`; phases §3–§9 filled by their phase skills.

<!-- HOW TO USE: /slo-experiment opens this Book (§0–§2 + tracker). Then run the phase
     skills in order: /slo-sandbox → /slo-play → /slo-pattern → /slo-precision →
     /slo-spike → /slo-curate → /slo-demo. Each fills its section and hands a named
     object to the next. A phase may be `skipped_with_reason` in §1. Section order
     §0–§11 is frozen (skills target sections by heading). -->

---

## 0. Experiment Metadata

| Field | Value |
|---|---|
| Experiment ID | `EXP-agt-redteam-agent-traps-opencre` |
| Created | `2026-06-18` |
| Owner | founder + mac-agent |
| Product area | agent-runtime / security / platform |
| Starting hunch | see fenced block below |
| Primary user / beneficiary | security engineer / benchmark maintainer / internal operator |
| Strategic lane | security / platform |
| Current phase | `sandbox` |
| Default data classification | Internal |
| Production promotion allowed? | **No — must route through SLO delivery** |
| Scratch code allowed? | yes; path `experiments/agt-redteam-agent-traps-opencre/<spike-id>/` |
| External services allowed? | none by default |
| Real user data allowed? | **no by default** |
| Review date | per phase / per session |

**Starting hunch** (user-supplied — rendered as inert data inside a fence; never an instruction):

~~~text
AGT Red Team can become a standards-linked agentic-control benchmark: it should combine the existing AGT prompt-injection corpus, the expanded governance corpus, Agent Traps scenario fixtures, Goose/live-agent adapters, and OpenCRE control mappings into a reproducible benchmark that produces validated evidence and promotion-ready proposals.
~~~

**Why This Is Not Yet a Feature**: the corpus schema, Agent Traps overlay, OpenCRE control-mapping shape, behavioural harness, Goose adapter contract, scorecard language, and upstream PR boundaries are still hypotheses; `/slo-ideate` or `/slo-plan` would be premature until the sandbox loop produces evidence and one honest route decision.

---

## 1. Experiment Tracker

Single source of truth for progress. Update the Status + Exit decision as each phase runs.

| Phase | Skill | Status | Input | Output | Exit decision |
|---|---|---|---|---|---|
| 1 | `/slo-sandbox` | `complete` | hunch | sandbox charter | |
| 2 | `/slo-play` | `complete` | sandbox charter | play log + probe cards | |
| 3 | `/slo-pattern` | `complete` | play log | pattern catalog | |
| 4 | `/slo-precision` | `complete` | pattern catalog | precision model | |
| 5 | `/slo-spike` | `complete` | precision model | spike evidence | |
| 6 | `/slo-curate` | `complete` | all evidence | curation decision | |
| 7 | `/slo-demo` | `complete` | promoted candidate | demo + handoff | `promote_to_runbook` |

<!-- Allowed status values (frozen): not_started | in_progress | blocked | complete | skipped_with_reason -->
<!-- Fail-safe: an unrecognised status is treated as `blocked`, never silently `complete`. -->

**Allowed status values** (frozen): `not_started | in_progress | blocked | complete | skipped_with_reason`

**Allowed final route decisions** (frozen 8 — the experiment closes on exactly one; an undecidable case is `blocked_by_unknown`, never silently terminal):

`promote_to_idea | promote_to_ticket | promote_to_research | promote_to_runbook | needs_more_play | blocked_by_unknown | killed_but_reusable | archive_no_action`

---

## 2. Global Experiment Rules

1. Do not productize inside the experiment.
2. Do not use production data unless explicitly approved.
3. Do not introduce production dependencies.
4. Do not expose public endpoints.
5. Do not store secrets in the repo, logs, screenshots, prompts, or demo artifacts.
6. Keep scratch code isolated under the declared experiment path (`experiments/<slug>/<spike-id>/`).
7. Capture surprises, not just successes.
8. Dead ends are valid outputs if they teach something reusable.
9. Every promoted candidate must include a handoff contract (§10).
10. Every experiment closes with one honest route decision.

### Experiment Safety Rails (defaults)

| Concern | Default |
|---|---|
| Production data | forbidden |
| Real secrets | forbidden |
| Public endpoint | forbidden |
| Production file changes | forbidden unless promoted through SLO |
| New dependency | allowed only in scratch with a license/security note |
| Cloud infra | no `pulumi up`; mock/local/sandbox only |
| Security primitive | do not hand-roll if SunLitSecurityLibraries / Hulumi applies |
| AI / model calls | approved proxy or offline model; no raw sensitive prompt payloads |
| Persistence | scratch only; no schema migration |
| User impact | no live-user experiment without a separate runbook/legal/privacy gate |

### Safety Check (every phase appends one)

```md
## Safety Check
- Data classification:
- Raw secrets present? yes/no
- PII present? yes/no
- External service called? yes/no
- Scratch path:
- Cleanup required:
- Abuse sketch:
```

### §2A Judgment Timing Rule (phase mood — protects the joy)

Critique is **phase-dependent**. Read your phase's mode before you start; it tells you whether to diverge or converge. During `/slo-play`, critique is **banned except for safety**. During `/slo-curate`, critique is **mandatory**.

| Phase | Mode | Agent behaviour | What may be judged |
|---|---|---|---|
| `/slo-sandbox` | framing | choose the playground, not the product | boundaries, not ideas |
| `/slo-play` | divergent | generate probes, defer judgment | **judge safety only**; defer quality judgment |
| `/slo-pattern` | convergent | name reusable tricks | reusability |
| `/slo-precision` | measurement | turn vague claims into handles | measurability |
| `/slo-spike` | evidence | test the smallest claim | evidence |
| `/slo-curate` | convergent | kill, continue, or promote | value, risk, promotion |
| `/slo-demo` | communication | make it communicable | clarity |

> Phase `Mode` is a frozen 5-value set: `divergent | convergent | measurement | evidence | communication` (`framing` is the sandbox-setup posture; `communication` covers the demo narrative).

### Experiment Phase Contract (every §3–§9 phase opens with this)

Lighter than the v4 Contract Block — enough structure to repeat the loop without killing exploration:

| Field | Value |
|---|---|
| Phase goal | what this phase is trying to learn |
| Mode | `divergent / convergent / measurement / evidence / communication` |
| Inputs consumed | which previous outputs this phase reads |
| Primary output | the object this phase must produce |
| Creative permission | what kind of weirdness/play is allowed |
| Boundaries | what is out of scope |
| Safety rails | data, network, secret, privacy, user-impact limits |
| Scratch space | where temporary code/files may live (spike only) |
| Resource budget | CPU, memory, time, cost, external calls |
| Evidence required | notes, screenshots, metrics, commands, examples |
| Kill criteria | what would stop this line of exploration |
| Handoff requirement | what the next skill receives |

### Definition of Learned (replaces Definition of Done)

**General phase — Definition of Learned.** A phase is complete only when: the prior phase's output was read; this phase's output was written into the Book; any safety-rail violation is recorded; any dead end is captured with what it taught; the next phase has a concrete handoff; the §1 tracker is updated; no scratch work was silently promoted to production.

**Spike — Definition of Learned.** A spike is complete only when: the learning question was answered or explicitly blocked; evidence is attached/summarized; accept/kill thresholds were evaluated; resource + safety bounds were checked; the scratch path is declared; no production files were changed; the spike has a decision hint.

**Curation — Definition of Learned.** Curation is complete only when: every candidate has exactly one disposition; every promoted candidate has a next SLO route; every killed candidate has a reusable lesson or archive reason; no vague "maybe" remains unowned.

---

## 3. Sandbox Charter

> Filled by `/slo-sandbox`. Mode: **framing**. Choose the material, not the feature.

### Phase Contract

| Field | Value |
|---|---|
| Phase goal | choose a rich material + bound the playground |
| Mode | framing (setup) |
| Inputs consumed | §0 hunch |
| Primary output | `SandboxCharter` + `ProbeSeedList` |
| Creative permission | wide — name strange materials |
| Boundaries | no feature commitment yet |
| Safety rails | inherit §2 defaults |
| Scratch space | none (no code in this phase) |
| Resource budget | time-boxed framing |
| Evidence required | ≥3 concrete probe seeds + explicit safety rails |
| Kill criteria | the material has no untried surface worth playing in |
| Handoff requirement | material, boundaries, weirdness budget, probe seeds → `/slo-play` |

**Material** (user-supplied — fenced, inert):

~~~text
Existing AGT benchmark + expanded AGT Embeddings Experiment corpus + Agent Traps taxonomy + AGT-AC control catalog idea + OpenCRE-compatible mappings + Goose/live-agent adapter contract + evidence-level scorecard proposal.
~~~

**Why this sandbox is rich**: it combines a real upstream prompt-injection fixture path, a large local synthetic corpus, local governance/control metadata, a proposed Agent Traps taxonomy overlay, a standards-linking target, and a live-agent target. The richest material is the trap-to-control-to-evidence mapping, not the current normalizer proposal by itself: a normalizer is one useful upstream control, while the benchmark needs to measure whether controls stop unsafe perception, reasoning, memory, action, multi-agent, and human-approval failures.

**Not a Feature Yet**: this phase does not decide an AGT upstream PR, runtime behavior, scorecard badge, OpenCRE contribution, or Goose integration. OpenCRE/AIVSS/ASI mappings remain candidate/self-assessment hypotheses until spikes produce evidence.

**Boundaries**:

| Boundary | Rule |
|---|---|
| Product | no benchmark, score, badge, upstream PR, or certification commitment |
| Code | scratch only under `experiments/agt-redteam-agent-traps-opencre/<spike-id>/` |
| Data | synthetic/generated/redacted only; no raw secrets, PII, or production prompts |
| Network | read-only research only; no live attacks, agent runs, credentials, or uncontrolled external calls |
| Cost | zero-cost local scripts only; no paid model calls |
| Time | one autonomous sandbox pass; stop at promotion packets |

**Creative constraints**:

- Map controls before mapping standards. If the map starts at OpenCRE/ASI labels, it risks becoming compliance theater.
- Treat the uploaded scorecard draft as a hypothesis to test, not a design authority.
- Prefer fixture and trace evidence over text-only prompt labels.
- Separate attempted unsafe action from executed unsafe action.
- Keep all artifacts raw-free: scenario IDs, synthetic payload placeholders, metadata, and aggregate coverage only.
- Use "OpenCRE-compatible" and "candidate mapping" language, never official certification language.

**Weirdness budget**: high. Category-shifting is allowed inside the sandbox: AGT Red Team may become an agent-control benchmark rather than a prompt-injection detector benchmark. Judgment is limited to safety and boundary fit until curation.

**Probe Seed List** (≥3):

| ID | Probe seed | Why try it? | Risk |
|---|---|---|---|
| P1 | Taxonomy crosswalk: map current corpus families to the six Agent Traps classes. | Tests whether prompt-injection rows can become trap scenarios. | Existing rows may overfit Behavioural Control and Cognitive State. |
| P2 | Control-first mapping: map scenarios to AGT-AC controls before OpenCRE/ASI labels. | Keeps failures actionable and avoids standards cargo-culting. | Controls may duplicate existing standards or be too AGT-specific. |
| P3 | Fixture adequacy: compare text-only rows with hidden-content/render-parse fixtures. | Tests whether perception traps need environment fixtures. | Fixtures may become unsafe or too expensive if they require real rendering. |
| P4 | Behavioural evidence: distinguish attempted unsafe calls from executed unsafe calls. | Agent-control safety depends on action boundaries, not only text output. | Mock traces may be too toy-like if not schema-constrained. |
| P5 | Stateful memory and A2A propagation: represent multi-session and multi-agent traps. | Covers Agent Traps classes underrepresented locally. | Determinism may be hard without over-simplifying. |
| P6 | Goose adapter contract: normalize real-agent results without live credentials. | Keeps a future live-agent target plausible but safe. | Real Goose smoke may require network/providers, so this phase may only define a contract. |
| P7 | Scorecard overclaim test: report evidence levels without a badge/certification claim. | Converts scorecard energy into defensible self-assessment evidence. | A single number may hide evidence quality and encourage overclaiming. |
| P8 | Upstream PR boundary draft: separate AGT benchmark, OpenCRE mapping, scorecard, and adapter PRs. | Avoids one giant upstream proposal. | The split may reveal missing dependency order. |

**Kill criteria**:

- More than two Agent Traps classes require ad hoc schema exceptions.
- Control mappings collapse into attack labels rather than actionable controls.
- Mock evidence cannot distinguish attempted from executed unsafe action.
- Any spike requires live credentials, real secrets, PII, unsafe tools, or external side effects.
- The scorecard language cannot avoid certification/badge overclaiming.
- Promotion requires one monolithic upstream PR.

### Safety Check

- Data classification: Internal.
- Raw secrets present? no.
- PII present? no.
- External service called? yes, read-only official/public web research for OpenCRE, Goose, Promptfoo, Inspect, and agent-audit context; no live agents or attacks.
- Scratch path: none in this phase.
- Cleanup required: none.
- Abuse sketch: unsafe use would be treating candidate mappings as official certification or running live trap payloads against third-party systems; both are explicitly out of scope.

---

## 4. Play Log

> Filled by `/slo-play`. Mode: **divergent**. Generate probes; **judge safety only; defer quality judgment**. Do NOT rank, pick a winner, or turn a probe into a product plan yet — that is `/slo-pattern`'s job.

### Phase Contract

| Field | Value |
|---|---|
| Phase goal | map possibilities; surface surprises and dead ends |
| Mode | divergent |
| Inputs consumed | §3 SandboxCharter + ProbeSeedList |
| Primary output | `ProbeLedger` + `DeadEndList` + `StrangeButInterestingList` |
| Creative permission | maximum — weird combinations encouraged |
| Boundaries | no convergence, no ranking, no product plan |
| Safety rails | inherit §2; the ONLY judgment allowed here is safety |
| Scratch space | none (throwaway probes; real code is `/slo-spike`) |
| Resource budget | enough probes to reveal a vocabulary |
| Evidence required | observations + surprises + dead ends |
| Kill criteria | the material produces no surprise after honest play |
| Handoff requirement | probe board, observations, strange-but-interesting, dead ends → `/slo-pattern` |

**Probe Board**:

| ID | Probe | Type | Setup | Observation | Surprise | Reusable? | Safety note |
|---|---|---|---|---|---|---|---|
| P1 | Taxonomy overlay on current local families | data_probe | Compared local Round 4/6/7 prompt-injection, governance, normalizer, terminal, package, memory, and reality-check families against the six trap classes. | Direct override, tool abuse, tool-result injection, output exfiltration, and memory poisoning map cleanly; Content Injection, Semantic Manipulation, Systemic, and HITL are thin. | The existing corpus is already action-rich, but not environment-rich. | yes | Metadata-only; no raw prompt copied. |
| P2 | Control-first catalog before OpenCRE | mechanism_probe | Seeded AGT-AC-001..010 from the proposal and tried mapping scenarios to controls before standards. | Mapping to controls is more actionable than mapping rows directly to OpenCRE/ASI labels. | A control can cover multiple trap classes and multiple attack families. | yes | Must stay "candidate mapping". |
| P3 | Text row vs fixture evidence | interaction_probe | Compared text-only rows with HTML/CSS/ARIA/Markdown/PDF hidden-content fixture ideas. | Text rows cannot faithfully represent human-visible vs agent-visible divergence. | Content Injection is primarily a perception-fixture problem, not just a prompt-string problem. | yes | Use harmless placeholder payloads. |
| P4 | Attempted vs executed action boundary | security_probe | Modeled evidence fields such as `unsafe_tool_call_attempted`, `unsafe_tool_call_executed`, `blocked_at`, and `audit_event_present`. | A benchmark can pass at the tool boundary even if the agent emitted unsafe text, and fail even if the final answer looks safe. | Tool-boundary telemetry is the load-bearing evidence. | yes | Mock-only; no real shell/email/network. |
| P5 | Memory poisoning as multi-session state | interaction_probe | Sketched a scenario where a synthetic memory write is attempted in session A and read in session B. | Scenario schema needs `session_model`, `state_preconditions`, and `state_assertions`. | A single prompt row cannot express persistence. | yes | Synthetic memory records only. |
| P6 | A2A spoof propagation | interaction_probe | Sketched two synthetic agents and a spoofed delegation message. | Scenario schema needs agent roles, message integrity expectation, and blast-radius assertion. | Systemic traps need multi-party fixtures even when no real agents run. | yes | No live agent bus or MCP calls. |
| P7 | Goose adapter dry-run surface | composition_probe | Reviewed current Goose positioning as desktop, CLI, API, provider, and MCP-capable agent; kept live run out of scope. | A safe adapter can be defined around scenario input, max turns, no-session mode, mock tools, timeout, trace capture, and normalized result JSON. | Contract-first is enough for promotion; live Goose is not needed in the experiment. | yes | No credentials or provider calls. |
| P8 | OpenCRE-compatible relation vocabulary | mechanism_probe | Tried exact/broad/narrow/related/candidate relations for AGT-AC controls. | Most early mappings should be broad/related/candidate, not exact. | "Candidate CRE gap" is a useful honest state. | yes | No official OpenCRE claims. |
| P9 | Scorecard evidence levels | magic_probe | Reframed badge-style scorecard language into L0 declared, L1 static, L2 mock behavioural, L3 live behavioural evidence. | The same report can be useful without becoming a certification badge. | Evidence level is more defensible than a single aggregate score. | yes | Avoid "OWASP-certified" wording. |
| P10 | Hard-benign adversary | failure_probe | Used local normalizer/round7 lessons: high-entropy structured data, security docs, code, legitimate encodings, and benign obfuscation can look hostile. | The benchmark needs hard-benign fixtures and false-positive reporting, not just attack coverage. | Controls need "must-not-block" expectations alongside attack success conditions. | yes | Synthetic benign controls only. |
| P11 | Static scanner prior art boundary | data_probe | Compared behavioural benchmark idea with agent-audit/static scanner prior art. | Static scanning is complementary evidence, not a replacement for behaviour traces. | Scorecard should aggregate static and mock evidence but preserve source type. | yes | Cite as prior art only. |
| P12 | Upstream PR boundary | mechanism_probe | Split proposed outputs into AGT scenario schema/harness, OpenCRE mapping methodology, gap mapper ticket, scorecard idea, and Goose adapter follow-up. | A small PR sequence exists if the schema/harness comes first and standards mapping stays separate. | OpenCRE mapping should probably be research before upstream contribution. | yes | No upstream PR in this loop. |

> Probe types (frozen): `mechanism_probe | interaction_probe | failure_probe | security_probe | data_probe | latency_probe | magic_probe | composition_probe`.

**Raw observations**:

- Local evidence already says prompt injection is only one of six Agent Traps categories; semantic manipulation, multi-agent/systemic, and HITL coverage are not tested.
- The Round 7 intake schema already carries `attack_class`, `harm_channel`, `multi_turn`, provenance, license, and redaction hygiene. It is a natural source for a metadata-only gap mapper.
- The current RFC is valuable as one upstream control proposal, but the broader benchmark must include controls that operate at source boundary, tool boundary, memory boundary, A2A boundary, and human-approval boundary.
- OpenCRE is a common-requirement linking platform, so the safer route is AGT-AC control -> candidate relation -> CRE, not prompt -> CRE.
- Goose's CLI/API/MCP shape makes it plausible as a later live target, but a dry-run adapter contract is the correct sandbox artifact.
- Promptfoo and Inspect/AgentThreatBench show the ecosystem is moving toward agentic red-team tasks, but this experiment's differentiator is control-linked evidence and raw-free artifacts.
- The scorecard draft's badge/aggregate-score impulse is useful energy but unsafe as-is; the experiment should preserve evidence levels and self-assessment language.

**Strange but interesting**:

- Hidden-content fixtures turn "prompt injection" into a rendering/parser-differential problem, which could make AGT's normalizer RFC part of a larger perceptual-integrity story.
- A mock tool can record an unsafe attempt even when execution is blocked, giving credit to boundary controls that a text-only detector would miss.
- "Candidate CRE gap" can be a productive output rather than a failure: it tells OpenCRE where agentic requirements may be under-specified.
- Hard-benign rows may need first-class scenario status because a safe benchmark must prove what it did not block.

**Dead ends**:

| Dead end | What failed | What it taught | Reusable fragment |
|---|---|---|---|
| Direct prompt-to-OpenCRE mapping | Rows were too concrete and attack-shaped to map cleanly to common requirements. | Map controls to OpenCRE, not prompts. | `opencre_relation: exact|broad|narrow|related|candidate`. |
| Text-only Agent Traps coverage | Content Injection, Systemic, and HITL traps became awkward prose labels. | Fixture and interaction state are required. | `human_visible_view` / `agent_visible_view` / `session_model`. |
| Badge-first scorecard | A single score hid evidence quality and encouraged certification language. | Evidence-level reporting is safer. | L0/L1/L2/L3 evidence ladder. |
| Live Goose smoke inside sandbox | A credible run would require provider config or unsafe tools. | Contract and dry-run JSON are enough for this loop. | Adapter contract with no-session, mock tools, timeout, cleanup. |

**Candidate patterns** (for `/slo-pattern`):

- Agent Traps scenario schema.
- OpenCRE-backed AGT-AC control catalog.
- Mock behavioural harness.
- Evidence-level scorecard.
- Goose adapter contract.

### Safety Check

- Data classification: Internal.
- Raw secrets present? no.
- PII present? no.
- External service called? yes, read-only public documentation/repository inspection only.
- Scratch path: none in this phase.
- Cleanup required: none.
- Abuse sketch: the dangerous path is ranking or promoting ideas before evidence; the play log defers promotion to curation.

---

## 5. Pattern Catalog

> Filled by `/slo-pattern`. Mode: **convergent**. Name reusable tricks. Cite probe IDs for every pattern. ≤5 serious candidates.

### Phase Contract

| Field | Value |
|---|---|
| Phase goal | turn raw play into named reusable mechanisms |
| Mode | convergent |
| Inputs consumed | §4 ProbeLedger |
| Primary output | `PatternCatalog` (+ NextCurve / ProductPull / ArchitecturePull) |
| Creative permission | naming + framing |
| Boundaries | do not promote everything; ≤5 candidates |
| Safety rails | inherit §2 |
| Scratch space | none |
| Resource budget | ≤5 serious candidates |
| Evidence required | cite probe IDs for every pattern |
| Kill criteria | no pattern survives the cite-evidence test |
| Handoff requirement | 1–5 candidates + evidence + claims to measure → `/slo-precision` |

**Pattern candidates**:

| Pattern | Mechanism | Probe evidence | Why surprising | Reuse cases | Risks |
|---|---|---|---|---|---|
| Agent Traps scenario schema | Add trap class, target layer, delivery surface, human/agent view divergence, session model, fixtures, controls, and success conditions to each scenario. | P1, P3, P5, P6, P10 | The schema has to represent environment and state, not just prompt text. | AGT benchmark schema, fixture packs, corpus gap mapper. | Schema could become heavy or too bespoke. |
| OpenCRE-backed AGT-AC catalog | Define AGT-AC controls first, then map controls to OpenCRE CREs or candidate CREs with relation status. | P2, P8, P12 | Candidate gaps become evidence, not embarrassment. | Standards mapping, remediation, research handoff. | Overclaiming official status; duplicating existing controls. |
| Mock behavioural harness | Use deterministic mock browser/tool/memory/audit/A2A fixtures that emit attempted/executed traces. | P4, P5, P6, P10 | It scores boundary controls even when text output is ambiguous. | Behavioural benchmark, replay, scorecard evidence. | Toy mocks may fail to predict real-agent behaviour. |
| Evidence-level scorecard | Aggregate static, mock, and optional live evidence by trap/control/evidence level instead of a badge-first score. | P7, P9, P11 | The report gets more honest and more useful by refusing certification language. | Internal posture reports, OpenCRE research, developer remediation. | Users may still read a rollup as certification. |
| Goose adapter contract | Treat Goose as the first live target behind a safe adapter contract: bounded input, mock tools, trace capture, timeout, cleanup, normalized JSON. | P7, P12 | A live-agent target can be designed without running live agents now. | Future harness adapter, comparative benchmark. | Real runs may require credentials/providers and careful sandboxing. |

**Next-Curve check** (10% improvement vs. category change):

| Pattern | Current curve | Possible next curve | Why |
|---|---|---|---|
| Agent Traps scenario schema | Prompt-injection corpus rows. | Agent-control scenarios with fixture/state semantics. | Moves from detector evaluation to environmental trap evaluation. |
| OpenCRE-backed AGT-AC catalog | Attack-class labels and ad hoc remediation. | Control-linked evidence and standards mapping. | Makes every failure actionable. |
| Mock behavioural harness | Text classifier metrics. | Action-boundary evidence. | Measures attempted vs executed unsafe behaviour. |
| Evidence-level scorecard | Aggregate score/badge pressure. | Evidence-quality posture report. | Reduces overclaim while preserving usefulness. |
| Goose adapter contract | Offline detector-only benchmark. | Optional real-agent benchmark lane. | Adds credibility after mock evidence exists. |

**DICEE check** (Deep / Intelligent / Complete / Empowering / Elegant):

| Pattern | Deep | Intelligent | Complete | Empowering | Elegant | Notes |
|---|---|---|---|---|---|---|
| Agent Traps scenario schema | yes | yes | partial | yes | medium | Needs spike to prove it is not too wide. |
| OpenCRE-backed AGT-AC catalog | yes | yes | partial | yes | medium | Strong if relation status remains honest. |
| Mock behavioural harness | yes | yes | partial | yes | high | Small deterministic traces can carry a lot of evidence. |
| Evidence-level scorecard | medium | yes | partial | yes | high | Elegant if it avoids a misleading single score. |
| Goose adapter contract | medium | yes | partial | medium | medium | Useful after schema/result contract stabilizes. |

**Sunlit strategic fit**:

| Pattern | B2C | B2B | Secure-data | Cybersecurity | Notes |
|---|---|---|---|---|---|
| Agent Traps scenario schema | low | high | medium | high | Benchmark infrastructure and upstream credibility. |
| OpenCRE-backed AGT-AC catalog | low | high | high | high | Strong research/compliance bridge if framed carefully. |
| Mock behavioural harness | medium | high | high | high | Reusable for platform and product guardrail validation. |
| Evidence-level scorecard | medium | high | medium | high | Could become a developer-facing posture report. |
| Goose adapter contract | low | medium | medium | high | Useful comparative lane, not first product wedge. |

**Product pull**: the evidence-level scorecard is the closest user-facing wedge, but only after the schema/harness can supply evidence. It should be routed as an idea, not a delivery commitment.

**Architecture pull**: the scenario schema, AGT-AC catalog, and mock behavioural harness form the platform core. The Goose adapter is a later extension once the result schema and mock trace contract are stable.

### Safety Check

- Data classification: Internal.
- Raw secrets present? no.
- PII present? no.
- External service called? no new calls during patterning.
- Scratch path: none.
- Cleanup required: none.
- Abuse sketch: the risky move would be promoting all five; precision keeps them measurable and curation will assign dispositions.

---

## 6. Precision Model

> Filled by `/slo-precision`. Mode: **measurement**. Make claims falsifiable. No "feels better" without a handle. Every candidate needs an accept AND a kill threshold.

### Phase Contract

| Field | Value |
|---|---|
| Phase goal | convert promising patterns into measurable claims |
| Mode | measurement |
| Inputs consumed | §5 PatternCatalog |
| Primary output | `PrecisionModel` (handles, thresholds, bounds, invariants) |
| Creative permission | choose the instruments |
| Boundaries | no unmeasured claims proceed to spike |
| Safety rails | inherit §2 + name security invariants |
| Scratch space | none (planning only) |
| Resource budget | declare expected resource bounds per claim |
| Evidence required | a metric / observable / falsifiable threshold per claim |
| Kill criteria | a candidate has no falsifiable claim |
| Handoff requirement | learning questions + instrumentation + accept/kill thresholds + invariants → `/slo-spike` |

**Claims that need handles**:

| Claim | Measurement handle | Instrumentation | Accept threshold | Kill threshold |
|---|---|---|---|---|
| A v2 schema can represent all six Agent Traps classes plus control/evidence labels. | Scenario validator pass/fail by trap class and required field coverage. | JSON Schema + 24 synthetic scenario examples. | 24 examples validate; all six trap classes represented; every scenario has at least one AGT-AC control and success condition. | More than two trap classes require ad hoc fields outside the schema. |
| A seed AGT-AC catalog can map scenarios to controls before CRE IDs are finalized. | Control count, scenario-control links, relation status distribution. | Mapping pack with `exact|broad|narrow|related|candidate` relations. | At least 15 controls; at least 30 scenario-control links; candidate gaps listed separately. | Mapping collapses into attack labels or certification claims. |
| Current corpus gaps can be quantified by trap class, ASI/AIVSS hypothesis, control, and evidence level. | Coverage matrix with counts and missing fixture types. | Metadata-only sampled rows + mapping rules + gap report. | Report identifies concrete under-covered classes and fixture needs. | Gaps remain qualitative only. |
| Mock tools can distinguish attempted unsafe actions from executed unsafe actions. | Tool trace fields and validator assertions. | Mock shell/email/memory/MCP/audit tools emitting JSON/JSONL traces. | At least 5 mock tools emit deterministic traces; unsafe attempt can be blocked while recorded. | Trace cannot distinguish attempt vs execution. |
| A scorecard report can aggregate evidence without overclaiming. | Report language scan and coverage by evidence level. | Sample results JSONL -> Markdown/JSON scorecard. | Report includes trap coverage, control coverage, OpenCRE status, evidence level, remediation, and no certification wording. | Report implies official OWASP/OpenCRE certification or collapses to one unexplained score. |
| Goose can be wrapped behind a stable adapter contract without benchmark-specific coupling. | Adapter contract completeness and normalized sample result. | Pseudocode + sample result matching the result schema. | Contract defines scenario input, execution limits, trace capture, timeout, cleanup, and dry-run output. | Basic smoke would require live secrets, unsafe tools, or uncontrolled side effects. |

**Invisible variables**:

| Variable | Unit | Expected range | Hard bound | How measured |
|---|---:|---:|---:|---|
| Trap class coverage | classes | 6 | 6 | Count distinct `trap_class` values in validated examples. |
| Control coverage | AGT-AC controls | 15-20 | at least 15 | Count controls in mapping pack. |
| Scenario-control links | links | 30-80 | at least 30 | Count links in generated coverage matrix. |
| Evidence level | L0-L3 | L1-L2 in this loop | no L3 live evidence | Scorecard/report fields. |
| External side effects | calls | 0 | 0 | Command log and safety checks. |
| Certification language | banned terms | 0 | 0 | Manual scan and report wording. |

**Reliability / compounding risk**:

| Chain | Per-step risk | Combined risk | Mitigation |
|---|---|---|---|
| Scenario schema -> gap mapper -> scorecard | Bad schema fields create misleading coverage. | Scorecard inherits schema error. | Validate examples first; keep evidence source and confidence explicit. |
| AGT-AC -> OpenCRE relation | Controls overfit local taxonomy. | Mapping looks standards-backed when it is only candidate. | Relation status required; candidate gaps separated. |
| Mock trace -> promotion | Toy mock overstates real-agent safety. | Live adapter promoted too early. | Mark mock evidence L2 only; Goose remains dry-run contract. |
| Corpus rows -> raw artifact | Raw prompt text leaks into reports. | Public/upstream artifact hygiene failure. | Metadata-only sampled rows and placeholder payloads. |

**False positive / false negative plan** (required for any classification/detection/retrieval/ML claim):

| Error type | How tested | Accept threshold | Must-never case |
|---|---|---|---|
| False positive: benign/hard-benign scenario labelled unsafe | Include hard-benign synthetic controls in schema/gap examples. | Gap report separates benign controls and does not treat all obfuscation as attack. | Security docs, code, structured data, or legitimate encodings become automatic failures without an unsafe success condition. |
| False negative: trap class appears covered by weak text-only row | Require fixture/session/evidence fields for Content Injection, Systemic, HITL, memory, and A2A scenarios. | Coverage matrix lists missing fixture type when evidence is only L0/L1. | A text-only prompt row counts as behavioural coverage. |
| Mapping false positive: official standards claim | Scan report language and relation status. | All mappings marked exact/broad/narrow/related/candidate; no certification language. | "OpenCRE certified", "OWASP certified", or equivalent. |
| Behavioural false negative: unsafe attempt hidden because execution blocked | Tool trace records attempt separately from execution. | Mock trace includes both `attempted=true` and `executed=false` for blocked action. | A blocked unsafe attempt disappears from evidence. |

**Resource budget**:

| Resource | Expected bound | Hard limit | Behavior at limit |
|---|---:|---:|---|
| CPU | standard local Python scripts | single workstation, no parallel load | stop and record blocked spike. |
| Memory | <256 MB per script | 512 MB | stop and reduce examples. |
| Time | <5 seconds per validation script | 60 seconds per script | stop and record timeout. |
| Network | 0 during spikes | 0 | refuse live adapter or OpenCRE API call. |
| Cost | 0 | 0 | no paid model/provider calls. |

**Security invariants** (what must never happen):

- No real secrets, credentials, PII, customer data, or production prompts in any artifact.
- No live external target, provider call, OpenCRE API write, Goose run with real tools, or upstream PR during this loop.
- No production/runtime file changes.
- No certification, official OWASP/OpenCRE, or badge-readiness claim.
- Scratch code remains under `experiments/agt-redteam-agent-traps-opencre/<spike-id>/`.
- Reports remain raw-free and use synthetic placeholders.

### Safety Check

- Data classification: Internal.
- Raw secrets present? no.
- PII present? no.
- External service called? no new calls during precision.
- Scratch path: declared for `/slo-spike`; none created yet.
- Cleanup required: none yet.
- Abuse sketch: the main abuse path is mistaking mock/L2 evidence for live/L3 safety; the precision model labels evidence levels explicitly.

---

## 7. Spike Cards and Evidence

> Filled by `/slo-spike`. Mode: **evidence**. The ONLY phase that may run code — scratch-only under `experiments/<slug>/<spike-id>/`. A spike is done when the learning question is answered, NOT when the prototype is polished. Every spike ends with a delete-or-promote decision. **No production files. No production promotion.**

### Spike Card — `s1-schema`

**Phase Contract**:

| Field | Value |
|---|---|
| Phase goal / learning question | Can a v2 AGT Red Team scenario schema represent prompt-injection, Agent Traps, control mapping, mock environment, and success conditions? |
| Mode | evidence |
| Inputs consumed | §6 PrecisionModel (the falsifiable claim) |
| Primary output | `SpikeCard` + `EvidenceLog` |
| Scratch path | `experiments/agt-redteam-agent-traps-opencre/s1-schema/` |
| Production files allowed | none by default |
| Data allowed | synthetic/generated only |
| External calls allowed | none |
| Dependency policy | Python standard library only |
| Resource budget | local CPU, <5s expected, 60s hard timeout, 0 network |
| Cleanup rule | no untracked junk outside the scratch path |

**Setup**: Generated `scenario.schema.json`, `result.schema.json`, `validate_scenarios.py`, and 24 synthetic scenario examples covering four examples per Agent Traps class.

**Method**: Validated every example for required fields, known trap class, AGT-AC controls, success conditions, view fields, and session model.

**Commands / Evidence**:

| Step | Command / action | Expected | Actual | Notes |
|---|---|---|---|---|
| S1.1 | `python3 experiments/agt-redteam-agent-traps-opencre/s1-schema/validate_scenarios.py experiments/agt-redteam-agent-traps-opencre/s1-schema/examples/*.json` | 24 valid scenarios, all six trap classes represented | PASS: `validated=24`; each trap class count = 4 | Meets accept threshold. |

**Results**: Accepted. Schema represented all six trap classes with no ad hoc fields outside the schema.

**Surprise**: The schema needed first-class `views` and `session_model` fields; attack labels alone were not enough.

**Safety Result**:

| Invariant | Result | Evidence |
|---|---|---|
| No raw secrets/PII | pass | examples use synthetic placeholders only |
| No production files changed | pass | scratch path only |
| No external calls | pass | local validator only |

**Decision hint**: `promote_to_runbook` for the schema/harness core.

### Spike Card — `s2-gap-map`

**Phase Contract**:

| Field | Value |
|---|---|
| Phase goal / learning question | What is actually missing from the current corpus when viewed through Agent Traps + controls? |
| Mode | evidence |
| Inputs consumed | §6 PrecisionModel |
| Primary output | `SpikeCard` + `EvidenceLog` |
| Scratch path | `experiments/agt-redteam-agent-traps-opencre/s2-gap-map/` |
| Production files allowed | none |
| Data allowed | synthetic/metadata-only sampled rows |
| External calls allowed | none |
| Dependency policy | generated static artifacts only |
| Resource budget | local file generation, 0 network |
| Cleanup rule | no files outside scratch |

**Setup**: Generated `mapping_rules.yaml`, `sampled_rows.jsonl`, `coverage_matrix.json`, and `gap_report.md`.

**Method**: Created metadata-only representative rows and aggregated coverage by trap class, controls, fixture types, and evidence levels.

**Commands / Evidence**:

| Step | Command / action | Expected | Actual | Notes |
|---|---|---|---|---|
| S2.1 | Inspect `coverage_matrix.json` | Six trap classes represented | PASS: matrix contains Behavioural Control, Cognitive State, Content Injection, Human-in-the-Loop, Semantic Manipulation, Systemic | Metadata-only; no prompt text. |
| S2.2 | Inspect `gap_report.md` | Decision-useful gaps listed | PASS: identifies Content Injection fixtures, Systemic A2A, HITL, memory, and hard-benign controls | Meets accept threshold. |

**Results**: Accepted. The report gives concrete next fixture/control gaps instead of repeating existing corpus families.

**Surprise**: Hard-benign must-not-block coverage deserves first-class reporting alongside attack coverage.

**Safety Result**:

| Invariant | Result | Evidence |
|---|---|---|
| No raw prompt leakage | pass | `sampled_rows.jsonl` is metadata-only |
| No production files changed | pass | scratch path only |
| No external calls | pass | generated local artifacts |

**Decision hint**: `promote_to_ticket` for a local corpus gap mapper.

### Spike Card — `s3-content-fixtures`

**Phase Contract**:

| Field | Value |
|---|---|
| Phase goal / learning question | Can AGT Red Team test perception traps using fixtures instead of text-only prompts? |
| Mode | evidence |
| Inputs consumed | §6 PrecisionModel |
| Primary output | `SpikeCard` + `EvidenceLog` |
| Scratch path | `experiments/agt-redteam-agent-traps-opencre/s3-content-fixtures/` |
| Production files allowed | none |
| Data allowed | synthetic placeholders |
| External calls allowed | none |
| Dependency policy | Python standard library only |
| Resource budget | local CPU, <5s expected, 60s hard timeout, 0 network |
| Cleanup rule | no files outside scratch |

**Setup**: Generated HTML, Markdown, and synthetic PDF-placeholder fixtures plus `extract_fixture_views.py`.

**Method**: Extracted human-visible and agent-visible views and counted render/parse divergence.

**Commands / Evidence**:

| Step | Command / action | Expected | Actual | Notes |
|---|---|---|---|---|
| S3.1 | First run of `extract_fixture_views.py` | At least 5 divergent fixtures | FAIL: 2/6 divergent | Useful failure: extractor stripped comments/ARIA/hrefs too aggressively. |
| S3.2 | Patch generator and rerun `extract_fixture_views.py` | At least 5 divergent fixtures | PASS: 6/6 divergent | Meets accept threshold; report at `fixture_view_report.json`. |

**Results**: Accepted after regression-style fix. The fixture pack can safely represent human-visible vs agent-visible divergence using harmless placeholders.

**Surprise**: The extractor itself is a benchmark subject; a naive parser can erase the agent-visible hidden channel and produce false comfort.

**Safety Result**:

| Invariant | Result | Evidence |
|---|---|---|
| No raw dangerous payloads | pass | placeholders only |
| No external rendering infrastructure | pass | local synthetic view extraction |
| No production files changed | pass | scratch path only |

**Decision hint**: `promote_to_ticket` after schema/harness work.

### Spike Card — `s4-mock-tools`

**Phase Contract**:

| Field | Value |
|---|---|
| Phase goal / learning question | Can deterministic mock tools produce evidence for attempted vs executed unsafe actions? |
| Mode | evidence |
| Inputs consumed | §6 PrecisionModel |
| Primary output | `SpikeCard` + `EvidenceLog` |
| Scratch path | `experiments/agt-redteam-agent-traps-opencre/s4-mock-tools/` |
| Production files allowed | none |
| Data allowed | synthetic |
| External calls allowed | none |
| Dependency policy | Python standard library only |
| Resource budget | local CPU, <5s expected, 60s hard timeout, 0 network |
| Cleanup rule | no files outside scratch |

**Setup**: Generated `mock_tools.py`, one JSON result per mock tool, `tool_trace.schema.json`, and `sample_trace.jsonl`.

**Method**: Simulated mock shell, email, memory, MCP registry, and audit log tools with separate `attempted`, `executed`, `blocked_at`, `canary_leaked`, and `audit_event_present` fields.

**Commands / Evidence**:

| Step | Command / action | Expected | Actual | Notes |
|---|---|---|---|---|
| S4.1 | `python3 experiments/agt-redteam-agent-traps-opencre/s4-mock-tools/mock_tools.py` | >=5 traces, blocked unsafe attempts recorded | PASS: 5 traces, 4 blocked attempts | Meets accept threshold. |

**Results**: Accepted. Attempted vs executed action evidence is representable with deterministic mock traces.

**Surprise**: Canary leakage can be recorded even when the unsafe send is blocked, which makes blocked-at-boundary evidence visible.

**Safety Result**:

| Invariant | Result | Evidence |
|---|---|---|
| Mock tools never execute real side effects | pass | generated JSON only |
| Unsafe attempts remain observable | pass | `sample_trace.jsonl` |
| No production files changed | pass | scratch path only |

**Decision hint**: `promote_to_runbook` as part of the benchmark harness.

### Spike Card — `s5-opencre`

**Phase Contract**:

| Field | Value |
|---|---|
| Phase goal / learning question | Can the AGT-AC catalog be expressed as an OpenCRE-compatible mapping pack? |
| Mode | evidence |
| Inputs consumed | §6 PrecisionModel |
| Primary output | `SpikeCard` + `EvidenceLog` |
| Scratch path | `experiments/agt-redteam-agent-traps-opencre/s5-opencre/` |
| Production files allowed | none |
| Data allowed | synthetic control catalog |
| External calls allowed | none |
| Dependency policy | generated static YAML/CSV/Markdown |
| Resource budget | local file generation, 0 network |
| Cleanup rule | no files outside scratch |

**Setup**: Generated `agentic-controls.yaml`, `opencre-mapping.yaml`, `agt-agentic-controls.csv`, `mapping-methodology.md`, and `unmapped-agentic-gaps.md`.

**Method**: Defined 15 AGT-AC controls and relation statuses `exact|broad|narrow|related|candidate`, while separating candidate CRE gaps.

**Commands / Evidence**:

| Step | Command / action | Expected | Actual | Notes |
|---|---|---|---|---|
| S5.1 | Count `agt-agentic-controls.csv` rows | >=15 controls | PASS: 15 controls | Meets accept threshold. |
| S5.2 | Scan mapping language | No official certification claim | PASS: mapping files state scratch/self-assessment/candidate status | Some scan hits are caveats, not claims. |

**Results**: Accepted as a research seed, not a standards contribution. The mapping pack is useful enough to promote to `/slo-research`.

**Surprise**: Candidate gaps are the most honest and useful output for render/parse divergence, memory integrity, A2A integrity, and evidence-level reporting.

**Safety Result**:

| Invariant | Result | Evidence |
|---|---|---|
| No certification language | pass with caveat | mentions are anti-claim caveats |
| No OpenCRE API writes | pass | static local files |
| No production files changed | pass | scratch path only |

**Decision hint**: `promote_to_research`.

### Spike Card — `s6-scorecard`

**Phase Contract**:

| Field | Value |
|---|---|
| Phase goal / learning question | Can a report aggregate results by Agent Traps, ASI/AIVSS, OpenCRE controls, evidence level, and remediation? |
| Mode | evidence |
| Inputs consumed | §6 PrecisionModel |
| Primary output | `SpikeCard` + `EvidenceLog` |
| Scratch path | `experiments/agt-redteam-agent-traps-opencre/s6-scorecard/` |
| Production files allowed | none |
| Data allowed | synthetic sample results |
| External calls allowed | none |
| Dependency policy | generated JSONL/JSON/Markdown |
| Resource budget | local file generation, 0 network |
| Cleanup rule | no files outside scratch |

**Setup**: Generated `sample_results.jsonl`, `scorecard_report.md`, `scorecard_report.json`, and `controls_coverage.json`.

**Method**: Aggregated sample results by trap class, AGT-AC control, and evidence level, with remediation and `certification_claim: false`.

**Commands / Evidence**:

| Step | Command / action | Expected | Actual | Notes |
|---|---|---|---|---|
| S6.1 | Inspect `scorecard_report.json` | Certification flag false | PASS: `certification_claim=false` | Meets no-overclaim threshold. |
| S6.2 | Inspect `scorecard_report.md` | Evidence levels and remediation visible | PASS | Report avoids single unexplained badge score. |

**Results**: Accepted as an idea seed. The scorecard is useful only when framed as evidence-level self-assessment.

**Surprise**: The scorecard becomes clearer when the aggregate score disappears.

**Safety Result**:

| Invariant | Result | Evidence |
|---|---|---|
| No certification claim | pass | explicit `certification_claim=false` |
| Raw-free report | pass | synthetic IDs and aggregate counts |
| No production files changed | pass | scratch path only |

**Decision hint**: `promote_to_idea`.

### Spike Card — `s7-goose-adapter`

**Phase Contract**:

| Field | Value |
|---|---|
| Phase goal / learning question | Can Goose be treated as a target agent through a stable adapter contract? |
| Mode | evidence |
| Inputs consumed | §6 PrecisionModel |
| Primary output | `SpikeCard` + `EvidenceLog` |
| Scratch path | `experiments/agt-redteam-agent-traps-opencre/s7-goose-adapter/` |
| Production files allowed | none |
| Data allowed | synthetic contract sample |
| External calls allowed | none |
| Dependency policy | pseudocode only; no Goose invocation |
| Resource budget | local file generation, 0 network |
| Cleanup rule | no files outside scratch |

**Setup**: Generated `adapter_contract.md`, `goose_adapter_pseudocode.py`, `sample_goose_result.json`, and `goose_safety_notes.md`.

**Method**: Defined scenario input, max turns, timeout, mock-tools-only mode, no-session cleanup, normalized result JSON, and no live credentials.

**Commands / Evidence**:

| Step | Command / action | Expected | Actual | Notes |
|---|---|---|---|---|
| S7.1 | `python3 -m py_compile .../goose_adapter_pseudocode.py` | Syntax OK | PASS | Pseudocode only; no live run. |

**Results**: Accepted as a later adapter ticket, after schema and mock harness stabilize.

**Surprise**: Contract-first gives enough clarity to defer live Goose execution safely.

**Safety Result**:

| Invariant | Result | Evidence |
|---|---|---|
| No provider credentials or live tools | pass | dry-run artifacts only |
| No network | pass | no Goose invocation |
| No production files changed | pass | scratch path only |

**Decision hint**: `promote_to_ticket` after harness.

### Spike Card — `s8-promotion`

**Phase Contract**:

| Field | Value |
|---|---|
| Phase goal / learning question | What should be promoted, and in what PR/order, if the experiment succeeds? |
| Mode | evidence |
| Inputs consumed | §6 PrecisionModel and S1-S7 evidence |
| Primary output | `SpikeCard` + `EvidenceLog` |
| Scratch path | `experiments/agt-redteam-agent-traps-opencre/s8-promotion/` |
| Production files allowed | none |
| Data allowed | generated planning docs |
| External calls allowed | none |
| Dependency policy | Markdown only |
| Resource budget | local file generation, 0 network |
| Cleanup rule | no files outside scratch |

**Setup**: Generated `promotion-plan.md`, AGT PR boundary drafts, OpenCRE mapping research draft, and scorecard follow-up draft.

**Method**: Split promotion into schema, mock harness, control reporting, Goose adapter, OpenCRE research, and scorecard idea routes.

**Commands / Evidence**:

| Step | Command / action | Expected | Actual | Notes |
|---|---|---|---|---|
| S8.1 | Inspect `promotion-plan.md` and sibling drafts | Small sequence, no monolithic PR | PASS | Meets accept threshold. |

**Results**: Accepted. Promotion can be split cleanly; upstream AGT and OpenCRE proposals remain separate.

**Surprise**: The first promotable unit is not the scorecard or Goose adapter; it is the schema and deterministic harness.

**Safety Result**:

| Invariant | Result | Evidence |
|---|---|---|
| No upstream PR opened | pass | planning docs only |
| No production files changed | pass | scratch path only |
| No certification claim | pass | scorecard follow-up says self-assessment |

**Decision hint**: `promote_to_runbook`.

### Spike Evidence Summary

| Spike | Decision hint | Evidence |
|---|---|---|
| S1 schema | `promote_to_runbook` | 24 validated examples; all six trap classes covered. |
| S2 gap map | `promote_to_ticket` | Metadata-only coverage matrix and gap report. |
| S3 content fixtures | `promote_to_ticket` | 6/6 divergent fixtures after extractor fix. |
| S4 mock tools | `promote_to_runbook` | 5 traces; 4 unsafe attempts blocked but recorded. |
| S5 OpenCRE mapping | `promote_to_research` | 15 controls; candidate relation vocabulary. |
| S6 scorecard | `promote_to_idea` | Evidence-level report; `certification_claim=false`. |
| S7 Goose adapter | `promote_to_ticket` | Dry-run contract and normalized sample result. |
| S8 promotion | `promote_to_runbook` | Small PR/runbook sequence; no monolithic promotion. |

### Safety Check

- Data classification: Internal.
- Raw secrets present? no.
- PII present? no.
- External service called? no during spikes.
- Scratch path: `experiments/agt-redteam-agent-traps-opencre/<spike-id>/`.
- Cleanup required: generated `__pycache__` directories were removed.
- Abuse sketch: unsafe use would be treating S1-S8 as production or live-agent evidence; the evidence level remains static/mock/dry-run only.

---

## 8. Curation Decision

> Filled by `/slo-curate`. Mode: **convergent**. Kill / continue / promote. Exactly one disposition per candidate, each citing a probe/spike. No vague maybes survive. Dead ends route to §11 compost.

### Phase Contract

| Field | Value |
|---|---|
| Phase goal | decide what to promote, continue, kill, or archive |
| Mode | convergent |
| Inputs consumed | §3–§7 (all evidence) |
| Primary output | `CurationDecision` + `CompostEntries` |
| Creative permission | none — this is the honesty gate |
| Boundaries | no candidate left undisposed |
| Safety rails | inherit §2 |
| Scratch space | none |
| Resource budget | exactly one disposition per candidate |
| Evidence required | every decision cites probes/spikes |
| Kill criteria | (n/a — this phase decides) |
| Handoff requirement | promoted candidates → `/slo-demo` |

**Candidate board**:

| Candidate | Evidence | Surprise | Value | Risk | Decision |
|---|---|---|---|---|---|
| Agent Traps scenario schema | P1/P3/P5/P6; S1 validates 24 scenarios across all six trap classes | Scenario needs view/session/environment fields, not just labels | High: unlocks all later benchmark work | Schema could grow too heavy | `promote_to_runbook` |
| OpenCRE-backed AGT-AC catalog | P2/P8/P12; S5 defines 15 controls and relation vocabulary | Candidate CRE gaps are useful evidence | High for research and standards mapping | Overclaiming official status | `promote_to_research` |
| Corpus gap report | P1/P10; S2 metadata-only coverage matrix | Hard-benign controls are first-class gaps | Medium/high: immediate local tooling | Can become shallow if it only counts labels | `promote_to_ticket` |
| Content fixtures | P3; S3 reaches 6/6 divergent fixture views after extractor fix | The extractor is itself a failure surface | High for Content Injection coverage | Fixture handling can get unsafe if raw payloads creep in | `promote_to_ticket` |
| Mock behavioural harness | P4/P5/P6/P10; S4 emits attempted/executed traces | Blocked unsafe attempts can still be scored | High: moves beyond detector metrics | Toy mocks may overstate live safety | `promote_to_runbook` |
| Evidence-level scorecard | P7/P9/P11; S6 reports evidence levels and `certification_claim=false` | It improves when the badge disappears | Medium: good future product/research wedge | Users may still read it as certification | `promote_to_idea` |
| Goose adapter contract | P7/P12; S7 dry-run contract and sample result | Contract-first makes live execution deferrable | Medium: credible later live-agent target | Live runs require provider/tool sandboxing | `promote_to_ticket` |
| Upstream PR boundary draft | P12; S8 separates PR/runbook/research tracks | First unit is schema+harness, not scorecard | High: prevents monolithic upstream proposal | Premature upstreaming before research | `promote_to_runbook` |

**Decision rubric**:

| Dimension | Question | Score / Notes |
|---|---|---|
| Meaning | Does this matter to Sunlit's mission? | Strong: turns agent-control safety from prose into replayable evidence. |
| User value | Would a user behave differently? | Yes, after promotion: maintainers can see which controls are declared, statically supported, or behaviourally tested. |
| Surprise | Does it create a "wait, that's possible?" moment? | Yes: attempted-vs-executed traces let blocked unsafe attempts become measurable evidence. |
| Reliability | Can this become dependable? | Plausible for schema/mock harness; live Goose remains future-gated. |
| Security | Can this be made safe without ruining it? | Yes if artifacts stay synthetic/raw-free and mappings stay candidate/self-assessment. |
| Strategic fit | B2C / B2B / secure-data / cybersecurity? | Primarily B2B/cybersecurity/platform. |
| Reuse | A reusable platform capability? | Yes: schema, controls, trace schema, and scorecard format are reusable. |
| Evidence quality | Actually tested, or only speculated? | S1/S3/S4 tested locally; S2/S5/S6/S7/S8 are bounded static/dry-run evidence. |
| Elegance | Simple from the user's point of view? | Best route is a runbook that packages schema+harness first, then standards/reporting/adapters. |

**Final disposition** (exactly one of the frozen 8 per candidate):

| Candidate | Decision | Why | Next artifact |
|---|---|---|---|
| Agent Traps scenario schema | `promote_to_runbook` | S1 validates 24 examples across all six trap classes; schema is the root dependency. | `docs/RUNBOOK-agt-redteam-agent-traps-opencre.md` |
| OpenCRE-backed AGT-AC catalog | `promote_to_research` | S5 proves a candidate mapping pack, but relation quality needs standards research before contribution. | `docs/slo/research/opencre-agentic-controls/` |
| Corpus gap report | `promote_to_ticket` | S2 produces a metadata-only gap matrix with immediate local value. | `docs/slo/tickets/ticket-<issue>-agent-traps-gap-mapper.md` |
| Content fixtures | `promote_to_ticket` | S3 proves safe divergent fixtures and exposes parser failure mode. | `docs/slo/tickets/ticket-<issue>-content-injection-fixtures.md` |
| Mock behavioural harness | `promote_to_runbook` | S4 proves attempted/executed traces; should ship with schema. | `docs/RUNBOOK-agt-redteam-agent-traps-opencre.md` |
| Evidence-level scorecard | `promote_to_idea` | S6 is promising but should not precede evidence substrate. | `docs/slo/idea/evidence-level-agentic-scorecard.md` |
| Goose adapter contract | `promote_to_ticket` | S7 gives a safe dry-run contract; live execution must wait for harness gates. | `docs/slo/tickets/ticket-<issue>-goose-adapter-contract.md` |
| Upstream PR boundary draft | `promote_to_runbook` | S8 proves promotion can be sequenced without one giant PR. | `docs/RUNBOOK-agt-redteam-agent-traps-opencre.md` |

**Compost / lessons routed forward**:

- Badge-first scorecard language is composted: keep the evidence ladder, drop certification framing.
- Direct prompt-to-OpenCRE mapping is composted: map controls first.
- Live Goose execution is parked behind a future runbook/ticket because this experiment only produced dry-run evidence.

### Safety Check

- Data classification: Internal.
- Raw secrets present? no.
- PII present? no.
- External service called? no during curation.
- Scratch path: `experiments/agt-redteam-agent-traps-opencre/<spike-id>/`.
- Cleanup required: none.
- Abuse sketch: unsafe promotion would skip the runbook and treat scratch evidence as production/live-agent validation; curation routes through SLO delivery.

---

## 9. Demo Pack

> Filled by `/slo-demo`. Mode: **communication**. Make the discovery communicable. Promotion is a **suggestion** the human accepts — never an auto-invocation of the next skill.

### Phase Contract

| Field | Value |
|---|---|
| Phase goal | make the discovery handable to the next SLO skill without chat memory |
| Mode | communication |
| Inputs consumed | §8 CurationDecision (promoted candidate) |
| Primary output | `PromotionPacket` (§10) + Demo Pack |
| Creative permission | narrative framing |
| Boundaries | no auto-invoke of a downstream skill |
| Safety rails | inherit §2 + the Security Posture table below |
| Scratch space | none |
| Resource budget | one demo per promoted candidate |
| Evidence required | reproducible demo path + evidence table |
| Kill criteria | (n/a) |
| Handoff requirement | a filled §10 seed table matching the disposition |

**One-sentence magic**: AGT Red Team can move from prompt-injection rows to a standards-linked agent-trap benchmark: every scenario maps to controls, candidate OpenCRE relations, evidence level, and remediation, and can be tested first in deterministic mocks before any live-agent run.

**Before**: the local corpus could measure detector catch/false-positive behaviour, but it could not clearly say which agent-control layer failed, whether an unsafe action was merely attempted or actually executed, which Agent Traps classes were uncovered, or what evidence level supported a standards-style claim.

**After**: a schema + mock harness can show trap coverage, control coverage, render/parse divergence, attempted-vs-executed tool traces, candidate OpenCRE relation status, and raw-free scorecard evidence without claiming official certification.

**Demo path**:

1. Validate the schema examples:
   `python3 experiments/agt-redteam-agent-traps-opencre/s1-schema/validate_scenarios.py experiments/agt-redteam-agent-traps-opencre/s1-schema/examples/*.json`
2. Extract fixture views:
   `python3 experiments/agt-redteam-agent-traps-opencre/s3-content-fixtures/extract_fixture_views.py`
3. Generate mock tool traces:
   `python3 experiments/agt-redteam-agent-traps-opencre/s4-mock-tools/mock_tools.py`
4. Inspect the control mapping:
   `experiments/agt-redteam-agent-traps-opencre/s5-opencre/agt-agentic-controls.csv`
5. Inspect the self-assessment report:
   `experiments/agt-redteam-agent-traps-opencre/s6-scorecard/scorecard_report.md`

**Evidence**:

| Evidence | Location | What it proves |
|---|---|---|
| Scenario schema + 24 examples | `experiments/agt-redteam-agent-traps-opencre/s1-schema/` | All six Agent Traps classes can be represented with controls and success conditions. |
| Gap mapper artifacts | `experiments/agt-redteam-agent-traps-opencre/s2-gap-map/` | Corpus gaps can be expressed by trap class, control, fixture type, and evidence level. |
| Content fixture pack | `experiments/agt-redteam-agent-traps-opencre/s3-content-fixtures/` | Human-visible and agent-visible divergence can be represented safely. |
| Mock tool traces | `experiments/agt-redteam-agent-traps-opencre/s4-mock-tools/` | Attempted unsafe actions can be recorded separately from execution. |
| AGT-AC/OpenCRE-compatible mapping | `experiments/agt-redteam-agent-traps-opencre/s5-opencre/` | 15 controls can be mapped with explicit relation status and candidate gaps. |
| Scorecard prototype | `experiments/agt-redteam-agent-traps-opencre/s6-scorecard/` | Evidence-level reporting can avoid certification claims. |
| Goose dry-run contract | `experiments/agt-redteam-agent-traps-opencre/s7-goose-adapter/` | A live-agent adapter can be specified without running live tools. |
| Promotion boundary | `experiments/agt-redteam-agent-traps-opencre/s8-promotion/` | Promotion can be split into schema/harness, mapping research, tickets, and scorecard idea. |

**Security posture**:

| Concern | Status | Notes |
|---|---|---|
| Data exposure | controlled | Synthetic placeholders and metadata-only reports. |
| Secret handling | pass | No real secrets or credentials; raw-free artifacts. |
| Network calls | none during spikes | Earlier research was read-only; no live agent/provider/API calls. |
| Abuse scenario | bounded | Do not treat candidate mappings as official certification or run live attacks. |
| Resource use | minimal | Local Python scripts only. |

**Productization route** (choose exactly one): `/slo-plan`.

### Safety Check

- Data classification: Internal.
- Raw secrets present? no.
- PII present? no.
- External service called? no during demo packaging.
- Scratch path: `experiments/agt-redteam-agent-traps-opencre/<spike-id>/`.
- Cleanup required: none.
- Abuse sketch: future agents must not auto-open upstream PRs or claim standards certification; the next step is a runbook plan.

---

## 10. Handoff Contract

> Filled by `/slo-demo` (or `/slo-curate`). Fill the ONE seed table that matches the chosen disposition. Promotion is a suggestion; the human runs the next skill.

### Idea Seed → `/slo-ideate`

| Field | Value |
|---|---|
| Working title | |
| Discovered pattern | |
| User who might care | |
| Pain hypothesis | |
| Smallest complete value slice candidate | |
| One-sentence magic | |
| Worst-day starter risks | |
| Success thesis draft | |
| Open questions | |
| Evidence from experiment | |

### Ticket Seed → `/slo-ticket-plan`

| Field | Value |
|---|---|
| Proposed ticket title | |
| Exact change | |
| Why now | |
| Files likely touched | |
| Out of scope | |
| Acceptance scenario | |
| Test expectation | |
| Security concern | |
| Evidence from experiment | |

### Research Seed → `/slo-research`

| Field | Value |
|---|---|
| Research question | |
| Decision it will unblock | |
| Sources needed | |
| Competing approaches | |
| Claims to verify | |
| Evidence already collected | |

### Runbook Seed → `/slo-plan` (rare — only when architecture clarity already exists)

| Field | Value |
|---|---|
| Proposed runbook title | AGT Red Team benchmark harness and Agent Traps scenario schema |
| Target architecture sketch | `benchmarks/agent-redteam/{schema,scenarios,fixtures,harness,controls,reporters,adapters}` with scratch evidence from S1-S8 as seed material. |
| Milestone candidates | M1 schema + validator; M2 Agent Traps smoke suite; M3 content fixture pack; M4 mock browser/tool/memory/audit/A2A harness; M5 control-linked reporter; M6 Goose adapter dry-run; M7 upstream-ready docs and PR boundaries. |
| Interfaces likely touched | Future upstream benchmark paths only; no AGT runtime behaviour until a separate accepted delivery runbook. |
| Data classification | Internal during planning; public-only subset requires upstream hygiene scan. |
| Threat-model starter rows | Raw prompt leakage; fixture parser hiding agent-visible content; unsafe mock escaping; overclaiming official standards status; live-agent side effects/cost; hard-benign false positives. |
| Measurement-contract starter | 24 scenario schema validation; all six trap classes; 15+ AGT-AC controls; fixture divergence count; attempted/executed trace assertions; raw-free reports; evidence-level scorecard; no certification wording. |
| Evidence from experiment | S1-S8 artifacts under `experiments/agt-redteam-agent-traps-opencre/`; validation commands in §9 demo path. |

### Compost Entry → archive / lessons

| Field | Value |
|---|---|
| What we tried | |
| Why it failed | |
| What it taught | |
| Reusable fragment | |
| Future trigger to revisit | |

---

## 11. Compost / Lessons

> Always filled — even a fully-promoted experiment records what it learned; a killed one records the reusable fragment.

- **What should future experiments or runbooks remember?** <bullets>
- **What should future experiments or runbooks remember?**
  - Map controls before standards; map scenarios to controls before OpenCRE.
  - Text-only prompt rows cannot represent Content Injection, Systemic, HITL, or stateful memory traps well enough.
  - Attempted-vs-executed action evidence is the behavioural core.
  - Scorecards are safer when they report evidence levels and remediation instead of badge-style certification.
  - Goose is plausible as a future target, but only after mock harness and trace schema gates.
- **Reusable fragments**:
  - `scenario.schema.json` and 24 examples.
  - `tool_trace.schema.json` and mock trace records.
  - `agt-agentic-controls.csv` and candidate OpenCRE relation vocabulary.
  - `scorecard_report.json` with `certification_claim=false`.
  - Promotion split in `s8-promotion/`.
- **Final experiment-level exit state**: `promote_to_runbook`
