#!/usr/bin/env python3
"""BDD tests for Gate 1 trained head (round-6 M2)."""

import json
import unittest

import numpy as np

import common as C
import head as H


class TestHead(unittest.TestCase):
    def setUp(self):
        rng = np.random.RandomState(0)
        # separable-ish synthetic embeddings
        self.X = np.vstack([rng.normal(0, 1, (200, 16)), rng.normal(1.5, 1, (200, 16))])
        self.y = np.array([0] * 200 + [1] * 200)

    def test_trains_and_scores(self):
        h = H.train_head(self.X, self.y, {"family": "lr", "C": 1.0})
        s = h.scores(self.X)
        self.assertEqual(s.shape, (400,))
        self.assertTrue(np.all((s >= 0) & (s <= 1)))
        self.assertGreater(C.roc_auc(self.y, s), 0.8)

    def test_determinism(self):
        a = H.train_head(self.X, self.y, {"family": "lr", "C": 1.0}).scores(self.X)
        b = H.train_head(self.X, self.y, {"family": "lr", "C": 1.0}).scores(self.X)
        np.testing.assert_array_equal(a, b)

    def test_grid_cap(self):
        self.assertLessEqual(len(H.model_specs()), 24)

    def test_lr_coefficients_exported(self):
        h = H.train_head(self.X, self.y, {"family": "lr", "C": 1.0})
        c = h.coefficients()
        self.assertEqual(len(c["weights"]), 16)
        self.assertIn("intercept", c)

    def test_hgb_no_coefficients(self):
        h = H.train_head(self.X, self.y, {"family": "hgb", "max_depth": 3, "learning_rate": 0.1})
        self.assertIsNone(h.coefficients())


class TestArtifacts(unittest.TestCase):
    """Run only if M2 artifacts exist."""

    def setUp(self):
        self.d = C.ROOT / "artifacts/round6-cascade/m2-head"
        if not (self.d / "freeze-record.json").exists():
            self.skipTest("m2 artifacts not present")

    def test_feature_source_embeddings_only(self):
        fr = json.loads((self.d / "freeze-record.json").read_text())
        self.assertEqual(fr["feature_source"], ["normalized_text_embedding"])

    def test_no_vectors_in_per_row(self):
        for f in ("validation-per-row.jsonl", "test-per-row.jsonl"):
            for ln in (self.d / f).read_text().splitlines():
                if ln.strip():
                    obj = json.loads(ln)
                    self.assertNotIn("embedding", obj)
                    self.assertNotIn("text", obj)

    def test_lofo_eight_folds(self):
        lofo = json.loads((self.d / "lofo-metrics.json").read_text())
        self.assertEqual(len(lofo["folds"]), 8)

    def test_freeze_before_test(self):
        fr = json.loads((self.d / "freeze-record.json").read_text())
        self.assertIsNotNone(fr["test_scoring_started_at"])
        self.assertLessEqual(fr["freeze_record_written_at"], fr["test_scoring_started_at"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
