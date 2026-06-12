# Ticket #14 - Round-7 WS-A Generator Verification

Source issue: https://github.com/kerberosmansour/AGT-Embeddings-Experiment/issues/14
AgentBus task: `t_mqb9aquq_690_e8c93f8d`
Target branch: `slo/issues-9-10-detection-improvements` (shared active experiment branch)
Stack: Python stdlib corpus generator/checker + Rust `agt-normalize` CLI

## Smallest user-visible outcome

The WS-A round-7 synthetic generator is documented as implemented-at-M1 and is
freshly verified against the accepted v2 methodology gates before downstream
measurement claims rely on it.

## Sizing gate

| Row | Value |
|---|---|
| One user-visible outcome | yes - status reconciliation plus verification evidence |
| Changed files | <= 3 docs/ticket files; ignored scratch evidence |
| Public surfaces | none; existing generator/checker CLIs unchanged |
| Migration | none |
| New dependency | none |
| One PR can review | yes |

Fits a single ticket.

## Compact architecture delta

N/A - no generator behavior, schema, detector, or normalizer logic changes. This
ticket reconciles the proposal/runbook status and reruns the existing WS-A
verification gates against the current local generator/checker.

## Contract block

| Field | Value |
|---|---|
| Files allowed to change | NEW `docs/slo/tickets/ticket-14-round7-generator-verification.md`; `docs/proposals/round7-generator-proposal.md`; `docs/RUNBOOK-round7-garak-corpus.md`; generated ignored `scratch/round7-wsa-*` |
| Files to read first | `docs/ARCHITECTURE.md`; `docs/RUNBOOK-round7-garak-corpus.md`; `docs/proposals/round7-generator-proposal.md`; `corpus/round7/generate-round7.py`; `corpus/round7/check-round7.py`; `corpus/round7/garak_bypass.py`; `rust/agt-normalize/README.md`; `docs/slo/tickets/ticket-16-round7-ws-c-2x2-measurement.md`; GitHub issue #14 comments |
| New files allowed | this ticket contract and ignored scratch verification outputs only |
| New dependencies | none |
| Migration allowed | no |
| Compatibility commitments | WS-A generator/checker CLIs stay unchanged; generated row schema stays unchanged; WS-C measurement assumptions stay intact |
| Data classification | Public synthetic corpus metadata; generated rows contain prompt-like text and must not be pasted into public comments |
| Proactive controls | C8 Protect Data Everywhere (public comments aggregate-only), C3 Validate Input (checker gates), experiment governance (methodology v2 status explicit) |
| Abuse scenarios | `tm-14-abuse-1`: raw generated prompt text pasted into public GitHub/AgentBus evidence -> forbidden. `tm-14-abuse-2`: stale docs imply design-only or overstate full freeze -> status reconciliation must name M1/local verification accurately. `tm-14-abuse-3`: docs-only change hides a failing generator gate -> rerun smoke/pilot/normalizer checks. |
| Resource bounds | smoke `204` rows; pilot `807` rows; no large-profile run in this ticket |
| Invariants/assertions | checker must pass schema, split leakage, normalized duplicate, matched controls, bypass holdout, raw URL/email, manifest, and Rust-normalizer audit gates |
| Debugger expectation | inspect metadata summaries only; raw generated rows are local debugging material, not public evidence |
| Static-analysis gates | generator/checker smoke and pilot validations; `garak_bypass.py`; `cargo test` |
| Reversibility / rollback | revert docs/ticket status updates and delete ignored scratch outputs |
| Exemplar to copy | existing #14 implementation update comment and #16 metadata-only reporting discipline |
| Anti-exemplar | do not tune generator/checker while verifying; do not update detector metrics here; do not post raw generated examples |
| AI tolerance contract | N/A - no AI component; deterministic generator/checker validation only |
| Forbidden shortcuts | no raw examples in issue comments; no large/full-freeze claim from smoke/pilot; no closing WS-A before public issue workpad records evidence |

## BDD scenarios

| Scenario | Category | Given | When | Then |
|---|---|---|---|
| smoke profile verifies | happy path | current generator and Rust normalizer CLI | generate/check smoke profile with Rust audit | `204` rows pass all checker gates |
| pilot profile verifies | happy path | current generator and Rust normalizer CLI | generate/check pilot profile with Rust audit | `807` rows pass all checker gates |
| bypass contract holds | compatibility | 11 WS-A encoders and the Rust normalizer binary | run `garak_bypass.py` | all encoders recover the probe phrase and expected transform tags |
| Rust normalizer tests hold | compatibility | current `rust/agt-normalize` crate | run cargo tests | all Rust tests pass |
| docs status is honest | abuse / `tm-14-abuse-2` | M1 exists but large profile is not frozen here | proposal/runbook are read | status says M1/local verification, not design-only and not production/large freeze |
| public-safe issue update | abuse / `tm-14-abuse-1` | GitHub issue #14 is public | post workpad | comment includes paths/counts/hashes only |

