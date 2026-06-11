#!/usr/bin/env python3
"""BDD tests for M4 Gate-2 tiered ablation."""

import json
import unittest

import numpy as np

import common as C
import gate2 as G


class TestCoarsen(unittest.TestCase):
    def test_fail_closed_trust_absent(self):
        fail = []
        f = G.coarsen({"source_type": None, "trust_level": None, "requires_tool_call": True}, "floor", fail)
        self.assertEqual(f["coarse_source"], "other")
        self.assertIn("coarse_source", fail)

    def test_fail_closed_sink_absent(self):
        fail = []
        f = G.coarsen({"source_type": "document", "trust_level": "untrusted",
                       "requires_tool_call": True}, "ceiling", fail)
        self.assertEqual(f["contains_sensitive_sink"], 1)  # fail-closed sensitive
        self.assertIn("contains_sensitive_sink", fail)

    def test_unknown_value_hard_error(self):
        with self.assertRaises(ValueError):
            G.coarsen({"trust_level": "admin", "source_type": "user"}, "floor", [])

    def test_coarse_source_mapping(self):
        self.assertEqual(G.coarse_source({"source_type": "tool_result", "trust_level": "tool_output"}, []), "tool_result")
        self.assertEqual(G.coarse_source({"source_type": "user", "trust_level": "authenticated_user"}, []), "user")
        self.assertEqual(G.coarse_source({"source_type": "document", "trust_level": "untrusted"}, []), "other")

    def test_ground_truth_assertion(self):
        with self.assertRaises(AssertionError):
            G.coarsen({"expected_action": "block", "requires_tool_call": True}, "floor", [])


class TestFeatureMatrix(unittest.TestCase):
    def setUp(self):
        self.metas = [{"source_type": "document", "trust_level": "untrusted",
                       "requires_tool_call": True, "contains_sensitive_sink": False}] * 5
        self.scores = np.array([0.5] * 5)

    def test_dims(self):
        self.assertEqual(G.feature_matrix(self.scores, self.metas, "control", []).shape[1], 1)
        self.assertEqual(G.feature_matrix(self.scores, self.metas, "floor", []).shape[1], 5)
        self.assertEqual(G.feature_matrix(self.scores, self.metas, "ceiling", []).shape[1], 12)

    def test_manifest_no_ground_truth(self):
        for arm, feats in G.FEATURE_MANIFESTS.items():
            self.assertEqual(set(feats) & G.GROUND_TRUTH, set())


class TestRuleArm(unittest.TestCase):
    def test_deterministic_rule(self):
        metas = [
            {"source_type": "document", "trust_level": "untrusted", "requires_tool_call": True},   # flag
            {"source_type": "user", "trust_level": "authenticated_user", "requires_tool_call": True},  # no (user)
            {"source_type": "document", "trust_level": "untrusted", "requires_tool_call": False},  # no (no tool)
        ]
        out = G.rule_decision(metas, [])
        self.assertEqual(list(out), [1, 0, 0])


class TestArtifacts(unittest.TestCase):
    def setUp(self):
        self.d = C.ROOT / "artifacts/round6-cascade/m4-gate2"
        if not (self.d / "freeze-record.json").exists():
            self.skipTest("m4 artifacts not present")

    def test_freeze_no_ground_truth_features(self):
        fr = json.loads((self.d / "freeze-record.json").read_text())
        for arm, feats in fr["feature_manifests"].items():
            self.assertEqual(set(feats) & {"expected_action", "risk_level"}, set())

    def test_per_row_has_all_arms(self):
        for ln in (self.d / "test-per-row.jsonl").read_text().splitlines():
            if ln.strip():
                o = json.loads(ln)
                for k in ("control_flag", "floor_flag", "ceiling_flag", "rule_flag"):
                    self.assertIn(k, o)
                break


if __name__ == "__main__":
    unittest.main(verbosity=2)
