# Ticket #12 - Output-Stage Sanitizer ACS Transform Proposal

Source issue: https://github.com/kerberosmansour/AGT-Embeddings-Experiment/issues/12
AgentBus task: `t_mqb9fn6d_205_69ecbd79`
Target branch: `slo/issues-9-10-detection-improvements` (shared active experiment branch)
Stack: docs-only proposal, AGT upstream shape verified through GitHub

## Smallest user-visible outcome

The output-stage sanitizer idea is converted from a captured issue into an
AGT-shaped proposal with the key safety distinction between full inbound
canonicalization and render-safe output transformation.

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
runtime integration should use `Decision::Transform` with a render-safe
sanitizer profile at output sinks.

## Contract block

| Field | Value |
|---|---|
| Files allowed to change | NEW `docs/slo/tickets/ticket-12-output-stage-sanitizer.md`; NEW `docs/proposals/output-stage-sanitizer-acs-transform.md`; `docs/proposals/agt-upstream-normalizer-rfc.md` |
| Files to read first | GitHub issue #12; GitHub issue #13; `docs/proposals/agt-upstream-normalizer-rfc.md`; `rust/agt-normalize/README.md`; `rust/agt-normalize/src/lib.rs`; `docs/RUNBOOK-round7-garak-corpus.md`; `docs/proposals/round7-generator-proposal.md`; `docs/slo/tickets/ticket-15-round7-normalizer-fp-triage.md`; AGT PR #2991 and RFC #2957; AGT `policy-engine/core/src/verdict.rs` |
| New files allowed | this ticket contract and one proposal doc |
| New dependencies | none |
| Migration allowed | no |
| Compatibility commitments | no generator, checker, normalizer, or harness behavior changes; proposal must not imply #2991 is merged |
| Data classification | Public docs only; no raw terminal-control payload examples |
| Proactive controls | C8 Protect Data Everywhere (metadata-only public evidence), C3 Validate Input (render-safe sanitizer bounds), experiment governance (structural vs evidence distinction) |
| Abuse scenarios | `tm-12-abuse-1`: full inbound canonicalized text used as the output replacement -> corrupts benign output. `tm-12-abuse-2`: raw unsafe output appears in telemetry or GitHub comments -> forbidden. `tm-12-abuse-3`: #12 is conflated with #13 and claims semantic harmful-output blocking -> scope violation. |
| Resource bounds | sanitizer should be O(n), bounded, no model call; docs-only ticket verifies design, not implementation |
| Invariants/assertions | `Transform.value` must come from a render-safe sanitizer, not from lowercasing/decoding canonical text; #13 remains separate evidence-grade outbound scan |
| Debugger expectation | inspect upstream `Decision::Transform` shape and local normalizer tests before writing |
| Static-analysis gates | `py_compile`; Rust normalizer tests; encoder contract; markdown diff hygiene |
| Reversibility / rollback | remove proposal/ticket and RFC cross-link |
| Exemplar to copy | AGT `policy-engine/core/src/verdict.rs` `Decision::Transform`; local `Transform::AnsiEscape` benign-safety tests |
| Anti-exemplar | do not use full `normalize()` output as user-visible replacement; do not post raw control-byte examples; do not implement runtime AGT code here |
| AI tolerance contract | N/A - no AI component; deterministic docs and local validation only |
| Forbidden shortcuts | no production/default-blocking claim, no #13 implementation, no raw examples |

## BDD scenarios

| Scenario | Category | Given | When | Then |
|---|---|---|---|
| proposal names render-safe split | happy path | inbound normalizer lowercases/decodes | proposal defines output sanitizer | `Transform.value` comes from render-safe sanitizer, not full canonicalizer |
| terminal escape mapped to structural path | happy path | round-7 has `terminal_escape_injection` blocked on #12 | proposal is read | it gives concrete `stage`, `control_under_test`, `acs_verdict`, and evidence tags |
| #13 separation | abuse / `tm-12-abuse-3` | outbound embedding scan exists as companion idea | proposal is read | semantic harmful-output detection remains #13 and evidence-grade |
| public-safe docs | abuse / `tm-12-abuse-2` | issue and AgentBus are public-ish coordination surfaces | updates are posted | only paths, commands, and design summary are posted |

