# Lessons Learned - agtrt-v2 Milestone 4

## What changed
- Added a Goose batch wrapper and `run-measurement.sh`.

## Assumptions verified
- Batch results preserve measurement labels and can be scored without modifying the single-scenario M6 adapter.

## Rules for the next milestone
- Linux/Mac live runs must report skipped/no-trace rows plainly.
- Use `--limit=<N>` for bounded slices only when full 240 live execution is too costly or blocked.
