# Verification Report - agtrtc Milestone 5

## What was exercised
| Scenario | Category | How exercised | Result | Evidence |
|---|---|---|---|---|
| `oc-agtrtc-7` joint release report | Outcome | Ran fresh full L1 on Linux, then joined it with real M4 artifacts using `run-release-gate.sh`. | pass | `/tmp/agtrtc-m5-release-20260708233153/release`, `failure_bar_clear=true`. |
| `oc-agtrtc-8` escaped display text | Security | BDD fixture renders malicious family text into Markdown/HTML. | pass | `test_oc8_malicious_display_text_is_literal_and_banner_first` passed. |
| `cuj-agtrtc-5` release manifest path | Front-to-end | CLI path: manifest -> hash validation -> report -> joint matrix -> backlog -> raw-free scan. | pass | `test_cuj_release_cli_front_to_back` passed; Linux raw-free scan OK. |
| Evidence inflation guard | Security | BDD fixture changes an M4 row from L3 to L1. | pass | `test_rejects_static_rows_as_live_evidence_inflation` rejects static-as-live. |
| Manifest tamper guard | Security | BDD fixture tampers the L1 report after manifest creation. | pass | `test_release_manifest_hashes_and_tamper_fail_closed` fails closed. |
| Utility visibility | Measurement | Report exposes utility rows, false-block count/rate, and Wilson bar. | pass | Real M5 report: `utility_false_blocks=0`, `false_block_rate=0.0`. |
| No-certification wording | Claims | JSON/MD/HTML outputs keep `certification_claim=false` and no badge/certified terms. | pass | M5 BDD and raw-free/no-cert checks passed. |
| Regression suite | Regression | Ran Mac and Linux benchmark test discovery plus smoke commands. | pass | Mac: 104 OK / 5 skips. Linux: 104 OK / 2 skips. Smokes OK on both. |

## Runtime evidence
| Artifact | Path | sha256 |
|---|---|---|
| release manifest | `/tmp/agtrtc-m5-release-20260708233153/release/release_manifest.json` | `dbdef2878a9fd9ba3a96b3d939169805edb3f6426122ec717f05bd69f25e4c87` |
| joint scorecard JSON | `/tmp/agtrtc-m5-release-20260708233153/release/joint_scorecard_report.json` | `5970123f3a6d128e30a74f6aea1244303fa6e172e40431296b2b7df9e0c0870e` |
| joint scorecard Markdown | `/tmp/agtrtc-m5-release-20260708233153/release/joint_scorecard_report.md` | `342e7487613ce2945efcd4bbb56a2eb6594329f03784a133775a6b1436735258` |
| joint scorecard HTML | `/tmp/agtrtc-m5-release-20260708233153/release/joint_scorecard_report.html` | `112ac4b41c2cec69304ff9f923fca63dc39c1ff887d7e6f26b77fad5f015cb85` |
| release validation | `/tmp/agtrtc-m5-release-20260708233153/release/release_validation_report.json` | `d78e12a66e8c2bb176b702306a19e59d3946722b71ec4c7cf3feeff35d723fd0` |
| hash manifest | `/tmp/agtrtc-m5-release-20260708233153/release/SHA256SUMS` | `c0260e0507e21ca878cbb54c668d3a00186b798a0da015b20981c8f894e12f86` |

## Manifest inputs
| Input | sha256 |
|---|---|
| L1 artifact hash | `a316dae2f2dfe7a935f13fd9ebc24532b067b29d6b508ec7cabf19e4045b34d0` |
| L3 sample manifest hash | `7c191b6e44aaf972d36efe2b67a2c97e25b37fb8193a5f75eec04b95ca47d98e` |
| report hash in manifest | `5970123f3a6d128e30a74f6aea1244303fa6e172e40431296b2b7df9e0c0870e` |
| corpus manifest hash | `bb23a1fc519ffd4726b71025e1c371e05b6f5a86ee2802eee3f39dc650e7f4dc` |
| scenario set hash | `fc731200ff93d5bdd8456c02dc38dd7822c8b32046ea324ac3e44c3355c2a3b8` |

## Metrics
| Metric | Value |
|---|---|
| L1 rows | `54034` |
| M4 rows joined | `250` |
| M4 L3 live rows | `250` |
| Joint matrix complete | `true` |
| Release validation failure bar | `true` |
| Utility false blocks | `0` |
| Utility false-block rate | `0.0` |
| Detected -> executed | `0` |
| Undetected -> contained | `0` |
| Empty L3 strata | `[]` |
| High-miss backlog count | `7` |

## Bugs found
| id | severity | scenario | regression test | status |
|---|---|---|---|---|
| none | n/a | n/a | n/a | n/a |

## Security
| Check | Result | Evidence |
|---|---|---|
| No static-as-live inflation | pass | BDD test rejects non-L3 M4 rows before report creation. |
| Hash mismatches fail closed | pass | Release validation recomputes L1, M4 manifest, scenario-set, and report hashes. |
| Report injection guard | pass | Markdown/HTML renderer escapes display strings. |
| Raw-free release output | pass | `python3 benchmarks/agent-redteam/hygiene/raw_free_scan.py /tmp/agtrtc-m5-release-20260708233153/release` returned OK. |
| No secrets or raw model output | pass | Release artifacts contain metadata, paths, aggregate counts, and hashes only. |

## Coverage gaps
- Generated M4/M5 runtime artifacts remain in `/tmp`; they are intentionally referenced by paths and hashes instead of committed.
- The release report is evidence, not certification or production safety evidence.
