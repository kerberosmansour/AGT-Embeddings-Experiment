#!/usr/bin/env python3
"""AGT Red Team scenario validator (M1) — stdlib-only, fail-closed.

Front-to-end (oc-1): the assessing engineer runs

    python validate_scenarios.py <scenario.json> [<scenario.json> ...]

and gets, on success, a JSON coverage summary on stdout and exit 0; on any
failure, a named reason on stderr and a non-zero exit. The field set is the
FROZEN public contract (see scenario.schema.json); it is enforced here in
stdlib (no jsonschema dependency) so the benchmark stays dependency-free.

Exit codes: 0 ok | 1 validation/coverage failure | 2 usage (no paths).
"""
import json
import re
import sys
from pathlib import Path

# --- Frozen contract (mirrors scenario.schema.json) -------------------------
TRAP_CLASSES = {
    "Content Injection", "Semantic Manipulation", "Cognitive State",
    "Behavioural Control", "Systemic", "Human-in-the-Loop",
}
TARGET_LAYERS = {
    "input", "retrieval", "memory", "tool", "browser",
    "a2a", "human_approval", "reporting",
}
OPENCRE_RELATIONS = {"exact", "broad", "narrow", "related", "candidate"}
SCENARIO_KINDS = {"canonical_positive", "evasion_positive", "hard_benign", "near_miss"}
EVASION_TECHNIQUES = {
    "none", "hidden_content", "format_smuggling", "render_parse_divergence",
    "encoding_indirection", "authority_spoofing", "roleplay_legitimacy",
    "goal_reframing", "ambiguous_scope", "state_carryover", "memory_shadowing",
    "preference_poisoning", "cross_session_echo", "approval_fatigue",
    "tool_schema_confusion", "irreversible_pressure", "least_privilege_blur",
    "cross_agent_relay", "mcp_registry_misdirection", "package_name_confusion",
    "delegation_loop", "fake_approval", "social_proof_pressure", "time_pressure",
    "visible_safe_hidden_unsafe",
}
EXPECTED_BEHAVIOURS = {"detect_or_block", "allow_or_clarify"}
LIVE_EXPECTED_TOOLS = {"shell", "none"}
MEASUREMENT_SUITE = "agt_redteam_measurement_v2"
REQUIRED = {
    "id", "title", "trap_class", "attack_class", "target_layer",
    "delivery_surface", "views", "session_model", "environment_fixtures",
    "controls", "standards", "success_conditions", "evidence_expected",
}
OPTIONAL = {
    "measurement_suite", "scenario_kind", "evasion_technique",
    "expected_control_behavior", "live_probe",
}
MEASUREMENT_REQUIRED = OPTIONAL
_CONTROL_RE = re.compile(r"AGT-AC-[0-9]{3}\Z")
_PLACEHOLDER_RE = re.compile(r"MEASUREMENT_[A-Z_]+_PLACEHOLDER")

# --- Raw-free / no-overclaim heuristics (concept at M1; full gate is M5) -----
_SECRET_RE = re.compile(
    r"AKIA[0-9A-Z]{16}"                       # AWS access key id
    r"|-----BEGIN [A-Z ]*PRIVATE KEY-----"    # PEM private key
    r"|sk-[A-Za-z0-9]{20,}"                   # OpenAI-style secret
    r"|xox[baprs]-[0-9A-Za-z-]{10,}"          # Slack token
)
_CERT_RE = re.compile(
    r"\b(certified|certification|official OWASP|official OpenCRE|OWASP-certified)\b",
    re.IGNORECASE,
)


def _texts(data):
    """Human-readable text fields a payload/term could hide in."""
    out = [data.get("title", "")]
    views = data.get("views", {})
    if isinstance(views, dict):
        out += [views.get("human_visible", ""), views.get("agent_visible", "")]
    live_probe = data.get("live_probe", {})
    if isinstance(live_probe, dict):
        out.append(live_probe.get("agent_visible", ""))
    out += [s for s in data.get("success_conditions", []) if isinstance(s, str)]
    return [t for t in out if isinstance(t, str)]


def raw_free_violations(data):
    """Return text fields containing a raw-secret heuristic hit (tm-agtrt-abuse-1)."""
    return [t for t in _texts(data) if _SECRET_RE.search(t)]


def certification_terms(data):
    """Return text fields asserting a certification claim (tm-agtrt-abuse-4)."""
    return [t for t in _texts(data) if _CERT_RE.search(t)]


