#!/usr/bin/env python3
"""Validate the public/open-source readiness package.

This is intentionally a narrow repository-packaging check. It does not validate
detector quality, rerun embeddings, or approve a release.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


REQUIRED_FILES = (
    "LICENSE",
    "README.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
    "CITATION.cff",
    "docs/CLAIMS-LEDGER.md",
    "docs/OPEN-SOURCE-READINESS.md",
    ".github/workflows/readiness.yml",
)

README_REQUIRED = (
    "synthetic research data",
    "not as proof of production safety or real-traffic performance",
    "optional, default-off",
    "What This Repo Does Not Claim",
    "validation on real traffic",
    "readiness for default blocking",
)

CLAIMS_REQUIRED = (
    'Say "optional/default-off signal"',
    'Say "not validated on real traffic"',
    'Say "not production safety evidence"',
)

SECURITY_REQUIRED = (
    "does not ship a production security control",
    "private vulnerability reporting",
    "avoid including secrets",
)

CONTRIBUTING_REQUIRED = (
    "Evidence Discipline",
    "Pull Request Checklist",
    "production-ready",
    "default blocking",
)

WORKFLOW_COMMAND = "python3 meta/harness/open-source-readiness/validate_open_source_readiness.py"

SECRET_PATTERNS = (
    ("aws-access-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("github-token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{16,}\b")),
    ("openai-token", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("private-key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
)

README_FORBIDDEN = (
    "production-ready",
    "ready for default blocking",
    "guarantees zero false positives",
    "certified detector",
)


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def read_text(root: Path, rel: str, result: ValidationResult) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        result.errors.append(f"missing required file: {rel}")
    except UnicodeDecodeError as exc:
        result.errors.append(f"{rel}: not valid UTF-8 ({exc})")
    return ""


def squash(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def require_snippets(rel: str, text: str, snippets: tuple[str, ...], result: ValidationResult) -> None:
    squashed = squash(text)
    squashed_lower = squashed.lower()
    for snippet in snippets:
        if snippet.lower() not in squashed_lower:
            result.errors.append(f"{rel}: missing required readiness wording: {snippet}")


def check_secret_markers(rel: str, text: str, result: ValidationResult) -> None:
    for name, pattern in SECRET_PATTERNS:
        if pattern.search(text):
            result.errors.append(f"{rel}: secret-like marker detected ({name})")


def check_readme(text: str, result: ValidationResult) -> None:
    require_snippets("README.md", text, README_REQUIRED, result)
    lowered = text.lower()
    for phrase in README_FORBIDDEN:
        if phrase in lowered:
            result.errors.append(f"README.md: forbidden overclaim wording found: {phrase}")


def check_license(text: str, result: ValidationResult) -> None:
    if "mit license" not in text.lower():
        result.errors.append("LICENSE: expected MIT license text")
    if "permission is hereby granted" not in text.lower():
        result.errors.append("LICENSE: expected standard MIT permission grant")


def check_citation(text: str, result: ValidationResult) -> None:
    lowered = text.lower()
    for snippet in ("cff-version:", "title:", "license: mit"):
        if snippet not in lowered:
            result.errors.append(f"CITATION.cff: missing {snippet}")


def check_open_source_readiness(text: str, result: ValidationResult) -> None:
    for rel in REQUIRED_FILES[:6]:
        if f"`{rel}`" not in text:
            result.errors.append(f"docs/OPEN-SOURCE-READINESS.md: missing package file reference: {rel}")
    if WORKFLOW_COMMAND not in text:
        result.errors.append("docs/OPEN-SOURCE-READINESS.md: missing readiness validator command")


def check_workflow(text: str, result: ValidationResult) -> None:
    if WORKFLOW_COMMAND not in text:
        result.errors.append(".github/workflows/readiness.yml: readiness validator is not wired")


def validate_repo(root: Path | str = ".") -> ValidationResult:
    root = Path(root)
    result = ValidationResult()

    contents: dict[str, str] = {}
    for rel in REQUIRED_FILES:
        contents[rel] = read_text(root, rel, result)

    for rel, text in contents.items():
        if text:
            check_secret_markers(rel, text, result)

    check_license(contents.get("LICENSE", ""), result)
    check_readme(contents.get("README.md", ""), result)
    require_snippets("CONTRIBUTING.md", contents.get("CONTRIBUTING.md", ""), CONTRIBUTING_REQUIRED, result)
    require_snippets("SECURITY.md", contents.get("SECURITY.md", ""), SECURITY_REQUIRED, result)
    require_snippets("docs/CLAIMS-LEDGER.md", contents.get("docs/CLAIMS-LEDGER.md", ""), CLAIMS_REQUIRED, result)
    check_citation(contents.get("CITATION.cff", ""), result)
    check_open_source_readiness(contents.get("docs/OPEN-SOURCE-READINESS.md", ""), result)
    check_workflow(contents.get(".github/workflows/readiness.yml", ""), result)

    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="repository root to validate")
    args = parser.parse_args(argv)

    result = validate_repo(Path(args.root))
    if result.ok:
        print(f"PASS open-source readiness root={args.root}")
        return 0

    for error in result.errors:
        print(f"ERROR {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
