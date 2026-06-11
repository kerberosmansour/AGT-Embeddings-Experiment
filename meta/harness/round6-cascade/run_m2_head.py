#!/usr/bin/env python3
"""Round-6 M2 — trained head vs kNN curve + 8-fold leave-one-family-out.

Protocol:
  1. Normalize + embed exemplar/validation/test (cached by normalize.py SHA +
     corpus manifest hash).
  2. <=24-config validation sweep -> select head by validation TPR@1%FPR.
  3. Compute 0.1%/1% validation-FPR cutoffs; write freeze record.
  4. Single frozen test scoring; TPR@cutoffs + ROC vs M1 post-normalization kNN.
  5. 8-fold LOFO with frozen hyperparameters (generalization sub-gate).
Outputs metadata-only (no vectors, no text).
"""

from __future__ import annotations

import argparse
import hashlib
import platform
from pathlib import Path

import numpy as np

import common as C
import head as H
from normalize import normalize

OUT = C.ROOT / "artifacts/round6-cascade/m2-head"
EMB_CACHE = C.ROOT / ".cache/round6-embeddings"
HERE = Path(__file__).resolve().parent
ATTACK_FAMILIES = [
    "direct_override", "prompt_leakage", "indirect_injection", "tool_abuse",
    "tool_result_injection", "output_exfiltration", "memory_poisoning",
    "data_boundary_abuse",
]


def cache_key() -> str:
    nsha = C.sha256_file(HERE / "normalize.py")
    manifest = C.load_json(C.MANIFEST)
    return hashlib.sha256((nsha + manifest["output_sha256"]).encode()).hexdigest()[:16]


def embed_split(model, rows, name, key):
    EMB_CACHE.mkdir(parents=True, exist_ok=True)
    path = EMB_CACHE / f"{name}-{key}.npz"
    if path.exists():
        d = np.load(path, allow_pickle=True)
        if list(d["ids"]) == [r["id"] for r in rows]:
            return d["vec"]
    texts = [normalize(r["text"]).text for r in rows]
    vec = C.embed_texts(model, texts)
    np.savez(path, vec=vec, ids=np.array([r["id"] for r in rows]))
    return vec


