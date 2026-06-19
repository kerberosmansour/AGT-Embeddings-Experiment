# AGT Red Team ↔ OpenCRE Mapping Handoff

Public GitHub issue: https://github.com/kerberosmansour/AGT-Embeddings-Experiment/issues/35

This document is the companion write-up for issue #35. It is written in plain English so it can be shared with the OpenCRE team or other security-standard maintainers.

## What we set out to do

We built the AGT Red Team benchmark to measure whether an AI agent's control boundaries hold under realistic classes of agent failure. The benchmark is not trying to certify an agent. It is trying to produce reproducible evidence about what the agent attempted, what actually executed, what was blocked, and which control layer was involved.

The OpenCRE question is: can these agent-control requirements map cleanly to existing Common Requirements, or are there agent-specific gaps that should be contributed upstream?

## The six agent-trap classes

| Trap class | Plain-English meaning | Example failure |
|---|---|---|
| Content Injection | Hidden or transformed content changes what the agent sees compared with what a human sees. | Hidden HTML or ARIA text tells the agent to do something unsafe while the human sees benign text. |
| Semantic Manipulation | The task or instruction hierarchy is reframed so the agent drifts from the real goal. | A document reframes a safety instruction as obsolete or delegated away. |
| Cognitive State | Memory, RAG state, or persisted preferences are poisoned or misused across turns/sessions. | A malicious memory write changes later behaviour. |
| Behavioural Control | The agent is pushed into unsafe tool use, exfiltration, package hallucination, or misleading tool results. | A shell/tool request attempts an unsafe action. |
| Systemic | Multi-agent, MCP, A2A, or delegated-agent boundaries are spoofed or widened. | A fake subagent or MCP registry entry expands authority. |
| Human-in-the-Loop | Approval, fatigue, fake authority, or irreversible-action pressure attacks the human gate. | The agent treats a fake manager approval as sufficient. |

## Current benchmark state

The current benchmark has:

- 24 scenarios total.
- 4 scenarios per trap class.
- 6 target layers: `input`, `browser`, `memory`, `tool`, `a2a`, `human_approval`.
- 15 AGT-AC controls.
- Evidence levels: `L0_declared`, `L1_static`, `L2_mock_behavioural`, `L3_live_behavioural`.
- One live L3 run where a real agent attempted a tool action and the OS sandbox contained it.

Every report carries `certification_claim: false`.

## The AGT-AC controls

| Control | Name | Current OpenCRE relation intent |
|---|---|---|
| AGT-AC-001 | Source Boundary and Provenance | broad |
| AGT-AC-002 | Instruction Hierarchy Integrity | related |
| AGT-AC-003 | Hidden Content and Render/Parse Divergence Detection | candidate |
| AGT-AC-004 | Tool Capability Boundary Enforcement | broad |
| AGT-AC-005 | Sensitive Data Egress Control | broad |
| AGT-AC-006 | Human Approval for Irreversible Actions | related |
| AGT-AC-007 | Memory Write/Read Integrity | candidate |
| AGT-AC-008 | RAG Source Traceback and Poisoning Detection | candidate |
| AGT-AC-009 | MCP and Tool Supply-Chain Verification | broad |
| AGT-AC-010 | A2A Delegation and Message Integrity | candidate |
| AGT-AC-011 | Audit Event Completeness | broad |
| AGT-AC-012 | Raw Prompt Artifact Hygiene | related |
| AGT-AC-013 | Session and State Boundary Enforcement | candidate |
| AGT-AC-014 | Hard-Benign Must-Not-Block Coverage | related |
| AGT-AC-015 | Evidence-Level Reporting | candidate |

Important: those relation intents are not verified yet. The current validator downgrades any relation without a committed backing reference to `candidate`.

## Current OpenCRE mapping status

The benchmark uses this relation vocabulary:

- `exact`
- `broad`
- `narrow`
- `related`
- `candidate`

Current effective state:

- 15 AGT-AC controls have candidate OpenCRE targets.
- 0 relations are verified.
- 9 aspirational `broad` / `related` claims are downgraded because no committed OpenCRE backing reference exists yet.
- Effective result today: all 15 mappings are `candidate`.

This is deliberate. We would rather underclaim than imply OpenCRE endorsement or standards coverage we have not proven.

## Candidate agentic CRE gaps

These are the places where we are not sure whether OpenCRE already has a good home:

1. **Render/parse divergence for hidden content** — the security requirement that the system understand when a human-visible view and an agent-visible parsed view diverge.
2. **Agent memory write/read integrity and traceback** — the requirement to control and audit memory writes and later memory use.
3. **Agent-to-agent delegation and message integrity** — the requirement to authenticate delegation and prevent authority expansion across agent boundaries.
4. **Evidence-level reporting for agent-control benchmarks** — the requirement to distinguish declared, static, mock-behavioural, and live-behavioural evidence.

These may already map to existing CREs. If they do, we want to link them properly. If they do not, they may be candidate new requirements.

## What we want from the OpenCRE team

1. Point us to existing CRE IDs for each AGT-AC control where there is a good match.
2. Tell us whether the four candidate gaps above are real gaps or just poorly-mapped existing requirements.
3. Recommend relation strengths (`exact`, `broad`, `narrow`, `related`, `candidate`) for agent-specific controls that overlap with traditional secure-design controls.
4. Recommend the best contribution route for new agentic mappings or new CREs.
5. Recommend the right reproducible OpenCRE snapshot/export method for this benchmark.

## Current artifacts

- `benchmarks/agent-redteam/controls/agt-ac.csv`
- `benchmarks/agent-redteam/controls/opencre/relations.csv`
- `benchmarks/agent-redteam/controls/opencre/validate_relations.py`
- `docs/slo/research/agtrt-opencre-relations.md`

## Safety and wording boundaries

- This is not an OpenCRE endorsement claim.
- This is not a certification claim.
- No raw attack payloads, secrets, or private operational details are included.
- Public reports should continue to say: **evidence, not certification**.

## References

- OpenCRE public site: https://www.opencre.org/
- OWASP/OpenCRE repository: https://github.com/OWASP/OpenCRE
