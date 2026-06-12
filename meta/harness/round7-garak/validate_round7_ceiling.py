#!/usr/bin/env python3
"""Validate Round-7 stepwise ceiling artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MANIFEST = ROOT / "artifacts/round7-garak/ceiling-pilot/manifest.json"
FORBIDDEN_FIELDS = {"text", "raw_text", "prompt", "content", "normalized_text", "payload"}
REQUIRED_STEPS = (
    "00_baseline_fixed_recb",
    "01_r1_prime_intent_gate",
    "02_hard_benign_guard",
    "03_round7_in_domain_training",
    "04_tool_output_authority_boundary",
    "05_output_stage_leakage_scan",
    "06_package_provenance_verifier",
    "07_terminal_escape_sanitizer",
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def metadata_only_errors(value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key in FORBIDDEN_FIELDS:
                errors.append(f"{path}.{key}: forbidden raw-text-like field")
            errors.extend(metadata_only_errors(item, f"{path}.{key}"))
    elif isinstance(value, list):
        for idx, item in enumerate(value):
            errors.extend(metadata_only_errors(item, f"{path}[{idx}]"))
    return errors


def validate_metric(value: Any, path: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, dict):
        return [f"{path}: expected object"]
    for key in ("tp", "fn", "fp", "tn", "attack_total", "benign_total", "attack_recall", "benign_fp_rate"):
        if key not in value:
            errors.append(f"{path}.{key}: missing")
    return errors


def validate_jsonl(path: Path) -> list[str]:
    errors: list[str] = []
    with path.open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"{path}:{line_no}: invalid JSON ({exc})")
                continue
            errors.extend(metadata_only_errors(row, f"{path}:{line_no}"))
            for key in ("row_id", "row_sha256", "label", "scores", "controls", "steps"):
                if key not in row:
                    errors.append(f"{path}:{line_no}: missing {key}")
            steps = row.get("steps", {})
            for step in REQUIRED_STEPS:
                if step not in steps:
                    errors.append(f"{path}:{line_no}: missing step {step}")
    return errors


def validate_manifest(path: Path) -> list[str]:
    manifest = load_json(path)
    errors = metadata_only_errors(manifest)
    if manifest.get("schema") != "round7-ceiling-experiment-v1":
        errors.append("manifest.schema: expected round7-ceiling-experiment-v1")
    if manifest.get("normalizer_id") != "agt_rust_round7":
        errors.append("manifest.normalizer_id: expected agt_rust_round7")
    contract = manifest.get("detector_contract", {})
    if contract.get("selection_split") != "validation":
        errors.append("manifest.detector_contract.selection_split: expected validation")
    if contract.get("test_scored_once_after_freeze") is not True:
        errors.append("manifest.detector_contract.test_scored_once_after_freeze: expected true")
    if tuple(contract.get("step_order", [])) != REQUIRED_STEPS:
        errors.append("manifest.detector_contract.step_order: wrong or missing required steps")

    metrics_rel = manifest.get("metrics_path")
    if not isinstance(metrics_rel, str):
        errors.append("manifest.metrics_path: missing string")
        metrics_rel = ""
    metrics_path = ROOT / metrics_rel
    if not metrics_path.exists():
        errors.append(f"manifest.metrics_path: missing file {metrics_rel}")
    else:
        metrics = load_json(metrics_path)
        errors.extend(metadata_only_errors(metrics, str(metrics_path)))
        if metrics.get("schema") != "round7-ceiling-metrics-v1":
            errors.append(f"{metrics_path}: wrong schema")
        if tuple(metrics.get("step_order", [])) != REQUIRED_STEPS:
            errors.append(f"{metrics_path}: wrong step_order")
        steps = metrics.get("steps", {})
        for step in REQUIRED_STEPS:
            if step not in steps:
                errors.append(f"{metrics_path}.steps.{step}: missing")
                continue
            errors.extend(validate_metric(steps[step].get("metrics"), f"{metrics_path}.steps.{step}.metrics"))
            if "delta_from_previous" not in steps[step]:
                errors.append(f"{metrics_path}.steps.{step}.delta_from_previous: missing")
            if "false_positive_attribution" not in steps[step]:
                errors.append(f"{metrics_path}.steps.{step}.false_positive_attribution: missing")

    per_row_rel = manifest.get("test_per_row_path")
    if not isinstance(per_row_rel, str):
        errors.append("manifest.test_per_row_path: missing string")
        per_row_rel = ""
    per_row_path = ROOT / per_row_rel
    if not per_row_path.exists():
        errors.append(f"manifest.test_per_row_path: missing file {per_row_rel}")
    else:
        errors.extend(validate_jsonl(per_row_path))

    recs = manifest.get("recommendations", [])
    rec_steps = {item.get("step_id") for item in recs if isinstance(item, dict)}
    missing_recs = set(REQUIRED_STEPS[1:]) - rec_steps
    if missing_recs:
        errors.append(f"manifest.recommendations: missing recommendation steps {sorted(missing_recs)}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", nargs="?", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args(argv)
    errors = validate_manifest(args.manifest)
    if errors:
        for error in errors:
            print(f"ERROR {error}", file=sys.stderr)
        return 1
    print(f"PASS {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
