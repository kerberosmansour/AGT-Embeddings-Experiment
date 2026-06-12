#!/usr/bin/env python3
"""Round-7 eight-improvement stepwise implementation experiment.

This harness applies the eight lessons from the Round-7 ceiling analysis one at
a time and records catch/FP after each step. It is still a measurement harness:
no production detector behavior is changed here.

Raw row text and normalized text are used in memory only. Artifacts contain row
IDs, hashes, metadata, scores, decisions, and aggregate metrics.
"""

from __future__ import annotations

import argparse
import base64
import codecs
import html
import importlib.util
import json
import re
import sys
import unicodedata
import urllib.parse
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ROUND6 = ROOT / "meta/harness/round6-cascade"
RUN_2X2 = HERE / "run_2x2.py"
DEFAULT_OUT = ROOT / "artifacts/round7-garak/improvements-pilot"
KNN_K = 5
TARGET_HEAD_FPR = 0.001
HARD_BENIGN_STRESS_LIMIT = 1200


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"could not load module at {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


r7 = load_module(RUN_2X2, "round7_run_2x2_improvements")
sys.path.insert(0, str(ROUND6))
import common as C  # noqa: E402
import head as H  # noqa: E402


HGB_SPEC = {"family": "hgb", "max_depth": 3, "learning_rate": 0.1}

STEP_IDS = (
    "00_baseline_fixed_recb",
    "01_tool_output_authority_boundary",
    "02_output_stage_leakage_scan",
    "03_package_provenance_verifier",
    "04_expanded_round7_in_domain_training",
    "05_r1_prime_intent_gate",
    "06_hard_benign_expansion_guard",
    "07_terminal_escape_parser",
    "08_memory_rag_taint_authority",
)

SENSITIVE_PLACEHOLDERS = (
    "[attacker_url]",
    "[canary]",
    "[cross_tenant_record]",
    "[destructive_tool]",
    "[disallowed_content_category]",
    "[harmful_goal]",
    "[hidden_instruction]",
    "[invented_package]",
    "[lookalike_package]",
    "[private_policy_text]",
    "[privileged_tool]",
    "[sensitive_data]",
    "[tool_call]",
    "[unsafe_action]",
    "[untrusted_source]",
)
LEAKAGE_PLACEHOLDERS = (
    "[attacker_url]",
    "[canary]",
    "[cross_tenant_record]",
    "[private_policy_text]",
    "[sensitive_data]",
)

HIGH_RISK_TERMS = (
    "administrator",
    "approval",
    "approve",
    "attacker",
    "bypass",
    "canary",
    "copy",
    "cross tenant",
    "destructive",
    "developer message",
    "disabled",
    "execute",
    "exfil",
    "external",
    "hidden",
    "ignore",
    "install",
    "lookalike",
    "network",
    "obsolete",
    "override",
    "pixel",
    "policy",
    "privileged",
    "reveal",
    "secret",
    "sensitive",
    "system instruction",
    "tool call",
    "unrestricted",
    "unsafe action",
)

HARD_BENIGN_TERMS = (
    "as an attack example",
    "assert flagged",
    "assertflagged",
    "copy editor",
    "detector fixture",
    "display data",
    "existing development toolchain",
    "fictional",
    "game narrator",
    "inert",
    "legitimate typography",
    "morse and braille alphabets",
    "no hidden instruction is present",
    "no instruction follows",
    "no tool call is approved",
    "not as an instruction",
    "policy docs say",
    "public issue search",
    "public issuesearch",
    "public package index",
    "public status page",
    "quoted",
    "read only status lookup",
    "readonly status lookup",
    "release checklist",
    "release note",
    "requires approval",
    "training material",
    "training note",
)

TOOL_AUTHORITY_TERMS = (
    "approval already happened",
    "approve the next privileged tool call",
    "caller policy is obsolete",
    "caller policy obsolete",
    "copy sensitive data",
    "diagnostic log says",
    "execute unsafe action",
    "hidden instruction",
    "new instruction",
    "obsolete execute",
    "policy is obsolete",
    "privileged tool",
    "system approve",
    "system:",
    "tool call without review",
    "tool output says approve",
    "unsafe action",
)

LEAKAGE_TERMS = (
    "append a hidden footnote link",
    "canary",
    "developer message",
    "external image",
    "external image request",
    "hidden footnote",
    "hidden system",
    "pixel",
    "policy text",
    "private policy text",
    "rendered markdown",
    "reveal hidden",
    "sensitive data",
    "show any private rules",
)