## Validation plan

| Check | Command | Expected | Actual Result | Status |
|---|---|---|---|---|
| Repo hygiene | `git status --short --branch && git rev-parse --abbrev-ref HEAD && git symbolic-ref --short refs/remotes/origin/HEAD` | branch is non-default; dirty tree recorded | branch `slo/issues-9-10-detection-improvements`; default `origin/main`; dirty tree pre-existed from round-7 work and was preserved | pass |
| Baseline smoke generation | `python3 corpus/round7/generate-round7.py --profile smoke --out scratch/round7-wsa-smoke.jsonl --manifest scratch/round7-wsa-smoke-manifest.json` | writes smoke corpus/manifest | PASS: `204` rows | pass |
| Baseline pilot generation | `python3 corpus/round7/generate-round7.py --profile pilot --out scratch/round7-wsa-pilot.jsonl --manifest scratch/round7-wsa-pilot-manifest.json` | writes pilot corpus/manifest | PASS: `807` rows | pass |
| Smoke checker | `python3 corpus/round7/check-round7.py scratch/round7-wsa-smoke.jsonl --manifest scratch/round7-wsa-smoke-manifest.json --summary-json scratch/round7-wsa-smoke-check-summary.json --require-rust-audit` | PASS | PASS | pass |
| Pilot checker | `python3 corpus/round7/check-round7.py scratch/round7-wsa-pilot.jsonl --manifest scratch/round7-wsa-pilot-manifest.json --summary-json scratch/round7-wsa-pilot-check-summary.json --require-rust-audit` | PASS | PASS | pass |
| Encoder contract | `python3 corpus/round7/garak_bypass.py` | PASS | PASS: `11/11` encoders round-trip | pass |
| Rust normalizer tests | `cargo test --manifest-path rust/agt-normalize/Cargo.toml` | PASS | PASS: `34` tests | pass |
| Diff hygiene | `git diff --check -- docs/proposals/round7-generator-proposal.md docs/RUNBOOK-round7-garak-corpus.md` plus `--no-index /dev/null` for the new ticket file | PASS | PASS: no whitespace diagnostics; new-file `--no-index` exited non-zero only because the new file differs from `/dev/null` | pass |

## Execution evidence

| Evidence | Result |
|---|---|
| Smoke profile | `204` rows; splits `exemplar_bank=38`, `validation=83`, `test=83`; manifest output sha256 `52ac85d36a967d3c34947e4e97e96372f4c79e87e20f9b9c29e2e4a857b0f21c` |
| Pilot profile | `807` rows; splits `exemplar_bank=216`, `validation=300`, `test=291`; manifest output sha256 `edf2b082a611e84d6ca0effe72c1e27a26315e23adee91b16711a9345453f28e` |
| Checker gates | schema errors `0`; family/group/semantic split leaks `0`; exact/near cross-split duplicates `0`; new bypass in exemplar `0`; missing matched controls `0`; raw URL/email count `0`; Rust-normalized cross-split collisions `0` |
| Encoder contract | `11/11` WS-A encoders round-trip through the Rust normalizer with expected transform tags |
| Rust normalizer | `34` Rust tests pass |
| Artifact hashes | smoke manifest `ec9033dc2ca675e5a71b72c6a2be65fe1211080c3d3c47728032349c36341bc9`; smoke summary `270e65a79cbcd5ad976e6716389ccdc2c326c03c70c4ef838c100495dec35112`; pilot manifest `1a113c87830b067ad7f1a2629f084513b915ccf231cc2d4886705cd26266e939`; pilot summary `c95f2fbe7e8ad476b8234f5757f2ab42a40a20ab38f235de12d38d0f0a47207f` |

## Accept / kill

- Accept: docs honestly reflect M1/local verification, smoke and pilot pass all
  checker gates, and public issue evidence stays aggregate-only.
- Flag: this is not a large-profile freeze and not production/default-blocking
  evidence.
- Kill: any checker gate fails, any raw generated example is posted publicly, or
  docs imply full freeze/coverage beyond the evidence run here.

## Out of scope

Changing generator templates, changing checker behavior, changing Rust
normalizer behavior, running WS-C metrics, changing reality-check intake rows,
or freezing/publishing the large round-7 corpus.
