"""M2 BDD + invariant tests for the mock behavioural harness.

Outcome-first (oc-2): the assessing engineer runs the harness over a scenario
and gets traces showing whether each unsafe action was *attempted but blocked*
vs *executed* — with no real side effect. These tests drive the REAL runner CLI
(subprocess) for the front-to-end outcome and unit-test the harness internals.

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
HARNESS_DIR = BENCH / "harness"
RUNNER = HARNESS_DIR / "runner.py"
TRACE_SCHEMA = json.loads((HARNESS_DIR / "tool_trace.schema.json").read_text(encoding="utf-8"))

sys.path.insert(0, str(HARNESS_DIR))
import mock_tools  # noqa: E402
import runner  # noqa: E402


def run_cli(out_dir, *extra):
    return subprocess.run(
        [sys.executable, str(RUNNER), "--out", str(out_dir), *extra],
        capture_output=True, text=True,
    )


def read_traces(out_dir):
    return [json.loads(line) for line in (Path(out_dir) / "traces.jsonl").read_text().splitlines() if line]


class OutcomeFrontToEnd(unittest.TestCase):
    """oc-2: run the harness front-to-end, see attempted vs executed."""

    def test_oc2_traces_attempted_executed(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = run_cli(tmp)
            self.assertEqual(r.returncode, 0, r.stderr)
            summary = json.loads(r.stdout)
            self.assertGreaterEqual(summary["traces"], 5)
            self.assertGreaterEqual(summary["blocked_attempts"], 4)
            traces = read_traces(tmp)
            blocked = [t for t in traces if t["attempted"] and not t["executed"]]
            self.assertGreaterEqual(len(blocked), 4)
            for t in blocked:
                self.assertIsNotNone(t["blocked_at"])  # blocked attempt recorded, not dropped
                self.assertTrue(t["attempted"])          # tm-agtrt-abuse-5: stays visible

    def test_benign_dry_run_executed(self):
        t = mock_tools.simulate("mock_audit_log", unsafe=False)
        self.assertTrue(t["executed"])
        self.assertIsNone(t["blocked_at"])

    def test_unknown_tool_structured_error(self):
        with self.assertRaises(mock_tools.UnknownToolError):
            mock_tools.simulate("mock_nope", unsafe=True)
        with tempfile.TemporaryDirectory() as tmp:
            r = run_cli(tmp, "--tool", "mock_nope")
            self.assertNotEqual(r.returncode, 0)
            self.assertNotIn("Traceback", r.stderr)

    def test_turn_cap_bounded(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = run_cli(tmp, "--max-turns", "1")
            self.assertEqual(r.returncode, 0, r.stderr)
            summary = json.loads(r.stdout)
            self.assertTrue(summary["capped"])
            self.assertLess(summary["traces"], 6)  # stopped before all turns


class Invariants(unittest.TestCase):
    """§5.5 load-bearing behavioural invariants."""

    def setUp(self):
        self.traces, self.capped = runner.run(runner.DEFAULT_SCENARIO)

    def test_executed_false_implies_blocked_at(self):
        for t in self.traces:
            if not t["executed"]:
                self.assertIsNotNone(t["blocked_at"], t["tool"])

    def test_unsafe_blocked_and_attempt_recorded(self):
        blocked = [t for t in self.traces if not t["executed"]]
        self.assertGreaterEqual(len(blocked), 4)
        for t in blocked:
            self.assertTrue(t["attempted"], t["tool"])

    def test_every_trace_has_audit_event(self):
        for t in self.traces:
            self.assertTrue(t["audit_event_present"], t["tool"])

    def test_trace_schema_conformance(self):
        required = set(TRACE_SCHEMA["required"])
        for t in self.traces:
            self.assertTrue(required <= set(t), f"{t['tool']} missing {required - set(t)}")
            self.assertIsInstance(t["attempted"], bool)
            self.assertIsInstance(t["executed"], bool)
            self.assertIsInstance(t["audit_event_present"], bool)
            self.assertIsInstance(t["canary_leaked"], bool)
            self.assertTrue(t["blocked_at"] is None or isinstance(t["blocked_at"], str))


class NoRealSideEffect(unittest.TestCase):
    """tm-agtrt-abuse-3: a mock tool must be structurally side-effect-free."""

    def test_no_dangerous_imports(self):
        banned = ("import subprocess", "import socket", "import requests",
                  "import urllib.request", "from subprocess", "from socket")
        for src_file in HARNESS_DIR.glob("*.py"):
            src = src_file.read_text(encoding="utf-8")
            for token in banned:
                self.assertNotIn(token, src, f"{src_file.name} contains {token!r}")


if __name__ == "__main__":
    unittest.main()
