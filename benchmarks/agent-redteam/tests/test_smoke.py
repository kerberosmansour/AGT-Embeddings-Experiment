"""M3 tests: reproducible one-command smoke + append-only CI guard.

Outcome-first (oc-3): the assessing engineer runs the whole assessment in one
command (`run-smoke.sh`: validate -> harness) and gets a single pass/fail with
summaries. Fail-fast on the first non-zero step.

stdlib-only; tests write only to a TemporaryDirectory.
"""
import json
import shlex
import shutil
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


def bash_path():
    bash = shutil.which("bash")
    if not bash and Path("/bin/bash").exists():
        bash = "/bin/bash"
    return bash


def run_smoke(env_overrides=None):
    import os
    bash = bash_path()
    if not bash:
        raise unittest.SkipTest("bash not installed on this host")
    env = dict(os.environ)
    if env_overrides:
        env.update(env_overrides)
    return subprocess.run([bash, str(SMOKE)], capture_output=True, text=True, env=env)


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


class Portability(unittest.TestCase):
    """DW-004 / Win-audit Finding 2: the interpreter probe must work where
    `python3` is a non-functional alias (Windows Store-alias), not just where
    `command -v python3` happens to resolve."""

    def test_probe_executes_interpreter_not_just_which(self):
        # Static guard: the probe must RUN the interpreter (so a `command -v`-only
        # check that the Windows python3 alias passes can never come back).
        src = SMOKE.read_text(encoding="utf-8")
        self.assertIn("import sys", src,
                      "interpreter probe must execute python, not just `command -v`")
        self.assertNotRegex(
            src, r'PY="\$\{PYTHON:-python3\}"\s*\n\s*command -v "\$PY"',
            "regressed to the command-v-only pick that fails on the Windows python3 alias",
        )

    def test_smoke_survives_a_broken_python3_on_path(self):
        # Behaviourally simulate the Windows Store-alias: a `python3` on PATH that
        # exists but exits non-zero without running Python. The probe must skip it
        # and fall through to a real interpreter, so the smoke still passes.
        import os
        real_python = None
        for cand in ("python", "python3"):
            resolved = shutil.which(cand)
            if not resolved:
                continue
            try:
                if subprocess.run([resolved, "-c", "import sys"],
                                  capture_output=True).returncode == 0:
                    real_python = resolved
                    break
            except FileNotFoundError:
                continue
        if real_python is None:
            self.skipTest("no real interpreter available to fall through to")
        with tempfile.TemporaryDirectory() as tmp:
            stub = Path(tmp) / "python3"
            stub.write_text("#!/usr/bin/env bash\n"
                            "echo 'Python was not found' >&2\nexit 9\n",
                            encoding="utf-8")
            stub.chmod(0o755)
            fallback = Path(tmp) / "python"
            fallback.write_text(
                "#!/usr/bin/env bash\n"
                f"exec {shlex.quote(real_python)} \"$@\"\n",
                encoding="utf-8",
            )
            fallback.chmod(0o755)
            # real interpreter still reachable AFTER the broken python3 shim.
            env = dict(os.environ)
            env["PATH"] = str(tmp) + os.pathsep + env.get("PATH", "")
            env["PYTHON"] = ""  # force the probe (don't let an override hide the bug)
            r = run_smoke(env)
            self.assertEqual(r.returncode, 0,
                             msg=f"probe failed to skip broken python3\n{r.stdout}\n{r.stderr}")


if __name__ == "__main__":
    unittest.main()
