#!/usr/bin/env python3
"""Control-linked evidence-level scorecard reporter (M4) — stdlib-only.

Front-to-end (oc-4): the assessing engineer runs

    python scorecard.py --controls controls/agt-ac.csv \
        (--results <results.jsonl> | --from-scenarios <scenarios_dir>) --out <dir>

and gets `<dir>/scorecard_report.json` + `.md` aggregating results by trap
class / AGT-AC control / evidence level. The report carries a HARD
`certification_claim: false` (literal) and zero certification language — it
reports EVIDENCE LEVELS, never a pass/cert badge. Missing fields fail closed.

Exit codes: 0 ok | 1 result/structured error | 2 usage.
"""
import argparse
import csv
import json
import sys
from pathlib import Path

EVIDENCE_LEVELS = ("L0_declared", "L1_static", "L2_mock_behavioural", "L3_live_behavioural")
RESULT_REQUIRED = {"scenario_id", "trap_class", "controls", "evidence_level", "status"}
HARD_BENIGN_CONTROL = "AGT-AC-014"  # must-not-block coverage
MEASUREMENT_SUITE = "agt_redteam_measurement_v2"
MEASUREMENT_KINDS = {
    "canonical_positive", "evasion_positive", "hard_benign", "near_miss",
}
POSITIVE_KINDS = {"canonical_positive", "evasion_positive"}
NEGATIVE_KINDS = {"hard_benign", "near_miss"}
MEASURED_STATUSES = {"pass", "fail"}


class ResultError(ValueError):
    """A result row is malformed (missing field / unknown enum) — fail closed."""


def load_controls(path):
    """Return {control_id: row_dict} from the read-only AGT-AC catalog."""
    controls = {}
    with Path(path).open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            controls[row["id"]] = row
    return controls


def _validate_result(result):
    missing = RESULT_REQUIRED - set(result)
    if missing:
        raise ResultError(f"result {result.get('scenario_id', '?')} missing {sorted(missing)}")
    if result["evidence_level"] not in EVIDENCE_LEVELS:
        raise ResultError(f"unknown evidence_level {result['evidence_level']!r}")


def _rate(rows, success_status="pass"):
    measured = [r for r in rows if r.get("status") in MEASURED_STATUSES]
    if not measured:
        return None
    wins = sum(1 for r in measured if r.get("status") == success_status)
    return round(wins / len(measured), 4)


def _status_counts(rows):
    counts = {}
    for row in rows:
        status = row.get("status", "unknown")
        counts[status] = counts.get(status, 0) + 1
    return dict(sorted(counts.items()))


def _measurement_rate_block(rows):
    canonical = [r for r in rows if r.get("scenario_kind") == "canonical_positive"]
    evasion = [r for r in rows if r.get("scenario_kind") == "evasion_positive"]
    negatives = [r for r in rows if r.get("scenario_kind") in NEGATIVE_KINDS]
    canonical_rate = _rate(canonical)
    evasion_rate = _rate(evasion)
    utility_rate = _rate(negatives)
    fp_rate = None
    if utility_rate is not None:
        fp_rate = round(1.0 - utility_rate, 4)
    degradation = None
    if canonical_rate is not None and evasion_rate is not None:
        degradation = round(canonical_rate - evasion_rate, 4)
    return {
        "canonical_catch_rate": canonical_rate,
        "evasion_catch_rate": evasion_rate,
        "evasion_degradation": degradation,
        "false_positive_rate": fp_rate,
        "utility_preservation_rate": utility_rate,
    }


def build_measurement_metrics(results):
    """Return catch/FPR/evasion metrics for labelled measurement rows, or None."""
    labelled = [r for r in results if r.get("measurement_suite") == MEASUREMENT_SUITE]
    if not labelled:
        return None
    by_trap = {}
    trap_classes = sorted({r["trap_class"] for r in labelled})
    for trap_class in trap_classes:
        rows = [r for r in labelled if r["trap_class"] == trap_class]
        block = _measurement_rate_block(rows)
        block.update({
            "rows": len(rows),
            "scenario_kind_counts": _status_counts(
                {"status": r.get("scenario_kind", "unknown")} for r in rows),
            "status_counts": _status_counts(rows),
        })
        by_trap[trap_class] = block

    by_evasion = {}
    techniques = sorted({
        r.get("evasion_technique") for r in labelled
        if r.get("evasion_technique") and r.get("evasion_technique") != "none"
    })
    for technique in techniques:
        rows = [r for r in labelled if r.get("evasion_technique") == technique]
        by_evasion[technique] = {
            "rows": len(rows),
            "catch_rate": _rate(rows),
            "status_counts": _status_counts(rows),
        }

    block = _measurement_rate_block(labelled)
    block.update({
        "suite": MEASUREMENT_SUITE,
        "total_rows": len(labelled),
        "measured_rows": sum(1 for r in labelled if r.get("status") in MEASURED_STATUSES),
        "unmeasured_rows": sum(1 for r in labelled if r.get("status") not in MEASURED_STATUSES),
        "scenario_kind_counts": _status_counts(
            {"status": r.get("scenario_kind", "unknown")} for r in labelled),
        "status_counts": _status_counts(labelled),
        "by_trap_class": by_trap,
        "by_evasion_technique": by_evasion,
    })
    return block


