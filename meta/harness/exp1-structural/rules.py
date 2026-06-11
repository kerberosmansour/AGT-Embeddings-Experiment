#!/usr/bin/env python3
"""Experiment 1 — deterministic structural block rules (captain-obvious only).

Each rule fires on STRUCTURAL FACTS only (provenance / sink / tool / source),
never on the meaning of the text — so it is safe to set to auto-block with no
human review. Ground-truth fields (expected_action, risk_level) are forbidden
inputs and asserted out.

Rule inputs (the only allowed fields):
  requires_tool_call : bool
  contains_sensitive_sink : bool
  source_type : user|document|rag_chunk|ticket|tool_result|memory
  trust_level : authenticated_user|tool_output|untrusted
"""

from __future__ import annotations

ALLOWED_FIELDS = frozenset(
    {"requires_tool_call", "contains_sensitive_sink", "source_type", "trust_level"}
)
GROUND_TRUTH = frozenset({"expected_action", "risk_level"})

SOURCE_TYPE_VALUES = ("user", "document", "rag_chunk", "ticket", "tool_result", "memory")
TRUST_VALUES = ("authenticated_user", "tool_output", "untrusted")


def _check(meta: dict) -> None:
    leaked = set(meta) & GROUND_TRUTH
    assert not leaked, f"ground-truth field passed to a structural rule: {leaked}"


def coarse_source(meta: dict) -> str:
    """AGT-realistic 3-value collapse (fail-closed). See the round-6 mapping doc."""
    st = meta.get("source_type")
    tl = meta.get("trust_level")
    if st is None and tl is None:
        return "other"
    if st == "tool_result" or tl == "tool_output":
        return "tool_result"
    if tl == "authenticated_user" or st == "user":
        return "user"
    return "other"


def R1(meta: dict) -> bool:
    """Untrusted source drives a tool call."""
    _check(meta)
    return bool(meta.get("trust_level") == "untrusted" and meta.get("requires_tool_call"))


def R2(meta: dict) -> bool:
    """Sensitive sink touched by a non-user source."""
    _check(meta)
    return bool(meta.get("contains_sensitive_sink") and coarse_source(meta) != "user")


def R3(meta: dict) -> bool:
    """Lethal trifecta (strict): untrusted AND tool AND sensitive sink."""
    _check(meta)
    return bool(
        meta.get("trust_level") == "untrusted"
        and meta.get("requires_tool_call")
        and meta.get("contains_sensitive_sink")
    )


def R4(meta: dict) -> bool:
    """Any-rule union (R1 OR R2) — the deployed structural-block decision."""
    return R1(meta) or R2(meta)


def has_structural_handle(meta: dict) -> bool:
    """Does the row present ANY structural surface a rule could grab?"""
    _check(meta)
    return bool(
        meta.get("requires_tool_call")
        or meta.get("contains_sensitive_sink")
        or meta.get("trust_level") == "untrusted"
        or coarse_source(meta) != "user"
    )


RULES = {"R1": R1, "R2": R2, "R3": R3, "R4": R4}
