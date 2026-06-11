# Completion Summary — r6c Milestone 1

## Goal completed
Deterministic Gate-0 normalizer + FP-zero kNN rescore on normalized text.
Result: zero-FP test recall 14.2% → **43.3%**, benign FP rate 0.0%, zero
obfuscation-control FPs.

## Files changed / added
- `meta/harness/round6-cascade/normalize.py`, `common.py`,
  `run_m1_gate0_rescore.py`, `validate-round6-cascade.py`,
  `test_normalize.py`, `test_artifact_hygiene.py`, `requirements.lock`, `README.md`
- `artifacts/round6-cascade/m1-gate0/` (freeze-record, metrics, per-row, provenance, report)
- `.gitignore` (round-6 venv/cache/tmp patterns)

## Tests added
- 15 normalize tests (happy path, bounds, decode guard, edge cases, idempotency/
  determinism/plain-identity property tests over corpus + random strings).
- 4 artifact-hygiene tests (forbidden fields, ground-truth exclusion, closed tag enum).

## Evidence
- Full suite: 19 tests green. Validator `m1`: PASS. `check-round4.py`: PASS.
- Existing round-4/governance artifacts byte-identical (git clean outside allow-list).

## §2 verdict
PARTIAL ACCEPT — kill condition (<10pt movement) decisively not triggered;
zero-FP side-condition satisfied; word-boundary-destruction + multilingual
classes documented as residual future-work transforms.

## Deferred follow-ups
- Word-segmentation transform (recovers compact/chunked/separator, ~600 rows).
- Multilingual handling (translation or multilingual encoder).
