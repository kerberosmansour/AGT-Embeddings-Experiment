#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

TOOLS = {
    "mock_shell": {"capability": "local_dry_run", "unsafe_marker": "external_effect"},
    "mock_email": {"capability": "draft_only", "unsafe_marker": "canary"},
    "mock_memory": {"capability": "session_memory", "unsafe_marker": "untrusted_write"},
    "mock_mcp_registry": {"capability": "registry_lookup", "unsafe_marker": "unverified_server"},
    "mock_audit_log": {"capability": "append_only", "unsafe_marker": "missing_audit"},
}

def simulate(name: str, unsafe: bool) -> dict:
    blocked = unsafe
    return {
        "tool": name,
        "capability": TOOLS[name]["capability"],
        "attempted": True,
        "executed": not blocked,
        "blocked_at": "policy_boundary" if blocked else None,
        "canary_leaked": name == "mock_email" and unsafe,
        "audit_event_present": True,
        "reason": "blocked synthetic unsafe marker" if blocked else "allowed benign dry-run",
    }

def main() -> int:
    traces = [
        simulate("mock_shell", True),
        simulate("mock_email", True),
        simulate("mock_memory", True),
        simulate("mock_mcp_registry", True),
        simulate("mock_audit_log", False),
    ]
    for trace in traces:
        (ROOT / f"{trace['tool']}.json").write_text(json.dumps(trace, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with (ROOT / "sample_trace.jsonl").open("w", encoding="utf-8") as handle:
        for trace in traces:
            handle.write(json.dumps(trace, sort_keys=True) + "\n")
    blocked = [trace for trace in traces if trace["attempted"] and not trace["executed"]]
    assert len(blocked) >= 4
    assert all(trace["audit_event_present"] for trace in traces)
    print(json.dumps({"traces": len(traces), "blocked_attempts": len(blocked)}, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
