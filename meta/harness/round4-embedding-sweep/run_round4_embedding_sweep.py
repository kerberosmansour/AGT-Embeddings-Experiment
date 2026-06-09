#!/usr/bin/env python3
"""Round-4 validation-only embedding/kNN sweep.

Runner for the AGT embeddings experiment. It writes migrated target artifacts
under artifacts/embedding-sweep/.

The runner scores exemplar_bank -> validation first, writes a freeze record,
then loads/scores the frozen test split. Outputs are metadata-only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import statistics
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import psutil
from fastembed import TextEmbedding
from sklearn.metrics import average_precision_score, roc_auc_score


ROOT = Path(__file__).resolve().parents[3]
ARTIFACTS = ROOT / "artifacts/embedding-sweep"
CACHE = ROOT / ".cache/fastembed"
CORPUS = ROOT / "corpus/round4/injection-round4-large.jsonl"
MANIFEST = ROOT / "corpus/round4/manifest-large.json"
RULES_METRICS = ROOT / "corpus/round4/rules-baseline-large-metrics.json"

MODEL_ID = "BAAI/bge-small-en-v1.5"
MODEL_DIMENSION = 384
MODEL_LICENSE = "mit"
K_GRID = [1, 3, 5, 10]
VALIDATION_THRESHOLD_QUANTILES = 401
EMBED_BATCH_SIZE = 256
SCORE_BATCH_SIZE = 128
MEMORY_LIMIT_BYTES = 16 * 1024 * 1024 * 1024
BASE_RATE_RATIOS = [100, 1000]
ADJACENT_BENIGN_SUBCLASSES = {
    "benign_security_discussion",
    "quoted_injection_example",
    "security_training_material",
    "research_blog_excerpt",
    "security_changelog",
    "detector_code_fixture",
    "owasp_ncsc_guidance",
    "docs_code_comment",
}
FORBIDDEN_OUTPUT_FIELDS = {"text", "raw_text", "prompt", "content"}
METADATA_FIELDS = [
    "id",
    "split",
    "attack_class",
    "benign_subclass",
    "bypass_class",
    "source_type",
    "trust_level",
    "expected_action",
    "contains_sensitive_sink",
    "requires_tool_call",
    "family_id",
    "group_id",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def check_memory(stage: str, memory_samples: list[dict[str, Any]]) -> None:
    rss = psutil.Process().memory_info().rss
    memory_samples.append(
        {"stage": stage, "rss_bytes": rss, "rss_gib": round(rss / (1024**3), 4), "ts": utc_now()}
    )
    if rss > MEMORY_LIMIT_BYTES:
        raise SystemExit(f"memory limit exceeded at {stage}: {rss} bytes")


def label_for(row: dict[str, Any]) -> str:
    return "benign" if row["attack_class"] == "benign" else "attack"


def load_rows(splits: set[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with CORPUS.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            # Fast skip avoids parsing test rows during validation phase.
            if not any(f'"split": "{split}"' in line for split in splits):
                continue
            row = json.loads(line)
            if row["split"] in splits:
                rows.append(row)
    return rows


def balanced_limit(rows: list[dict[str, Any]], limit: int | None) -> list[dict[str, Any]]:
    if limit is None or len(rows) <= limit:
        return rows
    attacks = [row for row in rows if label_for(row) == "attack"]
    benign = [row for row in rows if label_for(row) == "benign"]
    attack_take = min(len(attacks), max(1, limit // 2))
    benign_take = min(len(benign), max(1, limit - attack_take))
    selected = attacks[:attack_take] + benign[:benign_take]
    return sorted(selected, key=lambda row: row["id"])


def metadata_for(row: dict[str, Any]) -> dict[str, Any]:
    out = {key: row.get(key) for key in METADATA_FIELDS}
    out["label"] = label_for(row)
    return out


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


def embed_texts(model: TextEmbedding, rows: list[dict[str, Any]], memory_samples: list[dict[str, Any]]) -> np.ndarray:
    vectors: list[np.ndarray] = []
    texts = [row["text"] for row in rows]
    for start in range(0, len(texts), EMBED_BATCH_SIZE):
        batch = texts[start : start + EMBED_BATCH_SIZE]
        encoded = np.asarray(list(model.embed(batch, batch_size=EMBED_BATCH_SIZE)), dtype=np.float32)
        norms = np.linalg.norm(encoded, axis=1, keepdims=True)
        encoded = encoded / np.maximum(norms, 1e-12)
        vectors.append(encoded)
        if start == 0 or (start // EMBED_BATCH_SIZE) % 20 == 0:
            check_memory(f"embedded_{start + len(batch)}", memory_samples)
    return np.vstack(vectors)


def topk_mean_and_ids(
    query: np.ndarray,
    bank: np.ndarray,
    bank_ids: list[str],
    k: int,
    batch_size: int,
) -> tuple[np.ndarray, list[list[str]]]:
    means: list[np.ndarray] = []
    ids: list[list[str]] = []
    for start in range(0, query.shape[0], batch_size):
        q = query[start : start + batch_size]
        sims = q @ bank.T
        k_eff = min(k, sims.shape[1])
        idx = np.argpartition(sims, -k_eff, axis=1)[:, -k_eff:]
        vals = np.take_along_axis(sims, idx, axis=1)
        order = np.argsort(-vals, axis=1)
        sorted_idx = np.take_along_axis(idx, order, axis=1)
        sorted_vals = np.take_along_axis(vals, order, axis=1)
        means.append(sorted_vals.mean(axis=1))
        ids.extend([[bank_ids[int(i)] for i in row] for row in sorted_idx])
    return np.concatenate(means), ids


def score_split(
    rows: list[dict[str, Any]],
    vectors: np.ndarray,
    pos_bank: np.ndarray,
    pos_ids: list[str],
    neg_bank: np.ndarray,
    neg_ids: list[str],
    k: int,
    threshold_tau: float | None,
) -> tuple[list[dict[str, Any]], np.ndarray, np.ndarray]:
    s_pos, pos_neighbors = topk_mean_and_ids(vectors, pos_bank, pos_ids, k, SCORE_BATCH_SIZE)
    s_neg, neg_neighbors = topk_mean_and_ids(vectors, neg_bank, neg_ids, k, SCORE_BATCH_SIZE)
    margins = s_pos - s_neg
    outputs: list[dict[str, Any]] = []
    for idx, row in enumerate(rows):
        item = metadata_for(row)
        item.update(
            {
                "s_pos": round(float(s_pos[idx]), 8),
                "s_neg": round(float(s_neg[idx]), 8),
                "margin": round(float(margins[idx]), 8),
                "threshold_tau": None if threshold_tau is None else round(float(threshold_tau), 8),
                "pred_attack": None if threshold_tau is None else bool(margins[idx] > threshold_tau),
                "top_positive_neighbor_ids": pos_neighbors[idx],
                "top_negative_neighbor_ids": neg_neighbors[idx],
            }
        )
        outputs.append(item)
    labels = np.asarray([1 if label_for(row) == "attack" else 0 for row in rows], dtype=np.int8)
    return outputs, margins, labels


def wilson(successes: int, total: int, z: float = 1.959963984540054) -> dict[str, float | None]:
    if total == 0:
        return {"estimate": None, "lower": None, "upper": None, "successes": successes, "total": total}
    p = successes / total
    denom = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denom
    half = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denom
    return {"estimate": p, "lower": center - half, "upper": center + half, "successes": successes, "total": total}


def base_rate_precision(recall: float, fp_rate: float, benign_per_attack: int) -> float:
    prevalence = 1 / (benign_per_attack + 1)
    denom = recall * prevalence + fp_rate * (1 - prevalence)
    return 0.0 if denom == 0 else (recall * prevalence) / denom


def confusion(labels: np.ndarray, preds: np.ndarray) -> dict[str, int]:
    return {
        "tp": int(((labels == 1) & (preds == 1)).sum()),
        "fn": int(((labels == 1) & (preds == 0)).sum()),
        "fp": int(((labels == 0) & (preds == 1)).sum()),
        "tn": int(((labels == 0) & (preds == 0)).sum()),
    }


def metric_from_confusion(conf: dict[str, int]) -> dict[str, Any]:
    attack_total = conf["tp"] + conf["fn"]
    benign_total = conf["fp"] + conf["tn"]
    recall = conf["tp"] / attack_total if attack_total else 0.0
    fp_rate = conf["fp"] / benign_total if benign_total else 0.0
    recall_ci = wilson(conf["tp"], attack_total)
    fp_rate_ci = wilson(conf["fp"], benign_total)
    out: dict[str, Any] = {
        **conf,
        "attack_total": attack_total,
        "benign_total": benign_total,
        "attack_recall": recall,
        "attack_recall_wilson_95": recall_ci,
        "benign_fp_rate": fp_rate,
        "benign_fp_rate_wilson_95": fp_rate_ci,
        "false_positives_per_1k_benign": fp_rate * 1000,
        "base_rate_precision_wilson_95": {},
    }
    for ratio in BASE_RATE_RATIOS:
        estimate = base_rate_precision(recall, fp_rate, ratio)
        lower = base_rate_precision(
            float(recall_ci["lower"] or 0.0),
            float(fp_rate_ci["upper"] if fp_rate_ci["upper"] is not None else 1.0),
            ratio,
        )
        upper = base_rate_precision(
            float(recall_ci["upper"] if recall_ci["upper"] is not None else recall),
            float(fp_rate_ci["lower"] or 0.0),
            ratio,
        )
        out[f"base_rate_precision_{ratio}_benign_per_attack"] = estimate
        out["base_rate_precision_wilson_95"][f"1_attack_per_{ratio}_benign"] = {
            "estimate": estimate,
            "lower": lower,
            "upper": upper,
        }
    return out


def threshold_candidates(margins: np.ndarray) -> np.ndarray:
    quantiles = np.linspace(0, 1, VALIDATION_THRESHOLD_QUANTILES)
    values = np.quantile(margins, quantiles)
    pad = np.asarray([float(margins.min() - 1e-6), float(margins.max() + 1e-6)])
    return np.unique(np.concatenate([pad, values]))


def select_threshold(labels: np.ndarray, margins: np.ndarray) -> dict[str, Any]:
    best: dict[str, Any] | None = None
    attack_count = int((labels == 1).sum())
    min_tp = max(30, math.ceil(0.01 * attack_count))
    for tau in threshold_candidates(margins):
        preds = margins > tau
        conf = confusion(labels, preds.astype(np.int8))
        metrics = metric_from_confusion(conf)
        precision_100 = metrics["base_rate_precision_100_benign_per_attack"]
        recall = metrics["attack_recall"]
        if conf["tp"] < min_tp:
            continue
        f1_base100 = 0.0
        if precision_100 + recall > 0:
            f1_base100 = 2 * precision_100 * recall / (precision_100 + recall)
        candidate = {
            "threshold_tau": float(tau),
            "objective": "max_validation_base_rate_f1_100_with_min_tp",
            "objective_value": f1_base100,
            "min_tp": min_tp,
            "metrics": metrics,
        }
        if best is None or candidate["objective_value"] > best["objective_value"]:
            best = candidate
    if best is None:
        raise SystemExit("no validation threshold candidate satisfied min_tp")
    return best


def breakdown(rows: list[dict[str, Any]], labels: np.ndarray, preds: np.ndarray, field: str) -> dict[str, Any]:
    grouped: dict[str, list[int]] = defaultdict(list)
    for idx, row in enumerate(rows):
        grouped[str(row.get(field, "missing"))].append(idx)
    out: dict[str, Any] = {}
    for value, indexes in sorted(grouped.items()):
        idx = np.asarray(indexes)
        out[value] = metric_from_confusion(confusion(labels[idx], preds[idx]))
    return out


def metrics_report(
    split_name: str,
    rows: list[dict[str, Any]],
    labels: np.ndarray,
    margins: np.ndarray,
    threshold_tau: float,
) -> dict[str, Any]:
    preds = (margins > threshold_tau).astype(np.int8)
    conf = confusion(labels, preds)
    metrics = metric_from_confusion(conf)
    benign_fp_by_subclass = Counter()
    adjacent_fp_by_subclass = Counter()
    for idx, row in enumerate(rows):
        if labels[idx] == 0 and preds[idx] == 1:
            subclass = str(row.get("benign_subclass", "missing"))
            benign_fp_by_subclass[subclass] += 1
            if subclass in ADJACENT_BENIGN_SUBCLASSES:
                adjacent_fp_by_subclass[subclass] += 1
    metrics.update(
        {
            "split": split_name,
            "threshold_tau": threshold_tau,
            "roc_auc": float(roc_auc_score(labels, margins)) if len(set(labels.tolist())) > 1 else None,
            "pr_auc_average_precision": float(average_precision_score(labels, margins))
            if len(set(labels.tolist())) > 1
            else None,
            "margin_summary": {
                "min": float(np.min(margins)),
                "p05": float(np.quantile(margins, 0.05)),
                "median": float(np.median(margins)),
                "p95": float(np.quantile(margins, 0.95)),
                "max": float(np.max(margins)),
                "mean": float(np.mean(margins)),
                "stdev": float(statistics.pstdev(margins.tolist())),
            },
            "benign_false_positives_by_subclass": dict(sorted(benign_fp_by_subclass.items())),
            "adjacent_security_benign_false_positives": {
                "total": int(sum(adjacent_fp_by_subclass.values())),
                "by_subclass": dict(sorted(adjacent_fp_by_subclass.items())),
            },
            "breakdowns": {
                field: breakdown(rows, labels, preds, field)
                for field in (
                    "attack_class",
                    "benign_subclass",
                    "bypass_class",
                    "source_type",
                    "trust_level",
                    "expected_action",
                )
            },
        }
    )
    return metrics


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            errors = ensure_metadata_only(row)
            if errors:
                raise SystemExit(f"{path}: metadata-only validation failed: {errors[:3]}")
            f.write(json.dumps(row, sort_keys=True) + "\n")


def model_hashes(cache_dir: Path) -> dict[str, Any]:
    files = []
    for path in sorted(cache_dir.rglob("*")):
        if path.is_file():
            stat = path.stat()
            files.append(
                {
                    "path": str(path.relative_to(cache_dir)),
                    "size_bytes": stat.st_size,
                    "sha256": sha256_file(path),
                }
            )
    onnx_files = [item for item in files if item["path"].endswith((".onnx", ".ort"))]
    selected = max(onnx_files, key=lambda item: item["size_bytes"], default=None)
    return {"selected_model_file": selected, "files": files}


def read_rules_baseline() -> dict[str, Any]:
    metrics = load_json(RULES_METRICS)
    overall = metrics["overall"]
    return {
        "source": str(RULES_METRICS.relative_to(ROOT)),
        "rules_only_attacks": overall["attacks"],
        "rules_only_attacks_caught": overall["attacks_caught"],
        "rules_only_benign": overall["benign"],
        "rules_only_benign_flagged": overall["benign_flagged"],
        "rules_only_attack_recall": overall["attack_recall_wilson_95"]["estimate"],
        "rules_only_benign_fp_rate": overall["benign_fp_rate_wilson_95"]["estimate"],
        "rules_only_fp_per_1k_benign": overall["fp_per_1k_benign"],
        "rules_only_base_rate_precision_100": overall["base_rate_precision"]["1_attack_per_100_benign"],
        "rules_only_base_rate_precision_1000": overall["base_rate_precision"]["1_attack_per_1000_benign"],
    }


def baseline_comparison(metrics: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    expected_rules_tp = baseline["rules_only_attack_recall"] * metrics["attack_total"]
    expected_rules_fp = baseline["rules_only_benign_fp_rate"] * metrics["benign_total"]
    return {
        "baseline_source": baseline["source"],
        "attack_recall_delta": metrics["attack_recall"] - baseline["rules_only_attack_recall"],
        "benign_fp_rate_delta": metrics["benign_fp_rate"] - baseline["rules_only_benign_fp_rate"],
        "fp_per_1k_benign_delta": metrics["false_positives_per_1k_benign"]
        - baseline["rules_only_fp_per_1k_benign"],
        "expected_rules_tp_on_this_split": expected_rules_tp,
        "observed_embedding_tp": metrics["tp"],
        "tp_delta_vs_rules_rate_on_this_split": metrics["tp"] - expected_rules_tp,
        "expected_rules_fp_on_this_split": expected_rules_fp,
        "observed_embedding_fp": metrics["fp"],
        "fp_delta_vs_rules_rate_on_this_split": metrics["fp"] - expected_rules_fp,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="Optional debug row limit per split")
    args = parser.parse_args()

    start = time.monotonic()
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    memory_samples: list[dict[str, Any]] = []
    check_memory("start", memory_samples)

    manifest = load_json(MANIFEST)
    corpus_sha = sha256_file(CORPUS)
    if corpus_sha != manifest["output_sha256"]:
        raise SystemExit(f"corpus hash mismatch: {corpus_sha} != {manifest['output_sha256']}")

    exemplar_rows = load_rows({"exemplar_bank"})
    validation_rows = load_rows({"validation"})
    if args.limit:
        exemplar_rows = balanced_limit(exemplar_rows, args.limit)
        validation_rows = balanced_limit(validation_rows, args.limit)
    check_memory("loaded_exemplar_validation", memory_samples)

    model = TextEmbedding(model_name=MODEL_ID, cache_dir=str(CACHE), threads=max(1, (os.cpu_count() or 4) - 1))
    model_info = next(item for item in TextEmbedding.list_supported_models() if item["model"] == MODEL_ID)
    check_memory("model_loaded", memory_samples)

    exemplar_vectors = embed_texts(model, exemplar_rows, memory_samples)
    validation_vectors = embed_texts(model, validation_rows, memory_samples)
    check_memory("embedded_validation_phase", memory_samples)

    exemplar_labels = [label_for(row) for row in exemplar_rows]
    pos_idx = [idx for idx, label in enumerate(exemplar_labels) if label == "attack"]
    neg_idx = [idx for idx, label in enumerate(exemplar_labels) if label == "benign"]
    pos_bank = exemplar_vectors[pos_idx]
    neg_bank = exemplar_vectors[neg_idx]
    pos_ids = [exemplar_rows[idx]["id"] for idx in pos_idx]
    neg_ids = [exemplar_rows[idx]["id"] for idx in neg_idx]

    validation_grid: list[dict[str, Any]] = []
    best: dict[str, Any] | None = None
    best_outputs: list[dict[str, Any]] | None = None
    best_margins: np.ndarray | None = None
    best_labels: np.ndarray | None = None
    for k in K_GRID:
        outputs, margins, labels = score_split(
            validation_rows, validation_vectors, pos_bank, pos_ids, neg_bank, neg_ids, k, None
        )
        choice = select_threshold(labels, margins)
        choice["k"] = k
        validation_grid.append(choice)
        if best is None or choice["objective_value"] > best["objective_value"]:
            best = choice
            best_outputs = outputs
            best_margins = margins
            best_labels = labels
    if best is None or best_outputs is None or best_margins is None or best_labels is None:
        raise SystemExit("validation model selection failed")

    selected_k = int(best["k"])
    selected_tau = float(best["threshold_tau"])
    validation_outputs, validation_margins, validation_labels = score_split(
        validation_rows,
        validation_vectors,
        pos_bank,
        pos_ids,
        neg_bank,
        neg_ids,
        selected_k,
        selected_tau,
    )
    validation_metrics = metrics_report(
        "validation", validation_rows, validation_labels, validation_margins, selected_tau
    )

    model_files = model_hashes(CACHE)
    freeze_record = {
        "freeze_record_written_at": utc_now(),
        "model_id": MODEL_ID,
        "model_version": model_info.get("description"),
        "model_license": MODEL_LICENSE,
        "model_sources": model_info.get("sources"),
        "model_sha256": model_files["selected_model_file"]["sha256"]
        if model_files["selected_model_file"]
        else "unavailable-no-onnx-file-found",
        "model_file": model_files["selected_model_file"],
        "runtime": "fastembed/onnxruntime-local",
        "runtime_versions": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "fastembed_model_catalog_size": len(TextEmbedding.list_supported_models()),
        },
        "embedding_dimension": MODEL_DIMENSION,
        "normalization": "cosine_l2_normalized",
        "k": selected_k,
        "positive_bank_filter": "attack_class != benign",
        "negative_bank_filter": "attack_class == benign",
        "margin_formula": "mean_topk_positive_cosine - mean_topk_negative_cosine",
        "threshold_tau": selected_tau,
        "threshold_objective": best["objective"],
        "threshold_objective_value": best["objective_value"],
        "abstain_band": None,
        "selected_on": "validation",
        "corpus_sha256": corpus_sha,
        "test_scoring_started_at": None,
        "candidate_grid": validation_grid,
        "resource_budget": {
            "cpu": "Mac local CPU/ANE/GPU as exposed to ONNX Runtime; no hosted inference",
            "memory_limit_bytes": MEMORY_LIMIT_BYTES,
            "time_limit_seconds": 4 * 60 * 60,
            "network": "model download only; no hosted inference or external provider scoring",
            "data": "audited synthetic Round-4 corpus only",
        },
    }
    freeze_path = ARTIFACTS / "freeze-record.json"
    write_json(freeze_path, freeze_record)
    freeze_sha = sha256_file(freeze_path)
    write_jsonl(ARTIFACTS / "validation-per-row.jsonl", validation_outputs)
    write_json(ARTIFACTS / "validation-metrics.json", validation_metrics)

    # Frozen test split is loaded only after freeze record exists.
    test_scoring_started_at = utc_now()
    test_start_record = {
        "test_scoring_started_at": test_scoring_started_at,
        "freeze_record": str(freeze_path.relative_to(ROOT)),
        "freeze_record_sha256": freeze_sha,
        "selected_on": "validation",
        "k": selected_k,
        "threshold_tau": selected_tau,
        "corpus_sha256": corpus_sha,
    }
    test_start_path = ARTIFACTS / "test-start-record.json"
    write_json(test_start_path, test_start_record)
    test_rows = load_rows({"test"})
    if args.limit:
        test_rows = balanced_limit(test_rows, args.limit)
    check_memory("loaded_test_after_freeze", memory_samples)
    test_vectors = embed_texts(model, test_rows, memory_samples)
    check_memory("embedded_test_after_freeze", memory_samples)
    test_outputs, test_margins, test_labels = score_split(
        test_rows, test_vectors, pos_bank, pos_ids, neg_bank, neg_ids, selected_k, selected_tau
    )
    test_metrics = metrics_report("test", test_rows, test_labels, test_margins, selected_tau)
    baseline = read_rules_baseline()
    validation_metrics["rules_baseline_comparison"] = baseline_comparison(validation_metrics, baseline)
    test_metrics["rules_baseline_comparison"] = baseline_comparison(test_metrics, baseline)
    write_json(ARTIFACTS / "validation-metrics.json", validation_metrics)
    write_jsonl(ARTIFACTS / "test-per-row.jsonl", test_outputs)
    write_json(ARTIFACTS / "test-metrics.json", test_metrics)

    elapsed = time.monotonic() - start
    check_memory("complete", memory_samples)
    provenance = {
        "created_at": utc_now(),
        "head": os.popen("git rev-parse HEAD").read().strip(),
        "script": str(Path(__file__).relative_to(ROOT)),
        "script_sha256": sha256_file(Path(__file__)),
        "corpus": str(CORPUS.relative_to(ROOT)),
        "corpus_sha256": corpus_sha,
        "manifest": str(MANIFEST.relative_to(ROOT)),
        "manifest_output_sha256": manifest["output_sha256"],
        "freeze_record": str(freeze_path.relative_to(ROOT)),
        "freeze_record_sha256": freeze_sha,
        "test_start_record": str(test_start_path.relative_to(ROOT)),
        "test_start_record_sha256": sha256_file(test_start_path),
        "test_scoring_started_at": test_scoring_started_at,
        "model_files": model_files,
        "dependency_probe": {
            "fastembed": MODEL_ID,
            "numpy": np.__version__,
        },
        "resource_actual": {
            "elapsed_seconds": elapsed,
            "elapsed_minutes": elapsed / 60,
            "memory_samples": memory_samples,
            "max_rss_bytes": max(item["rss_bytes"] for item in memory_samples),
            "exceeded_budget": False,
        },
        "rules_baseline": baseline,
        "outputs": {
            "validation_per_row": "artifacts/embedding-sweep/validation-per-row.jsonl",
            "validation_metrics": "artifacts/embedding-sweep/validation-metrics.json",
            "test_start_record": "artifacts/embedding-sweep/test-start-record.json",
            "test_per_row": "artifacts/embedding-sweep/test-per-row.jsonl",
            "test_metrics": "artifacts/embedding-sweep/test-metrics.json",
        },
        "non_claims": [
            "research-corpus readout, not a certification or production-security assurance.",
            "no production promotion",
            "no source-material import",
            "no AGT detector/rules change",
            "threshold selected on validation only",
        ],
    }
    write_json(ARTIFACTS / "provenance.json", provenance)

    report = [
        "# Round-4 Embedding Sweep Report",
        "",
        "Status: research-corpus readout, not a certification or production-security assurance.",
        "",
        f"Model: `{MODEL_ID}` via fastembed/ONNX Runtime.",
        f"Selected on validation: k={selected_k}, tau={selected_tau:.8f}, objective={best['objective']}.",
        f"Freeze record: `{freeze_path.relative_to(ROOT)}` sha256 `{freeze_sha}`.",
        "",
        "## Validation",
        "",
        f"- ROC-AUC: {validation_metrics['roc_auc']:.6f}",
        f"- PR-AUC/AP: {validation_metrics['pr_auc_average_precision']:.6f}",
        f"- recall: {validation_metrics['attack_recall']:.6f}",
        f"- benign FP rate: {validation_metrics['benign_fp_rate']:.6f}",
        f"- FP per 1k benign: {validation_metrics['false_positives_per_1k_benign']:.3f}",
        "- base-rate precision 100:1: "
        f"{validation_metrics['base_rate_precision_100_benign_per_attack']:.6f} "
        f"(Wilson-derived {validation_metrics['base_rate_precision_wilson_95']['1_attack_per_100_benign']['lower']:.6f}-"
        f"{validation_metrics['base_rate_precision_wilson_95']['1_attack_per_100_benign']['upper']:.6f})",
        "- base-rate precision 1000:1: "
        f"{validation_metrics['base_rate_precision_1000_benign_per_attack']:.6f} "
        f"(Wilson-derived {validation_metrics['base_rate_precision_wilson_95']['1_attack_per_1000_benign']['lower']:.6f}-"
        f"{validation_metrics['base_rate_precision_wilson_95']['1_attack_per_1000_benign']['upper']:.6f})",
        f"- adjacent-security benign FP: {validation_metrics['adjacent_security_benign_false_positives']['total']}",
        "",
        "## Frozen Test",
        "",
        f"- ROC-AUC: {test_metrics['roc_auc']:.6f}",
        f"- PR-AUC/AP: {test_metrics['pr_auc_average_precision']:.6f}",
        f"- recall: {test_metrics['attack_recall']:.6f}",
        f"- benign FP rate: {test_metrics['benign_fp_rate']:.6f}",
        f"- FP per 1k benign: {test_metrics['false_positives_per_1k_benign']:.3f}",
        "- base-rate precision 100:1: "
        f"{test_metrics['base_rate_precision_100_benign_per_attack']:.6f} "
        f"(Wilson-derived {test_metrics['base_rate_precision_wilson_95']['1_attack_per_100_benign']['lower']:.6f}-"
        f"{test_metrics['base_rate_precision_wilson_95']['1_attack_per_100_benign']['upper']:.6f})",
        "- base-rate precision 1000:1: "
        f"{test_metrics['base_rate_precision_1000_benign_per_attack']:.6f} "
        f"(Wilson-derived {test_metrics['base_rate_precision_wilson_95']['1_attack_per_1000_benign']['lower']:.6f}-"
        f"{test_metrics['base_rate_precision_wilson_95']['1_attack_per_1000_benign']['upper']:.6f})",
        f"- adjacent-security benign FP: {test_metrics['adjacent_security_benign_false_positives']['total']}",
        "",
        "## Baseline Context",
        "",
        "- Rules-only baseline remains the negative control; compare against `corpus/round4/rules-baseline-large-metrics.json`.",
        f"- Test marginal recall delta vs rules-only rate: {test_metrics['rules_baseline_comparison']['attack_recall_delta']:.6f}.",
        f"- Test marginal FP-rate delta vs rules-only rate: {test_metrics['rules_baseline_comparison']['benign_fp_rate_delta']:.6f}.",
        f"- Test TP delta vs rules-only rate on this split: {test_metrics['rules_baseline_comparison']['tp_delta_vs_rules_rate_on_this_split']:.3f}.",
        f"- Test FP delta vs rules-only rate on this split: {test_metrics['rules_baseline_comparison']['fp_delta_vs_rules_rate_on_this_split']:.3f}.",
        "- The embedding signal is not an AGT policy or production detector claim.",
        "",
    ]
    (ARTIFACTS / "report.md").write_text("\n".join(report), encoding="utf-8")
    print(json.dumps({"status": "pass", "artifacts": str(ARTIFACTS), "elapsed_seconds": elapsed}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
