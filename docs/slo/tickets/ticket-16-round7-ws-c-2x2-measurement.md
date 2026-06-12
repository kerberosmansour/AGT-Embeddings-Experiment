# Ticket #16 - Round-7 WS-C 2x2 Normalizer x Corpus Measurement

Source issue: https://github.com/kerberosmansour/AGT-Embeddings-Experiment/issues/16
Target branch: `slo/issues-9-10-detection-improvements` (shared active experiment branch)
Stack: Python 3.13 batch harness + Rust `agt-normalize` CLI; no hosted inference

## Smallest user-visible outcome

Researchers get an AGT-shaped, metadata-only measurement harness that compares
old vs new Gate-0 normalizers across the round-4 and round-7 corpora while
holding the downstream detector protocol fixed.

## Sizing gate

| Row | Value |
|---|---|
| One user-visible outcome | yes - one 2x2 evidence harness |
| Changed files | 4 new harness/docs files, generated artifacts under a new directory |
| Public surfaces | 1 CLI: `meta/harness/round7-garak/run_2x2.py` |
| Migration | none |
| New dependency | none required for smoke; real kNN mode requires existing local `fastembed` stack |
| One PR can review | yes |

Fits a single ticket.

## Compact architecture delta

Add `meta/harness/round7-garak/` with a runner, validator, and focused tests.
The runner builds four cells: round-4 old normalizer, round-4 new normalizer,
round-7 old normalizer, and round-7 new normalizer. Each cell freezes its
threshold on validation before reading/scoring test rows, then writes only row
IDs, hashes, labels, metadata, scores, decisions, transform tags, metrics, and
comparison summaries.

Two scorer modes are allowed:

- `knn`: the real fixed detector path, using the round-4 bge-small kNN margin
  protocol and validation-frozen zero-FP threshold selection.
- `metadata-smoke`: deterministic harness-contract scorer for local smoke/CI
  validation when `fastembed` is absent. It must be clearly marked as not the
  headline measurement.

## Contract block

| Field | Value |
|---|---|
| Files allowed to change | NEW `docs/slo/tickets/ticket-16-round7-ws-c-2x2-measurement.md`; NEW `meta/harness/round7-garak/{README.md,run_2x2.py,validate_round7_garak.py,test_round7_garak.py}`; generated NEW `artifacts/round7-garak/**`; generated `scratch/round7-wsc-*` |
| Files to read first | `docs/ARCHITECTURE.md`; `docs/RUNBOOK-round7-garak-corpus.md`; `corpus/round7/generate-round7.py`; `corpus/round7/check-round7.py`; `meta/harness/round6-cascade/{common.py,normalize.py,run_m1_gate0_rescore.py}`; `rust/agt-normalize/README.md` |
| New files allowed | harness README, runner, validator, focused tests, this ticket doc, generated metadata artifacts |
| New dependencies | none for `metadata-smoke`; optional `fastembed` only for `--scorer knn` |
| Migration allowed | no |
| Compatibility commitments | Rust CLI remains the new-normalizer source of truth; runner treats AGT-facing transform names as metadata; no production/default-blocking claim |
| Data classification | Public synthetic corpus and metadata-only artifacts |
| Proactive controls | C8 Protect Data Everywhere (no raw prompt/payload output), C9 Security Logging (transform tags + hashes), experiment governance (validation freeze before test) |
| Abuse scenarios | `tm-16-abuse-1`: raw prompt fields accidentally serialized -> validator fails on forbidden keys. `tm-16-abuse-2`: test threshold tuned after seeing test -> validator requires freeze timestamp and selected split `validation`. `tm-16-abuse-3`: AGT Rust binary missing -> runner fails clearly unless deterministic smoke mode can use a declared fallback. |
| Resource bounds | smoke uses small corpora; pilot/large write bounded JSON/JSONL artifacts; kNN mode is local-only and records model/runtime provenance |
| Invariants/assertions | four cells present; detector/scorer mode constant across cells; validation freeze exists before test metrics; per-row artifacts omit `text`, `prompt`, `content`, and `normalized_text`; no raw URL/email values in artifacts |
| Debugger expectation | inspect one freeze record, one per-row file, and matrix summary before posting issue evidence |
| Static-analysis gates | `py_compile`, focused unittest, corpus checker, harness validator |
| Reversibility / rollback | remove new harness/artifact directory; no existing corpus or normalizer behavior changed |
| Exemplar to copy | `round6-cascade/common.py` metrics/metadata-only helpers and `run_m1_gate0_rescore.py` freeze discipline |
| Anti-exemplar | do NOT add round-7 templates here; do NOT add Rust transforms here; do NOT report `metadata-smoke` as the real kNN result |
| AI tolerance contract | ai_component: true only in `knn` scorer mode. Accepted variance: none for `metadata-smoke`; kNN must record model ID/hash and local runtime. Eval evidence: 2x2 matrix, Wilson intervals, base-rate precision, paired deltas where row IDs align. Must-never: raw text in artifacts or public issue comments. |
| Forbidden shortcuts | no test-split threshold selection; no detector changes between cells; no raw prompt/payload examples in GitHub comments; no unlabeled synthetic/placeholder values |

