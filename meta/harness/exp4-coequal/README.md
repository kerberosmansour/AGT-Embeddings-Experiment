# Ticket #9 — co-equal two-model ensemble (validation-frozen)

Promotes both detectors (kNN margin + trained head) to co-equal precision
inspectors, each frozen at its own zero-FP line **selected on validation**,
OR'd with R1. Test scored once. Uses committed round-6 m1/m2 scores (old
normalizer — apples-to-apples with the exp3 finding). No model run.

## Result — the honest answer

| Config (all validation-frozen) | catch | FP |
|---|---:|---:|
| co-equal, head @ strict 0-val-FP | 86.8% | 0.00% |
| co-equal, head @ 0.1%-val-FPR | 87.2% | 0.00% |
| exp3 Rec B (val-frozen, for comparison) | 87.2% | 0.00% |
| exp3 test-derived "ceiling" | 92.5% | (test-mined) |

**Verdict: the test-derived 92.5% does NOT survive validation freezing.** The
validation-frozen co-equal ensemble is ~**87% @ 0% FP — tied with Rec B**, not
92.5%. The ~5-point gain was **test-set overfitting** (we had mined the test
split repeatedly across exp1/exp3). The methodological caution in issue #9 was
correct and necessary.

**Correction propagated:** `prompt_leakage` is **not** caught at 0% FP by either
model's honest threshold — earlier "100%" claims were test-derived or measured at
1% FPR (round-6 LOFO), not at the 0%-FP operating point.

## Acceptance criteria — met (honest negative result)

- both thresholds selected on validation only; test scored once ✓
- honest validation-frozen catch reported; the gain did NOT survive ✓
- uses committed round-6 scores (old normalizer) ✓

## Run

```
.venv-round6/bin/python meta/harness/exp4-coequal/run_coequal.py
```
Writes `artifacts/exp4-coequal/`. The good-news follow-up (does the **new**
normalizer from #10 raise the ensemble bar?) is measured separately —
see `meta/harness/exp4-coequal/run_coequal_newnorm.py`.
