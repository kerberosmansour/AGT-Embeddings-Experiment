# Round-4 Embedding/kNN Sweep Contract

Date: 2026-06-08
Owner: mac-agent
AgentBus task: `t_mq5sspfi_302_aa06c2bb`
Status: contract only; no embedding run has started

## Purpose

Define the first permitted embedding/kNN sweep after the large corpus audit.
This contract is intentionally narrower than the full AGT policy hypothesis. It
answers only:

```text
Does an offline embedding margin over the audited Round-4 corpus carry
classification signal beyond the weak Rust rules-only baseline, without leaking
test information into threshold selection?
```

It does not test AGT policy metadata, source-derived rows, candidate AGT
detectors, fine-tuning, or production readiness.

## Hard Boundary

Allowed now:

- write this contract;
- review this contract on AgentBus;
- after Linux acknowledgement, run a bounded local/offline embedding sweep on
  Mac under the scratch path named below.

Not allowed in this task:

- importing source-derived rows;
- calling hosted embedding/model APIs;
- fine-tuning or changing embeddings with test labels;
- selecting a threshold from the frozen test split;
- changing Rust AGT detector rules or policy decisions;
- claiming production safety, ASI coverage, or detector promotion.

## Inputs

The sweep may use only these committed PR40 artifacts:

| Input | Required check before run |
|---|---|
| `corpus/round4/injection-round4-large.jsonl` | SHA-256 matches `manifest-large.json` |
| `corpus/round4/manifest-large.json` | `row_count=44800`; output hash present |
| `corpus/round4/check-large-summary.json` | split/leakage/duplicate gates pass |
| `corpus/round4/rules-baseline-large-metrics.json` | baseline comparison only |
| `corpus/round4/rules-baseline-large-provenance.json` | AGT provenance recorded |

Current audited split counts:

```text
exemplar_bank 28504 rows: 11160 attack / 17344 benign
validation     6888 rows:  2760 attack /  4128 benign
test           9408 rows:  3680 attack /  5728 benign
```

Current audited hygiene:

```text
family split leaks 0
group split leaks 0
exact normalized cross-split leaks 0
near-duplicate cross-split leaks 0
manifest hash mode byte_exact
```

## Split Protocol

The split meanings are frozen:

| Split | Permitted use |
|---|---|
| `exemplar_bank` | fit nearest-neighbor banks, optional centroid/cache construction, no operating threshold selection from final outcomes |
| `validation` | choose model arm, `k`, margin aggregation, abstain band, and operating threshold |
| `test` | one final read after all choices are frozen |

Before touching `test`, the runner must write and commit or attach a freeze
record with:

```json
{
  "model_id": "local-model-name",
  "model_version": "version-or-commit",
  "model_sha256": "sha256-or-unavailable-with-reason",
  "runtime": "fastembed/onnx/other-local-runtime",
  "embedding_dimension": 384,
  "normalization": "cosine_l2_normalized",
  "k": 5,
  "positive_bank_filter": "attack_class != benign",
  "negative_bank_filter": "attack_class == benign",
  "margin_formula": "mean_topk_positive_cosine - mean_topk_negative_cosine",
  "threshold_tau": 0.0,
  "abstain_band": null,
  "selected_on": "validation",
  "corpus_sha256": "33a02ac2b22e68970b3b808c5ba95bc119dc87dd93ae6dbc90546c074a5980ed"
}
```

If multiple models are tried, the selected model must be chosen using validation
only. Test results from losing model arms may be reported only after the winner
and all thresholds are frozen.

## Scoring Primitive

For each non-exemplar row:

```text
s_pos  = mean cosine similarity to top-k attack exemplar rows
s_neg  = mean cosine similarity to top-k benign exemplar rows
margin = s_pos - s_neg
pred_attack = margin > threshold_tau
```

Optional variants are allowed only if they are declared before the run:

- per-attack-class positive banks;
- per-benign-subclass negative banks;
- distance-as-abstain band around `threshold_tau`;
- one-vs-rest `attack_class` analysis for diagnostics.

All variants must use the same freeze discipline. A variant that sees test
results before its threshold is fixed is invalid.

## Per-Row Output Contract

Per-row outputs must be metadata-only. They may include:

