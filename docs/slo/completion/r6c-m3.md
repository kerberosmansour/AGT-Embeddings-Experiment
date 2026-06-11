# Completion Summary — r6c Milestone 3

## Goal completed
Calibrated three-bucket conformal router over M2 head scores, frozen on
validation, routed test once.

## Result vs §2
ACCEPT — coverage within α (benign escape 1.20%, 1% inside Wilson [0.95%,1.52%])
AND review-queue precision 5.07% ≥ 5% at 1:1000. Flag lane collapsed (documented).

## Files added
- meta/harness/round6-cascade/{buckets.py, run_m3_buckets.py, test_buckets.py}
- artifacts/round6-cascade/m3-buckets/ (freeze, metrics, per-row, provenance, report)

## Tests / evidence
- 10 bucket tests green (incl. brute-force conformal correctness); validator m3
  PASS; M1/M2 artifacts byte-identical.

## Handoff
- Uncertain lane: 2370 attacks / 69 benign → M4 Gate 2 input.
