#!/usr/bin/env python3
"""BDD tests for the migration closeout validator."""

from __future__ import annotations

import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
VALIDATOR = ROOT / "meta/harness/migration-closeout/validate_migration_closeout.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_migration_closeout", VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load validator spec")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class MigrationCloseoutValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="migration-closeout-"))
        self.addCleanup(lambda: shutil.rmtree(self.tmp))
        self._write_valid_repo(self.tmp)

    def _write_valid_repo(self, root: Path) -> None:
        required_files = [
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
        ]
        for rel in required_files:
            write(root / rel, "{}\n" if rel.endswith(".json") else "# placeholder\n")

        write(
            root / "README.md",
            """# AGT Embeddings Experiment

The dataset is synthetic research data. The embedding signal is optional,
default-off, additive, and auditable. This repo does not claim production
safety, certification, benchmark coverage, validation on real traffic, or
readiness for default blocking.

## What This Repo Does Not Claim
""",
        )
        write(
            root / "docs/RUNBOOK-agt-embeddings-migration.md",
            """# RUNBOOK: AGT Embeddings Migration

Status: M4 replacement gates PASS; M0-M3 migrated and audited; final packaging/readiness coordination next.

M1 AGT corpus and rules baseline migration
M2 Embedding/kNN evidence migration
M3 Governance/value-add evidence migration
M4 Narrative packaging and review
""",
        )
        write(
            root / "docs/AGENTBUS-WORKSPLIT.md",
            """# AgentBus Work Split

Linux M1 audit PASS
Windows vendored-source readback PASS
Linux M2 audit PASS
Windows formal M2 readback PASS
Linux M3 audit PASS
Replacement public-scope/no-overclaim gate PASS
Replacement AGT semantics/native-vocabulary gate PASS
""",
        )
        write(
            root / "docs/CLAIMS-LEDGER.md",
            """# Claims Ledger

AGT rules-only detector has low recall on the hard held-out set.
The evaluation corpus has 44,800 labelled examples.
Embedding/kNN at Youden's J catches about 88% on frozen test.
Embedding/kNN at Youden's J has about 16% false positives.
Conservative embedding point has zero observed false positives.
Embeddings should augment AGT policy, not replace it.
Round 5 improves methodology for source-reviewed fixture generation.
Say "optional/default-off signal" rather than "replacement detector."
Say "not validated on real traffic" until that evidence exists.
Say "not production safety evidence" until separate deployment evidence exists.
""",
        )

    def test_valid_fixture_passes(self) -> None:
        validator = load_validator()
        result = validator.validate_repo(self.tmp)
        self.assertEqual([], result.errors)

    def test_missing_artifact_fails(self) -> None:
        validator = load_validator()
        (self.tmp / "artifacts/embedding-sweep/freeze-record.json").unlink()
        result = validator.validate_repo(self.tmp)
        self.assertTrue(
            any("missing required migration path: artifacts/embedding-sweep/freeze-record.json" in err for err in result.errors)
        )

    def test_missing_claim_mapping_fails(self) -> None:
        validator = load_validator()
        ledger = self.tmp / "docs/CLAIMS-LEDGER.md"
        ledger.write_text("AGT rules-only detector has low recall on the hard held-out set.\n", encoding="utf-8")
        result = validator.validate_repo(self.tmp)
        self.assertTrue(any("missing required claim mapping" in err for err in result.errors))

    def test_overclaim_fails(self) -> None:
        validator = load_validator()
        readme = self.tmp / "README.md"
        readme.write_text(readme.read_text(encoding="utf-8") + "\nThis guarantees zero false positives.\n", encoding="utf-8")
        result = validator.validate_repo(self.tmp)
        self.assertTrue(any("forbidden overclaim" in err for err in result.errors))


if __name__ == "__main__":
    unittest.main()
