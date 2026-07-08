---
name: agt-redteam-benchmark-consolidation
created: 2026-07-08
status: proposal-brief
tla_required: false
source: attached proposal plus repo read-pass
---

# AGT Red Team Benchmark Consolidation

## The pain
An engineer responsible for assessing an AI agent currently has two useful but
separate evidence systems in this repo: a 44,800-row detector corpus and a
scenario harness that records action-level outcomes. On the day they need to
answer "did the agent merely detect the attack, or did it actually contain the
dangerous action?", the current split forces them to compare incompatible
schemas and evidence levels by hand.

## Five capabilities the user described without realizing
- Map corpus attack families to Agent Traps trap classes and delivery vectors.
- Reuse the corpus as a payload dimension of parameterized scenarios instead of
  cloning one scenario per corpus row.
- Preserve two evidence tiers: L1 static detector evidence for broad coverage
  and L3 live sandbox evidence for sampled action outcomes.
- Report joint detection x action outcomes, especially the off-diagonal cells
  `undetected -> contained` and `detected -> executed`.
- Keep benchmark releases hash-frozen, leakage-checked, raw-free, and clearly
  non-certifying.

## Top risks
- **Breach**: Raw attack payloads, live-looking URLs, credentials, or PII leave
  the repo boundary through generated reports, AgentBus messages, GitHub issue
  text, or scorecards.
- **Compliance fine**: A public or upstream artifact implies certification,
  real-traffic validation, or production safety without the required evidence;
  this is especially risky under AI governance and procurement review.
- **Prolonged outage**: A live L3 run executes too many scenario x payload
  combinations or loses sandbox containment, exhausting model quota or running
  unsafe tool effects before the assessing engineer notices.

## Approach A - conservative
- **Effort**: 2-3 person-weeks.
- **Wedge**: Crosswalk plus one family end-to-end using indirect injection and
  a small stratified payload sample.
- **Risks**: May not expose all Agent Traps gaps yet; safest path for schema and
  evidence discipline.

## Approach B - full benchmark consolidation
- **Effort**: 4-6 person-weeks.
- **Wedge**: Crosswalk, schema extension, L1 full-corpus tier, L3 stratified
  tier, benign utility arm, and joint scorecard.
- **Risks**: Sampling design and live adapter cost can sprawl without hard caps.

## Approach C - local analysis only
- **Effort**: 1-2 person-weeks.
- **Wedge**: Metadata-only report joining existing detector artifacts to
  scenario taxonomy without changing the harness.
- **Risks**: Does not prove action containment and keeps the most important
  benchmark claim untested.

## Recommendation
Use Approach B, but force it through a five-milestone runbook with an Approach A
entry wedge. The smallest complete value slice is: indirect injection payloads
flow through parameterized scenarios, produce L1 detector outcomes and sampled
L3 action outcomes, and render the joint matrix with evidence levels and hashes.

## Success thesis
- **Leading metric**: A fresh assessing engineer can run one front-to-end smoke
  command and obtain a joint detection x action scorecard with no raw payload
  leakage and no evidence-level ambiguity.
- **Lagging metric**: The benchmark becomes the durable AGT red-team evidence
  path for evaluating detector, normalizer, provenance, sandbox, and utility
  changes before upstream claims.
- **Guardrails**: No L1 result is labeled as L3; no live run executes without an
  OS-enforced sandbox; no generated public artifact includes raw payload text or
  certification language.
- **Review window**: First readout after the one-family end-to-end slice; full
  readout after the stratified L3 sample is fixed and run.
- **If it misses**: Technical miss if the schema cannot represent payload refs
  and joint outcomes; methodology miss if leakage/sample bars fail; weak-demand
  miss if engineers do not use the joint matrix to make decisions.

## Open questions for /slo-research
1. Which existing AI-agent and prompt-injection benchmarks are closest, and what
   gap remains for a joint detector x action-outcome benchmark?
2. Which standards or governance references should shape the trap taxonomy,
   evidence levels, and non-certification language?
3. What repo-local artifacts already implement scenario validation, L2/L3
   evidence, round-7 measurement, and licensed reality-check intake?
4. What hard failure bars make the benchmark honest enough to run before
   upstream AGT claims?
