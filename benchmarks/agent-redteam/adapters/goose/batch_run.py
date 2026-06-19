#!/usr/bin/env python3
"""Batch runner for the Goose live adapter over a scenario directory.

This is a convenience wrapper around adapter.run_live. It does not weaken the
adapter's fail-closed sandbox/credential gates; it only repeats the single-row
live path and writes a scorecard-compatible JSONL result stream.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import adapter  # noqa: E402
import sandbox  # noqa: E402


MEASUREMENT_FIELDS = (
    "measurement_suite", "scenario_kind", "evasion_technique",
    "expected_control_behavior",
)


def load_scenarios(scenarios_dir, limit=None):
    paths = sorted(Path(scenarios_dir).glob("*.json"))
    if limit is not None:
        paths = paths[:limit]
    return [json.loads(path.read_text(encoding="utf-8")) for path in paths]


def row_from_result(scenario, result):
    row = adapter.build_scorecard_result(scenario, result)
    for field in MEASUREMENT_FIELDS:
        if field in scenario:
            row[field] = scenario[field]
    if result.get("reason"):
        row["reason"] = result["reason"]
    return row


def run_batch(scenarios, *, out, model=adapter.DEFAULT_MODEL,
              max_tokens=adapter.DEFAULT_MAX_TOKENS, runner=adapter.run_live):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    rows, raw_results = [], []
    summary = {
        "total": len(scenarios),
        "completed": 0,
        "skipped": 0,
        "l3_trace_rows": 0,
        "no_trace_rows": 0,
        "status_counts": {},
    }
    for scenario in scenarios:
        result = runner(scenario, model=model, max_tokens=max_tokens)
        raw_results.append({"scenario_id": scenario.get("id"), "result": result})
        row = row_from_result(scenario, result)
        rows.append(row)
        if result.get("status") == "completed":
            summary["completed"] += 1
        if result.get("status") == "skipped":
            summary["skipped"] += 1
        if row.get("evidence_level") == "L3_live_behavioural":
            summary["l3_trace_rows"] += 1
        else:
            summary["no_trace_rows"] += 1
        status = row.get("status", "unknown")
        summary["status_counts"][status] = summary["status_counts"].get(status, 0) + 1

    (out / "live_results.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )
    (out / "live_raw_results.json").write_text(
        json.dumps(raw_results, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out / "live_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return summary


def main(argv):
    parser = argparse.ArgumentParser(prog="batch_run.py")
    parser.add_argument("--scenarios", required=True, help="scenario directory")
    parser.add_argument("--out", required=True, help="output directory")
    parser.add_argument("--limit", type=int, default=None,
                        help="optional first-N limit for bounded live slices")
    parser.add_argument("--model", default=adapter.DEFAULT_MODEL)
    parser.add_argument("--max-tokens", type=int, default=adapter.DEFAULT_MAX_TOKENS)
    try:
        args = parser.parse_args(argv[1:])
    except SystemExit:
        return 2
    try:
        scenarios = load_scenarios(args.scenarios, limit=args.limit)
        summary = run_batch(scenarios, out=args.out, model=args.model,
                            max_tokens=args.max_tokens)
    except sandbox.SandboxUnavailable as exc:
        print(f"refusing batch live run: {exc}", file=sys.stderr)
        return 1
    except (OSError, json.JSONDecodeError) as exc:
        print(f"input error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
