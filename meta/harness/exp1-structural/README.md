# Experiment 1 — Structural Auto-Block Ceiling

Measures the fully-automated, no-human-review stack: round-6 Gate-0 + kNN at the
zero-FP point, OR'd with deterministic structural block rules (R1–R4) computed
from corpus governance fields. No embedding model is run — the zero-FP decision
is reused from `artifacts/round6-cascade/m1-gate0/test-per-row.jsonl`.

Run (from repo root):
    V=.venv-round6/bin/python
    cd meta/harness/exp1-structural
    $V run_exp1_eval.py
    $V validate-exp1.py
    $V -m unittest discover -p "test_*.py"

Results: docs/reports/exp1-structural-autoblock-report.md
Rules: see rules.py (R1 untrusted+tool; R2 sink+non-user; R3 trifecta; R4 R1∨R2).
Ground-truth fields (expected_action, risk_level) are forbidden rule inputs.
