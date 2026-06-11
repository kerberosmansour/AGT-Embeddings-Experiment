# Round-6 M2 — trained head vs kNN curve + LOFO report

**Verdict vs §2 M2 head bar: NOT SUPPORTED (hypothesis refuted on this corpus).**
**Verdict vs §2 M2-LOFO sub-gate: PASS (decisively).**

## The hypothesis and the result

M2 tested the literature claim (PromptShield arXiv:2501.15145; embeddings+RF
arXiv:2412.01547) that a trained head over the same embeddings beats a
cosine/kNN threshold at deployable false-positive rates. On this corpus, with
bge-small embeddings of normalized text, **it does not.**

| metric | kNN margin (M1) | trained head (M2, HGB d=3 lr=0.1) |
|---|---:|---:|
| ROC-AUC (test) | 0.9470 | 0.9586 |
| TPR @ 1% FPR (test curve) | **0.6323** | 0.6274 |
| TPR @ 0.1% FPR (frozen val cutoff) | — | 0.4674 (realized FPR 0.0) |
| TPR @ 1% FPR (frozen val cutoff) | — | 0.6090 (realized FPR 0.77%) |

The head clears the ≥60% TPR@1%FPR primary number (60.9%), but it **does not
beat kNN** — and the compound accept bar also requires curve dominance for all
FPR ≤ 2%, which fails.

## Where the curves cross (test split)

| FPR | head TPR | kNN TPR | head − kNN |
|---:|---:|---:|---:|
| 0.000 | 0.517 | 0.582 | −0.065 |
| 0.001 | 0.560 | 0.583 | −0.023 |
| 0.005 | 0.587 | 0.619 | −0.032 |
| 0.010 | 0.627 | 0.632 | −0.005 |
| 0.011 | 0.639 | 0.633 | +0.006 |
| 0.020 | 0.702 | 0.648 | +0.054 |

**kNN dominates the head across the entire FPR ≤ 1% region** — exactly the
deployable region. The head only pulls ahead above 1.1% FPR, which is why its
overall AUC is higher while it loses where it matters.

## Reading

The decision rule is **not** the bottleneck at deployable FPR; kNN and the head
are within ~2 points of each other at 1% FPR, and kNN is marginally better. The
real lever was M1 normalization (it moved zero-FP recall 14%→43% and lifts the
1%-FPR operating point to ~63%). On a heavily templated synthetic corpus a 28k
nearest-neighbour bank is a very strong signal at the low-FPR tail; a
regularized head generalizes but loses the sharp neighbour signal there. The
literature's head-beats-kNN result does not reproduce here — a finding worth
carrying upstream, since it argues the cheap kNN signal is sufficient and a
trained head adds little on this data.

## LOFO generalization (8 folds, frozen HGB spec) — PASS

| held-out family | held-out test TPR @ 1% FPR |
|---|---:|
| direct_override | 0.982 |
| prompt_leakage | 1.000 |
| data_boundary_abuse | 0.982 |
| memory_poisoning | 0.584 |
| tool_result_injection | 0.500 |
| output_exfiltration | 0.365 |
| tool_abuse | 0.342 |
| indirect_injection | 0.847 |
| **median** | **0.716** |
| families below 5% | **0** |

§2 M2-LOFO bar (median ≥ 25%, ≤ 2 families < 5%) is cleared comfortably. The
head does **not** generalize by family memorization — every held-out family,
including the two that sat at 0% under the M1 FP-zero point (tool_abuse,
prompt_leakage), is caught well above the floor when entirely unseen in
training. This substantially de-risks the cascade.

## Decision for the cascade

Proceed to M3 on the calibrated head score (native probabilities for isotonic
calibration; within 2–3 points of kNN). End-to-end cascade numbers would be
marginally **better** with a kNN-routed variant at deployable FPR — recorded so
M5 does not overclaim the head. The M2 headline stands: **trained head not
supported; normalization (M1) was the decisive lever; generalization is strong.**
