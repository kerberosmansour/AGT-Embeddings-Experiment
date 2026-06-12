# Ticket #15 - Round-7 Normalizer Pilot FP Triage

Source issue: https://github.com/kerberosmansour/AGT-Embeddings-Experiment/issues/15
Workpad: https://github.com/kerberosmansour/AGT-Embeddings-Experiment/issues/15#issuecomment-4693888897
AgentBus task: `t_mqb86bvt_49_ee78483c`
Target branch: `slo/issues-9-10-detection-improvements` (shared active experiment branch; dirty worktree already contains round-7 artifacts)
Stack: Rust normalizer crate + Python WS-C harness

## Smallest user-visible outcome

The round-7 measurement can distinguish transform-induced benign FPs from
threshold/score-distribution FPs, while keeping the AGT Rust normalizer
benign-safety contract explicit for ANSI terminal output.

## Sizing gate

| Row | Value |
|---|---|
| One user-visible outcome | yes - metadata-only FP attribution for #15/#16 follow-up |
| Changed files | <= 5 |
| Public surfaces | 1 metadata field set in `matrix-summary.json` |
| Migration | none |
| New dependency | none |
| One PR can review | yes |

Fits a single ticket.

## Compact architecture delta

`meta/harness/round7-garak/run_2x2.py` already emits paired old-vs-new
normalizer deltas. Extend that paired-delta block with a metadata-only
`new_benign_fp_attribution` section that records whether each new benign FP had
a changed normalized hash, which transform tags fired, and which benign
subclass/bypass bucket it belongs to. This keeps the fixed-detector experiment
honest: not every new FP is a decoder bug.

Add a Rust benign-safety regression test for colored terminal transcript output:
ANSI SGR color is stripped and tagged, but the content remains benign-normalized
with no new dependency or transform enum change.

## Contract block

| Field | Value |
|---|---|
| Files allowed to change | NEW `docs/slo/tickets/ticket-15-round7-normalizer-fp-triage.md`; `meta/harness/round7-garak/run_2x2.py`; `meta/harness/round7-garak/test_round7_garak.py`; `meta/harness/round7-garak/README.md` if command docs need updating; `rust/agt-normalize/src/lib.rs`; generated `artifacts/round7-garak/pilot-knn-attribution/**` |
| Files to read first | `docs/RUNBOOK-round7-garak-corpus.md`; `docs/proposals/agt-upstream-normalizer-rfc.md`; `docs/slo/tickets/ticket-16-round7-ws-c-2x2-measurement.md`; `meta/harness/round7-garak/{run_2x2.py,test_round7_garak.py,validate_round7_garak.py}`; `rust/agt-normalize/src/lib.rs`; `artifacts/round7-garak/pilot-knn/matrix-summary.json` |
| New files allowed | this ticket contract and generated artifact directory only |
| New dependencies | none |
| Migration allowed | no |
| Compatibility commitments | Existing manifest schema remains readable; new attribution fields are additive; Rust `normalize()` API and `Transform` enum stay stable |
| Data classification | Public metadata-only artifacts; raw corpus text may be inspected locally but never serialized to reports or issue comments |
| Proactive controls | C8 Protect Data Everywhere (no raw payload output), C9 Security Logging (closed transform tags), experiment governance (honest attribution) |
| Abuse scenarios | `tm-15-abuse-1`: raw text accidentally added to attribution rows -> validator/test fails. `tm-15-abuse-2`: threshold-caused FP blamed on a transform -> attribution must include normalized-hash-change boolean. |
| Resource bounds | attribution is O(number of paired test rows), capped examples already limited to 25 |
| Invariants/assertions | paired rows remain metadata-only; new FP attribution includes row ID, class/subclass, bypass, transform tags, score/threshold, and `normalized_changed`; no raw prompt/payload fields |
| Debugger expectation | inspect the two pilot FP rows by metadata, and only inspect raw text locally if necessary to understand transform behavior |
| Static-analysis gates | `py_compile`; harness unit test; `cargo test`; `garak_bypass.py`; artifact validator |
| Reversibility / rollback | remove additive attribution block and Rust test; no corpus or API migration |
| Exemplar to copy | existing `paired_delta()` and metadata-only records in `run_2x2.py`; existing benign-safety tests in `rust/agt-normalize/src/lib.rs` |
| Anti-exemplar | do not tune the detector threshold on test rows; do not weaken ANSI stripping just to improve the pilot metric; do not post raw examples publicly |
| AI tolerance contract | AI component exists only in kNN scorer mode. Accepted variance: deterministic local embeddings/model cache; evidence is aggregate metrics and row metadata only. Must-never: raw text in artifacts or issue comments. |
| Forbidden shortcuts | no corpus-template changes; no transform enum change for reporting only; no unbounded artifact output; no unlabeled “fixed” claim if pilot FPs remain |