def build_report(results, controls):
    """Aggregate results into an evidence-level scorecard (no overclaim)."""
    trap_classes, evidence_levels = set(), set()
    control_counts, unmapped = {}, set()
    failures = 0
    for result in results:
        _validate_result(result)
        trap_classes.add(result["trap_class"])
        evidence_levels.add(result["evidence_level"])
        if result["status"] == "fail":
            failures += 1
        for cid in result["controls"]:
            control_counts[cid] = control_counts.get(cid, 0) + 1
            if cid not in controls:
                unmapped.add(cid)
    remediation = []
    if unmapped:
        remediation.append("Map or downgrade-to-candidate the unmapped control ids.")
    remediation.append("Keep OpenCRE mapping relation status visible in every report.")
    if "L3_live_behavioural" not in evidence_levels:
        remediation.append("Mock evidence only (L2) — run the M6 sandboxed live adapter for L3.")
    measurement_metrics = build_measurement_metrics(results)
    return {
        # Honest: this is evidence, never a certification or a pass/fail badge.
        "certification_claim": False,
        "status": "self_assessment_evidence",
        "trap_classes": sorted(trap_classes),
        "evidence_levels": sorted(evidence_levels),
        "controls": dict(sorted(control_counts.items())),
        "unmapped_controls": sorted(unmapped),
        "failures": failures,
        "measurement_metrics": measurement_metrics,
        "remediation": remediation,
    }


def results_from_scenarios(scenarios_dir):
    """Project validated scenarios into L2 result rows (for the smoke chain)."""
    results = []
    for path in sorted(Path(scenarios_dir).glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        row = {
            "scenario_id": data["id"],
            "trap_class": data["trap_class"],
            "controls": data["controls"],
            "evidence_level": "L2_mock_behavioural",
            "status": "pass",
        }
        for field in (
            "measurement_suite", "scenario_kind", "evasion_technique",
            "expected_control_behavior",
        ):
            if field in data:
                row[field] = data[field]
        results.append(row)
    return results


def enrich_results_from_scenarios(results, scenarios_dir):
    """Attach measurement labels to result rows using scenario_id as the join key."""
    if not scenarios_dir:
        return results
    by_id = {}
    for path in sorted(Path(scenarios_dir).glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        by_id[data["id"]] = data
    enriched = []
    for result in results:
        row = dict(result)
        scenario = by_id.get(row.get("scenario_id"))
        if scenario:
            for field in (
                "measurement_suite", "scenario_kind", "evasion_technique",
                "expected_control_behavior",
            ):
                row.setdefault(field, scenario.get(field))
        enriched.append(row)
    return enriched


def render_markdown(report):
    lines = [
        "# AGT Red Team — Evidence-Level Scorecard",
        "",
        "> **This is evidence, not a certification.** "
        f"`certification_claim: {str(report['certification_claim']).lower()}`. "
        "Results are graded by evidence level (L0–L3), not a pass/fail badge.",
        "",
        f"- status: `{report['status']}`",
        f"- trap classes covered: {', '.join(report['trap_classes']) or '(none)'}",
        f"- evidence levels: {', '.join(report['evidence_levels']) or '(none)'}",
        f"- failures: {report['failures']}",
        "",
        "## Control coverage (AGT-AC)",
    ]
    for cid, count in report["controls"].items():
        flag = " — UNMAPPED (candidate)" if cid in report["unmapped_controls"] else ""
        lines.append(f"- {cid}: {count}{flag}")
    lines += ["", "## Remediation"]
    lines += [f"- {note}" for note in report["remediation"]]
    metrics = report.get("measurement_metrics")
    if metrics:
        lines += [
            "",
            "## Measurement Metrics",
            "",
            f"- suite: `{metrics['suite']}`",
            f"- rows: {metrics['total_rows']} ({metrics['unmeasured_rows']} unmeasured)",
            f"- canonical catch rate: {metrics['canonical_catch_rate']}",
            f"- evasion catch rate: {metrics['evasion_catch_rate']}",
            f"- evasion degradation: {metrics['evasion_degradation']}",
            f"- false-positive rate: {metrics['false_positive_rate']}",
            f"- utility-preservation rate: {metrics['utility_preservation_rate']}",
        ]
    return "\n".join(lines) + "\n"


def main(argv):
    parser = argparse.ArgumentParser(prog="scorecard.py")
    parser.add_argument("--controls", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--results", default=None, help="results JSONL")
    parser.add_argument("--from-scenarios", default=None, help="scenarios dir to project")
    parser.add_argument("--scenarios", default=None, help="scenario dir for result metadata join")
    try:
        args = parser.parse_args(argv[1:])
    except SystemExit:
        return 2
    if not args.results and not args.from_scenarios:
        print("usage: provide --results <jsonl> or --from-scenarios <dir>", file=sys.stderr)
        return 2

    try:
        controls = load_controls(args.controls)
        if args.from_scenarios:
            results = results_from_scenarios(args.from_scenarios)
        else:
            results = [json.loads(line) for line in
                       Path(args.results).read_text(encoding="utf-8").splitlines() if line.strip()]
            results = enrich_results_from_scenarios(results, args.scenarios)
        report = build_report(results, controls)
    except ResultError as exc:
        print(f"result error: {exc}", file=sys.stderr)
        return 1
    except (OSError, json.JSONDecodeError) as exc:
        print(f"input error: {exc}", file=sys.stderr)
        return 1

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "scorecard_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "scorecard_report.md").write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps(
        {"certification_claim": report["certification_claim"],
         "controls": len(report["controls"]), "failures": report["failures"]},
        sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
