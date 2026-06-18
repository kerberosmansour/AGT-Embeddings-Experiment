#!/usr/bin/env python3
"""Pseudocode only: no live Goose invocation in this spike."""

def run_scenario_with_goose_contract(scenario):
    return {
        "scenario_id": scenario["id"],
        "status": "not_run",
        "evidence_level": "L0_declared",
        "adapter": "goose",
        "limits": {"max_turns": 4, "timeout_seconds": 30, "mock_tools_only": True},
        "trace": [],
        "cleanup": "no live session created",
    }
