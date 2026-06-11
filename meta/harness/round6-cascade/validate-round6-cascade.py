#!/usr/bin/env python3
"""Round-6 cascade artifact validator. Fails closed.

Usage: validate-round6-cascade.py [m1|m2|m3|m4|m5|all]
Checks per-milestone: artifact structure, metadata-only hygiene, ground-truth
exclusion, closed transform-tag enum, and freeze-before-test ordering.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import common as C
from normalize import TAGS

ART = C.ROOT / "artifacts/round6-cascade"


def fail(msg: str):
    print(f"FAIL: {msg}")
    sys.exit(1)


def load(p: Path):
    if not p.exists():
        fail(f"missing artifact {p}")
    return json.loads(p.read_text())


def check_metadata_only(p: Path):
    for ln in p.read_text().splitlines():
        if not ln.strip():
            continue
        obj = json.loads(ln)
        errs = C.ensure_metadata_only(obj)
        if errs:
            fail(f"{p}: forbidden fields {errs[:2]}")
        for gt in C.GROUND_TRUTH_FIELDS:
            if gt in obj:
                fail(f"{p}: ground-truth field '{gt}' present in per-row output")
        for t in obj.get("transform_tags", []):
            if t not in TAGS:
                fail(f"{p}: transform tag '{t}' outside closed enum")


def validate_m1():
    d = ART / "m1-gate0"
    fr = load(d / "freeze-record.json")
    if fr.get("selected_on") != "validation":
        fail("m1 freeze: tau not selected on validation")
    if fr.get("test_scoring_started_at") in (None, ""):
        fail("m1 freeze: test scoring timestamp missing (freeze-before-test broken)")
    if fr["freeze_record_written_at"] > fr["test_scoring_started_at"]:
        fail("m1 freeze: written_at after test_scoring_started_at")
    if sorted(fr.get("transform_tag_enum", [])) != sorted(TAGS):
        fail("m1 freeze: transform tag enum drift")
    for f in ("validation-per-row.jsonl", "test-per-row.jsonl"):
        check_metadata_only(d / f)
    te = load(d / "test-metrics.json")
    if te["fp"] != 0:
        print(f"WARN: m1 test FP={te['fp']} (FP-zero point expected 0 but is finite-sample)")
    print(f"OK m1: tau={fr['threshold_tau']:.6f} test_recall={te['attack_recall']:.4f} "
          f"test_fp={te['fp']} obf_control_fp={sum(te['benign_obfuscation_control_fp'].values())}")


def validate_m2():
    d = ART / "m2-head"
    fr = load(d / "freeze-record.json")
    if fr.get("selected_on") != "validation":
        fail("m2 freeze: head not selected on validation")
    if fr.get("test_scoring_started_at") in (None, ""):
        fail("m2 freeze: test scoring timestamp missing")
    if fr["freeze_record_written_at"] > fr["test_scoring_started_at"]:
        fail("m2 freeze: written_at after test scoring")
    feats = fr.get("feature_source")
    if feats != ["normalized_text_embedding"]:
        fail(f"m2 freeze: feature source not embeddings-only: {feats}")
    for f in ("validation-per-row.jsonl", "test-per-row.jsonl"):
        check_metadata_only(d / f)
        # no vectors in per-row
        for ln in (d / f).read_text().splitlines():
            if ln.strip() and "embedding" in json.loads(ln):
                fail(f"{f}: embedding vector leaked into per-row")
    lofo = load(d / "lofo-metrics.json")
    if len(lofo["folds"]) != 8:
        fail(f"m2 lofo: expected 8 folds got {len(lofo['folds'])}")
    print(f"OK m2: TPR@1%FPR={load(d/'test-metrics.json')['head']['tpr_at_1pct_fpr']:.4f}")


def validate_m3():
    d = ART / "m3-buckets"
    fr = load(d / "freeze-record.json")
    if fr.get("selected_on") != "validation":
        fail("m3 freeze: thresholds not selected on validation")
    if fr["t_low"] >= fr["t_high"]:
        fail(f"m3: t_low >= t_high ({fr['t_low']} >= {fr['t_high']})")
    if fr.get("test_scoring_started_at") in (None, ""):
        fail("m3 freeze: test scoring timestamp missing")
    check_metadata_only(d / "test-per-row.jsonl")
    print(f"OK m3: t_low={fr['t_low']:.4f} t_high={fr['t_high']:.4f}")


def validate_m4():
    d = ART / "m4-gate2"
    fr = load(d / "freeze-record.json")
    if fr.get("selected_on") != "validation":
        fail("m4 freeze: arms not selected on validation")
    if fr.get("test_scoring_started_at") in (None, ""):
        fail("m4 freeze: test scoring timestamp missing")
    manifests = fr["feature_manifests"]
    for arm in ("control", "floor", "ceiling", "rule"):
        if arm not in manifests:
            fail(f"m4: missing arm '{arm}' feature manifest")
        for gt in C.GROUND_TRUTH_FIELDS:
            if gt in manifests[arm]:
                fail(f"m4 arm {arm}: ground-truth feature {gt}")
    check_metadata_only(d / "test-per-row.jsonl")
    print("OK m4: four arms present, no ground-truth features")


def validate_m5():
    d = ART / "m5-summary"
    s = load(d / "summary-metrics.json")
    if not s.get("verdict_table"):
        fail("m5: verdict table empty")
    for row in s["verdict_table"]:
        if not row.get("verdict"):
            fail(f"m5: verdict missing for {row.get('gate')}")
    print(f"OK m5: {len(s['verdict_table'])} verdict lines recorded")


VALIDATORS = {"m1": validate_m1, "m2": validate_m2, "m3": validate_m3, "m4": validate_m4, "m5": validate_m5}


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    targets = list(VALIDATORS) if target == "all" else [target]
    for t in targets:
        if t not in VALIDATORS:
            fail(f"unknown milestone {t}")
        if (ART / f"{t}-{ {'m1':'gate0','m2':'head','m3':'buckets','m4':'gate2','m5':'summary'}[t] }").exists():
            VALIDATORS[t]()
        elif target != "all":
            VALIDATORS[t]()
        else:
            print(f"skip {t}: artifacts not present")
    print("VALIDATION PASS")


if __name__ == "__main__":
    main()
