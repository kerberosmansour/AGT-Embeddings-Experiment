# Round-5 Source-Scale Pilot

Date: 2026-06-10
Status: migrated as sanitized methodology evidence

## Summary

Round 5 adds a small source-scale pilot that is useful for upstream AGT
methodology review. It should not be used as a headline detector result.

The pilot is useful because it demonstrates how to build a professional
benchmark fixture:

- source-mapped prompt-injection families;
- reviewer-approved labels and expected actions;
- matched benign controls;
- family-level split isolation;
- duplicate and near-duplicate leakage checks;
- validation-only threshold selection;
- metadata-only per-row embedding artifacts.

## Shape

| Item | Value |
|---|---:|
| Source records | 72 |
| Synthetic rows | 72 |
| Attack families | 36 |
| Adjacent-security benign families | 18 |
| Plain benign control families | 18 |
| Exemplar-bank rows | 24 |
| Validation rows | 24 |
| Test rows | 24 |

Each split has 12 attack rows and 12 benign rows.

## Hygiene

| Check | Result |
|---|---:|
| Family split leaks | 0 |
| Group split leaks | 0 |
| Exact normalized cross-split leaks | 0 |
| Near-duplicate cross-split leaks | 0 |
| Split label coverage | PASS |
| Metadata-only embedding outputs | PASS |

## Embedding Smoke Result

The embedding smoke selected `k=1` and `threshold_tau=-0.1526973271369937` on
the validation split only.

| Split | TP | FN | FP | TN | Recall | FP rate |
|---|---:|---:|---:|---:|---:|---:|
| Validation | 12 | 0 | 0 | 12 | 1.00 | 0.00 |
| Test | 12 | 0 | 0 | 12 | 1.00 | 0.00 |

This is promising as a gate smoke, but the sample is too small to strengthen the
main detector claim. The test split contains only 12 attacks and 12 benign
controls.

## Recommended Use

Use Round 5 to improve PR 1:

- include a source-review gate;
- require matched benign controls;
- preserve family/group holdout checks;
- publish hashes and validation commands;
- keep raw prompt/source rows out of public claims unless maintainers
  explicitly review and approve them.

Do not use Round 5 to justify PR 2 runtime behavior. PR 2 still needs accepted
methodology, fresh AGT baseline pinning, and reviewer agreement on how the
embedding signal feeds policy or review routing.

## Source Hashes

| Artifact | SHA-256 |
|---|---|
| Source records JSONL | `d3cf69c48f18affb053cb825d7b66f38375db6ff90b6f5fb3ade02fa37bc6347` |
| Source rows JSONL | `a72dda5d9c040a04aa39aa846f20b4613f4cf1d40c5cbede09a73d0c2cc0f069` |
| Source manifest JSON | `d7c606716e910ac5cef1c08076ba2a82c05ff0b5a85ba2b5396dd2576f8ed606` |
| Check summary JSON | `a691b02a135035acc37290b067b0cf38ae3392e555fb80768603d9a1462a966b` |
| Freeze record JSON | `a08ca59efa4bccdf6d02fb30758962323193bcfb36d707ca97b8d0a938e31037` |
| Validation metrics JSON | `558df9cfbc125a2266df0a1deb69564489c34509a469be19e1630d4486082c58` |
| Test metrics JSON | `7b6a8c88f2337c38fe39fc0b01cb984900b06719c9817e23edc7e1fbd6205151` |
