"""M4 tests for the control-linked evidence-level scorecard reporter.

Outcome-first (oc-4): the assessing engineer runs the full chain and gets an
evidence-level scorecard (JSON+MD) by trap class / AGT-AC control / evidence
level, with a hard `certification_claim:false` and zero certification language.

stdlib-only; tests write only to a TemporaryDirectory.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
BENCH = HERE.parent
REPORTERS = BENCH / "reporters"
SCORECARD = REPORTERS / "scorecard.py"
CONTROLS = BENCH / "controls" / "agt-ac.csv"
SCENARIOS_DIR = BENCH / "scenarios"

sys.path.insert(0, str(REPORTERS))
import scorecard  # noqa: E402

EVIDENCE_ENUM = {"L0_declared", "L1_static", "L2_mock_behavioural", "L3_live_behavioural"}


def _result(**over):
    base = {
        "scenario_id": "hidden-html-comment-001",
        "trap_class": "Content Injection",
        "controls": ["AGT-AC-003"],
        "evidence_level": "L2_mock_behavioural",
        "status": "pass",
    }
    base.update(over)
    return base


def run_cli(out_dir, *extra):
    return subprocess.run(
        [sys.executable, str(SCORECARD), "--controls", str(CONTROLS),
         "--out", str(out_dir), *extra],
        capture_output=True, text=True,
    )


class OutcomeFrontToEnd(unittest.TestCase):
    """oc-4: get an actionable evidence-level scorecard."""

    def test_oc4_report_generated_from_scenarios(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = run_cli(tmp, "--from-scenarios", str(SCENARIOS_DIR))
            self.assertEqual(r.returncode, 0, r.stderr)
            report = json.loads((Path(tmp) / "scorecard_report.json").read_text())
            self.assertIs(report["certification_claim"], False)
            self.assertTrue(report["trap_classes"])
            self.assertTrue(report["controls"])
            self.assertTrue(set(report["evidence_levels"]) <= EVIDENCE_ENUM)
            md = (Path(tmp) / "scorecard_report.md").read_text()
            self.assertIn("certification_claim", md)

    def test_no_certification_terms(self):  # tm-agtrt-abuse-4
        with tempfile.TemporaryDirectory() as tmp:
            run_cli(tmp, "--from-scenarios", str(SCENARIOS_DIR))
            for name in ("scorecard_report.json", "scorecard_report.md"):
                text = (Path(tmp) / name).read_text().lower()
                for term in ("certified", "owasp-certified", "official opencre", "iso-certified"):
                    self.assertNotIn(term, text, f"{name} contains {term!r}")


class NoOverclaimAndHonesty(unittest.TestCase):

    def test_certification_claim_is_literal_false(self):
        report = scorecard.build_report([_result()], scorecard.load_controls(CONTROLS))
        self.assertIs(report["certification_claim"], False)

    def test_no_l3_produced_from_mock_results(self):
        results = [_result(), _result(evidence_level="L1_static")]
        report = scorecard.build_report(results, scorecard.load_controls(CONTROLS))
        self.assertNotIn("L3_live_behavioural", report["evidence_levels"])

    def test_hard_benign_not_failed(self):  # tm-agtrt-abuse-6
        # A hard-benign must-not-block result (AGT-AC-014) that passed is NOT a failure.
        results = [_result(scenario_id="hard-benign-security-doc-008",
                           trap_class="Semantic Manipulation",
                           controls=["AGT-AC-014"], status="pass")]
        report = scorecard.build_report(results, scorecard.load_controls(CONTROLS))
        self.assertEqual(report["failures"], 0)

    def test_missing_field_structured_error(self):
        bad = _result()
        del bad["evidence_level"]
        with self.assertRaises(scorecard.ResultError):
            scorecard.build_report([bad], scorecard.load_controls(CONTROLS))

    def test_unknown_evidence_level_rejected(self):
        with self.assertRaises(scorecard.ResultError):
            scorecard.build_report([_result(evidence_level="L9")],
                                   scorecard.load_controls(CONTROLS))

    def test_unmapped_control_reported_not_dropped(self):
        report = scorecard.build_report([_result(controls=["AGT-AC-999"])],
                                        scorecard.load_controls(CONTROLS))
        self.assertIn("AGT-AC-999", report["unmapped_controls"])

    def test_empty_results_valid_report(self):
        report = scorecard.build_report([], scorecard.load_controls(CONTROLS))
        self.assertIs(report["certification_claim"], False)
        self.assertEqual(report["controls"], {})


if __name__ == "__main__":
    unittest.main()
