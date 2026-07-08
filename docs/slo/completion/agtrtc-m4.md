# Completion Summary - agtrtc Milestone 4

## Goal completed
- The benchmark now has a reproducible M4 live batch runner and validator, plus Linux evidence that the stratified L3 sample and benign utility arm clear the runbook failure bar.

## Files changed
- `docs/RUNBOOK-agt-redteam-benchmark-consolidation.md`
- `benchmarks/agent-redteam/adapters/goose/m4_batch.py`
- `benchmarks/agent-redteam/run-m4-live.sh`
- `benchmarks/agent-redteam/tests/test_m4_batch.py`
- `docs/slo/verify/agtrtc-m4.md`
- `docs/slo/lessons/agtrtc-m4.md`
- `docs/slo/completion/agtrtc-m4.md`

## Tests added
- `benchmarks/agent-redteam/tests/test_m4_batch.py`

## Runtime validations added
- `python3 benchmarks/agent-redteam/adapters/goose/m4_batch.py build-sample --out <out>`
- `python3 benchmarks/agent-redteam/adapters/goose/m4_batch.py run --out <out>`
- `python3 benchmarks/agent-redteam/adapters/goose/m4_batch.py validate --out <out>`
- `bash benchmarks/agent-redteam/run-m4-live.sh`

## Compatibility checks performed
- macOS: `python3 -m unittest discover -s benchmarks/agent-redteam -p "test_*.py" -v` passed: 98 tests OK, 5 expected bwrap skips.
- macOS: `bash benchmarks/agent-redteam/run-smoke.sh` passed.
- macOS: `bash benchmarks/agent-redteam/run-consolidated-smoke.sh` passed.
- macOS: `python3 -m py_compile benchmarks/agent-redteam/adapters/goose/m4_batch.py benchmarks/agent-redteam/tests/test_m4_batch.py` passed.
- macOS: `bash -n benchmarks/agent-redteam/run-m4-live.sh benchmarks/agent-redteam/run-smoke.sh benchmarks/agent-redteam/run-consolidated-smoke.sh` passed.
- macOS: `git diff --check` passed.
- Linux: `python3 -m unittest discover -s benchmarks/agent-redteam -p "test_*.py" -v` passed: 97 tests OK, 2 expected skips.
- Linux: default smoke, consolidated smoke, live smoke, py_compile, bash -n, and `git diff --check` passed.
- Linux: full M4 live batch passed with `failure_bar_clear=true`.

## M4 evidence
- Commit: `d08b1c8`.
- Output directory: `/tmp/agtrtc-m4-full-20260708224509` on the Linux host.
- Sample: 250 rows, 7 attack strata * 30 plus 40 hard-benign utility rows.
- Live evidence: 250 L3 rows, 0 skipped rows.
- Attack action outcome: 210 no-tool-use rows, 0 executed rows.
- Utility outcome: 40 completed rows, 0 false blocks.
- Utility Wilson upper: `0.08762160119728664`, below the `0.10` bar.
- Validation errors: 0.
- Raw-free scan: OK.

## Artifact hashes
| Artifact | sha256 |
|---|---|
| `m4_sample_manifest.json` | `7c191b6e44aaf972d36efe2b67a2c97e25b37fb8193a5f75eec04b95ca47d98e` |
| `m4_live_results.jsonl` | `a0d49be997433fa919fd5761ceb909f517fdc88fb7a580aef398d1a027faf960` |
| `m4_live_report.json` | `5d315bf7c59669273f23add8bebf16f1ef3f85ec68fc1a048d93ef903fd3f218` |
| `m4_validation_report.json` | `c63e5c5496325272822296cec06e42c496ab1dd2a635251c4f319cb8e8805058` |
| `m4_sandbox_proof.json` | `ac0368b920974f1d1a588eb9b066ef292460ed66ce9f54a1dca0c1e16ba83ca2` |
| `SHA256SUMS` | `0321bd2beeb2da7898a87dd6729bab909ec4bf0fa720d33ca1927ed2da9e6ede` |

## Documentation updated
- Runbook M4 tracker and operator readiness evidence updated.
- M4 verification report, lessons, and completion summary written.

## Deferred follow-ups
- M5 must produce the frozen release report that joins M3 L1 evidence and M4 L3/utility evidence.
- Linux-owned AgentBus task `t_mrckfw8z_251_8ed66ad8` still needs the owner to flip status from `blocked` to `done`; Mac attached all completion evidence and hashes.
