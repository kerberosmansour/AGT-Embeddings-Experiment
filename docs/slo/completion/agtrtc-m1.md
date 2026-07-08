# Completion Summary - agtrtc Milestone 1

## Goal completed
- Crosswalk plus additive schema/result contracts now exist for the consolidated AGT benchmark.
- Existing scenarios remain compatible while new metadata-only payload refs can be validated.

## Files changed
- `docs/RUNBOOK-agt-redteam-benchmark-consolidation.md`
- `docs/slo/design/agt-redteam-benchmark-consolidation-threat-model.md`
- `benchmarks/agent-redteam/docs/crosswalk.md`
- `benchmarks/agent-redteam/schema/scenario.schema.json`
- `benchmarks/agent-redteam/schema/result.schema.json`
- `benchmarks/agent-redteam/schema/validate_scenarios.py`
- `benchmarks/agent-redteam/tests/test_schema.py`
- `docs/slo/verify/agtrtc-m1.md`

## Tests added
- Payload-ref valid fixture validates through the CLI.
- Payload-ref missing hash fails with a named reason.
- Static L1 detector rows cannot masquerade as L3 live evidence.
- Crosswalk primary mappings and backlog rows are asserted.
- Threat-model abuse IDs `tm-agtrtc-abuse-1..6` are frozen and asserted.

## Runtime validations added
- `docs/slo/verify/agtrtc-m1.md` records Pass 0 outcome validation, BDD runtime rows, security/tooling rows, and regression evidence.

## Compatibility checks performed
- Existing 24 scenario files validate unchanged.
- Existing AGT redteam smoke passes.
- Existing scorecard smoke remains non-certifying with `certification_claim:false`.

## Documentation updated
- M1 tracker/evidence log/self-review rows updated in the runbook.
- Crosswalk doc added.
- Threat-model doc added.
- Lessons and completion summary added.

## .gitignore changes
- None.

## Test artifact cleanup verified
- Tests used only temporary directories.
- No generated test artifacts were left behind.

## Deferred follow-ups
- M2 must resolve whether the one-family slice is L2/mock-only or gated on real sandboxed L3 readiness.
- M3 must freeze the hard-benign false-positive bar before measuring full-corpus static results.
- M5 must implement stronger recursive raw-free validation and visible skipped/unavailable L3 report states.

## Known non-blocking limitations
- Threat model is frozen as Markdown, not `.slo.json`.
- Reporter integration for the new joint result fields is deferred to later milestones.
