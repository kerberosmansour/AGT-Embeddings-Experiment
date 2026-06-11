#!/usr/bin/env python3
"""Does the #10 extended normalizer raise the ensemble bar on its own?

Re-runs the WHOLE validation-frozen co-equal ensemble with the NEW normalizer:
  1. re-embed exemplar/validation/test with the extended normalize()
  2. kNN: FP-zero tau on validation
  3. head: RE-TRAIN HistGB on new-normalized exemplar embeddings, 0.1%-val-FPR cutoff
  4. ensemble: (kNN>knn_zfp) OR (head>head_cut) OR R1, scored on test once
Compares to the old-normalizer ensemble (87.2% @ 0% FP).
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "meta/harness/round6-cascade"))
import common as C  # noqa: E402
import head as H  # noqa: E402
from normalize import normalize  # noqa: E402

OUT = ROOT / "artifacts/exp4-coequal"
K = 5
HGB = {"family": "hgb", "max_depth": 3, "learning_rate": 0.1}  # round-6 M2-selected spec


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    C.verify_corpus()
    exemplar = C.load_rows({"exemplar_bank"})
    validation = C.load_rows({"validation"})
    test = C.load_rows({"test"})
    model = C.make_model()

    def emb(rows):
        return C.embed_texts(model, [normalize(r["text"]).text for r in rows])

    Xex = emb(exemplar); yex = C.labels_array(exemplar)
    Xva = emb(validation); yva = C.labels_array(validation)
    Xte = emb(test); yte = C.labels_array(test)

    # kNN inspector (new normalizer)
    pos = Xex[yex == 1]; neg = Xex[yex == 0]
    va_m = C.knn_margin(Xva, pos, neg, K)
    te_m = C.knn_margin(Xte, pos, neg, K)
    knn_zfp = C.select_fp_zero_tau(yva, va_m)["threshold_tau"]

    # head inspector (RE-TRAINED on new-normalized embeddings)
    head = H.train_head(Xex, yex, HGB)
    va_h = head.scores(Xva); te_h = head.scores(Xte)
    head_cut = C.tpr_at_fpr(yva, va_h, 0.001)["threshold"]  # 0.1%-val-FPR cutoff

    # R1
    unt = np.array([corp_field(test, i, "trust_level") == "untrusted" for i in range(len(test))])
    tool = np.array([bool(corp_field(test, i, "requires_tool_call")) for i in range(len(test))])
    R1 = unt & tool

    blk = (te_m > knn_zfp) | (te_h > head_cut) | R1
    catch = 100 * blk[yte == 1].mean(); fp = 100 * blk[yte == 0].mean()

    fam = defaultdict(lambda: [0, 0])
    for i, r in enumerate(test):
        if yte[i] == 1:
            fam[r["attack_class"]][1] += 1
            fam[r["attack_class"]][0] += int(blk[i])

    C.write_json(OUT / "newnorm-metrics.json", {
        "normalizer": "extended (#10)", "selected_on": "validation",
        "knn_zerofp": knn_zfp, "head_0p1pct_val_fpr_cut": head_cut,
        "test_combined_recall": catch / 100, "test_combined_fp": fp / 100,
        "old_normalizer_ensemble": 0.872,
        "per_family_recall": {k: v[0] / v[1] for k, v in sorted(fam.items())},
    })

    print(f"[new-norm] validation-frozen co-equal ensemble (EXTENDED normalizer):")
    print(f"  catch {catch:.1f}%  FP {fp:.2f}%   (old normalizer: 87.2% @ 0%)")
    print(f"  thresholds: knn>{knn_zfp:.4f}  head>{head_cut:.4f}")
    for k, v in sorted(fam.items()):
        print(f"    {k:<22} {100*v[0]/v[1]:5.1f}%")
    return 0


def corp_field(rows, i, f):
    return rows[i].get(f)


if __name__ == "__main__":
    raise SystemExit(main())