## Validation plan

| Check | Command | Expected | Actual Result | Status |
|---|---|---|---|---|
| Repo hygiene | `git status --short --branch && git rev-parse --abbrev-ref HEAD && git symbolic-ref --short refs/remotes/origin/HEAD` | branch is non-default; dirty tree recorded | branch `slo/issues-9-10-detection-improvements`; default `origin/main`; dirty tree pre-existed and was preserved | pass |
| Upstream shape check | `gh pr view 2991 --repo microsoft/agent-governance-toolkit --json ...` and `gh api .../policy-engine/core/src/verdict.rs` | #2991 open; `Decision::Transform` exists with `$policy_target` transform payload | PASS | pass |
| Python compile | `python3 -m py_compile corpus/round7/garak_bypass.py corpus/round7/check-round7.py corpus/round7/generate-round7.py` | PASS | PASS | pass |
| Rust normalizer tests | `cargo test --manifest-path rust/agt-normalize/Cargo.toml` | PASS | PASS - 34 tests | pass |
| Encoder contract | `python3 corpus/round7/garak_bypass.py` | PASS | PASS - 11/11 cases | pass |
| Diff hygiene | `git diff --check -- docs/proposals/agt-upstream-normalizer-rfc.md` plus `--no-index /dev/null` for new docs | PASS | PASS - no whitespace diagnostics; `--no-index /dev/null` exits non-zero only because each new file differs from `/dev/null` | pass |

## Evidence ledger

| Evidence | Result |
|---|---|
| Upstream AGT RFC | microsoft/agent-governance-toolkit#2957 is open |
| Upstream AGT implementation PR | microsoft/agent-governance-toolkit#2991 is open; normalizer exposed but not yet wired into detector/policy surfaces |
| Upstream ACS verdict shape | `policy-engine/core/src/verdict.rs` has `Decision::Transform` with `Transform { path, value }` rooted at `$policy_target` |
| Local design artifact | `docs/proposals/output-stage-sanitizer-acs-transform.md` |
| RFC cross-link | `docs/proposals/agt-upstream-normalizer-rfc.md` now points #12 to the companion output-stage proposal |
| Critical safety finding | use full `normalize()` for detection/audit evidence only; use a render-safe sanitizer profile for user-visible `Transform.value` |

## Self-review gate

- [x] Changed files stay inside the ticket allow-list.
- [x] Public docs contain no raw terminal-control payload examples.
- [x] Proposal does not claim AGT PR #2991 is merged.
- [x] Proposal keeps #12 structural render hygiene separate from #13 outbound semantic scanning.
- [x] Local validation commands pass.
- [x] Dirty worktree was preserved; unrelated existing round-7 files were not reverted.

## Accept / kill

- Accept: proposal identifies the render-safe replacement profile, maps #12 to
  ACS `Transform`, and keeps #13 semantic scanning separate.
- Flag: runtime AGT implementation remains future work outside this repo.
- Kill: proposal recommends replacing output with full canonicalized/lowercased
  text or posts raw terminal-control examples publicly.

## Out of scope

Runtime AGT code, policy-engine integration PR, outbound embedding scan (#13),
round-7 generator changes, and public raw payload examples.

## 11. Closure Summary

Completed behavior: issue #12 now has a bounded AGT-shaped design artifact for
output-stage render sanitization using ACS `Decision::Transform`. The proposal
maps `terminal_escape_injection` to a structural post-tool-call/output control
while explicitly separating detection/audit normalization from user-visible
output replacement.

Tests and validation: upstream shape was checked against AGT RFC #2957, AGT PR
#2991, and `policy-engine/core/src/verdict.rs`; local Python compile, Rust
normalizer tests, garak bypass contract, and markdown diff hygiene pass.

Lessons and follow-ups: the most important design constraint is that full
inbound canonicalization is not replacement-safe because it may lowercase,
decode, or otherwise rewrite benign content. AGT needs a render-safe sanitizer
API/profile before wiring `Transform.value`. Runtime AGT implementation and
the #13 outbound semantic scan remain separate follow-ups.

Issue / PR links: source issue #12; PR not opened by this ticket-sized pass.
