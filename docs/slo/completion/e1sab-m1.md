# Completion — e1sab M1

## Goal completed
Structural rules R1–R4 + combined-stack evaluation, by control and by technique,
on the frozen test split. No model run; reused round-6 zero-FP embedding decision.

## Result
- Deployable stack embedding(zero-FP) ∨ R1 = 81.0% block @ 0.0% false-block.
- R1 owns the 4 action families (100%, 0% FP); R2 rejected (100% benign FP); 3
  residual families named with targeted fixes.

## Files added
- meta/harness/exp1-structural/{rules.py, run_exp1_eval.py, validate-exp1.py, test_rules.py, test_hygiene.py, README.md}
- artifacts/exp1-structural/ (rule-definitions, by-technique, by-bypass, by-benign, handle-rate, verdicts, per-row, provenance)

## Evidence
- 11 tests green (rules + hygiene); validate-exp1 PASS (rates reproduce exactly);
  round-6 m1 + round-4 validators green; existing artifacts byte-identical.
