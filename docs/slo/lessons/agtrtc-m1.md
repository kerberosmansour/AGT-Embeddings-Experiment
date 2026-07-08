# Lessons Learned - agtrtc Milestone 1

## What changed
- Added additive schema/result contract fields for payload refs, delivery vectors, expected containment, detection metadata, and action outcomes.
- Added stdlib validation for payload-ref completeness and static-as-L3 evidence overclaim.
- Added `benchmarks/agent-redteam/docs/crosswalk.md` with primary family mappings plus explicit backlog cells.
- Added `docs/slo/design/agt-redteam-benchmark-consolidation-threat-model.md` to freeze `tm-agtrtc-abuse-1..6`.

## Results vs thesis
- The M1 thesis held: the existing 24 scenarios stayed compatible while the schema gained the metadata needed to bridge corpus payloads later.
- Leading metric moved from no payload-ref validation to a passing front-to-end validator path over old scenarios plus one payload-ref fixture.
- Guardrails held: no dependencies, no raw payload text, no live adapter edits, and existing smoke stayed green.

## Outcome vs promise
- `oc-agtrtc-1` materialised at runtime: the assessing engineer can validate old scenarios plus a new payload-ref fixture through the real CLI.
- The adjacent critical outcome, existing AGT redteam smoke, stayed green.
- The crosswalk backlog is visible, so M1 does not pretend full taxonomy parity.

## Design decisions and why
- Kept new fields optional in schemas because M1 is additive and existing scenarios must validate unchanged.
- Put result validation in the stdlib schema validator rather than the reporter in M1 because reporter integration belongs to later reporting milestones.
- Froze the threat model as Markdown, not `.slo.json`, because the runbook only needed stable IDs for M1 and no schema contract existed yet.

## Mistakes made
- The runbook initially used `python` commands, but this environment only has `python3`. M1 corrected the command contract before implementation.
- The original runbook had no Evidence Log for retro closeout. M1 added one to avoid hand-wavy completion.

## Root causes
- The consolidation runbook was authored as a planning artifact first, while the repo's existing benchmark work already used Python 3 shebangs and outcome tests.
- Critique finding C-SEC-1 exposed that inline threat-model IDs are too easy to drift without a frozen artifact.

## What was harder than expected
- Keeping the M1 allow-list honest while satisfying the critique ask required explicitly adding the threat-model artifact to M1 scope.
- The repo already had a mature AGT redteam M1 from the parent runbook, so the work was mostly consolidation-contract closure rather than greenfield implementation.

## Naming conventions established
- Runbook prefix: `agtrtc`.
- Payload refs use `payload_ref.{id,family,split,corpus_manifest_hash}`.
- Detection verdicts: `flagged`, `clean`, `not_run`.
- Action outcomes: `attempted`, `executed`, `blocked`, `contained`.
- Threat-model IDs: `tm-agtrtc-abuse-N`, append-only.

## Test patterns that worked well
- BDD-first tests that drive the real CLI with temporary fixtures caught optional-field support without modifying committed scenarios.
- A focused `validate_result` test made evidence-level overclaim fail without needing to wire the full reporter in M1.

## Missing tests that should exist now
- M2 should add a consolidated-smoke test that proves L2/mock vs L3/live evidence cannot be confused.
- M3/M5 should add the stronger recursive raw-free validator from critique C-SEC-2.
- A future threat-model milestone should promote the Markdown threat model to `.slo.json` if machine-readable security gates need it.

## Rules for the next milestone
- Resolve critique C-ENG-1 before implementing M2: either M2 is explicitly L2/mock-only, or it is blocked on sandbox and budget readiness for any L3 claim.
- Do not emit any `L3_live_behavioural` row from M2 unless provider/model execution happened inside OS sandbox proof.
- Keep payload refs metadata-only; never copy corpus raw text into scenario templates or reports.
- Preserve existing `run-smoke.sh` green before and after M2.

## Template improvements suggested
- Future runbooks should include Evidence Log and Self-Review Gate sections in every milestone at planning time.
- Runbook metadata should prefer `python3` in this repo because no `python` executable is guaranteed.

## Issue filing
- No retro-derived GitHub issue filed in this closeout. The only follow-ups are already represented as runbook/critique gates for M2, M3, and M5.
