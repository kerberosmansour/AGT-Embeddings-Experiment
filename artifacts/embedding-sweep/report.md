# Round-4 Embedding Sweep Report

Status: research-corpus readout, not a certification or production-security assurance.

Model: `BAAI/bge-small-en-v1.5` via fastembed/ONNX Runtime.
Selected on validation: k=5, tau=0.08026764, objective=max_validation_base_rate_f1_100_with_min_tp.
Freeze record: `artifacts/embedding-sweep/freeze-record.json` sha256 `72429ea1222c9091c892f707bf326d3b5fda12de7371c39cd563125400934946`.

## Validation

- ROC-AUC: 0.918532
- PR-AUC/AP: 0.839878
- recall: 0.218478
- benign FP rate: 0.000000
- FP per 1k benign: 0.000
- base-rate precision 100:1: 1.000000 (Wilson-derived 0.686362-1.000000)
- base-rate precision 1000:1: 1.000000 (Wilson-derived 0.179547-1.000000)
- adjacent-security benign FP: 0

## Frozen Test

- ROC-AUC: 0.924454
- PR-AUC/AP: 0.856893
- recall: 0.141848
- benign FP rate: 0.000000
- FP per 1k benign: 0.000
- base-rate precision 100:1: 1.000000 (Wilson-derived 0.661463-1.000000)
- base-rate precision 1000:1: 1.000000 (Wilson-derived 0.163452-1.000000)
- adjacent-security benign FP: 0

## Baseline Context

- Rules-only baseline remains the negative control; compare against `corpus/round4/rules-baseline-large-metrics.json`.
- Test marginal recall delta vs rules-only rate: 0.131621.
- Test marginal FP-rate delta vs rules-only rate: -0.078529.
- Test TP delta vs rules-only rate on this split: 484.364.
- Test FP delta vs rules-only rate on this split: -449.816.
- The embedding signal is not an AGT policy or production detector claim.
