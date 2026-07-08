# Readiness Report - agtrtc Milestone 4

## Verdict
M4 is operator-blocked, not complete.

The local Mac checkout cannot produce L3 live evidence because the OS-enforced
sandbox prerequisite is absent and no provider key/budget is available. The
safe outcome is fail-closed refusal with zero L3 rows.

## Readiness Checks
| Check | Command | Result | Evidence |
|---|---|---|---|
| OS sandbox available | `command -v bwrap` | blocked | `bwrap` is absent on this host. |
| Provider/budget available | `printenv OPENAI_API_KEY` | blocked | `OPENAI_API_KEY` absent; no live spend approval in this session. |
| Live wrapper refuses safely | `bash benchmarks/agent-redteam/run-smoke.sh --live` | pass | Exits 1 after default smoke with `refusing --live: bwrap not found; refusing the live sandbox path`; no provider/model execution. |
| Regression coverage | `python3 -m unittest benchmarks/agent-redteam/tests/test_goose_adapter.py -v` | pass | 13 tests OK, 5 skipped for missing `bwrap`; includes no-model-override live wrapper regression. |
| Default path preserved | `bash benchmarks/agent-redteam/run-smoke.sh` | pass | Default mock/L2 smoke remains green. |

## Bug Fixed
`run-smoke.sh --live` previously failed on macOS Bash 3.2 with
`model_args[@]: unbound variable` before reaching the sandbox gate when no
`AGTRT_LIVE_MODEL` override was set. The wrapper now branches explicitly, so the
live path reaches the intended sandbox refusal.

Regression test:
`LiveSmokeWrapper.test_live_smoke_no_model_override_reaches_sandbox_refusal`.

## No L3 Claim
- No M4 L3 sample manifest was executed.
- No live provider/model call was made.
- No L3 rows were emitted locally.
- Prior external AgentBus evidence exists for a separate bounded Linux bwrap
  slice, but it does not satisfy this runbook's M4 sample-size/sample-manifest
  gate by itself.

## Required To Unblock
- Run on a Linux host with `bwrap`/network namespace support and proven egress,
  metadata, env, and host-filesystem isolation.
- Provide explicit provider/model budget and credentials out of band.
- Freeze the M4 sample manifest before the first live result.
- Run the bounded live batch and utility arm, then validate L3 rows and utility
  false-block metrics before marking M4 done.
