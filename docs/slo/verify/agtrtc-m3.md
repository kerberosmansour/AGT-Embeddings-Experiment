# Verification Report - agtrtc Milestone 3

## What was exercised
| Scenario | Category | How exercised | Result | Evidence |
|---|---|---|---|---|
| `oc-agtrtc-4` full L1 artifact | Outcome | Ran `run_l1_static.py --out <tmp>` then `validate_l1_static.py <tmp>/l1_static_report.json`. | pass | 54,034 rows validated; corpora are `round4-large` 44,800 rows and `round7-large` 9,234 rows; report records manifest/data hashes and zero validation errors. |
| full L1 artifact | Happy path | Focused unittest plus direct CLI run. | pass | `test_oc4_full_l1_artifact_validates_front_to_end` passed; direct run summary had `l1_rows=54034`, `l2_rows=0`, `l3_live_rows=0`. |
| recursive raw-free gate | Abuse case | Mutated first result row to include `prompt`. | pass | `test_validator_rejects_raw_prompt_like_key` passed with named raw-free failure. |
| freeze split guard | Governance | Mutated freeze record to `selection_split=test`. | pass | `test_validator_rejects_non_validation_freeze` passed. |
| static evidence guard | Abuse case | Mutated first result row to `L3_live_behavioural`. | pass | `test_validator_rejects_l2_or_l3_static_rows` passed. |
| hard-benign bar guard | Measurement | Mutated report to set hard-benign Wilson upper `0.101` with no residual analysis. | pass | `test_validator_rejects_hard_benign_bar_without_residual` passed. |
| existing AGT smoke | Regression | Ran `bash benchmarks/agent-redteam/run-smoke.sh`. | pass | 24 scenarios validated, 6 traces, 5 blocked attempts, `certification_claim:false`, raw-free OK. |
| M2 consolidated smoke | Regression | Ran `bash benchmarks/agent-redteam/run-consolidated-smoke.sh`. | pass | L1=2, L2=2, L3=0, `failure_bar_clear=true`, raw-free OK. |
| Round-7 harness compatibility | Regression | Ran existing validator over `artifacts/round7-garak/smoke/manifest.json` and `smoke-knn/manifest.json`. | pass | Both returned PASS. |

## Bugs found
| id | severity | scenario | regression test | status |
|---|---|---|---|---|
| none | N/A | N/A | N/A | No runtime bugs found in M3 verification. |

## Environment
- macOS shell: `zsh`.
- Python: `python3`.
- Browser/UI: N/A, CLI-only milestone.
- Network/live model/provider: N/A; M3 is static local corpus measurement only.

## Pass 4 Security
| Check | Result | Evidence |
|---|---|---|
| Raw-free artifact gate | pass | Recursive validator rejects raw-like keys and URL/email-like strings; focused raw-key abuse test passed. |
| Evidence-level inflation | pass | Validator rejects L2/L3 rows; actual report has 54,034 L1 rows and zero L2/L3 rows. |
| Freeze discipline | pass | Freeze record requires `selection_split=validation` and `test_scored_after_freeze=true`; mutation test fails closed. |
| Supply-chain | N/A | M3 adds no dependencies; stdlib-only Python. |
| DAST | N/A | No service or UI surface. |

## Pass 5 AI Tolerance
| Check | Result | Evidence |
|---|---|---|
| AI tolerance contract | pass | Deterministic static detector path; no live model calls. Config hash and frozen validation split are recorded. |

## Pass 6 Measurement
| Check | Result | Evidence |
|---|---|---|
| Full-corpus L1 metrics | pass | Report contains overall, split, family, and stratum metrics plus Wilson intervals and base-rate precision. |
| Hard-benign FP bar | pass | Wilson upper is `0.022666127761700065`, below the pre-registered `0.10` bar. |
| L3 sampling signal | pass | Report identifies 7 families needing L3 sampling: `direct_override`, `jailbreak`, `memory_poisoning`, `package_hallucination`, `prompt_leakage`, `terminal_escape_injection`, and `tool_result_injection`. |

## Coverage gaps
- M3 is L1 static-only. It does not prove live containment, action execution, or benign utility behavior; M4 must handle those with sandbox readiness.
- The static detector is a deterministic structural sidecar, not a production safety control or certification claim.
