# M3 Governance and Value-Add Source Map

Date: 2026-06-09
Owner: mac-agent
AgentBus task: `t_mq74ujpr_775_f09cbf2e`
Status: support map only; Windows still owns M3 artifact migration

## Purpose

This note identifies the AGT-only source files for M3 so the governance and
value-add evidence can be migrated without pulling unrelated research material
or stale publication language.

M3 should preserve the central comparison the AGT team needs:

- existing AGT rules-only behavior;
- embedding-only signal;
- rules plus governance;
- rules plus governance plus embedding signal;
- rules plus embedding without governance as a negative control.

The question is whether embeddings add measurable value over the existing AGT
rules/governance stack at an acceptable false-positive or review-load cost.
Youden's J remains a dialled operating point, not a default block threshold.

## Source Allowlist

All paths below are relative to the source repo `Embedding_Experiment`.

| Source path | Target suggestion | Notes |
|---|---|---|
| `experiments/embeddings-knn-security-classification/spk-round4-governance-eval/Cargo.toml` | `tools/round4-governance-eval/Cargo.toml` or M3 provenance only | Rust scratch harness manifest. Do not copy `target/`. |
| `experiments/embeddings-knn-security-classification/spk-round4-governance-eval/Cargo.lock` | `tools/round4-governance-eval/Cargo.lock` or M3 provenance only | Reproducibility lockfile for the scratch harness. |
| `experiments/embeddings-knn-security-classification/spk-round4-governance-eval/src/main.rs` | `tools/round4-governance-eval/src/main.rs` | Metadata-only stub-action generator. |
| `experiments/embeddings-knn-security-classification/spk-round4-governance-eval/artifacts/manifest.json` | `artifacts/governance-eval/manifest.json` | Records AGT commit, policy hash, and artifact hashes. |
| `experiments/embeddings-knn-security-classification/spk-round4-governance-eval/artifacts/metrics.json` | `artifacts/governance-eval/metrics.json` | Arm-level validation/test metrics. |
| `experiments/embeddings-knn-security-classification/spk-round4-governance-eval/artifacts/policy-profile.json` | `artifacts/governance-eval/policy-profile.json` | Low-cardinality policy profile. |
| `experiments/embeddings-knn-security-classification/spk-round4-governance-eval/artifacts/stub-tool-sink-catalog.json` | `artifacts/governance-eval/stub-tool-sink-catalog.json` | Synthetic tool/sink catalog, no side effects. |
| `experiments/embeddings-knn-security-classification/spk-round4-governance-eval/artifacts/validation.jsonl` | `artifacts/governance-eval/validation.jsonl` | Metadata-only per-arm validation rows. |
| `experiments/embeddings-knn-security-classification/spk-round4-governance-eval/artifacts/test.jsonl` | `artifacts/governance-eval/test.jsonl` | Metadata-only per-arm frozen-test rows. |
| `meta/harness/round4-governance-eval/README.md` | `meta/harness/round4-governance-eval/README.md` | Validator usage and claim boundary. |
| `meta/harness/round4-governance-eval/validate-governance-eval.py` | `meta/harness/round4-governance-eval/validate-governance-eval.py` | Shape validator for M3 evidence. |
| `meta/harness/round5-agt-value-add/README.md` | `meta/harness/round5-agt-value-add/README.md` | Report-gate contract for the value-add narrative. |
| `meta/harness/round5-agt-value-add/validate-round5-agt-value-add-report.py` | `meta/harness/round5-agt-value-add/validate-round5-agt-value-add-report.py` | Validates the AGT-facing report shape. |
| `meta/harness/round5-agt-value-add/round5-agt-value-add-report.example.json` | `meta/harness/round5-agt-value-add/round5-agt-value-add-report.example.json` | Schema example only, not evidence. |
| `docs/slo/experiments/embeddings-knn-security-classification/handoff/round4-governance-metadata-eval-contract.md` | `docs/reports/round4-governance-metadata-eval-contract.md` | Reword during migration to keep only AGT evidence boundaries. |
| `docs/slo/experiments/embeddings-knn-security-classification/handoff/round4-governance-eval-evidence.md` | `docs/reports/round4-governance-eval-evidence.md` | Reword safety/scope notes; do not copy old cross-track wording verbatim. |

## Explicit Exclusions

Do not migrate:

- `experiments/embeddings-knn-security-classification/spk-round4-governance-eval/target/**`;
- any `__pycache__/**` file;
- `docs/slo/experiments/embeddings-knn-security-classification/handoff/agt-governance-writeup-DRAFT.md`;
- any Round-5 source-material mini-smoke rows or Promptfoo/source-import rows;
- any unrelated product, data-classification, live-credential, provider-output,
  or publication-draft material.

The draft writeup is intentionally excluded because it contains older stronger
claims and wording that does not match this AGT-only repo's current claim
ledger. If any sentence from it is useful later, rewrite it against the migrated
M1-M3 evidence and route it through the Linux/Windows replacement gates.

## Source Hashes

