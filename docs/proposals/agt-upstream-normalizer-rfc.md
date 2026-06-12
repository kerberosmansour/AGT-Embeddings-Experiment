# RFC (draft for review) — Strengthen and surface content normalization as a shared pre-detection control

> Draft to post to microsoft/agent-governance-toolkit (use the **RFC** issue
> template). Human-authored and human-reviewed before posting, per CONTRIBUTING.
> Numbers below are from a synthetic research corpus — directional evidence, not
> production guarantees.

---

## Summary

AGT already normalizes text before regex detection (`normalize_for_detection`
in `agentmesh/src/prompt_injection.rs`: Unicode width-fold, strip, lowercase,
whitespace-collapse). This RFC proposes two changes:

1. **Strengthen** that normalization with additional *deterministic,
   false-positive-guarded* de-obfuscation transforms (homoglyph/confusable
   folding, leetspeak de-substitution, letter-spacing/separator collapse, and
   bounded decode layers for base64/hex/rot13/percent-encoding/unicode-escape/
   HTML-entities).
2. **Surface** normalization as a *shared canonicalization pass* — a small public
   module that emits the normalized text **plus a record of which transforms
   fired** — instead of a private function used only by the regex detector, so
   every text-based control can consume it.

The core idea: **normalization is a force-multiplier for every downstream
control — detective and preventative alike — and is worth having regardless of
whether you ever adopt an ML/embedding detector.** Disguised input (`1gn0re`,
homoglyphs, letter-spacing, encodings) defeats not just the regex detector but
*any* control that reads the text. Canonicalizing once, up front, and surfacing
the result helps the existing `PromptInjectionDetector`, classifier/LLM
annotators, IFC/policy decisions, and human reviewers all at the same time.

## Motivation — what the attack data shows

In a controlled study on a synthetic prompt-injection corpus (metadata-only,
frozen-test discipline), with a *fixed* downstream detector:

| Change | Catch @ 0% false-positives |
|---|---:|
| detector on raw text | 14% |
| **+ fuller normalization in front of it** | **43%** (3×) |
| **+ extended decode layers (encoding/rot13)** | encoding-attack class **35% → 62%**; overall **43% → 49%** |

…with **zero benign-control false-positives** throughout (measured against
deliberately obfuscated-but-legitimate inputs: percentages, ampersands,
high-entropy structured data, legitimate base64, code, security documentation).

Two takeaways:

- **The lift is large and it is upstream of the detector.** We changed *only* the
  normalization, not the detector. The same lift accrues to any text control AGT
  runs.
- **It is both detective and preventative.** A preventative policy/IFC decision
  that inspects content (e.g. "untrusted text requesting a sensitive tool")
  becomes more reliable when the content has been un-disguised first; a human
  reviewer sees what the agent actually parses, not the cosmetic surface.

## What's there today vs. what's missing (we checked the source)

`normalize_for_detection` (private to the regex detector) folds Unicode
fullwidth, strips zero-width/bidi/control chars, lowercases, and collapses
whitespace. Separately, `scan_encoding` decodes base64 (embedded tokens) and
backslash/unicode escapes *inside detection*, and string-matches the words
"rot13" / "base64 decode". A precise two-way comparison against our normalizer:

| Transform | AGT today | This proposal |
|---|---|---|
| Fullwidth fold · lowercase · whitespace-collapse | ✅ normalizes | ✅ (keep) |
| Zero-width strip | ✅ | ✅ |
| **Bidi-override / isolate strip (Trojan Source)** | ✅ (`202A–202E`, `2066–2069`) | ✅ — **adopt AGT's** (our research normalizer missed it) |
| base64 / backslash-escape decode | ✅ but **detection-internal only** | ✅ + **surfaced** to all controls |
| Homoglyph / confusable fold (Cyrillic/Greek → Latin) | ❌ | ✅ add |
| Leetspeak de-substitution (`1gn0r3`→`ignore`, token-guarded) | ❌ | ✅ add |
| Letter-spacing / separator collapse (run-length-guarded) | ❌ | ✅ add |
| rot13 **decode** (not just the string "rot13") | ❌ reference-only | ✅ add |
| percent/URL · HTML-entity · hex decode | ❌ | ✅ add |
| **Surface normalized text + transform tags to every control** | ❌ private to detector | ✅ the design idea |

