# Lessons Learned — r6c Milestone 4 (tiered Gate-2 ablation)

## Results vs §2 (all three bars NOT met, but rich findings)
- floor − control = +3.78pt (< 5pt bar): metadata helps, modestly.
- error overlap: miss-side 2.76 > 1.5 → independence refuted (shared blind spots).
- end-to-end max 64.4% @ 0.80% FPR (< 80% bar): structural ceiling.

## The four findings
1. **Gate 2 is a working FP-reducer**: ceiling arm holds 64.4% recall while
   cutting uncertain benign flags 69→46 (FPR 1.20%→0.80%) — its design job.
2. **Free metadata ≈ full metadata**: floor (free AGT fields) gets +3.8pt over
   score-only; ceiling (operator sink labels + full source_type) adds +0.11pt.
   Deployment headline: the floor tier is sufficient; skip the ceiling integration.
3. **Deterministic rule far weaker** (16.7%): a Rego-only rule on tool_call +
   coarse_source is not enough; a trained arm is needed.
4. **Independence assumption refuted** (miss-side overlap 2.76×): Gate 2 shares
   Gate 1's blind spots because its dominant feature is the same embedding score.
   The fp-side ratio (83) is a structural artifact (empty flag lane) — reported
   transparently, not headlined.

## Why 80% is unreachable
M3's conformal pass lane sheds 35.6% of attacks to keep benign coverage, so the
end-to-end recall ceiling is 64.4% regardless of Gate 2. Lifting it needs a
better Gate 1 (fewer attacks shed) or a higher FP budget — not a better Gate 2.

## Design decisions
- F-ENG-5 pinned overlap formulas computed; the fp-side proved degenerate in
  this empty-flag-lane configuration — documented as a method caveat for M5.
- Fail-closed coarsening implemented (absent trust→other, absent sink→sensitive),
  though the corpus exercised no substitutions.
- Ground-truth fields excluded by omission from the meta map + asserted in coarsen().

## Method caveat to carry to M5
- The §2 "worse of miss/fp ≤1.5" bar is unsatisfiable by construction when the
  flag lane is empty (fp-side is structural). M5 should report the miss-side
  ratio as the meaningful independence number and flag the fp-side as artifact.
