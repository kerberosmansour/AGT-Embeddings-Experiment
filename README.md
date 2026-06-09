# AGT Embeddings Experiment

This repository contains a research corpus and evidence pack for evaluating
whether an embedding + nearest-neighbour signal can improve AGT
prompt-injection detection.

The central artifact is a large annotated prompt-injection evaluation dataset:

- `44,800` labelled examples;
- `17,600` attack examples across direct override, prompt leakage, indirect
  injection, tool abuse, tool-result injection, output exfiltration, memory
  poisoning, and data-boundary abuse;
- `27,200` benign examples covering security discussions, tool-use requests,
  quoted injection examples, documentation/code fixtures, support urgency,
  high-entropy structured data, and other non-attack controls;
- split into exemplar-bank, validation, and frozen test partitions with family,
  group, exact-duplicate, and near-duplicate leakage checks.

The dataset is synthetic research data. It is designed for controlled
measurement and reproducibility, not as proof of production safety or
real-traffic performance.

The research question:

```text
Can an embedding + nearest-neighbour signal give AGT better prompt-injection
detection evidence than the current rules-only detector, while staying optional,
tunable, and auditable?
```

## Method At A Glance

The experiment uses the existing AGT Rust prompt-injection rules as the
rules-only baseline, then compares that baseline with a local embedding margin:

- Embedding model: `BAAI/bge-small-en-v1.5`.
- Runtime: `fastembed/onnxruntime-local`.
- Model source: `qdrant/bge-small-en-v1.5-onnx-q`.
- Model license recorded in the artifact: MIT.
- Embedding dimension: `384`.
- Model file SHA-256:
  `51f1bd0addd6e859e42c2c8021a5e5461385bb676a649f4b269aa445449f2431`.
- Network use: model download/cache only; no hosted inference or provider
  scoring.
- Nearest-neighbour setting selected on validation: `k=5`.
- Conservative threshold selected on validation:
  `threshold_tau=0.08026763573288917`.

At evaluation time, each validation/test row is embedded locally and compared
against the exemplar bank. The committed artifacts store metadata-only
per-row readouts: row IDs, labels, nearest-neighbour scores, margins,
threshold decisions, and metrics. They intentionally do not store raw prompt
text in the embedding/governance readout artifacts.

## Evidence Snapshot

The current evidence compares the migrated AGT rules-only detector with
embedding/kNN operating points on the research corpus:

| Approach | Catch rate | False positive rate | Notes |
|---|---:|---:|---|
| AGT rules-only baseline | about `1%` | about `8%` | Current detector catches obvious patterns but misses most held-out attacks. |
| Embeddings at Youden's J point | about `88%` | about `16%` | Strong separation point, too noisy for default blocking. |
| Embeddings at zero-FP point | about `14%` | `0%` observed | Conservative high-confidence routing signal. |

The zero-FP operating point is the most conservative comparison: on the frozen
test split it raises observed attack catch rate from about `1%` to about `14%`
while keeping observed benign false positives at `0`. That is still research
evidence, not a guarantee of zero false positives in the wild.

The work is not proposing default auto-blocking. The embedding signal is an
optional, default-off, auditable layer that can feed downstream policy or review
routing.

## What Is In The Repo

- Corpus and corpus hygiene tools:
  - `corpus/round4/injection-round4-large.jsonl`
  - `corpus/round4/manifest-large.json`
  - `corpus/round4/check-round4.py`
  - `corpus/round4/run-smoke.sh`
- AGT rules-only baseline runner and metrics:
  - `tools/agt-rules-baseline/`
  - `corpus/round4/rules-baseline-large.jsonl`
  - `corpus/round4/rules-baseline-large-metrics.json`
- Embedding/kNN readouts:
  - `artifacts/embedding-sweep/`
  - `meta/harness/round4-embedding-sweep/`
  - `docs/reports/round4-youden-j-tuning.md`
