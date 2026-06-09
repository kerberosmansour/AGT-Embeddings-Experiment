#!/usr/bin/env python3
"""Validate Round-4 governance metadata eval evidence shape.

The validator enforces metadata-only action-outcome evidence and native Rust
PolicyDecision labels. It does not run governance scoring, recompute metrics,
inspect row text, or authorize promotion claims.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


NATIVE_DECISIONS = {"allow", "deny", "requires_approval", "rate_limited"}
EXPECTED_ACTIONS = {"allow", "log_only", "require_approval", "block", "quarantine"}
POLICY_ARMS = {
    "rules_only",
    "embedding_only",
    "policy_only_gate",
    "policy_plus_embedding",
    "rules_plus_embedding_no_gate",
}
OUTCOMES = {
    "allowed",
    "executed",
    "prevented",
    "routed_for_approval",
    "rate_limited",
    "audit_only",
}
RAW_FIELD_NAMES = {
    "text",
    "raw_text",
    "prompt",
    "content",
    "source_excerpt",
    "model_prompt",
    "raw_prompt",
    "raw_content",
    "tool_args",
    "tool_arguments",
    "raw_tool_args",
    "raw_tool_result",
    "policy_target",
    "raw_policy_target",
    "snapshot",
    "raw_snapshot",
    "action",
    "raw_action",
    "agent_id",
    "canary",
    "secret",
    "url",
    "email",
}
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")

MANIFEST_REQUIRED = {
    "schema_version",
    "round",
    "embedding_freeze_sha256",
    "agt_repo_commit",
    "agt_policy_file_sha256",
    "policy_profile_sha256",
    "stub_tool_sink_catalog_sha256",
    "expected_action_mapping_version",
    "raw_field_deny_list_version",
}

ROW_REQUIRED = {
    "id",
    "split",
    "label",
    "attack_class",
    "benign_subclass",
    "source_type",
    "trust_level",
    "expected_action",
    "contains_sensitive_sink",
    "requires_tool_call",
    "embedding_margin",
    "embedding_threshold_tau",
    "embedding_pred_attack",
    "policy_arm",
    "agt_policy_decision",
    "quarantine_intent",
    "policy_reason_code",
    "intervention_point",
    "stub_tool_kind",
    "stub_sink_kind",
    "unsafe_action_requested",
    "unsafe_action_executed",
    "outcome",
}


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: invalid JSON: {exc}") from exc


def load_jsonl(path: Path) -> list[tuple[str, dict[str, Any] | None, list[str]]]:
    records = []
    with path.open(encoding="utf-8-sig") as f:
        for lineno, line in enumerate(f, 1):
            stripped = line.strip()
            if not stripped:
                continue
            label = f"{path}:{lineno}"
            try:
                value = json.loads(stripped)
            except json.JSONDecodeError as exc:
                records.append((label, None, [f"invalid JSON: {exc}"]))
                continue
            if not isinstance(value, dict):
                records.append((label, None, ["top-level JSONL value must be an object"]))
                continue
            records.append((label, value, []))
    return records


def walk_keys(value: Any, path: str = "$") -> list[tuple[str, str]]:
    found = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            found.append((child_path, str(key)))
            found.extend(walk_keys(child, child_path))
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            found.extend(walk_keys(child, f"{path}[{idx}]"))
    return found


def raw_field_errors(value: Any, label: str) -> list[str]:
    errors = []
    for key_path, key in walk_keys(value):
        if key.strip().lower() in RAW_FIELD_NAMES:
            errors.append(f"{label}: raw field denied at {key_path}")
    return errors


def expect_str(record: dict[str, Any], key: str, errors: list[str]) -> None:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{key}: expected non-empty string")


def expect_bool(record: dict[str, Any], key: str, errors: list[str]) -> None:
    if not isinstance(record.get(key), bool):
        errors.append(f"{key}: expected boolean")


def expect_number(record: dict[str, Any], key: str, errors: list[str]) -> None:
    value = record.get(key)
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        errors.append(f"{key}: expected number")


def expect_sha(record: dict[str, Any], key: str, errors: list[str]) -> None:
    value = record.get(key)
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        errors.append(f"{key}: expected lowercase SHA-256 hex")


def validate_manifest(manifest: Any) -> list[str]:
    errors = []
    if not isinstance(manifest, dict):
        return ["manifest: top-level JSON value must be an object"]
    errors.extend(raw_field_errors(manifest, "manifest"))
    missing = sorted(MANIFEST_REQUIRED - set(manifest))
    if missing:
        errors.append(f"manifest: missing required fields {missing}")
    if manifest.get("schema_version") != 1:
        errors.append("manifest.schema_version: expected 1")
    if manifest.get("round") != "round4":
        errors.append("manifest.round: expected round4")
    for key in (
        "embedding_freeze_sha256",
        "agt_policy_file_sha256",
        "policy_profile_sha256",
        "stub_tool_sink_catalog_sha256",
    ):
        if key in manifest:
            expect_sha(manifest, key, errors)
    for key in (
        "agt_repo_commit",
        "expected_action_mapping_version",
        "raw_field_deny_list_version",
    ):
        if key in manifest:
            expect_str(manifest, key, errors)
    return errors


def validate_row(record: dict[str, Any] | None, pre_errors: list[str], split: str) -> list[str]:
    errors = list(pre_errors)
    if record is None:
        return errors
    errors.extend(raw_field_errors(record, "row"))
    missing = sorted(ROW_REQUIRED - set(record))
    if missing:
        errors.append(f"missing required fields {missing}")
    for key in (
        "id",
        "split",
        "label",
        "attack_class",
        "benign_subclass",
        "source_type",
        "trust_level",
        "expected_action",
        "policy_arm",
        "agt_policy_decision",
        "policy_reason_code",
        "intervention_point",
        "stub_tool_kind",
        "stub_sink_kind",
        "outcome",
    ):
        if key in record:
            expect_str(record, key, errors)
    if record.get("split") != split:
        errors.append(f"split: expected {split!r}")
    if record.get("expected_action") not in EXPECTED_ACTIONS:
        errors.append(f"expected_action: expected one of {sorted(EXPECTED_ACTIONS)}")
    if record.get("policy_arm") not in POLICY_ARMS:
        errors.append(f"policy_arm: expected one of {sorted(POLICY_ARMS)}")
    if record.get("agt_policy_decision") not in NATIVE_DECISIONS:
        errors.append(f"agt_policy_decision: expected one of {sorted(NATIVE_DECISIONS)}")
    if record.get("outcome") not in OUTCOMES:
        errors.append(f"outcome: expected one of {sorted(OUTCOMES)}")
    for key in (
        "contains_sensitive_sink",
        "requires_tool_call",
        "embedding_pred_attack",
        "quarantine_intent",
        "unsafe_action_requested",
        "unsafe_action_executed",
    ):
        if key in record:
            expect_bool(record, key, errors)
    for key in ("embedding_margin", "embedding_threshold_tau"):
        if key in record:
            expect_number(record, key, errors)

    if record.get("expected_action") == "quarantine":
        if record.get("quarantine_intent") is not True:
            errors.append("quarantine rows must set quarantine_intent=true")
    elif record.get("quarantine_intent") is True:
        errors.append("quarantine_intent=true is allowed only for expected_action=quarantine")

    decision = record.get("agt_policy_decision")
    outcome = record.get("outcome")
    if decision == "deny" and record.get("unsafe_action_executed") is False and outcome != "prevented":
        errors.append("deny without execution must report outcome='prevented'")
    if decision == "requires_approval" and record.get("unsafe_action_executed") is False and outcome != "routed_for_approval":
        errors.append("requires_approval without execution must report outcome='routed_for_approval'")
    if decision == "rate_limited" and outcome != "rate_limited":
        errors.append("rate_limited decisions must report outcome='rate_limited'")
    return errors


def flatten_keys(value: Any) -> set[str]:
    return {key.strip().lower() for _, key in walk_keys(value)}


def has_key(keys: set[str], *tokens: str) -> bool:
    return any(all(token in key for token in tokens) for key in keys)


def validate_metrics(metrics: Any) -> list[str]:
    errors = []
    if not isinstance(metrics, dict):
        return ["metrics: top-level JSON value must be an object"]
    errors.extend(raw_field_errors(metrics, "metrics"))
    keys = flatten_keys(metrics)
    required = [
        ("unsafe", "success", "rate"),
        ("attack", "prevention", "rate"),
        ("critical", "allow", "count"),
        ("leak", "allow", "count"),
        ("hard", "block", "fp"),
        ("approval", "load", "fp"),
        ("rate", "limit", "fp"),
        ("adjacent", "hard", "block"),
        ("adjacent", "review", "load"),
        ("false", "positives", "per", "1k", "hard"),
        ("false", "positives", "per", "1k", "approval"),
    ]
    for pattern in required:
        if not has_key(keys, *pattern):
            errors.append(f"metrics: missing key containing tokens {pattern}")
    if not any(key in keys for key in {"validation", "validation_metrics"}):
        errors.append("metrics: missing validation section")
    if not any(key in keys for key in {"test", "test_metrics"}):
        errors.append("metrics: missing test section")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--validation", type=Path, required=True)
    parser.add_argument("--test", type=Path, required=True)
    parser.add_argument("--metrics", type=Path, required=True)
    args = parser.parse_args()

    errors: list[str] = []
    try:
        errors.extend(validate_manifest(load_json(args.manifest)))
    except (OSError, ValueError) as exc:
        errors.append(str(exc))
    for split, path in (("validation", args.validation), ("test", args.test)):
        try:
            records = load_jsonl(path)
        except OSError as exc:
            errors.append(f"{path}: failed to read: {exc}")
            continue
        if not records:
            errors.append(f"{path}: expected at least one row")
        for label, record, pre_errors in records:
            errors.extend(f"{label}: {err}" for err in validate_row(record, pre_errors, split))
    try:
        errors.extend(validate_metrics(load_json(args.metrics)))
    except (OSError, ValueError) as exc:
        errors.append(str(exc))

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("round4_governance_eval_artifact: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
