#!/usr/bin/env python3
"""Focused tests for the Round-7 Rec B artifact validator."""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
VALIDATOR = HERE / "validate_round7_recb.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_round7_recb", VALIDATOR)
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


def metric(tp=1, fn=0, fp=0, tn=1):
    return {
        "tp": tp,
        "fn": fn,
        "fp": fp,
        "tn": tn,
        "attack_total": tp + fn,
        "benign_total": fp + tn,
        "attack_recall": tp / max(1, tp + fn),
        "benign_fp_rate": fp / max(1, fp + tn),
    }


class Round7RecBValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="round7-recb-"))
        self.addCleanup(lambda: shutil.rmtree(self.tmp))
        self.validator = load_validator()
        self._write_valid_fixture()

    def _write_valid_fixture(self) -> None:
        recommendations = [
            {"control_id": "r1-prime-intent-gated-tool-control"},
            {"control_id": "terminal-escape-output-sanitizer"},
            {"control_id": "outbound-sensitive-output-scan"},
            {"control_id": "package-provenance-verifier"},
            {"control_id": "round7-hard-benign-expansion"},
        ]
        arms = []
        for arm in ("fixed_round4_bank", "round7_in_domain_bank"):
            arm_root = self.tmp / "artifacts/round7-garak/recb-pilot/arms" / arm
            freeze_rel = f"artifacts/round7-garak/recb-pilot/arms/{arm}/freeze-record.json"
            metrics_rel = f"artifacts/round7-garak/recb-pilot/arms/{arm}/metrics.json"
            rows_rel = f"artifacts/round7-garak/recb-pilot/arms/{arm}/test-per-row.jsonl"
            write_json(
                arm_root / "freeze-record.json",
                {
                    "schema": "round7-recb-freeze-record-v1",
                    "arm": arm,
                    "selection_split": "validation",
                    "normalizer_id": "agt_rust_round7",
                    "test_scored_once_after_freeze": True,
                },
            )
            write_json(
                arm_root / "metrics.json",
                {
                    "schema": "round7-recb-arm-metrics-v1",
                    "test": {
                        "knn_zero_fp": metric(),
                        "r1_legacy_untrusted_tool": metric(),
                        "recb_head_in_band": metric(),
                        "coequal_head_everywhere": metric(),
                    },
                    "test_breakdowns_for_recb": {
                        "attack_class": {},
                        "bypass_class": {},
                        "benign_subclass": {},
                    },
                },
            )
            write_jsonl(
                arm_root / "test-per-row.jsonl",
                [
                    {
                        "row_id": "r7-test",
                        "row_sha256": "abc",
                        "label": "attack",
                        "scores": {"knn_margin": 0.1, "head_score": 0.9},
                        "decisions": {"recb_head_in_band": True},
                    }
                ],
            )
            arms.append({"arm": arm, "freeze_record_path": freeze_rel, "metrics_path": metrics_rel, "test_per_row_path": rows_rel})

        write_json(
            self.tmp / "artifacts/round7-garak/recb-pilot/metrics.json",
            {"schema": "round7-recb-metrics-v1", "arms": {}, "recommendations": recommendations},
        )
        write_json(
            self.tmp / "artifacts/round7-garak/recb-pilot/manifest.json",
            {
                "schema": "round7-recb-experiment-v1",
                "normalizer_id": "agt_rust_round7",
                "detector_contract": {"selection_split": "validation"},
                "arms": arms,
                "metrics_path": "artifacts/round7-garak/recb-pilot/metrics.json",
                "recommendations": recommendations,
            },
        )

    def test_valid_fixture_passes(self) -> None:
        old_root = self.validator.ROOT
        self.validator.ROOT = self.tmp
        self.addCleanup(lambda: setattr(self.validator, "ROOT", old_root))
        errors = self.validator.validate_manifest(self.tmp / "artifacts/round7-garak/recb-pilot/manifest.json")
        self.assertEqual([], errors)

    def test_raw_text_field_fails(self) -> None:
        old_root = self.validator.ROOT
        self.validator.ROOT = self.tmp
        self.addCleanup(lambda: setattr(self.validator, "ROOT", old_root))
        row_path = self.tmp / "artifacts/round7-garak/recb-pilot/arms/fixed_round4_bank/test-per-row.jsonl"
        write_jsonl(row_path, [{"row_id": "x", "row_sha256": "abc", "label": "benign", "scores": {}, "decisions": {}, "text": "raw"}])
        errors = self.validator.validate_manifest(self.tmp / "artifacts/round7-garak/recb-pilot/manifest.json")
        self.assertTrue(any("forbidden raw-text-like field" in err for err in errors))

    def test_missing_arm_fails(self) -> None:
        old_root = self.validator.ROOT
        self.validator.ROOT = self.tmp
        self.addCleanup(lambda: setattr(self.validator, "ROOT", old_root))
        manifest_path = self.tmp / "artifacts/round7-garak/recb-pilot/manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["arms"] = manifest["arms"][:1]
        write_json(manifest_path, manifest)
        errors = self.validator.validate_manifest(manifest_path)
        self.assertTrue(any("missing required arms" in err for err in errors))

    def test_missing_recommendation_fails(self) -> None:
        old_root = self.validator.ROOT
        self.validator.ROOT = self.tmp
        self.addCleanup(lambda: setattr(self.validator, "ROOT", old_root))
        manifest_path = self.tmp / "artifacts/round7-garak/recb-pilot/manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["recommendations"] = []
        write_json(manifest_path, manifest)
        errors = self.validator.validate_manifest(manifest_path)
        self.assertTrue(any("missing controls" in err for err in errors))


if __name__ == "__main__":
    unittest.main()