## BDD scenarios

| Scenario | Category | Given | When | Then |
|---|---|---|---|---|
| smoke 2x2 | happy path | round-4 smoke + generated round-7 smoke | run `--profile smoke --scorer metadata-smoke` | manifest contains exactly four cells and a matrix summary |
| AGT Rust normalizer | happy path | `rust/agt-normalize` CLI exists | new-normalizer cells run | per-row records include closed transform names and `normalizer_id=agt-rust-round7` |
| validation freeze | governance | validation rows are scored | threshold selected | freeze record names `selection_split=validation` before test metrics exist |
| metadata only | abuse / `tm-16-abuse-1` | artifacts are produced | validator walks files | forbidden raw-text-like keys fail validation |
| fixed scorer | governance | four cells are compared | manifest is validated | scorer mode and threshold protocol match across cells |
| missing real kNN deps | invalid input | `fastembed` is unavailable | user requests `--scorer knn` | runner exits with clear setup message, not a fake metric |
| paired deltas | reporting | same corpus/test row IDs across old/new normalizer | matrix is written | treatment-baseline and round-4 regression deltas are reported |

## Validation plan

| Check | Command | Expected |
|---|---|---|
| Branch hygiene | `git status --short --branch` | only expected experiment changes |
| Compile | `python3 -m py_compile meta/harness/round7-garak/*.py` | clean |
| Unit tests | `python3 meta/harness/round7-garak/test_round7_garak.py` | green |
| Rust normalizer tests | `cargo test --manifest-path rust/agt-normalize/Cargo.toml` | green |
| Round-7 corpus smoke | `python3 corpus/round7/check-round7.py scratch/round7-smoke.jsonl --manifest scratch/round7-smoke-manifest.json --require-rust-audit` | PASS |
| Harness smoke | `python3 meta/harness/round7-garak/run_2x2.py --profile smoke --scorer metadata-smoke` | writes `artifacts/round7-garak/smoke/manifest.json` |
| Artifact validator | `python3 meta/harness/round7-garak/validate_round7_garak.py artifacts/round7-garak/smoke/manifest.json` | PASS |
| Real kNN smoke | `.venv-round6/bin/python meta/harness/round7-garak/run_2x2.py --profile smoke --scorer knn --out-dir artifacts/round7-garak/smoke-knn` | PASS + headline-valid smoke manifest |
| Real kNN pilot | `.venv-round6/bin/python meta/harness/round7-garak/run_2x2.py --profile pilot --scorer knn --out-dir artifacts/round7-garak/pilot-knn` | PASS + flagged pilot FP tradeoff |

## Execution evidence

| Evidence | Result |
|---|---|
| Contract smoke | `artifacts/round7-garak/smoke/manifest.json` validates; `metadata-smoke`; not headline-valid |
| kNN smoke | `artifacts/round7-garak/smoke-knn/manifest.json` validates; round-7 recall delta `+0.4844`; benign FP-rate delta `-0.0526`; no round-4 regression |
| kNN pilot | `artifacts/round7-garak/pilot-knn/manifest.json` validates; capped `limit_per_split_label=200`; round-7 recall delta `+0.0872`; benign FP-rate delta `+0.0208`; no round-4 regression |
| Round-7 corpus | `python3 corpus/round7/check-round7.py scratch/round7-smoke.jsonl --manifest scratch/round7-smoke-manifest.json --require-rust-audit` PASS |
| Rust normalizer | `cargo test --manifest-path rust/agt-normalize/Cargo.toml` PASS (`33 passed`) |
| Harness tests | `python3 -m py_compile meta/harness/round7-garak/*.py` and `python3 meta/harness/round7-garak/test_round7_garak.py` PASS |

Pilot interpretation: treatment improves round-7 detection but creates 2 new
benign FPs on the pilot test slice. This is a useful finding, not an accept:
the next normalizer/methodology pass should inspect the benign subclasses and
tighten or bucket the responsible transform(s) before claiming a clean win.

## Accept / kill

- **Accept:** smoke harness and validator pass; output is metadata-only; four
  cells and matrix deltas are present; issue evidence is public-safe and points
  to artifact paths rather than examples.
- **Flag:** `metadata-smoke` results may only prove harness behavior. If used in
  the final report, label them invalid for measurement.
- **Kill:** any raw prompt/payload text leaks to artifacts, threshold selection
  touches test rows, or the scorer/normalizer axes are mixed in a way that
  prevents a clean AGT upstream interpretation.

## Out of scope

Adding corpus templates, importing literal real-world payloads, adding or
tuning normalizer transforms, changing round-4 kNN protocol, or making
production policy/blocking claims.
