#!/usr/bin/env python3
"""Artifact hygiene + ground-truth exclusion tests for Experiment 1."""

import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "meta/harness/round6-cascade"))
import common as C  # noqa: E402
import rules as RU  # noqa: E402

ART = ROOT / "artifacts/exp1-structural"
FORBIDDEN = C.FORBIDDEN_OUTPUT_FIELDS
GROUND_TRUTH = {"expected_action", "risk_level"}


class TestHygiene(unittest.TestCase):
    def test_rule_fields_exclude_ground_truth(self):
        self.assertEqual(RU.ALLOWED_FIELDS & GROUND_TRUTH, set())

    def test_artifacts_metadata_only(self):
        if not ART.exists():
            self.skipTest("exp1 artifacts not present")
        for p in ART.rglob("*"):
            if p.suffix not in (".json", ".jsonl"):
                continue
            for ln in p.read_text().splitlines():
                ln = ln.strip().rstrip(",")
                if not ln or ln[0] not in "{[":
                    continue
                try:
                    obj = json.loads(ln)
                except json.JSONDecodeError:
                    continue
                self.assertEqual(C.ensure_metadata_only(obj), [], f"{p}")

    def test_per_row_no_ground_truth(self):
        f = ART / "test-per-row.jsonl"
        if not f.exists():
            self.skipTest("not present")
        for ln in f.read_text().splitlines():
            if ln.strip():
                obj = json.loads(ln)
                self.assertEqual(set(obj) & GROUND_TRUTH, set())


if __name__ == "__main__":
    unittest.main(verbosity=2)
