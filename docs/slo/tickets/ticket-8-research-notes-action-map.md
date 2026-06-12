# Ticket #8 - Q1/Q2 Research Notes Action Map

Source issue: https://github.com/kerberosmansour/AGT-Embeddings-Experiment/issues/8
AgentBus task: `t_mqbb5w58_500_8e97613d`
Target branch: `slo/issues-9-10-detection-improvements` (shared active experiment branch)
Stack: Markdown evidence synthesis only; no detector, corpus, or harness changes

## Smallest user-visible outcome

Issue #8 gets a durable, public-safe action map that reconciles the original
Q1/Q2 research notes with the follow-up work now completed or explicitly still
open.

## Sizing gate

| Row | Value |
|---|---|
| One user-visible outcome | yes - one action map plus a claims-ledger pointer |
| Changed files | <= 3 docs files |
| Public surfaces | none |
| Migration | none |
| New dependency | none |
| One PR can review | yes |

Fits a single ticket.

## Compact architecture delta

N/A - no architecture delta. This ticket updates research documentation only
and does not change runtime behavior, schemas, corpus rows, detectors, or
normalizers.

## Contract block

| Field | Value |
|---|---|
| Files allowed to change | NEW `docs/slo/tickets/ticket-8-research-notes-action-map.md`; NEW `docs/reports/research-notes-q1-q2-action-map.md`; `docs/CLAIMS-LEDGER.md` |
| Files to read first | GitHub issue #8; `docs/ARCHITECTURE.md`; `docs/CLAIMS-LEDGER.md`; `docs/reports/exp1-structural-autoblock-report.md`; `docs/reports/exp3-two-inspector-ensemble-report.md`; `docs/reports/exp4-normalizer-ensemble-report.md`; `docs/proposals/experiment-2-gate0plus-ISSUE-DRAFT.md`; `docs/RUNBOOK-round7-garak-corpus.md`; `docs/proposals/round7-generator-proposal.md`; `docs/slo/tickets/ticket-9-coequal-ensemble-validation.md`; `docs/slo/tickets/ticket-14-round7-generator-verification.md`; `docs/slo/tickets/ticket-15-round7-normalizer-fp-triage.md`; `docs/slo/tickets/ticket-16-round7-ws-c-2x2-measurement.md`; `docs/slo/tickets/ticket-17-reality-check-intake-validation.md`; `docs/proposals/output-stage-sanitizer-acs-transform.md`; `docs/proposals/outbound-embedding-scan-final-verification.md` |
| New files allowed | this ticket contract and the #8 action-map report |
| New dependencies | none |
| Migration allowed | no |
| Compatibility commitments | No headline metric, corpus row, detector threshold, or AGT interface changes |
| Data classification | Public methodology/evidence summary. No raw payload text or literal attack examples may be copied into GitHub, AgentBus, or this report. |
| Proactive controls | C8 Protect Data Everywhere (metadata/path-only public evidence), experiment governance (validation-frozen claims, synthetic vs real-data boundaries) |
| Abuse scenarios | `tm-8-abuse-1`: the rejected 92.5% test-derived number is revived as a claim -> report must mark it overfit/rejected. `tm-8-abuse-2`: synthetic results are described as real-traffic validation -> report must distinguish synthetic, payload-derived reality-check, and real data. `tm-8-abuse-3`: raw payload examples are pasted into public docs or comments -> forbidden. |
| Resource bounds | O(docs) read/write only; no model, corpus, or network-heavy measurement run |
| Invariants/assertions | Action map names completed follow-ups and remaining gaps; claims ledger points to the map; public updates include paths and commands only |
| Debugger expectation | N/A - no ambiguous runtime behavior; inspect source docs and diff |
| Static-analysis gates | file-presence check, `rg` key-term check, markdown diff hygiene |
| Reversibility / rollback | remove the new ticket/report and the small claims-ledger pointer |
| Exemplar to copy | concise evidence-ticket style from tickets #9, #14, #15, #16, and #17 |
| Anti-exemplar | do not add detector/corpus changes; do not paste payload rows; do not close issue #8 automatically |
| IAM secrets->role->trust-policy mapping | N/A - no IAM trust policy or workflow touched |
| Refactoring discipline | N/A - no refactoring |
| AI tolerance contract | N/A - no AI component; deterministic documentation synthesis only |
| Forbidden shortcuts | no raw examples in public evidence; no production/default-blocking claims; no unlabeled metric updates |

## Implementation plan

1. Re-open issue #8 and source evidence docs.
2. Write an action map that separates corrected findings, completed follow-ups,
   partial progress, and remaining gaps.
