#!/usr/bin/env python3
"""Round-6 M3 — calibrated three-bucket conformal routing.

Consumes M2 head scores (validation + test per-row). Fits the router on
validation (cal-A isotonic / cal-B conformal), freezes, routes test once.
Reports benign-side coverage (Wilson) and review-queue precision at 1:100 /
1:1000 prevalence.
"""

from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

import numpy as np

import common as C
from buckets import Bucket, fit_router

OUT = C.ROOT / "artifacts/round6-cascade/m3-buckets"
M2 = C.ROOT / "artifacts/round6-cascade/m2-head"
HERE = Path(__file__).resolve().parent


def load_scores(path: Path):
    rows = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
    ids = [r["id"] for r in rows]
    scores = np.array([r["head_score"] for r in rows], dtype=float)
    labels = np.array([1 if r["label"] == "attack" else 0 for r in rows], dtype=np.int8)
    return rows, ids, scores, labels


def lane_counts(buckets, labels):
    out = {b.value: {"attack": 0, "benign": 0} for b in Bucket}
    for b, y in zip(buckets, labels):
        out[b.value]["attack" if y == 1 else "benign"] += 1
    return out


def queue_precision(p_attack_in_unc, p_benign_in_unc, benign_per_attack):
    prev = 1 / (benign_per_attack + 1)
    a = prev * p_attack_in_unc
    b = (1 - prev) * p_benign_in_unc
    return a / (a + b) if (a + b) > 0 else 0.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    corpus_sha = C.verify_corpus()

    _, va_ids, va_scores, va_labels = load_scores(M2 / "validation-per-row.jsonl")
    te_rows, te_ids, te_scores, te_labels = load_scores(M2 / "test-per-row.jsonl")
    if args.dry_run:
        n = 200
        va_ids, va_scores, va_labels = va_ids[:n], va_scores[:n], va_labels[:n]

    router, info = fit_router(va_ids, va_scores, va_labels)

    freeze = {
        "milestone": "m3-buckets",
        "freeze_record_written_at": C.utc_now(),
        "selected_on": "validation",
        **info,
        "isotonic_knots": {
            "x": [round(float(x), 6) for x in router.iso.X_thresholds_],
            "y": [round(float(y), 6) for y in router.iso.y_thresholds_],
        },
        "corpus_sha256": corpus_sha,
        "m2_freeze_sha256": C.sha256_file(M2 / "freeze-record.json"),
        "test_scoring_started_at": None,
        "runtime": {"python": platform.python_version(), "platform": platform.platform()},
    }
    C.write_json(OUT / "freeze-record.json", freeze)

    freeze["test_scoring_started_at"] = C.utc_now()
    C.write_json(OUT / "freeze-record.json", freeze)

    # validation lanes (diagnostic) + test lanes (verdict)
    va_buckets = router.assign(va_scores)
    te_buckets = router.assign(te_scores)
    va_lanes = lane_counts(va_buckets, va_labels)
    te_lanes = lane_counts(te_buckets, te_labels)

    benign_total = int((te_labels == 0).sum())
    attack_total = int((te_labels == 1).sum())
    benign_escape = te_lanes["uncertain"]["benign"] + te_lanes["flag"]["benign"]
    benign_in_unc = te_lanes["uncertain"]["benign"]
    attack_in_unc = te_lanes["uncertain"]["attack"]
    benign_in_flag = te_lanes["flag"]["benign"]

    coverage = {
        "benign_escape_from_pass": benign_escape,
        "benign_total": benign_total,
        "benign_escape_rate": benign_escape / benign_total,
        "benign_escape_rate_wilson_95": C.wilson(benign_escape, benign_total),
        "alpha_pass_target": info["alpha_pass"],
        "coverage_holds": C.wilson(benign_escape, benign_total)["lower"] <= info["alpha_pass"] <= C.wilson(benign_escape, benign_total)["upper"]
        or benign_escape / benign_total <= info["alpha_pass"],
        "benign_in_flag": benign_in_flag,
        "benign_flag_rate": benign_in_flag / benign_total,
        "alpha_flag_target": info["alpha_flag"],
    }

    p_attack_unc = attack_in_unc / attack_total
    p_benign_unc = benign_in_unc / benign_total
    review = {}
    for ratio in (100, 1000):
        review[f"1_attack_per_{ratio}_benign"] = {
            "queue_precision": queue_precision(p_attack_unc, p_benign_unc, ratio),
            "uncertain_lane_benign_fraction": p_benign_unc,
        }

    metrics = {
        "split": "test",
        "t_low": info["t_low"], "t_high": info["t_high"],
        "validation_lanes": va_lanes,
        "test_lanes": te_lanes,
        "uncertain_lane_attack_recall": p_attack_unc,
        "uncertain_lane_benign_fraction": p_benign_unc,
        "flag_lane_attack_recall": te_lanes["flag"]["attack"] / attack_total,
        "coverage": coverage,
        "review_queue": review,
        "calibration": {
            "brier": float(np.mean((router.calibrate(te_scores) - te_labels) ** 2)),
        },
        "verdict": {
            "queue_precision_1000_ge_5pct": review["1_attack_per_1000_benign"]["queue_precision"] >= 0.05,
            "coverage_within_alpha": benign_escape / benign_total <= info["alpha_pass"] + 1e-9
            or coverage["benign_escape_rate_wilson_95"]["lower"] <= info["alpha_pass"],
        },
    }
    C.write_json(OUT / "test-metrics.json", metrics)

    cal_te = router.calibrate(te_scores)
    per_row = [{"id": r["id"], "label": r["label"], "attack_class": r.get("attack_class"),
                "calibrated_score": round(float(cal_te[i]), 8), "bucket": te_buckets[i].value}
               for i, r in enumerate(te_rows)]
    C.write_jsonl(OUT / "test-per-row.jsonl", per_row)

    C.write_json(OUT / "provenance.json", {
        "created_at": C.utc_now(), "corpus_sha256": corpus_sha,
        "dependency_probe": {"numpy": np.__version__, "sklearn": __import__("sklearn").__version__},
        "dry_run": args.dry_run})

    print(f"[m3] t_low={info['t_low']:.4f} t_high={info['t_high']:.4f} | "
          f"benign escape {benign_escape}/{benign_total}={benign_escape/benign_total:.4f} "
          f"(target {info['alpha_pass']}) | uncertain: {attack_in_unc} atk / {benign_in_unc} ben | "
          f"queue prec@1k={review['1_attack_per_1000_benign']['queue_precision']:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
