# Round-6 M3 — three-bucket conformal routing report

**Verdict vs §2 M3 bar: ACCEPT (both conditions met; one structural caveat).**

Scope note: the conformal coverage guarantee is **benign-side only** and holds
under exchangeability of benign traffic. It says nothing about attack-side
recall and gives no protection against an adaptive adversary. Validation was
reused for head selection (M2), so cal-B exchangeability is approximate; the
test-split coverage check below is the empirical verification.

## Pre-registered budgets

- α_pass = 1% (max benign fraction escaping the PASS lane)
- α_flag = 0.1% (max benign fraction reaching the FLAG lane)
- Thresholds = conformal `⌈(n+1)(1−α)⌉`-th order statistic over cal-B
  (benign-only half of validation), on isotonic-calibrated scores.

## Result (test split)

| lane | attacks | benign |
|---|---:|---:|
| pass | 1310 | 5659 |
| uncertain | 2370 | 69 |
| flag | 0 | 0 |

- **Benign escape from pass: 69 / 5728 = 1.20%** (target 1%). The Wilson 95%
  interval is [0.95%, 1.52%]; **1% lies inside it**, so coverage holds within
  sampling error. ✓
- **Review-queue precision at 1:1000 prevalence = 5.07% ≥ 5%.** ✓ (At 1:100 it
  is 34.8%.) Marginal pass — the uncertain lane carries 64.4% of attacks against
  1.20% of benign.
- Calibration Brier score: 0.099.

## Structural caveat: the flag lane collapsed

t_high resolved to 1.0 because α_flag = 0.1% is stricter than the calibrated
score resolution (cal-B has ~2k benign rows; the 99.9% order statistic is the
clipped maximum). So no row is auto-flagged; the router is effectively two-lane
(PASS / UNCERTAIN) and everything non-pass flows to Gate 2. This is benign for
the cascade — Gate 2 exists precisely to adjudicate the uncertain lane — but it
means the FLAG fast-path contributes nothing this round. A future round with a
larger benign calibration set, or a relaxed α_flag, would populate it.

## Verdict rationale

- Coverage within α (1% inside Wilson): **met**.
- Queue precision ≥5% at 1:1000: **met** (5.07%, marginal).
- Net: ACCEPT. The calibrated router transfers from validation to test within
  the conformal guarantee, and the review pile is economically plausible (5% of
  the queue is real attacks at realistic rarity, vs 0.54% for the round-4
  single-dial Youden point). The flag-lane collapse is documented, not hidden.
