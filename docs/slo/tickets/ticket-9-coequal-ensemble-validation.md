# Ticket #9 - Co-Equal Ensemble Artifact Validation

Source issue: https://github.com/kerberosmansour/AGT-Embeddings-Experiment/issues/9
AgentBus task: `t_mqbacqm8_312_f4b84ff5`
Target branch: `slo/issues-9-10-detection-improvements` (shared active experiment branch)
Stack: Python stdlib validator over existing exp4 artifacts; no model run

## Smallest user-visible outcome

The existing #9 co-equal ensemble result gets a deterministic validator and SLO
closeout evidence proving the honest validation-frozen metrics reproduce from
metadata-only artifacts.

## Sizing gate

| Row | Value |
|---|---|
| One user-visible outcome | yes - one artifact validator and ticket closeout |
| Changed files | <= 4 |
| Public surfaces | 1 CLI: `meta/harness/exp4-coequal/validate_coequal.py` |
| Migration | none |
| New dependency | none |
| One PR can review | yes |

Fits a single ticket.

## Compact architecture delta

Add a narrow validator for `artifacts/exp4-coequal/`. It does not compute
embeddings, retrain the head, change thresholds, or regenerate artifacts. It
checks that the freeze came from validation, artifacts are metadata-only, and
strict co-equal test metrics reproduce from `test-per-row.jsonl`.

## Contract block

| Field | Value |
|---|---|
| Files allowed to change | NEW `docs/slo/tickets/ticket-9-coequal-ensemble-validation.md`; NEW `meta/harness/exp4-coequal/validate_coequal.py`; NEW `meta/harness/exp4-coequal/test_validate_coequal.py`; `meta/harness/exp4-coequal/README.md` |
| Files to read first | GitHub issue #9; `docs/ARCHITECTURE.md`; `meta/harness/exp4-coequal/README.md`; `meta/harness/exp4-coequal/run_coequal.py`; `docs/reports/exp4-normalizer-ensemble-report.md`; `artifacts/exp4-coequal/{freeze-record.json,test-metrics.json,newnorm-metrics.json,test-per-row.jsonl}`; `meta/harness/round7-garak/validate_round7_garak.py` |
| New files allowed | this ticket contract and the validator/test pair |
| New dependencies | none |
| Migration allowed | no |
| Compatibility commitments | no model rerun; no detector threshold changes; no artifact schema migration beyond validator expectations |
| Data classification | Public metadata-only artifacts; raw corpus text must not appear in validator output, GitHub comments, or AgentBus notes |
| Proactive controls | C8 Protect Data Everywhere (metadata-only evidence), C9 Security Logging (bounded validation errors), experiment governance (validation freeze before test) |
| Abuse scenarios | `tm-9-abuse-1`: test threshold selection is accepted as a valid freeze -> validator must fail. `tm-9-abuse-2`: raw prompt/text-like fields appear in artifacts -> validator must fail. `tm-9-abuse-3`: metrics JSON drifts from per-row file -> validator must fail. |
| Resource bounds | O(rows) JSON/JSONL validation over existing artifacts; no embeddings, no model load, no network |
| Invariants/assertions | `freeze-record.selected_on == "validation"`; strict recall/FP and per-family/control recalls reproduce from per-row flags; `test_combined_fp_strict == 0`; artifacts omit raw text-like keys and raw URL/email-looking strings |
| Debugger expectation | inspect freeze record and recomputed metrics before posting issue evidence |
| Static-analysis gates | `py_compile`; focused unittest; validator on real artifacts; markdown diff hygiene |
| Reversibility / rollback | remove validator/test/ticket and README validation note |
| Exemplar to copy | metadata-only validation style from `meta/harness/round7-garak/validate_round7_garak.py` |
| Anti-exemplar | do not rerun/tune models here; do not update thresholds; do not post raw examples publicly |
| AI tolerance contract | AI component exists only in the already-generated upstream experiment artifacts. This ticket adds deterministic validation only. Must-never: raw text in artifacts, GitHub comments, or AgentBus notes. |
| Forbidden shortcuts | no test-threshold tuning, no model rerun, no weakening the overfitting correction, no unlabeled metric drift |

## BDD scenarios

| Scenario | Category | Given | When | Then |
|---|---|---|---|
| valid exp4 artifacts | happy path | freeze, metrics, newnorm metrics, and per-row JSONL are metadata-only | validator runs | validation passes and prints `PASS` |
| test-selected freeze | abuse / `tm-9-abuse-1` | `freeze-record.selected_on` is `test` | validator runs | validation fails |
| raw text field | abuse / `tm-9-abuse-2` | a per-row record contains `text` | validator runs | validation fails without echoing raw content |
| metric drift | abuse / `tm-9-abuse-3` | `test-metrics.json` recall disagrees with per-row flags | validator runs | validation fails |
| no model dependency | degraded state | local embedding environment is absent | validator runs | validation still passes because it reads existing artifacts only |

