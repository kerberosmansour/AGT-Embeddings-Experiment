# Synthetic variation policy

The `incoming/` arm is source-attributed reality-check data. Keep it limited to
Apache-2.0 and MIT sources only.

## Placeholder Policy

Rows may contain redaction placeholders such as `[EMAIL]`, `[ATTACKER_URL]`,
`[HARMFUL_GOAL]`, or `[DISALLOWED_CONTENT_CATEGORY]`. These are intentional:
they preserve attack structure while removing live-looking values, PII, secrets,
victim data, and ready-to-use harmful instructions.

For benchmark runs that need realistic surface form, generate a separate
synthetic-variation arm. Do not overwrite the source-attributed rows.

## Quality Bar For Synthetic Values

- Use reserved domains and addresses only: `example.test`, `example.invalid`,
  `attacker.invalid`, and similar non-routable values.
- Use clearly fake secrets: `sk-test-...-FAKE`, `[CANARY_*]`, or `TEST-*`.
- Use clearly fake people, files, IBANs, account numbers, and dates.
- Preserve attack grammar and placement. Replace the slot, not the whole prompt.
- For `[HARMFUL_GOAL]`, use abstract benchmark-safe surrogate goals such as
  `SYNTHETIC_DISALLOWED_GOAL_cyber_abuse_001`; do not generate operational
  instructions.
- Keep provenance: synthetic rows should point back to the parent source row in
  `notes` and retain the parent source license when it is Apache-2.0 or MIT.

## Generator

```bash
python3 corpus/round7/reality-check/make_synthetic_variations.py \
  --input-dir corpus/round7/reality-check/incoming \
  --output scratch/round7-synthetic-variations.jsonl \
  --variants-per-row 2
```

The generator fails if any input row is not Apache-2.0 or MIT unless
`--skip-disallowed-license` is passed.

By default it emits only rows with recognized placeholders. Pass
`--include-no-placeholder` if a downstream benchmark needs a full one-to-one
copy of the source arm with synthetic provenance metadata.
