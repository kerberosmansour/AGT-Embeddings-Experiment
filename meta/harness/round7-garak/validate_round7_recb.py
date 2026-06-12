#!/usr/bin/env python3
"""Validate Round-7 Rec B-style experiment artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MANIFEST = ROOT / "artifacts/round7-garak/recb-pilot/manifest.json"
REQUIRED_ARMS = {"fixed_round4_bank", "round7_in_domain_bank"}
FORBIDDEN_FIELDS = {"text", "raw_text", "prompt", "content", "normalized_text", "payload"}
REQUIRED_CONTROLS = {
    "r1-prime-intent-gated-tool-control",
    "terminal-escape-output-sanitizer",
    "outbound-sensitive-output-scan",
    "package-provenance-verifier",
    "round7-hard-benign-expansion",
}


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


def validate_metric_object(metrics: Any, path: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(metrics, dict):
        return [f"{path}: expected object"]
    for key in ("tp", "fn", "fp", "tn", "attack_total", "benign_total", "attack_recall", "benign_fp_rate"):
        if key not in metrics:
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
            for key in ("row_id", "row_sha256", "label", "scores", "decisions"):
                if key not in row:
                    errors.append(f"{path}:{line_no}: missing {key}")
    return errors


def validate_arm(root: Path, arm: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    name = arm.get("arm")
    if name not in REQUIRED_ARMS:
        errors.append(f"arms: unexpected arm {name!r}")
        return errors

    for field in ("freeze_record_path", "metrics_path", "test_per_row_path"):
        rel = arm.get(field)
        if not isinstance(rel, str):
            errors.append(f"{name}.{field}: missing string path")
            continue
        path = root / rel
        if not path.exists():
            errors.append(f"{name}.{field}: missing file {rel}")

    freeze_path = root / str(arm.get("freeze_record_path", ""))
    metrics_path = root / str(arm.get("metrics_path", ""))
    per_row_path = root / str(arm.get("test_per_row_path", ""))

    if freeze_path.exists():
        freeze = load_json(freeze_path)
        errors.extend(metadata_only_errors(freeze, str(freeze_path)))
        if freeze.get("schema") != "round7-recb-freeze-record-v1":
            errors.append(f"{freeze_path}: wrong schema")
        if freeze.get("selection_split") != "validation":
            errors.append(f"{freeze_path}: selection_split must be validation")
        if freeze.get("test_scored_once_after_freeze") is not True:
            errors.append(f"{freeze_path}: test_scored_once_after_freeze must be true")
        if freeze.get("normalizer_id") != "agt_rust_round7":
            errors.append(f"{freeze_path}: normalizer_id must be agt_rust_round7")

    if metrics_path.exists():
        metrics = load_json(metrics_path)
        errors.extend(metadata_only_errors(metrics, str(metrics_path)))
        if metrics.get("schema") != "round7-recb-arm-metrics-v1":
            errors.append(f"{metrics_path}: wrong schema")
        test = metrics.get("test", {})
        for decision in ("knn_zero_fp", "r1_legacy_untrusted_tool", "recb_head_in_band", "coequal_head_everywhere"):
            errors.extend(validate_metric_object(test.get(decision), f"{metrics_path}.test.{decision}"))
        breakdowns = metrics.get("test_breakdowns_for_recb", {})
        for field in ("attack_class", "bypass_class", "benign_subclass"):
            if field not in breakdowns:
                errors.append(f"{metrics_path}.test_breakdowns_for_recb.{field}: missing")

    if per_row_path.exists():
        errors.extend(validate_jsonl(per_row_path))

    return errors


def validate_manifest(path: Path) -> list[str]:
    root = ROOT
    manifest = load_json(path)
    errors = metadata_only_errors(manifest)
    if manifest.get("schema") != "round7-recb-experiment-v1":
        errors.append("manifest.schema: expected round7-recb-experiment-v1")
    if manifest.get("normalizer_id") != "agt_rust_round7":
        errors.append("manifest.normalizer_id: expected agt_rust_round7")
    if manifest.get("detector_contract", {}).get("selection_split") != "validation":
        errors.append("manifest.detector_contract.selection_split: expected validation")

    arms = manifest.get("arms")
    if not isinstance(arms, list):
        errors.append("manifest.arms: expected list")
        arms = []
    found = {arm.get("arm") for arm in arms if isinstance(arm, dict)}
    missing = REQUIRED_ARMS - found
    if missing:
        errors.append(f"manifest.arms: missing required arms {sorted(missing)}")
    for arm in arms:
        if isinstance(arm, dict):
            errors.extend(validate_arm(root, arm))

    metrics_path = manifest.get("metrics_path")
    if isinstance(metrics_path, str):
        metrics_file = root / metrics_path
        if metrics_file.exists():
            metrics = load_json(metrics_file)
            errors.extend(metadata_only_errors(metrics, str(metrics_file)))
            if metrics.get("schema") != "round7-recb-metrics-v1":
                errors.append(f"{metrics_file}: wrong schema")
        else:
            errors.append(f"manifest.metrics_path: missing file {metrics_path}")
    else:
        errors.append("manifest.metrics_path: missing string")

    controls = {item.get("control_id") for item in manifest.get("recommendations", []) if isinstance(item, dict)}
    missing_controls = REQUIRED_CONTROLS - controls
    if missing_controls:
        errors.append(f"manifest.recommendations: missing controls {sorted(missing_controls)}")

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
