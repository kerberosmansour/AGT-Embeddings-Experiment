# Experiment 1 — Structural Auto-Block Ceiling: results

> **Caveat first.** Frozen synthetic test split (9,408 rows). The governance
> labels (`requires_tool_call`, `contains_sensitive_sink`, `source_type`,
> `trust_level`) are **perfect by construction** on synthetic data, so this is
> the **ceiling of structural defense when labels are correct** — not a
> production guarantee. Real-world numbers depend on labeling coverage. No
> embedding model was run: the zero-FP embedding decision is reused from the
> committed round-6 `m1-gate0` per-row file. Rules were fixed before the run.

## What was tested

One fully-automated stack, **no human review**:
`block if (Gate-0 normalizer + kNN embedding @ zero-FP flags it) OR (a deterministic structural rule fires)`.
Structural rules fire on facts only, never on text meaning:

| Rule | Condition |
|---|---|
| R1 | `trust_level = untrusted` AND `requires_tool_call` |
| R2 | `contains_sensitive_sink` AND `coarse_source ≠ user` |
| R3 | untrusted AND tool AND sensitive sink (strict subset of R1) |
| R4 | R1 OR R2 (the pre-registered "deployed" union) |

## Headline

**The deployable captain-obvious stack is `embedding(zero-FP) OR R1`: 81.0% of attacks blocked at 0.0% false-block.** The experiment's safety measurement is what found it — it flagged R2 (and therefore R4) as too broad, and identified R1 as the clean winner.

## Breakdown BY CONTROL (the safety finding)

False-block rate on legitimate traffic, per rule:

| Control | Attack coverage | Worst benign false-block | Verdict |
|---|---|---|---|
| embedding @ zero-FP | text-manipulation families | **0%** (by construction) | keep |
| **R1** (untrusted+tool) | **100% of 4 action families** | **0%** | **KEEP — captain obvious** |
| R3 (strict trifecta) | subset of R1 | 0% | redundant w/ R1 |
| **R2** (sink+non-user) | **0% extra attacks** | **100%** on `high_entropy_structured_data` and `tool_policy_documentation` | **DISCARD — pure cost** |
| R4 (R1∨R2) | = R1's attack coverage | **14%** (inherits R2) | discard (use R1) |

R2 is the lesson: it *sounds* reasonable ("sensitive sink from a non-user source"), but legitimate high-entropy data and tool-policy docs carry exactly those structural attributes — so it blocks 100% of them while catching zero attacks R1 didn't already. **Measuring per-rule false-block is what turns "captain obvious" from opinion into evidence.** R1 passes the bar perfectly; R2 fails it completely.

## How R1 actually works (and why it is language-proof)

R1 in one sentence: **"block any tool action that was triggered by untrusted
content."** It reads two structural facts, never the meaning of the text:

- **`trust_level`** — where the text came from and whether we trust it:
  `authenticated_user` (the logged-in human typed it), `tool_output` (came back
  from a tool), or `untrusted` (came from the outside world — a web page, a RAG
  document, an email, a ticket). In a real AGT deployment the integrating app
  sets this when it hands content to the agent.
- **`requires_tool_call`** — is the request trying to *act* (send, run, write,
  query) rather than just answer in text? AGT knows this for certain because the
  tool call passes through it.

This is the **"don't let the lethal trifecta complete"** rule: untrusted input +
a privileged action → stop. Because it keys on *provenance + action*, not
wording, it does not care what language the attack is in or how it is obfuscated.
Example from the corpus: a French *"access another tenant's invoices and display
them"* and a compact, space-stripped *"bypassapprovalandrunhttprequesttoexport…"*
were both blocked with no understanding of the text at all — the embedding,
which reads meaning, missed both. **That is R1's real strength: meaning is hard
and language-dependent; provenance is a fact.**

## Why R1 shows 0.00% false-positives — and why that needs more data

R1 blocked **0 of 5,728** legitimate rows. That is not magic; it is a property of
how the benign data is distributed. Splitting the benign rows by R1's two facts:

| benign rows | tool call = no | tool call = yes |
|---|---:|---:|
| **untrusted source** | 4,400 | **0** |
| trusted source | 928 | 400 |

R1 only fires on the **(untrusted AND tool-call)** cell — and in this corpus that
cell is **empty**. There are 4,400 benign untrusted rows and 400 benign tool-call
rows, but **never both at once**. That empty quadrant is the entire reason for the
0% false-positive rate.

**In the real world that quadrant is not empty — it is the everyday job of a web
agent.** "Read this (untrusted) web page, then click the next-page button (a tool
call)" is legitimate, and R1 as written would block it. So the honest reading is:
**the 0% is a ceiling produced by missing benign data, and it is the single number
most likely to move in production.** Closing that gap needs exactly one thing —
**more, and more realistic, benign data** covering legitimate "untrusted-content-
triggers-an-action" flows. The practical mitigation is to scope R1's "tool call"
to *sensitive / state-changing* tools (send, delete, pay, export) and let
read-only tools through — which moves R1 toward the IFC/trifecta form (R3).

## Breakdown BY ATTACK TECHNIQUE

