"""M3 tests: reproducible one-command smoke + append-only CI guard.

Outcome-first (oc-3): the assessing engineer runs the whole assessment in one
command (`run-smoke.sh`: validate -> harness) and gets a single pass/fail with
summaries. Fail-fast on the first non-zero step.

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
SMOKE = BENCH / "run-smoke.sh"
SCENARIOS = sorted((BENCH / "scenarios").glob("*.json"))
REPO = BENCH.parent.parent                       # repo root
READINESS = REPO / ".github" / "workflows" / "readiness.yml"


def run_smoke(env_overrides=None):
    import os
    env = dict(os.environ)
    if env_overrides:
        env.update(env_overrides)
    return subprocess.run(["bash", str(SMOKE)], capture_output=True, text=True, env=env)


class OutcomeFrontToEnd(unittest.TestCase):
    """oc-3: run the whole assessment in one command."""

    def test_oc3_smoke_green(self):
        r = run_smoke()
        self.assertEqual(r.returncode, 0, r.stderr)
        out = r.stdout + r.stderr
        self.assertIn("validate", out.lower())
        self.assertIn("harness", out.lower())

    def test_smoke_failfast_names_step(self):
        # Point the smoke at a scenarios dir with one malformed scenario:
        # the validate step must fail FIRST and stop before the harness.
        with tempfile.TemporaryDirectory() as tmp:
            for p in SCENARIOS:
                (Path(tmp) / p.name).write_text(p.read_text(), encoding="utf-8")
            bad = json.loads(SCENARIOS[0].read_text())
            bad["trap_class"] = "Nonsense"
            (Path(tmp) / SCENARIOS[0].name).write_text(json.dumps(bad), encoding="utf-8")
            r = run_smoke({"AGTRT_SCENARIOS": tmp})
            self.assertNotEqual(r.returncode, 0)
            self.assertNotIn("[smoke] OK", r.stdout)


class CiAppendOnly(unittest.TestCase):
    """The CI job is APPENDED — existing readiness steps are not removed/reordered."""

    def setUp(self):
        self.text = READINESS.read_text(encoding="utf-8")

    def test_existing_job_preserved(self):
        self.assertIn("public-repo-readiness:", self.text)
        # original load-bearing steps still present
        for step in ("Diff hygiene", "Validate open-source readiness package",
                     "Round-4 smoke reproduction"):
            self.assertIn(step, self.text)

    def test_new_job_appended_after_existing(self):
        self.assertIn("agt-redteam-smoke:", self.text)
        self.assertLess(
            self.text.index("public-repo-readiness:"),
            self.text.index("agt-redteam-smoke:"),
            "new job must be appended after the existing job",
        )

    def test_smoke_is_failfast(self):
        self.assertIn("set -euo pipefail", SMOKE.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
