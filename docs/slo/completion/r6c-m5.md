# Completion Summary — r6c Milestone 5

## Goal completed
Aggregation + publication: per-family/per-bypass end-to-end floors, hard-negative
FP table, consolidated 9-line §2 verdict table, round-6 report, and additive
updates to README / CLAIMS-LEDGER / ARCHITECTURE / UPSTREAM-PR-PLAN.

## Result vs §2
Per-family floors PASS — no attack family at 0% (tool_abuse 37.7%,
prompt_leakage 100%). Cascade end-to-end (floor arm): 64.3% recall @ 0.87% FPR.

## Files added / changed
- meta/harness/round6-cascade/{run_m5_summary.py, test_summary not needed — covered by validator}
- artifacts/round6-cascade/m5-summary/ (summary-metrics, provenance)
- docs/reports/round6-cascade-report.md (NEW)
- README.md, docs/CLAIMS-LEDGER.md, docs/ARCHITECTURE.md, docs/UPSTREAM-PR-PLAN.md (additive)

## Evidence
- 48 tests green; validator all PASS; number-consistency verdict table complete;
  existing artifacts byte-identical.

## Non-passable gate restated
Real benign traffic at scale, advisory-only, FP re-measured before blocking.
