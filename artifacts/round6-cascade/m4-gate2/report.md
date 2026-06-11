# Round-6 M4 — tiered Gate-2 governance ablation report

**Verdict vs §2 M4 bars: all three NOT met — but the milestone yields three
positive, deployment-relevant findings and one decisive negative one.**

| §2 M4 bar | result | verdict |
|---|---|---|
| floor beats control by ≥5pt end-to-end catch | +3.78pt (60.5% → 64.3%) | **NOT met** (real but < 5pt) |
| error-overlap ratio ≤ 1.5 (worse side) | miss-side 2.76; fp-side 83 (artifact) | **NOT met** — independence refuted |
| end-to-end ≥80% catch @ ≤1% hard FPR | max 64.4% @ 0.80% FPR | **NOT met** — structural ceiling 64.4% |

## The four arms (test, end-to-end)

| arm | end-to-end recall | hard-action FPR | uncertain attacks caught | uncertain benign flagged |
|---|---:|---:|---:|---:|
| flag-all-uncertain (ceiling of possibility) | 0.6440 | 0.0120 | 2370 | 69 |
| control (score only) | 0.6052 | 0.0075 | 2227 | 43 |
| floor (+ tool_call + coarse_source) | 0.6429 | 0.0087 | 2366 | 50 |
| ceiling (+ sink + full source_type) | 0.6440 | 0.0080 | 2370 | 46 |
| rule (deterministic, zero-param) | 0.1666 | 0.0000 | 613 | 0 |

## Finding 1 — Gate 2 works as a false-positive reducer (its actual design job)

Flagging the entire uncertain lane gives 64.4% recall at **1.20%** hard FPR (69
benign). The ceiling arm holds the **same 64.4% recall at 0.80%** FPR (46
benign) — a 33% cut in false positives at zero recall cost. That is exactly what
a Gate 2 is for: adjudicating the uncertain lane to drop false alarms while
keeping catches.

## Finding 2 — free metadata ≈ full metadata (the deployment headline)

- floor − control = **+3.78pt** recall: the AGT-guaranteed fields
  (`requires_tool_call`, coarse source) add real value over score alone.
- ceiling − floor = **+0.11pt**: the integration-dependent fields
  (operator-configured sink sensitivity, full 6-way source type) add **almost
  nothing** on top of the free fields.

For an AGT deployment this is the most useful result of the round: **the floor
tier — fields every deployment has for free — captures essentially all of the
governance-metadata value. The expensive ceiling integration is not worth it on
this corpus.** Fail-closed substitutions were not exercised here (corpus carries
all fields), but the mapping and fail-closed defaults are in place for real
deployments that lack them.

## Finding 3 — the deterministic rule is far weaker (trained Gate 2 earns its keep)

The zero-parameter rule (`uncertain ∧ tool_call ∧ source ≠ user → flag`) reaches
only 16.7% — most uncertain attacks either don't request a tool or are tagged
`user`. So a trained arm is needed; a Rego-only rule on these two fields is not
sufficient.

## Finding 4 (decisive negative) — the independence assumption is refuted

The RFC's load-bearing assumption was that Gate 1 and Gate 2 make *different*
mistakes. They do not, by the meaningful measure:

- **miss-side overlap = 2.76** (floor): attacks that Gate 1 routed to PASS (its
  misses) are missed by a shadow Gate 2 at **2.76× the base miss rate**. Gate 2
  shares Gate 1's attack blind spots — because Gate 2's dominant feature is the
  same embedding-derived calibrated score. Governance metadata does not create
  an independent error structure.
- The fp-side ratio of 83 is a **structural artifact**, reported transparently:
  the flag lane is empty (M3), so Gate 1 contributes zero independent hard FPs;
  Gate 2 only adjudicates the uncertain lane, so 100% of its benign flags fall
  in the non-pass region while the overall benign-flag rate is tiny. The ratio
  is therefore not a meaningful independence measure in this configuration; the
  miss-side 2.76 is.

This confirms the pre-registered concern (and the original design critique):
two gates resting on the same embedding meaning-space share blind spots.
Independence would require a genuinely cross-modal Gate 2 (e.g. activation-based
task-drift detection), not a classifier whose strongest feature is the same
score.

## Structural ceiling — why 80% is unreachable here

M3's conformal PASS lane keeps benign coverage at the cost of routing only 64.4%
of attacks into uncertain; the other 35.6% are "allowed" and unrecoverable
downstream. So **no Gate-2 arm can exceed 64.4%** end-to-end. Reaching 80% would
require either a higher FP budget at M3 (more attacks into uncertain) or a
stronger Gate 1 that sheds fewer attacks into PASS — not a better Gate 2.

## Lane-shift diagnostic (F-ENG-1)

| lane | size | attack | benign | mean cal score |
|---|---:|---:|---:|---:|
| validation uncertain | 2635 | 2529 | 106 | 0.974 |
| test uncertain | 2439 | 2370 | 69 | 0.968 |

Composition is stable validation→test (≈97% attack both), so the floor−control
shortfall and the overlap result are **not** lane-shift artifacts — they are
genuine.
