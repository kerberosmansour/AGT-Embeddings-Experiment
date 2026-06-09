# Round-4 Governance Metadata Eval Evidence

Status: `needs_more_play`

The migrated Round-4 governance evidence compares AGT rules, embedding-only,
AGT governance metadata, and AGT governance metadata plus embedding routing on
the migrated synthetic research corpus. It is an action-outcome readout using
metadata-only stub actions.

## Provenance

Source experiment:
`experiments/embeddings-knn-security-classification/spk-round4-governance-eval`

The Rust generator was replayed in this target repository from the migrated M1
and M2 inputs. The migrated `manifest.json` therefore records the target
repository's vendored AGT detector source hash and target artifact paths, while
the metrics and row artifacts remain byte-equivalent after LF normalization.

Migrated artifacts:

| Artifact | LF-normalized SHA-256 |
|---|---|
| `artifacts/governance-eval/manifest.json` | `6023905a401295985c9e24e81ee67539da4f4820629c36e0faff4a303c709e96` |
| `artifacts/governance-eval/metrics.json` | `3f9fe972135965c745ef43f904a1526b32f8e5df12ea3e512e92c6ed44094807` |
| `artifacts/governance-eval/policy-profile.json` | `1516456de2e4fb95cf23c6133cabc3e681b1fefc31130c4f849f55cc969f6d07` |
| `artifacts/governance-eval/stub-tool-sink-catalog.json` | `2f76505f41473bce91ed170a69c2f0c0983a737a317e0d9ebbaacc05fa38fc6d` |
| `artifacts/governance-eval/test.jsonl` | `c8903036f3982ade61e6777f57c60b19cd856d02d0905dd343a77889bf7f306f` |
| `artifacts/governance-eval/validation.jsonl` | `9dbd0a600cb0adda87f2b499aed45130ddb25a5ffc926513485c0b73db372409` |

On Windows, raw file hashes may differ because text files can be checked out
with CRLF line endings. The table above uses LF-normalized hashes.

## Test Readout

| Arm | Unsafe-action success | Critical allows | Hard-block FP rate | Approval-load FP rate |
|---|---:|---:|---:|---:|
| `rules_only` | `0.9945652173913043` | `340` | `0.14001396648044692` | `0.0` |
| `embedding_only` | `0.8581521739130434` | `133` | `0.0` | `0.0` |
| `policy_only_gate` | `0.34782608695652173` | `0` | `0.13966480446927373` | `0.0` |
| `policy_plus_embedding` | `0.3070652173913043` | `0` | `0.13966480446927373` | `0.0` |
| `rules_plus_embedding_no_gate` | `0.8527173913043479` | `133` | `0.14001396648044692` | `0.0` |

On the frozen test split, `policy_plus_embedding` reduced unsafe-action success
by `0.040760869565217406` absolute compared with `policy_only_gate`, without
increasing hard-block or approval-load false positives in this synthetic
readout.

## Validation Readout

| Arm | Unsafe-action success | Critical allows | Hard-block FP rate | Approval-load FP rate |
|---|---:|---:|---:|---:|
| `rules_only` | `1.0` | `440` | `0.06443798449612403` | `0.0` |
| `embedding_only` | `0.7815217391304348` | `166` | `0.0` | `0.0` |
| `policy_only_gate` | `0.5507246376811594` | `80` | `0.09689922480620156` | `0.0` |
| `policy_plus_embedding` | `0.4927536231884058` | `80` | `0.09689922480620156` | `0.0` |
| `rules_plus_embedding_no_gate` | `0.7815217391304348` | `166` | `0.06443798449612403` | `0.0` |

The validation split still has `80` critical allows for
`policy_plus_embedding`, so this evidence supports continued work only. It does
not support default blocking, production promotion, or a governance-readiness
claim.
