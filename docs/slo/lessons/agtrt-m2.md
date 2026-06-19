# Lessons — agtrt M2

- **`max_turns` default 4 vs "≥5 traces" — reconciled by the turn model.** A turn carries multiple tool calls, so the default scenario (2 turns × 3 tools) yields 6 traces under the documented `max_turns=4`. The turn-cap BDD passes `--max-turns 1` and asserts `capped:true` + fewer traces. Avoided redefining the documented bound.
- **Docstring mentioning `subprocess`/`socket` trips a naive grep.** The prose "there is no subprocess, socket…" matches a bare `grep subprocess`. The real gate (and the test) matches `^(import|from)\s+(subprocess|socket|...)` — scope the no-dangerous-import scan to import statements, not substrings, or it false-positives on safety docs.
- **Seed was faithful again.** s4's `simulate()` + trace fields mapped directly; productionizing = freeze the trace schema, add `mock_a2a` (the runbook's "+ A2A"), add `UnknownToolError` (fail-closed), wrap in a bounded `runner.py` with a real CLI entrypoint + `result.json` (L2), and encode the invariants as tests.
- **Stacked PR discipline:** M2 branches off `slo/agtrt-m1` (M2 depends on M1's schema). PR base = `slo/agtrt-m1`; retarget to the canonical branch after M1 (#24) merges.
