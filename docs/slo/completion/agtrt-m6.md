# Completion Summary — agtrt M6 (Live Goose adapter — sandboxed L3)

**Outcome (oc-6):** the engineer can assess a REAL agent and get honest `L3_live` evidence — SAFELY, in an OS-enforced sandbox. **Built + security-proven; the keyed live run is gated on out-of-band credentials + the W-CEO-2 founder checkpoint (automate-to-seam + flag the gate).**

## Security-critical part — DONE + PROVEN (no keys needed)

| Control (CWE-918 / sandbox escape) | Proof | Result |
|---|---|---|
| OS-layer egress default-deny | real subprocess in `bwrap --unshare-all` → connect | **blocked** (internet 1.1.1.1 AND metadata 169.254.169.254) |
| Scrubbed env (no host creds) | `--clearenv`; secret in orchestrator env not visible inside | **not visible** |
| No host filesystem | read-only `/usr` + fresh `tmpfs /`; host `/home` | **not mounted** |
| Fail-closed | `sandbox.assert_secure()` before any live run | refuses if any control fails; no in-process fallback |
| Live skips without creds | no `.agtrt-goose.env`/env | `status:skipped`, never L3, exit 0 |
| Default path isolation | grep | no `import anthropic`/`goose` in schema/harness/reporters/hygiene |

8 M6 tests green; full suite **67 passed**.

## What landed (M6 file allow-list)
- `adapters/goose/sandbox.py` — bwrap hermetic jail (no-net + clearenv + ro-/usr + tmpfs); `assert_secure()` self-test; fail-closed `SandboxUnavailable`.
- `adapters/goose/adapter.py` — orchestrator: TRUSTED process calls a CHEAP model (`claude-3-5-haiku-latest`, `max_tokens=512`, `max_turns=2`) and reads the tool-call decision (L3 signal); any tool runs INSIDE the sandbox (contained). Lazy provider import; skips without creds.
- `run-smoke.sh` — opt-in `--live` step (default mock/L2 unchanged everywhere).
- `tests/test_goose_adapter.py` — 8 tests (OS controls, real-subprocess egress, host-cred invisibility, live-skip, CLI-refusal, cheap-model default, default-path isolation, L3-only-from-live).

## Architecture (why it's safe)
Keys are used ONLY by the trusted orchestrator for the model call (outside the sandbox). The harness NEVER executes the agent's real command — it runs a benign placeholder inside the no-network/no-fs/scrubbed sandbox to confirm the jail contains it. **Honest L3 semantics (M6-SEC-1, win review):** a tool the live agent attempted is recorded `attempted=True, executed=False, blocked_at="sandbox_contained"` — it is contained at the sandbox boundary, never executed for real, so the trace never overclaims that the action ran. The benchmark's L3 value is the *attempted* signal (did the live agent take the bait?) plus proof that containment held.

## Remaining (operator gate — NOT a code gap)
The actual L3 trace needs **only** the Anthropic key provisioned to the linux box **out-of-band** (`.agtrt-goose.env`, gitignored — never on the bus) + the **W-CEO-2** founder checkpoint. The model call uses **stdlib `urllib`** (no SDK to install — pip is unavailable on this box's Python 3.14, so this is also more robust). Cheap model + caps keep cost tiny. Once the key lands: `bash run-smoke.sh --live` emits real L3 traces.

## Status: `blocked_by_operator` — build + sandbox proof complete; keyed live run awaits creds + checkpoint.
