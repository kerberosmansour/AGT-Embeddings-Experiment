"""M8 tests for the shareable scorecard product.

Outcome-first (oc-8): the assessing engineer generates a shareable scorecard
(HTML+MD) from a run and hands it to a stakeholder, who correctly reads it as
honest evidence-level results, not a certification. Offline, raw-free, no badge.

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
PRODUCT_DIR = BENCH / "product"
RENDER = PRODUCT_DIR / "render.py"

sys.path.insert(0, str(PRODUCT_DIR))
import render  # noqa: E402


def _scorecard(**over):
    base = {
        "certification_claim": False,
        "status": "self_assessment_evidence",
        "trap_classes": ["Content Injection", "Systemic"],
        "evidence_levels": ["L2_mock_behavioural"],
        "controls": {"AGT-AC-003": 1, "AGT-AC-010": 1},
        "unmapped_controls": [],
        "failures": 0,
        "remediation": ["Keep OpenCRE relation status visible."],
    }
    base.update(over)
    return base


def _render_cli(tmp, report):
    src = Path(tmp) / "scorecard_report.json"
    src.write_text(json.dumps(report), encoding="utf-8")
    out = Path(tmp) / "out"
    r = subprocess.run([sys.executable, str(RENDER), str(src), "-o", str(out)],
                       capture_output=True, text=True)
    return r, out


class OutcomeFrontToEnd(unittest.TestCase):
    """oc-8: generate a shareable, honest scorecard."""

    def test_oc8_product_generated(self):
        with tempfile.TemporaryDirectory() as tmp:
            r, out = _render_cli(tmp, _scorecard())
            self.assertEqual(r.returncode, 0, r.stderr)
            html = (out / "scorecard.html").read_text(encoding="utf-8")
            md = (out / "scorecard.md").read_text(encoding="utf-8")
            self.assertIn("AGT-AC-003", html)
            self.assertIn("AGT-AC-003", md)

    def test_no_certification(self):  # tm-agtrt-abuse-4
        with tempfile.TemporaryDirectory() as tmp:
            _, out = _render_cli(tmp, _scorecard())
            for name in ("scorecard.html", "scorecard.md"):
                low = (out / name).read_text(encoding="utf-8").lower()
                self.assertIn("certification_claim", low)
                self.assertIn("not a certification", low)
                for term in ("certified", "owasp-certified", "official opencre"):
                    self.assertNotIn(term, low)
                # no single mystery score / pass badge
                self.assertNotIn("overall score", low)

    def test_html_escaped_no_xss(self):  # CWE-79
        with tempfile.TemporaryDirectory() as tmp:
            _, out = _render_cli(tmp, _scorecard(controls={"<script>alert(1)</script>": 1}))
            html = (out / "scorecard.html").read_text(encoding="utf-8")
            self.assertNotIn("<script>alert(1)</script>", html)
            self.assertIn("&lt;script&gt;", html)

    def test_offline_no_external_refs(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, out = _render_cli(tmp, _scorecard())
            html = (out / "scorecard.html").read_text(encoding="utf-8").lower()
            for ext in ("http://", "https://cdn", "src=\"http", "<script src"):
                self.assertNotIn(ext, html)

    def test_empty_run_valid_with_disclaimer(self):
        with tempfile.TemporaryDirectory() as tmp:
            r, out = _render_cli(tmp, _scorecard(controls={}, trap_classes=[], evidence_levels=[]))
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("not a certification",
                          (out / "scorecard.html").read_text(encoding="utf-8").lower())


if __name__ == "__main__":
    unittest.main()
