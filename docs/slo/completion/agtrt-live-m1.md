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
| Linux bounded live | 24/24 completed; 24 L3 rows; 8 expected contained shell traces; 16 expected no-tool passes; 0 failures |
| Linux full live | 240/240 completed; 240 L3 rows; 48 expected contained shell traces; 192 expected no-tool passes; 0 failures |

## Follow-Up

AgentBus M2 follow-up:

- Linux completed both the bounded slice and the full 240-row run on bwrap.
- Mac should still rerun deterministic tests and wrapper portability checks when
  available; task `t_mqkum7qp_313_5d549861` remains open.
