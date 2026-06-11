# Experiment 4 — Better normalizer + honest ensemble (issues #9, #10)

**Key result:** extending the Gate-0 normalizer lifts the standalone detector
**43% → 49%** and the full ensemble **87.2% → 88.7%**, all at a measured **0%
false-positives** — and an honest re-check shows the earlier **92.5% was test-set
overfitting** (the real figure is ~87%). Net: a real, compounding gain, plus a
correction that keeps the numbers trustworthy.

*Frozen synthetic test set, validation-frozen thresholds. Still a labels-perfect
ceiling — see caveats. AGT = Microsoft Agent Governance Toolkit.*

## Two pieces of work

| Issue | What | Outcome |
|---|---|---|
| **#10** | extend the Gate-0 normalizer (encoding / rot13 decoders) | **encoding catch 35.3% → 62.4%**, overall zero-FP recall 43.3% → 49.0%, 0 FP |
| **#9** | promote both detectors to co-equal precision inspectors, **validation-frozen** | the 92.5% "ceiling" was overfitting → honest **~87%**, tied with Rec B |

---

## #10 — the normalizer win

Added percent/URL, `\uXXXX` unicode-escape, and HTML-entity decoders (plus a
widened rot13 path) to `normalize.py`, each behind the same printable-ratio +
English-benefit acceptance guard so legitimate data is never mangled.

| metric (FP-zero operating point) | before | after |
|---|---:|---:|
| **encoding** bypass-class catch | 35.3% | **62.4%** (+27pt) |
| rot13 | 37.9% | 39.2% |
| overall zero-FP recall | 43.3% | **49.0%** |
| benign FP / obfuscation-control FP | 0 / 0 | **0 / 0** |

Out-of-scope classes unchanged (multilingual 0%, compact/chunked — word-boundary
problem). 24 normalizer/hygiene tests green, including new "benign percent" and
"benign ampersand" guards that prove benign data is left alone.

## #9 — the honest correction

The exp3 finding suggested a co-equal two-model ensemble could reach **92.5% @ 0%
FP**. That number was selected on the **test** split, which we had mined
repeatedly. Re-doing it properly — thresholds chosen on **validation**, test
scored once:

| config (validation-frozen, 0% FP) | catch |
|---|---:|
| co-equal, strict 0-val-FP head | 86.8% |
| co-equal, 0.1%-val-FPR head | 87.2% |
| exp3 Rec B (already validation-frozen) | 87.2% |
| ~~exp3 test-derived "ceiling"~~ | ~~92.5%~~ (overfit) |

**The ~5-point gain did not survive validation freezing.** The honest ensemble is
**~87% @ 0% FP**, tied with Rec B. (Correction: `prompt_leakage` is *not* caught
at 0% FP by either model's honest threshold — earlier 100% claims were
test-derived or measured at 1% FPR.)

---

## The compounding win (does the new normalizer raise the ensemble too?)

Yes. Re-running the whole ensemble with the **#10 normalizer** — re-embed both
signals, **re-train the head** on the new embeddings, thresholds on validation,
test scored once:

| Variant (validation-frozen, 0% FP) | old normalizer | new normalizer |
|---|---:|---:|
| base (kNN @ zero-FP OR R1) | 81.0% | **85.6%** |
| **Rec B** (head agrees, in the band) | 87.2% | **88.7%** |
| co-equal (head agrees, everywhere) | 87.2% | **88.7%** |

**The winning configuration: `Gate-0(extended) → kNN @ zero-FP, OR R1, OR the
re-trained head agreeing = 88.7% @ 0% FP`** — the robust Rec B shape. Co-equal
gives the identical number, so "head in the band" vs "head everywhere" is moot at
0% FP.

**Where the gain comes from:** the normalizer is the bigger lever — it lifts even
the simplest variant +4.6pt (81.0 → 85.6%) on its own; the second-model agreement
adds the final ~3pt on top. The two improvements partly overlap (a stronger Gate 0
catches some of what the head used to rescue) but still net higher than either
alone.

## The program so far (all validation-frozen, 0% FP)

| Milestone | Catch @ 0% FP |
|---|---:|
| Experiment 1 (Gate-0 + kNN zero-FP, OR R1) | 81% |
| Ensemble (+ 2nd model) | 87% |
| Ensemble + extended normalizer (#9 + #10) | **88.7%** |
| (standalone detector, separately) | 43% → **49%** |

## Caveats (unchanged)

- **Synthetic, labels-perfect ceiling.** The 0% FP especially rests on an empty
  benign `untrusted+tool` quadrant and a `handle ≈ attack` correlation that real
  traffic breaks. The #10 normalizer gain is the most robust piece (deterministic,
  measured against benign controls at 0 FP); the ensemble's 0% wants the
  realistic-benign-data validation tracked in issue #8.
- **Prompt injection only**, single-input, single-agent.
- **Not independently verified.**

## Reproduce

- #10 normalizer: `meta/harness/exp4-normalizer-plus/run_bypass_remeasure.py`
- #9 ensemble (old norm): `meta/harness/exp4-coequal/run_coequal.py`
- compounding + variant comparison (new norm): `run_coequal_newnorm.py`,
  `run_variant_compare.py`
- Tickets: `docs/slo/tickets/ticket-10-*.md`. Normalizer:
  `meta/harness/round6-cascade/normalize.py`.
