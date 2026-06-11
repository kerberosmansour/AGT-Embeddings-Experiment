#!/usr/bin/env python3
"""Two-inspector ensemble — exploratory sandbox play (reproducible).

Reuses committed artifacts only (no model run, no new data):
  - kNN margin + zero-FP decision: artifacts/round6-cascade/m1-gate0/test-per-row.jsonl
  - trained head score (2nd model): artifacts/round6-cascade/m2-head/test-per-row.jsonl
  - governance facts: corpus/round4

Idea: two readings of the same request — a precision-first inspector (zero-FP
line) and a recall-first inspector (Youden line). The band between them is the
"disagreement zone"; resolve it with an independent signal (the 2nd model, or
structural facts). Reports the two recommendations:
  Rec B  — keep 0% FP, still beat Experiment 1's 81%.
  Rec A  — spend ~0.3% FP for near-total catch.

EXPLORATORY: synthetic, labels-perfect ceiling. See FINDINGS.md for caveats.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
M1 = ROOT / "artifacts/round6-cascade/m1-gate0/test-per-row.jsonl"
M2 = ROOT / "artifacts/round6-cascade/m2-head/test-per-row.jsonl"
M2FR = ROOT / "artifacts/round6-cascade/m2-head/freeze-record.json"
CORPUS = ROOT / "corpus/round4/injection-round4-large.jsonl"
KNN_ZEROFP = 0.08294189  # validation-frozen (round-6 M1)


def load():
    m1 = {json.loads(l)["id"]: json.loads(l) for l in M1.read_text().splitlines() if l.strip()}
    m2 = {json.loads(l)["id"]: json.loads(l) for l in M2.read_text().splitlines() if l.strip()}
    corp = {}
    for ln in CORPUS.read_text().splitlines():
        if ln.strip():
            r = json.loads(ln)
            if r["split"] == "test":
                corp[r["id"]] = r
    ids = [i for i in m1 if i in m2]
    y = np.array([0 if m1[i]["label"] == "benign" else 1 for i in ids])
    knn = np.array([m1[i]["margin"] for i in ids])
    head = np.array([m2[i]["head_score"] for i in ids])
    unt = np.array([corp[i].get("trust_level") == "untrusted" for i in ids])
    tool = np.array([bool(corp[i].get("requires_tool_call")) for i in ids])
    sink = np.array([bool(corp[i].get("contains_sensitive_sink")) for i in ids])
    return y, knn, head, unt, tool, sink


def main():
    y, knn, head, unt, tool, sink = load()
    head_cut = json.loads(M2FR.read_text())["cutoff_0p1pct_fpr"]["threshold"]  # validation-frozen
    R1 = unt & tool
    handle = unt | tool | sink
    band = (knn > 0.0) & (knn <= KNN_ZEROFP)  # disagreement band
    base = (knn > KNN_ZEROFP) | R1            # Experiment 1

    def mc(b):
        return 100 * b[y == 1].mean(), 100 * b[y == 0].mean()

    rows = [
        ("Experiment 1 baseline", base),
        ("Rec B  : base OR (band AND 2nd-model agrees)", base | (band & (head > head_cut))),
        ("Rec B+ : base OR (band AND (tool OR 2nd-model))", base | (band & (tool | (head > head_cut)))),
        ("Rec A  : base OR (band AND any structural fact)", base | (band & handle)),
    ]
    print(f"disagreement band: {int((band & (y==0)).sum())} benign, {int((band & (y==1)).sum())} attacks")
    print(f"benign in band flagged by 2nd model (must be 0 for Rec B): "
          f"{int((band & (y==0) & (head>head_cut)).sum())}")
    for name, b in rows:
        c, f = mc(b)
        print(f"  {name:<50s} catch {c:5.1f}%  FP {f:5.2f}%")


if __name__ == "__main__":
    main()
