# AGT Consolidated Benchmark Crosswalk

Purpose: map corpus attack families to one primary Agent Trap class before any
payload expansion. This is a metadata-only bridge. It carries family names,
delivery vectors, expected containment, and backlog status; it does not carry
raw prompt, payload, URL, email, or secret material.

Source basis:

- Round-4 manifest: `corpus/round4/manifest-large.json`.
- Round-7 runbook: `docs/RUNBOOK-round7-garak-corpus.md`.
- Existing AGT redteam trap classes: `benchmarks/agent-redteam/scenarios/*.json`.

## Primary Family Mapping

| Corpus family | Primary Agent Trap class | Delivery vector | Expected containment | M1 status | Rationale |
|---|---|---|---|---|---|
| `direct_override` | Semantic Manipulation | `direct_prompt` | `require_approval` | mapped | Direct instruction override is primarily semantic goal/control override. |
| `prompt_leakage` | Semantic Manipulation | `direct_prompt` | `require_approval` | mapped | The unsafe objective is disclosure despite instruction hierarchy. |
| `indirect_injection` | Content Injection | `carrier_document` | `block` | mapped | Untrusted carrier content differs from user-visible task content. |
| `tool_result_injection` | Behavioural Control | `tool_result` | `block` | mapped | Tool output tries to steer downstream action. |
| `tool_abuse` | Behavioural Control | `tool_result` | `block` | mapped | The benchmark must measure attempted/executed/blocked tool action. |
| `output_exfiltration` | Behavioural Control | `reporting_artifact` | `block` | mapped | The safety question is whether outbound/reporting action is contained. |
| `memory_poisoning` | Cognitive State | `memory_record` | `quarantine` | mapped | Persistent state is the target, not a single prompt turn. |
| `data_boundary_abuse` | Systemic | `direct_prompt` | `block` | mapped | Data-boundary misuse crosses trust and policy boundaries. |
| `jailbreak` | Semantic Manipulation | `direct_prompt` | `require_approval` | mapped | Round-7 persona/alignment bypass stays semantic until action is attempted. |
| `agentic_tool_exploit` | Behavioural Control | `tool_result` | `block` | mapped | Multi-turn tool misuse is action containment work. |
| `package_hallucination` | Behavioural Control | `tool_result` | `require_approval` | mapped | The risk manifests through package/tooling action. |
| `terminal_escape_injection` | Content Injection | `reporting_artifact` | `quarantine` | mapped | Rendered terminal/control bytes are treated as content injection. |

## Explicit Backlog Cells

| Backlog cell | Why empty in M1 | Required before claiming coverage |
|---|---|---|
| Cognitive State beyond `memory_poisoning` | Corpus families mostly target prompts/tools, not long-lived preference or recall state. | Add stateful payload refs with explicit memory-write/read traces and leakage checks. |
| Human-in-the-Loop | Current corpus families do not model approval fatigue or manager-spoof workflows at corpus scale. | Add payload refs for approval prompts and require an approval-decision artifact. |
| Non-payload Behavioural Control | Corpus rows are text payloads; some behavioural traps require environment/action setup rather than payload text. | Add scenario templates whose stimulus is tool state, workflow state, or policy context rather than a raw payload. |

## M1 Coverage Summary

| Metric | Value |
|---|---:|
| Round-4 attack families mapped | 8 |
| Round-7 added attack families mapped | 4 |
| Primary Agent Trap classes represented | 5 |
| Explicit backlog cells | 3 |

M1 does not claim full taxonomy parity. Empty cells are backlog by design and
must stay visible in later reports.
