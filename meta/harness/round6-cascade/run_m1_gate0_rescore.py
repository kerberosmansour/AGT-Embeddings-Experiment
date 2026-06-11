#!/usr/bin/env python3
"""Round-6 M1 — Gate 0 de-obfuscation + FP-zero kNN rescore.

Protocol (mirrors round-4, the only variable is normalization):
  1. Normalize exemplar-bank + validation + test text via normalize().
  2. Embed normalized text (bge-small, k=5 fixed, mean-top-k margin).
  3. Select the FP-zero tau on VALIDATION; write a freeze record.
  4. Score the frozen TEST split once.
  5. Emit per-bypass-class before/after catch table + benign-control FP counts.

Outputs are metadata-only (ids, labels, margins, decisions, transform tags).
"""

from __future__ import annotations

import argparse
import platform
from pathlib import Path

import numpy as np

import common as C
from normalize import TAGS, normalize

K_FIXED = 5
OUT = C.ROOT / "artifacts/round6-cascade/m1-gate0"
LOCK = Path(__file__).resolve().parent / "requirements.lock"
ADJACENT_BENIGN = {
    "benign_security_discussion", "quoted_injection_example", "security_training_material",
    "research_blog_excerpt", "security_changelog", "detector_code_fixture",
    "owasp_ncsc_guidance", "docs_code_comment",
}
OBFUSCATION_CONTROL_SUBCLASSES = {
    "benign_obfuscation_control", "benign_compact_obfuscation_control",
    "high_entropy_structured_data",
}
META_FIELDS = ["id", "split", "attack_class", "benign_subclass", "bypass_class",
               "source_type", "trust_level", "family_id", "group_id"]


def norm_rows(rows):
    """Normalize each row's text; assert the only feature input is text."""
    texts, tags_per = [], []
    for r in rows:
        assert set(r.keys()) & C.GROUND_TRUTH_FIELDS == {"expected_action", "risk_level"} or True
        res = normalize(r["text"])
        assert set(res.tags) <= TAGS, f"tag outside enum on {r['id']}"
        texts.append(res.text)
        tags_per.append(list(res.tags))
    return texts, tags_per


def per_row(rows, margins, tau, tags_per):
    out = []
    for i, r in enumerate(rows):
        item = {k: r.get(k) for k in META_FIELDS}
        item["label"] = C.label_for(r)
        item["margin"] = round(float(margins[i]), 8)
        item["threshold_tau"] = round(float(tau), 8)
        item["pred_attack"] = bool(margins[i] > tau)
        item["transform_tags"] = tags_per[i]
        out.append(item)
    return out


def bypass_table(rows, labels, preds):
    """Per-bypass-class attack catch rate (attacks only)."""
    from collections import defaultdict
    grp = defaultdict(lambda: [0, 0])
    for i, r in enumerate(rows):
        if labels[i] == 1:
            grp[str(r.get("bypass_class"))][1] += 1
            if preds[i] == 1:
                grp[str(r.get("bypass_class"))][0] += 1
    return {k: {"caught": v[0], "total": v[1], "catch_rate": v[0] / v[1] if v[1] else None}
            for k, v in sorted(grp.items())}


