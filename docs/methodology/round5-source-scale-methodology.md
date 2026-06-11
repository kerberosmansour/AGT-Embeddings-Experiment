# Round-5 Source-Scale Methodology

Round 5 is useful, but not as a new headline performance result. Its value is
methodological: it shows how a future AGT benchmark fixture can connect
source-reviewed prompt-injection families to synthetic, reproducible rows
without importing external benchmark text or changing AGT runtime behavior.

## What Round 5 Adds

Round 4 established a large synthetic corpus, a rules-only AGT baseline, and an
embedding/kNN readout. Round 5 adds a smaller source-scale pilot with stronger
generation controls:

| Gate | Round-5 behavior |
|---|---|
| Source record review | Every source-mapped family has reviewer-approved expected action and attack class. |
| Matched controls | Attack families have adjacent-security or plain benign control families. |
| Split unit | Rows split by `family_id` / `group_id`, not random row sampling. |
| Leakage checks | Family, group, exact-normalized, and near-duplicate cross-split leakage are all zero. |
| Threshold hygiene | Embedding threshold selected on validation before test scoring. |
| Artifact hygiene | Per-row embedding outputs are metadata-only. |

The pilot contains 72 synthetic rows:

| Slice | Count |
|---|---:|
| Attack families | 36 |
| Adjacent-security benign families | 18 |
| Plain benign control families | 18 |
| Exemplar-bank rows | 24 |
| Validation rows | 24 |
| Test rows | 24 |

Each split has 12 attack rows and 12 benign rows.

## Why It Is Not A Performance Claim

The pilot scored 12/12 attacks and 0/12 benign false positives on both
validation and test. That is encouraging, but the sample is intentionally tiny:
the Wilson 95% lower bound for recall is about 0.758, and the Wilson 95% upper
bound for benign false-positive rate is about 0.242.

So the professional interpretation is:

```text
Round 5 is a useful source-review and leakage-gate smoke test. It is not enough
to claim a detector is ready, and it should not change the Round-4 headline
metrics.
```

## What Should Move Toward AGT Upstream

For AGT PR 1, Round 5 should inform the benchmark fixture design:

- a source-record schema with reviewer-approved expected action;
- a source-to-AGT action mapping document
  (`docs/methodology/source-to-agt-expected-action-mapping.md`);
- a matched-control requirement for every attack family;
- family/group split checks;
- exact and near-duplicate cross-split leakage checks;
- a manifest with row counts and SHA-256 hashes;
- a small smoke fixture that can run quickly in CI;
- documentation that source-mapped rows are evaluation data, not runtime policy.

## What Should Stay Out Of AGT Upstream Initially

The following should stay in the research repo unless maintainers explicitly
ask for them:

- internal AgentBus audit notes;
- raw source-scale scratch rows;
- raw source-record review JSONL;
- embedding model cache details beyond model ID and model hash;
- any source-taxonomy coverage language;
- any claim that the Round-5 pilot validates production behavior.

## Relationship To The Two-PR Plan

Round 5 strengthens PR 1, not PR 2.

PR 1 should land the benchmark fixture and reproducibility gates. Round 5 gives
the clearest template for those gates.

PR 2 should remain blocked until maintainers accept the corpus methodology,
baseline pin, threshold-freeze rules, and review-load reporting.

## Sanitized Artifact

The migrated sanitized summary lives at:

```text
artifacts/source-scale-pilot/summary.json
```

It records counts, hashes, validation outcomes, and caveats without importing
raw prompt/source rows.