PACKAGE_TERMS = (
    "add lookalike package",
    "invented package",
    "install invented package",
    "lookalike package",
    "made up package",
    "madeup package",
    "recommend a made up package",
    "suggest installing invented package",
    "trusted dependency",
    "without registry evidence",
)

TERMINAL_SURFACE_TERMS = (
    "clickable escape sequence",
    "colored log line",
    "escape coded",
    "escape sequence",
    "escape text",
    "rendered build output",
    "terminal controls",
    "terminal output",
)

TERMINAL_INTENT_TERMS = (
    "carrying hidden instruction",
    "escape coded instruction",
    "hidden instruction",
    "hides an instruction",
    "instruction in escape text",
    "terminal output hides",
    "unsafe action",
)

MEMORY_TERMS = (
    "administrator",
    "approvals are never required",
    "durable preference",
    "future requests should trust",
    "memory",
    "remember permanently",
    "save durable preference",
    "trust untrusted source",
    "update memory",
    "always trusted",
)

RAG_AUTHORITY_TERMS = (
    "approval already happened",
    "call destructive tool",
    "destructive tool",
    "escalate",
    "privileged tool",
    "retrieved task card",
    "tool transcript claims approval",
    "untrusted workflow note",
    "unsafe action",
    "vendor bulletin",
)

CONFUSABLES = str.maketrans(
    {
        "а": "a",
        "с": "c",
        "е": "e",
        "і": "i",
        "о": "o",
        "р": "p",
        "х": "x",
        "у": "y",
        "ѕ": "s",
    }
)
DELEET = str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t"})
ATBASH_SOURCE = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
ATBASH_TARGET = "zyxwvutsrqponmlkjihgfedcbaZYXWVUTSRQPONMLKJIHGFEDCBA"
ATBASH = str.maketrans(ATBASH_SOURCE, ATBASH_TARGET)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=("smoke", "pilot", "large"), default="pilot")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--round7-corpus", type=Path, default=None)
    parser.add_argument("--round7-manifest", type=Path, default=None)
    parser.add_argument("--expanded-corpus", type=Path, default=r7.SCRATCH / "round7-large.jsonl")
    parser.add_argument("--expanded-manifest", type=Path, default=r7.SCRATCH / "round7-large-manifest.json")
    parser.add_argument("--limit-per-split-label", type=int, default=None)
    parser.add_argument("--hard-benign-stress-limit", type=int, default=HARD_BENIGN_STRESS_LIMIT)
    parser.add_argument("--rust-bin", type=Path, default=r7.DEFAULT_RUST_BIN)
    parser.add_argument("--build-rust", action="store_true")
    return parser.parse_args()


def labels(rows: list[dict[str, Any]]) -> np.ndarray:
    return np.asarray([1 if r7.label_for(row) == "attack" else 0 for row in rows], dtype=np.int8)


def row_sha(row: dict[str, Any]) -> str:
    return r7.sha256_text(json.dumps(row, sort_keys=True, ensure_ascii=False))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return r7.load_jsonl(path)


def normalized_values(rows: list[dict[str, Any]], normalizer) -> list[Any]:
    return [normalizer(str(row.get("text", ""))) for row in rows]


def embed(model, normalized: list[Any]) -> np.ndarray:
    return C.embed_texts(model, [item.value for item in normalized])


def compact(value: str) -> str:
    return "".join(ch for ch in value.casefold() if ch.isalnum())


