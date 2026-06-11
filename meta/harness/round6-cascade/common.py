#!/usr/bin/env python3
"""Shared helpers for the round-6 cascade harness.

Embedding, kNN margin scoring, metrics, Wilson intervals, and metadata-only
artifact writers — adapted from the round-4 sweep runner so round-6 milestones
share one scoring path. Frozen-test discipline and metadata-only outputs are
enforced here (forbidden raw-text fields rejected at write time).

NOTE (execution deviation): the runbook scheduled this extraction for M2. It
was created during M1 execution instead, so M1 imports it directly rather than
duplicating round-4 code. Recorded in docs/slo/lessons/r6c-m1.md.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score

ROOT = Path(__file__).resolve().parents[3]
CORPUS = ROOT / "corpus/round4/injection-round4-large.jsonl"
MANIFEST = ROOT / "corpus/round4/manifest-large.json"
CACHE = ROOT / ".cache/fastembed"
MODEL_ID = "BAAI/bge-small-en-v1.5"
MODEL_DIMENSION = 384
EMBED_BATCH_SIZE = 256
SCORE_BATCH_SIZE = 128
MEMORY_LIMIT_BYTES = 16 * 1024 * 1024 * 1024
BASE_RATE_RATIOS = [100, 1000]
FORBIDDEN_OUTPUT_FIELDS = {"text", "raw_text", "prompt", "content", "normalized_text"}
Z95 = 1.959963984540054

# Ground-truth fields that may NEVER enter a feature path (asserted by callers).
GROUND_TRUTH_FIELDS = {"expected_action", "risk_level"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def label_for(row: dict) -> str:
    return "benign" if row["attack_class"] == "benign" else "attack"


def load_rows(splits: set[str]) -> list[dict]:
    rows: list[dict] = []
    with CORPUS.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            if not any(f'"split": "{s}"' in line for s in splits):
                continue
            row = json.loads(line)
            if row["split"] in splits:
                rows.append(row)
    return rows


def verify_corpus() -> str:
    manifest = load_json(MANIFEST)
    corpus_sha = sha256_file(CORPUS)
    if corpus_sha != manifest["output_sha256"]:
        raise SystemExit(f"corpus hash mismatch: {corpus_sha} != {manifest['output_sha256']}")
    return corpus_sha


def make_model():
    from fastembed import TextEmbedding

    return TextEmbedding(
        model_name=MODEL_ID,
        cache_dir=str(CACHE),
        threads=max(1, (os.cpu_count() or 4) - 1),
    )


def embed_texts(model, texts: list[str]) -> np.ndarray:
    vectors: list[np.ndarray] = []
    for start in range(0, len(texts), EMBED_BATCH_SIZE):
        batch = texts[start : start + EMBED_BATCH_SIZE]
        encoded = np.asarray(list(model.embed(batch, batch_size=EMBED_BATCH_SIZE)), dtype=np.float32)
        norms = np.linalg.norm(encoded, axis=1, keepdims=True)
        vectors.append(encoded / np.maximum(norms, 1e-12))
    return np.vstack(vectors)


def topk_mean(query: np.ndarray, bank: np.ndarray, k: int) -> np.ndarray:
    means: list[np.ndarray] = []
    for start in range(0, query.shape[0], SCORE_BATCH_SIZE):
        q = query[start : start + SCORE_BATCH_SIZE]
        sims = q @ bank.T
        k_eff = min(k, sims.shape[1])
        idx = np.argpartition(sims, -k_eff, axis=1)[:, -k_eff:]
        vals = np.take_along_axis(sims, idx, axis=1)
        means.append(vals.mean(axis=1))
    return np.concatenate(means)


def knn_margin(query: np.ndarray, pos_bank: np.ndarray, neg_bank: np.ndarray, k: int) -> np.ndarray:
    return topk_mean(query, pos_bank, k) - topk_mean(query, neg_bank, k)


def labels_array(rows: list[dict]) -> np.ndarray:
    return np.asarray([1 if label_for(r) == "attack" else 0 for r in rows], dtype=np.int8)


def wilson(successes: int, total: int, z: float = Z95) -> dict:
    if total == 0:
        return {"estimate": None, "lower": None, "upper": None, "successes": successes, "total": total}
    p = successes / total
    denom = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denom
    half = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denom
    return {"estimate": p, "lower": center - half, "upper": center + half, "successes": successes, "total": total}


def confusion(labels: np.ndarray, preds: np.ndarray) -> dict:
    return {
        "tp": int(((labels == 1) & (preds == 1)).sum()),
        "fn": int(((labels == 1) & (preds == 0)).sum()),
        "fp": int(((labels == 0) & (preds == 1)).sum()),
        "tn": int(((labels == 0) & (preds == 0)).sum()),
    }


def base_rate_precision(recall: float, fp_rate: float, benign_per_attack: int) -> float:
    prevalence = 1 / (benign_per_attack + 1)
    denom = recall * prevalence + fp_rate * (1 - prevalence)
    return 0.0 if denom == 0 else (recall * prevalence) / denom


def metric_from_confusion(conf: dict) -> dict:
    attack_total = conf["tp"] + conf["fn"]
    benign_total = conf["fp"] + conf["tn"]
    recall = conf["tp"] / attack_total if attack_total else 0.0
    fp_rate = conf["fp"] / benign_total if benign_total else 0.0
    out = {
        **conf,
        "attack_total": attack_total,
        "benign_total": benign_total,
        "attack_recall": recall,
        "attack_recall_wilson_95": wilson(conf["tp"], attack_total),
        "benign_fp_rate": fp_rate,
        "benign_fp_rate_wilson_95": wilson(conf["fp"], benign_total),
        "false_positives_per_1k_benign": fp_rate * 1000,
    }
    for ratio in BASE_RATE_RATIOS:
        out[f"base_rate_precision_{ratio}_benign_per_attack"] = base_rate_precision(recall, fp_rate, ratio)
    return out


def breakdown(rows: list[dict], labels: np.ndarray, preds: np.ndarray, field: str) -> dict:
    grouped: dict[str, list[int]] = defaultdict(list)
    for idx, row in enumerate(rows):
        grouped[str(row.get(field, "missing"))].append(idx)
    out: dict[str, Any] = {}
    for value, indexes in sorted(grouped.items()):
        idx = np.asarray(indexes)
        out[value] = metric_from_confusion(confusion(labels[idx], preds[idx]))
    return out


def select_fp_zero_tau(labels: np.ndarray, margins: np.ndarray, quantiles: int = 1001) -> dict:
    """Most aggressive (lowest) tau with zero benign FP on this split.

    Mirrors round-4's FP-zero operating point: scan candidate thresholds, keep
    those with benign_fp == 0, choose the one maximizing attack recall (i.e. the
    lowest qualifying tau). Pre-registered, validation-only.
    """
    qs = np.quantile(margins, np.linspace(0, 1, quantiles))
    cands = np.unique(np.concatenate([[margins.min() - 1e-6, margins.max() + 1e-6], qs]))
    best = None
    for tau in cands:
        preds = (margins > tau).astype(np.int8)
        conf = confusion(labels, preds)
        if conf["fp"] != 0:
            continue
        recall = conf["tp"] / max(1, conf["tp"] + conf["fn"])
        cand = {"threshold_tau": float(tau), "attack_recall": recall, "tp": conf["tp"]}
        if best is None or cand["attack_recall"] > best["attack_recall"]:
            best = cand
    if best is None:
        raise SystemExit("no zero-FP threshold candidate found on validation")
    return best


def ensure_metadata_only(value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key in FORBIDDEN_OUTPUT_FIELDS:
                errors.append(f"{path}.{key}: forbidden raw-text-like field")
            errors.extend(ensure_metadata_only(item, f"{path}.{key}"))
    elif isinstance(value, list):
        for idx, item in enumerate(value):
            errors.extend(ensure_metadata_only(item, f"{path}[{idx}]"))
    return errors


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            errors = ensure_metadata_only(row)
            if errors:
                raise SystemExit(f"{path}: metadata-only validation failed: {errors[:3]}")
            f.write(json.dumps(row, sort_keys=True) + "\n")


def roc_auc(labels: np.ndarray, scores: np.ndarray) -> float | None:
    return float(roc_auc_score(labels, scores)) if len(set(labels.tolist())) > 1 else None


def pr_auc(labels: np.ndarray, scores: np.ndarray) -> float | None:
    return float(average_precision_score(labels, scores)) if len(set(labels.tolist())) > 1 else None


def margin_summary(margins: np.ndarray) -> dict:
    return {
        "min": float(np.min(margins)),
        "p05": float(np.quantile(margins, 0.05)),
        "median": float(np.median(margins)),
        "p95": float(np.quantile(margins, 0.95)),
        "max": float(np.max(margins)),
        "mean": float(np.mean(margins)),
        "stdev": float(np.std(margins)),
    }


def tpr_at_fpr(labels: np.ndarray, scores: np.ndarray, target_fpr: float) -> dict:
    """TPR at the lowest threshold whose benign FPR <= target_fpr (validation
    cutoff selection helper). Returns the threshold and the achieved rates."""
    order = np.argsort(-scores)
    benign_total = int((labels == 0).sum())
    attack_total = int((labels == 1).sum())
    fp = tp = 0
    chosen_thr = float(scores.max()) + 1e-9
    # walk thresholds high->low; stop just before FPR exceeds target
    best = {"threshold": chosen_thr, "tpr": 0.0, "fpr": 0.0, "tp": 0, "fp": 0}
    for i in order:
        if labels[i] == 1:
            tp += 1
        else:
            fp += 1
        fpr = fp / benign_total if benign_total else 0.0
        if fpr > target_fpr:
            break
        best = {
            "threshold": float(scores[i]),
            "tpr": tp / attack_total if attack_total else 0.0,
            "fpr": fpr,
            "tp": tp,
            "fp": fp,
        }
    best["target_fpr"] = target_fpr
    return best
