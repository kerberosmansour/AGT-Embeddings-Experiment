"""M5 tests: raw-free hygiene gate + packaging.

Outcome-first (oc-5): the assessing engineer runs the full chain ending in the
raw-free hygiene gate and gets a benchmark they can trust to share — no raw
payload/secret/PII in any artifact — plus a PROMOTION.md boundary doc.

stdlib-only; tests write only to a TemporaryDirectory.
"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
BENCH = HERE.parent
HYGIENE = BENCH / "hygiene" / "raw_free_scan.py"
PROMOTION = BENCH / "PROMOTION.md"
SMOKE = BENCH / "run-smoke.sh"

sys.path.insert(0, str((BENCH / "hygiene")))
import raw_free_scan  # noqa: E402


def run_scan(path):
    return subprocess.run([sys.executable, str(HYGIENE), str(path)],
                          capture_output=True, text=True)


class HygieneGate(unittest.TestCase):

    def test_clean_tree_passes(self):
        # The committed benchmark data artifacts are synthetic + raw-free.
        r = run_scan(BENCH)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_planted_secret_fails(self):  # tm-agtrt-abuse-1, anti-vacuity
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "leak.json"
            bad.write_text('{"k": "AKIAIOSFODNN7EXAMPLE"}', encoding="utf-8")
            r = run_scan(tmp)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("leak.json", r.stdout + r.stderr)

    def test_pem_key_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "key.txt"
            bad.write_text("-----BEGIN RSA PRIVATE KEY-----\nabc\n", encoding="utf-8")
            self.assertNotEqual(run_scan(tmp).returncode, 0)

    def test_scanner_skips_detector_sources(self):
        # The .py detectors/tests legitimately contain secret PATTERNS; the
        # scanner must not flag its own source as a leak.
        self.assertTrue(raw_free_scan.is_scannable(Path("scenarios/x.json")))
        self.assertFalse(raw_free_scan.is_scannable(Path("hygiene/raw_free_scan.py")))
        self.assertFalse(raw_free_scan.is_scannable(Path("tests/test_schema.py")))


class Packaging(unittest.TestCase):

    def setUp(self):
        self.text = PROMOTION.read_text(encoding="utf-8")

    def test_promotion_md_exists_and_is_honest(self):
        low = self.text.lower()
        self.assertNotIn("certified", low)
        self.assertIn("raw-free", low)
        # no monolithic upstream PR is opened by this runbook
        self.assertIn("no upstream pr", low)

    def test_hidden_channel_note_for_fixtures(self):  # tm-agtrt-abuse-2
        low = self.text.lower()
        self.assertTrue("hides" in low or "hidden" in low or "divergence" in low)


class SmokeEndsInHygiene(unittest.TestCase):
    def test_smoke_has_hygiene_step(self):
        self.assertIn("raw_free_scan.py", SMOKE.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
