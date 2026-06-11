#!/usr/bin/env python3
"""Gate 2 — tiered cross-modal adjudication of the uncertain lane (round-6 M4).

Four arms over uncertain-lane rows:
  control : calibrated score only
  floor   : + requires_tool_call + coarse_source (AGT-guaranteed fields)
  ceiling : + contains_sensitive_sink + full source_type (integration-dependent)
  rule    : deterministic, zero-parameter (no model)

Coarsening is fail-closed (absent field -> least-trusted / sensitive), matching
AGT IFC behaviour. Ground-truth fields (expected_action, risk_level) are never
referenced. See docs/methodology/round6-corpus-to-agt-field-mapping.md.
"""

from __future__ import annotations

import numpy as np
from sklearn.linear_model import LogisticRegression

SEED = 40260611
C_GRID = [0.1, 1.0, 10.0]

COARSE_SOURCE_VALUES = ("user", "tool_result", "other")
SOURCE_TYPE_VALUES = ("user", "document", "rag_chunk", "ticket", "tool_result", "memory")
TRUST_VALUES = ("authenticated_user", "tool_output", "untrusted")

# Feature manifests (asserted at matrix build; ground-truth fields absent).
FEATURE_MANIFESTS = {
    "control": ["calibrated_score"],
    "floor": ["calibrated_score", "requires_tool_call", "coarse_source"],
    "ceiling": ["calibrated_score", "requires_tool_call", "coarse_source",
                "contains_sensitive_sink", "source_type"],
    "rule": ["requires_tool_call", "coarse_source"],
}
GROUND_TRUTH = {"expected_action", "risk_level"}


def coarse_source(meta: dict, fail: list) -> str:
    """Fail-closed derivation of AGT-style coarse source."""
    st = meta.get("source_type", None)
    tl = meta.get("trust_level", None)
    if st is None and tl is None:
        fail.append("coarse_source")
        return "other"
    if tl is not None and tl not in TRUST_VALUES:
        raise ValueError(f"unknown trust_level {tl!r}")
    if st is not None and st not in SOURCE_TYPE_VALUES:
        raise ValueError(f"unknown source_type {st!r}")
    if st == "tool_result" or tl == "tool_output":
        return "tool_result"
    if tl == "authenticated_user" or st == "user":
        return "user"
    return "other"


def coarsen(meta: dict, tier: str, fail: list) -> dict:
    """Return the feature dict for a tier. meta carries only allowed columns."""
    leaked = set(meta) & GROUND_TRUTH
    assert not leaked, f"ground-truth field in Gate-2 input: {leaked}"
    rtc = meta.get("requires_tool_call", None)
    if rtc is None:
        fail.append("requires_tool_call")
        rtc = True  # fail-closed: assume an action is requested
    cs = coarse_source(meta, fail)
    out = {"requires_tool_call": int(bool(rtc)), "coarse_source": cs}
    if tier == "ceiling":
        sink = meta.get("contains_sensitive_sink", None)
        if sink is None:
            fail.append("contains_sensitive_sink")
            sink = True  # fail-closed: assume sensitive
        out["contains_sensitive_sink"] = int(bool(sink))
        st = meta.get("source_type", None)
        out["source_type"] = st if st in SOURCE_TYPE_VALUES else "other"
    return out


def _onehot(value, values):
    return [1.0 if value == v else 0.0 for v in values]


def feature_matrix(scores: np.ndarray, metas: list[dict], tier: str, fail: list) -> np.ndarray:
    rows = []
    for s, m in zip(scores, metas):
        f = coarsen(m, tier, fail)
        if tier == "control":
            rows.append([s])
            continue
        vec = [s, float(f["requires_tool_call"])]
        vec += _onehot(f["coarse_source"], COARSE_SOURCE_VALUES)
        if tier == "ceiling":
            vec.append(float(f["contains_sensitive_sink"]))
            vec += _onehot(f["source_type"], SOURCE_TYPE_VALUES)
        rows.append(vec)
    X = np.asarray(rows, dtype=float)
    # assert declared dimensionality
    expected = {"control": 1, "floor": 2 + len(COARSE_SOURCE_VALUES),
                "ceiling": 3 + len(COARSE_SOURCE_VALUES) + len(SOURCE_TYPE_VALUES)}[tier]
    assert X.shape[1] == expected, f"{tier} dim {X.shape[1]} != {expected}"
    return X


def rule_decision(metas: list[dict], fail: list) -> np.ndarray:
    """Deterministic flag: requires_tool_call AND coarse_source != user."""
    out = []
    for m in metas:
        f = coarsen(m, "rule", fail)
        out.append(1 if (f["requires_tool_call"] and f["coarse_source"] != "user") else 0)
    return np.array(out, dtype=np.int8)


def train_arm(X: np.ndarray, y: np.ndarray, C: float) -> LogisticRegression:
    m = LogisticRegression(C=C, class_weight="balanced", max_iter=2000, random_state=SEED)
    m.fit(X, y)
    return m
