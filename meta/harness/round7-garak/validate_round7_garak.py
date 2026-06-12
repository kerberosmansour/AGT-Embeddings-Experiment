#!/usr/bin/env python3
"""Validate Round-7 WS-C 2x2 harness artifacts.

This validator is public-safe by construction: it rejects raw-text-like output
keys, raw URL/email-looking strings, missing freeze records, and incomplete
2x2 matrix artifacts.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DEFAULT_MANIFEST = ROOT / "artifacts/round7-garak/smoke/manifest.json"

FORBIDDEN_OUTPUT_FIELDS = {"text", "raw_text", "prompt", "content", "normalized_text", "payload"}
EXPECTED_CELLS = {
    "round4__old_gate0_round6",
    "round4__agt_rust_round7",
    "round7__old_gate0_round6",
    "round7__agt_rust_round7",
}
REQUIRED_METRIC_FIELDS = {
    "attack_recall",
    "attack_recall_wilson_95",
    "benign_fp_rate",
    "benign_fp_rate_wilson_95",
    "base_rate_precision_100_benign_per_attack",
    "base_rate_precision_1000_benign_per_attack",
    "breakdowns",
    "rules_only_sidecar",
}


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{path}: invalid JSON: {exc}") from exc


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                parsed = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{lineno}: invalid JSON: {exc}") from exc
            if not isinstance(parsed, dict):
                raise SystemExit(f"{path}:{lineno}: JSONL row must be an object")
            rows.append(parsed)
    return rows


def repo_path(path_str: str) -> Path:
    path = Path(path_str)
    return path if path.is_absolute() else ROOT / path


def metadata_only_errors(value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key in FORBIDDEN_OUTPUT_FIELDS:
                errors.append(f"{path}.{key}: forbidden raw-text-like field")
            errors.extend(metadata_only_errors(item, f"{path}.{key}"))
    elif isinstance(value, list):
        for idx, item in enumerate(value):
            errors.extend(metadata_only_errors(item, f"{path}[{idx}]"))
    elif isinstance(value, str):
        if re.search(r"https?://", value, re.IGNORECASE):
            errors.append(f"{path}: raw URL-like string")
        if re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", value):
            errors.append(f"{path}: raw email-like string")
    return errors


def validate_json_artifact(path: Path) -> list[str]:
    data = load_json(path)
    return [f"{path}: {err}" for err in metadata_only_errors(data)]


def validate_jsonl_artifact(path: Path) -> list[str]:
    errors: list[str] = []
    for idx, row in enumerate(load_jsonl(path), 1):
        for err in metadata_only_errors(row):
            errors.append(f"{path}:{idx}: {err}")
        required = {"row_id", "row_sha256", "label", "score", "threshold_tau", "pred_attack", "normalized_sha256"}
        missing = required - set(row)
        if missing:
            errors.append(f"{path}:{idx}: missing required row metadata {sorted(missing)}")
    return errors


def validate_cell(cell: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    key = str(cell.get("cell_key"))
    paths = {
        "freeze": repo_path(str(cell.get("freeze_record_path"))),
        "validation_metrics": repo_path(str(cell.get("validation_metrics_path"))),
        "validation_rows": repo_path(str(cell.get("validation_per_row_path"))),
        "test_metrics": repo_path(str(cell.get("test_metrics_path"))),
        "test_rows": repo_path(str(cell.get("test_per_row_path"))),
    }
    for name, path in paths.items():
        if not path.exists():
            errors.append(f"{key}: missing {name} artifact at {path}")
    if errors:
        return errors

    freeze = load_json(paths["freeze"])
    if freeze.get("selection_split") != "validation":
        errors.append(f"{key}: freeze record did not select on validation")
    if freeze.get("test_scored_after_freeze") is not True:
        errors.append(f"{key}: freeze record does not assert test_scored_after_freeze")
    if freeze.get("threshold_tau") is None:
        errors.append(f"{key}: freeze record missing threshold_tau")
    if freeze.get("scorer_mode") != cell.get("scorer_mode"):
        errors.append(f"{key}: freeze scorer_mode mismatch")

    for metric_name in ("validation_metrics", "test_metrics"):
        metrics = load_json(paths[metric_name])
        missing = REQUIRED_METRIC_FIELDS - set(metrics)
        if missing:
            errors.append(f"{key}: {metric_name} missing {sorted(missing)}")
        if "benign_subclass" not in metrics.get("breakdowns", {}):
            errors.append(f"{key}: {metric_name} missing benign_subclass breakdown")
        if "bypass_class" not in metrics.get("breakdowns", {}):
            errors.append(f"{key}: {metric_name} missing bypass_class breakdown")

    errors.extend(validate_json_artifact(paths["freeze"]))
    errors.extend(validate_json_artifact(paths["validation_metrics"]))
    errors.extend(validate_json_artifact(paths["test_metrics"]))
    errors.extend(validate_jsonl_artifact(paths["validation_rows"]))
    errors.extend(validate_jsonl_artifact(paths["test_rows"]))
    return errors


def validate_manifest(manifest_path: Path) -> list[str]:
    manifest = load_json(manifest_path)
    errors = [f"{manifest_path}: {err}" for err in metadata_only_errors(manifest)]
    if manifest.get("schema") != "round7-garak-2x2-manifest-v1":
        errors.append("manifest schema mismatch")
    scorer = manifest.get("scorer_mode")
    if scorer not in {"metadata-smoke", "knn"}:
        errors.append(f"invalid scorer_mode {scorer!r}")
    if scorer == "metadata-smoke" and manifest.get("measurement_valid_for_headline") is not False:
        errors.append("metadata-smoke manifests must be marked not headline-valid")
    if scorer == "knn" and manifest.get("measurement_valid_for_headline") is not True:
        errors.append("knn manifests must be marked headline-valid")

    cells = manifest.get("cells")
    if not isinstance(cells, list):
        return errors + ["manifest cells must be a list"]
    cell_keys = {str(cell.get("cell_key")) for cell in cells}
    if cell_keys != EXPECTED_CELLS:
        errors.append(f"manifest cells mismatch: {sorted(cell_keys)}")
    cell_scorers = {cell.get("scorer_mode") for cell in cells}
    if cell_scorers != {scorer}:
        errors.append(f"cell scorer modes are not fixed: {sorted(map(str, cell_scorers))}")

    for cell in cells:
        errors.extend(validate_cell(cell))

    matrix_path = repo_path(str(manifest.get("matrix_summary_path")))
    if not matrix_path.exists():
        errors.append(f"missing matrix summary at {matrix_path}")
    else:
        matrix = load_json(matrix_path)
        errors.extend(f"{matrix_path}: {err}" for err in metadata_only_errors(matrix))
        for key in (
            "round7_treatment_minus_baseline",
            "round4_new_minus_old_regression_guard",
            "paired_deltas",
            "cells",
        ):
            if key not in matrix:
                errors.append(f"matrix summary missing {key}")
        if set(matrix.get("cells", {})) != EXPECTED_CELLS:
            errors.append("matrix summary cells mismatch")
    return errors


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("manifest", type=Path, nargs="?", default=DEFAULT_MANIFEST)
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    errors = validate_manifest(args.manifest)
    if errors:
        print("FAIL", file=sys.stderr)
        for err in errors[:100]:
            print(f"- {err}", file=sys.stderr)
        if len(errors) > 100:
            print(f"- ... {len(errors) - 100} more errors", file=sys.stderr)
        return 1
    print(f"PASS {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
