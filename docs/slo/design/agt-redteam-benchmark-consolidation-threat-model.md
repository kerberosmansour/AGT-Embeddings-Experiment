# Threat Model - AGT Red Team Benchmark Consolidation

Status: frozen M1 Markdown threat-model artifact.
Owner: benchmark maintainer.
Date: 2026-07-08.

This artifact freezes the degraded inline threat-model rows from
`docs/RUNBOOK-agt-redteam-benchmark-consolidation.md` so later milestones can
cite stable `tm-agtrtc-abuse-*` IDs. It is intentionally metadata-only and does
not include raw payloads, prompts, URLs, emails, secrets, or PII.

## Scope

| Area | Summary |
|---|---|
| Assets | Corpus manifests, payload refs, scenario set, detector results, live traces, scorecards, model/API credentials. |
| Actors | Assessing engineer, benchmark maintainer, malicious payload contributor, compromised live model/tool, upstream reviewer. |
| Trust boundaries | Corpus input to benchmark harness; live adapter to OS sandbox; generated artifact to public/upstream boundary. |
| Entry points | JSONL corpus rows, scenario templates, live model output, CLI args, generated scorecard fields. |
| Residual risks | L3 cost and provider nondeterminism; owner: benchmark maintainer; review by M4 closeout. |

## Abuse Cases

| ID | Actor | Attack step | Impact | Required control | Verification milestone |
|---|---|---|---|---|---|
| `tm-agtrtc-abuse-1` | Malicious payload contributor | Adds raw prompt text, live URL/email, secret marker, or PII to a scenario, result, or report artifact. | Public/upstream artifact leaks sensitive or raw attack material. | Metadata-only serialization, raw-free validator, recursive forbidden-key/value scan before release. | M1 concept guard, M3/M5 full gate |
| `tm-agtrtc-abuse-2` | Benchmark maintainer | Summarizes an L1 static detector row as L3 live behavioral evidence. | Report overclaims containment and misleads the assessing engineer. | Closed evidence-level enum and result validation that rejects static-as-live rows. | M1/M5 |
| `tm-agtrtc-abuse-3` | Compromised live model/tool | Starts or continues a live adapter run without OS-enforced sandbox proof. | Real side effect, credential exposure, or false L3 evidence. | Sandbox refusal before provider/model execution and no in-process-only fallback. | M2/M4 |
| `tm-agtrtc-abuse-4` | Benchmark maintainer | Changes threshold, scenario-template selection, or L3 sample design after reading frozen test/live outcomes. | Test-set tuning hides detector or containment weakness. | Validation freeze record, sample manifest hash, and pre-read selection checks. | M3/M4/M5 |
| `tm-agtrtc-abuse-5` | Malicious payload contributor | Injects HTML/Markdown/control text into report display fields. | Stored report injection or misleading public scorecard. | Context-aware escaping and no-certification banner in report renderers. | M5 |
| `tm-agtrtc-abuse-6` | Benchmark maintainer | Hides benign utility false blocks behind an aggregate attack score. | A block-everything control appears safe despite unacceptable user impact. | Per-stratum utility reporting, false-block Wilson interval, and visible mitigation rows. | M4/M5 |

## Stable ID Rule

These IDs are append-only. Future milestones may add `tm-agtrtc-abuse-7+`, but
must not rename or renumber IDs 1 through 6. If a row is superseded, keep the ID
and add a supersession note.
