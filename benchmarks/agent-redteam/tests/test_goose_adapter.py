"""M6 tests: live Goose adapter + OS-enforced sandbox.

The security-critical controls (egress-deny, scrubbed env, no host fs) are
proven here WITHOUT any credentials or live model call — the live L3 leg is
gated on keys and skips cleanly without them.

stdlib-only; the default (mock/L2) path must not import the live deps.
"""
import os
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
BENCH = HERE.parent
GOOSE_DIR = BENCH / "adapters" / "goose"

sys.path.insert(0, str(GOOSE_DIR))
import sandbox  # noqa: E402
import adapter  # noqa: E402

HAVE_BWRAP = sandbox.available()


@unittest.skipUnless(HAVE_BWRAP, "bwrap not installed on this host")
class OsSandbox(unittest.TestCase):
    """tm-agtrt-abuse-3 / CWE-918: real containment at the OS layer."""

    def test_all_controls_hold(self):
        results = sandbox.assert_secure()
        self.assertTrue(results["egress_inet_blocked"])
        self.assertTrue(results["egress_metadata_blocked"])  # 169.254.169.254
        self.assertTrue(results["env_scrubbed"])
        self.assertTrue(results["no_host_home"])

    def test_real_subprocess_cannot_egress(self):
        probe = ("import socket,sys\n"
                 "try: socket.create_connection(('1.1.1.1',80),timeout=2); sys.exit(0)\n"
                 "except OSError: sys.exit(7)\n")
        rc, _out, _err = sandbox.run([sys.executable, "-c", probe], timeout=10)
        self.assertEqual(rc, 7, "subprocess egress was NOT blocked")

    def test_host_credentials_not_visible(self):
        # Even with a secret in the orchestrator's env, the sandbox cannot see it.
        os.environ["AGTRT_FAKE_SECRET"] = "AKIAIOSFODNN7EXAMPLE"
        try:
            probe = ("import os;print('AGTRT_FAKE_SECRET' in os.environ)\n")
            rc, out, _ = sandbox.run([sys.executable, "-c", probe], timeout=10)
            self.assertEqual(rc, 0)
            self.assertIn("False", out)
        finally:
            del os.environ["AGTRT_FAKE_SECRET"]


class LiveGating(unittest.TestCase):
    """The live path fail-closes and never fakes an L3 result."""

    @unittest.skipUnless(HAVE_BWRAP, "bwrap not installed")
    def test_live_skips_without_credentials(self):
        # No creds in env / no .agtrt-goose.env -> skipped, never L3, never crash.
        for v in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
            os.environ.pop(v, None)
        result = adapter.run_live({"views": {"agent_visible": "hi"}, "title": "t"},
                                  creds=None)
        if not (BENCH.parents[1] / adapter.CRED_FILE).exists():
            self.assertEqual(result["status"], "skipped")
            self.assertEqual(result["traces"], [])
            self.assertNotEqual(result["evidence_level"], "L3_live")

    def test_cli_refuses_without_live_flag(self):
        self.assertEqual(adapter.main(["adapter.py"]), 2)

    def test_default_cheap_model(self):
        self.assertEqual(adapter.DEFAULT_MODEL, "claude-haiku-4-5")  # cost-safe default

    def test_m6sec1_contained_trace_is_honest(self):
        # M6-SEC-1 (win review): a tool the agent ATTEMPTED is contained, never
        # executed for real — so the L3 trace must NOT claim executed:True.
        t = adapter._contained_trace("shell", sandbox_ok=True, model="m")
        self.assertTrue(t["attempted"])
        self.assertFalse(t["executed"], "must not overclaim the agent's action ran")
        self.assertEqual(t["blocked_at"], "sandbox_contained")
        self.assertEqual(t["evidence_level"], "L3_live")
        self.assertTrue(t["sandbox_ok"])

    def test_live_result_projects_to_m4_scorecard_shape(self):
        scenario = {
            "id": "m6-live-probe",
            "trap_class": "Behavioural Control",
            "controls": ["AGT-AC-004"],
        }
        trace = adapter._contained_trace("shell", sandbox_ok=True, model="claude-haiku-4-5")
        row = adapter.build_scorecard_result(
            scenario, {"status": "completed", "traces": [trace]})
        self.assertEqual(row["scenario_id"], "m6-live-probe")
        self.assertEqual(row["evidence_level"], "L3_live_behavioural")
        self.assertEqual(row["status"], "pass")
        self.assertEqual(row["trace"], [trace])

    def test_require_trace_fails_vacuous_keyed_live_run(self):
        result = {"status": "completed", "evidence_level": "L3_live", "traces": []}
        self.assertIn("required live L3 trace", adapter.require_trace_error(result))

    def test_require_trace_allows_no_credentials_skip(self):
        result = {
            "status": "skipped",
            "evidence_level": "L0_declared",
            "reason": "no credentials provisioned (set ANTHROPIC_API_KEY or .agtrt-goose.env)",
            "traces": [],
        }
        self.assertIsNone(adapter.require_trace_error(result))


class DefaultPathIsolation(unittest.TestCase):
    """The default (mock/L2) benchmark path must not import the live deps."""

    def test_default_modules_have_no_live_imports(self):
        for rel in ("schema/validate_scenarios.py", "harness/runner.py",
                    "reporters/scorecard.py", "hygiene/raw_free_scan.py"):
            src = (BENCH / rel).read_text(encoding="utf-8")
            for banned in ("import anthropic", "import goose", "adapters.goose"):
                self.assertNotIn(banned, src, f"{rel} imports live dep {banned!r}")

    def test_l3_only_from_live_path(self):
        # A skipped run carries no L3 traces.
        for v in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
            os.environ.pop(v, None)
        if not HAVE_BWRAP:
            self.skipTest("bwrap not installed")
        if (BENCH.parents[1] / adapter.CRED_FILE).exists():
            self.skipTest("creds provisioned; live path active")
        result = adapter.run_live({"views": {"agent_visible": "x"}, "title": "t"}, creds=None)
        self.assertFalse([t for t in result["traces"] if t.get("evidence_level") == "L3_live"])


class LiveSmokeWrapper(unittest.TestCase):
    """The shell wrapper must reach the live sandbox gate, even with no model override."""

    @unittest.skipIf(HAVE_BWRAP, "sandbox-present hosts exercise the live/skip path instead")
    def test_live_smoke_no_model_override_reaches_sandbox_refusal(self):
        env = os.environ.copy()
        env.pop("AGTRT_LIVE_MODEL", None)
        env.pop("ANTHROPIC_API_KEY", None)
        env.pop("OPENAI_API_KEY", None)
        proc = subprocess.run(
            ["bash", str(BENCH / "run-smoke.sh"), "--live"],
            cwd=str(BENCH.parents[1]),
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        combined = proc.stdout + proc.stderr
        self.assertNotEqual(proc.returncode, 0, combined)
        self.assertIn("bwrap not found; refusing the live sandbox path", combined)
        self.assertNotIn("unbound variable", combined)


if __name__ == "__main__":
    unittest.main()
