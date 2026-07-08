# Verification Report - agtrtc Milestone 2

## What was exercised
| Scenario | Category | How exercised | Result | Evidence |
|---|---|---|---|---|
| `oc-agtrtc-2` one-family report | Outcome | Ran `AGTRTC_OUT=<tmp> bash benchmarks/agent-redteam/run-consolidated-smoke.sh` and inspected `consolidated_report.json`. | pass | Report has `family=indirect_injection`, `l1_rows=2`, `l2_rows=2`, `l3_live_rows=0`, evidence levels `L1_static` and `L2_mock_behavioural`, and `failure_bar_clear=true`. |
| `oc-agtrtc-3` no fake L3 | Outcome/security | Ran `python3 benchmarks/agent-redteam/consolidated/bridge.py --out <tmp> --live`. | pass | Command exited 1 with `M2 refuses --live: L3 deferred to M4 sandbox and budget readiness`; no L3 rows were written. |
| indirect slice report | Happy path | Ran `python3 -m unittest benchmarks/agent-redteam/tests/test_consolidated.py -v` and consolidated smoke. | pass | `test_oc2_consolidated_smoke_report` passed; smoke emitted L1/L2 joint matrix and raw-free OK. |
| missing sandbox | Dependency failure | Focused test drives the `--live` refusal path. | pass | `test_live_request_refuses_without_fake_l3` passed. |
| raw payload leak | Abuse case | Focused test injects a raw-like payload-ref field and expects closed failure. | pass | `test_raw_payload_ref_field_fails` passed. |
| action contained but undetected | Off-diagonal | Focused test inspects joint matrix. | pass | `test_report_has_undetected_contained_off_diagonal` passed; matrix includes `undetected -> contained: 1`. |
| detected but executed | Off-diagonal/failure bar | Focused test builds a report with `detected -> executed`. | pass | `test_detected_executed_fails_failure_bar` passed; the cell increments and `failure_bar_clear=false`. |
| sample bound | Boundary | Focused test exceeds the M2 max row cap. | pass | `test_sample_size_bound` passed. |
| artifact L3 absence | Boundary/security | Focused test scans smoke artifacts for forbidden L3 evidence enum. | pass | `test_no_l3_in_smoke_artifacts` passed. |
| existing AGT redteam smoke | Regression | Ran `bash benchmarks/agent-redteam/run-smoke.sh`. | pass | 24 scenarios validated, 6 traces, 5 blocked attempts, `certification_claim:false`, raw-free OK. |

## Bugs found
| id | severity | scenario | regression test | status |
|---|---|---|---|---|
| none | N/A | N/A | N/A | No runtime bugs found in M2 verification. |

## Environment
- macOS shell: `zsh`.
- Python: `python3` only; `python` is not assumed by this runbook.
- Browser/UI: N/A, CLI-only milestone.
- Network/live model/provider: N/A for M2; `--live` intentionally refuses.

## Pass 4 Security
| Check | Result | Evidence |
|---|---|---|
| Secrets/raw text surface | pass | Smoke raw-free gate passed; M2 sample manifest stores payload ids, family, split, and hashes only. |
| Evidence-level inflation | pass | M2 artifacts contain zero L3 rows; live request refuses before output. |
| Supply-chain | N/A | M2 adds no dependencies and uses Python stdlib only. |
| DAST | N/A | No HTTP service or UI surface. |

## Pass 5 AI Tolerance
| Check | Result | Evidence |
|---|---|---|
| AI tolerance contract | N/A | M2 is deterministic mock/metadata tooling with no live model calls. |

## Pass 6 Measurement
| Check | Result | Evidence |
|---|---|---|
| M2 one-family metrics | pass | Report records row counts, off-diagonal counts, wall-clock milliseconds, per-row wall-clock milliseconds, and `failure_bar_clear`. |

## Coverage gaps
- M2 intentionally does not provide L3 live behavioural evidence. That is deferred to M4, where sandbox and budget readiness are the gate.
- M2 covers one family only (`indirect_injection`) by design; full static scale-out belongs to M3.
