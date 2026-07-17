import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUNNER = ROOT / "meta/harness/agent-redteam-consolidated/run_l1_static.py"
VALIDATOR = ROOT / "meta/harness/agent-redteam-consolidated/validate_l1_static.py"
ROUND7_CORPUS = ROOT / "scratch/round7-large.jsonl"
ROUND7_MANIFEST = ROOT / "scratch/round7-large-manifest.json"
ROUND7_SETUP = (
    "generate the Round-7 corpus first: python3 corpus/round7/generate-round7.py "
    "--profile large --out scratch/round7-large.jsonl "
    "--manifest scratch/round7-large-manifest.json"
)


@unittest.skipUnless(
    ROUND7_CORPUS.is_file() and ROUND7_MANIFEST.is_file(),
    ROUND7_SETUP,
)
class L1StaticFrontToEnd(unittest.TestCase):
    def run_l1(self, out_dir: Path) -> Path:
        proc = subprocess.run(
            [sys.executable, str(RUNNER), "--out", str(out_dir)],
            cwd=str(ROOT),
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        return out_dir / "l1_static_report.json"

    def validate(self, report_path: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATOR), str(report_path)],
            cwd=str(ROOT),
            text=True,
            capture_output=True,
            check=False,
        )

    def test_oc4_full_l1_artifact_validates_front_to_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            report_path = self.run_l1(Path(tmp))
            proc = self.validate(report_path)
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)

            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(report["schema"], "agt-consolidated-l1-static-report-v1")
            self.assertEqual(report["row_count"], 54034)
            self.assertEqual(report["l1_rows"], 54034)
            self.assertEqual(report["l2_rows"], 0)
            self.assertEqual(report["l3_live_rows"], 0)
            self.assertEqual(report["evidence_levels"], ["L1_static"])
            self.assertEqual(report["selection_split"], "validation")
            self.assertFalse(report["certification_claim"])
            self.assertLessEqual(
                report["hard_benign_fp_wilson_95"]["upper"],
                report["hard_benign_fp_wilson_upper_bar"],
            )
            self.assertEqual(report["hard_benign_fp_wilson_upper_bar"], 0.10)
            self.assertGreater(len(report["families_needing_l3_sampling"]), 0)

            corpora = {c["corpus_id"]: c for c in report["corpora"]}
            self.assertEqual(set(corpora), {"round4-large", "round7-large"})
            self.assertEqual(corpora["round4-large"]["row_count"], 44800)
            self.assertEqual(corpora["round7-large"]["row_count"], 9234)
            for corpus in corpora.values():
                self.assertRegex(corpus["manifest_sha256"], r"^[0-9a-f]{64}$")
                self.assertRegex(corpus["data_sha256"], r"^[0-9a-f]{64}$")

            result_path = report_path.parent / report["result_path"]
            first_row = json.loads(result_path.read_text(encoding="utf-8").splitlines()[0])
            self.assertEqual(first_row["evidence_level"], "L1_static")
            self.assertIn("payload_ref", first_row)
            self.assertRegex(first_row["payload_ref"]["corpus_manifest_hash"], r"^[0-9a-f]{64}$")
            self.assertNotIn("action_outcome", first_row)
            self.assertNotIn("trace_path", first_row)

    def test_validator_rejects_raw_prompt_like_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            report_path = self.run_l1(Path(tmp))
            report = json.loads(report_path.read_text(encoding="utf-8"))
            result_path = report_path.parent / report["result_path"]
            lines = result_path.read_text(encoding="utf-8").splitlines()
            row = json.loads(lines[0])
            row["prompt"] = "raw prompt should never serialize"
            lines[0] = json.dumps(row, sort_keys=True)
            result_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

            proc = self.validate(report_path)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("forbidden raw-text-like field", proc.stderr)

    def test_validator_rejects_non_validation_freeze(self):
        with tempfile.TemporaryDirectory() as tmp:
            report_path = self.run_l1(Path(tmp))
            report = json.loads(report_path.read_text(encoding="utf-8"))
            freeze_path = report_path.parent / report["freeze_record_path"]
            freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
            freeze["selection_split"] = "test"
            freeze_path.write_text(json.dumps(freeze, indent=2, sort_keys=True) + "\n", encoding="utf-8")

            proc = self.validate(report_path)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("selection_split must be validation", proc.stderr)

    def test_validator_rejects_l2_or_l3_static_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            report_path = self.run_l1(Path(tmp))
            report = json.loads(report_path.read_text(encoding="utf-8"))
            result_path = report_path.parent / report["result_path"]
            lines = result_path.read_text(encoding="utf-8").splitlines()
            row = json.loads(lines[0])
            row["evidence_level"] = "L3_live_behavioural"
            lines[0] = json.dumps(row, sort_keys=True)
            result_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

            proc = self.validate(report_path)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("M3 rows must use L1_static", proc.stderr)

    def test_validator_rejects_hard_benign_bar_without_residual(self):
        with tempfile.TemporaryDirectory() as tmp:
            report_path = self.run_l1(Path(tmp))
            report = json.loads(report_path.read_text(encoding="utf-8"))
            report["hard_benign_fp_wilson_95"]["upper"] = 0.101
            report["residual_analysis"] = []
            report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

            proc = self.validate(report_path)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("hard-benign FP Wilson upper exceeds bar", proc.stderr)


if __name__ == "__main__":
    unittest.main()
