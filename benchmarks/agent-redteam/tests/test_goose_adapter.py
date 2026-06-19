"""M6 tests: live Goose adapter + OS-enforced sandbox.

The security-critical controls (egress-deny, scrubbed env, no host fs) are
proven here WITHOUT any credentials or live model call — the live L3 leg is
gated on keys and skips cleanly without them.

stdlib-only; the default (mock/L2) path must not import the live deps.
"""
import os
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
        self.assertIn("haiku", adapter.DEFAULT_MODEL)  # cost-safe default


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


if __name__ == "__main__":
    unittest.main()
