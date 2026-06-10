# Source-To-AGT Expected-Action Mapping

Status: PR 1 methodology guardrail

This document defines how source-reviewed corpus `expected_action` metadata
should map to AGT-native policy vocabulary for a standalone prompt-injection
evaluation fixture.

It is intentionally not a runtime policy. It exists so benchmark rows can carry
reviewed action intent without inventing non-native AGT `PolicyDecision`
variants or changing AGT behavior.

## Vocabulary Boundary

Corpus `expected_action` describes reviewer intent for evaluation data. It is
not the same thing as AGT's Rust `PolicyDecision` enum.

AGT-native policy decisions are:

| AGT decision | Meaning in AGT |
|---|---|
| `allow` | The action is permitted. |
| `deny` | The action is denied with an audit reason. |
| `requires_approval` | The action is routed for human approval with a reason. |
| `rate_limited` | The action is delayed and may be retried later. |

Evaluation rows may use broader `expected_action` metadata:

| Corpus `expected_action` | Evaluation meaning | AGT-native interpretation |
|---|---|---|
| `allow` | Benign or acceptable request. | Expected safe path is `allow`. |
| `log_only` | Record for audit without blocking or approval. | Expected safe path is still non-denial; it must not imply a new AGT decision. |
| `require_approval` | Potentially risky action should be reviewed before execution. | Equivalent to AGT `requires_approval` when a policy profile chooses to route it. |
| `block` | Unsafe action should not execute. | Equivalent to AGT `deny` when a policy profile chooses to block it. |
| `quarantine` | Strong unsafe-action intent requiring containment/downstream handling. | Metadata only. It is not an AGT `PolicyDecision`; do not serialize `agt_policy_decision=quarantine`. |

## PR 1 Rule

For upstream AGT PR 1, the fixture should evaluate detector behavior and
baseline methodology only. It must not add:

- a runtime embedding dependency;
- a default threshold;
- policy-routing integration;
- default blocking behavior;
- a new native AGT policy decision.

Any row with `expected_action=quarantine` must remain evaluation metadata. If a
future AGT policy profile wants to treat that intent as containment, it should
do so through existing native outcomes such as `deny` or `requires_approval`,
plus separate downstream handling metadata. It should not add or imply
`PolicyDecision::Quarantine`.

## Matched Controls

Every attack family proposed for a source-reviewed fixture should have matched
benign control coverage:

- adjacent-security benign controls, such as safe discussions of prompt
  injection or detector behavior;
- plain benign controls, such as normal tool or documentation requests;
- family/group holdouts so near-duplicates cannot cross validation and test;
- exact-normalized and near-duplicate leakage checks.

Matched controls are part of the fixture methodology, not evidence that a
runtime policy is ready. They make false positives inspectable and keep the
benchmark from overfitting to attack-shaped wording alone.

## Reporting

Reports should keep these fields distinct:

- `expected_action`: reviewer intent for the corpus row;
- `agt_policy_decision`: an AGT-native decision label only;
- `quarantine_intent`: optional boolean metadata for rows whose expected action
  is `quarantine`;
- detector scores or margins: evidence values, not policy outcomes.

The fixture can report recall, false-positive rate, Wilson intervals,
base-rate precision, and review-load cost. Those metrics are corpus-specific
evaluation results. They are not production, certification, real-traffic, or
default-blocking claims.
