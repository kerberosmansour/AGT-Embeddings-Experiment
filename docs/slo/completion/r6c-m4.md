# Completion Summary — r6c Milestone 4

## Goal completed
Tiered Gate-2 ablation (control/floor/ceiling/rule) over the uncertain lane,
with pinned overlap ratios and lane-shift diagnostic.

## Result vs §2 (all three bars NOT met)
- floor−control +3.78pt (<5pt); miss-side overlap 2.76 (>1.5, independence
  refuted); end-to-end max 64.4% (<80%, structural ceiling).

## Positive findings
- Gate 2 reduces FP at constant recall (69→46 benign, 1.20%→0.80% FPR).
- Free metadata ≈ full metadata (floor +3.8pt; ceiling +0.1pt over floor) →
  deployment insight: skip the expensive integration.
- Deterministic rule far weaker (16.7%) → trained arm needed.

## Files added
- meta/harness/round6-cascade/{gate2.py, run_m4_gate2.py, test_gate2.py}
- docs/methodology/round6-corpus-to-agt-field-mapping.md
- artifacts/round6-cascade/m4-gate2/ (freeze, metrics, lane-shift, per-row, coefficients, provenance, report)

## Tests / evidence
- 10 gate2 tests green; validator m4 PASS; M1–M3 artifacts byte-identical.

## Method caveat for M5
- fp-side overlap (83) is a structural artifact of the empty flag lane; miss-side
  (2.76) is the meaningful independence number.
