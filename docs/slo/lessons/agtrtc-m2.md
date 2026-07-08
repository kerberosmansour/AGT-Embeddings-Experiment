# Lessons Learned - agtrtc Milestone 2

## What changed
- Added a stdlib-only consolidated bridge for the indirect-injection family.
- Added a metadata-only sample manifest with two test-split payload refs.
- Added `run-consolidated-smoke.sh` to emit L1 detector rows, L2 mock action rows, a joint matrix, and a raw-free check.
- Added focused BDD/outcome tests for the bridge, report, live refusal, raw-like key rejection, bounds, and failure-bar behavior.

## Results vs thesis
- The M2 thesis held: one family can produce a useful joint detector/action report before scaling to the full corpus.
- The leading metric `joint_matrix_complete=true` materialised for indirect injection with 2 L1 rows, 2 L2 rows, and 0 L3 rows.
- Guardrails held: no raw payload text, no dependencies, no live provider calls, no adapter changes, and existing AGT redteam smoke stayed green.

## Outcome vs promise
- `oc-agtrtc-2` materialised at runtime: one command produces detector verdicts, L2 mock action outcomes, evidence levels, hashes, and off-diagonal counts.
- `oc-agtrtc-3` also held: requesting live/L3 in M2 refuses with a named reason and emits no fake L3 rows.
- The adjacent critical outcome, existing `run-smoke.sh`, remained green.

## Design decisions and why
- Kept M2 explicitly L2/mock-only because M1 lessons and critique C-ENG-1 said L3 needs real OS sandbox and budget readiness.
- Used a small committed sample manifest rather than corpus expansion because M2's job is bridge proof, not scale.
- Put the raw-like key ban in the bridge because generated reports must be raw-free even if future manifests grow.
- Made `detected -> executed` a failure-bar cell rather than hiding it inside aggregate success.

## Mistakes made
- A manual verification command initially used the wrong bridge option name (`--out-dir` instead of `--out`), which proved the need to keep CLI checks exact.
- `py_compile` created an ignored `__pycache__` under the new consolidated folder; it was removed before closeout evidence.

## Root causes
- The proposal's phrase "end-to-end" is easy to over-read as live L3. The runbook needed an explicit M2 evidence boundary to prevent evidence inflation.
- The existing benchmark already has live-adapter history, so M2 had to be unusually clear about not touching provider or sandbox paths.

## What was harder than expected
- Keeping the report useful while staying raw-free required treating payload refs as the central join key instead of carrying any prompt text.
- Verifying "no fake L3" needed both behavior tests and output artifact scans.

## Naming conventions established
- Consolidated bridge module: `benchmarks/agent-redteam/consolidated/bridge.py`.
- Smoke command: `benchmarks/agent-redteam/run-consolidated-smoke.sh`.
- M2 evidence levels: `L1_static` and `L2_mock_behavioural`; no `L3_live_behavioural`.
- M2 report keys: `l1_rows`, `l2_rows`, `l3_live_rows`, `joint_matrix`, `failure_bar_clear`.

## Test patterns that worked well
- Front-to-end smoke over a temp output directory made raw-free and report-shape assertions realistic.
- Unit-level `build_report` tests made off-diagonal failure cells cheap to exercise without fabricating live traces.
- A direct `--live` refusal test kept C-ENG-1 from regressing.

## Missing tests that should exist now
- M3 should add a reusable recursive raw-free artifact validator so full-corpus L1 outputs cannot smuggle raw text through nested fields.
- M3 should freeze the hard-benign false-positive bar before any full-corpus static measurements are generated.
- M4 should prove sandbox readiness with an executable refusal/acceptance test before any L3 row can be written.

## Rules for the next milestone
- Before M3 implementation, freeze the hard-benign false-positive bar and make it mechanically checked.
- Keep M3 static-only: every M3 row must remain L1 evidence and must not inherit action outcomes.
- Add the stronger raw-free validator in M3 and reuse it again in M5.
- Preserve the M2 consolidated smoke as a regression command after M3.

## Template improvements suggested
- Milestones that use "end-to-end" should name the exact highest evidence layer in their title or context.
- Runbook evidence rows should reserve a line for "forbidden evidence level absent" when overclaim risk is material.

## Issue filing
- No retro-derived GitHub issue filed in this closeout. The follow-ups are already represented as M3/M4/M5 runbook gates.
