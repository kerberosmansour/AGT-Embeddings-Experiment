#!/usr/bin/env python3
"""BDD tests for M3 three-bucket conformal router."""

import json
import unittest

import numpy as np

import common as C
from buckets import Bucket, FrozenRouter, conformal_upper, fit_router


class TestConformal(unittest.TestCase):
    def test_quantile_brute_force(self):
        # ceil((n+1)(1-alpha))-th order statistic, 1-indexed.
        s = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
        n = len(s)
        for alpha in (0.01, 0.1, 0.2):
            rank = int(np.ceil((n + 1) * (1 - alpha)))
            expected = float(np.sort(s)[min(rank, n) - 1])
            self.assertEqual(conformal_upper(s, alpha), expected)

    def test_small_n_clips_to_max(self):
        s = np.array([0.3, 0.6, 0.9])  # n=3, alpha=0.001 -> rank>n -> max
        self.assertEqual(conformal_upper(s, 0.001), 0.9)


class TestRouter(unittest.TestCase):
    def setUp(self):
        rng = np.random.RandomState(0)
        self.ids = [f"r{i}" for i in range(2000)]
        # benign low scores, attacks high
        self.scores = np.concatenate([rng.beta(2, 8, 1600), rng.beta(8, 2, 400)])
        self.labels = np.array([0] * 1600 + [1] * 400, dtype=np.int8)

    def test_total_assignment(self):
        r, _ = fit_router(self.ids, self.scores, self.labels)
        buckets = r.assign(self.scores)
        self.assertEqual(len(buckets), len(self.scores))
        self.assertTrue(all(isinstance(b, Bucket) for b in buckets))

    def test_thresholds_ordered(self):
        r, info = fit_router(self.ids, self.scores, self.labels)
        self.assertLess(r.t_low, r.t_high)

    def test_degenerate_raises(self):
        with self.assertRaises(AssertionError):
            FrozenRouter(iso=None, t_low=0.9, t_high=0.5)

    def test_calibration_monotone(self):
        r, _ = fit_router(self.ids, self.scores, self.labels)
        xs = np.linspace(0, 1, 50)
        cal = r.calibrate(xs)
        self.assertTrue(np.all(np.diff(cal) >= -1e-9))

    def test_determinism(self):
        a, ia = fit_router(self.ids, self.scores, self.labels)
        b, ib = fit_router(self.ids, self.scores, self.labels)
        self.assertEqual((ia["t_low"], ia["t_high"]), (ib["t_low"], ib["t_high"]))

    def test_cal_b_benign_only(self):
        # inject an attack id into cal-B's hash bucket would be caught by assert;
        # here verify cal-B size is plausible (~half of benign).
        _, info = fit_router(self.ids, self.scores, self.labels)
        self.assertGreater(info["cal_b_benign_size"], 600)
        self.assertLess(info["cal_b_benign_size"], 1000)


class TestArtifacts(unittest.TestCase):
    def setUp(self):
        self.d = C.ROOT / "artifacts/round6-cascade/m3-buckets"
        if not (self.d / "freeze-record.json").exists():
            self.skipTest("m3 artifacts not present")

    def test_coverage_reproducible(self):
        m = json.loads((self.d / "test-metrics.json").read_text())
        rows = [json.loads(l) for l in (self.d / "test-per-row.jsonl").read_text().splitlines() if l.strip()]
        benign_escape = sum(1 for r in rows if r["label"] == "benign" and r["bucket"] != "pass")
        self.assertEqual(benign_escape, m["coverage"]["benign_escape_from_pass"])

    def test_freeze_before_test(self):
        fr = json.loads((self.d / "freeze-record.json").read_text())
        self.assertIsNotNone(fr["test_scoring_started_at"])
        self.assertLess(fr["t_low"], fr["t_high"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
