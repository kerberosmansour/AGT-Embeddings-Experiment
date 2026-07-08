# Verification Report - agtrtc Milestone 1

Target: `docs/RUNBOOK-agt-redteam-benchmark-consolidation.md`
Milestone: M1 - Crosswalk + additive schema/result contracts
Date: 2026-07-08
Verifier: mac-agent

Threat-model mode: formal Markdown artifact now exists at
`docs/slo/design/agt-redteam-benchmark-consolidation-threat-model.md`; no
`.slo.json` exists yet.

## What Was Exercised

| Scenario | Category | How exercised | Result | Evidence |
|---|---|---|---|---|
| Pass 0 `oc-agtrtc-1` | outcome | `python3 -m unittest benchmarks/agent-redteam/tests/test_schema.py -v` drives the validator CLI over 24 existing scenarios plus one temp payload-ref fixture. | pass | 22 focused schema tests OK; `test_oc1_payload_ref_fixture_validates` returned 25 validated rows. |
| `cuj-agtrtc-1` | critical journey | Read `benchmarks/agent-redteam/docs/crosswalk.md`, then validator CLI, then schema tests inspect explicit backlog rows. | pass | Crosswalk primary mappings and backlog assertions passed. |
| existing scenarios still validate | compatibility | `python3 benchmarks/agent-redteam/schema/validate_scenarios.py benchmarks/agent-redteam/scenarios/*.json` | pass | 24 validated; all 6 trap classes have 4 scenarios. |
| payload ref complete | happy path | Focused CLI test writes a temp scenario with `payload_ref`, `delivery_vector`, and `expected_containment`. | pass | `test_oc1_payload_ref_fixture_validates`. |
| payload ref missing hash | invalid input | Focused CLI test writes a temp scenario whose `payload_ref` lacks `corpus_manifest_hash`. | pass | Named failure contains `corpus_manifest_hash`. |
| static result cannot masquerade as live | abuse case | Unit/runtime validator test calls `validate_result` on L1 static detection marked as L3 live. | pass | `test_result_joint_contract_rejects_static_as_l3`. |
| empty crosswalk cell backlog | empty state | Focused schema test inspects the crosswalk for Cognitive State, Human-in-the-Loop, and non-payload Behavioural Control backlog rows. | pass | `test_crosswalk_has_primary_mappings_and_backlog`. |
| core smoke regression | regression | `bash benchmarks/agent-redteam/run-smoke.sh` | pass | Smoke OK: 24 scenarios, 6 traces, 5 blocked, `certification_claim:false`, raw-free OK. |
| full unit regression | regression | `python3 -m unittest discover -s benchmarks/agent-redteam -p "test_*.py"` | pass | 78 tests OK, 5 skipped. |

## Security And Tooling Passes

| Pass | Check | Result | Evidence |
|---|---|---|---|
| Pass 2 | Empty/degraded states | pass | Empty crosswalk cells and missing payload hash fail visibly. |
| Pass 4 | SAST/static | pass | `python3 -m py_compile benchmarks/agent-redteam/schema/validate_scenarios.py` passed. |
| Pass 4 | Secrets/raw-free | pass | `bash benchmarks/agent-redteam/run-smoke.sh` ended in raw-free OK; new crosswalk and threat model are metadata-only. |
| Pass 4 | Dependency/SCA | not_applicable | M1 adds no dependencies; validator remains stdlib-only. |
| Pass 4 | DAST | not_applicable | No service/API/UI surface in M1. |
| Pass 5 | AI tolerance | not_applicable | M1 is deterministic schema/metadata tooling. |
| Pass 6 | Measurement | pass | Crosswalk coverage count and schema validation count are recorded in tests/runbook evidence. |

## Bugs Found

| id | severity | scenario | regression test | status |
|----|----------|----------|-----------------|--------|
| none | n/a | n/a | n/a | n/a |

## Environment

- OS: macOS host via local shell
- Python: `python3` at `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3`
- Browser/UI: not applicable

## Coverage Gaps

- No `.slo.json` threat-model schema artifact exists yet; M1 froze IDs in
  Markdown. Later security automation should promote this to `.slo.json` if the
  runbook needs machine-readable abuse rows.
