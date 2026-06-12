#!/usr/bin/env python3
"""BDD tests for the open-source readiness validator."""

from __future__ import annotations

import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
VALIDATOR = ROOT / "meta/harness/open-source-readiness/validate_open_source_readiness.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_open_source_readiness", VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load validator spec")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class ReadinessValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="readiness-validator-"))
        self.addCleanup(lambda: shutil.rmtree(self.tmp))
        self._write_valid_repo(self.tmp)

    def _write_valid_repo(self, root: Path) -> None:
        write(root / "LICENSE", "MIT License\n\nPermission is hereby granted.\n")
        write(
            root / "README.md",
            """# AGT Embeddings Experiment

The dataset is synthetic research data, not as proof of production safety or
real-traffic performance.

The embedding signal is optional, default-off, additive, and auditable.

## What This Repo Does Not Claim

- production safety, certification, or benchmark-coverage claims;
- validation on real traffic;
- readiness for default blocking.
""",
        )
        write(
            root / "CONTRIBUTING.md",
            """# Contributing

## Out Of Scope

Claims that the embedding layer is production-ready. Changes that make
embeddings a default blocking path.

## Evidence Discipline

Claims remain optional, default-off, additive, and research-only. Do not include
raw secrets, live credentials, customer data, or private prompts.

## Pull Request Checklist

- Claims remain scoped.
""",
        )
        write(
            root / "CODE_OF_CONDUCT.md",
            """# Code Of Conduct

Do not publish private data, credentials, or sensitive reports.
""",
        )
        write(
            root / "SECURITY.md",
            """# Security Policy

This repository does not ship a production security control.

Use GitHub private vulnerability reporting if it is enabled. Avoid including
secrets, private prompts, or raw sensitive data.
""",
        )
        write(
            root / "CITATION.cff",
            """cff-version: 1.2.0
title: "AGT Embeddings Experiment"
license: MIT
""",
        )
        write(
            root / "docs/CLAIMS-LEDGER.md",
            """# Claims Ledger

- Say "optional/default-off signal" rather than "replacement detector."
- Say "not validated on real traffic" until that evidence exists.
- Say "not production safety evidence" until separate deployment evidence exists.
""",
        )
        write(
            root / "docs/OPEN-SOURCE-READINESS.md",
            """# Open Source Readiness

- `LICENSE`
- `README.md`
- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `SECURITY.md`
- `CITATION.cff`

python3 meta/harness/open-source-readiness/validate_open_source_readiness.py
""",
        )
        write(
            root / ".github/workflows/readiness.yml",
            """name: readiness
jobs:
  public-repo-readiness:
    steps:
      - name: Validate open-source readiness
        run: python3 meta/harness/open-source-readiness/validate_open_source_readiness.py
""",
        )

    def test_valid_fixture_passes(self) -> None:
        validator = load_validator()
        result = validator.validate_repo(self.tmp)
        self.assertEqual([], result.errors)

    def test_missing_required_file_fails(self) -> None:
        validator = load_validator()
        (self.tmp / "SECURITY.md").unlink()
        result = validator.validate_repo(self.tmp)
        self.assertTrue(any("missing required file: SECURITY.md" in err for err in result.errors))

    def test_readme_overclaim_fails(self) -> None:
        validator = load_validator()
        readme = self.tmp / "README.md"
        readme.write_text(
            readme.read_text(encoding="utf-8")
            + "\nThis detector is production-ready and is ready for default blocking.\n",
            encoding="utf-8",
        )
        result = validator.validate_repo(self.tmp)
        self.assertTrue(any("README.md" in err and "production-ready" in err for err in result.errors))
        self.assertTrue(
            any("README.md" in err and "ready for default blocking" in err for err in result.errors)
        )

    def test_secret_marker_fails(self) -> None:
        validator = load_validator()
        (self.tmp / "CONTRIBUTING.md").write_text("accidental token ghp_abcdefghijklmnop\n", encoding="utf-8")
        result = validator.validate_repo(self.tmp)
        self.assertTrue(any("secret-like marker" in err for err in result.errors))


if __name__ == "__main__":
    unittest.main()
