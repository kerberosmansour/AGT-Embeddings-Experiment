# Ticket #1 - Migration Closeout Audit

Source issue: https://github.com/kerberosmansour/AGT-Embeddings-Experiment/issues/1
Workpad: https://github.com/kerberosmansour/AGT-Embeddings-Experiment/issues/1#issuecomment-4695119343
AgentBus task: `t_mqbdqhvh_13_2adad333`
Target branch: `slo/issues-9-10-detection-improvements` (shared active experiment branch)
Stack: Python stdlib validator + Markdown runbook status

## Smallest user-visible outcome

Issue #1 gets a deterministic closeout validator proving the migrated AGT
embeddings evidence package is present, claim-mapped, and still public-safe.

## Sizing gate

| Row | Value |
|---|---|
| One user-visible outcome | yes - one migration closeout validator |
| Changed files | <= 4 |
| Public surfaces | 1 CLI: `meta/harness/migration-closeout/validate_migration_closeout.py` |
| Migration | none |
| New dependency | none |
| One PR can review | yes |

Fits a single ticket.

## Compact architecture delta

Add a stdlib-only migration closeout validator. It checks that migrated docs,
corpus/artifact roots, validator harnesses, peer-readback records, and claims
ledger guardrails are present. It does not regenerate artifacts, change metrics,
or touch detector/normalizer code.

## Contract block

| Field | Value |
|---|---|
| Files allowed to change | NEW `docs/slo/tickets/ticket-1-migration-closeout-audit.md`; `docs/RUNBOOK-agt-embeddings-migration.md`; NEW `meta/harness/migration-closeout/validate_migration_closeout.py`; NEW `meta/harness/migration-closeout/test_validate_migration_closeout.py` |
| Files to read first | GitHub issue #1; `docs/ARCHITECTURE.md`; `README.md`; `docs/CLAIMS-LEDGER.md`; `docs/RUNBOOK-agt-embeddings-migration.md`; `docs/AGENTBUS-WORKSPLIT.md`; `docs/OPEN-SOURCE-READINESS.md`; `docs/UPSTREAM-PR-PLAN.md`; `.github/workflows/readiness.yml` |
| New files allowed | this ticket contract and the validator/test pair |
| New dependencies | none |
| Migration allowed | no |
| Compatibility commitments | Existing corpus/artifacts/metrics and validators remain unchanged |
| Data classification | Public migration metadata and aggregate evidence paths only; no raw payload examples |
| Proactive controls | C8 Protect Data Everywhere (path-only evidence), C3 Validate Input (required path/claim checks), experiment governance (no-overclaim guardrails) |
| Abuse scenarios | `tm-1-abuse-1`: an artifact root is missing but issue #1 appears complete -> validator fails. `tm-1-abuse-2`: a claims-ledger mapping is missing -> validator fails. `tm-1-abuse-3`: README claims guaranteed/production/default-blocking performance -> validator fails. |
| Resource bounds | O(public docs + path existence); no corpus/model load |
| Invariants/assertions | M1/M2/M3 evidence paths exist; claims ledger maps core metrics; runbook/worksplit record peer gates; README preserves no-production/no-real-traffic/default-off boundaries |
| Debugger expectation | N/A - deterministic file validation |
| Static-analysis gates | `py_compile`; focused unittest; validator on repo root; diff hygiene |
| Reversibility / rollback | remove validator/test/ticket and the runbook command note |
| Exemplar to copy | stdlib validation style from `meta/harness/open-source-readiness/validate_open_source_readiness.py` |
| Anti-exemplar | do not rerun/tune detector metrics; do not bulk-edit migration docs; do not close #1 automatically |
| IAM secrets->role->trust-policy mapping | N/A - no workflow/IAM trust policy touched |
| Refactoring discipline | N/A - no refactoring |
| AI tolerance contract | N/A - no AI component |
| Forbidden shortcuts | no warning-only mode for missing evidence roots; no production/default-blocking/certification claims; no raw examples in issue comments |

## Implementation plan

1. Add focused validator tests first and confirm they fail before the validator exists.
2. Add the stdlib migration closeout validator.
3. Add the validator command to the migration runbook verification section.
4. Run focused validation plus existing readiness evidence checks.
5. Update #1 and AgentBus with paths/hashes only.

## BDD scenarios

| Scenario | Category | Given | When | Then |
|---|---|---|---|---|
| valid migration package | happy path | required docs, artifacts, and claim mappings exist | validator runs | validation passes |
| missing artifact root | invalid input | embedding freeze record is absent | validator runs | validation fails |
| missing claim mapping | invalid input | claims ledger omits migrated metric rows | validator runs | validation fails |
| overclaim wording | abuse / `tm-1-abuse-3` | README guarantees zero false positives | validator runs | validation fails |
| peer-gate trace | governance | migration runbook/worksplit are present | validator runs | M1-M4 peer gate phrases are checked |

## Validation plan

