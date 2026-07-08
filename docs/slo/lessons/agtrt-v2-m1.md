# Lessons Learned - agtrt-v2 Milestone 1

## What changed
- Added additive measurement metadata to the closed scenario schema and validator.

## Assumptions verified
- Existing 24-row seed scenarios still validate without measurement labels.
- Measurement-path rows can fail closed when labels are missing or inconsistent.

## Rules for the next milestone
- Keep the measurement suite separate from the smoke suite.
- Treat `scenario_kind` and `expected_control_behavior` as the measurement contract, not prose.
