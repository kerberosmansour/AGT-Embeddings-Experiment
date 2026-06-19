"""Tests for the Goose batch live-run wrapper."""
import json
import os
import subprocess
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
    def test_runner_live_without_limit_is_bash32_safe(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            fake_python = tmp_path / "fake-python"
            log = tmp_path / "fake-python.log"
            fake_python.write_text(
                "#!/bin/sh\n"
                "printf '%s\\n' \"$*\" >> \"$AGTRT_FAKE_PYTHON_LOG\"\n"
                "exit 0\n",
                encoding="utf-8",
            )
            fake_python.chmod(0o755)

            env = os.environ.copy()
            env.update({
                "PYTHON": str(fake_python),
                "AGTRT_FAKE_PYTHON_LOG": str(log),
                "AGTRT_MEASUREMENT_OUT": str(tmp_path / "out"),
            })
            result = subprocess.run(
                ["/bin/bash", str(BENCH / "run-measurement.sh"), "--live"],
                capture_output=True, text=True, env=env,
            )
            calls = log.read_text(encoding="utf-8").splitlines()

        self.assertEqual(result.returncode, 0, result.stderr)
        batch_calls = [call for call in calls if "batch_run.py" in call]
        self.assertEqual(len(batch_calls), 1)
        self.assertNotIn("--limit", batch_calls[0])

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
