# Verification Report - agtrt-live Milestone 1

## What was exercised

| Scenario | Category | How exercised | Result | Evidence |
|---|---|---|---|---|
| Live probe schema/corpus | BDD | `python -m unittest benchmarks/agent-redteam/tests/test_measurement_suite.py` | pass | 240 rows, complete `live_probe`, all 24 evasion techniques covered |
| Goose expected-tool scoring | BDD | `python -m unittest benchmarks/agent-redteam/tests/test_goose_adapter.py` | pass | no-tool pass/fail and shell pass/fail cases covered |
| Goose batch summary | BDD | `python -m unittest benchmarks/agent-redteam/tests/test_goose_batch.py` | pass | `l3_rows`, `l3_trace_rows`, `no_trace_rows`, `failed_rows` covered |
| Scenario validator | Runtime | `python benchmarks/agent-redteam/schema/validate_scenarios.py <240 expanded paths>` | pass | 240 validated |
| Raw-free hygiene | Security | `python benchmarks/agent-redteam/hygiene/raw_free_scan.py benchmarks/agent-redteam` | pass | no data-artifact hits |
| Static syntax | Static | `python -m py_compile <changed Python files>` | pass | no syntax errors |
| Full discovery | Regression | `python -m unittest discover -s benchmarks/agent-redteam -p "test_*.py"` | pass | 87 tests, 9 skips on Windows |

## Bugs found

| id | severity | scenario | regression test | status |
|---|---|---|---|---|
| none | N/A | N/A | N/A | N/A |

## Coverage gaps

- No Windows L3 live run: this host lacks the Linux bwrap sandbox path.
- Cross-agent Linux/Mac rerun is pending on AgentBus after the branch is pushed.
