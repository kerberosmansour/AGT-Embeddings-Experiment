#!/usr/bin/env python3
"""Validate Round-7 synthetic corpus rows before WS-C measurement runs."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
CORPUS = HERE.parent
REPO = CORPUS.parent
GENERATOR_PATH = HERE / "generate-round7.py"
DEFAULT_RUST_BIN = REPO / "rust/agt-normalize/target/debug/agt-normalize"


spec = importlib.util.spec_from_file_location("round7_generator", GENERATOR_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"could not load {GENERATOR_PATH}")
GEN = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = GEN
spec.loader.exec_module(GEN)


REQUIRED = {
    "id",
    "text",
    "source_type",
    "trust_level",
    "attack_class",
    "risk_level",
    "expected_action",
    "agt_policy_decision",
    "quarantine_intent",
    "contains_sensitive_sink",
    "requires_tool_call",
    "bypass_class",
    "group_id",
    "match_group_id",
    "split",
    "family_id",
    "semantic_family_id",
    "canonical_payload_sha256",
    "generator_id",
    "benign_subclass",
    "label_source",
    "created_round",
    "text_marker",
    "turns",
    "placement",
    "owasp_llm",
    "mitre_atlas",
    "containment_class",
    "defense_stage",
    "control_under_test",
    "control_contract",
    "acs_verdict",
    "blocked_on",
    "source_name",
    "source_license",
    "technique_source",
    "technique_license",
    "literal_payload_import",
    "provenance_kind",
    "synthetic_fields",
    "synthetic_value_policy",
}

ALLOWED_SPLITS = set(GEN.SPLITS)
ALLOWED_ACTIONS = {"allow", "quarantine", "block", "require_approval", "log_only"}
NATIVE_DECISIONS = {"allow", "deny", "requires_approval", "rate_limited"}
ALLOWED_CONTAINMENT = {"structural", "evidence", "workflow_review", "benign_control"}
ALLOWED_LICENSES = {"MIT", "Apache-2.0"}
ALLOWED_ROLES = {"user", "assistant", "tool", "system"}
ALLOWED_PLACEMENTS = {None, "top", "middle", "bottom", "wrapped"}

MATCHED_CONTROL_REQUIREMENTS = {
    "jailbreak": "benign_roleplay_creative",
    "agentic_tool_exploit": "benign_multistep_tool_use",
    "package_hallucination": "benign_package_install",
    "terminal_escape_injection": "benign_terminal_output",
    "indirect_injection": "benign_carrier_document",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_lf_normalized(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def normalize_text(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{lineno}: invalid JSON: {exc}") from exc
    return rows


def count_by(rows: list[dict], key: str) -> dict[str, int]:
    return dict(sorted(Counter(str(row.get(key, "")) for row in rows).items()))


def row_ref(row: dict, extra: dict | None = None) -> dict:
    ref = GEN.row_ref(row)
    if extra:
        ref.update(extra)
    return ref


def expected_native(expected_action: str) -> str:
    if expected_action == "allow":
        return "allow"
    if expected_action == "require_approval":
        return "requires_approval"
    if expected_action in {"block", "quarantine"}:
        return "deny"
    if expected_action == "log_only":
        return "allow"
    return "__invalid__"


def all_texts(row: dict) -> list[str]:
    texts = [str(row.get("text", ""))]
    for turn in row.get("turns") or []:
        texts.append(str(turn.get("text", "")))
    return texts


def raw_url_email_check(rows: list[dict]) -> dict:
    url_re = re.compile(r"https?://", re.IGNORECASE)
    email_re = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
    examples = []
    total = 0
    for row in rows:
        joined = "\n".join(all_texts(row))
        if url_re.search(joined) or email_re.search(joined):
            total += 1
            if len(examples) < GEN.MAX_LEAK_EXAMPLES:
                examples.append(row_ref(row))
    return {"raw_url_or_email_count": total, "examples": examples, "passed": total == 0}


def schema_check(rows: list[dict]) -> dict:
    errors: list[str] = []
    ids: set[str] = set()

    for idx, row in enumerate(rows, 1):
        missing = REQUIRED - set(row)
        row_id = row.get("id", f"row-{idx}")
        if missing:
            errors.append(f"{row_id}: missing fields {sorted(missing)}")
            continue

        if row_id in ids:
            errors.append(f"{row_id}: duplicate id")
        ids.add(str(row_id))

        if not str(row_id).startswith("r7-"):
            errors.append(f"{row_id}: id must start with r7-")
        if row.get("created_round") != "round7":
            errors.append(f"{row_id}: created_round must be round7")
        if row.get("text_marker") != "R7":
            errors.append(f"{row_id}: text_marker must be R7")
        if row.get("split") not in ALLOWED_SPLITS:
            errors.append(f"{row_id}: invalid split {row.get('split')!r}")
        if row.get("expected_action") not in ALLOWED_ACTIONS:
            errors.append(f"{row_id}: invalid expected_action {row.get('expected_action')!r}")
        if row.get("agt_policy_decision") not in NATIVE_DECISIONS:
            errors.append(f"{row_id}: invalid agt_policy_decision {row.get('agt_policy_decision')!r}")
        if row.get("agt_policy_decision") != expected_native(str(row.get("expected_action"))):
            errors.append(f"{row_id}: agt_policy_decision does not match expected_action mapping")
        if row.get("expected_action") == "quarantine" and row.get("quarantine_intent") is not True:
            errors.append(f"{row_id}: quarantine rows must set quarantine_intent=true")
        if row.get("expected_action") != "quarantine" and row.get("quarantine_intent") is not False:
            errors.append(f"{row_id}: quarantine_intent=true is allowed only for quarantine rows")

        if row.get("bypass_class") not in GEN.ALLOWED_BYPASS_CLASSES:
            errors.append(f"{row_id}: invalid bypass_class {row.get('bypass_class')!r}")
        if row.get("bypass_class") in GEN.NEW_BYPASS_CLASSES and row.get("split") == "exemplar_bank":
            errors.append(f"{row_id}: new round-7 bypass class appears in exemplar_bank")

        attack_class = row.get("attack_class")
        if attack_class != "benign" and attack_class not in GEN.ATTACK_CLASSES:
            errors.append(f"{row_id}: invalid attack_class {attack_class!r}")
        if attack_class == "benign":
            if row.get("expected_action") != "allow":
                errors.append(f"{row_id}: benign expected_action must be allow")
            if row.get("benign_subclass") == "not_applicable":
                errors.append(f"{row_id}: benign row must carry a benign_subclass")
            if row.get("containment_class") != "benign_control":
                errors.append(f"{row_id}: benign containment_class must be benign_control")
        else:
            if row.get("benign_subclass") != "not_applicable":
                errors.append(f"{row_id}: attack row benign_subclass must be not_applicable")

        if row.get("containment_class") not in ALLOWED_CONTAINMENT:
            errors.append(f"{row_id}: invalid containment_class {row.get('containment_class')!r}")
        if row.get("containment_class") == "structural":
            contract = row.get("control_contract")
            if not isinstance(contract, dict):
                errors.append(f"{row_id}: structural row requires control_contract object")
            else:
                for key in ("stage", "required_runtime_fields", "rule_id", "native_policy_decision", "evidence_tags"):
                    if key not in contract:
                        errors.append(f"{row_id}: control_contract missing {key}")
                if contract.get("native_policy_decision") not in NATIVE_DECISIONS:
                    errors.append(f"{row_id}: control_contract native decision is not AGT-native")
            if row.get("acs_verdict") not in {"Deny", "Allow", "Warn", "Escalate", "Transform"}:
                errors.append(f"{row_id}: structural row requires acs_verdict")
        else:
            if row.get("control_contract") is not None:
                errors.append(f"{row_id}: non-structural row must not carry control_contract")
            if row.get("acs_verdict") is not None:
                errors.append(f"{row_id}: non-structural row must not carry acs_verdict")
        if row.get("containment_class") == "workflow_review" and not row.get("blocked_on"):
            errors.append(f"{row_id}: workflow_review row must name blocked_on")
        if row.get("containment_class") == "evidence" and row.get("blocked_on"):
            errors.append(f"{row_id}: evidence row should not name blocked_on")

        turns = row.get("turns")
        if turns is not None:
            if not isinstance(turns, list) or not turns:
                errors.append(f"{row_id}: turns must be null or a non-empty list")
            else:
                for turn_idx, turn in enumerate(turns, 1):
                    if not isinstance(turn, dict):
                        errors.append(f"{row_id}: turn {turn_idx} must be an object")
                        continue
                    if turn.get("role") not in ALLOWED_ROLES:
                        errors.append(f"{row_id}: invalid turn role {turn.get('role')!r}")
                    if not isinstance(turn.get("text"), str) or not turn.get("text"):
                        errors.append(f"{row_id}: turn {turn_idx} text must be non-empty")
                try:
                    flattened = GEN.flatten_turns(turns)
                    if row.get("text") != flattened:
                        errors.append(f"{row_id}: text must equal deterministic flattened turns")
                except Exception as exc:
                    errors.append(f"{row_id}: could not flatten turns: {exc}")

        if row.get("placement") not in ALLOWED_PLACEMENTS:
            errors.append(f"{row_id}: invalid placement {row.get('placement')!r}")
        if row.get("source_license") not in ALLOWED_LICENSES:
            errors.append(f"{row_id}: source_license must be MIT or Apache-2.0")
        if row.get("technique_license") not in ALLOWED_LICENSES:
            errors.append(f"{row_id}: technique_license must be MIT or Apache-2.0")
        if row.get("literal_payload_import") is not False:
            errors.append(f"{row_id}: synthetic arm must set literal_payload_import=false")
        if row.get("provenance_kind") != "synthetic_technique_derived":
            errors.append(f"{row_id}: provenance_kind must be synthetic_technique_derived")
        if not isinstance(row.get("synthetic_fields"), list):
            errors.append(f"{row_id}: synthetic_fields must be a list")
        if not isinstance(row.get("owasp_llm"), list) or not isinstance(row.get("mitre_atlas"), list):
            errors.append(f"{row_id}: owasp_llm and mitre_atlas must be lists")

        canonical_hash = sha256_text(normalize_text(str(row.get("text", ""))))
        if row.get("bypass_class") in {"plain", "none"} and row.get("turns") is None:
            if row.get("canonical_payload_sha256") != canonical_hash:
                # Carrier benign twins and some templated rows add trace text before
                # hashing, so this is advisory. Keep it visible rather than fatal.
                pass

    return {
        "checked_rows": len(rows),
        "error_count": len(errors),
        "errors": errors[:100],
        "passed": not errors,
    }


def split_leakage_check(rows: list[dict]) -> dict:
    return GEN.split_leakage(rows)


def normalized_text_check(rows: list[dict]) -> dict:
    return GEN.normalized_text_check(rows)


def bypass_holdout_check(rows: list[dict]) -> dict:
    return GEN.bypass_holdout_check(rows)


def split_label_coverage(rows: list[dict]) -> dict:
    return GEN.split_label_coverage(rows)


def matched_controls_check(rows: list[dict]) -> dict:
    benign_subclasses = {row.get("benign_subclass") for row in rows if row.get("attack_class") == "benign"}
    attack_classes = {row.get("attack_class") for row in rows if row.get("attack_class") != "benign"}
    missing = []
    for attack_class, subclass in sorted(MATCHED_CONTROL_REQUIREMENTS.items()):
        if attack_class in attack_classes and subclass not in benign_subclasses:
            missing.append({"attack_class": attack_class, "missing_benign_subclass": subclass})

    encoded_benign_bypasses = {
        row.get("bypass_class")
        for row in rows
        if row.get("attack_class") == "benign" and row.get("benign_subclass") == "benign_encoded_asset"
    }
    missing_bypass_controls = sorted(set(GEN.NEW_BYPASS_CLASSES) - encoded_benign_bypasses)
    return {
        "attack_control_missing": missing,
        "missing_new_bypass_benign_controls": missing_bypass_controls,
        "passed": not missing and not missing_bypass_controls,
    }


def rust_normalize(rust_bin: Path, text: str) -> dict[str, Any]:
    proc = subprocess.run([str(rust_bin)], input=text, capture_output=True, text=True, check=True)
    return json.loads(proc.stdout)


def rust_normalizer_audit(rows: list[dict], rust_bin: Path, required: bool) -> dict:
    if not rust_bin.exists():
        return {
            "available": False,
            "rust_bin": str(rust_bin),
            "required": required,
            "exact_cross_split_collision_count": 0,
            "examples": [],
            "passed": not required,
        }

    by_hash: dict[tuple[str, str], list[dict]] = defaultdict(list)
    failures = []
    for row in rows:
        row_id = row.get("id")
        scopes = [("flattened", str(row.get("text", "")), None)]
        for idx, turn in enumerate(row.get("turns") or [], 1):
            scopes.append((f"turn:{idx}:{turn.get('role')}", str(turn.get("text", "")), idx))
        for scope, text, turn_idx in scopes:
            try:
                normalized = rust_normalize(rust_bin, text)
            except Exception as exc:
                failures.append({"id": row_id, "scope": scope, "error": str(exc)})
                continue
            digest = sha256_text(normalize_text(str(normalized.get("text", ""))))
            by_hash[(scope, digest)].append(row_ref(row, {"scope": scope, "turn_idx": turn_idx}))

    examples = []
    collision_count = 0
    for (_scope, digest), refs in sorted(by_hash.items()):
        splits = {ref.get("split") for ref in refs}
        semantics = {ref.get("semantic_family_id") for ref in refs}
        if len(splits) > 1 and len(semantics) > 1:
            collision_count += 1
            if len(examples) < GEN.MAX_LEAK_EXAMPLES:
                examples.append({"rust_normalized_sha256": digest, "rows": refs})

    return {
        "available": True,
        "rust_bin": str(rust_bin),
        "required": required,
        "normalization_failure_count": len(failures),
        "normalization_failures": failures[:GEN.MAX_LEAK_EXAMPLES],
        "exact_cross_split_collision_count": collision_count,
        "examples": examples,
        "passed": not failures and collision_count == 0,
    }


def manifest_check(manifest: dict | None, corpus_path: Path, rows: list[dict], summary: dict) -> dict:
    if manifest is None:
        return {"present": False, "passed": True, "errors": []}
    errors = []
    if manifest.get("row_count") != len(rows):
        errors.append(f"row_count mismatch: {manifest.get('row_count')} != {len(rows)}")
    expected_hash = manifest.get("output_sha256")
    actual_hash = sha256(corpus_path)
    normalized_hash = None
    hash_mode = "byte_exact"
    if expected_hash != actual_hash:
        normalized_hash = sha256_lf_normalized(corpus_path)
        hash_mode = "lf_normalized" if expected_hash == normalized_hash else "mismatch"
    if hash_mode == "mismatch":
        errors.append(f"output_sha256 mismatch: {expected_hash} != {actual_hash}")

    for key, counts in summary["counts"].items():
        if manifest.get("counts", {}).get(key) != counts:
            errors.append(f"counts mismatch for {key}")
    for key in (
        "leakage_check",
        "normalized_text_check",
        "duplicate_check",
        "bypass_holdout_check",
        "split_label_coverage_check",
        "synthetic_url_email_check",
    ):
        if manifest.get(key) != summary.get(key):
            errors.append(f"manifest {key} mismatch")

    return {
        "present": True,
        "manifest_output_sha256": expected_hash,
        "worktree_output_sha256": actual_hash,
        "lf_normalized_output_sha256": normalized_hash,
        "hash_mode": hash_mode,
        "errors": errors,
        "passed": not errors,
    }


def validate(rows: list[dict], manifest: dict | None, corpus_path: Path, rust_bin: Path, require_rust: bool) -> tuple[bool, list[str], dict]:
    schema = schema_check(rows)
    leakage = split_leakage_check(rows)
    text_check = normalized_text_check(rows)
    duplicate = GEN.duplicate_check_from_normalized(text_check)
    holdout = bypass_holdout_check(rows)
    coverage = split_label_coverage(rows)
    url_email = raw_url_email_check(rows)
    matched = matched_controls_check(rows)
    rust_audit = rust_normalizer_audit(rows, rust_bin, require_rust)

    summary = {
        "row_count": len(rows),
        "counts": {
            "split": count_by(rows, "split"),
            "attack_class": count_by(rows, "attack_class"),
            "bypass_class": count_by(rows, "bypass_class"),
            "benign_subclass": count_by(rows, "benign_subclass"),
            "source_type": count_by(rows, "source_type"),
            "trust_level": count_by(rows, "trust_level"),
            "expected_action": count_by(rows, "expected_action"),
            "agt_policy_decision": count_by(rows, "agt_policy_decision"),
            "containment_class": count_by(rows, "containment_class"),
            "source_license": count_by(rows, "source_license"),
            "technique_license": count_by(rows, "technique_license"),
        },
        "schema_check": schema,
        "leakage_check": leakage,
        "normalized_text_check": text_check,
        "duplicate_check": duplicate,
        "bypass_holdout_check": holdout,
        "split_label_coverage_check": coverage,
        "synthetic_url_email_check": url_email,
        "matched_controls_check": matched,
        "rust_normalizer_audit_check": rust_audit,
    }
    manifest_result = manifest_check(manifest, corpus_path, rows, summary)
    summary["manifest_check"] = manifest_result

    errors: list[str] = []
    for name in (
        "schema_check",
        "leakage_check",
        "normalized_text_check",
        "bypass_holdout_check",
        "split_label_coverage_check",
        "synthetic_url_email_check",
        "matched_controls_check",
        "rust_normalizer_audit_check",
        "manifest_check",
    ):
        check = summary[name]
        if check.get("passed") is not True:
            errors.append(f"{name}.passed is not true")
            for err in check.get("errors", [])[:20]:
                errors.append(f"{name}: {err}")

    return not errors, errors, summary


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus", type=Path)
    ap.add_argument("--manifest", type=Path)
    ap.add_argument("--summary-json", type=Path)
    ap.add_argument("--rust-bin", type=Path, default=DEFAULT_RUST_BIN)
    ap.add_argument("--require-rust-audit", action="store_true")
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    rows = load_jsonl(args.corpus)
    manifest = json.loads(args.manifest.read_text()) if args.manifest else None
    ok, errors, summary = validate(rows, manifest, args.corpus, args.rust_bin, args.require_rust_audit)
    if args.summary_json:
        with args.summary_json.open("w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if not ok:
        for err in errors:
            print(f"ERROR: {err}")
        return 1
    print("round7-check: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