## BDD scenarios

| Scenario | Category | Given | When | Then |
|---|---|---|---|
| transform-induced FP attribution | happy path | old benign record is not predicted and new benign record is predicted with a changed normalized hash | paired delta runs | attribution marks `cause_hint=normalizer_changed_view` and records new transform tags |
| threshold-caused FP attribution | happy path | old/new benign records have the same normalized hash but only the new cell predicts attack | paired delta runs | attribution marks `cause_hint=threshold_or_score_distribution` |
| metadata-only attribution | abuse / `tm-15-abuse-1` | attribution rows are serialized | validator walks artifacts | no `text`, `prompt`, `content`, `normalized_text`, raw URL, or raw email fields |
| benign ANSI regression | benign safety | a colored terminal transcript contains ANSI SGR color | Rust normalizer runs | `AnsiEscape` is tagged, ESC/control bytes are absent, content remains benign-normalized |
| no detector tuning | governance | pilot kNN is rerun | threshold is selected | validation-only zero-FP threshold protocol stays unchanged |

## Validation plan

| Check | Command | Expected |
|---|---|---|
| Repo hygiene | `git status --short --branch && git rev-parse --abbrev-ref HEAD && git symbolic-ref --short refs/remotes/origin/HEAD` | branch is non-default; dirty tree recorded |
| New test fails first | `python3 meta/harness/round7-garak/test_round7_garak.py` after adding attribution test before implementation | fails on missing attribution |
| Harness compile/tests | `python3 -m py_compile meta/harness/round7-garak/*.py && python3 meta/harness/round7-garak/test_round7_garak.py` | PASS |
| Rust tests | `cargo test --manifest-path rust/agt-normalize/Cargo.toml` | PASS |
| Garak bypass contract | `python3 corpus/round7/garak_bypass.py` | PASS |
| kNN pilot rerun | `.venv-round6/bin/python meta/harness/round7-garak/run_2x2.py --profile pilot --scorer knn --out-dir artifacts/round7-garak/pilot-knn-attribution` | writes manifest and attribution |
| Artifact validator | `python3 meta/harness/round7-garak/validate_round7_garak.py artifacts/round7-garak/pilot-knn-attribution/manifest.json` | PASS |
| Attribution inspection | inspect `artifacts/round7-garak/pilot-knn-attribution/matrix-summary.json` | new benign FPs separated into normalizer-changed vs threshold/distribution causes |

## Execution evidence

| Evidence | Result |
|---|---|
| Repo hygiene | branch `slo/issues-9-10-detection-improvements`; default `origin/main`; dirty tree pre-existed from round-7 work and was preserved |
| New tests fail first | harness tests failed on missing `new_benign_fp_attribution` before implementation |
| Harness compile/tests | PASS: `python3 -m py_compile meta/harness/round7-garak/*.py && python3 meta/harness/round7-garak/test_round7_garak.py` (`5` tests) |
| Rust tests | PASS: `cargo test --manifest-path rust/agt-normalize/Cargo.toml` (`34` tests) |
| Garak bypass contract | PASS: `python3 corpus/round7/garak_bypass.py` (`11/11`) |
| kNN pilot rerun | PASS: `.venv-round6/bin/python meta/harness/round7-garak/run_2x2.py --profile pilot --scorer knn --out-dir artifacts/round7-garak/pilot-knn-attribution` |
| Artifact validator | PASS: `python3 meta/harness/round7-garak/validate_round7_garak.py artifacts/round7-garak/pilot-knn-attribution/manifest.json` |
| Attribution result | 2 new benign FPs split into 1 `normalizer_changed_view` (`AnsiEscape,Lowercase`) and 1 `threshold_or_score_distribution` (`none`, unchanged normalized hash) |

Interpretation: do **not** weaken ANSI stripping to chase the pilot metric. The
AGT behavior is correct for terminal-control safety. The next clean-win path is
either stronger detector calibration / more matched benign terminal controls, or
a downstream policy that treats `AnsiEscape` as evidence for review rather than
as a standalone block signal.

## Accept / kill

- **Accept:** pilot artifacts validate and identify both FP causes without raw
  text; Rust benign ANSI test passes; GitHub/AgentBus updates stay public-safe.
- **Flag:** if pilot FPs remain, report them honestly. This ticket is allowed
  to improve attribution without claiming metric success.
- **Kill:** if fixing the FP requires weakening ANSI stripping, changing corpus
  labels/templates, or tuning on test rows.

## Out of scope

Changing corpus templates, adding transform variants, changing detector/kNN
protocol, changing AGT public API, or claiming production/default-blocking
readiness.
