#!/usr/bin/env python3
"""Validate the Phase 5 AGT embeddings migration closeout package."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


REQUIRED_PATHS = (
    "README.md",
    "docs/CLAIMS-LEDGER.md",
    "docs/RUNBOOK-agt-embeddings-migration.md",
    "docs/AGENTBUS-WORKSPLIT.md",
    "docs/OPEN-SOURCE-READINESS.md",
    "docs/UPSTREAM-PR-PLAN.md",
    "corpus/round4/manifest-large.json",
    "corpus/round4/check-round4.py",
    "tools/agt-rules-baseline/Cargo.toml",
    "tools/agt-rules-baseline/vendor/agent-governance-toolkit/prompt_injection.rs",
    "artifacts/embedding-sweep/freeze-record.json",
    "artifacts/embedding-sweep/test-metrics.json",
    "artifacts/governance-eval/manifest.json",
    "artifacts/governance-eval/metrics.json",
    "artifacts/source-scale-pilot/summary.json",
    "meta/harness/round4-embedding-sweep/validate-embedding-sweep.py",
    "meta/harness/round4-governance-eval/validate-governance-eval.py",
)

CLAIMS_REQUIRED = (
    "AGT rules-only detector has low recall on the hard held-out set.",
    "The evaluation corpus has 44,800 labelled examples.",
    "Embedding/kNN at Youden's J catches about 88% on frozen test.",
    "Embedding/kNN at Youden's J has about 16% false positives.",
    "Conservative embedding point has zero observed false positives.",
    "Embeddings should augment AGT policy, not replace it.",
    "Round 5 improves methodology for source-reviewed fixture generation.",
    'Say "optional/default-off signal"',
    'Say "not validated on real traffic"',
    'Say "not production safety evidence"',
)

RUNBOOK_REQUIRED = (
    "M4 replacement gates PASS",
    "M0-M3 migrated and audited",
    "M1 AGT corpus and rules baseline migration",
    "M2 Embedding/kNN evidence migration",
    "M3 Governance/value-add evidence migration",
    "M4 Narrative packaging and review",
)

WORKSPLIT_REQUIRED = (
    "Linux M1 audit PASS",
    "Windows vendored-source readback PASS",
    "Linux M2 audit PASS",
    "Windows formal M2 readback PASS",
    "Linux M3 audit PASS",
    "Replacement public-scope/no-overclaim gate PASS",
    "Replacement AGT semantics/native-vocabulary gate PASS",
)

README_REQUIRED = (
    "synthetic research data",
    "optional, default-off",
    "What This Repo Does Not Claim",
    "validation on real traffic",
    "readiness for default blocking",
)

FORBIDDEN_OVERCLAIMS = (
    "guarantees zero false positives",
    "production-ready detector",
    "certified detector",
    "has been validated on real traffic",
    "is validated on real traffic",
)


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def squash(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def read_text(root: Path, rel: str, result: ValidationResult) -> str:
    path = root / rel
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        result.errors.append(f"missing required migration path: {rel}")
    except UnicodeDecodeError as exc:
        result.errors.append(f"{rel}: not valid UTF-8 ({exc})")
    return ""


def require_snippets(rel: str, text: str, snippets: tuple[str, ...], result: ValidationResult) -> None:
    squashed = squash(text).lower()
    for snippet in snippets:
        if snippet.lower() not in squashed:
            result.errors.append(f"{rel}: missing required claim mapping or gate wording: {snippet}")


def check_overclaims(rel: str, text: str, result: ValidationResult) -> None:
    lowered = text.lower()
    for phrase in FORBIDDEN_OVERCLAIMS:
        if phrase in lowered:
            result.errors.append(f"{rel}: forbidden overclaim wording found: {phrase}")


def validate_repo(root: Path | str = ".") -> ValidationResult:
    root = Path(root)
    result = ValidationResult()

    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            result.errors.append(f"missing required migration path: {rel}")

    readme = read_text(root, "README.md", result)
    claims = read_text(root, "docs/CLAIMS-LEDGER.md", result)
    runbook = read_text(root, "docs/RUNBOOK-agt-embeddings-migration.md", result)
    worksplit = read_text(root, "docs/AGENTBUS-WORKSPLIT.md", result)

    require_snippets("README.md", readme, README_REQUIRED, result)
    require_snippets("docs/CLAIMS-LEDGER.md", claims, CLAIMS_REQUIRED, result)
    require_snippets("docs/RUNBOOK-agt-embeddings-migration.md", runbook, RUNBOOK_REQUIRED, result)
    require_snippets("docs/AGENTBUS-WORKSPLIT.md", worksplit, WORKSPLIT_REQUIRED, result)

    for rel, text in (
        ("README.md", readme),
        ("docs/CLAIMS-LEDGER.md", claims),
        ("docs/RUNBOOK-agt-embeddings-migration.md", runbook),
        ("docs/AGENTBUS-WORKSPLIT.md", worksplit),
    ):
        check_overclaims(rel, text, result)

    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="repository root to validate")
    args = parser.parse_args(argv)

    result = validate_repo(Path(args.root))
    if result.ok:
        print(f"PASS migration closeout root={args.root}")
        return 0

    for error in result.errors:
        print(f"ERROR {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
