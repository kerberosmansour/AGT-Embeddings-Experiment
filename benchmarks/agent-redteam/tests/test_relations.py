"""M7 tests: OpenCRE relation-quality validator (fail-honest).

Outcome-first (oc-7): the assessing engineer's control mappings carry honest,
verified relation quality. Any relation without a committed OpenCRE backing
reference is downgraded to `candidate` — no false authority.

stdlib-only; tests write only to a TemporaryDirectory.
"""
import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
BENCH = HERE.parent
OPENCRE_DIR = BENCH / "controls" / "opencre"
VALIDATOR = OPENCRE_DIR / "validate_relations.py"
RELATIONS = OPENCRE_DIR / "relations.csv"
CONTROLS = BENCH / "controls" / "agt-ac.csv"

sys.path.insert(0, str(OPENCRE_DIR))
import validate_relations as vr  # noqa: E402


def run_cli(relations=RELATIONS, *extra):
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--relations", str(relations),
         "--controls", str(CONTROLS), *extra],
        capture_output=True, text=True,
    )


def run_default_cli():
    return subprocess.run([sys.executable, str(VALIDATOR)], capture_output=True, text=True)


def _write_relations(tmp, rows):
    p = Path(tmp) / "rel.csv"
    with p.open("w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=["control_id", "target", "relation", "backing_ref"])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    return p


class OutcomeFrontToEnd(unittest.TestCase):
    """oc-7: honest relation quality, end to end."""

    def test_oc7_committed_relations_all_honest(self):
        r = run_cli(RELATIONS)
        self.assertEqual(r.returncode, 0, r.stderr)
        report = json.loads(r.stdout)
        # No committed OpenCRE backing yet -> every relation is candidate.
        self.assertEqual(report["verified"], 0)
        self.assertEqual(report["candidate"], 15)
        self.assertGreater(report["downgraded"], 0)  # strong claims downgraded
        for row in report["relations"]:
            if not row["backing_ref"]:
                self.assertEqual(row["effective_relation"], "candidate", row["control_id"])

    def test_oc7_default_invocation_uses_bundled_files(self):
        r = run_default_cli()
        self.assertEqual(r.returncode, 0, r.stderr)
        report = json.loads(r.stdout)
        self.assertEqual(report["verified"], 0)
        self.assertEqual(report["candidate"], 15)
        self.assertEqual(report["unmapped_controls"], [])

    def test_no_endorsement_terms(self):  # tm-agtrt-abuse-4
        r = run_cli(RELATIONS)
        text = r.stdout.lower()
        for term in ("certified", "official opencre", "owasp-certified"):
            self.assertNotIn(term, text)


class FailHonest(unittest.TestCase):

    def test_downgrade_unproven_to_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = _write_relations(tmp, [
                {"control_id": "AGT-AC-001", "target": "x", "relation": "broad", "backing_ref": ""},
            ])
            report = vr.build_report(vr.load_relations(p), vr.load_control_ids(CONTROLS))
            self.assertEqual(report["relations"][0]["effective_relation"], "candidate")

    def test_verified_when_backing_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = _write_relations(tmp, [
                {"control_id": "AGT-AC-001", "target": "x", "relation": "broad",
                 "backing_ref": "CRE-764-507"},
            ])
            report = vr.build_report(vr.load_relations(p), vr.load_control_ids(CONTROLS))
            self.assertEqual(report["relations"][0]["effective_relation"], "broad")
            self.assertEqual(report["verified"], 1)

    def test_unknown_relation_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = _write_relations(tmp, [
                {"control_id": "AGT-AC-001", "target": "x", "relation": "bogus", "backing_ref": ""},
            ])
            with self.assertRaises(vr.RelationError):
                vr.build_report(vr.load_relations(p), vr.load_control_ids(CONTROLS))

    def test_unknown_control_id_reported_not_dropped(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = _write_relations(tmp, [
                {"control_id": "AGT-AC-999", "target": "x", "relation": "candidate", "backing_ref": ""},
            ])
            report = vr.build_report(vr.load_relations(p), vr.load_control_ids(CONTROLS))
            self.assertIn("AGT-AC-999", report["unmapped_controls"])


if __name__ == "__main__":
    unittest.main()
