#!/usr/bin/env python3
"""Validate Round-4 embedding/kNN sweep artifact metadata.

This validator is intentionally narrow. It enforces the reviewed artifact
contract for freeze/provenance, metadata-only per-row outputs, and required
metric categories. It does not compute embeddings, recompute metrics, read the
source corpus, select thresholds, or authorize any promotion claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from typing import Any


EXPECTED_CORPUS_SHA256 = (
    "33a02ac2b22e68970b3b808c5ba95bc119dc87dd93ae6dbc90546c074a5980ed"
)

FREEZE_REQUIRED_FIELDS = {
    "model_id",
    "model_version",
    "model_sha256",
    "runtime",
    "embedding_dimension",
    "normalization",
    "k",
    "positive_bank_filter",
    "negative_bank_filter",
    "margin_formula",
    "threshold_tau",
    "abstain_band",
    "selected_on",
    "corpus_sha256",
}

ROW_REQUIRED_FIELDS = {
    "id",
    "split",
    "label",
    "attack_class",
    "benign_subclass",
    "bypass_class",
    "source_type",
    "trust_level",
    "expected_action",
    "contains_sensitive_sink",
    "requires_tool_call",
    "family_id",
    "group_id",
    "s_pos",
    "s_neg",
    "margin",
    "threshold_tau",
    "pred_attack",
    "top_positive_neighbor_ids",
    "top_negative_neighbor_ids",
}

ROW_OPTIONAL_FIELDS = {
    "embedding_model_id",
    "embedding_model_version",
    "embedding_runtime",
    "margin_bucket",
    "abstained",
    "pred_attack_before_abstain",
    "nearest_positive_score",
    "nearest_negative_score",
}

ROW_ALLOWED_FIELDS = ROW_REQUIRED_FIELDS | ROW_OPTIONAL_FIELDS

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
}

SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
LABELS = {"attack", "benign"}


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: invalid JSON: {exc}") from exc


def load_jsonl(path: Path) -> list[tuple[str, dict[str, Any] | None, list[str]]]:
    records: list[tuple[str, dict[str, Any] | None, list[str]]] = []
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
    found: list[tuple[str, str]] = []
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
        normalized = key.strip().lower()
        if normalized in RAW_FIELD_NAMES:
            errors.append(f"{label}: raw field denied at {key_path}")
    return errors


def expect_string(record: dict[str, Any], key: str, errors: list[str]) -> None:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{key}: expected non-empty string")


def expect_number(record: dict[str, Any], key: str, errors: list[str]) -> None:
    value = record.get(key)
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
        errors.append(f"{key}: expected finite number")


def expect_bool(record: dict[str, Any], key: str, errors: list[str]) -> None:
    if not isinstance(record.get(key), bool):
        errors.append(f"{key}: expected boolean")


def expect_string_array(record: dict[str, Any], key: str, errors: list[str]) -> None:
    value = record.get(key)
    if not isinstance(value, list) or not value:
        errors.append(f"{key}: expected non-empty string array")
        return
    if not all(isinstance(item, str) and item.strip() for item in value):
        errors.append(f"{key}: expected only non-empty row ID strings")


def validate_freeze(freeze: Any, expected_corpus_sha256: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(freeze, dict):
        return ["freeze: top-level JSON value must be an object"]

    errors.extend(raw_field_errors(freeze, "freeze"))
    missing = sorted(FREEZE_REQUIRED_FIELDS - set(freeze))
    if missing:
        errors.append(f"freeze: missing required fields {missing}")

    for key in (
        "model_id",
        "model_version",
        "runtime",
        "normalization",
        "positive_bank_filter",
        "negative_bank_filter",
        "margin_formula",
        "selected_on",
        "corpus_sha256",
    ):
        if key in freeze:
            expect_string(freeze, key, errors)

    if freeze.get("selected_on") != "validation":
        errors.append("freeze.selected_on: expected 'validation'")

    if freeze.get("corpus_sha256") != expected_corpus_sha256:
        errors.append(
            "freeze.corpus_sha256: does not match audited Round-4 large corpus hash"
        )

    model_sha = freeze.get("model_sha256")
    if not isinstance(model_sha, str) or not model_sha.strip():
        errors.append("freeze.model_sha256: expected string")
    elif model_sha != "unavailable-with-reason" and not SHA256_RE.fullmatch(model_sha):
        if not model_sha.startswith("unavailable"):
            errors.append(
                "freeze.model_sha256: expected lowercase SHA-256 or unavailable-with-reason"
            )

    if not isinstance(freeze.get("embedding_dimension"), int) or freeze.get("embedding_dimension", 0) <= 0:
        errors.append("freeze.embedding_dimension: expected positive integer")
    if not isinstance(freeze.get("k"), int) or freeze.get("k", 0) <= 0:
        errors.append("freeze.k: expected positive integer")
    if "threshold_tau" in freeze:
        expect_number(freeze, "threshold_tau", errors)

    return errors


def validate_row(record: dict[str, Any] | None, pre_errors: list[str], expected_split: str) -> list[str]:
    errors = list(pre_errors)
    if record is None:
        return errors

    errors.extend(raw_field_errors(record, "row"))
    missing = sorted(ROW_REQUIRED_FIELDS - set(record))
    extra = sorted(set(record) - ROW_ALLOWED_FIELDS)
    if missing:
        errors.append(f"missing required fields {missing}")
    if extra:
        errors.append(f"unknown fields {extra}")

    for key in (
        "id",
        "split",
        "label",
        "attack_class",
        "benign_subclass",
        "bypass_class",
        "source_type",
        "trust_level",
        "expected_action",
        "family_id",
        "group_id",
    ):
        if key in record:
            expect_string(record, key, errors)

    if record.get("split") != expected_split:
        errors.append(f"split: expected {expected_split!r}")
    if record.get("label") not in LABELS:
        errors.append(f"label: expected one of {sorted(LABELS)}")

    for key in ("contains_sensitive_sink", "requires_tool_call", "pred_attack"):
        if key in record:
            expect_bool(record, key, errors)
    for key in ("s_pos", "s_neg", "margin", "threshold_tau"):
        if key in record:
            expect_number(record, key, errors)
    for key in ("top_positive_neighbor_ids", "top_negative_neighbor_ids"):
        if key in record:
            expect_string_array(record, key, errors)

    return errors


def sha256_file_modes(path: Path) -> set[str]:
    data = path.read_bytes()
    hashes = {hashlib.sha256(data).hexdigest()}
    lf_normalized = data.replace(b"\r\n", b"\n")
    hashes.add(hashlib.sha256(lf_normalized).hexdigest())
    return hashes


def validate_test_start(
    test_start: Any,
    freeze: dict[str, Any],
    freeze_hashes: set[str],
) -> list[str]:
    errors: list[str] = []
    if not isinstance(test_start, dict):
        return ["test_start: top-level JSON value must be an object"]
    errors.extend(raw_field_errors(test_start, "test_start"))
    if test_start.get("freeze_record_sha256") not in freeze_hashes:
        errors.append("test_start.freeze_record_sha256: does not match freeze file")
    if test_start.get("selected_on") != "validation":
        errors.append("test_start.selected_on: expected 'validation'")
    if test_start.get("k") != freeze.get("k"):
        errors.append("test_start.k: does not match freeze.k")
    if test_start.get("threshold_tau") != freeze.get("threshold_tau"):
        errors.append("test_start.threshold_tau: does not match freeze.threshold_tau")
    if test_start.get("corpus_sha256") != freeze.get("corpus_sha256"):
        errors.append("test_start.corpus_sha256: does not match freeze.corpus_sha256")
    expect_string(test_start, "test_scoring_started_at", errors)
    return errors


def validate_metric_object(metrics: Any, expected_split: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(metrics, dict):
        return ["metrics: top-level JSON value must be an object"]

    errors.extend(raw_field_errors(metrics, "metrics"))
    if metrics.get("split") != expected_split:
        errors.append(f"metrics.split: expected {expected_split!r}")

    for key in ("tp", "fn", "fp", "tn", "attack_total", "benign_total"):
        if not isinstance(metrics.get(key), int) or metrics.get(key, -1) < 0:
            errors.append(f"metrics.{key}: expected non-negative integer")

    for key in (
        "attack_recall",
        "benign_fp_rate",
        "false_positives_per_1k_benign",
        "base_rate_precision_100_benign_per_attack",
        "base_rate_precision_1000_benign_per_attack",
        "roc_auc",
        "pr_auc_average_precision",
        "threshold_tau",
    ):
        if key in metrics:
            expect_number(metrics, key, errors)
        else:
            errors.append(f"metrics.{key}: missing")

    base_ci = metrics.get("base_rate_precision_wilson_95")
    if not isinstance(base_ci, dict):
        errors.append("metrics.base_rate_precision_wilson_95: expected object")
    else:
        for key in ("1_attack_per_100_benign", "1_attack_per_1000_benign"):
            item = base_ci.get(key)
            if not isinstance(item, dict):
                errors.append(f"metrics.base_rate_precision_wilson_95.{key}: expected object")
                continue
            for subkey in ("estimate", "lower", "upper"):
                if subkey not in item or not isinstance(item[subkey], (int, float)):
                    errors.append(
                        f"metrics.base_rate_precision_wilson_95.{key}.{subkey}: expected number"
                    )

    adjacent = metrics.get("adjacent_security_benign_false_positives")
    if not isinstance(adjacent, dict) or not isinstance(adjacent.get("total"), int):
        errors.append("metrics.adjacent_security_benign_false_positives.total: expected integer")

    comparison = metrics.get("rules_baseline_comparison")
    if not isinstance(comparison, dict):
        errors.append("metrics.rules_baseline_comparison: expected object")
    else:
        for key in (
            "attack_recall_delta",
            "benign_fp_rate_delta",
            "tp_delta_vs_rules_rate_on_this_split",
        ):
            if key not in comparison or not isinstance(comparison[key], (int, float)):
                errors.append(f"metrics.rules_baseline_comparison.{key}: expected number")

    return errors


def validate_provenance(
    provenance: Any,
    freeze_hashes: set[str],
    test_start_hashes: set[str] | None,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(provenance, dict):
        return ["provenance: top-level JSON value must be an object"]
    errors.extend(raw_field_errors(provenance, "provenance"))
    if provenance.get("freeze_record_sha256") not in freeze_hashes:
        errors.append("provenance.freeze_record_sha256: does not match freeze file")
    if (
        test_start_hashes is not None
        and provenance.get("test_start_record_sha256") not in test_start_hashes
    ):
        errors.append("provenance.test_start_record_sha256: does not match test-start file")
    resource = provenance.get("resource_actual")
    if not isinstance(resource, dict):
        errors.append("provenance.resource_actual: expected object")
    elif resource.get("exceeded_budget") is not False:
        errors.append("provenance.resource_actual.exceeded_budget: expected false")
    non_claims = provenance.get("non_claims")
    if not isinstance(non_claims, list) or not any(
        isinstance(item, str) and "not a certification" in item for item in non_claims
    ):
        errors.append("provenance.non_claims: missing research-corpus/non-certification disclaimer")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--test-start", type=Path)
    parser.add_argument("--validation", type=Path, required=True)
    parser.add_argument("--test", type=Path, required=True)
    parser.add_argument("--validation-metrics", type=Path, required=True)
    parser.add_argument("--test-metrics", type=Path, required=True)
    parser.add_argument("--provenance", type=Path)
    parser.add_argument("--expected-corpus-sha256", default=EXPECTED_CORPUS_SHA256)
    parser.add_argument("--expected-validation-rows", type=int, default=6888)
    parser.add_argument("--expected-test-rows", type=int, default=9408)
    args = parser.parse_args()

    errors: list[str] = []
    freeze: dict[str, Any] | None = None
    freeze_hashes: set[str] | None = None
    test_start_hashes: set[str] | None = None

    try:
        freeze = load_json(args.freeze)
        errors.extend(validate_freeze(freeze, args.expected_corpus_sha256))
        freeze_hashes = sha256_file_modes(args.freeze)
    except OSError as exc:
        errors.append(f"{args.freeze}: failed to read: {exc}")
    except ValueError as exc:
        errors.append(str(exc))

    if args.test_start and freeze is not None and freeze_hashes is not None:
        try:
            test_start = load_json(args.test_start)
            test_start_hashes = sha256_file_modes(args.test_start)
            errors.extend(validate_test_start(test_start, freeze, freeze_hashes))
        except OSError as exc:
            errors.append(f"{args.test_start}: failed to read: {exc}")
        except ValueError as exc:
            errors.append(str(exc))

    for expected_split, path, expected_rows in (
        ("validation", args.validation, args.expected_validation_rows),
        ("test", args.test, args.expected_test_rows),
    ):
        try:
            records = load_jsonl(path)
        except OSError as exc:
            errors.append(f"{path}: failed to read: {exc}")
            continue
        if not records:
            errors.append(f"{path}: expected at least one row")
        if len(records) != expected_rows:
            errors.append(f"{path}: expected {expected_rows} rows, got {len(records)}")
        for label, record, pre_errors in records:
            row_errors = validate_row(record, pre_errors, expected_split)
            errors.extend(f"{label}: {error}" for error in row_errors)

    for expected_split, path in (
        ("validation", args.validation_metrics),
        ("test", args.test_metrics),
    ):
        try:
            metrics = load_json(path)
            metric_errors = validate_metric_object(metrics, expected_split)
            errors.extend(f"{path}: {error}" for error in metric_errors)
        except OSError as exc:
            errors.append(f"{path}: failed to read: {exc}")
        except ValueError as exc:
            errors.append(str(exc))

    if args.provenance and freeze_hashes is not None:
        try:
            provenance = load_json(args.provenance)
            errors.extend(validate_provenance(provenance, freeze_hashes, test_start_hashes))
        except OSError as exc:
            errors.append(f"{args.provenance}: failed to read: {exc}")
        except ValueError as exc:
            errors.append(str(exc))

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("round4_embedding_sweep_artifact: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