- Governance/value-add metadata evidence:
  - `artifacts/governance-eval/`
  - `meta/harness/round4-governance-eval/`
  - `meta/harness/round5-agt-value-add/`
- Claim and methodology notes:
  - `docs/CLAIMS-LEDGER.md`
  - `docs/reports/`
  - `docs/OPEN-SOURCE-READINESS.md`

Some paths and reports use `round4` as the internal experiment label. Publicly,
the important thing is the research corpus, the frozen artifacts, and the
claim boundaries around them.

## How To Use This Repo

Start by reading the corpus manifest and the claims ledger:

```bash
cat corpus/round4/manifest-large.json
cat docs/CLAIMS-LEDGER.md
```

Run the smoke reproduction path:

```bash
bash corpus/round4/run-smoke.sh
```

Validate the committed embedding and governance artifacts:

```bash
python3 meta/harness/round4-embedding-sweep/validate-embedding-sweep.py \
  --provenance artifacts/embedding-sweep/provenance.json \
  --freeze artifacts/embedding-sweep/freeze-record.json \
  --validation artifacts/embedding-sweep/validation-per-row.jsonl \
  --test artifacts/embedding-sweep/test-per-row.jsonl \
  --validation-metrics artifacts/embedding-sweep/validation-metrics.json \
  --test-metrics artifacts/embedding-sweep/test-metrics.json

python3 meta/harness/round4-governance-eval/validate-governance-eval.py \
  --manifest artifacts/governance-eval/manifest.json \
  --validation artifacts/governance-eval/validation.jsonl \
  --test artifacts/governance-eval/test.jsonl \
  --metrics artifacts/governance-eval/metrics.json
```

For quick orientation, the most useful reports are:

- `docs/reports/round4-mac-embedding-sweep-evidence.md`
- `docs/reports/round4-youden-j-tuning.md`
- `docs/reports/round4-governance-eval-evidence.md`

For deeper details:

- Corpus shape, splits, leakage checks, and hashes:
  `corpus/round4/manifest-large.json` and
  `corpus/round4/check-large-summary.json`.
- Baseline AGT rules-only result:
  `corpus/round4/rules-baseline-large-metrics.json` and
  `tools/agt-rules-baseline/README.md`.
- Embedding model, runtime, threshold freeze, resource usage, and artifact
  hashes: `artifacts/embedding-sweep/freeze-record.json`,
  `artifacts/embedding-sweep/provenance.json`, and
  `docs/reports/round4-mac-embedding-sweep-evidence.md`.
- Youden's J threshold readout and why it is not a default threshold:
  `artifacts/embedding-sweep/youden-j-tuning.json` and
  `docs/reports/round4-youden-j-tuning.md`.
- Governance/value-add comparison:
  `artifacts/governance-eval/metrics.json` and
  `docs/reports/round4-governance-eval-evidence.md`.
- Claim-to-evidence mapping and stronger-claim gaps:
  `docs/CLAIMS-LEDGER.md`.

## What This Repo Does Not Claim

- unrelated product research tracks;
- unrelated data-classification experiments;
- raw secrets, live credentials, or customer data;
- production safety, certification, or benchmark-coverage claims;
- validation on real traffic;
- readiness for default blocking.

## Internal Migration Notes

The following files preserve the migration/audit trail used to extract this
research repo from the original experiment workspace:

- [`docs/RUNBOOK-agt-embeddings-migration.md`](docs/RUNBOOK-agt-embeddings-migration.md)
- [`docs/AGENTBUS-WORKSPLIT.md`](docs/AGENTBUS-WORKSPLIT.md)

They are included for provenance, but the main public value of the repository is
the corpus, validators, result artifacts, and reports.

## Community And Security

- [`CONTRIBUTING.md`](CONTRIBUTING.md)
- [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md)
- [`SECURITY.md`](SECURITY.md)
- [`CITATION.cff`](CITATION.cff)
