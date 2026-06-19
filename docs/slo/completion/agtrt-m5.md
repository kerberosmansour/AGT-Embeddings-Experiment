# Completion Summary — agtrt M5 (raw-free hygiene gate + packaging)

**Outcome delivered (oc-5):** the assessing engineer runs the full chain ending in the raw-free hygiene gate and gets a benchmark they can trust to share — no raw payload/secret/PII in any artifact — plus a `PROMOTION.md` boundary doc.

## Evidence

| Step | Command | Result |
|---|---|---|
| oc-5 front-to-end | `bash run-smoke.sh` (4 steps, ends in hygiene) | validate→harness→scorecard→`raw-free: OK`, `[smoke] OK`, exit 0 |
| Anti-vacuity (abuse-1) | planted `AKIA…` secret | scan exits non-zero, names artifact:line |
| Full tests | unittest discover | 46 passed (16+9+5+9+7 M5) |
| Detector not self-flagged | `is_scannable` excludes `.py` | detectors/tests (which hold secret patterns) skipped |
| Packaging | `PROMOTION.md` | raw-free + no-certification + no-upstream-PR; tm-agtrt-abuse-2 hidden-channel note |
| DW ledger | `gh issue` DW-001 filed | content-fixtures deferral routed out |
| Static | `py_compile` + `bash -n` + `git diff --check` | clean |

## What landed (M5 file allow-list)
- `hygiene/raw_free_scan.py` — stdlib, fail-closed raw/secret/PII heuristic scan over DATA artifacts (`.json/.jsonl/.csv/.md/.txt`); excludes `.py` detectors by design.
- `PROMOTION.md` — PR-boundary sequence + deferred routes (DW-001 out; M6/M7/M8 now built) + safety posture.
- `run-smoke.sh` — appended the hygiene step (validate→harness→report→**hygiene**).
- `tests/test_hygiene.py` — 7 tests: clean-pass, planted-secret (anti-vacuity), PEM, detector-exclusion, PROMOTION honesty, hidden-channel note, smoke-has-hygiene.

## Note
DW-002 (Goose) / DW-003 (OpenCRE) / scorecard-product are now BUILT as M6/M7/M8 (founder lifted the cap), so only DW-001 (content-fixtures) is filed out.

## DoD: met (outcome-first — oc-5 passes front-to-end). Tracker M5 → `done`.