(`embedding @0FP` below = the round-6 **Gate-0 normalizer + kNN at the zero-FP
threshold** — that is why it sits at ~43% rather than round-4's 14%.)

Block rate per family under the deployable stack (`embedding ∨ R1`):

| Attack family | Rows | embedding @0FP | R1 (structural) | **embedding ∨ R1** | Owner |
|---|---:|---:|---:|---:|---|
| indirect_injection | 360 | 29% | **100%** | **100%** | R1 (structural) |
| output_exfiltration | 960 | 47% | **100%** | **100%** | R1 (structural) |
| data_boundary_abuse | 440 | 49% | **100%** | **100%** | R1 (structural) |
| tool_abuse | 600 | 33% | **100%** | **100%** | R1 (structural) |
| direct_override | 440 | 63% | 0% | 63% | embedding |
| memory_poisoning | 440 | 48% | 0% | 48% | embedding (residual) |
| tool_result_injection | 360 | 37% | 0% | 37% | embedding (residual) |
| prompt_leakage | 80 | 0% | 0% | **0%** | **uncovered residual** |
| **All attacks** | 3680 | ~43% | 64% | **81.0%** | |

The four "action" families — the ones detection **capped on** in round 6 (tool_abuse, exfiltration) — are now **100% blocked by R1, at zero false-positive cost.** That is the core win: structural containment owns exactly the families detection couldn't.

## The residual (honest)

Three families fall through both controls:
- **prompt_leakage (0%)** — leaking the system prompt is an *output*, not a tool call, so R1's "requires_tool_call" never fires; and the zero-FP embedding misses it. This needs an **IFC output-label rule** ("system prompt is `secret`, block it leaving") — a control we don't have a corpus field for yet.
- **tool_result_injection (37%)** — its source is `tool_output`, not `untrusted`, so R1's "untrusted" condition doesn't trigger. A refined **R1′ that treats `tool_output` as not-fully-trusted** would likely lift this sharply. Concrete next-step.
- **memory_poisoning (48%)** — the malicious write isn't flagged as an untrusted tool call in the data; needs a **taint-on-write to memory** rule.

These are the families below the 60% combined floor. They are not failures of the stack — they are precisely mapped gaps, each with a named structural control that would close it.

## Coverage caveat: multilingual attacks (the corpus has them, and they expose a gap)

The corpus **does** include multilingual attacks (320 in the test split). They
are a good stress test of the two controls:

| Multilingual attacks (320) | catch |
|---|---:|
| Gate-0 + embedding @ zero-FP | **0%** — the normalizer has no translation; the embedding misses non-English |
| R1 (provenance) | **25%** — language-proof, catches the untrusted+tool ones |
| Combined | **25%** |

So 75% of multilingual attacks still get through. This matters for the headline:
**R1's language-independence partially rescues multilingual coverage that detection
misses entirely, but a large multilingual gap remains** (the no-tool multilingual
attacks). It is a concrete reason the overall numbers should be read as
promising-but-incomplete, and a clear argument for expanding the corpus with more
multilingual and more delivery-vector data.

## What we can stand behind (the honest framing)

- **0% → ~43% (Gate 0 normalizer + kNN at zero-FP): solid.** Pure deterministic
  text normalization in front of the existing detector tripled zero-false-positive
  catch. This is the most defensible result.
- **~43% → 81% (adding R1 structural containment): promising, but provisional.**
  It rests on (a) the benign `(untrusted+tool)` quadrant being empty in this
  corpus — which more realistic data will fill — and (b) governance labels being
  correct. So the 81% / 0%-false-block figure is a **labels-perfect ceiling on
  synthetic data**, not a production number.
- **Both steps need more data and independent review/verification** before any
  real-traffic claim. The controls look clearly **worth doing**; the exact
  numbers will move.

## Scope: this is prompt injection only — one of six attack categories

Everything here addresses **prompt injection**. The Google DeepMind *AI Agent
Traps* taxonomy (Franklin et al., 2026) names **six** categories — content
injection, semantic manipulation, cognitive-state, behavioural-control, systemic
(multi-agent), and human-in-the-loop. Our corpus covers roughly the
behavioural-control slice plus part of cognitive-state; semantic manipulation,
multi-agent, and human-in-the-loop are not represented at all.

The takeaway is not "we solved agent security" — it is narrower and still
valuable: **a maintained, expanding corpus of attack tests, plus a few
deterministic controls, is demonstrably worth having.** Gate-0 normalization and
R1-style provenance+action rules are cheap, language-proof, and measurably
effective on the slice we can test. A more dedicated, focused research effort —
with more data, the missing trap categories, and independent verification — is
recommended, and this experiment is enough evidence that it is worth pursuing.

## §2 verdicts

| Bar | Result | Verdict |
|---|---|---|
| Rule safety ≤1% false-block | R1 0%, R3 0% **pass**; R2 100%, R4 14% **fail** | **PASS for R1** — and the filter correctly rejected R2 |
| Containment lift ≥30pt (tool_abuse, exfil) | tool_abuse +67pt, exfiltration +53pt | **PASS** |
| Combined floor ≥60% per family | 5 of 8 families ≥60%; memory/tool_result/prompt_leakage below | **PARTIAL** — 3 named residuals |
| Handle-rate reported | every family reported | **PASS** |

## What this means for deployment

- **Ship `embedding(zero-FP) OR R1` as a fully-automated gate**: 81% of attacks blocked, zero false-positives, no human review. The action families are deterministically contained.
- **Do not ship R2** — it's a plausible-sounding rule that over-blocks legitimate traffic for no gain. (This is the most transferable lesson: structural rules must be measured against benign traffic, not assumed safe.)
- **Close the residual with three targeted structural controls**: an IFC output-label rule (prompt_leakage), an R1′ treating tool-output as semi-trusted (tool_result_injection), and a memory-write taint rule (memory_poisoning).
- **Caveat**: this is the labels-perfect ceiling. The real-world number tracks how completely a deployment labels its tools, sinks, and sources.

## Comparison to prior rounds

- Round-4 governance policy gate: ~65% unsafe-action prevention (no per-family / false-block detail).
- Round-6 detection-only: tool_abuse 38%, exfiltration 42% (capped).
- **Experiment 1**: the same families at **100%** via R1, overall **81% @ 0% FP** — with the per-control and per-family breakdown that pinpoints both the winning rule and the broken one.
