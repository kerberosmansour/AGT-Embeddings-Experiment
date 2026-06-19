# Completion Summary — agtrt M1 (Scenario schema + validator)

**Outcome delivered (oc-1):** the assessing engineer can validate a scenario set front-to-end via the CLI and get a coverage report (or a named reason on failure).

## Evidence

| Step | Command | Result |
|---|---|---|
| oc-1 front-to-end | `python benchmarks/agent-redteam/schema/validate_scenarios.py benchmarks/agent-redteam/scenarios/*.json` | `{"validated":24,"trap_counts":{...all 4}}`, exit 0 |
| Full tests | `python -m unittest discover -s benchmarks/agent-redteam -p "test_*.py"` | 16 passed |
| Fail-closed | unknown trap_class / missing field / extra field / bad JSON | non-zero exit, named reason, no traceback |
| Coverage gap | only Systemic scenarios | exit 1, "uncovered trap classes" named |
| Static | `py_compile` + `git diff --check` + stdlib-only grep | clean |

## What landed
- `schema/scenario.schema.json` + `schema/result.schema.json` — frozen field set (closed enums, `additionalProperties:false`).
- `schema/validate_scenarios.py` — stdlib, fail-closed, explicit path args (no glob — Win audit Finding 2), JSON stdout, structured errors, exit 0/1/2. Carries `raw_free_violations()` + `certification_terms()` helpers (M1 concept; full gate is M5).
- `scenarios/*.json` — 24 seed scenarios, 4 per trap class × 6 classes, raw-free (`agent_visible` = `[UNTRUSTED_INSTRUCTION_PLACEHOLDER]`).
- `tests/test_schema.py` — 16 tests: oc-1 front-to-end (subprocess CLI), §5.5 invariants, abuse tm-agtrt-abuse-1 (raw payload) + tm-agtrt-abuse-4 (certification term), stdlib-only.

## Invariants encoded (§5.5)
unknown trap_class/target_layer rejected; ≥1 `AGT-AC-NNN` control + ≥1 success_condition required; `views == {human_visible, agent_visible}`; closed field set; all 6 classes × 4 across the seeds; unknown opencre relation rejected.

## DoD: met (outcome-first — oc-1 passes front-to-end). Tracker M1 → `done` on merge.
