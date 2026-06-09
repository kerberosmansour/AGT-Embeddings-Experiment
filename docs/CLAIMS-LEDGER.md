# Claims Ledger

This ledger maps the public narrative to the evidence that must be migrated
into this repository.

## Narrative Claims And Evidence

| Narrative claim | Current evidence | Source artifact to migrate | Status |
|---|---|---|---|
| AGT rules-only detector has low recall on the hard held-out set. | `180 / 17600 = 0.010227` attack recall. | `corpus/round4/rules-baseline-large-metrics.json` | Ready to migrate. |
| AGT rules-only detector has material false positives on benign examples. | `2136 / 27200 = 0.078529` benign false-positive rate. | `corpus/round4/rules-baseline-large-metrics.json` | Ready to migrate. |
| The evaluation corpus has 44,800 labelled examples. | `row_count=44800`; split counts `28504 / 6888 / 9408`. | `corpus/round4/manifest-large.json`; `corpus/round4/check-large-summary.json` | Ready to migrate after content audit. |
| The split avoids family/group leakage. | Family leaks `0`; group leaks `0`; exact normalized cross-split leaks `0`; near-duplicate cross-split leaks `0`. | `corpus/round4/check-large-summary.json` | Ready to migrate. |
| Embedding/kNN at Youden's J catches about 88% on frozen test. | Test recall `0.882609` at threshold `-0.00609511`. | `experiments/.../youden-j-tuning.json`; `docs/.../round4-youden-j-tuning.md` | Ready to migrate with plateau caveat. |
| Embedding/kNN at Youden's J has about 16% false positives. | Test FPR `0.163059`, FP `934 / 5728`. | `experiments/.../youden-j-tuning.json`; `docs/.../round4-youden-j-tuning.md` | Ready to migrate. |
| Conservative embedding point has zero observed false positives. | Test recall `0.141848`, FPR `0.0`, FP `0`. | `experiments/.../youden-j-tuning.json`; embedding sweep artifacts | Ready to migrate. |
| Youden's J is a dial, not a default threshold recommendation. | Linux audit PASS with plateau-midpoint caveat; no production threshold claim. | `docs/.../round4-youden-j-tuning.md`; AgentBus #861 | Ready to migrate. |
| Embeddings should augment AGT policy, not replace it. | `policy_plus_embedding` reduced unsafe-action success vs `policy_only_gate` by `0.040761` absolute in synthetic metadata-only readout. | `docs/.../round4-governance-eval-evidence.md`; `meta/harness/round5-agt-value-add/` | Ready to migrate as research evidence only. |

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
| Governance integration is ready. | AGT semantics readback plus outcome-level audit on the migrated artifacts. |
