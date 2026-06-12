# Ticket #2 - Open-Source Readiness Audit

Source issue: https://github.com/kerberosmansour/AGT-Embeddings-Experiment/issues/2
Workpad: https://github.com/kerberosmansour/AGT-Embeddings-Experiment/issues/2#issuecomment-4694559050
AgentBus task: `t_mqbbiisz_739_8d727267`
Target branch: `slo/issues-9-10-detection-improvements` (shared active experiment branch)
Stack: Python stdlib validator + Markdown readiness docs

## Smallest user-visible outcome

The public-release readiness package gets a deterministic validator and CI
workflow hook that checks community files, security instructions, and public
claim guardrails before release.

## Sizing gate

| Row | Value |
|---|---|
| One user-visible outcome | yes - one open-source readiness validator |
| Changed files | <= 5 |
| Public surfaces | 1 CLI: `meta/harness/open-source-readiness/validate_open_source_readiness.py` |
| Migration | none |
| New dependency | none |
| One PR can review | yes |

Fits a single ticket.

## Compact architecture delta

Add a stdlib-only readiness validator beside the existing harnesses and run it
from `.github/workflows/readiness.yml`. It does not change corpus artifacts,
detector behavior, metrics, or AGT-facing APIs.

## Contract block

| Field | Value |
|---|---|
| Files allowed to change | NEW `docs/slo/tickets/ticket-2-open-source-readiness-audit.md`; `docs/OPEN-SOURCE-READINESS.md`; NEW `meta/harness/open-source-readiness/validate_open_source_readiness.py`; NEW `meta/harness/open-source-readiness/test_validate_open_source_readiness.py`; `.github/workflows/readiness.yml` |
| Files to read first | GitHub issue #2; `docs/ARCHITECTURE.md`; `README.md`; `docs/CLAIMS-LEDGER.md`; `docs/OPEN-SOURCE-READINESS.md`; `LICENSE`; `CONTRIBUTING.md`; `CODE_OF_CONDUCT.md`; `SECURITY.md`; `CITATION.cff`; `.github/workflows/readiness.yml` |
| New files allowed | this ticket contract and the validator/test pair |
| New dependencies | none |
| Migration allowed | no |
| Compatibility commitments | Existing readiness workflow still runs round-4/embedding/governance/source-scale checks; validator is additive |
| Data classification | Public repository metadata and docs; no raw payload examples or secrets may be emitted |
| Proactive controls | C8 Protect Data Everywhere (secret-marker scan), C3 Validate Input (required-file/readiness checks), experiment governance (no-overclaim wording) |
| Abuse scenarios | `tm-2-abuse-1`: required community file is removed -> validator fails. `tm-2-abuse-2`: README claims production/default-blocking readiness -> validator fails. `tm-2-abuse-3`: secret-like marker appears in public package files -> validator fails without echoing secrets. |
| Resource bounds | O(size of public docs/community files); no corpus/model load |
| Invariants/assertions | required files exist; README/claims ledger preserve optional/default-off and no-real-traffic/no-production guardrails; `SECURITY.md` includes reporting instructions; readiness workflow runs the validator |
| Debugger expectation | N/A - deterministic file validation |
| Static-analysis gates | `py_compile`; focused unittest; validator on repo root; diff hygiene |
| Reversibility / rollback | remove validator/test/ticket and workflow step; no data migration |
| Exemplar to copy | stdlib validator/test style from other repo harness validators |
| Anti-exemplar | do not edit corpus/artifacts/metrics; do not add dependencies; do not turn readiness into release approval |
| IAM secrets->role->trust-policy mapping | N/A - workflow touched has no `role-to-assume:` or IAM/OIDC trust policy |
| Refactoring discipline | N/A - no refactoring |
| AI tolerance contract | N/A - no AI component |
| Forbidden shortcuts | no warning-only mode for missing package files; no production/default-blocking/certification claims; no raw examples in issue comments |

## Implementation plan

1. Add focused validator tests first and confirm they fail before the validator exists.
2. Add the stdlib validator with required-file, guardrail, workflow, and secret-marker checks.
3. Add the validator to the readiness workflow.
4. Update `docs/OPEN-SOURCE-READINESS.md` with the validator command.
5. Run validation and update #2/AgentBus with paths and hashes.

## BDD scenarios

| Scenario | Category | Given | When | Then |
|---|---|---|---|---|
| valid readiness package | happy path | all required files and guardrail phrases exist | validator runs | validation passes |
| missing security policy | invalid input | `SECURITY.md` is absent | validator runs | validation fails |
| production overclaim | abuse / `tm-2-abuse-2` | README says the detector is production-ready or ready for default blocking | validator runs | validation fails |
| secret marker | abuse / `tm-2-abuse-3` | a public package file contains a token-like marker | validator runs | validation fails without printing the token value |
| workflow hook | compatibility | readiness workflow exists | validator runs | workflow contains the readiness validator step |

## Validation plan

