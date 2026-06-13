# Reality-check arm — intake spec (for the research agents)

**Drop collected real-world attack samples here:** `corpus/round7/reality-check/incoming/`
one or more `*.jsonl` files (one JSON object per line). Claude picks these up later
and folds them into the round-7 **payload-derived** arm (separate manifest, split,
and claim — never mixed into the synthetic headline).

## What we want
Real, attributed attack samples that are **not already covered** by our taxonomy —
novel techniques, real phrasings, real obfuscations, and multi-turn agent traces.
**The most valuable samples are ones our current detector/normalizer MISSES** — the
whole point is visibility into where we're blind, so "it slips past us" is a
feature, not a reason to exclude it.

Already covered (don't need more unless a genuinely new variant): direct override,
prompt leakage, indirect/latent injection, tool-result injection, tool abuse,
output exfiltration, memory poisoning, data-boundary abuse, jailbreak/persona,
package hallucination, terminal/ANSI escape, and the obfuscations base32/ascii85/
atbash/morse/nato/braille/unicode-tag/variation-selector/sneaky-bits/zalgo/rot13/
base64/hex/percent/homoglyph/leet/spacing.

## Per-sample schema (one JSON object per line)
```jsonc
{
  "text": "<raw attack payload, verbatim>",
  "technique": "<short name, e.g. 'GCG suffix', 'crescendo multi-turn', garak probe id>",
  "attack_class": "<closest of our families, OR 'novel:<short-name>' if it doesn't fit>",
  "harm_channel": "action | leak | output_bytes | output_text | unknown",
  "multi_turn": false,
  "turns": null,                       // single-turn: null. multi-turn: [{"role":"user|assistant|tool|system","text":"..."}]
  "origin": "<where it came from: garak/paper/blog/CVE/dataset/repo>",
  "origin_url": "<link, must start with http(s)://>",
  "license": "<source license: Apache-2.0 | MIT>",
  "why_novel": "<one line: why this isn't already in our taxonomy>",
  "notes": "<short note; use \"\" if none — the field must be present>"
}
```

## Rules (so it's usable + safe to commit)
- **Provenance + license on every row** — this arm is source-attributed; we keep a
  NOTICE. Committed `incoming/` rows must be Apache-2.0 or MIT only. Unknown,
  proprietary, NC-only, or unclear-redistribution datasets stay outside this
  folder until cleared.
- **No live secrets / credentials / PII, and no raw URLs/emails in the payload** —
  the validator rejects ANY `http(s)://`, email address, or secret marker inside
  `text` / `turns[*].text` (even reserved domains like `example.com`). Redact to
  **bracket placeholders** that preserve the attack structure: `[URL]`,
  `[ATTACKER_URL]`, `[ATTACKER_EMAIL]`, `[SECRET]`, `[TOOL_NAME]`, … — e.g. a
  markdown-exfil payload becomes `![x]([ATTACKER_URL])`. A real provenance link
  belongs in `origin_url` only.
- Include **every** field shown above (use `""` / `null` when empty) and **no
  extra fields** — the validator flags both missing and unexpected keys.
- Keep each source's samples in a separate file named by origin, e.g.
  `garak-latentinjection.jsonl`, `crescendo-paper.jsonl`.
- Multi-turn traces welcome — use the `turns` array (`multi_turn: true`).
- Duplicates of what we already have are fine to skip; novelty > volume.

When samples land here, ping Claude to normalize them into the payload-derived
manifest, run the leakage audit against the synthetic arm, and label
`containment_class` / harm channel.

## Validation

Before handoff, run the intake validator and keep the summary metadata-only:

```bash
python3 corpus/round7/reality-check/check_reality_check.py \
  corpus/round7/reality-check/incoming \
  --summary scratch/round7-reality-check-summary.json
```

The validator enforces Apache-2.0/MIT-only source licenses, required provenance
fields, multi-turn shape, and payload-field redaction hygiene. It allows
`origin_url` as provenance, but rejects live-looking URLs, emails, and common
secret markers inside `text` or `turns[*].text`.
