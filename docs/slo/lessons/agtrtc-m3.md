# Lessons Learned - agtrtc Milestone 3

## What changed
- Added `meta/harness/agent-redteam-consolidated/` with a static L1 runner, validator, shared helpers, and README.
- Added focused M3 BDD/outcome tests for full-corpus L1 output, raw-free validation, freeze split guard, evidence-level guard, and hard-benign FP bar enforcement.
- Froze the hard-benign false-positive Wilson upper bar at `0.10` before implementation.
- Produced a temp-artifact L1 report over 54,034 rows from round4-large and round7-large.

## Results vs thesis
- The M3 thesis held: corpus-scale static evidence can be generated as metadata-only L1 rows without claiming containment.
- The leading metric moved from a one-family M2 bridge to a full static corpus artifact with per-family and per-stratum metrics.
- Guardrails held: no raw text, no dependencies, no live/provider/adapters path, no L2/L3 evidence, and existing M1/M2 smokes stayed green.

## Outcome vs promise
- `oc-agtrtc-4` materialised at runtime: an engineer can run L1 measurement, validate the artifact, join rows by `payload_ref`, and inspect which strata need L3 sampling.
- Adjacent critical outcomes were preserved: existing AGT redteam smoke, M2 consolidated smoke, and existing Round-7 harness validation all remained green.

## Design decisions and why
- Used a deterministic structural static detector because M3 needs full-corpus L1 coverage without optional kNN dependencies or live model calls.
- Wrote all output rows as metadata-only payload refs with corpus manifest hashes so later milestones can join without raw prompt text.
- Reported L3 sampling needs from low-recall test families rather than hiding weak strata behind aggregate recall.
- Kept generated L1 artifacts in temp output during verification to avoid committing large generated JSONL.

## Mistakes made
- The original M3 runbook section lacked BDD and Evidence Log blocks; M3 added them before implementation so closeout could be mechanical.
- The exact hard-benign bar was missing until M2 lessons forced it to be frozen.

## Root causes
- The consolidation runbook was written at planning depth first, while execution needed stricter machine-checkable rows for raw-free, freeze, and evidence-level gates.
- Existing harnesses already had several static-measurement styles, so M3 needed to choose the simplest one that satisfied this runbook without changing earlier harnesses.

## What was harder than expected
- "Full corpus" in this repo spans both round4-large and round7-large, so the validator needed multi-corpus hash accounting rather than a single manifest field.
- Keeping artifacts public-safe required avoiding convenient but risky fields from source rows.

## Naming conventions established
- L1 static report schema: `agt-consolidated-l1-static-report-v1`.
- L1 freeze schema: `agt-consolidated-l1-freeze-record-v1`.
- Static detector id: `agt-structural-l1-v1`.
- Hard-benign bar key: `hard_benign_fp_wilson_upper_bar`.

## Test patterns that worked well
- Mutation-based validator tests made each failure-bar clause executable.
- The temp-output front-to-end test covered runner, report, result JSONL, freeze record, and validator in one user journey.

## Missing tests that should exist now
- M4 must add sandbox-readiness tests that prove L3 rows cannot be emitted without OS-enforced sandbox proof.
- M4 should add sample-manifest immutability tests: modifying the sample after the first live result must fail.
- M5 should reuse the M3 raw-free validator shape for final release reports and HTML/Markdown output.

## Rules for the next milestone
- Do not start L3 execution unless sandbox and budget readiness are explicit; if unavailable, M4 must fail closed or produce skipped-with-reason metadata, not fake L3.
- Freeze the M4 sample manifest before any live result is read.
- Include benign utility rows in M4; do not let attack ASR hide false blocks.
- Seed M4 active attack strata from M3's low-recall families, but keep sample size and cost bounded.

## Template improvements suggested
- Planning runbooks should include BDD, Evidence Log, and Self-Review blocks for every milestone from the start.
- Milestones that require numeric bars should include an explicit row for the pre-registered threshold.

## Issue filing
- No retro-derived GitHub issue filed in this closeout. Follow-ups are already represented as M4/M5 gates.