| Check | Command | Expected | Actual Result | Status |
|---|---|---|---|---|
| Repo hygiene | `git status --short --branch && git rev-parse --abbrev-ref HEAD && git symbolic-ref --short refs/remotes/origin/HEAD` | branch is non-default; dirty tree recorded | branch `slo/issues-9-10-detection-improvements`; default `origin/main`; dirty tree pre-existed and was preserved | pass |
| New tests fail first | `python3 meta/harness/open-source-readiness/test_validate_open_source_readiness.py` before validator implementation | fails on missing validator | FAIL as expected: 4 errors, all `FileNotFoundError` for missing `validate_open_source_readiness.py` | pass |
| Compile | `python3 -m py_compile meta/harness/open-source-readiness/*.py` | PASS | PASS | pass |
| Unit / BDD tests | `python3 meta/harness/open-source-readiness/test_validate_open_source_readiness.py` | PASS | PASS: 4 tests | pass |
| Repo readiness validation | `python3 meta/harness/open-source-readiness/validate_open_source_readiness.py` | PASS | PASS: `PASS open-source readiness root=.` | pass |
| Existing round-4 smoke | `bash corpus/round4/run-smoke.sh` | PASS | PASS: corpus hygiene, Rust scorer build/run, metrics rebuild, metadata-only evidence | pass |
| Existing embedding artifact validator | `python3 meta/harness/round4-embedding-sweep/validate-embedding-sweep.py --provenance artifacts/embedding-sweep/provenance.json --freeze artifacts/embedding-sweep/freeze-record.json --validation artifacts/embedding-sweep/validation-per-row.jsonl --test artifacts/embedding-sweep/test-per-row.jsonl --validation-metrics artifacts/embedding-sweep/validation-metrics.json --test-metrics artifacts/embedding-sweep/test-metrics.json` | PASS | PASS: `round4_embedding_sweep_artifact: PASS` | pass |
| Existing governance artifact validator | `python3 meta/harness/round4-governance-eval/validate-governance-eval.py --manifest artifacts/governance-eval/manifest.json --validation artifacts/governance-eval/validation.jsonl --test artifacts/governance-eval/test.jsonl --metrics artifacts/governance-eval/metrics.json` | PASS | PASS: `round4_governance_eval_artifact: PASS` | pass |
| Existing value-add/source-scale checks | `python3 meta/harness/round5-agt-value-add/validate-round5-agt-value-add-report.py meta/harness/round5-agt-value-add/round5-agt-value-add-report.example.json && python3 -m json.tool artifacts/source-scale-pilot/summary.json >/dev/null` | PASS | PASS: schema validator OK and source-scale summary parses | pass |
| Diff hygiene | `git diff --check -- docs/slo/tickets/ticket-2-open-source-readiness-audit.md docs/OPEN-SOURCE-READINESS.md meta/harness/open-source-readiness/validate_open_source_readiness.py meta/harness/open-source-readiness/test_validate_open_source_readiness.py .github/workflows/readiness.yml` plus new-file `--no-index` checks | PASS | PASS: no whitespace diagnostics; new-file `--no-index` checks exited non-zero only because files differ from `/dev/null` | pass |

## Execution evidence

| Evidence | Result |
|---|---|
| Validator CLI | `meta/harness/open-source-readiness/validate_open_source_readiness.py` |
| Validator tests | `meta/harness/open-source-readiness/test_validate_open_source_readiness.py`; 4 tests cover valid fixture, missing `SECURITY.md`, README overclaims, and secret-like marker detection |
| Workflow hook | `.github/workflows/readiness.yml` now runs `python3 meta/harness/open-source-readiness/validate_open_source_readiness.py` before the heavier readiness checks |
| Readiness docs | `docs/OPEN-SOURCE-READINESS.md` now lists the validator command in final packaging checks |
| Full readiness sequence | New validator, round-4 smoke, embedding artifact validator, governance artifact validator, value-add schema validator, and source-scale summary JSON check all pass |
| Public-safety check | Issue/AgentBus evidence uses paths, hashes, and command results only; no raw payload examples |

## Accept / kill

- Accept: validator and tests pass; readiness workflow runs the validator; issue
  evidence stays path/hash-only.
- Flag: this is readiness validation, not public release approval.
- Kill: any change edits corpus/artifacts/metrics, weakens claim guardrails, or
  posts raw payload examples.

## Out of scope

Changing licenses, changing corpus/artifact data, running new detector
experiments, making release announcements, closing #2 automatically, or opening
upstream AGT PRs.

## Self-review gate

- [x] Changed files stay inside the allow-list.
- [x] Required community files are checked.
- [x] README and claims-ledger guardrails are checked.
- [x] Security reporting instructions are checked.
- [x] Readiness workflow runs the validator.
- [x] Validation commands pass and are recorded.
- [x] GitHub issue #2 and AgentBus are updated with paths only.

## 11. Closure Summary

Completed behavior: issue #2 now has a deterministic open-source readiness
validator, focused BDD tests, and a readiness workflow hook. The validator checks
required community files, security reporting wording, README/claims-ledger
guardrails, and secret-like markers in public package files.

Tests and validation: new tests failed first on the missing validator, then
passed after implementation. Python compile, focused tests, repository readiness
validation, existing readiness artifact validators, and diff hygiene all pass.

Lessons and follow-ups: this is packaging validation, not release approval. A
human still decides when to announce or make release claims.

Issue / PR links: source issue #2; PR not opened by this ticket-sized pass.
