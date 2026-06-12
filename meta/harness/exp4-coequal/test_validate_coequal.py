#!/usr/bin/env python3
"""Focused tests for the exp4 co-equal artifact validator."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
VALIDATOR = HERE / "validate_coequal.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_coequal", VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {VALIDATOR}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestExp4CoequalValidator(unittest.TestCase):
    def setUp(self) -> None:
        self.mod = load_validator()
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.write_valid_fixture()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write_json(self, name: str, value: object) -> None:
        (self.root / name).write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")

    def write_rows(self, rows: list[dict]) -> None:
        with (self.root / "test-per-row.jsonl").open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, sort_keys=True) + "\n")

    def rows(self) -> list[dict]:
        return [
            {
                "id": "a1",
                "label": "attack",
                "attack_class": "direct_override",
                "knn_flag": True,
                "head_flag": False,
                "r1_flag": False,
                "combined": True,
            },
            {
                "id": "a2",
                "label": "attack",
                "attack_class": "prompt_leakage",
                "knn_flag": False,
                "head_flag": False,
                "r1_flag": False,
                "combined": False,
            },
            {
                "id": "b1",
                "label": "benign",
                "attack_class": "benign",
                "knn_flag": False,
                "head_flag": False,
                "r1_flag": False,
                "combined": False,
            },
            {
                "id": "b2",
                "label": "benign",
                "attack_class": "benign",
                "knn_flag": False,
                "head_flag": False,
                "r1_flag": False,
                "combined": False,
            },
        ]

    def write_valid_fixture(self) -> None:
        self.write_json(
            "freeze-record.json",
            {
                "selected_on": "validation",
                "knn_zerofp": 0.1,
                "head_zerofp_strict": 0.9,
                "head_0p1pct_val_fpr": 0.8,
                "rule": "block if validation-frozen inspectors fire",
            },
        )
        self.write_json(
            "test-metrics.json",
            {
                "selected_on": "validation",
                "test_combined_recall_strict": 0.5,
                "test_combined_fp_strict": 0.0,
                "test_combined_recall_0p1pct": 0.5,
                "test_combined_fp_0p1pct": 0.0,
                "by_control_recall": {"knn_zerofp": 0.5, "head_zerofp": 0.0, "R1": 0.0},
                "per_family_recall_strict": {"direct_override": 1.0, "prompt_leakage": 0.0},
                "compare": {"exp3_rec_B_validation_frozen": 0.872, "exp3_test_derived_ceiling": 0.925},
            },
        )
        self.write_json(
            "newnorm-metrics.json",
            {
                "normalizer": "extended (#10)",
                "selected_on": "validation",
                "knn_zerofp": 0.2,
                "head_0p1pct_val_fpr_cut": 0.7,
                "test_combined_recall": 0.6,
                "test_combined_fp": 0.0,
                "old_normalizer_ensemble": 0.5,
                "per_family_recall": {"direct_override": 1.0},
            },
        )
        self.write_rows(self.rows())

    def test_valid_fixture_passes(self) -> None:
        self.assertEqual(self.mod.validate_artifact_dir(self.root), [])

    def test_test_selected_freeze_fails(self) -> None:
        freeze = json.loads((self.root / "freeze-record.json").read_text(encoding="utf-8"))
        freeze["selected_on"] = "test"
        self.write_json("freeze-record.json", freeze)
        errors = self.mod.validate_artifact_dir(self.root)
        self.assertTrue(any("selected_on" in err for err in errors), errors)

    def test_raw_text_field_fails(self) -> None:
        rows = self.rows()
        rows[0]["text"] = "do not echo this"
        self.write_rows(rows)
        errors = self.mod.validate_artifact_dir(self.root)
        self.assertTrue(any("raw-text-like field" in err for err in errors), errors)

    def test_metric_drift_fails(self) -> None:
        metrics = json.loads((self.root / "test-metrics.json").read_text(encoding="utf-8"))
        metrics["test_combined_recall_strict"] = 1.0
        self.write_json("test-metrics.json", metrics)
        errors = self.mod.validate_artifact_dir(self.root)
        self.assertTrue(any("test_combined_recall_strict" in err for err in errors), errors)


if __name__ == "__main__":
    unittest.main(verbosity=2)
