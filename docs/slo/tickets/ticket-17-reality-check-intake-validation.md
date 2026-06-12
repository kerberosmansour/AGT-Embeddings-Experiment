# Ticket #17 - Reality-Check Intake Validation

Source issue: https://github.com/kerberosmansour/AGT-Embeddings-Experiment/issues/17
AgentBus task: `t_mqb8p9l2_534_4d0cd076`
Target branch: `slo/issues-9-10-detection-improvements` (shared active experiment branch)
Stack: Python stdlib JSONL tooling; no hosted inference

## Smallest user-visible outcome

Researchers get a repeatable, public-safe validator for the round-7
payload-derived reality-check intake, proving source attribution, Apache-2.0/MIT
license gates, redaction hygiene, and synthetic-variation readiness.

## Sizing gate

| Row | Value |
|---|---|
| One user-visible outcome | yes - one intake validator and evidence summary |
| Changed files | <= 5 source/doc files plus ignored scratch outputs |
| Public surfaces | 1 CLI: `corpus/round7/reality-check/check_reality_check.py` |
| Migration | none |
| New dependency | none |
| One PR can review | yes |

Fits a single ticket.

## Compact architecture delta

Add a stdlib-only validator beside the reality-check intake. It walks
source-separated `*.jsonl` files under `incoming/`, checks the schema and license
rules from #17, scans only payload-bearing fields for live-looking URLs, emails,
and common secret markers, and writes an aggregate JSON summary that contains no
raw payload text.

The existing `make_synthetic_variations.py` generator remains the separate path
for benchmark-safe fake surface forms. The source-attributed rows stay redacted.

## Contract block

| Field | Value |
|---|---|
| Files allowed to change | NEW `docs/slo/tickets/ticket-17-reality-check-intake-validation.md`; `corpus/round7/reality-check/INTAKE.md`; NEW `corpus/round7/reality-check/check_reality_check.py`; NEW `corpus/round7/reality-check/test_reality_check.py`; generated ignored `scratch/round7-reality-check-summary.json`; generated ignored `scratch/round7-synthetic-variations.jsonl` |
| Files to read first | `docs/ARCHITECTURE.md`; `docs/RUNBOOK-round7-garak-corpus.md`; `docs/proposals/round7-generator-proposal.md`; `corpus/round7/reality-check/INTAKE.md`; `corpus/round7/reality-check/SYNTHETIC_VARIATIONS.md`; `corpus/round7/reality-check/make_synthetic_variations.py`; `corpus/round7/reality-check/incoming/MANIFEST.md` |
| New files allowed | this ticket contract, validator, focused tests, ignored scratch summaries |
| New dependencies | none |
| Migration allowed | no |
| Compatibility commitments | Existing source-attributed JSONL schema remains unchanged; synthetic generator remains separate and fail-closed on non-MIT/Apache rows |
| Data classification | Public source-attributed corpus metadata; payload text is committed locally but must not appear in public issue comments, AgentBus notes, or generated summaries |
| Proactive controls | C8 Protect Data Everywhere (metadata-only summaries), C3 Validate Input (schema/license/role/harm-channel checks), C9 Security Logging (row id by file/line/hash only on errors) |
| Abuse scenarios | `tm-17-abuse-1`: raw payload text leaks into generated summary or public comment -> tests/inspection fail. `tm-17-abuse-2`: disallowed/unknown license sneaks into `incoming/` -> validator exits non-zero. `tm-17-abuse-3`: live URL/email/secret appears in payload text or turns -> validator exits non-zero while allowing provenance `origin_url`. |
| Resource bounds | O(rows) streaming JSONL validation; summary stores bounded aggregate counters and capped metadata-only error records |
| Invariants/assertions | every row has the required fields; license is exactly Apache-2.0 or MIT; `multi_turn` and `turns` agree; turn roles are from the allowed set; summaries never include `text`, `prompt`, `content`, `turns`, or `origin_url` |
| Debugger expectation | inspect aggregate summary and validator error metadata only; inspect raw rows locally only if a validation failure needs manual redaction |
| Static-analysis gates | `py_compile`; focused unittest; validator on full incoming arm; synthetic generator smoke |
| Reversibility / rollback | remove validator/test/ticket docs and scratch outputs; no corpus row rewrite required |
| Exemplar to copy | existing metadata-only validation style from `corpus/round7/check-round7.py` and `meta/harness/round7-garak/validate_round7_garak.py` |
| Anti-exemplar | do not paste raw examples in GitHub; do not allow CC-BY/proprietary/unknown in committed `incoming/`; do not mutate source-attributed rows to create synthetic values |
| AI tolerance contract | N/A - no AI component; deterministic file validation and synthetic slot filling only |
| Forbidden shortcuts | no raw payloads in summaries; no license warning-only mode for committed intake; no new dependencies; no detector or benchmark headline changes |

