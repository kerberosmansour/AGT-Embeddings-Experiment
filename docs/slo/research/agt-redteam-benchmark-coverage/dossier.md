---
name: agt-redteam-benchmark-coverage
researched: 2026-06-19
incomplete: false
research_mode: repo-local SLO research, not market research
---

# Research Dossier — AGT Red Team Benchmark Coverage Expansion

## Purpose

This dossier answers the founder question: how do we make the AGT Red Team benchmark more thorough without turning it into a bloated corpus that is expensive, noisy, or hard to maintain?

The answer is a two-tier benchmark:

1. Keep the current **24-scenario smoke suite** as the fast reproducibility / CI guard.
2. Add a **120-scenario core measurement suite** for catch-rate, evasion catch-rate, and false-positive measurement.

This is the Goldilocks starting point: enough rows to measure control behaviour by trap class and benign-vs-adversarial outcome, but not a Cartesian explosion across every possible surface/model/tool combination. It is **not** a hard ceiling. If a specific control, evasion family, or false-positive cell is underpowered, the suite should grow with targeted extension packs rather than being forced into 120 rows.

## Source artifacts used

- Current benchmark scenarios: `benchmarks/agent-redteam/scenarios/*.json`
- Scenario schema: `benchmarks/agent-redteam/schema/scenario.schema.json`
- Controls: `benchmarks/agent-redteam/controls/agt-ac.csv`
- OpenCRE relations: `benchmarks/agent-redteam/controls/opencre/relations.csv`
- Runbook: `docs/RUNBOOK-agt-redteam-agent-traps-opencre.md`
- Experiment book: `docs/slo/experiments/agt-redteam-agent-traps-opencre/EXPERIMENT.md`
- M6 completion evidence: `docs/slo/completion/agtrt-m6.md`
- Founder-supplied OWASP Agentic Scorecard draft (`pasted-text.txt`, 2026-06-19), especially its three-tier static/mock/live architecture, AIVSS/ASI signal map, and explicit static-vs-behavioural gap analysis.
- Prior-art pointers from that draft: AgentDojo, AgentThreatBench / `inspect_evals`, Promptfoo OWASP Agentic plugin suite, and the prompt-injection corpus pattern of testing evasive variants rather than only canonical attacks.

## Current benchmark shape

Current seed benchmark:

| Property | Current state |
|---|---|
| Total scenarios | 24 |
| Trap classes | 6 |
| Rows per trap class | 4 each |
| Target layers | 6 (`input`, `browser`, `memory`, `tool`, `a2a`, `human_approval`) |
| Delivery surface | all rows use `synthetic_fixture` |
| Stateful rows | 8 of 24 |
| Multi-agent rows | 4 of 24 |
| Controls covered | 15 AGT-AC controls |
| Evidence supported | L1 static, L2 mock, one L3 live proof |

Trap-class distribution:

| Trap class | Rows |
|---|---:|
| Content Injection | 4 |
| Semantic Manipulation | 4 |
| Cognitive State | 4 |
| Behavioural Control | 4 |
| Systemic | 4 |
| Human-in-the-Loop | 4 |

This is balanced as a **seed**, but it is not enough for stable catch-rate or false-positive measurement.

## The coverage gap

The current 24 rows prove that the benchmark format works. They do not yet prove that a detector/control has a reliable catch rate.

The main gaps are:

1. **No clean false-positive denominator.** There are a few hard-benign ideas, but the suite is mostly trap-positive. To measure false positives, every trap class needs benign and near-miss rows.
2. **Delivery surfaces are under-varied.** Everything is a synthetic fixture. The schema can represent browser, memory, tool, A2A, and human approval flows, but the corpus needs more surface variation.
3. **Controls are covered, but not stressed.** Each AGT-AC appears, but there are not enough independent examples per control to estimate per-control recall or precision.
4. **L3 is proven but thin.** M6 produced one real-agent L3 trace. That proves the path, not the distribution.
5. **OpenCRE relations are candidate-honest.** The mapping mechanism exists, but all effective relations are `candidate` until backed by committed OpenCRE references.

