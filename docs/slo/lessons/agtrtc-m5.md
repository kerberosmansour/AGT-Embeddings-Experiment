# Lessons Learned - agtrtc Milestone 5

## What changed
- Added `benchmarks/agent-redteam/reporters/release_gate.py` to join validated L1 static evidence with M4 live/utility evidence.
- Added `benchmarks/agent-redteam/run-release-gate.sh` as the one-command M5 wrapper.
- Added focused M5 BDD tests for hash tamper, static-as-live evidence inflation, utility visibility, no-certification wording, raw-free outputs, and HTML/Markdown escaping.
- Produced a real Linux M5 release evidence pack from fresh L1 output plus the completed M4 live artifacts.

## Results vs thesis
- The M5 thesis held: the benchmark can now publish a joint matrix and release manifest without raw payloads or certification language.
- The failure bar cleared on real Linux evidence: 54,034 L1 rows joined with 250 M4 L3 rows, zero utility false blocks, zero detected-executed rows, and release validation `failure_bar_clear=true`.
- The report keeps the seven high-miss families visible as backlog instead of hiding them behind an aggregate score.

## Outcome vs promise
- `oc-agtrtc-7` materialised: an engineer can inspect detector misses, action outcomes, utility false blocks, and residual backlog from the report without reading raw payloads.
- `oc-agtrtc-8` materialised: malicious display text is escaped/literal in HTML and Markdown, and the no-certification banner appears first.
- `cuj-agtrtc-5` materialised: release manifest -> validate hashes -> render report -> inspect joint matrix -> inspect backlog -> raw-free scan.

## Design decisions and why
- Kept JSON, Markdown, and HTML generation in one stdlib-only reporter so the failure bar is tested at the same boundary users run.
- Stored source artifact absolute paths and hashes in the release manifest so tampering after report generation fails closed.
- Kept L1 and L3 as separate evidence levels in the report; no aggregate score collapses static detection into live containment.
- Rendered HTML as optional but generated it by default because M5's injection scenario explicitly covers browser-viewable output.

## Mistakes made
- The Mac host had no usable SSH identity for the Linux VM, so direct `scp` of M4 artifacts failed.
- I accidentally sent a stale AgentBus update that marked the Linux read-only peer task `superseded` after Linux had already completed it.

## Root causes
- Linux VM access depends on Parallels Tools in this environment, not a stable SSH key in `~/.ssh`.
- AgentBus task status can change between polling and follow-up updates; stale status writes need one more read before mutating peer-owned tasks.

## What was harder than expected
- The release JSON hash changes when source paths/timestamps differ, so Markdown/HTML hashes were more stable than manifest/report/validation hashes across independent Linux runs.
- Keeping the report useful without raw rows required carefully choosing aggregate fields: per-family, per-stratum, joint matrix cells, utility metrics, and backlog.

## Naming conventions established
- `release_gate.py` for the M5 reporter/validator.
- `run-release-gate.sh` for the wrapper.
- `joint_scorecard_report.{json,md,html}`, `release_manifest.json`, `release_validation_report.json`, and `SHA256SUMS` for generated release outputs.

## Test patterns that worked well
- BDD fixtures synthesize small L1/M4 bundles but drive the same CLI path as the real release.
- Tamper-after-manifest tests prove hashes are live checks, not static fields.
- Malicious display-string tests cover both Markdown and HTML renderers.

## Missing tests that should exist now
- A future release-pack test should compare two generated reports while ignoring timestamp/source-path fields, to make deterministic semantic diffs easier.
- A future AgentBus coordination test or checklist should prevent stale status mutation on peer-owned tasks.

## Rules for the next milestone
- Treat generated release artifacts as evidence references; do not commit live/generated rows unless a later runbook explicitly changes the artifact policy.
- Keep every public summary non-certifying and separate synthetic research evidence from production safety evidence.
- Use `prlctl exec Omarchy` for Linux VM file/proof access when SSH has no loaded identity.

## Template improvements suggested
- Add an AgentBus closeout reminder: re-read a peer task immediately before changing its status.

## Issue filing
- No GitHub issues filed. The AgentBus status correction was requested from `linux-agent` on the bus, and the main M5 task carries the authoritative evidence.
