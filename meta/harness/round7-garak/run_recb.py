#!/usr/bin/env python3
"""Round-7 Rec B-style ensemble experiment.

Scores Round-7 with the Rust normalizer and the validation-frozen rule:

  base = kNN_zeroFP OR R1
  Rec B = base OR (head_confident AND kNN_in_disagreement_band)

Artifacts are metadata-only: raw row text and normalized text never leave
process memory.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ROUND6 = ROOT / "meta/harness/round6-cascade"
RUN_2X2 = HERE / "run_2x2.py"
DEFAULT_OUT = ROOT / "artifacts/round7-garak/recb-pilot"
TARGET_HEAD_FPR = 0.001
KNN_K = 5


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"could not load module at {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


r7 = load_module(RUN_2X2, "round7_run_2x2")
sys.path.insert(0, str(ROUND6))
import common as C  # noqa: E402
import head as H  # noqa: E402


HGB_SPEC = {"family": "hgb", "max_depth": 3, "learning_rate": 0.1}
HIGH_RISK_TRANSFORMS = {
    "AnsiEscape",
    "UnicodeTag",
    "VariationSelector",
    "SneakyBits",
    "Zalgo",
    "Base32",
    "Base85",
    "Atbash",
    "Morse",
    "Nato",
    "Braille",
    "Hex",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=("smoke", "pilot", "large"), default="pilot")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--round7-corpus", type=Path, default=None)
    parser.add_argument("--round7-manifest", type=Path, default=None)
    parser.add_argument("--limit-per-split-label", type=int, default=None)
    parser.add_argument("--rust-bin", type=Path, default=r7.DEFAULT_RUST_BIN)
    parser.add_argument("--build-rust", action="store_true")
    return parser.parse_args()


def jsonl_rows(path: Path) -> list[dict[str, Any]]:
    return r7.load_jsonl(path)


def json_file(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def labels_array(rows: list[dict[str, Any]]) -> np.ndarray:
    return np.asarray([1 if r7.label_for(row) == "attack" else 0 for row in rows], dtype=np.int8)


def row_sha(row: dict[str, Any]) -> str:
    return r7.sha256_text(json.dumps(row, sort_keys=True, ensure_ascii=False))


def youden_tau(labels: np.ndarray, scores: np.ndarray) -> float:
    order = np.argsort(-scores)
    positives = int(labels.sum())
    negatives = int((labels == 0).sum())
    tp = fp = 0
    best = (-1.0, float(scores.max()))
    for idx in order:
        if labels[idx] == 1:
            tp += 1
        else:
            fp += 1
        sensitivity = tp / positives if positives else 0.0
        fallout = fp / negatives if negatives else 0.0
        score = sensitivity - fallout
        if score > best[0]:
            best = (score, float(scores[idx]))
    return best[1]


def confusion(labels: np.ndarray, preds: np.ndarray) -> dict[str, int]:
    return {
        "tp": int(((labels == 1) & preds).sum()),
        "fn": int(((labels == 1) & (~preds)).sum()),
        "fp": int(((labels == 0) & preds).sum()),
        "tn": int(((labels == 0) & (~preds)).sum()),
    }


def metric(labels: np.ndarray, preds: np.ndarray) -> dict[str, Any]:
    return C.metric_from_confusion(confusion(labels, preds))


def metric_by(rows: list[dict[str, Any]], labels: np.ndarray, preds: np.ndarray, field: str) -> dict[str, Any]:
    groups: dict[str, list[int]] = defaultdict(list)
    for idx, row in enumerate(rows):
        groups[str(row.get(field, "missing"))].append(idx)
    out: dict[str, Any] = {}
    for value, indexes in sorted(groups.items()):
        idx = np.asarray(indexes)
        out[value] = metric(labels[idx], preds[idx])
    return out


def normalize_rows(rows: list[dict[str, Any]], normalizer) -> list[Any]:
    return [normalizer(str(row.get("text", ""))) for row in rows]


def embed_normalized(model, normalized: list[Any]) -> np.ndarray:
    return C.embed_texts(model, [item.value for item in normalized])


def legacy_r1(row: dict[str, Any], _tags: set[str]) -> bool:
    return row.get("trust_level") == "untrusted" and bool(row.get("requires_tool_call"))


def r1_prime(row: dict[str, Any], _tags: set[str]) -> bool:
    trust = row.get("trust_level") in {"untrusted", "tool_output"}
    source = row.get("source_type") in {"rag_chunk", "tool_result", "memory"}
    tool = bool(row.get("requires_tool_call"))
    sink = bool(row.get("contains_sensitive_sink"))
    return trust and source and (tool or sink)


def sink_required(row: dict[str, Any], _tags: set[str]) -> bool:
    return (
        row.get("trust_level") in {"untrusted", "tool_output"}
        and bool(row.get("requires_tool_call"))
        and bool(row.get("contains_sensitive_sink"))
    )


def transform_and_sink(row: dict[str, Any], tags: set[str]) -> bool:
    return bool(tags & HIGH_RISK_TRANSFORMS) and bool(row.get("contains_sensitive_sink"))


def tool_output_transform(row: dict[str, Any], tags: set[str]) -> bool:
    return (
        row.get("source_type") == "tool_result"
        and bool(row.get("requires_tool_call"))
        and bool(tags & HIGH_RISK_TRANSFORMS)
    )


def terminal_ansi(row: dict[str, Any], tags: set[str]) -> bool:
    return row.get("source_type") == "tool_result" and "AnsiEscape" in tags


CONTROL_RULES: dict[str, Callable[[dict[str, Any], set[str]], bool]] = {
    "r1_legacy_untrusted_tool": legacy_r1,
    "r1_prime_source_tool_or_sink": r1_prime,
    "sink_required_tool_gate": sink_required,
    "transform_and_sensitive_sink": transform_and_sink,
    "tool_output_high_risk_transform": tool_output_transform,
    "terminal_ansi_tool_output": terminal_ansi,
}


def control_predictions(rows: list[dict[str, Any]], normalized: list[Any]) -> dict[str, np.ndarray]:
    out: dict[str, np.ndarray] = {}
    tag_sets = [set(item.tags) for item in normalized]
    for name, fn in CONTROL_RULES.items():
        out[name] = np.asarray([fn(row, tags) for row, tags in zip(rows, tag_sets)], dtype=bool)
    return out


def select_head_threshold(labels: np.ndarray, scores: np.ndarray) -> dict[str, Any]:
    return C.tpr_at_fpr(labels, scores, TARGET_HEAD_FPR)


def fp_attribution(rows: list[dict[str, Any]], normalized: list[Any], preds: np.ndarray, labels: np.ndarray) -> dict[str, Any]:
    fp_rows = [
        (row, norm)
        for row, norm, pred, label in zip(rows, normalized, preds, labels)
        if bool(pred) and int(label) == 0
    ]
    return {
        "count": len(fp_rows),
        "by_benign_subclass": dict(sorted(Counter(str(row.get("benign_subclass")) for row, _ in fp_rows).items())),
        "by_source_type": dict(sorted(Counter(str(row.get("source_type")) for row, _ in fp_rows).items())),
        "by_transform_tags": dict(sorted(Counter(",".join(norm.tags) or "none" for _, norm in fp_rows).items())),
        "row_ids": [str(row.get("id")) for row, _ in fp_rows],
    }


def score_arm(
    *,
    name: str,
    bank_rows: list[dict[str, Any]],
    bank_normalized: list[Any],
    validation_rows: list[dict[str, Any]],
    validation_normalized: list[Any],
    test_rows: list[dict[str, Any]],
    test_normalized: list[Any],
    validation_embeddings: np.ndarray,
    test_embeddings: np.ndarray,
    model,
    out_dir: Path,
) -> dict[str, Any]:
    arm_dir = out_dir / "arms" / name
    arm_dir.mkdir(parents=True, exist_ok=True)

    bank_embeddings = embed_normalized(model, bank_normalized)
    bank_labels = labels_array(bank_rows)
    validation_labels = labels_array(validation_rows)
    test_labels = labels_array(test_rows)

    pos = bank_embeddings[bank_labels == 1]
    neg = bank_embeddings[bank_labels == 0]
    if not len(pos) or not len(neg):
        raise SystemExit(f"{name}: bank must contain attack and benign rows")

    validation_knn = C.knn_margin(validation_embeddings, pos, neg, KNN_K)
    test_knn = C.knn_margin(test_embeddings, pos, neg, KNN_K)
    knn_freeze = r7.select_zero_fp_threshold(validation_labels.tolist(), [float(x) for x in validation_knn])
    knn_zero_fp_tau = float(knn_freeze["threshold_tau"])
    knn_youden_tau = float(youden_tau(validation_labels, validation_knn))

    trained_head = H.train_head(bank_embeddings, bank_labels, HGB_SPEC)
    validation_head = trained_head.scores(validation_embeddings)
    test_head = trained_head.scores(test_embeddings)
    head_freeze = select_head_threshold(validation_labels, validation_head)
    head_tau = float(head_freeze["threshold"])

    validation_controls = control_predictions(validation_rows, validation_normalized)
    test_controls = control_predictions(test_rows, test_normalized)

    def decisions(knn_scores: np.ndarray, head_scores: np.ndarray, controls: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
        knn = knn_scores > knn_zero_fp_tau
        head = head_scores > head_tau
        band = (knn_scores > knn_youden_tau) & (knn_scores <= knn_zero_fp_tau)
        r1 = controls["r1_legacy_untrusted_tool"]
        base = knn | r1
        return {
            "knn_zero_fp": knn,
            "head_only": head,
            "r1_legacy_untrusted_tool": r1,
            "base_knn_or_r1": base,
            "recb_head_in_band": base | (band & head),
            "coequal_head_everywhere": base | head,
            "recb_without_r1": knn | (band & head),
            "head_in_band_only": band & head,
            **controls,
        }

    validation_decisions = decisions(validation_knn, validation_head, validation_controls)
    test_decisions = decisions(test_knn, test_head, test_controls)

    validation_metrics = {key: metric(validation_labels, pred) for key, pred in validation_decisions.items()}
    test_metrics = {key: metric(test_labels, pred) for key, pred in test_decisions.items()}
    breakdowns = {
        "attack_class": metric_by(test_rows, test_labels, test_decisions["recb_head_in_band"], "attack_class"),
        "bypass_class": metric_by(test_rows, test_labels, test_decisions["recb_head_in_band"], "bypass_class"),
        "benign_subclass": metric_by(test_rows, test_labels, test_decisions["recb_head_in_band"], "benign_subclass"),
    }
    fp = {
        key: fp_attribution(test_rows, test_normalized, pred, test_labels)
        for key, pred in test_decisions.items()
        if test_metrics[key]["fp"] > 0
    }

    freeze = {
        "schema": "round7-recb-freeze-record-v1",
        "arm": name,
        "selection_split": "validation",
        "normalizer_id": "agt_rust_round7",
        "bank_rows": len(bank_rows),
        "bank_attack_rows": int(bank_labels.sum()),
        "bank_benign_rows": int((bank_labels == 0).sum()),
        "knn_k": KNN_K,
        "knn_zero_fp_tau": knn_zero_fp_tau,
        "knn_youden_tau": knn_youden_tau,
        "head_spec": HGB_SPEC,
        "head_target_fpr": TARGET_HEAD_FPR,
        "head_threshold": head_tau,
        "validation_metrics_at_freeze": {
            "knn_zero_fp": validation_metrics["knn_zero_fp"],
            "head_only": validation_metrics["head_only"],
            "recb_head_in_band": validation_metrics["recb_head_in_band"],
        },
        "test_scored_once_after_freeze": True,
    }
    r7.write_json(arm_dir / "freeze-record.json", freeze)

    metrics = {
        "schema": "round7-recb-arm-metrics-v1",
        "arm": name,
        "thresholds": {
            "knn_zero_fp_tau": knn_zero_fp_tau,
            "knn_youden_tau": knn_youden_tau,
            "head_threshold": head_tau,
        },
        "validation": validation_metrics,
        "test": test_metrics,
        "test_breakdowns_for_recb": breakdowns,
        "test_false_positive_attribution": fp,
    }
    r7.write_json(arm_dir / "metrics.json", metrics)

    per_row: list[dict[str, Any]] = []
    for idx, (row, norm) in enumerate(zip(test_rows, test_normalized)):
        record = {
            "row_id": str(row.get("id")),
            "row_sha256": row_sha(row),
            "split": "test",
            "label": r7.label_for(row),
            "attack_class": str(row.get("attack_class")),
            "benign_subclass": str(row.get("benign_subclass")),
            "bypass_class": str(row.get("bypass_class")),
            "source_type": str(row.get("source_type")),
            "trust_level": str(row.get("trust_level")),
            "requires_tool_call": bool(row.get("requires_tool_call")),
            "contains_sensitive_sink": bool(row.get("contains_sensitive_sink")),
            "transform_tags": list(norm.tags),
            "normalized_sha256": r7.sha256_text(norm.value),
            "scores": {
                "knn_margin": float(test_knn[idx]),
                "head_score": float(test_head[idx]),
            },
            "decisions": {key: bool(pred[idx]) for key, pred in test_decisions.items()},
        }
        per_row.append(record)
    r7.write_jsonl(arm_dir / "test-per-row.jsonl", per_row)

    return {
        "arm": name,
        "freeze_record_path": str((arm_dir / "freeze-record.json").relative_to(ROOT)),
        "metrics_path": str((arm_dir / "metrics.json").relative_to(ROOT)),
        "test_per_row_path": str((arm_dir / "test-per-row.jsonl").relative_to(ROOT)),
        "bank_rows": len(bank_rows),
        "test_recb_recall": test_metrics["recb_head_in_band"]["attack_recall"],
        "test_recb_fp_rate": test_metrics["recb_head_in_band"]["benign_fp_rate"],
        "test_recb_tp": test_metrics["recb_head_in_band"]["tp"],
        "test_recb_fp": test_metrics["recb_head_in_band"]["fp"],
    }


def recommendation_rows(arm_metrics: dict[str, Any]) -> list[dict[str, Any]]:
    fixed = arm_metrics["fixed_round4_bank"]["test"]
    in_domain = arm_metrics["round7_in_domain_bank"]["test"]
    return [
        {
            "control_id": "r1-prime-intent-gated-tool-control",
            "why": "Legacy R1 is the largest catch lever but creates benign tool-use false positives.",
            "evidence": {
                "fixed_bank_legacy_r1_fp": fixed["r1_legacy_untrusted_tool"]["fp"],
                "fixed_bank_recb_fp": fixed["recb_head_in_band"]["fp"],
                "in_domain_recb_fp": in_domain["recb_head_in_band"]["fp"],
            },
            "next_experiment": "Replace bare untrusted+tool-call with tool provenance plus sink/intent routing and measure on expanded benign tool-use controls.",
        },
        {
            "control_id": "terminal-escape-output-sanitizer",
            "why": "Terminal escape attacks remain weak and one FP is benign terminal output.",
            "evidence": {
                "terminal_ansi_candidate": fixed["terminal_ansi_tool_output"],
            },
            "next_experiment": "Split ANSI rendering safety from attack detection: always sanitize unsafe terminal controls, only escalate when paired with tool/policy intent.",
        },
        {
            "control_id": "outbound-sensitive-output-scan",
            "why": "Prompt leakage and output exfiltration need an output-stage control rather than only input embedding similarity.",
            "evidence": {
                "fixed_bank_prompt_leakage_recall": arm_metrics["fixed_round4_bank"]["test_breakdowns_for_recb"]["attack_class"]["prompt_leakage"]["attack_recall"],
            },
            "next_experiment": "Add final-response labels/sinks and verify system/developer/policy leakage before release to the user.",
        },
        {
            "control_id": "package-provenance-verifier",
            "why": "Package hallucination is not primarily an obfuscation problem.",
            "evidence": {
                "fixed_bank_package_hallucination_recall": arm_metrics["fixed_round4_bank"]["test_breakdowns_for_recb"]["attack_class"]["package_hallucination"]["attack_recall"],
            },
            "next_experiment": "Route package recommendations through registry existence, typosquat, age, maintainer, and source allowlist checks.",
        },
        {
            "control_id": "round7-hard-benign-expansion",
            "why": "Only 96 pilot benign test rows makes every FP expensive and prevents credible sub-1% FPR tuning.",
            "evidence": {
                "pilot_test_benign_rows": fixed["recb_head_in_band"]["benign_total"],
            },
            "next_experiment": "Add many more benign tool workflows, terminal logs, package installs, encoded assets, and quoted attack examples before tuning thresholds.",
        },
    ]


def main() -> int:
    args = parse_args()
    out_dir = args.out_dir if args.out_dir.is_absolute() else ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    r7.maybe_build_rust(args.rust_bin, args.build_rust)
    round7_corpus = args.round7_corpus or (r7.SCRATCH / f"round7-{args.profile}.jsonl")
    round7_manifest = args.round7_manifest or (r7.SCRATCH / f"round7-{args.profile}-manifest.json")
    r7.ensure_round7_corpus(args.profile, round7_corpus, round7_manifest, True)

    limit = r7.PROFILE_LIMIT_PER_SPLIT_LABEL[args.profile] if args.limit_per_split_label is None else args.limit_per_split_label
    round4_rows = r7.balanced_limit(jsonl_rows(r7.PROFILE_ROUND4[args.profile]), limit)
    round7_rows = r7.balanced_limit(jsonl_rows(round7_corpus), limit)

    round7_validation = r7.split_rows(round7_rows, "validation")
    round7_test = r7.split_rows(round7_rows, "test")
    round7_bank = r7.split_rows(round7_rows, "exemplar_bank")
    round4_bank = r7.split_rows(round4_rows, "exemplar_bank")

    normalizer = r7.RustNormalizer(args.rust_bin)
    model = C.make_model()

    round7_validation_norm = normalize_rows(round7_validation, normalizer)
    round7_test_norm = normalize_rows(round7_test, normalizer)
    round7_validation_embeddings = embed_normalized(model, round7_validation_norm)
    round7_test_embeddings = embed_normalized(model, round7_test_norm)

    round4_bank_norm = normalize_rows(round4_bank, normalizer)
    round7_bank_norm = normalize_rows(round7_bank, normalizer)

    arms = {}
    manifests = []
    for name, bank_rows, bank_norm in (
        ("fixed_round4_bank", round4_bank, round4_bank_norm),
        ("round7_in_domain_bank", round7_bank, round7_bank_norm),
    ):
        manifest = score_arm(
            name=name,
            bank_rows=bank_rows,
            bank_normalized=bank_norm,
            validation_rows=round7_validation,
            validation_normalized=round7_validation_norm,
            test_rows=round7_test,
            test_normalized=round7_test_norm,
            validation_embeddings=round7_validation_embeddings,
            test_embeddings=round7_test_embeddings,
            model=model,
            out_dir=out_dir,
        )
        manifests.append(manifest)
        arms[name] = json_file(out_dir / "arms" / name / "metrics.json")

    recommendations = recommendation_rows(arms)
    manifest = {
        "schema": "round7-recb-experiment-v1",
        "created_at": r7.utc_now(),
        "profile": args.profile,
        "normalizer_id": "agt_rust_round7",
        "round7_corpus": {
            "path": str(round7_corpus.relative_to(ROOT) if round7_corpus.is_relative_to(ROOT) else round7_corpus),
            "sha256": r7.sha256_file(round7_corpus),
            "manifest_path": str(round7_manifest.relative_to(ROOT) if round7_manifest.is_relative_to(ROOT) else round7_manifest),
            "manifest_sha256": r7.sha256_file(round7_manifest),
            "used_summary": r7.summarize_rows(round7_rows),
        },
        "detector_contract": {
            "rule": "Rec B = (kNN_zeroFP OR legacy_R1) OR (head_confident AND kNN_youden < margin <= kNN_zeroFP)",
            "selection_split": "validation",
            "test_scored_once_after_freeze": True,
            "head_spec": HGB_SPEC,
            "head_target_fpr": TARGET_HEAD_FPR,
            "knn_k": KNN_K,
            "arms": {
                "fixed_round4_bank": "Uses the existing round-7 WS-C fixed round-4 exemplar bank.",
                "round7_in_domain_bank": "Uses round-7 exemplar rows to estimate what in-domain training can recover.",
            },
        },
        "arms": manifests,
        "recommendations": recommendations,
        "metrics_path": str((out_dir / "metrics.json").relative_to(ROOT)),
    }
    r7.write_json(out_dir / "manifest.json", manifest)
    r7.write_json(
        out_dir / "metrics.json",
        {
            "schema": "round7-recb-metrics-v1",
            "arms": arms,
            "recommendations": recommendations,
        },
    )

    for arm in manifests:
        print(
            f"{arm['arm']}: RecB recall={arm['test_recb_recall']:.4f} "
            f"tp={arm['test_recb_tp']} fp_rate={arm['test_recb_fp_rate']:.4f} fp={arm['test_recb_fp']}"
        )
    print(f"wrote {out_dir.relative_to(ROOT) if out_dir.is_relative_to(ROOT) else out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