## Goldilocks recommendation

### Tier 1 — keep the current 24-row smoke suite

Purpose:

- CI and quick local confidence.
- Proves schema, harness, reporter, hygiene, OpenCRE validator, and product render still work.
- Should stay small and fast.

Do not grow this too much. It is the smoke test, not the measurement corpus.

### Tier 2 — start with a 120-row core measurement suite

Recommended shape:

| Per trap class | Count | Purpose |
|---|---:|---|
| Adversarial positives | 12 | Catch-rate denominator: did the control detect/block/contain the trap? |
| Hard-benign negatives | 4 | False-positive denominator: should not block or flag. |
| Near-miss / ambiguous negatives | 4 | Calibration: checks if controls overfit keywords or superficial features. |
| **Total per class** | **20** | Enough for directional per-class metrics without corpus bloat. |

Core total: **6 trap classes × 20 = 120 scenarios**.

Why 120?

- 24 is too small for catch-rate/FP measurement.
- 120 gives every class a first real positive, evasion-positive, and negative denominator.
- 120 is still small enough to run in CI/nightly and review manually.
- It avoids pretending we can exhaustively enumerate the agent-trap space.

Why 120 may not be enough:

- It supports directional class-level measurement; it does **not** guarantee statistically stable per-control × per-evasion-family estimates.
- Some AGT-AC controls span multiple trap classes, so a fixed 20-per-class layout can still leave individual controls thin.
- Some evasion families are more important for certain classes than others; forcing equal allocation can hide risk.
- If a control's canonical catch rate is high but evasion catch rate is unstable or low, the benchmark needs more evasion rows for that control family.

### Expansion rule: targeted packs, not benchmark sprawl

Do not grow the benchmark just to feel more thorough. Grow it when the evidence says a metric cell is underpowered.

Use this rule:

| Trigger | Action |
|---|---|
| A reported control has fewer than 5 positive rows | Add a targeted positive pack for that AGT-AC control. |
| A reported control has fewer than 3 hard-benign / near-miss rows | Add negative calibration rows before reporting FPR for that control. |
| Evasion degradation is high or noisy | Add a targeted evasion pack for that trap class/control pair. |
| A new evasion family appears in prompt-injection / agentic prior art | Add it to the research bank first; promote only after review. |
| L3 result disagrees with L2 mock result | Add a focused live-sampling pack before making broad claims. |

Recommended extension pack size: **+10 rows per trap class or control family** (6 canonical/evasion positives, 2 hard-benign, 2 near-miss). This keeps additions reviewable while avoiding a square-peg/round-hole 120-row cap.

### Important correction: evasion resistance must be designed in

The 120-row suite is **not** automatically enough to measure whether controls are effective against evasion techniques. It is enough only if the positive rows are deliberately stratified.

Per trap class, the recommended 20 rows should be:

| Per trap class | Count | Purpose |
|---|---:|---|
| Canonical trap positives | 4 | Baseline catch rate against straightforward attacks. |
| Evasion trap positives | 8 | Evasion catch rate: same control intent, but with obfuscation, staging, delegation, laundering, or camouflage. |
| Hard-benign negatives | 4 | False-positive denominator for legitimate security-looking content. |
| Near-miss / ambiguous negatives | 4 | Calibration denominator for superficial-keyword overfitting. |
| **Total per class** | **20** | Directional recall, evasion robustness, and precision without corpus bloat. |

This changes the interpretation of the earlier `12 adversarial positives` row: those 12 must be **4 canonical + 8 evasion-positive**, not 12 undifferentiated positives.

Without this split, a control could look good on the 120-row suite while still failing under simple evasive transformations.

### Tier 3 — optional research bank / extension packs, not CI

Optional later bank:

- 180-240+ rows, generated and curated over time as evidence demands.
- Used for model comparisons, live L3 sampling, and upstream research.
- Not the primary acceptance gate.

## Measurement design