## BDD scenarios

| Scenario | Category | Given | When | Then |
|---|---|---|---|
| valid source row | happy path | a row with required fields, MIT license, redacted placeholders, and provenance URL | validator runs | validation passes and summary counts one row |
| provenance URL allowed | happy path | `origin_url` is an HTTPS source link | validator runs | the provenance link is accepted but omitted from the summary |
| disallowed license | invalid input | a row has `license=unknown` | validator runs | validation fails with file/line metadata |
| raw payload URL | abuse / `tm-17-abuse-3` | payload `text` contains `https://...` | validator runs | validation fails and no raw URL appears in the error summary |
| raw turn email | abuse / `tm-17-abuse-3` | a multi-turn payload has a live-looking email in a turn | validator runs | validation fails and no raw email appears in the error summary |
| full incoming intake | runtime | current `incoming/` directory | validator runs with `--summary scratch/round7-reality-check-summary.json` | 2,213 rows pass with MIT/Apache counts and no raw payload fields in the summary |

## Validation plan

| Check | Command | Expected | Actual Result | Status |
|---|---|---|---|---|
| Repo hygiene | `git status --short --branch && git rev-parse --abbrev-ref HEAD && git symbolic-ref --short refs/remotes/origin/HEAD` | branch is non-default; dirty tree recorded | branch `slo/issues-9-10-detection-improvements`; default `origin/main`; dirty tree pre-existed from round-7 work and was preserved | pass |
| New test fails first | `python3 corpus/round7/reality-check/test_reality_check.py` after adding tests before validator | fails on missing validator implementation | failed with `FileNotFoundError` for missing `check_reality_check.py`, as expected | pass |
| Compile | `python3 -m py_compile corpus/round7/reality-check/*.py` | PASS | PASS | pass |
| Unit / BDD tests | `python3 corpus/round7/reality-check/test_reality_check.py` | PASS | PASS (`4` tests) | pass |
| Full intake validation | `python3 corpus/round7/reality-check/check_reality_check.py corpus/round7/reality-check/incoming --summary scratch/round7-reality-check-summary.json` | PASS, summary is aggregate-only | PASS: `2,213` rows across `10` files; licenses `Apache-2.0=742`, `MIT=1,471`; `1,240` rows with recognized placeholders; `0` errors | pass |
| Synthetic variation smoke | `python3 corpus/round7/reality-check/make_synthetic_variations.py --input-dir corpus/round7/reality-check/incoming --output scratch/round7-synthetic-variations.jsonl --variants-per-row 2` | PASS, output is separate ignored arm | PASS: wrote `2,480` rows; all rows retain Apache-2.0/MIT license and parent provenance in `notes` | pass |
| Diff hygiene | `git diff --check -- docs/slo/tickets/ticket-17-reality-check-intake-validation.md corpus/round7/reality-check/INTAKE.md corpus/round7/reality-check/check_reality_check.py corpus/round7/reality-check/test_reality_check.py` plus `--no-index /dev/null` for untracked new files | PASS | PASS: no whitespace diagnostics; new-file `--no-index` checks exited non-zero only because files differ from `/dev/null` | pass |

## Execution evidence

| Evidence | Result |
|---|---|
| Intake summary | `scratch/round7-reality-check-summary.json`; sha256 `1acc350a2769530540a5e146d1091a957b3861190c280c27447336c59c6fdea0` |
| Intake aggregate counts | `2,213` source-attributed rows; `10` files; Apache-2.0 `742`; MIT `1,471`; multi-turn `325`; single-turn `1,888`; placeholders in `1,240` rows; validation errors `0` |
| Harm-channel counts | action `393`; leak `66`; output_bytes `37`; output_text `1,710`; unknown `7` |
| Synthetic variation smoke | `scratch/round7-synthetic-variations.jsonl`; sha256 `009b62a8909cabbe125876da2db3559bfb604d7c96e39aab8e3356b608d7f352`; `2,480` rows; parent provenance present on every row |
| Public-safe inspection | Summary JSON contains no `text`, `prompt`, `content`, `raw_text`, `turns`, or `origin_url` keys |

## Accept / kill

- Accept: validator and tests pass; full intake summary reports 2,213 rows, only
  Apache-2.0/MIT licenses, and no live-looking payload URL/email/secret markers.
- Accept: public GitHub update points to paths and aggregate counts only.
- Kill: any committed or public evidence includes raw payload text, live
  credentials/PII, or a disallowed source license.

## Out of scope

Changing detector scoring, changing round-7 synthetic corpus generation,
labeling containment classes, folding payload-derived rows into the synthetic
headline corpus, or adding new real-world sources.
