#!/usr/bin/env python3
"""Focused tests for the Round-7 ceiling artifact validator."""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
VALIDATOR = HERE / "validate_round7_ceiling.py"
STEPS = (
    "00_baseline_fixed_recb",
    "01_r1_prime_intent_gate",
    "02_hard_benign_guard",
    "03_round7_in_domain_training",
    "04_tool_output_authority_boundary",
    "05_output_stage_leakage_scan",
    "06_package_provenance_verifier",
    "07_terminal_escape_sanitizer",
)


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_round7_ceiling", VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load validator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def metric():
    return {
        "tp": 1,
        "fn": 0,
        "fp": 0,
        "tn": 1,
        "attack_total": 1,
        "benign_total": 1,
        "attack_recall": 1.0,
        "benign_fp_rate": 0.0,
    }


class CeilingValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="round7-ceiling-"))
        self.addCleanup(lambda: shutil.rmtree(self.tmp))
        self.validator = load_validator()
        self._write_valid_fixture()

    def _write_valid_fixture(self) -> None:
        root = self.tmp / "artifacts/round7-garak/ceiling-pilot"
        steps = {
            step: {
                "metrics": metric(),
                "delta_from_previous": {},
                "false_positive_attribution": {},
            }
            for step in STEPS
        }
        recommendations = [{"step_id": step, "next_action": "next"} for step in STEPS[1:]]
        write_json(root / "metrics.json", {"schema": "round7-ceiling-metrics-v1", "step_order": list(STEPS), "steps": steps})
        write_jsonl(
            root / "test-per-row.jsonl",
            [
                {
                    "row_id": "r7-test",
                    "row_sha256": "abc",
                    "label": "attack",
                    "scores": {},
                    "controls": {},
                    "steps": {step: True for step in STEPS},
                }
            ],
        )
        write_json(
            root / "manifest.json",
            {
                "schema": "round7-ceiling-experiment-v1",
                "normalizer_id": "agt_rust_round7",
                "detector_contract": {
                    "selection_split": "validation",
                    "test_scored_once_after_freeze": True,
                    "step_order": list(STEPS),
                },
                "metrics_path": "artifacts/round7-garak/ceiling-pilot/metrics.json",
                "test_per_row_path": "artifacts/round7-garak/ceiling-pilot/test-per-row.jsonl",
                "recommendations": recommendations,
            },
        )

    def with_tmp_root(self):
        old_root = self.validator.ROOT
        self.validator.ROOT = self.tmp
        self.addCleanup(lambda: setattr(self.validator, "ROOT", old_root))

    def test_valid_fixture_passes(self) -> None:
        self.with_tmp_root()
        errors = self.validator.validate_manifest(self.tmp / "artifacts/round7-garak/ceiling-pilot/manifest.json")
        self.assertEqual([], errors)

    def test_raw_text_field_fails(self) -> None:
        self.with_tmp_root()
        write_jsonl(
            self.tmp / "artifacts/round7-garak/ceiling-pilot/test-per-row.jsonl",
            [{"row_id": "x", "row_sha256": "abc", "label": "benign", "scores": {}, "controls": {}, "steps": {step: False for step in STEPS}, "text": "raw"}],
        )
        errors = self.validator.validate_manifest(self.tmp / "artifacts/round7-garak/ceiling-pilot/manifest.json")
        self.assertTrue(any("forbidden raw-text-like field" in err for err in errors))

    def test_missing_step_fails(self) -> None:
        self.with_tmp_root()
        metrics_path = self.tmp / "artifacts/round7-garak/ceiling-pilot/metrics.json"
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        metrics["step_order"] = list(STEPS[:-1])
        write_json(metrics_path, metrics)
        errors = self.validator.validate_manifest(self.tmp / "artifacts/round7-garak/ceiling-pilot/manifest.json")
        self.assertTrue(any("wrong step_order" in err for err in errors))

    def test_missing_recommendation_fails(self) -> None:
        self.with_tmp_root()
        manifest_path = self.tmp / "artifacts/round7-garak/ceiling-pilot/manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["recommendations"] = []
        write_json(manifest_path, manifest)
        errors = self.validator.validate_manifest(manifest_path)
        self.assertTrue(any("missing recommendation steps" in err for err in errors))


if __name__ == "__main__":
    unittest.main()
