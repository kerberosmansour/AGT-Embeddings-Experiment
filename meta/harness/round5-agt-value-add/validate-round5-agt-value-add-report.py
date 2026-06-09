#!/usr/bin/env python3
"""Validate a Round-5 AGT value-add report contract.

The gate is intentionally metadata-only. It checks that AGT-facing reports
compare rules, rules+governance, and rules+governance+embedding arms before
claiming value-add. It does not run AGT, score embeddings, inspect raw prompts,
or authorize production/security claims.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any


REQUIRED_ARMS = {
    "rules_only",
    "embedding_only",
    "policy_only_gate",
    "policy_plus_embedding",
    "rules_plus_embedding_no_gate",
}
REQUIRED_METRICS = {
    "attack_total",
    "attack_true_positive",
    "attack_false_negative",
    "benign_total",
    "benign_false_positive",
    "attack_recall",
    "benign_fp_rate",
    "fp_per_1k_benign",
    "adjacent_security_benign_total",
    "adjacent_security_false_positive",
    "adjacent_security_fp_rate",
    "unsafe_action_total",
    "unsafe_action_success",
    "unsafe_action_success_rate",
    "critical_allows",
    "hard_block_fp_rate",
    "approval_load_fp_rate",
    "leak_allows",
}
COUNT_METRICS = {
    "attack_total",
    "attack_true_positive",
    "attack_false_negative",
    "benign_total",
    "benign_false_positive",
    "adjacent_security_benign_total",
    "adjacent_security_false_positive",
    "unsafe_action_total",
    "unsafe_action_success",
    "critical_allows",
    "leak_allows",
}
RATE_METRICS = {
    "attack_recall",
    "benign_fp_rate",
    "adjacent_security_fp_rate",
    "unsafe_action_success_rate",
    "hard_block_fp_rate",
    "approval_load_fp_rate",
}
REQUIRED_DELTAS = {
    "policy_plus_embedding_vs_policy_only_gate": ("policy_plus_embedding", "policy_only_gate"),
    "policy_plus_embedding_vs_rules_only": ("policy_plus_embedding", "rules_only"),
    "rules_plus_embedding_no_gate_vs_rules_only": ("rules_plus_embedding_no_gate", "rules_only"),
}
DELTA_METRICS = {
    "attack_recall_delta": "attack_recall",
    "unsafe_action_success_rate_delta": "unsafe_action_success_rate",
    "critical_allows_delta": "critical_allows",
    "hard_block_fp_rate_delta": "hard_block_fp_rate",
    "approval_load_fp_rate_delta": "approval_load_fp_rate",
    "leak_allows_delta": "leak_allows",
}
OPERATING_POINTS = {"fp_zero", "youden_j"}
BASE_RATES = {"benign_to_attack_100", "benign_to_attack_1000"}
NO_CLAIMS = {
    "asi_aivss_coverage",
    "benchmark_coverage",
    "certification",
    "detector_promotion",
    "production_safety",
    "promptfoo_coverage",
}
RECOMMENDED_USES = {
    "worth_pursuing",
    "routing_signal_only",
    "review_queue_only",
    "not_default_block",
    "not_value_add",
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
EPS = 1e-6


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: invalid JSON: {exc}") from exc


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


def raw_field_errors(value: Any) -> list[str]:
    return [
        f"raw field denied at {key_path}"
        for key_path, key in walk_keys(value)
        if key.strip().lower() in RAW_FIELD_NAMES
    ]


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def expect_number(record: dict[str, Any], key: str, errors: list[str]) -> None:
    if not is_number(record.get(key)):
        errors.append(f"{key}: expected finite number")


def expect_rate(record: dict[str, Any], key: str, errors: list[str]) -> None:
    value = record.get(key)
    if not is_number(value) or not 0 <= value <= 1:
        errors.append(f"{key}: expected finite rate between 0 and 1")


def expect_count(record: dict[str, Any], key: str, errors: list[str]) -> None:
    value = record.get(key)
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        errors.append(f"{key}: expected non-negative integer")


def expect_sha(record: dict[str, Any], key: str, errors: list[str]) -> None:
    value = record.get(key)
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        errors.append(f"provenance.{key}: expected lowercase SHA-256 hex")


def approx_equal(actual: Any, expected: float) -> bool:
    return is_number(actual) and abs(float(actual) - expected) <= EPS


def ratio(numerator: int, denominator: int) -> float:
    return 0.0 if denominator == 0 else numerator / denominator


def validate_root(report: dict[str, Any], errors: list[str]) -> None:
    required = {
        "schema_version",
        "round",
        "status",
        "scope",
        "provenance",
        "arm_aliases",
        "arms",
        "embedding_operating_points",
        "deltas",
        "recommendation",
        "audit",
        "no_claims",
    }
    missing = sorted(required - set(report))
    if missing:
        errors.append(f"missing required fields: {missing}")
    if report.get("schema_version") != 1:
        errors.append("schema_version: expected 1")
    if report.get("round") != "round5":
        errors.append("round: expected round5")
    if report.get("status") not in {"schema_example_not_evidence", "draft_evidence", "audited_evidence"}:
        errors.append("status: expected schema_example_not_evidence, draft_evidence, or audited_evidence")


def validate_scope(scope: Any, errors: list[str]) -> None:
    if not isinstance(scope, dict):
        errors.append("scope: expected object")
        return
    if scope.get("raw_payloads_in_report") is not False:
        errors.append("scope.raw_payloads_in_report: expected false")
    if scope.get("metadata_only") is not True:
        errors.append("scope.metadata_only: expected true")


def validate_provenance(provenance: Any, errors: list[str]) -> None:
    if not isinstance(provenance, dict):
        errors.append("provenance: expected object")
        return
    for key in (
        "corpus_manifest_sha256",
        "embedding_freeze_sha256",
        "agt_policy_file_sha256",
        "policy_profile_sha256",
        "report_inputs_sha256",
    ):
        expect_sha(provenance, key, errors)
    commit = provenance.get("agt_repo_commit")
    if not isinstance(commit, str) or not commit.strip():
        errors.append("provenance.agt_repo_commit: expected non-empty string")


def validate_aliases(aliases: Any, errors: list[str]) -> None:
    if not isinstance(aliases, dict):
        errors.append("arm_aliases: expected object")
        return
    expected = {
        "policy_only_gate": "rules_plus_governance",
        "policy_plus_embedding": "rules_plus_governance_plus_embedding",
    }
    for key, value in expected.items():
        if aliases.get(key) != value:
            errors.append(f"arm_aliases.{key}: expected {value}")


def validate_metric_consistency(arm: str, metrics: dict[str, Any], errors: list[str]) -> None:
    attack_total = metrics.get("attack_total")
    attack_tp = metrics.get("attack_true_positive")
    attack_fn = metrics.get("attack_false_negative")
    benign_total = metrics.get("benign_total")
    benign_fp = metrics.get("benign_false_positive")
    adjacent_total = metrics.get("adjacent_security_benign_total")
    adjacent_fp = metrics.get("adjacent_security_false_positive")
    unsafe_total = metrics.get("unsafe_action_total")
    unsafe_success = metrics.get("unsafe_action_success")

    if isinstance(attack_total, int) and isinstance(attack_tp, int) and isinstance(attack_fn, int):
        if attack_tp + attack_fn != attack_total:
            errors.append(f"arms.{arm}.metrics: attack_true_positive + attack_false_negative must equal attack_total")
        if not approx_equal(metrics.get("attack_recall"), ratio(attack_tp, attack_total)):
            errors.append(f"arms.{arm}.metrics.attack_recall: inconsistent with counts")
    if isinstance(benign_total, int) and isinstance(benign_fp, int):
        if benign_fp > benign_total:
            errors.append(f"arms.{arm}.metrics.benign_false_positive: exceeds benign_total")
        if not approx_equal(metrics.get("benign_fp_rate"), ratio(benign_fp, benign_total)):
            errors.append(f"arms.{arm}.metrics.benign_fp_rate: inconsistent with counts")
        if not approx_equal(metrics.get("fp_per_1k_benign"), ratio(benign_fp, benign_total) * 1000):
            errors.append(f"arms.{arm}.metrics.fp_per_1k_benign: inconsistent with counts")
    if isinstance(adjacent_total, int) and isinstance(adjacent_fp, int):
        if adjacent_fp > adjacent_total:
            errors.append(f"arms.{arm}.metrics.adjacent_security_false_positive: exceeds adjacent_security_benign_total")
        if not approx_equal(metrics.get("adjacent_security_fp_rate"), ratio(adjacent_fp, adjacent_total)):
            errors.append(f"arms.{arm}.metrics.adjacent_security_fp_rate: inconsistent with counts")
    if isinstance(unsafe_total, int) and isinstance(unsafe_success, int):
        if unsafe_success > unsafe_total:
            errors.append(f"arms.{arm}.metrics.unsafe_action_success: exceeds unsafe_action_total")
        if not approx_equal(metrics.get("unsafe_action_success_rate"), ratio(unsafe_success, unsafe_total)):
            errors.append(f"arms.{arm}.metrics.unsafe_action_success_rate: inconsistent with counts")


def validate_arms(arms: Any, errors: list[str]) -> dict[str, dict[str, Any]]:
    if not isinstance(arms, dict):
        errors.append("arms: expected object")
        return {}
    actual = set(arms)
    if actual != REQUIRED_ARMS:
        errors.append(f"arms: expected exactly {sorted(REQUIRED_ARMS)}, got {sorted(actual)}")
        return {}
    metrics_by_arm: dict[str, dict[str, Any]] = {}
    for arm, body in arms.items():
        if not isinstance(body, dict):
            errors.append(f"arms.{arm}: expected object")
            continue
        description = body.get("description")
        if not isinstance(description, str) or not description.strip():
            errors.append(f"arms.{arm}.description: expected non-empty string")
        metrics = body.get("metrics")
        if not isinstance(metrics, dict):
            errors.append(f"arms.{arm}.metrics: expected object")
            continue
        missing = sorted(REQUIRED_METRICS - set(metrics))
        if missing:
            errors.append(f"arms.{arm}.metrics: missing {missing}")
        for key in COUNT_METRICS & set(metrics):
            expect_count(metrics, key, errors)
        for key in RATE_METRICS & set(metrics):
            expect_rate(metrics, key, errors)
        if "fp_per_1k_benign" in metrics:
            expect_number(metrics, "fp_per_1k_benign", errors)
        validate_metric_consistency(arm, metrics, errors)
        metrics_by_arm[arm] = metrics
    return metrics_by_arm


def validate_base_rate_precision(point: str, body: dict[str, Any], errors: list[str]) -> None:
    base = body.get("base_rate_precision")
    if not isinstance(base, dict):
        errors.append(f"embedding_operating_points.{point}.base_rate_precision: expected object")
        return
    missing = sorted(BASE_RATES - set(base))
    if missing:
        errors.append(f"embedding_operating_points.{point}.base_rate_precision: missing {missing}")
    for base_rate, interval in base.items():
        if not isinstance(interval, dict):
            errors.append(f"embedding_operating_points.{point}.base_rate_precision.{base_rate}: expected object")
            continue
        for key in ("precision", "wilson_low", "wilson_high"):
            expect_rate(interval, key, errors)
        low = interval.get("wilson_low")
        precision = interval.get("precision")
        high = interval.get("wilson_high")
        if is_number(low) and is_number(precision) and is_number(high) and not low <= precision <= high:
            errors.append(f"embedding_operating_points.{point}.base_rate_precision.{base_rate}: Wilson bounds must contain precision")


def validate_operating_points(points: Any, errors: list[str]) -> None:
    if not isinstance(points, dict):
        errors.append("embedding_operating_points: expected object")
        return
    missing = sorted(OPERATING_POINTS - set(points))
    if missing:
        errors.append(f"embedding_operating_points: missing {missing}")
    for point in OPERATING_POINTS:
        body = points.get(point)
        if not isinstance(body, dict):
            continue
        expect_number(body, "threshold", errors)
        if body.get("selection_split") != "validation":
            errors.append(f"embedding_operating_points.{point}.selection_split: expected validation")
        if body.get("test_split_frozen") is not True:
            errors.append(f"embedding_operating_points.{point}.test_split_frozen: expected true")
        if point == "youden_j":
            expect_rate(body, "youden_j", errors)
        validate_base_rate_precision(point, body, errors)


def validate_deltas(deltas: Any, metrics_by_arm: dict[str, dict[str, Any]], errors: list[str]) -> None:
    if not isinstance(deltas, dict):
        errors.append("deltas: expected object")
        return
    missing = sorted(set(REQUIRED_DELTAS) - set(deltas))
    if missing:
        errors.append(f"deltas: missing {missing}")
    for delta_name, (left_arm, right_arm) in REQUIRED_DELTAS.items():
        body = deltas.get(delta_name)
        if not isinstance(body, dict):
            continue
        for delta_key, metric_key in DELTA_METRICS.items():
            expect_number(body, delta_key, errors)
            left = metrics_by_arm.get(left_arm, {}).get(metric_key)
            right = metrics_by_arm.get(right_arm, {}).get(metric_key)
            if is_number(left) and is_number(right) and not approx_equal(body.get(delta_key), float(left) - float(right)):
                errors.append(f"deltas.{delta_name}.{delta_key}: inconsistent with arm metrics")


def validate_recommendation(recommendation: Any, errors: list[str]) -> None:
    if not isinstance(recommendation, dict):
        errors.append("recommendation: expected object")
        return
    if recommendation.get("net_value_add") not in RECOMMENDED_USES:
        errors.append(f"recommendation.net_value_add: expected one of {sorted(RECOMMENDED_USES)}")
    if recommendation.get("recommended_use") not in RECOMMENDED_USES:
        errors.append(f"recommendation.recommended_use: expected one of {sorted(RECOMMENDED_USES)}")
    if recommendation.get("default_block_threshold_recommended") is not False:
        errors.append("recommendation.default_block_threshold_recommended: expected false")
    if recommendation.get("human_review_required_before_claim") is not True:
        errors.append("recommendation.human_review_required_before_claim: expected true")


def validate_audit(audit: Any, errors: list[str]) -> None:
    if not isinstance(audit, dict):
        errors.append("audit: expected object")
        return
    if audit.get("linux_required_before_claim") is not True:
        errors.append("audit.linux_required_before_claim: expected true")
    tasks = audit.get("agentbus_tasks")
    if not isinstance(tasks, list):
        errors.append("audit.agentbus_tasks: expected array")
    elif not all(isinstance(task, str) for task in tasks):
        errors.append("audit.agentbus_tasks: expected string array")


def validate_no_claims(no_claims: Any, errors: list[str]) -> None:
    if not isinstance(no_claims, list) or not all(isinstance(item, str) for item in no_claims):
        errors.append("no_claims: expected string array")
        return
    missing = sorted(NO_CLAIMS - set(no_claims))
    if missing:
        errors.append(f"no_claims: missing {missing}")


def validate(report: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(report, dict):
        return ["top-level JSON value must be an object"]
    errors.extend(raw_field_errors(report))
    validate_root(report, errors)
    validate_scope(report.get("scope"), errors)
    validate_provenance(report.get("provenance"), errors)
    validate_aliases(report.get("arm_aliases"), errors)
    metrics_by_arm = validate_arms(report.get("arms"), errors)
    validate_operating_points(report.get("embedding_operating_points"), errors)
    validate_deltas(report.get("deltas"), metrics_by_arm, errors)
    validate_recommendation(report.get("recommendation"), errors)
    validate_audit(report.get("audit"), errors)
    validate_no_claims(report.get("no_claims"), errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    args = parser.parse_args()

    try:
        report = load_json(args.report)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    errors = validate(report)
    if errors:
        print(f"ERROR: {args.report}", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1
    print(f"OK: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

