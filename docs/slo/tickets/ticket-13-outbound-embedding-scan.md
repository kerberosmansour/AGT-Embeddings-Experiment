# Ticket #13 - Outbound Embedding Scan Final Verification Proposal

Source issue: https://github.com/kerberosmansour/AGT-Embeddings-Experiment/issues/13
AgentBus task: `t_mqb9onv4_0_93f8c40e`
Target branch: `slo/issues-9-10-detection-improvements` (shared active experiment branch)
Stack: docs-only proposal, AGT upstream shape verified through GitHub

## Smallest user-visible outcome

The outbound embedding-scan idea is converted into an AGT-shaped experiment
proposal that preserves the round-7 methodology and keeps semantic output
scanning evidence-grade.

## Sizing gate

| Row | Value |
|---|---|
| One user-visible outcome | yes - one bounded design proposal |
| Changed files | <= 3 docs/ticket files |
| Public surfaces | none |
| Migration | none |
| New dependency | none |
| One PR can review | yes |

Fits a single ticket.

## Compact architecture delta

N/A - no runtime implementation in this repo. The proposal defines how an AGT
runtime integration could run a default-off outbound embedding evidence annotator
at `post_model_call`, `post_tool_call`, and `output`, with policy routing to
`Escalate`/`Warn` rather than default auto-blocking.

## Contract block

| Field | Value |
|---|---|
| Files allowed to change | NEW `docs/slo/tickets/ticket-13-outbound-embedding-scan.md`; NEW `docs/proposals/outbound-embedding-scan-final-verification.md`; `docs/RUNBOOK-round7-garak-corpus.md` |
| Files to read first | GitHub issue #13; GitHub issue #12; `docs/ARCHITECTURE.md`; `docs/RUNBOOK-round7-garak-corpus.md`; `docs/proposals/round7-generator-proposal.md`; `docs/proposals/output-stage-sanitizer-acs-transform.md`; `docs/methodology/source-to-agt-expected-action-mapping.md`; `meta/harness/round7-garak/{README.md,run_2x2.py,validate_round7_garak.py}`; AGT PR #2991; AGT `policy-engine/core/src/verdict.rs` |
| New files allowed | this ticket contract and one proposal doc |
| New dependencies | none |
| Migration allowed | no |
| Compatibility commitments | no generator, checker, normalizer, or harness behavior changes; proposal must not imply #2991 is merged |
| Data classification | Public docs only; no raw outbound examples or payload-derived samples |
| Proactive controls | C8 Protect Data Everywhere (metadata-only public evidence), C9 Security Logging (bounded evidence pointers), experiment governance (validation freeze before test) |
| Abuse scenarios | `tm-13-abuse-1`: embedding score is represented as deterministic auto-blocking -> scope violation. `tm-13-abuse-2`: raw outbound body or payload-derived example appears in telemetry/GitHub/AgentBus -> forbidden. `tm-13-abuse-3`: inbound prompt rows are reused as outbound rows without stage-specific relabeling -> misleading transfer metric. |
| Resource bounds | outbound scan must record embedding calls, chars scanned, cache hit rate, p50/p95 latency, and stage-level throughput impact; docs-only ticket verifies design, not implementation |
| Invariants/assertions | tau is validation-frozen; artifacts are metadata-only; #12 render sanitizer runs before #13 when the output sink can render terminal-control bytes; #13 routes to `Escalate`/`Warn` by default |
| Debugger expectation | inspect the round-7 2x2 freeze discipline and AGT `Decision`/`Evidence` shape before writing |
| Static-analysis gates | `py_compile`; Rust normalizer tests; encoder contract; markdown diff hygiene |
| Reversibility / rollback | remove proposal/ticket and runbook cross-link |
| Exemplar to copy | `meta/harness/round7-garak/` freeze/metadata-only discipline; AGT `Decision::Escalate` and bounded `Evidence` shape |
| Anti-exemplar | do not claim production/default blocking; do not fold #12 byte/render sanitizer into semantic scan; do not post raw examples |
| AI tolerance contract | AI component exists only in future embedding scorer mode. Eval evidence must be aggregate metrics, hashes, model/bank IDs, and bounded evidence only. Must-never: raw text in artifacts or public issue comments. |
| Forbidden shortcuts | no runtime implementation claim, no test-threshold tuning, no raw payload examples, no unlabeled reuse of inbound prompt rows as outbound outputs |

## BDD scenarios

