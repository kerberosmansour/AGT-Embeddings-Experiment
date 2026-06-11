#!/usr/bin/env python3
"""Pin down the winning variant: Rec B (head as band tie-breaker) vs co-equal
(head everywhere), each with the NEW normalizer. All validation-frozen.

base    = (kNN > knn_zeroFP) OR R1                         [Experiment-1 shape]
Rec B   = base OR (band AND head>head_cut)                 [head only in the disagreement band]
co-equal= base OR (head>head_cut)                          [head everywhere]
band    = knn_youden < margin <= knn_zeroFP
All thresholds selected on validation; test scored once.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "meta/harness/round6-cascade"))
import common as C  # noqa: E402
import head as H  # noqa: E402
from normalize import normalize  # noqa: E402

K = 5
HGB = {"family": "hgb", "max_depth": 3, "learning_rate": 0.1}


def youden_tau(y, score):
    o = np.argsort(-score); P = y.sum(); N = (y == 0).sum(); tp = fp = 0; best = (-1, score.max())
    for i in o:
        if y[i] == 1:
            tp += 1
        else:
            fp += 1
        J = tp / P - fp / N
        if J > best[0]:
            best = (J, score[i])
    return best[1]


def main() -> int:
    C.verify_corpus()
    ex = C.load_rows({"exemplar_bank"}); va = C.load_rows({"validation"}); te = C.load_rows({"test"})
    model = C.make_model()
    emb = lambda rows: C.embed_texts(model, [normalize(r["text"]).text for r in rows])
    Xex, yex = emb(ex), C.labels_array(ex)
    Xva, yva = emb(va), C.labels_array(va)
    Xte, yte = emb(te), C.labels_array(te)

    pos, neg = Xex[yex == 1], Xex[yex == 0]
    va_m, te_m = C.knn_margin(Xva, pos, neg, K), C.knn_margin(Xte, pos, neg, K)
    knn_zfp = C.select_fp_zero_tau(yva, va_m)["threshold_tau"]
    knn_y = youden_tau(yva, va_m)

    headm = H.train_head(Xex, yex, HGB)
    va_h, te_h = headm.scores(Xva), headm.scores(Xte)
    head_cut = C.tpr_at_fpr(yva, va_h, 0.001)["threshold"]

    unt = np.array([r.get("trust_level") == "untrusted" for r in te])
    tool = np.array([bool(r.get("requires_tool_call")) for r in te])
    R1 = unt & tool

    base = (te_m > knn_zfp) | R1
    band = (te_m > knn_y) & (te_m <= knn_zfp)
    recB = base | (band & (te_h > head_cut))
    coeq = base | (te_h > head_cut)

    def mc(b):
        return 100 * b[yte == 1].mean(), 100 * b[yte == 0].mean()

    print("NEW normalizer, all validation-frozen:")
    for name, b in [("base (Exp-1 shape: kNN_zeroFP OR R1)", base),
                    ("Rec B  (head as tie-breaker IN BAND)", recB),
                    ("co-equal (head EVERYWHERE)", coeq)]:
        c, f = mc(b)
        print(f"  {name:<42} catch {c:5.1f}%  FP {f:.2f}%")
    print("\n  (old normalizer reference: base 81.0% | Rec B 87.2% | co-equal 87.2%, all @ 0% FP)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
