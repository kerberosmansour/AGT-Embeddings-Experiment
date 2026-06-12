#!/usr/bin/env python3
"""Validate exp4 co-equal ensemble artifacts for issue #9.

This validator is intentionally narrow: it reads existing JSON/JSONL artifacts,
checks metadata-only hygiene, confirms validation-frozen threshold selection,
and recomputes the strict co-equal metrics from per-row flags. It does not load
an embedding model, retrain a head, or choose any thresholds.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DEFAULT_ARTIFACT_DIR = ROOT / "artifacts/exp4-coequal"

FORBIDDEN_OUTPUT_FIELDS = {
    "text",
    "raw_text",
    "prompt",
    "content",
    "normalized_text",
    "payload",
    "raw_payload",
    "raw_prompt",
    "raw_content",
    "tool_args",
    "tool_arguments",
    "raw_tool_result",
}
REQUIRED_FILES = {
    "freeze": "freeze-record.json",
    "metrics": "test-metrics.json",
    "newnorm": "newnorm-metrics.json",
    "rows": "test-per-row.jsonl",
}
ROW_REQUIRED = {
    "id",
    "label",
    "attack_class",
    "knn_flag",
    "head_flag",
    "r1_flag",
    "combined",
}
ROW_ALLOWED = ROW_REQUIRED
LABELS = {"attack", "benign"}
TOL = 1e-12


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: invalid JSON: {exc}") from exc


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for lineno, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            try:
                parsed = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{lineno}: invalid JSON: {exc}") from exc
            if not isinstance(parsed, dict):
                raise ValueError(f"{path}:{lineno}: JSONL row must be an object")
            rows.append(parsed)
    return rows


def metadata_only_errors(value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            child_path = f"{path}.{key}"
            if str(key).strip().lower() in FORBIDDEN_OUTPUT_FIELDS:
                errors.append(f"{child_path}: forbidden raw-text-like field")
            errors.extend(metadata_only_errors(item, child_path))
    elif isinstance(value, list):
        for idx, item in enumerate(value):
            errors.extend(metadata_only_errors(item, f"{path}[{idx}]"))
    elif isinstance(value, str):
        if re.search(r"https?://", value, re.IGNORECASE):
            errors.append(f"{path}: raw URL-like string")
        if re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", value):
            errors.append(f"{path}: raw email-like string")
    return errors


def expect_number(record: dict[str, Any], key: str, errors: list[str], label: str) -> None:
    value = record.get(key)
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
        errors.append(f"{label}.{key}: expected finite number")


def expect_bool(record: dict[str, Any], key: str, errors: list[str], label: str) -> None:
    if not isinstance(record.get(key), bool):
        errors.append(f"{label}.{key}: expected boolean")


def compare_float(name: str, actual: float, expected: Any, errors: list[str]) -> None:
    if not isinstance(expected, (int, float)) or isinstance(expected, bool) or not math.isfinite(expected):
        errors.append(f"{name}: expected metrics value must be finite number")
        return
    if abs(actual - float(expected)) > TOL:
        errors.append(f"{name}: metrics value {expected!r} does not match recomputed {actual!r}")


def validate_freeze(freeze: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(freeze, dict):
        return ["freeze-record.json: top-level value must be an object"]
    errors.extend(f"freeze-record.json:{err}" for err in metadata_only_errors(freeze))
    if freeze.get("selected_on") != "validation":
        errors.append("freeze-record.json.selected_on: expected 'validation'")
    for key in ("knn_zerofp", "head_zerofp_strict", "head_0p1pct_val_fpr"):
        expect_number(freeze, key, errors, "freeze-record.json")
    if not isinstance(freeze.get("rule"), str) or not freeze["rule"].strip():
        errors.append("freeze-record.json.rule: expected non-empty string")
    return errors


def validate_row(row: dict[str, Any], row_idx: int) -> list[str]:
    errors: list[str] = []
    label = f"test-per-row.jsonl:{row_idx}"
    errors.extend(f"{label}:{err}" for err in metadata_only_errors(row))
    missing = ROW_REQUIRED - set(row)
    extra = set(row) - ROW_ALLOWED
    if missing:
        errors.append(f"{label}: missing required fields {sorted(missing)}")
    if extra:
        errors.append(f"{label}: unknown fields {sorted(extra)}")
    if not isinstance(row.get("id"), str) or not row.get("id", "").strip():
        errors.append(f"{label}.id: expected non-empty string")
    if row.get("label") not in LABELS:
        errors.append(f"{label}.label: expected one of {sorted(LABELS)}")
    if not isinstance(row.get("attack_class"), str) or not row.get("attack_class", "").strip():
        errors.append(f"{label}.attack_class: expected non-empty string")
    for key in ("knn_flag", "head_flag", "r1_flag", "combined"):
        if key in row:
            expect_bool(row, key, errors, label)
    return errors


def rate(numerator: int, denominator: int) -> float:
    return 0.0 if denominator == 0 else numerator / denominator


def recompute_strict(rows: list[dict[str, Any]]) -> dict[str, Any]:
    attack_rows = [row for row in rows if row.get("label") == "attack"]
    benign_rows = [row for row in rows if row.get("label") == "benign"]
    by_control = {
        "knn_zerofp": rate(sum(1 for row in attack_rows if row.get("knn_flag") is True), len(attack_rows)),
        "head_zerofp": rate(sum(1 for row in attack_rows if row.get("head_flag") is True), len(attack_rows)),
        "R1": rate(sum(1 for row in attack_rows if row.get("r1_flag") is True), len(attack_rows)),
    }
    family_counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for row in attack_rows:
        family = str(row.get("attack_class"))
        family_counts[family][1] += 1
        if row.get("combined") is True:
            family_counts[family][0] += 1
    return {
        "test_combined_recall_strict": rate(
            sum(1 for row in attack_rows if row.get("combined") is True),
            len(attack_rows),
        ),
        "test_combined_fp_strict": rate(
            sum(1 for row in benign_rows if row.get("combined") is True),
            len(benign_rows),
        ),
        "by_control_recall": by_control,
        "per_family_recall_strict": {
            family: counts[0] / counts[1]
            for family, counts in sorted(family_counts.items())
        },
        "attack_total": len(attack_rows),
        "benign_total": len(benign_rows),
        "rows": len(rows),
    }


def validate_metrics(metrics: Any, rows: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    if not isinstance(metrics, dict):
        return ["test-metrics.json: top-level value must be an object"]
    errors.extend(f"test-metrics.json:{err}" for err in metadata_only_errors(metrics))
    if metrics.get("selected_on") != "validation":
        errors.append("test-metrics.json.selected_on: expected 'validation'")
    for key in (
        "test_combined_recall_strict",
        "test_combined_fp_strict",
        "test_combined_recall_0p1pct",
        "test_combined_fp_0p1pct",
    ):
        expect_number(metrics, key, errors, "test-metrics.json")
    if not isinstance(metrics.get("by_control_recall"), dict):
        errors.append("test-metrics.json.by_control_recall: expected object")
    if not isinstance(metrics.get("per_family_recall_strict"), dict):
        errors.append("test-metrics.json.per_family_recall_strict: expected object")
    if not isinstance(metrics.get("compare"), dict):
        errors.append("test-metrics.json.compare: expected object")
    if errors:
        return errors

    recomputed = recompute_strict(rows)
    compare_float(
        "test-metrics.json.test_combined_recall_strict",
        recomputed["test_combined_recall_strict"],
        metrics.get("test_combined_recall_strict"),
        errors,
    )
    compare_float(
        "test-metrics.json.test_combined_fp_strict",
        recomputed["test_combined_fp_strict"],
        metrics.get("test_combined_fp_strict"),
        errors,
    )
    if metrics.get("test_combined_fp_strict") != 0:
        errors.append("test-metrics.json.test_combined_fp_strict: expected 0 at the reported operating point")
    if metrics.get("test_combined_fp_0p1pct") != 0:
        errors.append("test-metrics.json.test_combined_fp_0p1pct: expected 0 at the reported operating point")

    for key, actual in recomputed["by_control_recall"].items():
        compare_float(
            f"test-metrics.json.by_control_recall.{key}",
            actual,
            metrics["by_control_recall"].get(key),
            errors,
        )

    metric_families = set(metrics["per_family_recall_strict"])
    row_families = set(recomputed["per_family_recall_strict"])
    if metric_families != row_families:
        errors.append(
            "test-metrics.json.per_family_recall_strict: family keys do not match per-row attack families"
        )
    for family, actual in recomputed["per_family_recall_strict"].items():
        compare_float(
            f"test-metrics.json.per_family_recall_strict.{family}",
            actual,
            metrics["per_family_recall_strict"].get(family),
            errors,
        )
    return errors


def validate_newnorm(metrics: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(metrics, dict):
        return ["newnorm-metrics.json: top-level value must be an object"]
    errors.extend(f"newnorm-metrics.json:{err}" for err in metadata_only_errors(metrics))
    if metrics.get("selected_on") != "validation":
        errors.append("newnorm-metrics.json.selected_on: expected 'validation'")
    for key in (
        "knn_zerofp",
        "head_0p1pct_val_fpr_cut",
        "test_combined_recall",
        "test_combined_fp",
        "old_normalizer_ensemble",
    ):
        expect_number(metrics, key, errors, "newnorm-metrics.json")
    if metrics.get("test_combined_fp") != 0:
        errors.append("newnorm-metrics.json.test_combined_fp: expected 0 at the reported operating point")
    if not isinstance(metrics.get("per_family_recall"), dict):
        errors.append("newnorm-metrics.json.per_family_recall: expected object")
    return errors


def validate_artifact_dir(artifact_dir: Path) -> list[str]:
    artifact_dir = artifact_dir.resolve()
    errors: list[str] = []
    paths = {name: artifact_dir / rel for name, rel in REQUIRED_FILES.items()}
    for name, path in paths.items():
        if not path.exists():
            errors.append(f"missing {name} artifact at {path}")
    if errors:
        return errors

    try:
        freeze = load_json(paths["freeze"])
        metrics = load_json(paths["metrics"])
        newnorm = load_json(paths["newnorm"])
        rows = load_jsonl(paths["rows"])
    except ValueError as exc:
        return [str(exc)]

    errors.extend(validate_freeze(freeze))
    for idx, row in enumerate(rows, 1):
        errors.extend(validate_row(row, idx))
    if not rows:
        errors.append("test-per-row.jsonl: expected at least one row")
    if not errors:
        errors.extend(validate_metrics(metrics, rows))
    errors.extend(validate_newnorm(newnorm))
    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact_dir", type=Path, nargs="?", default=DEFAULT_ARTIFACT_DIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    errors = validate_artifact_dir(args.artifact_dir)
    if errors:
        print("FAIL", file=sys.stderr)
        for error in errors[:100]:
            print(f"- {error}", file=sys.stderr)
        if len(errors) > 100:
            print(f"- ... {len(errors) - 100} more errors", file=sys.stderr)
        return 1

    rows = load_jsonl(args.artifact_dir / REQUIRED_FILES["rows"])
    metrics = load_json(args.artifact_dir / REQUIRED_FILES["metrics"])
    print(
        "PASS "
        f"{args.artifact_dir} "
        f"rows={len(rows)} "
        f"strict_recall={metrics['test_combined_recall_strict']:.12f} "
        f"strict_fp={metrics['test_combined_fp_strict']:.12f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