```json
{
  "id": "row-id",
  "split": "validation-or-test",
  "label": "attack-or-benign",
  "attack_class": "direct_override",
  "benign_subclass": "not_applicable",
  "bypass_class": "plain",
  "source_type": "user",
  "trust_level": "untrusted",
  "expected_action": "block",
  "contains_sensitive_sink": true,
  "requires_tool_call": false,
  "family_id": "family-id",
  "group_id": "group-id",
  "s_pos": 0.0,
  "s_neg": 0.0,
  "margin": 0.0,
  "threshold_tau": 0.0,
  "pred_attack": false,
  "top_positive_neighbor_ids": ["row-id"],
  "top_negative_neighbor_ids": ["row-id"]
}
```

They must not include `text`, `raw_text`, `prompt`, `content`, model prompts, or
source excerpts. Neighbor evidence is by row ID only.

## Metrics Contract

The validation and test reports must include:

- attack recall with Wilson 95 percent interval;
- benign false-positive rate with Wilson 95 percent interval;
- false positives per 1k benign;
- adjacent-security benign false positives, especially
  `benign_security_discussion`, `quoted_injection_example`,
  `security_training_material`, `research_blog_excerpt`,
  `security_changelog`, `detector_code_fixture`, `owasp_ncsc_guidance`, and
  `docs_code_comment`;
- precision adjusted to 1 attack per 100 benign and 1 attack per 1000 benign;
- ROC-AUC and PR-AUC if implemented without test threshold fitting;
- by-`attack_class`, by-`benign_subclass`, by-`bypass_class`, by-`source_type`,
  by-`trust_level`, and by-`expected_action` breakdowns;
- confusion matrix for validation and final test.

Base-rate precision must use:

```text
prevalence = 1 / (benign_per_attack + 1)
precision  = recall * prevalence /
             (recall * prevalence + fp_rate * (1 - prevalence))
```

The report must compare against the audited Rust rules-only baseline, including
the fact that the baseline is poor:

```text
rules_only attack recall 180/17600 = 0.010227
rules_only benign FP 2136/27200 = 0.078529
rules_only base-rate precision 0.001300655 at 100:1
rules_only base-rate precision 0.000130218 at 1000:1
```

## Resource Budget For The Future Run

The first execution spike must declare:

- artifact path:
  `artifacts/embedding-sweep/`;
- CPU: Mac local CPU/GPU/ANE only as supported by the local runtime;
- memory: stop and record if resident memory exceeds 16 GB;
- time: stop and record if wall time exceeds 4 hours;
- network: no hosted inference or external providers; model download allowed
  only if the model/version/license/hash is recorded and the cache stays
  git-ignored;
- data: audited synthetic Round-4 corpus only.

If the run exceeds budget, stop and publish the partial evidence as blocked.

## Required Pre-Run Commands

Before any embedding computation:

```bash
python3 corpus/round4/check-round4.py \
  corpus/round4/injection-round4-large.jsonl \
  --manifest corpus/round4/manifest-large.json \
  --summary-json /tmp/round4-check-before-embedding.json

python3 meta/harness/round4-report/validate-round4-gates.py \
  --profile large \
  --metrics corpus/round4/rules-baseline-large-metrics.json \
  --check-summary corpus/round4/check-large-summary.json \
  --out /tmp/round4-large-gate-before-embedding.json
```

The regenerated checker and gate summaries must match the committed pass
conditions. Any mismatch blocks the run.

## Required Post-Run Gates

A future sweep can be considered audit-ready only if:

- the freeze record exists and predates test scoring;
- validation and test outputs pass the metadata-only field check;
- no raw text fields appear in per-row outputs, summaries, metrics, or reports;
- all model/runtime/provenance fields are present;
- metrics include base-rate precision and adjacent-security benign FP;
- the report clearly states whether the embedding signal is useful, weak, or
  negative;
- Linux independently reruns the metric summary from per-row outputs.

## Safety Check

- Data classification: Internal synthetic experiment contract only.
- Raw secrets present? no.
- Non-AGT data-classification track present? no.
- External service called? no.
- Scratch path: future run only, listed above.
- Cleanup required: none for this contract.
- Abuse sketch: the risk is test-set leakage through model, `k`, or threshold
  selection. This contract requires a validation-only freeze record before any
  test readout.
