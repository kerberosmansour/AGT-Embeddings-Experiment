# Round-6 cascade harness

Four-stage detection pipeline over the frozen round-4 corpus, evaluating
whether a de-obfuscation → trained-head → conformal-routing → governance-Gate-2
cascade widens the TP/FP gap beyond the round-4 single-dial kNN margin.

See `docs/RUNBOOK-round6-cascade-experiment.md` for the full contract and the §2
pre-registered accept/kill thresholds, and `docs/reports/round6-cascade-report.md`
for results.

## Environment

```bash
python3.13 -m venv .venv-round6
.venv-round6/bin/pip install --require-hashes -r meta/harness/round6-cascade/requirements.lock
```

The bge-small-en-v1.5 ONNX model downloads to `.cache/fastembed/` on first run
(SHA-256 pinned in each milestone freeze record). Embedding inference is local;
network use is model download only.

## Running (from repo root)

```bash
V=.venv-round6/bin/python
cd meta/harness/round6-cascade
$V run_m1_gate0_rescore.py        # Gate 0 + FP-zero rescore
$V run_m2_head.py                 # trained head + 8-fold LOFO
$V run_m3_buckets.py              # conformal three-bucket routing
$V run_m4_gate2.py                # tiered Gate-2 ablation
$V run_m5_summary.py              # aggregation + report
$V validate-round6-cascade.py all # artifact validator (fails closed)
$V -m unittest discover -p "test_*.py"
```

Each runner writes metadata-only artifacts to `artifacts/round6-cascade/m<N>-*/`
(ids, labels, scores, decisions, transform tags — never raw text). Selection is
validation-only; the test split is scored once per frozen configuration, with a
freeze record written before test scoring.

## Modules

- `normalize.py` — Gate 0 pure de-obfuscation (closed transform-tag enum).
- `common.py` — shared embedding / kNN / metrics / Wilson / metadata-only writers.
- `head.py`, `buckets.py`, `gate2.py` — Gate 1 / routing / Gate 2 logic.
- `run_m*.py` — per-milestone runners. `validate-round6-cascade.py` — validator.
