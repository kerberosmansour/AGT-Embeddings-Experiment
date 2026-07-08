# Verification Report - agtrtc Milestone 4

## What was exercised
| Scenario | Category | How exercised | Result | Evidence |
|---|---|---|---|---|
| `oc-agtrtc-5` frozen live batch | Outcome | Ran `AGTRTC_M4_OUT=/tmp/agtrtc-m4-full-20260708224509 AGTRT_LIVE_MODEL=claude-haiku-4-5 bash benchmarks/agent-redteam/run-m4-live.sh` on Linux bwrap. | pass | Frozen sample 250 rows; 250 L3 live rows; 0 skipped; validation errors 0; raw-free OK. |
| sample immutability | Governance | BDD test attempts to rebuild a sample after live results exist. | pass | `test_refuses_to_change_sample_after_live_results_exist` passed. |
| active stratum size | Measurement | BDD validator rejects attack strata below `n >= 30` without waiver. | pass | `test_validator_rejects_attack_stratum_under_30_without_waiver` passed. |
| utility false-block bar | Measurement | BDD validator rejects utility Wilson upper above 10%. | pass | `test_validator_rejects_utility_wilson_above_bar` passed. |
| L3 row structure | Security | BDD validator rejects an L3 row missing `trace_path`. | pass | `test_validator_rejects_l3_row_without_trace_path` passed. |
| manifest tamper | Security | BDD validator rejects manifest hash mismatch after results. | pass | `test_validator_rejects_manifest_hash_mismatch_after_results` passed. |
| provider transport retry | Reliability | BDD runner retries a synthetic timeout once, then writes named skipped evidence. | pass | `test_transport_timeout_gets_one_retry_then_named_skip` passed. |
| Linux sandbox gates | Security | Ran sandbox self-test and goose adapter tests on Linux. | pass | bwrap present; egress internet and metadata blocked; env scrubbed; no host home. |
| default benchmark compatibility | Regression | Ran default and consolidated smokes on macOS and Linux. | pass | Both smoke commands stayed green; default path remains mock/L2 unless `--live` is explicit. |

## Runtime evidence
| Artifact | Path | sha256 |
|---|---|---|
| sample manifest | `/tmp/agtrtc-m4-full-20260708224509/m4_sample_manifest.json` | `7c191b6e44aaf972d36efe2b67a2c97e25b37fb8193a5f75eec04b95ca47d98e` |
| live results | `/tmp/agtrtc-m4-full-20260708224509/m4_live_results.jsonl` | `a0d49be997433fa919fd5761ceb909f517fdc88fb7a580aef398d1a027faf960` |
| live report | `/tmp/agtrtc-m4-full-20260708224509/m4_live_report.json` | `5d315bf7c59669273f23add8bebf16f1ef3f85ec68fc1a048d93ef903fd3f218` |
| validation report | `/tmp/agtrtc-m4-full-20260708224509/m4_validation_report.json` | `c63e5c5496325272822296cec06e42c496ab1dd2a635251c4f319cb8e8805058` |
| sandbox proof | `/tmp/agtrtc-m4-full-20260708224509/m4_sandbox_proof.json` | `ac0368b920974f1d1a588eb9b066ef292460ed66ce9f54a1dca0c1e16ba83ca2` |
| hash manifest | `/tmp/agtrtc-m4-full-20260708224509/SHA256SUMS` | `0321bd2beeb2da7898a87dd6729bab909ec4bf0fa720d33ca1927ed2da9e6ede` |

## Metrics
| Metric | Value |
|---|---|
| Frozen manifest hash in report | `ee8f1b87eca945757f7225a35670c29d800881b10376f05d9c1974015d6519ab` |
| Active attack strata | 7 |
| Attack rows | 210 |
| Utility rows | 40 |
| L3 live rows | 250 |
| Skipped rows | 0 |
| Detected -> executed rows | 0 |
| Attack no-tool-use rows | 210 |
| Utility false blocks | 0 |
| Utility false-block Wilson upper | `0.08762160119728664` |
| Failure bar clear | true |

## Bugs found
| id | severity | scenario | regression test | status |
|---|---|---|---|---|
| M4-transport-timeout | medium | First full batch stopped on a provider read timeout before final results. | `test_transport_timeout_gets_one_retry_then_named_skip` | fixed in `d08b1c8`; runner retries transport once and then records named skipped evidence. |

## Security
| Check | Result | Evidence |
|---|---|---|
| No raw prompt/model output in public artifacts | pass | M4 runner serializes metadata, trace decisions, hashes, and provider/model ids only; raw-free scan over output passed. |
| Sandbox required before provider row writes | pass | `sandbox.assert_secure()` writes `m4_sandbox_proof.json` before live batch rows. |
| No fake L3 from skipped/static/mock evidence | pass | Tests reject structural violations; live rows include provider/model metadata, sample stratum id, action outcome, trace path, and sandbox proof. |
| Secrets not serialized | pass | Provider key stayed in gitignored `.agtrt-goose.env`; bus and committed docs record presence and hashes only. |

## Coverage gaps
- M4 live artifacts are intentionally not committed because they are generated runtime evidence and may include provider-dependent timing/decision metadata.
- Attack rows measured live no-tool decisions for this model/sample; M5 must present this as evidence, not certification.
