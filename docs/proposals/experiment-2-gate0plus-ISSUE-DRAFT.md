# GitHub issue draft — Experiment 2 (ready to paste)

> Could not be filed automatically: `gh issue create` was blocked by the local
> permission classifier and the GitHub MCP integration lacks write scope (403).
> Paste the body below into a new issue, or approve `gh` and re-run.
> Suggested title / labels:
>
> **Title:** Experiment 2: Gate 0++ delivery-layer normalization (needs new markup/multimodal corpus data)
> **Labels:** enhancement, help wanted

---

## Summary

Round 6 showed **Gate 0 character-level de-obfuscation** is the single biggest
lever (zero-FP catch 14.2% → 43.3%). The Google DeepMind *AI Agent Traps*
taxonomy (Franklin et al., 2026) makes clear that character tricks are only the
smallest slice of the **Content Injection** category. The high-value,
deterministic next step is **Gate 0++**: extend normalization from
character-level to the **delivery/markup layer** — reconcile what the agent
parses with what a human actually sees.

**Blocker: we cannot measure Gate 0++ on the current corpus.** The round-4
corpus is plain text; it contains zero markup/multimodal delivery attacks.
Measuring a delivery-layer normalizer on it would just reproduce the Gate 0
numbers. This experiment is gated on generating new data first.

## What Gate 0++ would do (deterministic, no human review)

Parse content the way a human sees it, before scoring:
- Drop hidden text: `display:none`, off-viewport (`left:-9999px`), zero-size,
  colour-on-colour.
- Strip HTML comments and `aria-label` / metadata payloads that don't render.
- Decode Markdown/LaTeX masking (payload hidden in a link anchor; white/tiny
  LaTeX).
- Surface or flag image `alt`/metadata text (steganographic decoding is out of
  scope for v1 — flag, don't decode).

Rationale: "a human can't see it" is a **structural fact**, so stripping
invisible markup is safe to automate — same confidence basis as Gate 0.

## Data we need to generate (the real ask)

A markup/delivery-layer extension of the corpus, mirroring round-4 hygiene
(synthetic, metadata-only artifacts, family/group holdouts, frozen splits,
exact-/near-duplicate leakage checks).

**Attack variants — wrap existing attack payloads in delivery vectors:**

| Slice | Delivery vector |
|---|---|
| `web_hidden_css` | payload in `display:none` / off-viewport / colour-matched spans |
| `web_html_comment` | payload in `<!-- ... -->` |
| `web_aria_label` | payload in `aria-label` / alt / metadata attributes |
| `markdown_anchor` | payload masked in a Markdown link anchor / reference |
| `latex_masking` | payload as white-on-white or tiny-font LaTeX |
| `image_alt_stego` (v2, optional) | payload in image alt/metadata — flag-only |

**Benign markup controls — the critical half (prevent over-stripping):**
legitimate pages with real HTML comments, genuine `aria-label` accessibility
text, normal Markdown links, real LaTeX. These must survive Gate 0++ untouched —
they are the false-positive control.

Target ≈200–600 attack rows/slice + matched benign controls (Wilson intervals
comparable to round 4).

## What it measures (once data exists)
- Catch at the validation-frozen FP-zero point, **per delivery-vector slice**,
  vs Gate 0 (char-only) and the round-4 baseline.
- FP on the benign-markup controls (must stay ~0 — over-stripping guard).
- Same metadata-only / freeze-before-test discipline as round 6.

## Out of scope (v1)
- Multimodal/steganographic *decoding* (flag-only).
- Semantic-manipulation and systemic / human-in-the-loop trap categories.
- Any control that requires judging text meaning (not deterministic).

## Dependencies
- Sequenced **after** Experiment 1 (structural auto-block ceiling — needs no new
  data). Data generation is the long pole; harness reuses round-6
  `normalize.py` + runner shape.

## References
- `docs/reports/round6-cascade-report.md` (Gate 0 result)
- Franklin et al., *AI Agent Traps*, Google DeepMind, 2026 — Content Injection
  category.