def tpr_at_threshold(labels, scores, thr):
    preds = (scores > thr).astype(np.int8)
    conf = C.confusion(labels, preds)
    at = conf["tp"] + conf["fn"]
    bt = conf["fp"] + conf["tn"]
    return (conf["tp"] / at if at else 0.0, conf["fp"] / bt if bt else 0.0)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    corpus_sha = C.verify_corpus()

    exemplar = C.load_rows({"exemplar_bank"})
    validation = C.load_rows({"validation"})
    test = C.load_rows({"test"})
    if args.dry_run:
        specs = H.model_specs()[:2]
        def bal(rows, n):
            a = [r for r in rows if C.label_for(r) == "attack"][: n // 2]
            b = [r for r in rows if C.label_for(r) == "benign"][: n // 2]
            return a + b
        exemplar = bal(exemplar, 2000)
        validation, test = bal(validation, 800), bal(test, 800)
        families = ATTACK_FAMILIES[:1]
    else:
        specs = H.model_specs()
        families = ATTACK_FAMILIES

    key = cache_key()
    model = C.make_model()
    Xex = embed_split(model, exemplar, "exemplar", key)
    Xva = embed_split(model, validation, "validation", key)
    Xte = embed_split(model, test, "test", key)
    yex = C.labels_array(exemplar)
    yva = C.labels_array(validation)
    yte = C.labels_array(test)

    # feature-source assertion (ground-truth exclusion): only embeddings.
    feature_source = ["normalized_text_embedding"]

    # ---- validation sweep ----
    grid = []
    best = None
    for spec in specs:
        h = H.train_head(Xex, yex, spec)
        sva = h.scores(Xva)
        c1 = C.tpr_at_fpr(yva, sva, 0.01)
        rec = {"spec": spec, "val_tpr_at_1pct_fpr": c1["tpr"],
               "val_roc_auc": C.roc_auc(yva, sva)}
        grid.append(rec)
        if best is None or rec["val_tpr_at_1pct_fpr"] > best["val_tpr_at_1pct_fpr"]:
            best, best_head, best_sva = rec, h, sva

    cut1 = C.tpr_at_fpr(yva, best_sva, 0.01)
    cut01 = C.tpr_at_fpr(yva, best_sva, 0.001)

    lock_sha = C.sha256_file(HERE / "requirements.lock")
    freeze = {
        "milestone": "m2-head",
        "freeze_record_written_at": C.utc_now(),
        "selected_on": "validation",
        "selected_spec": best["spec"],
        "feature_source": feature_source,
        "seed": H.SEED,
        "candidate_grid": grid,
        "grid_size": len(specs),
        "cutoff_1pct_fpr": {"threshold": cut1["threshold"], "val_tpr": cut1["tpr"], "val_fpr": cut1["fpr"]},
        "cutoff_0p1pct_fpr": {"threshold": cut01["threshold"], "val_tpr": cut01["tpr"], "val_fpr": cut01["fpr"]},
        "normalize_sha256": C.sha256_file(HERE / "normalize.py"),
        "embedding_cache_key": key,
        "corpus_sha256": corpus_sha,
        "requirements_lock_sha256": lock_sha,
        "test_scoring_started_at": None,
        "runtime": {"python": platform.python_version(), "platform": platform.platform()},
    }
    C.write_json(OUT / "freeze-record.json", freeze)

    # ---- frozen test scoring ----
    freeze["test_scoring_started_at"] = C.utc_now()
    C.write_json(OUT / "freeze-record.json", freeze)
    ste = best_head.scores(Xte)

    tpr1, fpr1 = tpr_at_threshold(yte, ste, cut1["threshold"])
    tpr01, fpr01 = tpr_at_threshold(yte, ste, cut01["threshold"])

    # kNN reference curve from M1 per-row margins (post-normalization).
    m1_test = [__import__("json").loads(l) for l in
               (C.ROOT / "artifacts/round6-cascade/m1-gate0/test-per-row.jsonl").read_text().splitlines() if l.strip()]
    knn_by_id = {r["id"]: r["margin"] for r in m1_test}
    knn_scores = np.array([knn_by_id[r["id"]] for r in test])
    knn_c1 = C.tpr_at_fpr(yte, knn_scores, 0.01)  # kNN TPR@1%FPR computed directly on test for the curve
    head_c1_test = C.tpr_at_fpr(yte, ste, 0.01)

    # dominance check: head ROC >= kNN ROC for all FPR <= 2% (on test).
    from sklearn.metrics import roc_curve
    fpr_h, tpr_h, _ = roc_curve(yte, ste)
    fpr_k, tpr_k, _ = roc_curve(yte, knn_scores)
    grid_fpr = np.linspace(0, 0.02, 21)
    tpr_h_i = np.interp(grid_fpr, fpr_h, tpr_h)
    tpr_k_i = np.interp(grid_fpr, fpr_k, tpr_k)
    dominates = bool(np.all(tpr_h_i + 1e-9 >= tpr_k_i))

    test_metrics = {
        "split": "test",
        "head": {
            "spec": best["spec"],
            "roc_auc": C.roc_auc(yte, ste),
            "pr_auc": C.pr_auc(yte, ste),
            "tpr_at_1pct_fpr": tpr1, "realized_fpr_at_1pct_cut": fpr1,
            "tpr_at_0p1pct_fpr": tpr01, "realized_fpr_at_0p1pct_cut": fpr01,
            "tpr_at_1pct_fpr_test_curve": head_c1_test["tpr"],
        },
        "knn_reference": {
            "roc_auc": C.roc_auc(yte, knn_scores),
            "tpr_at_1pct_fpr_test_curve": knn_c1["tpr"],
        },
        "dominance_fpr_le_2pct": dominates,
        "dominance_grid": {"fpr": grid_fpr.tolist(),
                           "head_tpr": tpr_h_i.tolist(), "knn_tpr": tpr_k_i.tolist()},
    }
    C.write_json(OUT / "test-metrics.json", test_metrics)

    # per-row (no vectors): id, label, head score
    def per_row(rows, scores):
        return [{"id": r["id"], "label": C.label_for(r), "attack_class": r["attack_class"],
                 "bypass_class": r.get("bypass_class"), "head_score": round(float(scores[i]), 8)}
                for i, r in enumerate(rows)]
    C.write_jsonl(OUT / "validation-per-row.jsonl", per_row(validation, best_sva))
    C.write_jsonl(OUT / "test-per-row.jsonl", per_row(test, ste))

    coef = best_head.coefficients()
    C.write_json(OUT / "head-coefficients.json",
                 {"spec": best["spec"], "lr_coefficients": coef,
                  "note": "384 weights + intercept; metadata, not data"})

    # ---- 8-fold LOFO (frozen spec) ----
    folds = []
    for fam in families:
        keep = np.array([r["attack_class"] != fam for r in exemplar])
        h = H.train_head(Xex[keep], yex[keep], best["spec"])
        # 1%-FPR threshold on validation benign (unaffected by removing F)
        cut = C.tpr_at_fpr(yva, h.scores(Xva), 0.01)
        ste_f = h.scores(Xte)
        fam_idx = np.array([i for i, r in enumerate(test) if r["attack_class"] == fam])
        if len(fam_idx) == 0:
            folds.append({"family": fam, "held_out_test_rows": 0, "tpr_at_1pct_fpr": None})
            continue
        caught = int((ste_f[fam_idx] > cut["threshold"]).sum())
        # purity assertion
        assert not any(exemplar[j]["attack_class"] == fam for j in np.where(keep)[0]), "LOFO purity broken"
        folds.append({"family": fam, "held_out_test_rows": int(len(fam_idx)),
                      "caught": caught, "tpr_at_1pct_fpr": caught / len(fam_idx),
                      "val_threshold": cut["threshold"]})
    valid = [f["tpr_at_1pct_fpr"] for f in folds if f["tpr_at_1pct_fpr"] is not None]
    median = float(np.median(valid)) if valid else None
    below5 = sum(1 for v in valid if v < 0.05)
    C.write_json(OUT / "lofo-metrics.json",
                 {"folds": folds, "median_tpr_at_1pct_fpr": median,
                  "families_below_5pct": below5,
                  "frozen_spec": best["spec"]})

    C.write_json(OUT / "provenance.json", {
        "created_at": C.utc_now(), "corpus_sha256": corpus_sha,
        "embedding_cache_key": key, "requirements_lock_sha256": lock_sha,
        "dependency_probe": {"numpy": np.__version__, "sklearn": __import__("sklearn").__version__},
        "dry_run": args.dry_run})

    print(f"[m2] head={best['spec']} TPR@1%FPR={tpr1:.4f} (knn {knn_c1['tpr']:.4f}) "
          f"dominates={dominates} | LOFO median={median} below5={below5}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
