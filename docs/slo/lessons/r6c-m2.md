# Lessons Learned — r6c Milestone 2 (trained head + LOFO)

## Headline (honest negative result)
- The trained head (HistGB, selected on validation TPR@1%FPR) does **NOT** beat
  the post-normalization kNN margin at deployable FPR. kNN dominates the head
  across all FPR ≤ 1% (the deployable region); the head's higher ROC-AUC
  (0.959 vs 0.947) comes entirely from FPR > 1.1%.
- The literature claim (head > kNN at low FPR) does not reproduce on this
  heavily-templated synthetic corpus with a 28k exemplar bank. M2's hypothesis
  is refuted; M1 normalization was the real lever.

## What passed
- LOFO sub-gate: median held-out TPR@1%FPR = 0.716, 0 families below 5%. The
  head generalizes to entirely-unseen attack families well above floor —
  including tool_abuse (0.34) and prompt_leakage (1.00), which sat at 0% under
  the M1 FP-zero point. Strong de-risking signal: no family memorization.

## Design decisions
- Embedding cache keyed by sha256(normalize.py)+manifest hash (F-ENG-3), so a
  normalizer edit auto-invalidates vectors.
- LOFO retrains with the frozen spec only; per-fold tuning forbidden, fold
  purity (held-out family absent from training) asserted per fold.
- common.py was already extracted in M1, so M2's refactor budget was unused.

## Decision for the cascade
- Proceed to M3 on the calibrated head score (native probabilities ease
  isotonic calibration; within ~2-3 pts of kNN). M5 must state the head did not
  beat kNN at deployable FPR so the cascade does not overclaim the head.

## Rules for next milestone
- M3 calibrates the head score and sets conformal benign-side bucket thresholds;
  cal-B must stay benign-only and out of any fitting path.
