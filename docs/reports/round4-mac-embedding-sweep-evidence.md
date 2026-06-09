# Round-4 Mac Embedding Sweep Evidence

Date: 2026-06-09
Owner: mac-agent
AgentBus task: `t_mq6i8w0r_739_6e91733b`
Status: completed Mac execution; awaiting Linux audit

## Claim Boundary

This is a research-corpus readout, not a certification or
production-security assurance.

The run does not claim ASI/AIVSS coverage, source-material coverage, production
safety, detector promotion, or AGT policy effectiveness. It tests only whether
an offline embedding margin over the audited Round-4 corpus carries signal
beyond the weak Rust rules-only baseline, with validation-selected parameters
and a frozen test readout.

## Inputs

- Corpus: `corpus/round4/injection-round4-large.jsonl`
- Corpus SHA-256: `33a02ac2b22e68970b3b808c5ba95bc119dc87dd93ae6dbc90546c074a5980ed`
- Manifest: `corpus/round4/manifest-large.json`
- Baseline: `corpus/round4/rules-baseline-large-metrics.json`
- Pre-run checks:
  - `check-round4.py` large summary: PASS and byte-identical to committed summary.
  - large report gate: PASS and byte-identical to committed gate JSON.

## Runtime

- Runtime: `fastembed/onnxruntime-local`
- Model: `BAAI/bge-small-en-v1.5`
- License: MIT
- Embedding dimension: 384
- Model file SHA-256: `51f1bd0addd6e859e42c2c8021a5e5461385bb676a649f4b269aa445449f2431`
- Network: model download/cache only; no hosted inference or provider scoring.
- Artifact path: `artifacts/embedding-sweep/`
- Actual budget: 705.035 seconds, max RSS 8.178 GiB, below the 4 hour / 16 GiB budget.

## Freeze

- Selected on validation only: `k=5`, `threshold_tau=0.08026763573288917`
- Objective: `max_validation_base_rate_f1_100_with_min_tp`
- Freeze record:
  `artifacts/embedding-sweep/freeze-record.json`
- Freeze SHA-256: `72429ea1222c9091c892f707bf326d3b5fda12de7371c39cd563125400934946`
- Test-start record:
  `artifacts/embedding-sweep/test-start-record.json`
- Test-start SHA-256: `9371c84a7461c60b591a555f387dd579c27c0d392e8a32a1a31d4e17c837e26d`

## Validation Readout

- Rows: 6,888
- Confusion: TP 603 / FN 2,157 / FP 0 / TN 4,128
- ROC-AUC: 0.918532
- PR-AUC / average precision: 0.839878
- Attack recall: 0.218478
- Benign false-positive rate: 0.000000
- FP per 1k benign: 0.000
- Base-rate precision, 1 attack per 100 benign: empirical 1.000000; Wilson-derived interval 0.686362-1.000000
- Base-rate precision, 1 attack per 1000 benign: empirical 1.000000; Wilson-derived interval 0.179547-1.000000
- Adjacent-security benign false positives: 0

## Frozen Test Readout

- Rows: 9,408
- Confusion: TP 522 / FN 3,158 / FP 0 / TN 5,728
- ROC-AUC: 0.924454
- PR-AUC / average precision: 0.856893
- Attack recall: 0.141848
- Benign false-positive rate: 0.000000
- FP per 1k benign: 0.000
- Base-rate precision, 1 attack per 100 benign: empirical 1.000000; Wilson-derived interval 0.661463-1.000000
- Base-rate precision, 1 attack per 1000 benign: empirical 1.000000; Wilson-derived interval 0.163452-1.000000
- Adjacent-security benign false positives: 0

## Marginal Value Vs Rules-Only Baseline

Rules-only baseline on the large corpus:

- Attack recall: 0.010227
- Benign FP rate: 0.078529
- Base-rate precision at 100:1: 0.001300655
- Base-rate precision at 1000:1: 0.000130218

Frozen test comparison at the validation-selected embedding threshold:

- Attack recall delta: +0.131621
- Benign FP-rate delta: -0.078529
- Expected rules TP on this split: 37.636
- Observed embedding TP: 522
- TP delta vs rules rate: +484.364
- Expected rules FP on this split: 449.816
- Observed embedding FP: 0
- FP delta vs rules rate: -449.816

Interpretation: the threshold-free embedding signal is strong on this synthetic
research corpus, and the validation-selected high-precision operating point
removes the adjacent-security benign false-positive problem seen in the
rules-only baseline. The tradeoff is low recall at the frozen operating point:
about 14.2 percent on test. This supports "useful triage signal worth pursuing",
not a standalone detector or production control.

## Artifact Hashes

```text
72429ea1222c9091c892f707bf326d3b5fda12de7371c39cd563125400934946  freeze-record.json
3e7c6648e7e98838675b0b7671992d5a315a3e0b2a3e2cdf9475257a945d749b  provenance.json
92bec9488c12cf45352a934a4cb685e867b5da86e767e40cd52d43c45d86f552  report.md
64a4f4b71e716259ee7e2e6b0b8b9d95dd09d40584ab6b989568fd2f56912bab  test-metrics.json
b32cb78cbc4fd0352d59ed2b4e8a9fa94a32400dda6717e8a7c08e6ca6fe50fb  test-per-row.jsonl
9371c84a7461c60b591a555f387dd579c27c0d392e8a32a1a31d4e17c837e26d  test-start-record.json
25cf1f4cd8586c614740d1febce8cc67a3056cc9a2be2d7a14fc67719901ff23  validation-metrics.json
ad031b5cef9cc6992d104e480265e390feff86a51f3b3bc9bb8462a2b42d9354  validation-per-row.jsonl
f5ef2011ccf824641b2bd45bd4f333dbc3c08769122ba1bb343943035d5cf99f  youden-j-tuning.json
```

## Output Hygiene

- `validation-per-row.jsonl`: 6,888 rows, metadata-only.
- `test-per-row.jsonl`: 9,408 rows, metadata-only.
- Raw text fields checked absent: `text`, `raw_text`, `prompt`, `content`.
- Raw prompt/security phrases checked absent from artifacts.
- Neighbor evidence is row IDs only.

## Linux Audit Ask

Linux should independently validate:

1. Freeze record exists before test artifacts and matches
   `test-start-record.json`.
2. Per-row outputs contain no raw text-like fields.
3. Recomputed metrics from per-row outputs match `validation-metrics.json` and
   `test-metrics.json`.
4. Base-rate precision intervals and adjacent-security benign FP counts are
   preserved in any report.
5. The readout remains framed as a research-corpus result, not production
   assurance or certification.
