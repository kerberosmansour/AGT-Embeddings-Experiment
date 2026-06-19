#!/usr/bin/env python3
import json
import sys
from pathlib import Path

TRAP_CLASSES = {
    "Content Injection",
    "Semantic Manipulation",
    "Cognitive State",
    "Behavioural Control",
    "Systemic",
    "Human-in-the-Loop",
}

REQUIRED = {
    "id", "title", "trap_class", "attack_class", "target_layer",
    "delivery_surface", "views", "session_model", "environment_fixtures",
    "controls", "standards", "success_conditions", "evidence_expected",
}

def validate(path: Path) -> tuple[bool, str, dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    missing = REQUIRED - set(data)
    extra = set(data) - REQUIRED
    if missing or extra:
        return False, f"field mismatch missing={sorted(missing)} extra={sorted(extra)}", data
    if data["trap_class"] not in TRAP_CLASSES:
        return False, "unknown trap_class", data
    if not data["controls"] or not all(c.startswith("AGT-AC-") for c in data["controls"]):
        return False, "missing AGT-AC controls", data
    if not data["success_conditions"]:
        return False, "missing success_conditions", data
    views = data["views"]
    if set(views) != {"human_visible", "agent_visible"}:
        return False, "views must include human_visible and agent_visible only", data
    session = data["session_model"]
    if not {"turns", "stateful", "agents"} <= set(session):
        return False, "session_model incomplete", data
    return True, "ok", data

def main() -> int:
    paths = [Path(p) for p in sys.argv[1:]]
    if not paths:
        print("usage: validate_scenarios.py examples/*.json", file=sys.stderr)
        return 2
    trap_counts = {trap: 0 for trap in TRAP_CLASSES}
    failures = []
    for path in paths:
        ok, message, data = validate(path)
        if not ok:
            failures.append(f"{path}: {message}")
        else:
            trap_counts[data["trap_class"]] += 1
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    uncovered = [trap for trap, count in trap_counts.items() if count == 0]
    if uncovered:
        print(f"uncovered trap classes: {uncovered}", file=sys.stderr)
        return 1
    print(json.dumps({"validated": len(paths), "trap_counts": trap_counts}, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