So the additions are genuinely complementary — AGT already strips bidi-override
characters (which our research normalizer did not, and which we'd adopt), and we
add the homoglyph/leet/spacing/decoder transforms and the surfacing layer that
AGT does not have. The net is "merge the best of both," not "replace."

## Proposal

### A. Strengthen the transforms (FP-safety is the design centerpiece)

Add the transforms above, each behind an **acceptance guard** so benign text is
never mangled:

- **Decoders** only accept a decode if the result is valid UTF-8, ≥90% printable,
  and increases a generic English-marker signal (not derived from attack labels);
  bounded to depth ≤ 2 and ≤ 4× expansion.
- **Leetspeak / homoglyph / spacing** fire only under token / run-length guards
  characteristic of obfuscation and rare in prose.
- Everything is deterministic and idempotent (`normalize(normalize(x)) ==
  normalize(x)`), property-tested.

We would bring benign-safety tests proving legitimate inputs (percentages,
`&amp;`, legit base64, code, structured data) pass through unchanged — this is
the part maintainers will rightly scrutinize, and it's where our 0-FP evidence
focuses.

### B. Surface it as a shared, audited canonicalization pass

- Promote `normalize_for_detection` from a private `fn` to a small **public,
  configurable `normalize` module**.
- Return the normalized text **and a closed set of "transform tags"** recording
  which transforms fired (e.g. `leet`, `confusables`, `base64`, `decode_rejected`).
- Make the normalized view + tags available at the **Input** stage (and
  `PreToolCall` args / `PostToolCall` results), so policy-engine annotators/Rego
  and the AgentMesh detector can both read it — and so audit can show what was
  un-disguised and why.

### Where it sits in AGT

An Input-stage (and tool-arg / tool-result) **canonicalization pass**, shared
across controls. Concretely: promote the existing private function in
`agentmesh` to a public module the detector consumes, and expose its output on
the snapshot/annotations surface that policy-engine controls already read.

## Scope — what this RFC is *not*

This is **only** the normalization control. We have separate research on an
embedding/kNN detector that builds on top of this normalizer, but that is a
distinct conversation. The normalizer stands on its own: it improves the
**existing** regex detector and any policy/IFC control with **no ML dependency**.

## Companion follow-up: output-stage sanitization

The shared normalizer also opens a downstream control path, but with an important
API distinction: output replacement must use a **render-safe sanitizer profile**,
not the full inbound canonicalized text. Full normalization is appropriate for
detection/audit annotations; user-visible `Transform.value` should preserve
ordinary output and only strip or escape rendering controls such as ANSI/OSC/C1
terminal sequences.

The detailed follow-up proposal lives in
`docs/proposals/output-stage-sanitizer-acs-transform.md`. It maps round-7
`terminal_escape_injection` to an ACS `output` / `post_tool_call` sanitizer that
can emit `Transform {$policy_target.body = sanitized_body}` while keeping
semantic harmful-output scanning as a separate outbound experiment.

## Contribution offer

We implemented and measured this in **Python** (research repo). AGT's core
detector is **Rust**. I'd like to **volunteer to contribute the Rust
implementation first** — extend and surface `normalize_for_detection` in
`agentmesh`, with the acceptance guards, the transform-tag output, and the
benign-safety + idempotency test suite — and then follow with **Python
(`agent-os`) parity**. Happy to align on the public API shape and the
configuration surface before writing code.

## Alternatives considered

- **Status quo (detector-private normalization):** every other control
  re-derives normalization or misses it; disguised input bypasses preventative
  controls and human review.
- **Per-language ad-hoc normalization:** drift between the Rust/Python/.NET/Go/TS
  detectors; no shared canonical form.
- **Do nothing:** the `EncodingAttack` family stays detect-by-pattern on
  partially-normalized text, and disguised attacks continue to evade both
  detection and prevention.

## Caveats / evidence basis

- All numbers are from a **synthetic research corpus**; they are directional, not
  a production guarantee. Real-traffic validation and a false-positive audit on
  real benign data are separate work.
- The transforms are deterministic; the only real risk is over-normalizing
  benign text, which the acceptance guards + benign-control tests are designed to
  prevent (0 benign-control FP in our measurements).
