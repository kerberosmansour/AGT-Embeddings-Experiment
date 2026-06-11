#!/usr/bin/env python3
"""Gate 1 — trained classifier head over normalized-text embeddings (round-6 M2).

A trained decision surface (logistic regression / histogram gradient boosting)
over the same bge-small embeddings the round-4 kNN margin used. Pinned seeds,
frozen hyperparameters, auditable LR coefficients.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression

SEED = 20260611

# <=24 config grid (hard cap, enumerated in freeze record).
LR_C_GRID = [0.01, 0.1, 1.0, 10.0]
HGB_GRID = [
    {"max_depth": 3, "learning_rate": 0.1},
    {"max_depth": 6, "learning_rate": 0.1},
    {"max_depth": 3, "learning_rate": 0.05},
    {"max_depth": 6, "learning_rate": 0.05},
]


def model_specs() -> list[dict]:
    specs = [{"family": "lr", "C": c} for c in LR_C_GRID]
    specs += [{"family": "hgb", **g} for g in HGB_GRID]
    assert len(specs) <= 24, "grid exceeds 24-config cap"
    return specs


def build(spec: dict):
    if spec["family"] == "lr":
        return LogisticRegression(
            C=spec["C"], class_weight="balanced", max_iter=2000, random_state=SEED
        )
    if spec["family"] == "hgb":
        return HistGradientBoostingClassifier(
            max_depth=spec["max_depth"], learning_rate=spec["learning_rate"],
            max_iter=200, random_state=SEED,
        )
    raise ValueError(spec)


@dataclass
class FrozenHead:
    spec: dict
    model: object

    def scores(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(X)[:, 1]

    def coefficients(self) -> dict | None:
        if self.spec["family"] == "lr":
            return {
                "intercept": float(self.model.intercept_[0]),
                "weights": [round(float(w), 6) for w in self.model.coef_[0]],
            }
        return None


def train_head(X: np.ndarray, y: np.ndarray, spec: dict) -> FrozenHead:
    m = build(spec)
    m.fit(X, y)
    return FrozenHead(spec, m)
