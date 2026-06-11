#!/usr/bin/env python3
"""Validator: recompute by-technique/by-benign rates from per-row; check hygiene."""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "meta/harness/round6-cascade"))
import common as C  # noqa: E402

ART = ROOT / "artifacts/exp1-structural"
CONTROLS = ["embedding_zeroFP", "R1", "R2", "R3", "R4", "structural_block", "combined"]
GROUND_TRUTH = {"expected_action", "risk_level"}


def fail(m):
    print("FAIL:", m)
    sys.exit(1)


def main():
    rows = [json.loads(l) for l in (ART / "test-per-row.jsonl").read_text().splitlines() if l.strip()]
    # hygiene
    for r in rows:
        if set(r) & GROUND_TRUTH:
            fail(f"ground-truth field in per-row {r['id']}")
        if C.ensure_metadata_only(r):
            fail(f"forbidden field in per-row {r['id']}")
    # recompute by-technique and compare
    bt = json.loads((ART / "by-technique.json").read_text())["per_family"]
    grp = defaultdict(lambda: {c: 0 for c in CONTROLS} | {"rows": 0})
    for r in rows:
        if r["label"] != "attack":
            continue
        g = r["attack_class"]
        grp[g]["rows"] += 1
        for c in CONTROLS:
            grp[g][c] += int(r[c])
    for fam, d in grp.items():
        for c in CONTROLS:
            recomputed = d[c] / d["rows"]
            stored = bt[fam][c]["rate"]
            if abs(recomputed - stored) > 1e-9:
                fail(f"{fam}/{c}: stored {stored} != recomputed {recomputed}")
    print(f"OK exp1: {len(rows)} rows; by-technique rates reproduce exactly for {len(grp)} families")
    print("VALIDATION PASS")


if __name__ == "__main__":
    main()