| Check | Command | Expected | Actual Result | Status |
|---|---|---|---|---|
| Repo hygiene | `git status --short --branch && git rev-parse --abbrev-ref HEAD && git symbolic-ref --short refs/remotes/origin/HEAD` | branch is non-default; dirty tree recorded | branch `slo/issues-9-10-detection-improvements`; default `origin/main`; dirty tree pre-existed and was preserved | pass |
| New tests fail first | `python3 meta/harness/migration-closeout/test_validate_migration_closeout.py` before validator implementation | fails on missing validator | failed first with missing `validate_migration_closeout.py`, then passed after implementation | pass |
| Compile | `python3 -m py_compile meta/harness/migration-closeout/*.py` | PASS | passed | pass |
| Unit / BDD tests | `python3 meta/harness/migration-closeout/test_validate_migration_closeout.py` | PASS | `Ran 4 tests ... OK` | pass |
| Migration closeout validation | `python3 meta/harness/migration-closeout/validate_migration_closeout.py` | PASS | `PASS migration closeout root=.` | pass |
| Existing readiness validator | `python3 meta/harness/open-source-readiness/validate_open_source_readiness.py` | PASS | `PASS open-source readiness root=.` | pass |
| Existing round4 smoke | `bash corpus/round4/run-smoke.sh` | PASS | passed; known Rust dead-code warnings only | pass |
| Existing embedding sweep gate | `python3 meta/harness/round4-embedding-sweep/validate-embedding-sweep.py --provenance artifacts/embedding-sweep/provenance.json --freeze artifacts/embedding-sweep/freeze-record.json --validation artifacts/embedding-sweep/validation-per-row.jsonl --test artifacts/embedding-sweep/test-per-row.jsonl --validation-metrics artifacts/embedding-sweep/validation-metrics.json --test-metrics artifacts/embedding-sweep/test-metrics.json` | PASS | `round4_embedding_sweep_artifact: PASS` | pass |
| Existing governance gate | `python3 meta/harness/round4-governance-eval/validate-governance-eval.py --manifest artifacts/governance-eval/manifest.json --validation artifacts/governance-eval/validation.jsonl --test artifacts/governance-eval/test.jsonl --metrics artifacts/governance-eval/metrics.json` | PASS | `round4_governance_eval_artifact: PASS` | pass |
| Existing value/source-scale gates | `python3 meta/harness/round5-agt-value-add/validate-round5-agt-value-add-report.py meta/harness/round5-agt-value-add/round5-agt-value-add-report.example.json` and `python3 -m json.tool artifacts/source-scale-pilot/summary.json >/dev/null` | PASS | schema validator OK and source-scale summary parses | pass |
| Diff hygiene | `git diff --check -- docs/slo/tickets/ticket-1-migration-closeout-audit.md docs/RUNBOOK-agt-embeddings-migration.md meta/harness/migration-closeout/validate_migration_closeout.py meta/harness/migration-closeout/test_validate_migration_closeout.py` plus new-file `--no-index` checks | PASS | passed | pass |

## Execution evidence

- Added `meta/harness/migration-closeout/validate_migration_closeout.py`, a
  stdlib-only validator that checks required migration files, claim mappings,
  peer-gate wording, README safety boundaries, and forbidden overclaims.
- Added `meta/harness/migration-closeout/test_validate_migration_closeout.py`
  with four BDD-style tests: valid fixture, missing artifact root, missing claim
  mapping, and overclaim wording.
- Added the validator command to `docs/RUNBOOK-agt-embeddings-migration.md`
  so migration closeout checks are part of the recorded verification sequence.
- No corpus payloads, artifact metrics, detector thresholds, or normalizer logic
  were changed.

## Accept / kill

- Accept: validator and tests pass; #1 gets path/hash-only closeout evidence.
- Flag: this does not approve a release, merge a PR, or close #1 automatically.
- Kill: any change touches corpus/artifact metric content, weakens claim
  guardrails, or posts raw payload examples.

## Out of scope

Changing migrated artifacts, changing detector/normalizer/harness behavior,
running new experiments, making release announcements, closing #1 automatically,
or editing upstream AGT PR content.

## Self-review gate

- [x] Changed files stay inside the allow-list.
- [x] Required migration docs/evidence roots are checked.
- [x] Claims ledger mappings are checked.
- [x] Peer-gate/readback trace is checked.
- [x] Public guardrail wording is checked.
- [x] Validation commands pass and are recorded.
- [x] GitHub issue #1 and AgentBus are updated with paths only.

## 11. Closure Summary

Issue #1 now has a deterministic closeout audit for the migrated AGT embeddings
package. The validator proves that the expected docs, corpus/artifact evidence
roots, claims-ledger mappings, and peer-readback gates are present, while also
failing on public overclaim wording such as production/default-blocking or
real-traffic validation claims. This is a closeout-readiness check only: it does
not close the issue, approve a release, or change any experiment result.
