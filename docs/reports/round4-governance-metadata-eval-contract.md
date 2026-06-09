# Round-4 Governance Metadata Eval Contract

This contract describes the migrated Round-4 AGT governance metadata evidence in
`artifacts/governance-eval/`.

The evidence is metadata-only synthetic action-outcome evidence. It does not
include raw prompt text, tool arguments, source excerpts, model prompts, secrets,
URLs, email addresses, or raw action payloads.

## Scope

- Corpus source: migrated Round-4 synthetic research corpus and embedding sweep.
- Governance source: AGT policy vocabulary and metadata-derived stub actions.
- Artifact location: `artifacts/governance-eval/`.
- Validator: `meta/harness/round4-governance-eval/validate-governance-eval.py`.

The governance rows use native AGT policy decision labels:

- `allow`
- `deny`
- `requires_approval`
- `rate_limited`

Rows whose expected action is `quarantine` must use
`quarantine_intent=true`. `quarantine` is not treated as a native AGT
`PolicyDecision`.

## Arms

- `rules_only`
- `embedding_only`
- `policy_only_gate`
- `policy_plus_embedding`
- `rules_plus_embedding_no_gate`

`policy_only_gate` is the AGT governance metadata arm without embedding margin
routing. `policy_plus_embedding` adds embedding-margin routing to that metadata
gate. `rules_plus_embedding_no_gate` is a negative-control arm and must not be
used as a deployment recommendation.

## Non-Claims

This evidence does not claim:

- production safety
- default blocking readiness
- certification
- benchmark coverage
- Promptfoo, ASI, or AIVSS coverage
- real-traffic validation
- AGT detector or policy promotion

Any stronger claim requires a separate reviewed dataset, prevalence model,
review-load analysis, and independent audit.
