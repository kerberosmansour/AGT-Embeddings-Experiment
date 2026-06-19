# Completion Summary — agtrt M6 (Live Goose adapter — sandboxed L3)

**Outcome (oc-6):** the engineer can assess a REAL agent and get honest `L3_live` evidence — safely, in an OS-enforced sandbox. **Done:** on Linux/Omarchy, `bash benchmarks/agent-redteam/run-smoke.sh --live` emitted 1 live trace and an M4 scorecard row after the bwrap controls proved egress/env/fs containment.

## Security-critical part — DONE + PROVEN (no keys needed)

| Control (CWE-918 / sandbox escape) | Proof | Result |
|---|---|---|
| OS-layer egress default-deny | real subprocess in `bwrap --unshare-all` → connect | **blocked** (internet 1.1.1.1 AND metadata 169.254.169.254) |
| Scrubbed env (no host creds) | `--clearenv`; secret in orchestrator env not visible inside | **not visible** |
| No host filesystem | read-only `/usr` + fresh `tmpfs /`; host `/home` | **not mounted** |
| Fail-closed | `sandbox.assert_secure()` before any live run | refuses if any control fails; no in-process fallback |
| Live skips without creds | no `.agtrt-goose.env`/env | `status:skipped`, never L3, exit 0 |
| Default path isolation | grep | no `import anthropic`/`goose` in schema/harness/reporters/hygiene |

Linux M6 targeted suite: **12 tests green** (1 skip because credentials were provisioned and the no-creds assertion is no longer applicable). The bwrap tests ran on Linux and proved internet egress, metadata egress, env scrub, and host-home isolation.

## What landed (M6 file allow-list)
- `adapters/goose/sandbox.py` — bwrap hermetic jail (no-net + clearenv + ro-/usr + tmpfs); `assert_secure()` self-test; fail-closed `SandboxUnavailable`.
- `adapters/goose/adapter.py` — orchestrator: TRUSTED process calls a CHEAP model (`claude-haiku-4-5`, `max_tokens=512`, `max_turns=2`) and reads the tool-call decision (L3 signal); any tool runs INSIDE the sandbox (contained). Lazy provider import; skips without creds; `--require-trace` fails closed on vacuous keyed live runs.
- `run-smoke.sh` — opt-in `--live` step (default mock/L2 unchanged everywhere). The live smoke generates a non-secret oc-6 probe unless `AGTRT_LIVE_SCENARIO` is supplied, then feeds `live_results.jsonl` into the M4 scorecard reporter.
- `tests/test_goose_adapter.py` — 12 tests (OS controls, real-subprocess egress, host-cred invisibility, live-skip, CLI-refusal, cheap-model default, M4 scorecard projection, vacuous-trace failure, default-path isolation, L3-only-from-live).

## Architecture (why it's safe)
Keys are used ONLY by the trusted orchestrator for the model call (outside the sandbox). The harness NEVER executes the agent's real command — it runs a benign placeholder inside the no-network/no-fs/scrubbed sandbox to confirm the jail contains it. **Honest L3 semantics (M6-SEC-1, win review):** a tool the live agent attempted is recorded `attempted=True, executed=False, blocked_at="sandbox_contained"` — it is contained at the sandbox boundary, never executed for real, so the trace never overclaims that the action ran. The benchmark's L3 value is the *attempted* signal (did the live agent take the bait?) plus proof that containment held.

## Evidence
- Mac merge branch: `python3 -m unittest discover benchmarks/agent-redteam/tests -v` → 72 tests OK (5 bwrap skips); default `run-smoke.sh`, `py_compile`, `bash -n`, and `git diff --check` clean.
- Linux/Omarchy M6 branch: `python3 -m unittest discover benchmarks/agent-redteam/tests -v` → 71 tests OK (1 no-creds skip because live creds are active); `py_compile`, `bash -n`, and `git diff --check` clean.
- `python3 -m unittest benchmarks/agent-redteam/tests/test_goose_adapter.py -v` on Linux/Omarchy: 12 tests, OK, 1 skip (creds active).
- `bash benchmarks/agent-redteam/run-smoke.sh --live` on Linux/Omarchy: validates 24 scenarios, mock harness green, raw-free hygiene green, live adapter `{"evidence_level":"L3_live","status":"completed","traces":1}`, live scorecard `{"certification_claim":false,"controls":3,"failures":0}`.
- SSH path used the documented `sunlit-agent-ops` route (`kerberosmansour@<Omarchy IP>` with `~/.ssh/sunlit_winvm`). Credentials stayed in the gitignored `.agtrt-goose.env` and were never printed, committed, or sent over AgentBus.

## Status: `done` — build, sandbox proof, keyed live oc-6 trace, and live scorecard evidence complete.