## Validation plan

| Check | Command | Expected | Actual Result | Status |
|---|---|---|---|---|
| Repo hygiene | `git status --short --branch && git rev-parse --abbrev-ref HEAD && git symbolic-ref --short refs/remotes/origin/HEAD` | branch is non-default; dirty tree recorded | branch `slo/issues-9-10-detection-improvements`; default `origin/main`; dirty tree pre-existed and was preserved | pass |
| New tests fail first | `python3 meta/harness/exp4-coequal/test_validate_coequal.py` before validator implementation | fails on missing validator | failed with `FileNotFoundError` for missing `validate_coequal.py`, as expected | pass |
| Compile | `python3 -m py_compile meta/harness/exp4-coequal/*.py` | PASS | PASS | pass |
| Unit / BDD tests | `python3 meta/harness/exp4-coequal/test_validate_coequal.py` | PASS | PASS - 4 tests | pass |
| Real artifact validation | `python3 meta/harness/exp4-coequal/validate_coequal.py artifacts/exp4-coequal` | PASS | PASS - `9408` rows; strict recall `0.868478260870`; strict FP `0.000000000000` | pass |
| Diff hygiene | `git diff --check -- docs/slo/tickets/ticket-9-coequal-ensemble-validation.md meta/harness/exp4-coequal/validate_coequal.py meta/harness/exp4-coequal/test_validate_coequal.py meta/harness/exp4-coequal/README.md` plus `--no-index /dev/null` for new files | PASS | PASS - no whitespace diagnostics; new-file `--no-index` checks exited non-zero only because files differ from `/dev/null` | pass |

## Execution evidence

| Evidence | Result |
|---|---|
| Validator CLI | `meta/harness/exp4-coequal/validate_coequal.py` |
| Validator tests | `meta/harness/exp4-coequal/test_validate_coequal.py`; 4 tests cover valid fixture, test-selected freeze, raw text field, and metric drift |
| Real artifact validation | `PASS artifacts/exp4-coequal rows=9408 strict_recall=0.868478260870 strict_fp=0.000000000000` |
| Freeze record | `artifacts/exp4-coequal/freeze-record.json`; sha256 `ef0f36ef53bdb9e1b519a398dd049aab2638b7e19a2383ad624abc77c7a577d6` |
| Strict metrics | `artifacts/exp4-coequal/test-metrics.json`; sha256 `2afadeba8493fa50773c6bdbe02c856687d315647ec1501e35159fd80a41c5d7` |
| New-normalizer metrics | `artifacts/exp4-coequal/newnorm-metrics.json`; sha256 `d824c4c996f86ea0c4273a54369da0632d4a874818dbb94e69a210d9fc3f24a4` |
| Per-row artifact | `artifacts/exp4-coequal/test-per-row.jsonl`; sha256 `b537e96a7f78c667b76fc1d33af60fbac465634908fb8a13f6497e778344669a` |

Interpretation: the validator confirms the #9 correction. The test-derived
92.5% ceiling does not survive validation freezing; strict co-equal is 86.85%
at 0 observed FP, and the 0.1%-validation-FPR variant remains tied with Rec B at
87.23% at 0 observed FP. The #10 extended normalizer follow-up remains the real
incremental gain, with `newnorm-metrics.json` reporting 88.72% at 0 observed FP.

## Self-review gate

- [x] Changed files stay inside the ticket allow-list.
- [x] Validator does not load models, embed rows, retrain a head, or change thresholds.
- [x] Public evidence contains no raw corpus text.
- [x] Validator fails on test-selected freeze metadata.
- [x] Validator fails on raw-text-like artifact fields.
- [x] Validator fails when strict metrics drift from per-row flags.
- [x] Local validation commands pass.

## Accept / kill

- Accept: validator proves the #9 correction and strict metrics reproduce from
  metadata-only artifacts.
- Flag: the old 92.5% result remains rejected as test-set overfitting.
- Kill: validator requires model execution, accepts test-selected thresholds, or
  leaks raw text in public output.

## Out of scope

Changing #9 thresholds, rerunning embeddings/head training, modifying #10
normalizer behavior, round-7 corpus work, or closing the GitHub issue.

## 11. Closure Summary

Completed behavior: issue #9 now has deterministic artifact validation for the
co-equal ensemble evidence. The validator proves the freeze is validation-based,
the artifacts are metadata-only, and strict recall/FP plus by-control and
per-family recall reproduce from `test-per-row.jsonl`.

Tests and validation: the new BDD tests failed first on the missing validator,
then passed after implementation. Python compile, unit tests, real artifact
validation, and diff hygiene pass.

Lessons and follow-ups: the durable claim remains the correction, not the
headline originally hoped for. The 92.5% value was test-set overfitting; the
honest co-equal result is about 87% at 0 observed FP, and the stronger #10
normalizer is the useful compounding gain.

Issue / PR links: source issue #9; PR not opened by this ticket-sized pass.
