#!/usr/bin/env python3
"""OpenCRE relation-quality validator (M7) — stdlib-only, fail-honest.

Front-to-end (oc-7): the assessing engineer runs

    python validate_relations.py

and gets an honest relation report from the bundled `relations.csv` and
`agt-ac.csv`: each AGT-AC -> OpenCRE relation is reported with its claimed
relation, backing reference, and EFFECTIVE relation. The effective relation
equals the claim ONLY when a committed backing reference exists; otherwise it is
downgraded to `candidate` (no false authority). This is self-assessment
evidence, NOT an OpenCRE/OWASP certification.

Exit codes: 0 ok | 1 malformed relation data | 2 usage.
"""
import argparse
import csv
import json
import sys
from pathlib import Path

RELATION_VOCAB = {"exact", "broad", "narrow", "related", "candidate"}
RELATION_REQUIRED = {"control_id", "target", "relation", "backing_ref"}
HERE = Path(__file__).resolve().parent
DEFAULT_RELATIONS = HERE / "relations.csv"
DEFAULT_CONTROLS = HERE.parent / "agt-ac.csv"


class RelationError(ValueError):
    """A relation row is malformed (unknown vocab / missing field)."""


def load_relations(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_control_ids(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return {row["id"] for row in csv.DictReader(handle)}


def build_report(rows, control_ids):
    relations, unmapped = [], set()
    verified = candidate = downgraded = 0
    for row in rows:
        if not RELATION_REQUIRED <= set(row):
            raise RelationError(f"relation row missing fields: {row}")
        claimed = (row["relation"] or "").strip()
        if claimed not in RELATION_VOCAB:
            raise RelationError(f"unknown relation {claimed!r} for {row['control_id']}")
        backing = (row["backing_ref"] or "").strip()
        # Fail-honest: a relation is only as strong as its committed backing.
        effective = claimed if backing else "candidate"
        if backing:
            verified += 1
        else:
            candidate += 1
            if claimed != "candidate":
                downgraded += 1
        if row["control_id"] not in control_ids:
            unmapped.add(row["control_id"])
        relations.append({
            "control_id": row["control_id"],
            "target": row["target"],
            "claimed_relation": claimed,
            "backing_ref": backing,
            "effective_relation": effective,
        })
    return {
        "certification_claim": False,
        "note": "self-assessment evidence; relations are candidate unless backed by a committed OpenCRE reference",
        "verified": verified,
        "candidate": candidate,
        "downgraded": downgraded,
        "unmapped_controls": sorted(unmapped),
        "relations": relations,
    }


def main(argv):
    parser = argparse.ArgumentParser(prog="validate_relations.py")
    parser.add_argument("--relations", default=DEFAULT_RELATIONS)
    parser.add_argument("--controls", default=DEFAULT_CONTROLS)
    try:
        args = parser.parse_args(argv[1:])
    except SystemExit:
        return 2
    try:
        report = build_report(load_relations(args.relations), load_control_ids(args.controls))
    except RelationError as exc:
        print(f"relation error: {exc}", file=sys.stderr)
        return 1
    except (OSError, KeyError) as exc:
        print(f"input error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
