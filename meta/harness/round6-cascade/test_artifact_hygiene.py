#!/usr/bin/env python3
"""Artifact-hygiene tests: metadata-only outputs + ground-truth exclusion
+ closed transform-tag enum (F-SEC-2)."""

import json
import unittest
from pathlib import Path

import common as C
from normalize import TAGS

ART = C.ROOT / "artifacts/round6-cascade"
FORBIDDEN = C.FORBIDDEN_OUTPUT_FIELDS
GROUND_TRUTH = C.GROUND_TRUTH_FIELDS


def all_artifact_files():
    if not ART.exists():
        return []
    return [p for p in ART.rglob("*") if p.suffix in (".json", ".jsonl")]


class TestNoRawText(unittest.TestCase):
    def test_no_forbidden_fields(self):
        for p in all_artifact_files():
            for ln in p.read_text().splitlines():
                ln = ln.strip().rstrip(",")
                if not ln or ln[0] not in "{[":
                    continue
                try:
                    obj = json.loads(ln)
                except json.JSONDecodeError:
                    continue
                errs = C.ensure_metadata_only(obj)
                self.assertEqual(errs, [], f"{p}: {errs[:2]}")

    def test_no_ground_truth_in_per_row(self):
        # expected_action / risk_level must never appear as per-row feature keys.
        for p in ART.rglob("*-per-row.jsonl"):
            for ln in p.read_text().splitlines():
                if not ln.strip():
                    continue
                obj = json.loads(ln)
                leaked = set(obj.keys()) & GROUND_TRUTH
                self.assertEqual(leaked, set(), f"{p}: ground-truth leaked {leaked}")


class TestTagEnum(unittest.TestCase):
    def test_transform_tags_closed(self):
        for p in ART.rglob("*-per-row.jsonl"):
            for ln in p.read_text().splitlines():
                if not ln.strip():
                    continue
                obj = json.loads(ln)
                for t in obj.get("transform_tags", []):
                    self.assertIn(t, TAGS, f"{p}: tag '{t}' outside closed enum")


class TestFeatureExclusionAssertion(unittest.TestCase):
    def test_ground_truth_constant(self):
        # The exclusion set the harness enforces must contain both fields.
        self.assertIn("expected_action", GROUND_TRUTH)
        self.assertIn("risk_level", GROUND_TRUTH)


if __name__ == "__main__":
    unittest.main(verbosity=2)