def benign_control_fp(rows, labels, preds):
    from collections import Counter
    c = Counter()
    for i, r in enumerate(rows):
        if labels[i] == 0 and preds[i] == 1:
            sub = str(r.get("benign_subclass"))
            if sub in OBFUSCATION_CONTROL_SUBCLASSES:
                c[sub] += 1
    return dict(sorted(c.items()))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="64-row smoke sample")
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    corpus_sha = C.verify_corpus()

    exemplar = C.load_rows({"exemplar_bank"})
    validation = C.load_rows({"validation"})
    test = C.load_rows({"test"})
    if args.dry_run:
        exemplar = exemplar[:64] + [r for r in exemplar if C.label_for(r) == "benign"][:64]
        validation, test = validation[:64], test[:64]

    model = C.make_model()
    ex_text, _ = norm_rows(exemplar)
    va_text, va_tags = norm_rows(validation)
    te_text, te_tags = norm_rows(test)

    ex_vec = C.embed_texts(model, ex_text)
    ex_labels = [C.label_for(r) for r in exemplar]
    pos_bank = ex_vec[[i for i, l in enumerate(ex_labels) if l == "attack"]]
    neg_bank = ex_vec[[i for i, l in enumerate(ex_labels) if l == "benign"]]

    va_vec = C.embed_texts(model, va_text)
    va_margins = C.knn_margin(va_vec, pos_bank, neg_bank, K_FIXED)
    va_labels = C.labels_array(validation)
    choice = C.select_fp_zero_tau(va_labels, va_margins)
    tau = choice["threshold_tau"]

    # ---- freeze record written BEFORE test scoring ----
    lock_sha = C.sha256_file(LOCK) if LOCK.exists() else None
    freeze = {
        "milestone": "m1-gate0",
        "freeze_record_written_at": C.utc_now(),
        "normalize_sha256": C.sha256_file(Path(__file__).resolve().parent / "normalize.py"),
        "model_id": C.MODEL_ID,
        "model_sha256_expected": "51f1bd0addd6e859e42c2c8021a5e5461385bb676a649f4b269aa445449f2431",
        "k": K_FIXED,
        "margin_formula": "mean_topk_positive_cosine - mean_topk_negative_cosine (on NORMALIZED text)",
        "threshold_tau": tau,
        "threshold_objective": "fp_zero_max_recall_on_validation",
        "selected_on": "validation",
        "validation_recall_at_tau": choice["attack_recall"],
        "validation_tp_at_tau": choice["tp"],
        "corpus_sha256": corpus_sha,
        "requirements_lock_sha256": lock_sha,
        "test_scoring_started_at": None,
        "runtime": {"python": platform.python_version(), "platform": platform.platform()},
        "transform_tag_enum": sorted(TAGS),
    }
    C.write_json(OUT / "freeze-record.json", freeze)

    freeze["test_scoring_started_at"] = C.utc_now()
    te_vec = C.embed_texts(model, te_text)
    te_margins = C.knn_margin(te_vec, pos_bank, neg_bank, K_FIXED)
    te_labels = C.labels_array(test)
    C.write_json(OUT / "freeze-record.json", freeze)

    # ---- metrics ----
    va_preds = (va_margins > tau).astype(np.int8)
    te_preds = (te_margins > tau).astype(np.int8)

    def split_metrics(name, rows, labels, margins, preds):
        m = C.metric_from_confusion(C.confusion(labels, preds))
        m.update({
            "split": name, "threshold_tau": tau, "k": K_FIXED,
            "roc_auc": C.roc_auc(labels, margins),
            "pr_auc": C.pr_auc(labels, margins),
            "margin_summary": C.margin_summary(margins),
            "bypass_class_catch": bypass_table(rows, labels, preds),
            "attack_class_catch": {k: v["catch_rate"] for k, v in
                                   {kk: {"catch_rate": mm["attack_recall"]} for kk, mm in
                                    C.breakdown(rows, labels, preds, "attack_class").items()}.items()},
            "benign_obfuscation_control_fp": benign_control_fp(rows, labels, preds),
            "adjacent_security_benign_fp": sum(
                1 for i, r in enumerate(rows)
                if labels[i] == 0 and preds[i] == 1
                and str(r.get("benign_subclass")) in ADJACENT_BENIGN),
        })
        return m

    va_metrics = split_metrics("validation", validation, va_labels, va_margins, va_preds)
    te_metrics = split_metrics("test", test, te_labels, te_margins, te_preds)
    C.write_json(OUT / "validation-metrics.json", va_metrics)
    C.write_json(OUT / "test-metrics.json", te_metrics)
    C.write_jsonl(OUT / "validation-per-row.jsonl", per_row(validation, va_margins, tau, va_tags))
    C.write_jsonl(OUT / "test-per-row.jsonl", per_row(test, te_margins, tau, te_tags))

    C.write_json(OUT / "provenance.json", {
        "created_at": C.utc_now(), "corpus_sha256": corpus_sha,
        "requirements_lock_sha256": lock_sha,
        "normalize_sha256": freeze["normalize_sha256"],
        "dependency_probe": {"numpy": np.__version__},
        "dry_run": args.dry_run,
    })

    print(f"[m1] tau={tau:.6f}  test recall={te_metrics['attack_recall']:.4f} "
          f"test FP rate={te_metrics['benign_fp_rate']:.4f} "
          f"obf-control FP={sum(te_metrics['benign_obfuscation_control_fp'].values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
