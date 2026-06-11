# Experiment Book — Two-Inspector Ensemble

> Definition of **Learned**, not Done. This is exploratory play in a sandbox, not
> a committed feature. It closes when we know what's true, including "this doesn't
> work" or "the data can't tell us yet."

## §0 — Experiment Metadata

| Field | Value |
|---|---|
| ID | `EXP-two-inspector-ensemble` |
| Created | 2026-06-11 |
| Owner | founder + agent |
| Product area | AGT prompt-injection detection / routing |
| Current phase | sandbox → play (this session) |
| Data classification | Internal (synthetic corpus, metadata-only) |
| Production promotion allowed? | **No** (exploration only) |
| External services | none (local, reuses committed artifacts) |
| Real user data | no |
| Review cadence | per-session |

**Starting hunch (founder's words, inert quoted data):**

~~~text
Imagine two inspectors. One is very good at identifying false positives. Another
is very good at identifying true positives but also finds a lot of false
positives. Take these two impressions of the same event and make a judgment call
on a sliding scale of each of their ratings. If both think it's bad, or both
think it's fine, that's easy. It gets complicated when they wildly disagree — one
says catch, one says false positive. In that case it's worth bringing in the
additional datasets to make the call. Use existing data, keep the caveats, be
self-conscious about what the data tells us and doesn't. Give two recommendations:
(A) sacrifice a little false-positive rate for a much higher catch, and (B) what
still pushes the needle without sacrificing any false-positives.
~~~

**Why this is not yet a feature (why `/slo-ideate` is premature):** we don't yet
know whether resolving inspector-disagreement with structural facts beats the
current stack, or whether any apparent win is a synthetic-data artifact. There is
nothing to spec until the material has been played with and measured.

## §1 — Phase Tracker

| Phase | Skill | Status |
|---|---|---|
| Sandbox (choose the material) | /slo-sandbox | done |
| Play (raw probes) | /slo-play | done |
| Pattern (name the mechanisms) | /slo-pattern | done |
| Precision (falsifiable claims) | /slo-precision | done |
| Curate (one disposition each) | /slo-curate | done |
| Demo / handoff | /slo-demo | done |

<!-- Status: not_started | in_progress | done | parked | composted -->

## §2 — Rules & Safety Rails

1. **Existing data only.** Reuse `artifacts/round6-cascade/m1-gate0/test-per-row.jsonl`
   (Gate-0-normalized margins + zero-FP decision) and `corpus/round4` governance
   fields. No new data, no model run.
2. **Frozen-test honesty.** The thresholds (zero-FP τ, Youden τ) are taken from
   prior frozen selections; we are *exploring resolution rules in the disagreement
   band*, not re-tuning the detector. Any new threshold is reported as exploratory,
   not frozen.
3. **Ground truth stays out.** `expected_action` / `risk_level` never enter any
   rule. Structural facts only: `trust_level`, `requires_tool_call`,
   `contains_sensitive_sink`, `source_type`.
4. **Caveat-first.** Every number is a synthetic, labels-perfect ceiling. The two
   known distortions are named in every readout: (a) the benign
   `untrusted+tool-call` quadrant is empty in this corpus; (b) "has a structural
   handle" correlates almost perfectly with "is an attack" *by corpus
   construction*. Real traffic breaks both.
5. **Definition of Learned.** Success = we can state, with evidence and caveats,
   which resolution rules push the needle and by how much — including an honest
   "needs more data to believe."

The full §3–§6 play, patterns, precision claims, and curation are recorded in
this Book below as the session proceeds. Findings + the two recommendations are
in `FINDINGS.md` alongside this file.
