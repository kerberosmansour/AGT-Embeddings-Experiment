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
REQUIRED = {
    "id", "title", "trap_class", "attack_class", "target_layer",
    "delivery_surface", "views", "session_model", "environment_fixtures",
    "controls", "standards", "success_conditions", "evidence_expected",
}
OPTIONAL = {
    "payload_ref", "delivery_vector", "expected_containment", "detection",
    "action_outcome",
}
SPLITS = {"exemplar", "exemplar_bank", "validation", "test"}
DELIVERY_VECTORS = {
    "direct_prompt", "carrier_document", "browser_dom", "tool_result",
    "memory_record", "a2a_message", "approval_request", "reporting_artifact",
}
EXPECTED_CONTAINMENT = {
    "allow", "require_approval", "quarantine", "block", "contain",
    "not_applicable",
}
DETECTION_VERDICTS = {"flagged", "clean", "not_run"}
ACTION_OUTCOMES = {"attempted", "executed", "blocked", "contained"}
EVIDENCE_LEVELS = {
    "L0_declared", "L1_static", "L2_mock_behavioural", "L3_live_behavioural",
}
_CONTROL_RE = re.compile(r"AGT-AC-[0-9]{3}\Z")
_HASH_RE = re.compile(r"(sha256:)?[0-9a-f]{64}\Z")

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
    out += [s for s in data.get("success_conditions", []) if isinstance(s, str)]
    return [t for t in out if isinstance(t, str)]


def raw_free_violations(data):
    """Return text fields containing a raw-secret heuristic hit (tm-agtrt-abuse-1)."""
    return [t for t in _texts(data) if _SECRET_RE.search(t)]


def certification_terms(data):
    """Return text fields asserting a certification claim (tm-agtrt-abuse-4)."""
    return [t for t in _texts(data) if _CERT_RE.search(t)]


# --- Schema validation -------------------------------------------------------
def validate(data):
    """Return (ok: bool, message: str). Fail-closed on the frozen contract."""
    if not isinstance(data, dict):
        return False, "scenario must be a JSON object"
    keys = set(data)
    missing, extra = REQUIRED - keys, keys - (REQUIRED | OPTIONAL)
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
    if "payload_ref" in data:
        ok, message = validate_payload_ref(data["payload_ref"])
        if not ok:
            return False, message
    if data.get("delivery_vector") not in (None, *DELIVERY_VECTORS):
        return False, f"unknown delivery_vector {data['delivery_vector']!r}"
    if data.get("expected_containment") not in (None, *EXPECTED_CONTAINMENT):
        return False, f"unknown expected_containment {data['expected_containment']!r}"
    if "detection" in data:
        ok, message = validate_detection(data["detection"])
        if not ok:
            return False, message
    if data.get("action_outcome") not in (None, *ACTION_OUTCOMES):
        return False, f"unknown action_outcome {data['action_outcome']!r}"
    return True, "ok"


def validate_payload_ref(ref):
    """Validate metadata-only corpus payload references; never raw text."""
    if not isinstance(ref, dict):
        return False, "payload_ref must be an object"
    required = {"id", "family", "split", "corpus_manifest_hash"}
    keys = set(ref)
    missing, extra = required - keys, keys - required
    if missing or extra:
        return False, f"payload_ref field mismatch missing={sorted(missing)} extra={sorted(extra)}"
    for field in ("id", "family"):
        if not isinstance(ref[field], str) or len(ref[field]) < 3:
            return False, f"payload_ref.{field} must be a non-empty string"
    if ref["split"] not in SPLITS:
        return False, f"payload_ref.split must be one of {sorted(SPLITS)}"
    if not isinstance(ref["corpus_manifest_hash"], str) or not _HASH_RE.match(ref["corpus_manifest_hash"]):
        return False, "payload_ref.corpus_manifest_hash must be sha256:<64 hex>"
    return True, "ok"


def validate_detection(detection):
    """Validate detector metadata without accepting raw prompt/payload fields."""
    if not isinstance(detection, dict):
        return False, "detection must be an object"
    allowed = {"verdict", "detector_id", "config_hash", "evidence_level"}
    extra = set(detection) - allowed
    if extra:
        return False, f"detection extra fields {sorted(extra)}"
    verdict = detection.get("verdict")
    if verdict not in DETECTION_VERDICTS:
        return False, f"unknown detection.verdict {verdict!r}"
    level = detection.get("evidence_level")
    if level is not None and level != "L1_static":
        return False, "detection.evidence_level must be L1_static when present"
    config_hash = detection.get("config_hash")
    if config_hash is not None and not _HASH_RE.match(str(config_hash)):
        return False, "detection.config_hash must be sha256:<64 hex>"
    return True, "ok"


def validate_result(result):
    """Validate additive joint-result fields and reject L1-as-L3 overclaim."""
    if not isinstance(result, dict):
        return False, "result must be a JSON object"
    required = {"scenario_id", "status", "evidence_level", "trace"}
    allowed = required | {
        "trap_class", "controls", "payload_ref", "delivery_vector",
        "expected_containment", "detection", "action_outcome",
    }
    missing, extra = required - set(result), set(result) - allowed
    if missing or extra:
        return False, f"result field mismatch missing={sorted(missing)} extra={sorted(extra)}"
    if result["evidence_level"] not in EVIDENCE_LEVELS:
        return False, f"unknown evidence_level {result['evidence_level']!r}"
    if "payload_ref" in result:
        ok, message = validate_payload_ref(result["payload_ref"])
        if not ok:
            return False, message
    if "detection" in result:
        ok, message = validate_detection(result["detection"])
        if not ok:
            return False, message
    if result.get("action_outcome") not in (None, *ACTION_OUTCOMES):
        return False, f"unknown action_outcome {result['action_outcome']!r}"
    if result["evidence_level"] == "L3_live_behavioural":
        if result.get("action_outcome") not in {"attempted", "executed", "blocked", "contained"}:
            return False, "L3 result requires action_outcome"
        if not result.get("trace"):
            return False, "L3 result requires non-empty live trace"
        if result.get("detection", {}).get("evidence_level") == "L1_static":
            return False, "L1_static detection cannot masquerade as L3 live evidence"
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
    ok, message = validate(data)
    return ok, message, data


def main(argv):
    paths = argv[1:]
    if not paths:
        print("usage: validate_scenarios.py <scenario.json> [<scenario.json> ...]",
              file=sys.stderr)
        return 2
    trap_counts = {trap: 0 for trap in TRAP_CLASSES}
    failures = []
    for path in paths:
        ok, message, data = load_and_validate(path)
        if not ok:
            failures.append(f"{path}: {message}")
        else:
            trap_counts[data["trap_class"]] += 1
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    uncovered = sorted(trap for trap, count in trap_counts.items() if count == 0)
    if uncovered:
        print(f"uncovered trap classes: {uncovered}", file=sys.stderr)
        return 1
    print(json.dumps({"validated": len(paths), "trap_counts": trap_counts}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
