#!/usr/bin/env python3
"""Three-bucket conformal router over calibrated head scores (round-6 M3).

Split-conformal on the benign class:
  - cal-A = half of validation benign + ALL validation attack -> isotonic fit.
  - cal-B = the other half of validation benign (benign-only) -> conformal
    quantiles for the bucket thresholds. cal-B never enters any fitting path.

Buckets by calibrated P(attack):  score < t_low -> PASS; > t_high -> FLAG;
otherwise UNCERTAIN. Thresholds are conformal order statistics over cal-B benign
calibrated scores at pre-registered budgets (alpha_pass, alpha_flag).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import Enum

import numpy as np
from sklearn.isotonic import IsotonicRegression

ALPHA_PASS = 0.01   # <= 1% of benign may escape the PASS lane
ALPHA_FLAG = 0.001  # <= 0.1% of benign may reach the FLAG lane
SPLIT_SEED = 70260611


class Bucket(str, Enum):
    PASS = "pass"
    UNCERTAIN = "uncertain"
    FLAG = "flag"


def _stable_half(ids: list[str]) -> np.ndarray:
    """Deterministic 50/50 split mask by hash of id (no Math.random)."""
    out = []
    for i in ids:
        h = int(hashlib.sha256(f"{SPLIT_SEED}:{i}".encode()).hexdigest(), 16)
        out.append(h % 2 == 0)
    return np.array(out)


def conformal_upper(cal_scores: np.ndarray, alpha: float) -> float:
    """The ceil((n+1)(1-alpha))-th order statistic (1-indexed) of cal_scores.

    Guarantees <= alpha of an exchangeable benign stream exceeds the threshold.
    """
    n = len(cal_scores)
    s = np.sort(cal_scores)
    rank = int(np.ceil((n + 1) * (1 - alpha)))
    if rank > n:  # alpha too small for this n -> use the max (most conservative)
        return float(s[-1])
    return float(s[rank - 1])


@dataclass
class FrozenRouter:
    iso: IsotonicRegression
    t_low: float
    t_high: float

    def __post_init__(self):
        assert self.t_low < self.t_high, f"t_low >= t_high ({self.t_low} >= {self.t_high})"

    def calibrate(self, raw: np.ndarray) -> np.ndarray:
        return self.iso.predict(raw)

    def assign(self, raw: np.ndarray) -> list[Bucket]:
        cal = self.calibrate(raw)
        out = []
        for s in cal:
            if s < self.t_low:
                out.append(Bucket.PASS)
            elif s > self.t_high:
                out.append(Bucket.FLAG)
            else:
                out.append(Bucket.UNCERTAIN)
        return out


def fit_router(val_ids: list[str], val_scores: np.ndarray, val_labels: np.ndarray) -> tuple[FrozenRouter, dict]:
    benign = val_labels == 0
    half = _stable_half(val_ids)
    cal_a = benign & half        # half of benign ...
    cal_a = cal_a | (val_labels == 1)   # ... + all attacks  -> isotonic fit
    cal_b = benign & ~half       # other half of benign -> conformal (benign only)

    assert not np.any(cal_b & (val_labels == 1)), "cal-B contains attacks"
    assert not np.any(cal_a & cal_b & benign), "cal-A and cal-B benign overlap"

    iso = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
    iso.fit(val_scores[cal_a], val_labels[cal_a])

    cal_b_cal = iso.predict(val_scores[cal_b])
    t_low = conformal_upper(cal_b_cal, ALPHA_PASS)
    t_high = conformal_upper(cal_b_cal, ALPHA_FLAG)

    info = {
        "alpha_pass": ALPHA_PASS, "alpha_flag": ALPHA_FLAG,
        "cal_a_size": int(cal_a.sum()), "cal_b_benign_size": int(cal_b.sum()),
        "t_low": t_low, "t_high": t_high, "split_seed": SPLIT_SEED,
    }
    return FrozenRouter(iso, t_low, t_high), info
