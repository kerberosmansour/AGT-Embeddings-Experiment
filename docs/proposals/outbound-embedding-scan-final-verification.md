# Proposal - Outbound Embedding Scan As Final Verification Evidence

Issue: https://github.com/kerberosmansour/AGT-Embeddings-Experiment/issues/13

## Summary

Run the existing embedding/kNN detector pattern on outbound content as a
default-off, evidence-grade verifier at AGT output-side stages:

- `post_model_call`: model response or tool-call arguments before dispatch;
- `post_tool_call`: tool result before it is consumed, logged, or rendered;
- `output`: final assembled user-visible response.

This is not a deterministic safety boundary. Semantic output harms such as
harmful instructions, jailbreak-compliant answers, prompt leakage, or data
leakage should feed `Escalate`, `Warn`, review queues, or host-specific
transform workflows. They should not be reported as automatic structural blocks
unless a separate structural control can express the containment contract.

## Current Upstream Shape

Verified on June 12, 2026:

- AGT PR microsoft/agent-governance-toolkit#2991 is open and exposes shared
  normalization, but it is not merged and does not yet wire detector/policy
  surfaces.
- AGT `policy-engine/core/src/verdict.rs` supports `Decision::Escalate`,
  `Decision::Warn`, and bounded `Evidence` payloads, plus `Decision::Transform`
  for value-changing policies.
- This repo already has a metadata-only 2x2 harness in
  `meta/harness/round7-garak/` with validation-frozen thresholds, Wilson
  intervals, base-rate precision, and no raw text in artifacts.

## Control Classification

#13 is an **evidence** control, not a structural sanitizer.

| Control | Handles | Default decision role |
|---|---|---|
| #12 render sanitizer | byte/render hazards such as terminal controls | `Transform` when safely replaceable |
| #13 outbound embedding scan | semantic output risk and leakage evidence | `Escalate` / `Warn` / review |

Run #12 first at `post_tool_call` and `output` when the sink can render
terminal-control bytes. Then scan the sanitized body, using the full detection
normalizer only for the embedding view. The normalized text must remain
metadata-only and must not become user-visible output.

## Proposed AGT Flow

```text
stage target: post_model_call | post_tool_call | output
  -> select scan subject
       body/text fields only, no unrelated JSON metadata
       after #12 render sanitization when applicable
  -> detection normalizer
       normalized_text stays in memory only
       transform tags become metadata
  -> embedding/kNN scorer
       validation-frozen tau
       nearest-neighbor IDs/hashes only
  -> outbound evidence annotation
       stage, sink_type, subject_sha256, normalized_sha256
       score, tau, model_id, bank_id, transform tags
  -> policy
       Allow below tau
       Escalate/Warn above tau by default
       Transform only if a separate safe rewrite policy exists
       Deny only if host policy has an independent structural reason
```

Recommended reference-policy posture:

| Score state | Default verdict | Notes |
|---|---|---|
| below frozen tau | `Allow` | Attach optional low-risk evidence only if requested |
| above tau, final `output` | `Escalate` | Human/review routing or safe fallback response |
| above tau, `post_model_call` before tool dispatch | `Escalate` or `Deny` only if paired with a structural tool policy | Do not claim embedding alone is a block boundary |
| above tau, `post_tool_call` | `Warn`/`Escalate` | #12 should already have handled render bytes |

The evidence object must stay within AGT's 4 KiB bound. Large per-row evidence
belongs in offline artifacts addressed by hash or URI.

## Experiment Design

Question 1: does the inbound exemplar bank transfer to outbound content?

Question 2: if not, how much does an outbound-specific exemplar bank improve
visibility, and what review-load cost does it create?

Recommended matrix:

| Axis | Values |
|---|---|
| Stage | `post_model_call`, `post_tool_call`, `output` |
| Bank | inbound round-4 bank, outbound-specific bank |
| Normalization | old round-6 Gate-0, new AGT Rust round-7 |
| Corpus arm | synthetic outbound rows, payload-derived reality-check outbound rows |