# --- Schema validation -------------------------------------------------------
def _validate_measurement(data, require_measurement):
    """Validate optional v2 measurement labels when present or required."""
    present = OPTIONAL & set(data)
    if require_measurement or present:
        missing = MEASUREMENT_REQUIRED - set(data)
        if missing:
            return False, f"measurement labels missing={sorted(missing)}"
    if not present and not require_measurement:
        return True, "ok"
    suite = data.get("measurement_suite")
    kind = data.get("scenario_kind")
    evasion = data.get("evasion_technique")
    expected = data.get("expected_control_behavior")
    live_probe = data.get("live_probe")
    if suite != MEASUREMENT_SUITE:
        return False, f"unknown measurement_suite {suite!r}"
    if kind not in SCENARIO_KINDS:
        return False, f"unknown scenario_kind {kind!r}"
    if evasion not in EVASION_TECHNIQUES:
        return False, f"unknown evasion_technique {evasion!r}"
    if expected not in EXPECTED_BEHAVIOURS:
        return False, f"unknown expected_control_behavior {expected!r}"
    ok, message = _validate_live_probe(kind, live_probe)
    if not ok:
        return ok, message
    if kind == "evasion_positive":
        if evasion == "none":
            return False, "evasion_positive requires non-none evasion_technique"
        if expected != "detect_or_block":
            return False, "evasion_positive requires detect_or_block"
    elif kind == "canonical_positive":
        if evasion != "none":
            return False, "canonical_positive requires evasion_technique none"
        if expected != "detect_or_block":
            return False, "canonical_positive requires detect_or_block"
    else:
        if evasion != "none":
            return False, f"{kind} requires evasion_technique none"
        if expected != "allow_or_clarify":
            return False, f"{kind} requires allow_or_clarify"
    return True, "ok"


def _validate_live_probe(kind, live_probe):
    if not isinstance(live_probe, dict):
        return False, "live_probe must be an object"
    if set(live_probe) != {"agent_visible", "expected_tool"}:
        return False, "live_probe must be exactly {agent_visible, expected_tool}"
    text = live_probe.get("agent_visible")
    expected_tool = live_probe.get("expected_tool")
    if not isinstance(text, str) or len(text.strip()) < 20:
        return False, "live_probe.agent_visible must be a non-empty string"
    if _PLACEHOLDER_RE.search(text):
        return False, "live_probe.agent_visible must not be a measurement placeholder"
    if expected_tool not in LIVE_EXPECTED_TOOLS:
        return False, f"unknown live_probe.expected_tool {expected_tool!r}"
    expected_by_kind = "shell" if kind == "hard_benign" else "none"
    if expected_tool != expected_by_kind:
        return False, f"{kind} requires live_probe.expected_tool {expected_by_kind}"
    return True, "ok"


def validate(data, require_measurement=False):
    """Return (ok: bool, message: str). Fail-closed on the frozen contract."""
    if not isinstance(data, dict):
        return False, "scenario must be a JSON object"
    keys = set(data)
    missing, extra = REQUIRED - keys, keys - REQUIRED - OPTIONAL
    if missing or extra:
        return False, f"field mismatch missing={sorted(missing)} extra={sorted(extra)}"
    if data["trap_class"] not in TRAP_CLASSES:
        return False, f"unknown trap_class {data['trap_class']!r}"
    if data["target_layer"] not in TARGET_LAYERS:
        return False, f"unknown target_layer {data['target_layer']!r}"
    controls = data["controls"]
    if not controls or not all(isinstance(c, str) and _CONTROL_RE.match(c) for c in controls):
        return False, "controls must be >=1 AGT-AC-NNN id"
    if not data["success_conditions"]:
        return False, "missing success_conditions"
    if set(data.get("views", {})) != {"human_visible", "agent_visible"}:
        return False, "views must be exactly {human_visible, agent_visible}"
    if not {"turns", "stateful", "agents"} <= set(data.get("session_model", {})):
        return False, "session_model incomplete (needs turns, stateful, agents)"
    standards = data.get("standards", {})
    if not isinstance(standards, dict):
        return False, "standards must be an object"
    if any(r not in OPENCRE_RELATIONS for r in standards.get("opencre_relations", [])):
        return False, "unknown opencre relation"
    ok, message = _validate_measurement(data, require_measurement)
    if not ok:
        return ok, message
    return True, "ok"


def load_and_validate(path):
    """Return (ok, message, data). Structured errors, never a raw traceback."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return False, "file not found", None
    except json.JSONDecodeError as exc:
        return False, f"invalid JSON ({exc.msg} at line {exc.lineno})", None
    except OSError as exc:
        return False, f"unreadable ({exc.strerror})", None
    require_measurement = "measurement" in Path(path).parts
    ok, message = validate(data, require_measurement=require_measurement)
    return ok, message, data


def main(argv):
    paths = argv[1:]
    if not paths:
        print("usage: validate_scenarios.py <scenario.json> [<scenario.json> ...]",
              file=sys.stderr)
        return 2
    trap_counts = {trap: 0 for trap in TRAP_CLASSES}
    scenario_kind_counts = {kind: 0 for kind in SCENARIO_KINDS}
    failures = []
    for path in paths:
        ok, message, data = load_and_validate(path)
        if not ok:
            failures.append(f"{path}: {message}")
        else:
            trap_counts[data["trap_class"]] += 1
            if data.get("scenario_kind") in scenario_kind_counts:
                scenario_kind_counts[data["scenario_kind"]] += 1
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    uncovered = sorted(trap for trap, count in trap_counts.items() if count == 0)
    if uncovered:
        print(f"uncovered trap classes: {uncovered}", file=sys.stderr)
        return 1
    out = {"validated": len(paths), "trap_counts": trap_counts}
    if any(scenario_kind_counts.values()):
        out["scenario_kind_counts"] = scenario_kind_counts
        out["measurement_suite"] = MEASUREMENT_SUITE
    print(json.dumps(out, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
