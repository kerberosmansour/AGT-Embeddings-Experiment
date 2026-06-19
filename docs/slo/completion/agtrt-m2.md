# Completion Summary — agtrt M2 (Mock behavioural harness + trace schema)

**Outcome delivered (oc-2):** the assessing engineer runs the harness over a scenario and gets per-tool traces showing whether each unsafe action was *attempted but blocked* vs *executed* — with no real side effect.

## Evidence

| Step | Command | Result |
|---|---|---|
| oc-2 front-to-end | `python benchmarks/agent-redteam/harness/runner.py --out <dir>` | `{"traces":6,"blocked_attempts":5,"capped":false}`, exit 0; `<dir>/traces.jsonl` + `result.json` (L2_mock_behavioural) |
| Full tests | `python -m unittest discover -s benchmarks/agent-redteam -p "test_*.py"` | 25 passed (16 M1 + 9 M2) |
| No real side effect | source scan of `harness/*.py` | zero `import subprocess/socket/requests/urllib` (tm-agtrt-abuse-3) |
| Blocked attempt visible | unsafe traces | `attempted:true`, `executed:false`, `blocked_at` set (tm-agtrt-abuse-5) |
| Turn cap | `--max-turns 1` | `capped:true`, fewer traces — bounded, no unbounded loop |
| Static | `py_compile` + `git diff --check` | clean |

## What landed (M2 file allow-list)
- `harness/tool_trace.schema.json` — frozen trace contract (tool, attempted, executed, blocked_at, canary_leaked, audit_event_present required).
- `harness/mock_tools.py` — 5 dangerous-capability mocks (shell/email/memory/mcp_registry/audit) **+ mock_a2a**; `UnknownToolError` (fail-closed); structurally side-effect-free.
- `harness/runner.py` — bounded turn runner (`max_turns` default 4, `timeout_seconds` declared), emits JSONL traces + a `result.json` (L2), CLI front-to-end entrypoint.
- `tests/test_harness.py` — 9 tests: oc-2 front-to-end (subprocess), §5.5 invariants, tm-agtrt-abuse-3/5, trace-schema conformance, turn cap, unknown tool, benign dry-run.

## Invariants encoded (§5.5)
`executed==False ⇒ blocked_at!=None`; unsafe ⇒ `executed==False` AND `attempted==True`; `audit_event_present==True` for every trace; no `subprocess`/`socket`/network import (source scan); trace-schema conformance.

## Design note
A "turn" can carry multiple tool calls, so the documented `max_turns` default of 4 still yields ≥5 traces (default scenario = 2 turns × 3 tools = 5 unsafe-blocked + 1 benign). L2 mock only — never proves live-agent safety (that is M6).

## DoD: met (outcome-first — oc-2 passes front-to-end). Tracker M2 → `done` on merge.
