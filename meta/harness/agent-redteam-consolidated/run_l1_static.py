#!/usr/bin/env python3
"""Run the AGT consolidated L1 static detector tier."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from l1_static import build_artifacts


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True, type=Path, help="Output directory for L1 static artifacts.")
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    paths = build_artifacts(args.out)
    report = json.loads(paths["report"].read_text(encoding="utf-8"))
    print(
        json.dumps(
            {
                "report": str(paths["report"]),
                "row_count": report["row_count"],
                "l1_rows": report["l1_rows"],
                "l2_rows": report["l2_rows"],
                "l3_live_rows": report["l3_live_rows"],
                "hard_benign_fp_wilson_upper": report["hard_benign_fp_wilson_95"]["upper"],
                "failure_bar_clear": report["hard_benign_fp_wilson_95"]["upper"]
                <= report["hard_benign_fp_wilson_upper_bar"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
