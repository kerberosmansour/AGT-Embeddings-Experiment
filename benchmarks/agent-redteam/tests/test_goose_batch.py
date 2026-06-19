"""Tests for the Goose batch live-run wrapper."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
BENCH = HERE.parent
GOOSE_DIR = BENCH / "adapters" / "goose"
MEASUREMENT_DIR = BENCH / "measurement" / "scenarios"

sys.path.insert(0, str(GOOSE_DIR))
import adapter  # noqa: E402
import batch_run  # noqa: E402


class BatchRun(unittest.TestCase):
    def test_batch_preserves_measurement_labels_and_summary(self):
        scenarios = [
            json.loads((MEASUREMENT_DIR / "ms-content-injection-canonical-001.json")
                       .read_text(encoding="utf-8")),
            json.loads((MEASUREMENT_DIR / "ms-content-injection-hidden-content-001.json")
                       .read_text(encoding="utf-8")),
        ]

        def fake_runner(_scenario, **_kwargs):
            trace = adapter._contained_trace("shell", sandbox_ok=True, model="fake-model")
            return {"status": "completed", "evidence_level": "L3_live", "traces": [trace]}

        with tempfile.TemporaryDirectory() as tmp:
            summary = batch_run.run_batch(scenarios, out=tmp, runner=fake_runner)
            rows = [
                json.loads(line) for line in
                (Path(tmp) / "live_results.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            saved_summary = json.loads((Path(tmp) / "live_summary.json").read_text())

        self.assertEqual(summary, saved_summary)
        self.assertEqual(summary["total"], 2)
        self.assertEqual(summary["l3_trace_rows"], 2)
        self.assertEqual(rows[0]["scenario_kind"], "canonical_positive")
        self.assertEqual(rows[0]["evasion_technique"], "none")
        self.assertEqual(rows[1]["scenario_kind"], "evasion_positive")
        self.assertEqual(rows[1]["evasion_technique"], "hidden_content")
        self.assertEqual(rows[1]["measurement_suite"], "agt_redteam_measurement_v2")


if __name__ == "__main__":
    unittest.main()
