"""M2 BDD tests for the consolidated one-family bridge.

Outcome-first (oc-agtrtc-2): the assessing engineer runs one consolidated
smoke command and receives a metadata-only L1/L2 joint matrix for the
indirect-injection slice. M2 is deliberately L2/mock-only: any live/L3 request
must refuse without producing fake L3 evidence.
"""
import importlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
BENCH = HERE.parent
SMOKE = BENCH / "run-consolidated-smoke.sh"
BRIDGE = BENCH / "consolidated" / "bridge.py"


def run_smoke(out_dir, *extra):
    env = dict(os.environ)
    env["AGTRTC_OUT"] = str(out_dir)
    return subprocess.run(
        ["bash", str(SMOKE), *extra],
        capture_output=True, text=True, env=env,
    )


def run_bridge(out_dir, *extra):
    return subprocess.run(
        [sys.executable, str(BRIDGE), "--out", str(out_dir), *extra],
        capture_output=True, text=True,
    )


def read_report(out_dir):
    return json.loads((Path(out_dir) / "consolidated_report.json").read_text(encoding="utf-8"))


class OutcomeFrontToEnd(unittest.TestCase):
    """oc-agtrtc-2: one command produces the one-family joint report."""

    def test_oc2_consolidated_smoke_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = run_smoke(tmp)
            self.assertEqual(r.returncode, 0, r.stderr)
            report = read_report(tmp)
            self.assertIs(report["certification_claim"], False)
            self.assertEqual(report["family"], "indirect_injection")
            self.assertGreater(report["l1_rows"], 0)
            self.assertGreater(report["l2_rows"], 0)
            self.assertNotIn("L3_live_behavioural", report["evidence_levels"])
            self.assertTrue(report["failure_bar_clear"])

    def test_report_has_undetected_contained_off_diagonal(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(run_smoke(tmp).returncode, 0)
            report = read_report(tmp)
            self.assertGreater(report["joint_matrix"]["undetected -> contained"], 0)


class FailureModes(unittest.TestCase):
    """M2 failure-bar and abuse-case coverage."""

    def test_live_request_refuses_without_fake_l3(self):  # tm-agtrtc-abuse-3
        with tempfile.TemporaryDirectory() as tmp:
            r = run_bridge(tmp, "--live")
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("L3 deferred to M4", r.stderr)
            if (Path(tmp) / "consolidated_report.json").exists():
                self.assertNotIn("L3_live_behavioural",
                                 (Path(tmp) / "consolidated_report.json").read_text())

    def test_raw_payload_ref_field_fails(self):  # tm-agtrtc-abuse-1
        bad_sample = {
            "sample_id": "bad",
            "family": "indirect_injection",
            "rows": [{
                "template_id": "hidden-html-comment-001",
                "payload_ref": {
                    "id": "r7-inj-raw",
                    "family": "indirect_injection",
                    "split": "test",
                    "corpus_manifest_hash": "sha256:" + ("0" * 64),
                    "text": "raw payload should not be here",
                },
                "detector_verdict": "flagged",
                "action_outcome": "contained",
            }],
        }
        with tempfile.TemporaryDirectory() as tmp:
            sample = Path(tmp) / "bad-sample.json"
            sample.write_text(json.dumps(bad_sample), encoding="utf-8")
            r = run_bridge(Path(tmp) / "out", "--sample", sample)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("raw", r.stderr.lower())

    def test_detected_executed_fails_failure_bar(self):  # tm-agtrtc-abuse-2
        sys.path.insert(0, str(BENCH / "consolidated"))
        bridge = importlib.import_module("bridge")
        row = {
            "scenario_id": "hidden-html-comment-001",
            "payload_ref": bridge.DEFAULT_SAMPLE["rows"][0]["payload_ref"],
            "detection": {"verdict": "flagged", "evidence_level": "L1_static"},
            "action_outcome": "executed",
            "evidence_level": "L2_mock_behavioural",
            "trace_path": "traces/example.jsonl",
            "benign": False,
        }
        report = bridge.build_report([row], elapsed_ms=1)
        self.assertFalse(report["failure_bar_clear"])
        self.assertEqual(report["joint_matrix"]["detected -> executed"], 1)


class BoundsAndRawFree(unittest.TestCase):
    def test_sample_size_bound(self):
        sys.path.insert(0, str(BENCH / "consolidated"))
        bridge = importlib.import_module("bridge")
        self.assertLessEqual(len(bridge.DEFAULT_SAMPLE["rows"]), 30)

    def test_no_l3_in_smoke_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(run_smoke(tmp).returncode, 0)
            for path in Path(tmp).rglob("*"):
                if path.is_file():
                    self.assertNotIn("L3_live_behavioural",
                                     path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
