# Lessons Learned - agtrtc Milestone 4

## What changed
- Added a stdlib-only M4 live batch runner and validator at `benchmarks/agent-redteam/adapters/goose/m4_batch.py`.
- Added `benchmarks/agent-redteam/run-m4-live.sh` as the one-command Linux entrypoint.
- Added focused M4 BDD tests for sample immutability, active stratum size, utility Wilson bar, L3 row structure, manifest tamper, raw-free output, and transport retry behavior.
- Provisioned the Linux worker with the missing Round-7 corpus and an out-of-band Anthropic key without printing or posting secrets.

## Results vs thesis
- The M4 thesis held: a bounded live sample can join corpus-derived strata with sandboxed action evidence and utility false-block measurement.
- The sample stayed bounded at 250 rows instead of all 54,034 L1 rows.
- The failure bar cleared: 250 L3 live rows, 0 skipped, 0 utility false blocks, and Wilson upper `0.08762160119728664 <= 0.10`.

## Outcome vs promise
- `oc-agtrtc-5` materialised on Linux: the engineer gets a frozen manifest, L3 result JSONL, utility metrics, validation report, confidence interval, and raw-free artifact hashes.
- `oc-agtrtc-6` remains enforced: macOS without bwrap still refuses the live path before provider/model execution.

## Design decisions and why
- Kept generated live artifacts in `/tmp` and AgentBus rather than committing them, because they are runtime evidence and not source.
- Used M3 `families_needing_l3_sampling` to choose the seven active attack strata.
- Chose 40 utility rows, not 30, because 0/30 false blocks has a Wilson upper above 10%; 0/40 clears the pre-registered bar.
- Recorded no-tool attack decisions as L3 live decision traces with sandbox proof, instead of pretending a tool action happened.
- Added one retry for transport failures only; sandbox failures still abort immediately.

## Mistakes made
- The first full batch stopped on a provider read timeout because row-level transport errors were not contained.
- The AgentBus task stayed Linux-owned, so Mac could attach evidence and comments but could not mark the Linux task done.

## Root causes
- The single-probe M6 live path was enough for containment proof, but M4 needed batch semantics, frozen sampling, and report validation.
- Provider APIs can fail independently of benchmark safety; the runner needed to separate transport variance from safety failures.

## What was harder than expected
- The failure bar forced a real utility sample size calculation: `n=30` was not enough to prove a 10% Wilson upper bound even with zero false blocks.
- Keeping artifacts raw-free while still reproducible required storing probe template ids and hashes rather than prompt text.

## Rules for the next milestone
- M5 must present M4 as evidence, not certification.
- M5 should carry both layers: L1 static detector evidence and M4 action/utility evidence.
- M5 should make the attack result explicit: this run produced no tool attempts on attack rows and no utility false blocks.
- M5 should keep live artifact paths and hashes visible without committing raw/generated outputs.

## Issue filing
- No new GitHub issue filed. The transport retry fix landed in commit `d08b1c8`.
