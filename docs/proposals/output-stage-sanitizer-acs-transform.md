# Proposal - Output-Stage Sanitizer via ACS Transform

Issue: https://github.com/kerberosmansour/AGT-Embeddings-Experiment/issues/12

## Summary

Use the shared AGT content-normalization work as the basis for an
**output-side render sanitizer** at `post_tool_call` and `output` ACS stages.
The first target is `terminal_escape_injection`: ANSI, OSC, C1, and related
terminal-control bytes in model/tool output that can hijack a terminal, CLI,
log viewer, or rich console.

This is a structural control because the dangerous unit is byte/control-sequence
shape in the rendered output stream, not text meaning. The control should emit an
ACS `Transform` verdict when it can safely replace the output with a
render-safe body, and `Deny` only when the host cannot safely transform or the
policy marks the sink as non-transformable.

## Current Upstream Shape

Verified on June 12, 2026:

- AGT RFC microsoft/agent-governance-toolkit#2957 proposes surfaced shared
  normalization.
- AGT PR microsoft/agent-governance-toolkit#2991 is open and adds
  `agentmesh::normalize` / `agent_os.normalize` as a pure addition. It does not
  yet wire the detector or policy-engine surfaces to consume it.
- AGT `policy-engine/core/src/verdict.rs` already has
  `Decision::Transform` and a single-target `Transform { path, value }` payload
  rooted at `$policy_target`.

## Critical Design Constraint

Do **not** use the full inbound canonicalized text as the output replacement.

The inbound normalizer is correct for detection because it may lowercase,
collapse whitespace, fold confusables, decode encodings, and surface tags. That
is too destructive for user-visible output. A final answer, terminal transcript,
or tool result must preserve ordinary text as much as possible.

So #12 should define two related but distinct outputs:

| Use | API shape | Replacement-safe? | Purpose |
|---|---|---|---|
| Detection/audit annotation | `normalize()` / `normalize_with()` | no | canonical text + transform tags for detectors and reviewers |
| Output sanitizer | `sanitize_for_render()` or `normalize_with(OutputSanitizeConfig)` | yes | minimally changed rendered body for ACS `Transform` |

The render-safe sanitizer should enable only transformations that remove or
escape rendering controls, for example:

- strip/escape ANSI CSI, OSC, C1, and other terminal escape sequences;
- strip bidi override/isolate controls when the sink cannot render them safely;
- optionally strip invisible controls under a render-safety profile;
- preserve case, ordinary whitespace, prose, code blocks, base64 blobs,
  package names, and quoted examples.

The full normalization result can still be attached as **metadata-only evidence**
for policy decisions, but the `Transform.value` must come from the render-safe
sanitizer.

## Proposed Control Flow

```text
post_tool_call/output policy target
  -> render sanitizer
       sanitized_body
       render_transform_tags
       original_sha256
       sanitized_sha256
  -> policy decision
       Transform {$policy_target.body = sanitized_body}
       or Deny if transform is forbidden/impossible for this sink
  -> audit/event
       tags + hashes + sink metadata, not raw unsafe body
```

Recommended default behavior:

| Stage | Source | Sanitizer changed body? | Default verdict |
|---|---|---:|---|
| `post_tool_call` | untrusted tool output | no | `Allow` |
| `post_tool_call` | untrusted tool output | yes | `Transform`, or `Deny` for non-transformable sinks |
| `output` | final user-visible response | no | `Allow` |
| `output` | final user-visible response | yes | `Transform` |

`Deny` should be reserved for policy-selected high-risk conditions, such as a
sink that cannot preserve safety after transformation, an output format where
replacement would corrupt integrity, or a deployment policy that refuses
terminal-control bytes from untrusted tools. Transform should be the ergonomic
default for final user-visible text because it neutralizes the hazard while
still returning useful content.

## Policy Contract

An AGT reference policy should be able to express:

```jsonc
{
  "stage": "output",
  "control_under_test": "render_sanitizer_terminal_controls",
  "required_annotations": [
    "render_sanitizer.tags",
    "render_sanitizer.sanitized_body",
    "render_sanitizer.original_sha256",
    "render_sanitizer.sanitized_sha256"
  ],
  "transform": {
    "path": "$policy_target.body",
    "value_from": "render_sanitizer.sanitized_body"
  }
}
```

The policy should not need to parse terminal bytes itself. It should consume a
closed tag vocabulary from the sanitizer, such as:

- `AnsiEscape`
- `BidiControl`
- `InvisibleControl`
- `OutputCapped` / `SanitizeFailed` when bounds are hit

## Round-7 Mapping

Round-7 currently labels `terminal_escape_injection` as `workflow_review` with
`blocked_on=["#12"]`. This proposal is the path to make that bucket structural:

- `containment_class`: `structural`
- `defense_stage`: `post_tool_call` or `output`
- `control_under_test`: `render_sanitizer_terminal_controls`
- `acs_verdict`: `Transform` by default, `Deny` only when policy requires
- `evidence_tags`: sanitizer transform tags and hashes

This does not change the inbound WS-B normalizer result. It adds a downstream
consumer profile for the output/rendering boundary.

## Relationship To #13

#12 and #13 are complementary:

- #12 is deterministic byte/render hygiene. It should be auto-transformable for
  terminal-control and improper-output-handling hazards.
- #13 is evidence-grade outbound semantic scanning. It may detect harmful text,
  leakage, or jailbreak-style output, but it should feed `Escalate` or review
  workflows rather than claiming deterministic structural blocking.

If both controls run, #12 should sanitize first so downstream logs, reviewers,
and embedding/evidence tools do not consume unsafe terminal-control bytes.

## Required AGT Implementation Work

1. Add or expose a render-safe sanitizer API in the shared normalizer module.
2. Add a policy-engine annotation/dispatcher hook at `post_tool_call` and
   `output` that records sanitizer tags, sanitized value, and hashes.
3. Add a reference policy that maps sanitizer changes to ACS `Transform`.
4. Add integration tests proving `$policy_target.body` replacement works and
   `Transform` is rejected for forbidden paths.
5. Add benign output tests: colored CI logs, terminal transcripts, code blocks,
   package install output, and quoted security examples.
6. Add bounds tests: sanitizer remains O(n), caps pathological expansion, and
   never logs the raw unsafe body in telemetry.

## Acceptance Gates

- Render-safe sanitizer preserves ordinary benign output byte-for-byte except
  for targeted control sequences.
- Dangerous terminal-control sequences are removed or escaped and tagged.
- `Transform.value` comes from the render-safe sanitizer, not from the full
  lowercasing/decoding canonicalizer.
- Audit artifacts are metadata-only: tags, hashes, stage, source trust, and
  policy ID; no raw unsafe output.
- Round-7 `terminal_escape_injection` can move from `workflow_review` to
  `structural` only after the AGT hook and reference policy exist and pass.

## Non-Goals

- No semantic harmful-output detection. That is #13.
- No claim that output sanitization handles prompt leakage, jailbreak, or data
  exfiltration by meaning.
- No production/default-blocking claim from this research repo alone.
- No literal payload-derived examples in public issue comments.