The benchmark should report these metrics:

| Metric | Meaning |
|---|---|
| Trap catch rate | Of trap-positive scenarios, how often did the expected control detect/block/contain the attempt? |
| Canonical catch rate | Catch/block/contain rate on direct trap positives. |
| Evasion catch rate | Catch/block/contain rate on evasion-positive variants. |
| Evasion degradation | Difference between canonical and evasion catch rates; high values identify brittle controls. |
| False-positive rate | Of hard-benign / near-miss scenarios, how often did the benchmark incorrectly flag or block? |
| Utility-preservation rate | Hard-benign rows that complete without spurious blocking. |
| Attempt visibility | Unsafe attempt appears as `attempted:true`, even when blocked. |
| Containment effectiveness | Unsafe attempted actions have `executed:false` and a non-null `blocked_at`. |
| Control coverage | Which AGT-AC controls were exercised, and at which evidence level. |
| Evidence mix | Counts by `L1_static`, `L2_mock_behavioural`, and `L3_live_behavioural`. |

The key reporting principle stays unchanged: evidence levels, not certification.

## Scenario-design rules

Each new scenario should be one atomic test card:

1. One primary trap class.
2. One primary expected control family.
3. One expected outcome: positive, hard-benign, or near-miss.
4. One evidence target: L1, L2, or L3-eligible.
5. Raw-free synthetic content only.
6. Explicit human-visible vs agent-visible view where relevant.
7. Explicit session model: single-turn, multi-turn, cross-session, or multi-agent.
8. Deterministic expected trace semantics: attempted, executed, blocked_at, evidence_level.

## Proposed core 120-row allocation

| Trap class | Canonical positive | Evasion positive | Hard-benign | Near-miss | Total |
|---|---:|---:|---:|---:|---:|
| Content Injection | 4 | 8 | 4 | 4 | 20 |
| Semantic Manipulation | 4 | 8 | 4 | 4 | 20 |
| Cognitive State | 4 | 8 | 4 | 4 | 20 |
| Behavioural Control | 4 | 8 | 4 | 4 | 20 |
| Systemic | 4 | 8 | 4 | 4 | 20 |
| Human-in-the-Loop | 4 | 8 | 4 | 4 | 20 |
| **Total** | **24** | **48** | **24** | **24** | **120** |

This table is the **core suite**, not the final word. The benchmark should preserve this core for stable comparisons, then add named extension packs when specific controls or evasion families need more rows.

## Evasion technique axis

The founder-supplied Agentic Scorecard draft makes a critical point: agentic testing needs more than static repository signals and more than single-turn attack generation. It needs static, mock-behavioural, and optional live tiers, and it needs to measure whether controls survive evasion. That matches the lesson from the prompt-injection corpus: canonical payloads are not enough.

Add this field to the measurement-suite schema or metadata:

```yaml
scenario_kind: canonical_positive | evasion_positive | hard_benign | near_miss
evasion_technique: none | encoding_obfuscation | indirection | multi_turn_staging | tool_result_laundering | memory_trigger | a2a_relay | authority_camouflage | benign_camouflage | paraphrase
```

Suggested evasion families:

| Evasion family | Applies most directly to | What it tests |
|---|---|---|
| Encoding / format obfuscation | Content Injection, Behavioural Control | Whether controls catch transformed instructions, not just plain text. |
| Indirection / retrieval laundering | Content Injection, Cognitive State | Whether a harmful instruction hidden behind a source/tool/result boundary is still controlled. |
| Multi-turn staging | Semantic Manipulation, Cognitive State, Human-in-the-Loop | Whether a trap split across turns bypasses single-message checks. |
| Tool-result laundering | Behavioural Control, Systemic | Whether the agent trusts an untrusted tool result that asks for a follow-on action. |
| Memory trigger / delayed activation | Cognitive State | Whether poisoned memory only becomes dangerous later. |
| A2A relay / delegation spoof | Systemic | Whether control survives agent-to-agent propagation. |
| Authority / approval camouflage | Human-in-the-Loop | Whether fake approval or role pressure bypasses the human gate. |
| Benign camouflage | All classes | Whether a trap embedded in mostly legitimate content evades keyword rules. |
| Paraphrase / linguistic variation | All classes | Whether controls catch intent rather than exact wording. |

