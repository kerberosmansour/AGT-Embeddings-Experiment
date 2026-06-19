# Completion Summary - agtrt-live Milestone 1

## Outcome

Completed. The 240-row measurement suite now has safe, non-secret live probes
per evasion technique and a Goose scoring contract that can distinguish catch
evidence from utility failures.

## Evidence

| Check | Result |
|---|---|
| Baseline affected tests before change | `OK (skipped=6)` across 22 tests |
| BDD-first failing tests | Failed on missing `live_probe`, old trace-only scoring, and missing batch summary fields |
| Affected unit tests after change | `OK (skipped=6)` across 27 tests |
| Full local discovery | `OK (skipped=9)` across 87 tests; Windows Bash-dependent smoke tests skip cleanly when Bash is absent |
| Scenario validation | 240 rows validated; 40 rows per trap class; 48 canonical, 96 evasion, 48 hard-benign, 48 near-miss |
| Raw-free scan | `raw-free: OK` |
| Py compile | Clean for changed Python files |
| L2 scorecard | 240 measured rows, 0 failures, no certification claim |

## Follow-Up

AgentBus M2 rerun remains pending after push:

- Linux should run the bounded `--live --limit=24` slice and report
  `l3_rows`, `l3_trace_rows`, `no_trace_rows`, `failed_rows`, and status counts.
- Mac should rerun deterministic tests and wrapper portability checks.
