#!/usr/bin/env python3
"""Validate AGT consolidated L1 static artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from l1_static import EVIDENCE_LEVEL, metadata_only_errors


REQUIRED_ROW_FIELDS = {
    "row_id",
    "row_sha256",
    "corpus_id",
    "payload_ref",
    "family",
    "stratum",
    "split",
    "label",
    "hard_benign",
    "evidence_level",
    "selection_split",
    "detector_config_hash",
    "detection",
}


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{path}: invalid JSON: {exc}") from exc


def resolve(base: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else base / path


def validate_report(report_path: Path) -> tuple[list[str], dict[str, Any]]:
    report = load_json(report_path)
    base = report_path.parent
    errors = [f"{report_path}: {err}" for err in metadata_only_errors(report)]

    if report.get("schema") != "agt-consolidated-l1-static-report-v1":
        errors.append("report schema mismatch")
    if report.get("certification_claim") is not False:
        errors.append("certification_claim must be literal false")
    if report.get("selection_split") != "validation":
        errors.append("selection_split must be validation")
    if report.get("evidence_levels") != [EVIDENCE_LEVEL]:
        errors.append("report evidence_levels must be ['L1_static']")
    if report.get("l2_rows") != 0 or report.get("l3_live_rows") != 0:
        errors.append("M3 report must have zero L2 and L3 rows")

    freeze_path = resolve(base, str(report.get("freeze_record_path", "")))
    result_path = resolve(base, str(report.get("result_path", "")))
    if not freeze_path.exists():
        errors.append(f"missing freeze record at {freeze_path}")
    if not result_path.exists():
        errors.append(f"missing result rows at {result_path}")

    freeze: dict[str, Any] = {}
    if freeze_path.exists():
        freeze = load_json(freeze_path)
        errors.extend(f"{freeze_path}: {err}" for err in metadata_only_errors(freeze))
        if freeze.get("selection_split") != "validation":
            errors.append("selection_split must be validation")
        if freeze.get("test_scored_after_freeze") is not True:
            errors.append("freeze record must assert test_scored_after_freeze")
        if freeze.get("detector_config_hash") != report.get("detector_config_hash"):
            errors.append("detector_config_hash mismatch between freeze and report")

    corpus_hashes = {
        str(c.get("corpus_id")): str(c.get("manifest_sha256"))
        for c in report.get("corpora", [])
        if isinstance(c, dict)
    }
    validated_rows = 0
    l1_rows = 0
    if result_path.exists():
        with result_path.open(encoding="utf-8") as f:
            for lineno, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as exc:
                    errors.append(f"{result_path}:{lineno}: invalid JSON: {exc}")
                    continue
                if not isinstance(row, dict):
                    errors.append(f"{result_path}:{lineno}: row must be an object")
                    continue
                validated_rows += 1
                errors.extend(f"{result_path}:{lineno}: {err}" for err in metadata_only_errors(row))
                missing = REQUIRED_ROW_FIELDS - set(row)
                if missing:
                    errors.append(f"{result_path}:{lineno}: missing required fields {sorted(missing)}")
                if row.get("evidence_level") != EVIDENCE_LEVEL:
                    errors.append(f"{result_path}:{lineno}: M3 rows must use L1_static")
                else:
                    l1_rows += 1
                if row.get("selection_split") != "validation":
                    errors.append(f"{result_path}:{lineno}: selection_split must be validation")
                if "action_outcome" in row or "trace_path" in row:
                    errors.append(f"{result_path}:{lineno}: static row must not contain action outcome or trace")
                detection = row.get("detection")
                if not isinstance(detection, dict) or detection.get("verdict") not in {"flagged", "clean"}:
                    errors.append(f"{result_path}:{lineno}: detection verdict must be flagged or clean")
                payload_ref = row.get("payload_ref")
                if not isinstance(payload_ref, dict):
                    errors.append(f"{result_path}:{lineno}: payload_ref must be an object")
                else:
                    missing_ref = {"id", "family", "split", "corpus_manifest_hash"} - set(payload_ref)
                    if missing_ref:
                        errors.append(f"{result_path}:{lineno}: payload_ref missing {sorted(missing_ref)}")
                    expected_hash = corpus_hashes.get(str(row.get("corpus_id")))
                    if expected_hash and payload_ref.get("corpus_manifest_hash") != expected_hash:
                        errors.append(f"{result_path}:{lineno}: payload_ref corpus_manifest_hash mismatch")

    if validated_rows != report.get("row_count"):
        errors.append(f"row_count mismatch: report={report.get('row_count')} actual={validated_rows}")
    if l1_rows != report.get("l1_rows"):
        errors.append(f"l1_rows mismatch: report={report.get('l1_rows')} actual={l1_rows}")

    upper = report.get("hard_benign_fp_wilson_95", {}).get("upper")
    bar = report.get("hard_benign_fp_wilson_upper_bar")
    if isinstance(upper, (int, float)) and isinstance(bar, (int, float)):
        if upper > bar and not report.get("residual_analysis"):
            errors.append("hard-benign FP Wilson upper exceeds bar without residual analysis")
    else:
        errors.append("hard-benign FP Wilson upper/bar missing or non-numeric")

    summary = {
        "validated_rows": validated_rows,
        "l1_rows": l1_rows,
        "l2_rows": report.get("l2_rows"),
        "l3_live_rows": report.get("l3_live_rows"),
        "families_needing_l3_sampling": len(report.get("families_needing_l3_sampling", [])),
        "hard_benign_fp_wilson_upper": upper,
        "hard_benign_fp_wilson_upper_bar": bar,
        "errors": len(errors),
    }
    return errors, summary


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("report", type=Path)
    ap.add_argument(
        "--summary-out",
        type=Path,
        default=None,
        help="Optional explicit validation summary path. Defaults beside the report.",
    )
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    errors, summary = validate_report(args.report)
    if errors:
        print("FAIL", file=sys.stderr)
        for err in errors[:100]:
            print(f"- {err}", file=sys.stderr)
        if len(errors) > 100:
            print(f"- ... {len(errors) - 100} more errors", file=sys.stderr)
        return 1
    summary_path = args.summary_out or (args.report.parent / "validation_summary.json")
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
