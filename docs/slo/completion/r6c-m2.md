# Completion Summary — r6c Milestone 2

## Goal completed
Trained head over normalized embeddings + 8-fold LOFO, frozen on validation.

## Result vs §2
- Head bar: NOT SUPPORTED — head TPR@1%FPR 60.9% but does not beat kNN (kNN
  dominates all FPR ≤ 1%); compound dominance condition fails. Hypothesis refuted.
- LOFO sub-gate: PASS — median 0.716, 0 families < 5%.

## Files added
- meta/harness/round6-cascade/{head.py, run_m2_head.py, test_head.py}
- artifacts/round6-cascade/m2-head/ (freeze, metrics, per-row, lofo, coefficients, provenance, report)

## Tests / evidence
- 9 head tests green; validator m2 PASS; M1 artifacts byte-identical.

## Deferred
- Encoder upgrade (stronger embedding model) is the literature-indicated lever
  if a future round wants head > kNN; recorded, not pursued this round.