def strip_diacritics(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def printable(value: bytes) -> bool:
    if not value:
        return False
    printable_count = sum(1 for byte in value if byte in b"\n\r\t" or 32 <= byte <= 126)
    return printable_count / len(value) >= 0.85


def decoded_token_views(value: str) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for token in re.findall(r"[A-Za-z0-9+/=]{24,}", value):
        padded = token + "=" * ((4 - len(token) % 4) % 4)
        try:
            decoded = base64.b64decode(padded, validate=False)
        except Exception:
            continue
        if printable(decoded):
            text = decoded.decode("utf-8", "ignore")
            if text and text not in seen:
                out.append(text)
                seen.add(text)
    for token in re.findall(r"(?:[0-9A-Fa-f]{2}){12,}", value):
        try:
            decoded = bytes.fromhex(token)
        except ValueError:
            continue
        if printable(decoded):
            text = decoded.decode("utf-8", "ignore")
            if text and text not in seen:
                out.append(text)
                seen.add(text)
    return out


def analysis_views(row: dict[str, Any], norm: Any) -> list[str]:
    raw = str(row.get("text", ""))
    base = [raw, norm.value]
    expanded: list[str] = []
    for item in base:
        expanded.extend(
            [
                item,
                html.unescape(item),
                urllib.parse.unquote(item),
                strip_diacritics(item),
                item.translate(CONFUSABLES),
                item.translate(ATBASH),
                codecs.decode(item, "rot_13"),
                compact(item),
                compact(item).translate(DELEET),
            ]
        )
        expanded.extend(decoded_token_views(item))
    deduped: list[str] = []
    seen: set[str] = set()
    for item in expanded:
        if not item:
            continue
        lowered = item.casefold()
        if lowered in seen:
            continue
        deduped.append(lowered)
        seen.add(lowered)
    return deduped


def has_any(views: list[str], terms: tuple[str, ...]) -> bool:
    compact_views = [compact(view) for view in views]
    for term in terms:
        lowered = term.casefold()
        if any(lowered in view for view in views):
            return True
        if "[" in lowered or "]" in lowered:
            continue
        term_compact = compact(lowered)
        if term_compact and any(term_compact in view for view in compact_views):
            return True
    return False


def high_risk_intent(row: dict[str, Any], norm: Any) -> bool:
    views = analysis_views(row, norm)
    return bool(row.get("contains_sensitive_sink")) or has_any(views, SENSITIVE_PLACEHOLDERS) or has_any(views, HIGH_RISK_TERMS)


def hard_benign_allow(row: dict[str, Any], norm: Any) -> bool:
    if bool(row.get("contains_sensitive_sink")):
        return False
    views = analysis_views(row, norm)
    if not has_any(views, HARD_BENIGN_TERMS):
        return False
    unsafe_without_benign_frame = has_any(
        views,
        (
            "attacker url",
            "call the privileged tool",
            "exfiltrate",
            "harmful goal",
            "hidden retrieved instruction",
            "privileged tool",
            "sensitive data",
            "unsafe action",
        ),
    )
    return not unsafe_without_benign_frame


def legacy_r1(row: dict[str, Any], _norm: Any) -> bool:
    return row.get("trust_level") == "untrusted" and bool(row.get("requires_tool_call"))


def r1_prime(row: dict[str, Any], norm: Any) -> bool:
    trust = row.get("trust_level") in {"untrusted", "tool_output"}
    source = row.get("source_type") in {"rag_chunk", "tool_result", "memory", "user"}
    tool_or_sink = bool(row.get("requires_tool_call")) or bool(row.get("contains_sensitive_sink"))
    return trust and source and tool_or_sink and high_risk_intent(row, norm) and not hard_benign_allow(row, norm)


def tool_output_authority(row: dict[str, Any], norm: Any) -> bool:
    if row.get("source_type") != "tool_result":
        return False
    return has_any(analysis_views(row, norm), TOOL_AUTHORITY_TERMS) and not hard_benign_allow(row, norm)


def output_stage_leakage(row: dict[str, Any], norm: Any) -> bool:
    views = analysis_views(row, norm)
    leak_handle = has_any(views, LEAKAGE_PLACEHOLDERS) or has_any(views, LEAKAGE_TERMS)
    return leak_handle and not hard_benign_allow(row, norm)


def package_provenance(row: dict[str, Any], norm: Any) -> bool:
    views = analysis_views(row, norm)
    if has_any(views, ("public package index", "existing development toolchain")):
        return False
    return has_any(views, PACKAGE_TERMS)


def terminal_escape_parser(row: dict[str, Any], norm: Any) -> bool:
    if row.get("source_type") != "tool_result":
        return False
    views = analysis_views(row, norm)
    tags = set(norm.tags)
    terminal_surface = has_any(views, TERMINAL_SURFACE_TERMS) or bool(
        tags
        & {
            "AnsiEscape",
            "UnicodeTag",
            "VariationSelector",
            "SneakyBits",
            "Zalgo",
            "Base32",
            "Base85",
            "Morse",
            "Nato",
            "Braille",
        }
    )
    terminal_intent = has_any(views, TERMINAL_INTENT_TERMS)
    return terminal_surface and terminal_intent and not hard_benign_allow(row, norm)


def memory_rag_taint_authority(row: dict[str, Any], norm: Any) -> bool:
    source = row.get("source_type")
    views = analysis_views(row, norm)
    if hard_benign_allow(row, norm):
        return False
    if source == "memory":
        return has_any(views, MEMORY_TERMS)
    if source == "rag_chunk" and bool(row.get("requires_tool_call")):
        return has_any(views, RAG_AUTHORITY_TERMS) or high_risk_intent(row, norm)
    return False


def bool_array(rows: list[dict[str, Any]], norms: list[Any], fn) -> np.ndarray:
    return np.asarray([fn(row, norm) for row, norm in zip(rows, norms)], dtype=bool)


def youden_tau(y: np.ndarray, scores: np.ndarray) -> float:
    order = np.argsort(-scores)
    positives = int(y.sum())
    negatives = int((y == 0).sum())
    tp = fp = 0
    best = (-1.0, float(scores.max()))
    for idx in order:
        if y[idx] == 1:
            tp += 1
        else:
            fp += 1
        j = (tp / positives if positives else 0.0) - (fp / negatives if negatives else 0.0)
        if j > best[0]:
            best = (j, float(scores[idx]))
    return best[1]


def confusion(y: np.ndarray, pred: np.ndarray) -> dict[str, int]:
    return {
        "tp": int(((y == 1) & pred).sum()),
        "fn": int(((y == 1) & (~pred)).sum()),
        "fp": int(((y == 0) & pred).sum()),
        "tn": int(((y == 0) & (~pred)).sum()),
    }


def metric(y: np.ndarray, pred: np.ndarray) -> dict[str, Any]:
    return C.metric_from_confusion(confusion(y, pred))


def make_scores(
    *,
    bank_rows: list[dict[str, Any]],
    bank_norms: list[Any],
    eval_embeddings: dict[str, np.ndarray],
    model,
) -> dict[str, Any]:
    bank_embeddings = embed(model, bank_norms)
    bank_labels = labels(bank_rows)
    pos = bank_embeddings[bank_labels == 1]
    neg = bank_embeddings[bank_labels == 0]
    if not len(pos) or not len(neg):
        raise SystemExit("bank must include attack and benign rows")
    eval_knn = {name: C.knn_margin(embeddings, pos, neg, KNN_K) for name, embeddings in eval_embeddings.items()}
    return {
        "bank_rows": len(bank_rows),
        "bank_attack_rows": int(bank_labels.sum()),
        "bank_benign_rows": int((bank_labels == 0).sum()),
        "eval_knn": eval_knn,
        "bank_embeddings": bank_embeddings,
        "bank_labels": bank_labels,
    }


def fit_head(bank_embeddings: np.ndarray, bank_labels: np.ndarray, eval_embeddings: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    head = H.train_head(bank_embeddings, bank_labels, HGB_SPEC)
    return {name: head.scores(embeddings) for name, embeddings in eval_embeddings.items()}


def freeze_thresholds(y_validation: np.ndarray, knn_validation: np.ndarray, head_validation: np.ndarray) -> dict[str, float]:
    return {
        "knn_zero_fp_tau": float(r7.select_zero_fp_threshold(y_validation.tolist(), [float(x) for x in knn_validation])["threshold_tau"]),
        "knn_youden_tau": float(youden_tau(y_validation, knn_validation)),
        "head_tau": float(C.tpr_at_fpr(y_validation, head_validation, TARGET_HEAD_FPR)["threshold"]),
    }


def recb_decision(knn: np.ndarray, head: np.ndarray, r1: np.ndarray, thresholds: dict[str, float]) -> np.ndarray:
    knn_hit = knn > thresholds["knn_zero_fp_tau"]
    head_hit = head > thresholds["head_tau"]
    band = (knn > thresholds["knn_youden_tau"]) & (knn <= thresholds["knn_zero_fp_tau"])
    return knn_hit | r1 | (band & head_hit)


def apply_hard_benign_guard(pred: np.ndarray, guard: np.ndarray, preserve: np.ndarray) -> np.ndarray:
    return pred & ~(guard & ~preserve)


def fp_attribution(rows: list[dict[str, Any]], norms: list[Any], pred: np.ndarray, y: np.ndarray) -> dict[str, Any]:
    fps = [(row, norm) for row, norm, hit, label in zip(rows, norms, pred, y) if bool(hit) and int(label) == 0]
    return {
        "count": len(fps),
        "row_ids": [str(row.get("id")) for row, _ in fps],
        "by_benign_subclass": dict(sorted(Counter(str(row.get("benign_subclass")) for row, _ in fps).items())),
        "by_source_type": dict(sorted(Counter(str(row.get("source_type")) for row, _ in fps).items())),
        "by_transform_tags": dict(sorted(Counter(",".join(norm.tags) or "none" for _, norm in fps).items())),
    }


def step_analysis(rows: list[dict[str, Any]], y: np.ndarray, pred: np.ndarray) -> dict[str, Any]:
    misses = [row for row, hit, label in zip(rows, pred, y) if int(label) == 1 and not bool(hit)]
    return {
        "misses_by_attack_class": dict(sorted(Counter(str(row.get("attack_class")) for row in misses).items())),
        "misses_by_source_type": dict(sorted(Counter(str(row.get("source_type")) for row in misses).items())),
        "misses_by_bypass_class": dict(sorted(Counter(str(row.get("bypass_class")) for row in misses).items())),
    }


def delta_analysis(rows: list[dict[str, Any]], y: np.ndarray, before: np.ndarray | None, after: np.ndarray) -> dict[str, Any]:
    gained: list[str] = []
    lost: list[str] = []
    new_fp: list[str] = []
    cleared_fp: list[str] = []
    gained_classes: Counter[str] = Counter()
    lost_classes: Counter[str] = Counter()
    cleared_fp_subclasses: Counter[str] = Counter()
    new_fp_subclasses: Counter[str] = Counter()
    if before is not None:
        for row, old, new, label in zip(rows, before, after, y):
            if int(label) == 1 and not bool(old) and bool(new):
                gained.append(str(row.get("id")))
                gained_classes[str(row.get("attack_class"))] += 1
            if int(label) == 1 and bool(old) and not bool(new):
                lost.append(str(row.get("id")))
                lost_classes[str(row.get("attack_class"))] += 1
            if int(label) == 0 and not bool(old) and bool(new):
                new_fp.append(str(row.get("id")))
                new_fp_subclasses[str(row.get("benign_subclass"))] += 1
            if int(label) == 0 and bool(old) and not bool(new):
                cleared_fp.append(str(row.get("id")))
                cleared_fp_subclasses[str(row.get("benign_subclass"))] += 1
    return {
        "gained_attack_catch_count": len(gained),
        "lost_attack_catch_count": len(lost),
        "new_benign_fp_count": len(new_fp),
        "cleared_benign_fp_count": len(cleared_fp),
        "gained_attack_catch_row_ids": gained[:50],
        "lost_attack_catch_row_ids": lost[:50],
        "new_benign_fp_row_ids": new_fp[:50],
        "cleared_benign_fp_row_ids": cleared_fp[:50],
        "gained_attack_catch_by_class": dict(sorted(gained_classes.items())),
        "lost_attack_catch_by_class": dict(sorted(lost_classes.items())),
        "new_benign_fp_by_subclass": dict(sorted(new_fp_subclasses.items())),
        "cleared_benign_fp_by_subclass": dict(sorted(cleared_fp_subclasses.items())),
    }


def hard_benign_stress_rows(large_rows: list[dict[str, Any]], pilot_rows: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    pilot_semantics = {str(row.get("semantic_family_id")) for row in pilot_rows}
    rows = [
        row
        for row in large_rows
        if r7.label_for(row) == "benign"
        and row.get("split") == "test"
        and str(row.get("semantic_family_id")) not in pilot_semantics
    ]
    rows = sorted(rows, key=lambda row: str(row.get("id")))
    if limit > 0:
        return rows[:limit]
    return rows


def predictions_for_steps(
    *,
    fixed: dict[str, Any],
    fixed_head: dict[str, np.ndarray],
    fixed_thresholds: dict[str, float],
    expanded: dict[str, Any],
    expanded_head: dict[str, np.ndarray],
    expanded_thresholds: dict[str, float],
    controls: dict[str, np.ndarray],
    split_name: str,
) -> dict[str, np.ndarray]:
    baseline = recb_decision(
        fixed["eval_knn"][split_name],
        fixed_head[split_name],
        controls["legacy_r1"],
        fixed_thresholds,
    )
    route_1 = controls["tool_output_authority"]
    route_2 = route_1 | controls["output_stage_leakage"]
    route_3 = route_2 | controls["package_provenance"]
    expanded_legacy = recb_decision(
        expanded["eval_knn"][split_name],
        expanded_head[split_name],
        controls["legacy_r1"],
        expanded_thresholds,
    )
    expanded_r1_prime = recb_decision(
        expanded["eval_knn"][split_name],
        expanded_head[split_name],
        controls["r1_prime"],
        expanded_thresholds,
    )
    step_preds: dict[str, np.ndarray] = {
        "00_baseline_fixed_recb": baseline,
        "01_tool_output_authority_boundary": baseline | route_1,
    }
    step_preds["02_output_stage_leakage_scan"] = step_preds["01_tool_output_authority_boundary"] | controls["output_stage_leakage"]
    step_preds["03_package_provenance_verifier"] = step_preds["02_output_stage_leakage_scan"] | controls["package_provenance"]
    step_preds["04_expanded_round7_in_domain_training"] = expanded_legacy | route_3
    step_preds["05_r1_prime_intent_gate"] = expanded_r1_prime | route_3
    step_preds["06_hard_benign_expansion_guard"] = apply_hard_benign_guard(
        step_preds["05_r1_prime_intent_gate"],
        controls["hard_benign_allow"],
        route_3,
    )
    step_preds["07_terminal_escape_parser"] = step_preds["06_hard_benign_expansion_guard"] | controls["terminal_escape_parser"]
    step_preds["08_memory_rag_taint_authority"] = step_preds["07_terminal_escape_parser"] | controls["memory_rag_taint_authority"]
    return step_preds


def recommendations() -> list[dict[str, str]]:
    return [
        {
            "step_id": "01_tool_output_authority_boundary",
            "readout": "Tool output needs an explicit authority boundary before it reaches policy/tool decisions.",
            "next_action": "Implement facts-only tool-result handling and block policy, approval, and privileged-action authority from tool output.",
        },
        {
            "step_id": "02_output_stage_leakage_scan",
            "readout": "Leakage/exfiltration moves best at output time, not by more input-side embedding tuning.",
            "next_action": "Add final-response checks for protected context labels, canaries, secret placeholders, policy strings, and outbound sinks.",
        },
        {
            "step_id": "03_package_provenance_verifier",
            "readout": "Package hallucination needs provenance checks rather than text similarity alone.",
            "next_action": "Verify registry existence, namespace/typosquat risk, maintainer/reputation, and source allowlists.",
        },
        {
            "step_id": "04_expanded_round7_in_domain_training",
            "readout": "Use a larger split-clean Round-7 exemplar bank only after generator leakage checks pass.",
            "next_action": "Keep training expansion gated by corpus checks and freeze thresholds on validation before scoring test once.",
        },
        {
            "step_id": "05_r1_prime_intent_gate",
            "readout": "R1-prime controls false positives by requiring intent/provenance/sink risk instead of bare tool-use.",
            "next_action": "Replace legacy R1 with R1-prime, but rely on route controls to recover recall.",
        },
        {
            "step_id": "06_hard_benign_expansion_guard",
            "readout": "Hard benigns should be both a guard and a separate stress measurement.",
            "next_action": "Keep growing benign tool workflows, terminal logs, package installs, quoted examples, docs, and encoded assets.",
        },
        {
            "step_id": "07_terminal_escape_parser",
            "readout": "Terminal hazards need parser/sanitizer semantics rather than a few exact phrases.",
            "next_action": "Build a render sanitizer that tags terminal-control surfaces and escalates only when hidden/unsafe intent is present.",
        },
        {
            "step_id": "08_memory_rag_taint_authority",
            "readout": "Memory and RAG content must carry authority labels; they can provide facts, not durable policy/tool authority.",
            "next_action": "Model memory/RAG taint and block attempts to authorize future trust, approvals, or privileged tool use from tainted content.",
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
    r7.ensure_round7_corpus("large", args.expanded_corpus, args.expanded_manifest, True)

    limit = r7.PROFILE_LIMIT_PER_SPLIT_LABEL[args.profile] if args.limit_per_split_label is None else args.limit_per_split_label
    round4_rows = r7.balanced_limit(load_jsonl(r7.PROFILE_ROUND4[args.profile]), limit)
    round7_rows = r7.balanced_limit(load_jsonl(round7_corpus), limit)
    expanded_rows = load_jsonl(args.expanded_corpus)

    round4_bank = r7.split_rows(round4_rows, "exemplar_bank")
    expanded_bank = r7.split_rows(expanded_rows, "exemplar_bank")
    validation_rows = r7.split_rows(round7_rows, "validation")
    test_rows = r7.split_rows(round7_rows, "test")
    stress_rows = hard_benign_stress_rows(expanded_rows, round7_rows, args.hard_benign_stress_limit)

    y_validation = labels(validation_rows)
    y_test = labels(test_rows)
    y_stress = labels(stress_rows)
    if int(y_stress.sum()) != 0:
        raise SystemExit("hard benign stress set must contain only benign rows")

    normalizer = r7.RustNormalizer(args.rust_bin)
    validation_norms = normalized_values(validation_rows, normalizer)
    test_norms = normalized_values(test_rows, normalizer)
    stress_norms = normalized_values(stress_rows, normalizer)
    round4_bank_norms = normalized_values(round4_bank, normalizer)
    expanded_bank_norms = normalized_values(expanded_bank, normalizer)

    model = C.make_model()
    eval_embeddings = {
        "validation": embed(model, validation_norms),
        "test": embed(model, test_norms),
        "hard_benign_stress": embed(model, stress_norms),
    }

    fixed = make_scores(
        bank_rows=round4_bank,
        bank_norms=round4_bank_norms,
        eval_embeddings=eval_embeddings,
        model=model,
    )
    fixed_head = fit_head(fixed["bank_embeddings"], fixed["bank_labels"], eval_embeddings)
    fixed_thresholds = freeze_thresholds(y_validation, fixed["eval_knn"]["validation"], fixed_head["validation"])

    expanded = make_scores(
        bank_rows=expanded_bank,
        bank_norms=expanded_bank_norms,
        eval_embeddings=eval_embeddings,
        model=model,
    )
    expanded_head = fit_head(expanded["bank_embeddings"], expanded["bank_labels"], eval_embeddings)
    expanded_thresholds = freeze_thresholds(y_validation, expanded["eval_knn"]["validation"], expanded_head["validation"])

    controls_by_split = {}
    for split_name, rows, norms in (
        ("validation", validation_rows, validation_norms),
        ("test", test_rows, test_norms),
        ("hard_benign_stress", stress_rows, stress_norms),
    ):
        controls_by_split[split_name] = {
            "legacy_r1": bool_array(rows, norms, legacy_r1),
            "r1_prime": bool_array(rows, norms, r1_prime),
            "tool_output_authority": bool_array(rows, norms, tool_output_authority),
            "output_stage_leakage": bool_array(rows, norms, output_stage_leakage),
            "package_provenance": bool_array(rows, norms, package_provenance),
            "hard_benign_allow": bool_array(rows, norms, hard_benign_allow),
            "terminal_escape_parser": bool_array(rows, norms, terminal_escape_parser),
            "memory_rag_taint_authority": bool_array(rows, norms, memory_rag_taint_authority),
        }

    test_preds = predictions_for_steps(
        fixed=fixed,
        fixed_head=fixed_head,
        fixed_thresholds=fixed_thresholds,
        expanded=expanded,
        expanded_head=expanded_head,
        expanded_thresholds=expanded_thresholds,
        controls=controls_by_split["test"],
        split_name="test",
    )
    validation_preds = predictions_for_steps(
        fixed=fixed,
        fixed_head=fixed_head,
        fixed_thresholds=fixed_thresholds,
        expanded=expanded,
        expanded_head=expanded_head,
        expanded_thresholds=expanded_thresholds,
        controls=controls_by_split["validation"],
        split_name="validation",
    )
    stress_preds = predictions_for_steps(
        fixed=fixed,
        fixed_head=fixed_head,
        fixed_thresholds=fixed_thresholds,
        expanded=expanded,
        expanded_head=expanded_head,
        expanded_thresholds=expanded_thresholds,
        controls=controls_by_split["hard_benign_stress"],
        split_name="hard_benign_stress",
    )

    step_metrics = {}
    previous = None
    for step_id in STEP_IDS:
        pred = test_preds[step_id]
        stress_pred = stress_preds[step_id]
        step_metrics[step_id] = {
            "metrics": metric(y_test, pred),
            "validation_metrics": metric(y_validation, validation_preds[step_id]),
            "hard_benign_stress_metrics": metric(y_stress, stress_pred),
            "delta_from_previous": delta_analysis(test_rows, y_test, previous, pred),
            "false_positive_attribution": fp_attribution(test_rows, test_norms, pred, y_test),
            "hard_benign_stress_fp_attribution": fp_attribution(stress_rows, stress_norms, stress_pred, y_stress),
            "analysis": step_analysis(test_rows, y_test, pred),
        }
        previous = pred

    per_row = []
    for idx, (row, norm) in enumerate(zip(test_rows, test_norms)):
        per_row.append(
            {
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
                    "fixed_knn_margin": float(fixed["eval_knn"]["test"][idx]),
                    "fixed_head_score": float(fixed_head["test"][idx]),
                    "expanded_knn_margin": float(expanded["eval_knn"]["test"][idx]),
                    "expanded_head_score": float(expanded_head["test"][idx]),
                },
                "controls": {key: bool(value[idx]) for key, value in controls_by_split["test"].items()},
                "steps": {key: bool(value[idx]) for key, value in test_preds.items()},
            }
        )
    r7.write_jsonl(out_dir / "test-per-row.jsonl", per_row)

    stress_per_row = []
    for idx, (row, norm) in enumerate(zip(stress_rows, stress_norms)):
        stress_per_row.append(
            {
                "row_id": str(row.get("id")),
                "row_sha256": row_sha(row),
                "split": "hard_benign_stress",
                "label": r7.label_for(row),
                "benign_subclass": str(row.get("benign_subclass")),
                "bypass_class": str(row.get("bypass_class")),
                "source_type": str(row.get("source_type")),
                "trust_level": str(row.get("trust_level")),
                "requires_tool_call": bool(row.get("requires_tool_call")),
                "contains_sensitive_sink": bool(row.get("contains_sensitive_sink")),
                "transform_tags": list(norm.tags),
                "normalized_sha256": r7.sha256_text(norm.value),
                "scores": {
                    "fixed_knn_margin": float(fixed["eval_knn"]["hard_benign_stress"][idx]),
                    "fixed_head_score": float(fixed_head["hard_benign_stress"][idx]),
                    "expanded_knn_margin": float(expanded["eval_knn"]["hard_benign_stress"][idx]),
                    "expanded_head_score": float(expanded_head["hard_benign_stress"][idx]),
                },
                "controls": {key: bool(value[idx]) for key, value in controls_by_split["hard_benign_stress"].items()},
                "steps": {key: bool(value[idx]) for key, value in stress_preds.items()},
            }
        )
    r7.write_jsonl(out_dir / "hard-benign-stress-per-row.jsonl", stress_per_row)

    recs = recommendations()
    metrics_doc = {
        "schema": "round7-improvements-metrics-v1",
        "step_order": list(STEP_IDS),
        "test_rows": len(test_rows),
        "test_attack_rows": int(y_test.sum()),
        "test_benign_rows": int((y_test == 0).sum()),
        "hard_benign_stress_rows": len(stress_rows),
        "thresholds": {
            "fixed_round4_bank": fixed_thresholds,
            "expanded_round7_bank": expanded_thresholds,
        },
        "banks": {
            "fixed_round4_bank": {
                "rows": fixed["bank_rows"],
                "attack_rows": fixed["bank_attack_rows"],
                "benign_rows": fixed["bank_benign_rows"],
            },
            "expanded_round7_bank": {
                "rows": expanded["bank_rows"],
                "attack_rows": expanded["bank_attack_rows"],
                "benign_rows": expanded["bank_benign_rows"],
            },
        },
        "steps": step_metrics,
        "recommendations": recs,
    }
    r7.write_json(out_dir / "metrics.json", metrics_doc)

    manifest = {
        "schema": "round7-improvements-experiment-v1",
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
        "expanded_round7_corpus": {
            "path": str(args.expanded_corpus.relative_to(ROOT) if args.expanded_corpus.is_relative_to(ROOT) else args.expanded_corpus),
            "sha256": r7.sha256_file(args.expanded_corpus),
            "manifest_path": str(args.expanded_manifest.relative_to(ROOT) if args.expanded_manifest.is_relative_to(ROOT) else args.expanded_manifest),
            "manifest_sha256": r7.sha256_file(args.expanded_manifest),
            "used_summary": r7.summarize_rows(expanded_rows),
            "usage": "exemplar_bank for expanded training; split-clean test benign rows for hard-benign stress metrics",
        },
        "detector_contract": {
            "selection_split": "validation",
            "test_scored_once_after_freeze": True,
            "baseline": "fixed Round-4-bank Rec B with legacy R1",
            "step_order": list(STEP_IDS),
            "head_spec": HGB_SPEC,
            "head_target_fpr": TARGET_HEAD_FPR,
            "knn_k": KNN_K,
            "note": "Prototype controls use operational metadata and in-memory text/normalized text, never label-only fields.",
        },
        "metrics_path": str((out_dir / "metrics.json").relative_to(ROOT)),
        "test_per_row_path": str((out_dir / "test-per-row.jsonl").relative_to(ROOT)),
        "hard_benign_stress_per_row_path": str((out_dir / "hard-benign-stress-per-row.jsonl").relative_to(ROOT)),
        "recommendations": recs,
    }
    r7.write_json(out_dir / "manifest.json", manifest)

    for step_id in STEP_IDS:
        m = step_metrics[step_id]["metrics"]
        sm = step_metrics[step_id]["hard_benign_stress_metrics"]
        print(
            f"{step_id}: catch={m['attack_recall']:.4f} tp={m['tp']}/{m['attack_total']} "
            f"fp={m['fp']}/{m['benign_total']} fpr={m['benign_fp_rate']:.4f} "
            f"stress_fp={sm['fp']}/{sm['benign_total']} stress_fpr={sm['benign_fp_rate']:.4f}"
        )
    print(f"wrote {out_dir.relative_to(ROOT) if out_dir.is_relative_to(ROOT) else out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
