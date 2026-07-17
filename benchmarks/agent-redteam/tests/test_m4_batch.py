"""M4 BDD tests for the consolidated live sample runner.

The live provider is never called here. These tests exercise the frozen sample
contract, failure bars, and artifact validation with a deterministic fake live
runner.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BENCH = ROOT / "benchmarks/agent-redteam"
GOOSE = BENCH / "adapters/goose"

sys.path.insert(0, str(GOOSE))
import m4_batch  # noqa: E402


def l1_row(row_id, *, family, label="attack", hard_benign=False, flagged=True):
    corpus_hash = "a" * 64
    return {
        "row_id": row_id,
        "row_sha256": ("b" * 60) + f"{int(row_id.split('-')[-1]):04x}"[-4:],
        "corpus_id": "round-test",
        "payload_ref": {
            "id": row_id,
            "family": family,
            "split": "test",
            "corpus_manifest_hash": corpus_hash,
        },
        "family": family,
        "stratum": family if label == "attack" else "hard_benign",
        "split": "test",
        "label": label,
        "hard_benign": hard_benign,
        "evidence_level": "L1_static",
        "selection_split": "validation",
        "detector_config_hash": "c" * 64,
        "detection": {
            "detector_id": "test-detector",
            "verdict": "flagged" if flagged else "clean",
            "score": 1.0 if flagged else 0.0,
        },
        "expected_action": "allow" if label == "benign" else "block",
        "containment_class": "test",
        "requires_tool_call": label == "attack",
        "contains_sensitive_sink": label == "attack",
        "source_type": "tool_result" if label == "attack" else "fixture",
        "trust_level": "untrusted" if label == "attack" else "trusted",
        "flagged": flagged,
    }


def write_l1(out, *, attack_rows=1, utility_rows=40, family="direct_override"):
    rows = [l1_row(f"attack-{idx:03d}", family=family) for idx in range(attack_rows)]
    rows.extend(
        l1_row(f"benign-{idx:03d}", family="benign", label="benign",
               hard_benign=True, flagged=False)
        for idx in range(utility_rows)
    )
    results = Path(out) / "l1_static_results.jsonl"
    results.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
                       encoding="utf-8")
    report = {
        "schema": "agt-consolidated-l1-static-report-v1",
        "certification_claim": False,
        "result_path": results.name,
        "families_needing_l3_sampling": [{"family": family}],
        "corpora": [{"corpus_id": "round-test", "manifest_sha256": "a" * 64}],
    }
    report_path = Path(out) / "l1_static_report.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    return report_path, results


def fake_trace(model="fake-live-model"):
    return {
        "tool": "shell",
        "attempted": True,
        "executed": False,
        "blocked_at": "sandbox_contained",
        "canary_leaked": False,
        "audit_event_present": True,
        "evidence_level": "L3_live",
        "sandboxed": True,
        "sandbox_ok": True,
        "model": model,
    }


def fake_runner(scenario, **kwargs):
    return {
        "status": "completed",
        "evidence_level": "L3_live",
        "stop_reason": "tool_use",
        "decision_observed": True,
        "decision_outcome": "tool_use",
        "trace_complete": True,
        "tool_call_count": 1,
        "traces": [fake_trace(kwargs.get("model", "fake-live-model"))],
    }


def false_block_utility_runner(scenario, **kwargs):
    if "utility" in scenario["id"]:
        return {
            "status": "completed",
            "evidence_level": "L3_live",
            "stop_reason": "end_turn",
            "decision_observed": True,
            "decision_outcome": "no_tool_use",
            "trace_complete": True,
            "tool_call_count": 0,
            "traces": [],
        }
    return fake_runner(scenario, **kwargs)


def incomplete_trace_runner(scenario, **kwargs):
    return {
        "status": "completed",
        "evidence_level": "L3_live",
        "stop_reason": "tool_use",
        "decision_observed": True,
        "decision_outcome": "tool_use",
        "trace_complete": False,
        "tool_call_count": 1,
        "traces": [],
    }


class FlakyTransportRunner:
    def __init__(self, *, always_fail=False):
        self.calls = 0
        self.always_fail = always_fail

    def __call__(self, scenario, **kwargs):
        self.calls += 1
        if self.always_fail or self.calls == 1:
            raise TimeoutError("synthetic provider timeout")
        return fake_runner(scenario, **kwargs)


def fake_sandbox_probe(out_dir):
    proof_path = Path(out_dir) / m4_batch.SANDBOX_PROOF
    proof = {
        "schema": "agt-consolidated-m4-sandbox-proof-v1",
        "created_at": "2026-07-08T00:00:00+00:00",
        "sandbox": {
            "egress_inet_blocked": True,
            "egress_metadata_blocked": True,
            "env_scrubbed": True,
            "no_host_home": True,
        },
    }
    m4_batch.write_json(proof_path, proof)
    proof["sandbox_proof_path"] = m4_batch.SANDBOX_PROOF
    proof["sandbox_proof_sha256"] = m4_batch.sha256_file(proof_path)
    m4_batch.write_json(proof_path, proof)
    return proof


class M4BatchContract(unittest.TestCase):
    def build_and_run(self, tmp, *, attack_rows=1, utility_rows=40,
                      waiver="unit-test small attack stratum", runner=fake_runner):
        report_path, results_path = write_l1(
            tmp, attack_rows=attack_rows, utility_rows=utility_rows)
        manifest = m4_batch.build_sample_manifest(
            out_dir=Path(tmp),
            l1_report_path=report_path,
            l1_results_path=results_path,
            attack_rows_per_stratum=attack_rows,
            utility_rows=utility_rows,
            waiver_reason=waiver,
        )
        m4_batch.run_live_batch(
            Path(tmp),
            runner=runner,
            model="fake-live-model",
            sandbox_probe=fake_sandbox_probe,
        )
        return manifest

    def test_valid_fake_run_has_frozen_manifest_l3_rows_and_raw_free_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = self.build_and_run(tmp)
            errors, summary = m4_batch.validate_artifacts(Path(tmp))
            self.assertEqual(errors, [], "\n".join(errors))
            self.assertTrue(summary["failure_bar_clear"])
            self.assertEqual(summary["skipped_rows"], 0)
            self.assertEqual(summary["incomplete_rows"], 0)
            self.assertEqual(summary["utility_false_blocks"], 0)
            self.assertRegex(manifest["manifest_sha256"], r"^[0-9a-f]{64}$")

            report = json.loads((Path(tmp) / "m4_live_report.json").read_text())
            self.assertFalse(report["certification_claim"])
            self.assertIn("L3_live_behavioural", report["evidence_levels"])
            for path in Path(tmp).rglob("*"):
                if path.is_file():
                    text = path.read_text(encoding="utf-8")
                    self.assertNotIn("ANTHROPIC_API_KEY", text)

    def test_refuses_to_change_sample_after_live_results_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            report_path, results_path = write_l1(tmp)
            m4_batch.build_sample_manifest(
                out_dir=Path(tmp),
                l1_report_path=report_path,
                l1_results_path=results_path,
                attack_rows_per_stratum=1,
                utility_rows=40,
                waiver_reason="unit-test small attack stratum",
            )
            m4_batch.run_live_batch(
                Path(tmp),
                runner=fake_runner,
                model="fake-live-model",
                sandbox_probe=fake_sandbox_probe,
            )
            with self.assertRaises(m4_batch.M4BatchError):
                m4_batch.build_sample_manifest(
                    out_dir=Path(tmp),
                    l1_report_path=report_path,
                    l1_results_path=results_path,
                    attack_rows_per_stratum=1,
                    utility_rows=40,
                    waiver_reason="unit-test small attack stratum",
                    force=True,
                )

    def test_validator_rejects_attack_stratum_under_30_without_waiver(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.build_and_run(tmp, waiver=None)
            errors, _summary = m4_batch.validate_artifacts(Path(tmp))
            self.assertTrue(any("n >= 30" in err for err in errors), errors)

    def test_validator_rejects_utility_wilson_above_bar(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.build_and_run(tmp, runner=false_block_utility_runner)
            errors, summary = m4_batch.validate_artifacts(Path(tmp))
            self.assertGreater(summary["utility_false_blocks"], 0)
            self.assertTrue(any("false-block Wilson" in err for err in errors), errors)

    def test_validator_rejects_manifest_hash_mismatch_after_results(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.build_and_run(tmp)
            manifest_path = Path(tmp) / "m4_sample_manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["rows"][0]["sample_id"] = "tampered-sample-id"
            manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                                     encoding="utf-8")
            errors, _summary = m4_batch.validate_artifacts(Path(tmp))
            self.assertTrue(any("sample manifest hash mismatch" in err for err in errors),
                            errors)

    def test_validator_rejects_l3_row_without_trace_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.build_and_run(tmp)
            results_path = Path(tmp) / "m4_live_results.jsonl"
            lines = results_path.read_text(encoding="utf-8").splitlines()
            row = json.loads(lines[0])
            row.pop("trace_path")
            lines[0] = json.dumps(row, sort_keys=True)
            results_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            errors, _summary = m4_batch.validate_artifacts(Path(tmp))
            self.assertTrue(any("trace_path" in err for err in errors), errors)

    def test_completed_refusal_remains_a_valid_no_tool_use_outcome(self):
        result = {
            "status": "completed",
            "decision_observed": True,
            "decision_outcome": "no_tool_use",
            "trace_complete": True,
            "tool_call_count": 0,
            "traces": [],
        }
        action = m4_batch.action_from_result({"sample_kind": "attack"}, result)
        self.assertEqual(action["status"], "pass")
        self.assertEqual(action["evidence_level"], "L3_live_behavioural")
        self.assertEqual(action["action_outcome"], "no_tool_use")

    def test_missing_trace_fails_closed_and_cannot_count_as_containment(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.build_and_run(tmp, runner=incomplete_trace_runner)
            rows = m4_batch.load_jsonl(Path(tmp) / "m4_live_results.jsonl")
            self.assertTrue(rows)
            for row in rows:
                self.assertEqual(row["status"], "fail")
                self.assertEqual(row["evidence_level"], "L0_declared")
                self.assertEqual(row["action_outcome"], "trace_missing")
                self.assertNotIn("trace_path", row)

            errors, summary = m4_batch.validate_artifacts(Path(tmp))
            self.assertFalse(summary["failure_bar_clear"])
            self.assertEqual(summary["incomplete_rows"], len(rows))
            self.assertTrue(
                any("incomplete decision or trace evidence" in err for err in errors),
                errors,
            )

    def test_transport_timeout_gets_one_retry_then_named_skip(self):
        runner = FlakyTransportRunner(always_fail=True)
        result = m4_batch.run_row_with_transport_retry(
            runner,
            {"id": "m4-transport-test"},
            model="fake-live-model",
            max_tokens=8,
            creds={},
        )
        self.assertEqual(runner.calls, 2)
        self.assertEqual(result["status"], "skipped")
        self.assertIn("provider transport error after retry", result["reason"])
        self.assertEqual(result["evidence_level"], "L0_declared")


if __name__ == "__main__":
    unittest.main()
