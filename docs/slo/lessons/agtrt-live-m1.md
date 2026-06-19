# Lessons Learned - agtrt-live Milestone 1

## What changed

- Added `live_probe` to every measurement scenario so L3 Goose prompts are
  separate from L2 label placeholders.
- Made the validator reject placeholder-only live probes in measurement rows.
- Changed Goose scorecard projection to score expected live behavior:
  no-tool catch probes pass without a trace, while hard-benign utility probes
  need a contained shell trace.

## What we learned

- A trace-only L3 definition was too blunt: it made false positives visible for
  hard-benign rows, but it could not count a successful no-tool block as live
  evidence.
- The safe middle ground is explicit `expected_tool`: `none` for catch/near-miss
  rows, `shell` for benign utility rows.
- Keeping `views.agent_visible` as the L2 label surface avoids churn in the
  deterministic corpus while giving live runs real prompts.

## Rules for the next milestone

- Linux live rerun should start with `--limit=24`; do not spend the full 240
  until the bounded slice shows meaningful L3 counts.
- Report both `l3_rows` and `l3_trace_rows`; no-tool positives can be L3 without
  producing traces.
- Treat Mac as deterministic portability evidence unless a real bwrap-equivalent
  sandbox is available.
