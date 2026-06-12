#!/usr/bin/env python3
"""Validate the round-7 payload-derived reality-check intake.

Outputs are metadata-only: errors point at file, line, field, code, and a short
row hash, never the payload text itself.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import Any


REQUIRED_FIELDS = {
    "text",
    "technique",
    "attack_class",
    "harm_channel",
    "multi_turn",
    "turns",
    "origin",
    "origin_url",
    "license",
    "why_novel",
    "notes",
}
ALLOWED_LICENSES = {"Apache-2.0", "MIT"}
ALLOWED_HARM_CHANNELS = {"action", "leak", "output_bytes", "output_text", "unknown"}
ALLOWED_TURN_ROLES = {"assistant", "system", "tool", "user"}
SUMMARY_FORBIDDEN_KEYS = {"text", "prompt", "content", "raw_text", "turns", "origin_url"}

PLACEHOLDERS = [
    "[EMAIL]",
    "[SENDER_EMAIL]",
    "[PARTICIPANT_EMAIL]",
    "[ATTACKER_URL]",
    "[URL]",
    "[SECRET]",
    "[NEW_PASSWORD]",
    "[ATTACKER_IBAN]",
    "[IBAN]",
    "[CARD_OR_ACCOUNT_NUMBER]",
    "[PHONE_OR_NUMBER]",
    "[FILE_ID]",
    "[SUBJECT]",
    "[BODY]",
    "[EXFIL_TEXT]",
    "[START_TIME]",
    "[TITLE]",
    "[TARGET]",
    "[HARMFUL_GOAL]",
    "[HARMFUL_BEHAVIOR]",
    "[DISALLOWED_CONTENT_CATEGORY]",
    "[ILLEGAL_CONTENT_CATEGORY]",
    "[HARMFUL_SUBJECT]",
    "[TARGET_PREFIX]",
    "[PLACEHOLDER]",
    "[PLACEHOLDER_ARGS]",
    "[TOOL_NAME]",
    "[SECOND_TOOL]",
    "[USER]",
    "[MODEL]",
    "[INJECTED_TASK_INPUT]",
    "[TARGET_TASK_INPUT]",
    "[ATTACKER_USER]",
]

FORBIDDEN_PAYLOAD_PATTERNS = [
    ("raw_url_in_payload", re.compile(r"\bhttps?://[^\s<>\]\)\"']+", re.IGNORECASE)),
    (
        "email_in_payload",
        re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    ),
    (
        "secret_marker_in_payload",
        re.compile(
            r"AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}|"
            r"gh[pousr]_[A-Za-z0-9_]{20,}|"
            r"xox[baprs]-[A-Za-z0-9-]{10,}|"
            r"sk-[A-Za-z0-9_-]{16,}|"
            r"BEGIN (?:RSA |EC |OPENSSH |DSA |)PRIVATE KEY",
            re.IGNORECASE,
        ),
    ),
]


def stable_row_hash(row: Any) -> str:
    payload = json.dumps(row, sort_keys=True, ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def stable_line_hash(line: str) -> str:
    return hashlib.sha256(line.encode("utf-8")).hexdigest()[:16]


def public_field_name(field_name: str) -> str:
    if field_name == "text":
        return "payload"
    if field_name == "turns":
        return "payload_turns"
    if field_name == "origin_url":
        return "provenance_url"
    if field_name.startswith("turns["):
        return field_name.replace("turns", "payload_turns", 1).replace(".text", ".payload")
    return field_name


@dataclass
class ValidationResult:
    total_rows: int = 0
    files: Counter[str] = field(default_factory=Counter)
    by_license: Counter[str] = field(default_factory=Counter)
    by_attack_class: Counter[str] = field(default_factory=Counter)
    by_harm_channel: Counter[str] = field(default_factory=Counter)
    by_multi_turn: Counter[str] = field(default_factory=Counter)
    by_placeholder: Counter[str] = field(default_factory=Counter)
    rows_with_placeholder: int = 0
    errors: list[dict[str, Any]] = field(default_factory=list)

    def add_error(
        self,
        path: Path,
        line_number: int,
        code: str,
        *,
        field_name: str | None = None,
        row: Any | None = None,
        line: str | None = None,
    ) -> None:
        error: dict[str, Any] = {
            "file": path.name,
            "line": line_number,
            "code": code,
        }
        if field_name is not None:
            error["field"] = public_field_name(field_name)
        if row is not None:
            error["row_hash"] = stable_row_hash(row)
        elif line is not None:
            error["line_hash"] = stable_line_hash(line)
        self.errors.append(error)

    def to_summary(self) -> dict[str, Any]:
        summary = {
            "schema": "round7-reality-check-validation-summary-v1",
            "total_rows": self.total_rows,
            "files": dict(sorted(self.files.items())),
            "by_license": dict(sorted(self.by_license.items())),
            "by_attack_class": dict(sorted(self.by_attack_class.items())),
            "by_harm_channel": dict(sorted(self.by_harm_channel.items())),
            "by_multi_turn": dict(sorted(self.by_multi_turn.items())),
            "rows_with_placeholder": self.rows_with_placeholder,
            "by_placeholder": dict(sorted(self.by_placeholder.items())),
            "allowed_licenses": sorted(ALLOWED_LICENSES),
            "error_count": len(self.errors),
            "errors": self.errors[:50],
            "error_truncated": len(self.errors) > 50,
            "public_safe": len(self.errors) == 0,
        }
        encoded = json.dumps(summary, ensure_ascii=True)
        leaked_keys = [key for key in SUMMARY_FORBIDDEN_KEYS if f'"{key}"' in encoded]
        if leaked_keys:
            raise AssertionError(f"summary contains forbidden key(s): {leaked_keys}")
        return summary


def payload_texts(row: dict[str, Any]) -> list[tuple[str, str]]:
    texts = [("text", row.get("text", ""))]
    turns = row.get("turns")
    if isinstance(turns, list):
        for index, turn in enumerate(turns):
            if isinstance(turn, dict):
                texts.append((f"turns[{index}].text", turn.get("text", "")))
    return texts


def count_placeholders(result: ValidationResult, row: dict[str, Any]) -> None:
    found = False
    for _, text in payload_texts(row):
        if not isinstance(text, str):
            continue
        for placeholder in PLACEHOLDERS:
            count = text.count(placeholder)
            if count:
                result.by_placeholder[placeholder] += count
                found = True
    if found:
        result.rows_with_placeholder += 1


def validate_row(
    result: ValidationResult, path: Path, line_number: int, row: dict[str, Any]
) -> None:
    result.total_rows += 1
    result.files[path.name] += 1

    missing = REQUIRED_FIELDS - set(row)
    extra = set(row) - REQUIRED_FIELDS
    for field_name in sorted(missing):
        result.add_error(path, line_number, "missing_field", field_name=field_name, row=row)
    for field_name in sorted(extra):
        result.add_error(path, line_number, "unexpected_field", field_name=field_name, row=row)

    license_name = row.get("license")
    result.by_license[str(license_name)] += 1
    if license_name not in ALLOWED_LICENSES:
        result.add_error(path, line_number, "disallowed_license", field_name="license", row=row)

    harm_channel = row.get("harm_channel")
    result.by_harm_channel[str(harm_channel)] += 1
    if harm_channel not in ALLOWED_HARM_CHANNELS:
        result.add_error(path, line_number, "invalid_harm_channel", field_name="harm_channel", row=row)

    result.by_attack_class[str(row.get("attack_class"))] += 1
    multi_turn = row.get("multi_turn")
    result.by_multi_turn[str(multi_turn).lower()] += 1
    if not isinstance(multi_turn, bool):
        result.add_error(path, line_number, "invalid_multi_turn_type", field_name="multi_turn", row=row)

    for field_name in ("text", "technique", "attack_class", "origin", "origin_url", "why_novel", "notes"):
        if field_name in row and not isinstance(row[field_name], str):
            result.add_error(path, line_number, "invalid_string_field", field_name=field_name, row=row)
    if isinstance(row.get("text"), str) and not row["text"].strip():
        result.add_error(path, line_number, "empty_text", field_name="text", row=row)
    if isinstance(row.get("origin_url"), str) and not row["origin_url"].startswith(("http://", "https://")):
        result.add_error(path, line_number, "invalid_origin_url", field_name="origin_url", row=row)

    turns = row.get("turns")
    if multi_turn is True:
        if not isinstance(turns, list) or not turns:
            result.add_error(path, line_number, "invalid_turns_for_multi_turn", field_name="turns", row=row)
    elif multi_turn is False and turns is not None:
        result.add_error(path, line_number, "turns_present_for_single_turn", field_name="turns", row=row)

    if isinstance(turns, list):
        for index, turn in enumerate(turns):
            field_prefix = f"turns[{index}]"
            if not isinstance(turn, dict):
                result.add_error(path, line_number, "invalid_turn_object", field_name=field_prefix, row=row)
                continue
            if set(turn) != {"role", "text"}:
                result.add_error(path, line_number, "invalid_turn_fields", field_name=field_prefix, row=row)
            role = turn.get("role")
            if role not in ALLOWED_TURN_ROLES:
                result.add_error(path, line_number, "invalid_turn_role", field_name=f"{field_prefix}.role", row=row)
            if not isinstance(turn.get("text"), str) or not turn.get("text", "").strip():
                result.add_error(path, line_number, "invalid_turn_text", field_name=f"{field_prefix}.text", row=row)

    for field_name, text in payload_texts(row):
        if not isinstance(text, str):
            continue
        for code, pattern in FORBIDDEN_PAYLOAD_PATTERNS:
            if pattern.search(text):
                result.add_error(path, line_number, code, field_name=field_name, row=row)

    count_placeholders(result, row)


def validate_file(result: ValidationResult, path: Path) -> None:
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                result.add_error(path, line_number, "invalid_json", line=line)
                continue
            if not isinstance(row, dict):
                result.add_error(path, line_number, "row_not_object", line=line)
                continue
            validate_row(result, path, line_number, row)


def validate_directory(input_dir: Path) -> ValidationResult:
    result = ValidationResult()
    if not input_dir.exists() or not input_dir.is_dir():
        raise FileNotFoundError(f"input directory not found: {input_dir}")
    jsonl_files = sorted(input_dir.glob("*.jsonl"))
    if not jsonl_files:
        raise FileNotFoundError(f"no .jsonl files found in {input_dir}")
    for path in jsonl_files:
        validate_file(result, path)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("--summary", type=Path)
    args = parser.parse_args(argv)

    result = validate_directory(args.input_dir)
    summary = result.to_summary()
    if args.summary:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if result.errors:
        print(json.dumps(summary, indent=2, sort_keys=True), file=sys.stderr)
        return 1

    print(
        "PASS: validated "
        f"{summary['total_rows']} rows across {len(summary['files'])} files; "
        f"licenses={summary['by_license']}; "
        f"rows_with_placeholder={summary['rows_with_placeholder']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
