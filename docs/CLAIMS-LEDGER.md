# Claims Ledger

This ledger maps the public narrative to the evidence that must be migrated
into this repository.

Current migrated evidence is split across:

- M1 corpus/rules baseline: target commit `25f8d06`.
- M2 embedding/kNN sweep and Youden's J readout: target commit `834da55`.
- M3 governance metadata/value-add readout: this M3 migration commit.

## Narrative Claims And Evidence

| Narrative claim | Current evidence | Source artifact to migrate | Status |
|---|---|---|---|
| AGT rules-only detector has low recall on the hard held-out set. | `180 / 17600 = 0.010227` attack recall. | `corpus/round4/rules-baseline-large-metrics.json` | Migrated in M1; Linux and Windows readbacks PASS. |
| AGT rules-only detector has material false positives on benign examples. | `2136 / 27200 = 0.078529` benign false-positive rate. | `corpus/round4/rules-baseline-large-metrics.json` | Migrated in M1; Linux and Windows readbacks PASS. |
| The evaluation corpus has 44,800 labelled examples. | `row_count=44800`; split counts `28504 / 6888 / 9408`. | `corpus/round4/manifest-large.json`; `corpus/round4/check-large-summary.json` | Migrated in M1; leakage checks PASS. |
| The split avoids family/group leakage. | Family leaks `0`; group leaks `0`; exact normalized cross-split leaks `0`; near-duplicate cross-split leaks `0`. | `corpus/round4/check-large-summary.json` | Migrated in M1; independent audit PASS. |
| Embedding/kNN at Youden's J catches about 88% on frozen test. | Test recall `0.882609` at threshold `-0.00609511`. | `artifacts/embedding-sweep/youden-j-tuning.json`; `docs/reports/round4-youden-j-tuning.md` | Migrated in M2 with plateau-midpoint caveat; Linux M2 audit PASS. |
| Embedding/kNN at Youden's J has about 16% false positives. | Test FPR `0.163059`, FP `934 / 5728`. | `artifacts/embedding-sweep/youden-j-tuning.json`; `docs/reports/round4-youden-j-tuning.md` | Migrated in M2; Linux M2 audit PASS. |
| Conservative embedding point has zero observed false positives. | Test recall `0.141848`, FPR `0.0`, FP `0`. | `artifacts/embedding-sweep/test-metrics.json`; `artifacts/embedding-sweep/youden-j-tuning.json`; `docs/reports/round4-mac-embedding-sweep-evidence.md` | Migrated in M2; Linux M2 audit PASS. |
| Youden's J is a dial, not a default threshold recommendation. | Plateau-midpoint caveat recorded; no production threshold claim. | `docs/reports/round4-youden-j-tuning.md` | Migrated in M2; report frames J-max as a review-load stress point. |
| Embeddings should augment AGT policy, not replace it. | On frozen test, `policy_plus_embedding` reduced unsafe-action success vs `policy_only_gate` by `0.040761` absolute with unchanged hard-block FP `0.139665` and approval-load FP `0.0`. Validation still has `80` critical allows. | `artifacts/governance-eval/metrics.json`; `docs/reports/round4-governance-eval-evidence.md` | Migrated in M3; Linux M3 audit PASS. Research readout only; not default blocking or production evidence. |

## Baseline Pinning Requirement

The "about 1%" rules-only catch-rate claim is the most important number to
anchor before upstreaming. It means:

```text
AGT Rust prompt-injection detector at a specific commit and detector-file hash,
scored on this synthetic hard held-out corpus, caught 180 of 17,600 attack rows.
```

It does not mean AGT generally catches only 1% of prompt-injection attacks.
Before any AGT PR is opened, rerun the rules-only harness against fresh AGT
upstream `main` and record the commit SHA, detector SHA-256, command, corpus
manifest hash, and resulting TP/FP rates. Current local cross-check:
`prompt_injection.rs` matches AGT commit
`1bf359397df64aeb5285bdf5d609ade291c329b9` with SHA-256
`92ac1f855e03502886fffdfb8cf9eece8ce7c2bea268ecacb4ff6386cb345ab3`.

## Wording Guardrails

- Say "labelled examples" or "technique-labelled examples" unless reviewed
  source-derived artifacts are included.
- Say "synthetic research corpus" where the evidence comes from generated rows.
- Say "optional/default-off signal" rather than "replacement detector."
- Say "review/routing signal" rather than "auto-blocking."
- Say "not validated on real traffic" until that evidence exists.
- Say "not production safety evidence" until separate deployment evidence
  exists.

## Evidence Gaps Before Stronger Claims

| Stronger claim | Missing evidence |
|---|---|
| Validated on real traffic. | Real traffic sample, privacy review, and false-positive audit. |
| Source-derived public examples are folded in. | Reviewed source-derived pilot artifacts and independent audit. |
| Ready for default blocking. | Review-load budget, policy evaluation, and false-positive proof at realistic prevalence. |
| Governance integration is ready. | Validation split still has critical allows; needs policy/harness iteration plus independent audit. |
| Upstream optional embedding feature is ready. | PR 1 benchmark fixture review plus documented generation methodology and fresh AGT baseline pin. |