The inbound bank is the transfer baseline. The outbound-specific bank is allowed
only if it is built with the same family/split discipline as round-7: no prompt,
conversation, source, or semantic family may straddle exemplar, validation, and
test.

## Outbound Corpus Shape

Do not reuse inbound prompts as outbound rows without relabeling the surface.
Outbound rows should look like the thing AGT would actually inspect at each
stage:

- final assistant responses;
- model-produced tool-call arguments or proposed actions;
- tool result text returned from untrusted sources;
- final assembled answer with citations, markdown, code, summaries, or refusal
  text.

Suggested attack labels:

| Outbound label | Source families |
|---|---|
| `harmful_completion` | jailbreak/direct-override responses that comply with a disallowed request |
| `secret_or_policy_leak` | prompt leakage, memory leakage, cross-tenant data leakage |
| `unsafe_tool_argument` | model-produced arguments that would trigger a risky action |
| `exfiltration_response` | output text that attempts to move data to an external sink |
| `tool_result_instruction` | untrusted tool output that asks the agent to change behavior |

Suggested benign controls:

- safe refusals and policy-grounded explanations;
- security education and quoted examples;
- normal tool summaries and status reports;
- harmless code snippets and dependency instructions;
- benign markdown with links/citations;
- sanitized terminal transcripts after #12 render cleanup;
- creative roleplay that does not cross the disallowed-content boundary.

Payload-derived rows from `corpus/round7/reality-check/` may be used only under
that arm's license, attribution, and redaction rules. Public reports should
publish aggregate counts, IDs, hashes, labels, and source licenses, never raw
payload text.

## Methodology Gates

Reuse the round-7 measurement discipline:

1. Family/source split: no `conversation_id`, source URL, prompt/response pair,
   semantic family, or payload-derived origin crosses splits.
2. Leakage checks at zero: exact normalized hash, near-duplicate similarity,
   semantic-family split leakage, plus outbound-stage subject hash leakage.
3. Threshold freeze: tau is fit on validation only and frozen before test.
4. Metrics: Wilson 95% intervals, base-rate precision at 100:1 and 1000:1,
   per-stage and per-benign-subclass FP rates, and review-load counts.
5. Paired deltas: compare inbound-bank vs outbound-bank and old-normalizer vs
   new-normalizer on the same frozen test subjects.
6. Cost: record embedding calls, characters scanned, cache hit rate, p50/p95
   latency, and throughput impact per stage.
7. Metadata-only artifacts: no `text`, `prompt`, `content`, raw response body,
   normalized text, raw URL, or raw email values in artifacts or public issue
   comments.

## Accept / Kill

Accept as useful evidence if:

- artifacts validate as metadata-only;
- validation-frozen thresholds are used;
- outbound scanning finds new visibility in at least one output-side family or
  stage without hiding the FP/review-load cost;
- the report clearly distinguishes transfer baseline from outbound-specific
  training.

Flag, but do not fail, if the inbound bank transfers poorly. That is the point
of the experiment.

Kill or redesign if:

- embedding evidence is framed as default auto-blocking;
- test rows influence tau, bank selection, or prompt/response construction;
- raw output text or payload-derived examples enter public artifacts;
- #13 is used to claim coverage for #12 byte/render hazards;
- latency or review-load cost is omitted.

## Required AGT Implementation Work

1. Add an outbound scan-subject extractor for each stage.
2. Add a default-off outbound embedding evidence annotator.
3. Reuse the shared normalizer for the embedding view while keeping normalized
   text in memory only.
4. Add a bounded evidence payload: model/bank IDs, score, tau, hashes, stage,
   transform tags, and offline artifact pointers.
5. Add reference policies that route above-threshold findings to `Escalate` or
   `Warn`.
6. Add latency and cache instrumentation.
7. Add tests proving ground-truth fields are not used as features and raw text
   is never emitted to telemetry/artifacts.

## Non-Goals

- No production/default-blocking claim.
- No detector threshold chosen on test rows.
- No outbound runtime implementation in this research pass.
- No raw payload-derived examples in public issue comments.
- No replacement for #12 render-safe output sanitization.
