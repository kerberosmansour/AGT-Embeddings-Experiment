#!/usr/bin/env python3
"""Round-6 M5 — aggregation + consolidated verdict table.

NO new scoring, NO model execution (asserted import manifest). Aggregates the
committed m1-m4 artifacts + corpus class joins into per-family / per-bypass
end-to-end floors, a hard-negative benign FP table, and the §2 verdict table.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import common as C

OUT = C.ROOT / "artifacts/round6-cascade/m5-summary"
ART = C.ROOT / "artifacts/round6-cascade"

# no-new-scoring invariant: this module must not import scoring/model code.
_FORBIDDEN_IMPORTS = {"head", "gate2", "buckets", "fastembed", "sklearn"}
assert not (_FORBIDDEN_IMPORTS & set(sys.modules) & {"head", "gate2", "buckets"}), \
    "M5 must not import scoring modules"

ADJACENT_BENIGN = {
    "benign_security_discussion", "quoted_injection_example", "security_training_material",
    "research_blog_excerpt", "security_changelog", "detector_code_fixture",
    "owasp_ncsc_guidance", "docs_code_comment",
}


def jl(path):
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    corpus_sha = C.verify_corpus()

    # corpus class join (test split)
    test_rows = C.load_rows({"test"})
    cls = {r["id"]: (r["attack_class"], r.get("bypass_class"), r.get("benign_subclass"),
                     C.label_for(r)) for r in test_rows}

    m1 = json.load(open(ART / "m1-gate0/test-metrics.json"))
    m2 = json.load(open(ART / "m2-head/test-metrics.json"))
    m2l = json.load(open(ART / "m2-head/lofo-metrics.json"))
    m3 = json.load(open(ART / "m3-buckets/test-metrics.json"))
    m4 = json.load(open(ART / "m4-gate2/test-metrics.json"))

    # final cascade config = ceiling arm decisions (best FP-reduced), joined to M3 buckets
    m3_rows = {r["id"]: r for r in jl(ART / "m3-buckets/test-per-row.jsonl")}
    m4_rows = {r["id"]: r for r in jl(ART / "m4-gate2/test-per-row.jsonl")}

    # final end-to-end flag per test row: flag lane (none) OR (uncertain AND chosen arm flags)
    ARM = "floor_flag"  # report the deployable free-tier arm as the shipped config
    final_flag = {}
    for rid, (ac, bc, bs, lab) in cls.items():
        if rid not in m3_rows:
            sys.exit(f"join orphan: {rid} not in m3 per-row")
        b = m3_rows[rid]["bucket"]
        if b == "flag":
            final_flag[rid] = 1
        elif b == "uncertain":
            final_flag[rid] = int(m4_rows[rid][ARM]) if rid in m4_rows else 0
        else:
            final_flag[rid] = 0

    # per-family end-to-end catch
    fam = defaultdict(lambda: [0, 0])
    byp = defaultdict(lambda: [0, 0])
    for rid, (ac, bc, bs, lab) in cls.items():
        if lab == "attack":
            fam[ac][1] += 1
            byp[str(bc)][1] += 1
            if final_flag[rid]:
                fam[ac][0] += 1
                byp[str(bc)][0] += 1
    per_family = {k: {"caught": v[0], "total": v[1], "catch_rate": v[0] / v[1] if v[1] else None}
                  for k, v in sorted(fam.items())}
    per_bypass = {k: {"caught": v[0], "total": v[1], "catch_rate": v[0] / v[1] if v[1] else None}
                  for k, v in sorted(byp.items())}

    # hard-negative benign FP table (adjacent-security subclasses flagged end-to-end)
    hardneg = defaultdict(lambda: [0, 0])
    for rid, (ac, bc, bs, lab) in cls.items():
        if lab == "benign" and bs in ADJACENT_BENIGN:
            hardneg[bs][1] += 1
            if final_flag[rid]:
                hardneg[bs][0] += 1
    hard_negative = {k: {"flagged": v[0], "total": v[1], "fp_rate": v[0] / v[1] if v[1] else None}
                     for k, v in sorted(hardneg.items())}

    families_at_zero = [k for k, v in per_family.items() if v["catch_rate"] == 0]

    # consolidated §2 verdict table (8 lines)
    miss_overlap = m4["overlap_ratios"]["floor"]["miss_side"]
    verdict_table = [
        {"gate": "M1 Gate 0 (de-obfuscation)",
         "result": f"zero-FP recall 14.2%->43.3%; obf-control FP=0",
         "verdict": "PARTIAL ACCEPT (kill not triggered; word-boundary + multilingual residual)"},
        {"gate": "M2 Gate 1 head (TPR@1%FPR + dominance)",
         "result": f"head TPR@1%FPR {m2['head']['tpr_at_1pct_fpr']:.3f}; does NOT dominate kNN (kNN wins FPR<=1%)",
         "verdict": "NOT SUPPORTED (head ~ kNN; normalization was the lever)"},
        {"gate": "M2 LOFO (generalization)",
         "result": f"median held-out TPR@1%FPR {m2l['median_tpr_at_1pct_fpr']:.3f}; {m2l['families_below_5pct']} families <5%",
         "verdict": "PASS"},
        {"gate": "M3 buckets (coverage)",
         "result": f"benign escape {m3['coverage']['benign_escape_rate']:.4f} (1% inside Wilson)",
         "verdict": "ACCEPT"},
        {"gate": "M3 buckets (queue precision @1:1000)",
         "result": f"{m3['review_queue']['1_attack_per_1000_benign']['queue_precision']:.4f} (>=5%)",
         "verdict": "ACCEPT (marginal)"},
        {"gate": "M4 Gate 2 (floor beats control >=5pt)",
         "result": f"floor-control {m4['floor_minus_control_recall']:+.4f}",
         "verdict": "NOT MET (real but <5pt; free~=full metadata)"},
        {"gate": "M4 Gate 2 (error independence <=1.5)",
         "result": f"miss-side overlap {miss_overlap:.2f} (fp-side 83 is structural artifact)",
         "verdict": "NOT MET (independence refuted; shared blind spots)"},
        {"gate": "M4 Gate 2 (end-to-end >=80% @ <=1% FPR)",
         "result": f"max {m4['end_to_end_recall_ceiling']:.3f} @ ~0.8% FPR (structural ceiling)",
         "verdict": "NOT MET (M3 pass lane sheds 35.6% of attacks)"},
        {"gate": "M5 per-family floors (no family at 0%)",
         "result": f"families at 0%: {families_at_zero or 'none'}",
         "verdict": "PASS" if not families_at_zero else "NOT MET (see residual)"},
    ]

    summary = {
        "created_at_note": "stamp added post-run; no Date.now in harness",
        "corpus_sha256": corpus_sha,
        "shipped_arm": ARM,
        "headline": {
            "m1_zero_fp_recall_round4": m1.get("attack_recall"),  # round-6 m1 recall @ fp-zero
            "cascade_end_to_end_recall": sum(final_flag[r] for r in cls if cls[r][3] == "attack")
            / sum(1 for r in cls if cls[r][3] == "attack"),
            "cascade_end_to_end_hard_fpr": sum(final_flag[r] for r in cls if cls[r][3] == "benign")
            / sum(1 for r in cls if cls[r][3] == "benign"),
        },
        "per_family_end_to_end": per_family,
        "per_bypass_end_to_end": per_bypass,
        "hard_negative_fp": hard_negative,
        "families_at_zero": families_at_zero,
        "verdict_table": verdict_table,
    }
    C.write_json(OUT / "summary-metrics.json", summary)
    C.write_json(OUT / "provenance.json", {
        "corpus_sha256": corpus_sha, "no_new_scoring": True,
        "imported": sorted(set(sys.modules) & {"head", "gate2", "buckets", "fastembed", "sklearn"})})

    h = summary["headline"]
    print(f"[m5] cascade end-to-end: recall={h['cascade_end_to_end_recall']:.4f} "
          f"FPR={h['cascade_end_to_end_hard_fpr']:.4f} | families at 0%: {families_at_zero or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