| Scenario | Category | Given | When | Then |
|---|---|---|---|
| evidence-grade routing | happy path | an outbound score exceeds frozen tau | policy consumes the annotation | default route is `Escalate`/`Warn`, not auto-block |
| #12 ordering | happy path | output sink may render terminal controls | #13 scan runs | #12 render sanitizer has already produced the scan subject |
| transfer baseline | methodology | inbound exemplar bank is tested on outbound subjects | experiment reports metrics | result is labeled transfer baseline, not outbound-trained performance |
| outbound corpus shape | methodology | a model response is evaluated | row is built | row surface is an outbound response/tool result/final output, not an inbound prompt pasted unchanged |
| metadata-only docs | abuse / `tm-13-abuse-2` | public updates are posted | GitHub/AgentBus are read | only paths, hashes, commands, and aggregate design claims appear |

## Validation plan

| Check | Command | Expected | Actual Result | Status |
|---|---|---|---|---|
| Repo hygiene | `git status --short --branch && git rev-parse --abbrev-ref HEAD && git symbolic-ref --short refs/remotes/origin/HEAD` | branch is non-default; dirty tree recorded | branch `slo/issues-9-10-detection-improvements`; default `origin/main`; dirty tree pre-existed and was preserved | pass |
| Upstream shape check | `gh pr view 2991 --repo microsoft/agent-governance-toolkit --json ...` and `gh api .../policy-engine/core/src/verdict.rs` | #2991 open; `Decision::Escalate`, `Decision::Warn`, bounded `Evidence`, and `Decision::Transform` exist | PASS | pass |
| Python compile | `python3 -m py_compile corpus/round7/garak_bypass.py corpus/round7/check-round7.py corpus/round7/generate-round7.py` | PASS | PASS | pass |
| Rust normalizer tests | `cargo test --manifest-path rust/agt-normalize/Cargo.toml` | PASS | PASS - 34 tests | pass |
| Encoder contract | `python3 corpus/round7/garak_bypass.py` | PASS | PASS - 11/11 cases | pass |
| Diff hygiene | `git diff --check -- docs/RUNBOOK-round7-garak-corpus.md` plus `--no-index /dev/null` for new docs | PASS | PASS - no whitespace diagnostics; `--no-index /dev/null` exits non-zero only because each new file differs from `/dev/null` | pass |

## Evidence ledger

| Evidence | Result |
|---|---|
| Upstream AGT implementation PR | microsoft/agent-governance-toolkit#2991 is open; shared normalization exists but detector/policy wiring is not merged |
| Upstream ACS verdict shape | `policy-engine/core/src/verdict.rs` has `Decision::Escalate`, `Decision::Warn`, `Decision::Transform`, and 4 KiB bounded `Evidence` |
| Local design artifact | `docs/proposals/outbound-embedding-scan-final-verification.md` |
| Runbook cross-link | `docs/RUNBOOK-round7-garak-corpus.md` now names #13 as the outbound verification follow-on |
| Critical safety finding | outbound embedding scan is evidence-grade by default; above-threshold findings route to `Escalate`/`Warn` unless a separate structural control justifies stronger action |

## Self-review gate

- [x] Changed files stay inside the ticket allow-list.
- [x] Public docs contain no raw outbound/payload examples.
- [x] Proposal does not claim AGT PR #2991 is merged.
- [x] Proposal keeps #12 render sanitization before #13 scanning for renderable sinks.
- [x] Proposal preserves validation-frozen tau, leakage-zero checks, Wilson/base-rate reporting, and metadata-only artifacts.
- [x] Local validation commands pass.

## Accept / kill

- Accept: proposal identifies outbound scan subjects, stage routing, evidence
  payload shape, transfer-vs-outbound-bank methodology, and cost metrics.
- Flag: runtime AGT implementation remains future work outside this repo.
- Kill: proposal frames semantic output scan as default auto-blocking, tunes on
  test rows, or posts raw examples publicly.

## Out of scope

Runtime AGT code, outbound embedding harness implementation, new outbound corpus
generation, detector threshold selection, public raw payload examples, and #12
render sanitizer implementation.

## 11. Closure Summary

Completed behavior: issue #13 now has a bounded AGT-shaped design artifact for
outbound embedding scan as final verification evidence. The proposal defines
scan stages, subject extraction, evidence payload shape, transfer-vs-outbound
bank methodology, cost metrics, and safe policy routing.

Tests and validation: upstream shape was checked against AGT PR #2991 and
`policy-engine/core/src/verdict.rs`; local Python compile, Rust normalizer
tests, garak bypass contract, and markdown diff hygiene pass.

Lessons and follow-ups: the core design constraint is that semantic output
scanning is not structural containment. The scan can improve visibility and
review routing, but default auto-blocking requires a separate executable policy
contract. Runtime AGT implementation and an outbound corpus/harness remain
future work.

Issue / PR links: source issue #13; PR not opened by this ticket-sized pass.
