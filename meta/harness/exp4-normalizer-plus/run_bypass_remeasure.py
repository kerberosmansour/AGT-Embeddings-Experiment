#!/usr/bin/env python3
"""Ticket #10 — re-measure per-bypass-class catch with the EXTENDED Gate-0
normalizer (encoding + rot13), at the same FP-zero protocol as round-6 M1.

Re-embeds the corpus with the updated normalize.py (the cache key changes
because normalize.py changed), selects the FP-zero threshold on validation,
scores the frozen test split once, and prints a before/after per-bypass-class
table vs the committed round-6 m1-gate0 baseline. Writes to a NEW artifact dir
(does not touch the committed m1 artifacts).
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "meta/harness/round6-cascade"))
import common as C  # noqa: E402
from normalize import normalize  # noqa: E402

OUT = ROOT / "artifacts/exp4-normalizer-plus"
BASELINE = ROOT / "artifacts/round6-cascade/m1-gate0/test-metrics.json"
K = 5
OBF_CONTROLS = {"benign_obfuscation_control", "benign_compact_obfuscation_control",
                "high_entropy_structured_data"}


def bypass_catch(rows, labels, preds):
    g = defaultdict(lambda: [0, 0])
    for i, r in enumerate(rows):
        if labels[i] == 1:
            g[str(r.get("bypass_class"))][1] += 1
            g[str(r.get("bypass_class"))][0] += int(preds[i])
    return {k: v[0] / v[1] for k, v in g.items()}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    C.verify_corpus()
    exemplar = C.load_rows({"exemplar_bank"})
    validation = C.load_rows({"validation"})
    test = C.load_rows({"test"})
    model = C.make_model()

    def emb(rows):
        return C.embed_texts(model, [normalize(r["text"]).text for r in rows])

    ex = emb(exemplar)
    ex_lab = [C.label_for(r) for r in exemplar]
    pos = ex[[i for i, l in enumerate(ex_lab) if l == "attack"]]
    neg = ex[[i for i, l in enumerate(ex_lab) if l == "benign"]]

    va = emb(validation); va_m = C.knn_margin(va, pos, neg, K); va_y = C.labels_array(validation)
    tau = C.select_fp_zero_tau(va_y, va_m)["threshold_tau"]
    te = emb(test); te_m = C.knn_margin(te, pos, neg, K); te_y = C.labels_array(test)
    preds = (te_m > tau).astype(np.int8)

    after = bypass_catch(test, te_y, preds)
    base = json.loads(BASELINE.read_text())
    before = {k: v["catch_rate"] for k, v in base["bypass_class_catch"].items()}

    # benign obfuscation-control FP (must stay ~0)
    obf_fp = sum(1 for i, r in enumerate(test)
                 if te_y[i] == 0 and preds[i] == 1 and r.get("benign_subclass") in OBF_CONTROLS)
    overall_fp = int(((te_y == 0) & (preds == 1)).sum())
    overall_recall = float(te_m[te_y == 1].__gt__(tau).mean())

    table = []
    for bc in sorted(set(before) | set(after)):
        b = before.get(bc); a = after.get(bc)
        table.append({"bypass_class": bc, "before": b, "after": a,
                      "delta": (a - b) if (a is not None and b is not None) else None})
    result = {
        "tau": tau, "overall_recall": overall_recall,
        "overall_benign_fp": overall_fp, "obf_control_fp": obf_fp,
        "bypass_before_after": table,
    }
    C.write_json(OUT / "bypass-remeasure.json", result)

    print(f"[#10] tau={tau:.5f}  overall recall {base['attack_recall']:.3f} -> {overall_recall:.3f} "
          f"| benign FP {overall_fp}  obf-control FP {obf_fp}")
    print(f"  {'bypass_class':<22}{'before':>8}{'after':>8}{'delta':>8}")
    for row in table:
        b = f"{row['before']:.3f}" if row['before'] is not None else "  -"
        a = f"{row['after']:.3f}" if row['after'] is not None else "  -"
        d = f"{row['delta']:+.3f}" if row['delta'] is not None else "  -"
        star = "  <--" if (row['delta'] or 0) > 0.02 else ""
        print(f"  {row['bypass_class']:<22}{b:>8}{a:>8}{d:>8}{star}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