```text
dd42f722f63de67289db5f90b2713ecde0dc99a6ccb73c291a401b8205caadbb  experiments/embeddings-knn-security-classification/spk-round4-governance-eval/Cargo.toml
0e1e25f279f31ae745d0084b0bcbf7feb62d7f516c97a3219a0100f36ad5c367  experiments/embeddings-knn-security-classification/spk-round4-governance-eval/Cargo.lock
5e1bafa6022043b1c1b0850079a737d80270072220927446ae30f5010a39cdd3  experiments/embeddings-knn-security-classification/spk-round4-governance-eval/src/main.rs
b16786402f1f076d26437c561a8a2f2155ccd2fc37df446b1a027e226ca50bba  experiments/embeddings-knn-security-classification/spk-round4-governance-eval/artifacts/manifest.json
3f9fe972135965c745ef43f904a1526b32f8e5df12ea3e512e92c6ed44094807  experiments/embeddings-knn-security-classification/spk-round4-governance-eval/artifacts/metrics.json
1516456de2e4fb95cf23c6133cabc3e681b1fefc31130c4f849f55cc969f6d07  experiments/embeddings-knn-security-classification/spk-round4-governance-eval/artifacts/policy-profile.json
2f76505f41473bce91ed170a69c2f0c0983a737a317e0d9ebbaacc05fa38fc6d  experiments/embeddings-knn-security-classification/spk-round4-governance-eval/artifacts/stub-tool-sink-catalog.json
9dbd0a600cb0adda87f2b499aed45130ddb25a5ffc926513485c0b73db372409  experiments/embeddings-knn-security-classification/spk-round4-governance-eval/artifacts/validation.jsonl
c8903036f3982ade61e6777f57c60b19cd856d02d0905dd343a77889bf7f306f  experiments/embeddings-knn-security-classification/spk-round4-governance-eval/artifacts/test.jsonl
282b03c0f47d5ea80be969e65f9f79bb8970046da7fbf55f24dfb7a1eb4f05d8  meta/harness/round4-governance-eval/README.md
afdfb8a3994368c63716837dafc1e14e4b60544ac7d27cf770b5a8e6fd7d41ce  meta/harness/round4-governance-eval/validate-governance-eval.py
12234099e5b1e13d41519b245a093200823029f04be57db9bd57fc72bfa44aaf  meta/harness/round5-agt-value-add/README.md
41233162af68a0864d86c9f2b17e5392ccf6d8514971eacd76f674c5de433db1  meta/harness/round5-agt-value-add/validate-round5-agt-value-add-report.py
aa2f684fc546e71c59c77e5ea73d5d9b2a212530a213ed0c3f66e6bed1c88468  meta/harness/round5-agt-value-add/round5-agt-value-add-report.example.json
```

## Evidence Shape

The governance eval rows are metadata-only and use five arms:

- `rules_only`
- `embedding_only`
- `policy_only_gate`
- `policy_plus_embedding`
- `rules_plus_embedding_no_gate`

Row counts from the source artifacts:

| Split | Rows | Rows per arm | Attack rows per arm | Benign rows per arm |
|---|---:|---:|---:|---:|
| validation | 34,440 | 6,888 | 2,760 | 4,128 |
| test | 47,040 | 9,408 | 3,680 | 5,728 |

Native AGT policy decision labels observed in the row artifacts:

- `allow`
- `deny`
- `requires_approval`

No non-native quarantine enum is present. Quarantine intent, when needed, is
represented as metadata on top of a native decision.

## Headline Metrics To Preserve

These numbers are source-map pointers for the M3 migration. They should not be
turned into release-facing claims until Linux audits the migrated artifacts and
the replacement M4 gates review the wording.

| Split | Arm | Unsafe-action success | Prevention | Critical allows | Hard-block FP | Adjacent hard-block FP |
|---|---|---:|---:|---:|---:|---:|
| validation | `rules_only` | 1.000000 | 0.000000 | 440 | 0.064438 | 0.166250 |
| validation | `embedding_only` | 0.781522 | 0.218478 | 166 | 0.000000 | 0.000000 |
| validation | `policy_only_gate` | 0.550725 | 0.449275 | 80 | 0.096899 | 0.000000 |
| validation | `policy_plus_embedding` | 0.492754 | 0.507246 | 80 | 0.096899 | 0.000000 |
| validation | `rules_plus_embedding_no_gate` | 0.781522 | 0.218478 | 166 | 0.064438 | 0.166250 |
| test | `rules_only` | 0.994565 | 0.005435 | 340 | 0.140014 | 0.250625 |
| test | `embedding_only` | 0.858152 | 0.141848 | 133 | 0.000000 | 0.000000 |
| test | `policy_only_gate` | 0.347826 | 0.652174 | 0 | 0.139665 | 0.000000 |
| test | `policy_plus_embedding` | 0.307065 | 0.692935 | 0 | 0.139665 | 0.000000 |
| test | `rules_plus_embedding_no_gate` | 0.852717 | 0.147283 | 133 | 0.140014 | 0.250625 |

The narrow research finding is that `policy_plus_embedding` improved
unsafe-action success versus `policy_only_gate` by `0.057971` absolute on
validation and `0.040761` absolute on frozen test, without increasing
hard-block or adjacent hard-block false positives in this synthetic readout.
The validation split still has `80` critical allows, so this remains research
evidence, not a delivery or default-blocking claim.

## Validation Commands

After Windows migrates the files, run:

```bash
python3 meta/harness/round4-governance-eval/validate-governance-eval.py \
  --manifest artifacts/governance-eval/manifest.json \
  --validation artifacts/governance-eval/validation.jsonl \
  --test artifacts/governance-eval/test.jsonl \
  --metrics artifacts/governance-eval/metrics.json

python3 meta/harness/round5-agt-value-add/validate-round5-agt-value-add-report.py \
  meta/harness/round5-agt-value-add/round5-agt-value-add-report.example.json
```

Linux M3 audit should also independently recompute the table above from
`artifacts/governance-eval/metrics.json`, scan the row artifacts for denied raw
field names, and confirm that target docs do not turn M3 into a production,
certification, benchmark-coverage, or default-blocking recommendation.
