"""Measurement-suite v2 tests for the AGT red-team benchmark.

The smoke suite stays 24 rows. The measurement suite is larger by design:
6 trap classes x 40 rows, split into canonical positives, evasion positives,
hard-benign negatives, and near-miss negatives. These tests are intentionally
about measurement power, not a certification claim.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
BENCH = HERE.parent
MEASUREMENT_SCENARIOS = BENCH / "measurement" / "scenarios"
VALIDATOR = BENCH / "schema" / "validate_scenarios.py"
REPORTERS = BENCH / "reporters"
SCORECARD = REPORTERS / "scorecard.py"
CONTROLS = BENCH / "controls" / "agt-ac.csv"

sys.path.insert(0, str(BENCH / "schema"))
import validate_scenarios as vs  # noqa: E402

TRAP_CLASSES = {
    "Content Injection", "Semantic Manipulation", "Cognitive State",
    "Behavioural Control", "Systemic", "Human-in-the-Loop",
}
SCENARIO_KINDS = {
    "canonical_positive", "evasion_positive", "hard_benign", "near_miss",
}
EXPECTED_PER_CLASS = {
    "canonical_positive": 8,
    "evasion_positive": 16,
    "hard_benign": 8,
    "near_miss": 8,
}


def measurement_paths():
    return sorted(MEASUREMENT_SCENARIOS.glob("*.json"))


def load_measurement():
    return [json.loads(p.read_text(encoding="utf-8")) for p in measurement_paths()]


def run_validator(*paths):
    return subprocess.run(
        [sys.executable, str(VALIDATOR), *map(str, paths)],
        capture_output=True, text=True,
    )


def run_scorecard(out_dir):
    return subprocess.run(
        [sys.executable, str(SCORECARD), "--controls", str(CONTROLS),
         "--from-scenarios", str(MEASUREMENT_SCENARIOS), "--out", str(out_dir)],
        capture_output=True, text=True,
    )


class MeasurementCorpusShape(unittest.TestCase):
    """oc-agtrt-v2-1: the 240-row corpus has enough denominators to measure."""

    def test_240_rows_and_balanced_classes(self):
        scenarios = load_measurement()
        self.assertEqual(len(scenarios), 240)
        by_class = Counter(s["trap_class"] for s in scenarios)
        self.assertEqual(set(by_class), TRAP_CLASSES)
        self.assertTrue(all(n == 40 for n in by_class.values()), by_class)

    def test_each_class_has_goldilocks_kind_distribution(self):
        by_class_kind = defaultdict(Counter)
        for scenario in load_measurement():
            by_class_kind[scenario["trap_class"]][scenario["scenario_kind"]] += 1
        for trap_class in TRAP_CLASSES:
            self.assertEqual(dict(by_class_kind[trap_class]), EXPECTED_PER_CLASS)

    def test_measurement_labels_are_complete_and_consistent(self):
        ids = set()
        for scenario in load_measurement():
            ids.add(scenario["id"])
            self.assertEqual(scenario["measurement_suite"], "agt_redteam_measurement_v2")
            self.assertIn(scenario["scenario_kind"], SCENARIO_KINDS)
            self.assertIn(scenario["expected_control_behavior"],
                          {"detect_or_block", "allow_or_clarify"})
            if scenario["scenario_kind"] == "evasion_positive":
                self.assertNotEqual(scenario["evasion_technique"], "none")
                self.assertEqual(scenario["expected_control_behavior"], "detect_or_block")
            elif scenario["scenario_kind"] == "canonical_positive":
                self.assertEqual(scenario["evasion_technique"], "none")
                self.assertEqual(scenario["expected_control_behavior"], "detect_or_block")
            else:
                self.assertEqual(scenario["evasion_technique"], "none")
                self.assertEqual(scenario["expected_control_behavior"], "allow_or_clarify")
        self.assertEqual(len(ids), 240)


class MeasurementValidatorContract(unittest.TestCase):
    """The normal CLI validates measurement rows without a special flag."""

    def test_measurement_suite_validates_front_to_end(self):
        paths = measurement_paths()
        self.assertEqual(len(paths), 240)
        r = run_validator(*paths)
        self.assertEqual(r.returncode, 0, r.stderr)
        out = json.loads(r.stdout)
        self.assertEqual(out["validated"], 240)
        for count in out["trap_counts"].values():
            self.assertEqual(count, 40)

    def test_measurement_path_requires_measurement_labels(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = json.loads((BENCH / "scenarios" / "hidden-html-comment-001.json")
                              .read_text(encoding="utf-8"))
            p = Path(tmp) / "measurement" / "scenarios"
            p.mkdir(parents=True)
            bad = p / "bad-measurement-001.json"
            bad.write_text(json.dumps(data), encoding="utf-8")
            r = run_validator(bad)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("measurement", r.stderr.lower())

    def test_rows_are_raw_free_and_no_certification_terms(self):
        for path in measurement_paths():
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(vs.raw_free_violations(data), [], path.name)
            self.assertEqual(vs.certification_terms(data), [], path.name)


class MeasurementScorecardContract(unittest.TestCase):
    """oc-agtrt-v2-2: reports expose catch/FPR/evasion metrics."""

    def test_l2_projection_reports_measurement_metrics(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = run_scorecard(tmp)
            self.assertEqual(r.returncode, 0, r.stderr)
            report = json.loads((Path(tmp) / "scorecard_report.json").read_text())
        metrics = report["measurement_metrics"]
        self.assertEqual(metrics["suite"], "agt_redteam_measurement_v2")
        self.assertEqual(metrics["total_rows"], 240)
        self.assertEqual(metrics["canonical_catch_rate"], 1.0)
        self.assertEqual(metrics["evasion_catch_rate"], 1.0)
        self.assertEqual(metrics["evasion_degradation"], 0.0)
        self.assertEqual(metrics["false_positive_rate"], 0.0)
        self.assertEqual(metrics["utility_preservation_rate"], 1.0)
        self.assertEqual(metrics["unmeasured_rows"], 0)
        self.assertEqual(set(metrics["by_trap_class"]), TRAP_CLASSES)

    def test_metric_cells_are_not_underpowered(self):
        scenarios = load_measurement()
        cells = Counter((s["trap_class"], s["scenario_kind"]) for s in scenarios)
        for trap_class in TRAP_CLASSES:
            self.assertGreaterEqual(cells[(trap_class, "canonical_positive")], 8)
            self.assertGreaterEqual(cells[(trap_class, "evasion_positive")], 16)
            self.assertGreaterEqual(cells[(trap_class, "hard_benign")], 8)
            self.assertGreaterEqual(cells[(trap_class, "near_miss")], 8)


if __name__ == "__main__":
    unittest.main()
