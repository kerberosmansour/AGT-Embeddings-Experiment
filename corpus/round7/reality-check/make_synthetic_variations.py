#!/usr/bin/env python3
"""Generate benchmark-safe synthetic variants from licensed reality-check rows.

The source arm stays attributed and redacted. This script creates a separate
derived arm where placeholders are instantiated with reserved, non-live values.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path
from typing import Any


ALLOWED_LICENSES = {"Apache-2.0", "MIT"}
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


def stable_seed(text: str, variant: int, seed: int) -> int:
    digest = hashlib.sha256(f"{seed}:{variant}:{text}".encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def parent_hash(row: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(row, sort_keys=True, ensure_ascii=True).encode("utf-8")
    ).hexdigest()[:16]


def replacements(row: dict[str, Any], variant: int, seed: int) -> dict[str, str]:
    rng = random.Random(stable_seed(row["text"], variant, seed))
    n = rng.randint(1000, 9999)
    case = f"{variant + 1:02d}-{n}"
    disallowed_categories = [
        "cyber_abuse",
        "credential_theft",
        "privacy_invasion",
        "fraud",
        "unsafe_physical_harm",
    ]
    harmful_subjects = [
        "synthetic_controlled_substance",
        "synthetic_explosive_topic",
        "synthetic_weapon_topic",
    ]
    tools = ["send_email", "post_web_request", "create_calendar_event", "update_record"]

    return {
        "[EMAIL]": f"exfil.{case}@example.test",
        "[SENDER_EMAIL]": f"sender.{case}@example.test",
        "[PARTICIPANT_EMAIL]": f"participant.{case}@example.test",
        "[ATTACKER_URL]": f"https://collect-{case}.attacker.invalid/ingest",
        "[URL]": f"https://resource-{case}.example.invalid/item",
        "[SECRET]": f"sk-test-{case}-FAKE",
        "[NEW_PASSWORD]": f"TEST-PASSWORD-{case}",
        "[ATTACKER_IBAN]": f"GB00TEST00000000{n:04d}",
        "[IBAN]": f"GB00TEST11110000{n:04d}",
        "[CARD_OR_ACCOUNT_NUMBER]": f"411111111111{n:04d}",
        "[PHONE_OR_NUMBER]": f"+1555010{n:04d}",
        "[FILE_ID]": f"file_test_{case}",
        "[SUBJECT]": f"synthetic subject {case}",
        "[BODY]": f"synthetic body canary {case}",
        "[EXFIL_TEXT]": f"synthetic exfiltration canary {case}",
        "[START_TIME]": f"2030-05-{(n % 20) + 1:02d}T09:00:00Z",
        "[TITLE]": f"synthetic event {case}",
        "[TARGET]": f"synthetic target {case}",
        "[HARMFUL_GOAL]": (
            "SYNTHETIC_DISALLOWED_GOAL_"
            f"{rng.choice(disallowed_categories)}_{case}"
        ),
        "[HARMFUL_BEHAVIOR]": (
            "SYNTHETIC_DISALLOWED_BEHAVIOR_"
            f"{rng.choice(disallowed_categories)}_{case}"
        ),
        "[DISALLOWED_CONTENT_CATEGORY]": (
            f"SYNTHETIC_DISALLOWED_CATEGORY_{rng.choice(disallowed_categories)}"
        ),
        "[ILLEGAL_CONTENT_CATEGORY]": "SYNTHETIC_ILLEGAL_CONTENT_CATEGORY",
        "[HARMFUL_SUBJECT]": rng.choice(harmful_subjects),
        "[TARGET_PREFIX]": f"Synthetic target prefix {case}",
        "[PLACEHOLDER]": f"SYNTHETIC_PLACEHOLDER_{case}",
        "[PLACEHOLDER_ARGS]": f"{{'case_id': '{case}', 'canary': 'CANARY_{case}'}}",
        "[TOOL_NAME]": rng.choice(tools),
        "[SECOND_TOOL]": rng.choice(tools),
        "[USER]": f"Synthetic User {case}",
        "[MODEL]": f"Synthetic Model {case}",
        "[INJECTED_TASK_INPUT]": f"synthetic injected task input {case}",
        "[TARGET_TASK_INPUT]": f"synthetic target task input {case}",
        "[ATTACKER_USER]": f"synthetic-attacker-{case}",
    }


def apply_replacements(text: str, mapping: dict[str, str]) -> str:
    for placeholder in PLACEHOLDERS:
        text = text.replace(f"[{placeholder}]", placeholder)
    for placeholder, value in mapping.items():
        text = text.replace(placeholder, value)
    return text


def has_placeholder(row: dict[str, Any]) -> bool:
    texts = [row.get("text", "")]
    if row.get("turns") is not None:
        texts.extend(turn.get("text", "") for turn in row["turns"])
    return any(placeholder in text for text in texts for placeholder in PLACEHOLDERS)


def iter_rows(input_dir: Path):
    for path in sorted(input_dir.glob("*.jsonl")):
        with path.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if line.strip():
                    yield path, line_number, json.loads(line)


def make_variant(row: dict[str, Any], variant: int, seed: int) -> dict[str, Any]:
    mapping = replacements(row, variant, seed)
    out = dict(row)
    out["text"] = apply_replacements(row["text"], mapping)
    if row.get("turns") is not None:
        out["turns"] = [
            {**turn, "text": apply_replacements(turn["text"], mapping)}
            for turn in row["turns"]
        ]
    out["technique"] = f"{row['technique']}:synthetic-slot-fill"
    out["origin"] = f"synthetic variation of {row['origin']}"
    out["why_novel"] = (
        "Synthetic placeholder instantiation for benchmark surface-form quality; "
        "parent attack structure is unchanged."
    )
    out["notes"] = (
        f"synthetic_variation=true; variant={variant + 1}; "
        f"parent_hash={parent_hash(row)}; parent_origin={row['origin']}; "
        "reserved fake values only; no live endpoints, secrets, PII, or "
        "operational harmful instructions."
    )
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--variants-per-row", type=int, default=1)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--skip-disallowed-license", action="store_true")
    parser.add_argument(
        "--include-no-placeholder",
        action="store_true",
        help="Also copy rows with no recognized placeholders into the synthetic arm.",
    )
    args = parser.parse_args()

    if args.variants_per_row < 1:
        raise SystemExit("--variants-per-row must be at least 1")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with args.output.open("w", encoding="utf-8") as handle:
        for path, line_number, row in iter_rows(args.input_dir):
            license_name = row.get("license")
            if license_name not in ALLOWED_LICENSES:
                message = (
                    f"{path}:{line_number} has disallowed license {license_name!r}; "
                    f"allowed={sorted(ALLOWED_LICENSES)}"
                )
                if args.skip_disallowed_license:
                    continue
                raise SystemExit(message)
            if not args.include_no_placeholder and not has_placeholder(row):
                continue
            for variant in range(args.variants_per_row):
                out = make_variant(row, variant, args.seed)
                handle.write(json.dumps(out, ensure_ascii=True) + "\n")
                written += 1

    print(f"wrote {written} synthetic rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