3. Add a small claims-ledger pointer so the corrected claim boundaries are hard
   to miss.
4. Run docs-only validation commands.
5. Update GitHub issue #8 and AgentBus with paths and aggregate evidence only.

## BDD scenarios

| Scenario | Category | Given | When | Then |
|---|---|---|---|---|
| action map exists | happy path | issue #8 has broad research notes | report is written | each Q1/Q2 note has a disposition and evidence pointer |
| overfit number corrected | abuse / `tm-8-abuse-1` | the issue body mentions 92.5% @ 0 FP | report is read | 92.5% is labeled test-set overfitting, not a valid headline |
| synthetic boundary preserved | abuse / `tm-8-abuse-2` | follow-ups include synthetic and payload-derived arms | report is read | synthetic, reality-check, and real data claims are distinct |
| no raw examples | abuse / `tm-8-abuse-3` | public issue/reports are generated | evidence is inspected | only paths, labels, counts, and metrics appear |
| remaining gaps visible | degraded state | several follow-ups are partial | report is read | remaining real-traffic FP and outbound/runtime gaps are explicit |

## Validation plan

| Check | Command | Expected | Actual Result | Status |
|---|---|---|---|---|
| Repo hygiene | `git status --short --branch && git rev-parse --abbrev-ref HEAD && git symbolic-ref --short refs/remotes/origin/HEAD` | branch is non-default; dirty tree recorded | branch `slo/issues-9-10-detection-improvements`; default `origin/main`; dirty tree pre-existed and was preserved | pass |
| File presence | `test -f docs/reports/research-notes-q1-q2-action-map.md && test -f docs/slo/tickets/ticket-8-research-notes-action-map.md` | PASS | PASS | pass |
| Key-term coverage | `rg -n "92.5|88.72|hard benign|reality-check|synthetic|real data|validation-frozen" docs/reports/research-notes-q1-q2-action-map.md` | PASS | PASS: all required correction/boundary terms present | pass |
| Diff hygiene | `git diff --check -- docs/slo/tickets/ticket-8-research-notes-action-map.md docs/reports/research-notes-q1-q2-action-map.md docs/CLAIMS-LEDGER.md` plus new-file `--no-index` checks | PASS | PASS: no whitespace diagnostics; new-file `--no-index` checks exited non-zero only because files differ from `/dev/null` | pass |

## Execution evidence

| Evidence | Result |
|---|---|
| Action map | `docs/reports/research-notes-q1-q2-action-map.md`; sha256 `fd112275497b0020b2537ee081cc2104dfb375814966791f103f540f4466300a` |
| Ticket contract | `docs/slo/tickets/ticket-8-research-notes-action-map.md`; final hash recorded in AgentBus artifact metadata |
| Claims ledger | `docs/CLAIMS-LEDGER.md`; final hash recorded in AgentBus artifact metadata |
| Public-safety check | Report contains paths, aggregate metrics, and claim boundaries only; no raw payload examples |

## Accept / kill

- Accept: #8 has a public-safe action map, the claims ledger points to it, and
  validation commands pass.
- Flag: this ticket does not solve the remaining real-traffic FP validation gap.
- Kill: any raw payload examples are added to public docs/comments, or the
  rejected 92.5% number is presented as valid.

## Out of scope

Changing corpus rows, importing payload-derived examples, running new kNN
measurements, editing the Rust/Python normalizers, filing new GitHub issues, or
closing #8 automatically.

## Self-review gate

- [x] Changed files stay inside the ticket allow-list.
- [x] Public evidence contains no raw payload-derived examples.
- [x] The 92.5% value is rejected as test-set overfitting.
- [x] Synthetic, payload-derived reality-check, and real-data claim boundaries
  remain distinct.
- [x] Remaining gaps are not hidden behind completed follow-ups.
- [x] Validation commands are run and recorded.
- [x] GitHub issue #8 and AgentBus are updated with paths only.

## 11. Closure Summary

Completed behavior: issue #8 now has a public-safe action map that reconciles
the Q1/Q2 research notes with completed follow-ups and remaining gaps. The claims
ledger points to the map and records the corrected metric boundary.

Tests and validation: repo hygiene, file presence, key-term coverage, diff
hygiene, and new-file whitespace checks passed.

Lessons and follow-ups: #8 should close as "mapped to action", not "problem
solved". The unresolved blocker is still credible false-positive validation on
realistic benign traffic.

Issue / PR links: source issue #8; PR not opened by this ticket-sized pass.
