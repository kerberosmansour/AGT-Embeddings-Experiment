# Completion Summary — agtrt M3 (one-command smoke + CI)

**Outcome delivered (oc-3):** the assessing engineer runs the WHOLE assessment in one command (`run-smoke.sh`: validate → harness) and gets a single pass/fail with summaries; CI runs the same chain so a regression is caught automatically.

## Evidence

| Step | Command | Result |
|---|---|---|
| oc-3 front-to-end | `bash benchmarks/agent-redteam/run-smoke.sh` | validate (24/6 classes) → harness (6 traces/5 blocked) → `[smoke] OK`, exit 0 |
| Fail-fast | malformed scenario via `AGTRT_SCENARIOS` | non-zero, stops before harness, no `[smoke] OK` |
| Full tests | `python -m unittest discover -s benchmarks/agent-redteam -p "test_*.py"` | 30 passed (16 M1 + 9 M2 + 5 M3) |
| CI append-only | `readiness.yml` | existing `public-repo-readiness` job + steps unchanged; new `agt-redteam-smoke` job appended after |
| Static | `bash -n` + YAML parse + `git diff --check` | clean |

## What landed (M3 file allow-list)
- `benchmarks/agent-redteam/run-smoke.sh` — portable (`python`/`python3` fallback + bash array, no bare glob — DW-004 fixed), `set -euo pipefail` fail-fast, validate→harness chain, `AGTRT_SCENARIOS` override for testing.
- `.github/workflows/readiness.yml` — **appended** one job `agt-redteam-smoke` (setup-python 3.12 → `bash run-smoke.sh`); existing job untouched.
- `tests/test_smoke.py` — 5 tests: oc-3 front-to-end, fail-fast, CI append-only guards, `set -euo pipefail` check.

## Notes
- DW-004 (python3/glob portability, Win audit Finding 2) resolved here in `run-smoke.sh`.
- Python 3.12 pinned in the CI job (matches operator-readiness; the VM has 3.14 — stdlib-only is forward-compatible).

## DoD: met (outcome-first — oc-3 passes front-to-end). Tracker M3 → `done`.
