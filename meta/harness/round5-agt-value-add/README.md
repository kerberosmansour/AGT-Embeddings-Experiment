# Round-5 AGT Value-Add Report Gate

This harness validates the shape of an AGT-facing value-add report before any
Round-5 M3/M4 claim is made.

It does not score embeddings, run AGT, inspect raw prompts, or certify detector
quality. It only enforces that a future report compares the right arms and keeps
the evidence metadata-only.

Required arms:

- `rules_only`
- `embedding_only`
- `policy_only_gate` (`rules_plus_governance`)
- `policy_plus_embedding` (`rules_plus_governance_plus_embedding`)
- `rules_plus_embedding_no_gate`

The central question is whether embeddings add measurable lift over the existing
AGT rules/governance stack at an acceptable false-positive or review-load cost.
Youden's J is treated as a dialled operating point, not a default recommendation.

Validate the schema example:

```bash
python3 meta/harness/round5-agt-value-add/validate-round5-agt-value-add-report.py \
  meta/harness/round5-agt-value-add/round5-agt-value-add-report.example.json
```

Expected output:

```text
OK: meta/harness/round5-agt-value-add/round5-agt-value-add-report.example.json
```

