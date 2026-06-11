# Lessons Learned — r6c Milestone 3 (conformal three-bucket routing)

## Result
- ACCEPT. Benign escape from PASS = 1.20% (target 1%); 1% lies inside the
  Wilson 95% interval [0.95%, 1.52%] → coverage transfers validation→test.
- Review-queue precision at 1:1000 = 5.07% ≥ 5% (marginal pass). Uncertain lane
  = 64.4% of attacks vs 1.20% of benign → 2370 attacks / 69 benign to review.

## Key finding
- The FLAG lane collapsed (t_high = 1.0): α_flag = 0.1% is stricter than the
  calibrated-score resolution given ~2k cal-B benign rows, so the 99.9% order
  statistic clips to the max. The router is effectively two-lane; everything
  non-pass flows to Gate 2. Benign for the cascade, documented as a caveat.

## Design decisions
- Split-conformal: cal-A (half val benign + all val attack) for the isotonic
  fit; cal-B (other half benign, benign-only) for the conformal thresholds.
  cal-B asserted attack-free and never enters fitting.
- Deterministic 50/50 split by sha256(seed:id) — no RNG (resume-safe).
- t_low < t_high asserted at FrozenRouter construction (degenerate → raises).

## Unresolved / caveat
- Conformal guarantee is benign-side only and assumes exchangeability; M2 reused
  validation, so it is approximate — the test coverage check is the real proof.
- A larger benign calibration set or relaxed α_flag would repopulate the flag
  fast-path next round.

## Rules for next milestone
- M4 consumes the uncertain lane (2370 atk / 69 ben) and adjudicates with
  governance metadata; pass-lane attacks (1310) are already missed at this stage.
