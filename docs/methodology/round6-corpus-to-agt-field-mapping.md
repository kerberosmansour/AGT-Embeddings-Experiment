# Round-6 corpus → AGT runtime field mapping (Gate 2 tier definitions)

Status: M4 methodology guardrail. Defines how the frozen corpus's governance
columns are coarsened to the vocabulary AGT (microsoft/agent-governance-toolkit)
actually exposes at a runtime decision point, so the Gate-2 ablation measures
"what a real deployment would have" rather than synthetic ground truth.

`expected_action` and `risk_level` are ground-truth annotations and are
**forbidden** as Gate-2 features (asserted in code and validator). They never
appear below.

## What AGT provides at a decision point (verified against the codebase)

The richer `policy-engine/` ("ACS") core builds a policy input at intervention
points (`pre_tool_call`, `post_tool_call`, `input`, …). Dependable fields:

| AGT runtime field | Source in AGT | Reliability |
|---|---|---|
| `tool_call.{name,args}` present | `pre_tool_call` snapshot | **guaranteed** — AGT is invoked because an action is requested |
| `input.source ∈ {user, webhook, scheduled, other}` | input snapshot | always present, coarse |
| interception point = tool_result | `post_tool_call` | always derivable |
| `tool.clearance`, `tool.security_labels` | manifest `tools` section | **operator-configured; no built-in catalog** |
| `ifc.source_labels` | host-supplied | integration-dependent; absent unless instrumented |
| `prior_decisions`, actor track record | host-supplied | **absent** by default (core is stateless) |

## Tier definitions

### Floor — what every AGT deployment has for free
- `requires_tool_call` (bool) ← corpus `requires_tool_call`. AGT always knows
  whether a tool call is being requested.
- `coarse_source ∈ {user, tool_result, other}` ← derived from corpus
  `source_type` + `trust_level`, collapsed to AGT's `input.source`-style
  vocabulary:
  - `tool_result` if `source_type == "tool_result"` or `trust_level == "tool_output"`
  - `user` else if `trust_level == "authenticated_user"` or `source_type == "user"`
  - `other` otherwise

### Ceiling — adds integration-dependent fields
- `contains_sensitive_sink` (bool) ← corpus `contains_sensitive_sink`
  (≈ operator-configured manifest `clearance`/`security_labels`).
- full `source_type` (6-way: user / document / rag_chunk / ticket / tool_result
  / memory) ≈ host-supplied IFC `source_labels`.

### Control — no metadata (calibrated score only).
### Rule — deterministic, zero-parameter: `requires_tool_call ∧ coarse_source ≠ user` → flag.

## Fail-closed semantics (mirrors AGT IFC, which fails closed on missing labels)

When a field is **absent** at runtime (not merely a known value):
- missing `trust_level`/`source_type` → `coarse_source = other` (least trusted)
- missing `contains_sensitive_sink` → treated as **sensitive** (True)

Each fail-closed substitution emits a counted `fail_closed` tag in the run
provenance. A field carrying an **unknown value** (not in the corpus vocabulary)
is a hard error — unknown ≠ absent.

## PR2 integration appendix (not built this round)

The shipping shape is an AGT `AnnotatorDispatcher` emitting
`annotations.gate2.score`, gated by a Rego policy modelled on the stock
`confidence.rego` (deny/escalate below threshold). The embedding/head score and
the Gate-2 decision attach as `Evidence` on the verdict for auditability. No
new `PolicyDecision` variant is introduced; `escalate`/`requires_approval`
carries the uncertain-lane routing.