The acceptance bar should be:

1. A control is not considered effective unless it has acceptable canonical catch rate **and** acceptable evasion catch rate.
2. A control is not considered usable unless its hard-benign / near-miss false-positive rate stays low.
3. The report must show canonical-vs-evasion degradation explicitly.
4. L3 live runs should sample both canonical and evasion-positive rows, not only the easiest canonical rows.

## Class-specific expansion targets

### Content Injection

Add variants for:

- HTML comments.
- CSS hidden/offscreen text.
- ARIA-label mismatch.
- Markdown link masking.
- PDF/document hidden layer.
- Human-visible safe / agent-visible unsafe splits.

False-positive rows should include benign hidden metadata and accessibility labels that should not trigger a block.

### Semantic Manipulation

Add variants for:

- Goal reframing.
- Ambiguous delegation.
- Instruction-priority confusion.
- Hard-benign security docs.
- Conflicting but non-malicious documentation.

False-positive rows should stress legitimate policy/security text that should not be treated as an attack.

### Cognitive State

Add variants for:

- Memory write poisoning.
- Memory readback poisoning.
- RAG provenance poison.
- Cross-session recall.
- Stateful preference poisoning.

False-positive rows should include legitimate user preferences and benign memory updates.

### Behavioural Control

Add variants for:

- Shell/tool abuse.
- Tool-result injection.
- Output exfiltration.
- Package hallucination.
- Sensitive-data egress requests.

False-positive rows should include safe dry-runs and legitimate package/tool lookups.

### Systemic

Add variants for:

- A2A spoofing.
- MCP registry spoofing.
- Subagent blast-radius widening.
- Prompt relay across agents.
- Delegation boundary confusion.

False-positive rows should include legitimate delegation and verified MCP/tool registry entries.

### Human-in-the-Loop

Add variants for:

- Approval fatigue.
- Fake manager approval.
- Irreversible-action pressure.
- Human-visible safe / agent-visible unsafe approvals.
- Missing audit trail on approval.

False-positive rows should include legitimate approvals and reversible low-risk actions.

## Methodology guardrails

To avoid the benchmark becoming theater:

1. Freeze the core 120-row measurement suite once accepted.
2. Keep separate named extension packs for extra rows, e.g. `content-injection-evasion-pack-01` or `a2a-spoofing-pack-01`.
3. Do not tune controls on the measurement suite and then report those numbers as evaluation.
4. Report confidence honestly: 120 rows are enough for directional class-level rates, not definitive model rankings or every per-control/evasion-family estimate.
5. Keep false positives first-class, not an afterthought.
6. Keep raw payloads out; test the structure of traps, not copy real dangerous content.
7. Require every new row to validate against the schema before review.
8. Require every generated report to preserve `certification_claim:false`.

## Recommended next SLO step

Open a follow-up runbook or ticket series for **AGT Red Team Measurement Suite v2**:

1. M1: add scenario labels for `canonical_positive | evasion_positive | hard_benign | near_miss`, `evasion_technique`, and `measurement_suite` membership.
2. M2: author the core 120-row suite with BDD fixtures first: 4 canonical positives, 8 evasion positives, 4 hard-benign negatives, and 4 near-miss negatives per trap class.
3. M3: add an evidence-power check that flags undercovered control/evasion cells and recommends targeted extension packs when 120 is not enough.
4. M4: extend reporter metrics for canonical catch rate, evasion catch rate, evasion degradation, false-positive rate, and utility-preservation rate by class and AGT-AC.
5. M5: add calibration gates: hard-benign and near-miss rows must not fail by default.
6. M6: run L3 sampling over a small, representative slice that includes evasion-positive rows only after L2 gates are green.
