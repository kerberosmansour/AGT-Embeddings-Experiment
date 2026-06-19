#!/usr/bin/env bash
# AGT redteam benchmark smoke (M3) — the single reproducible entrypoint.
#
# Outcome-first (oc-3): the assessing engineer runs ONE command and gets the
# whole assessment (validate -> harness) with a single pass/fail + summaries.
# Fail-fast: the first non-zero step stops the run (set -euo pipefail).
#
# Portable (DW-004): uses `python` with a `python3` fallback and a bash array
# for the scenario paths (no bare CLI glob). Runs under Linux CI and Git-Bash.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PY="${PYTHON:-python3}"
command -v "$PY" >/dev/null 2>&1 || PY=python

SCEN_DIR="${AGTRT_SCENARIOS:-$HERE/scenarios}"
scenarios=("$SCEN_DIR"/*.json)

echo "[smoke] 1/3 validate scenarios (${#scenarios[@]} files)"
"$PY" "$HERE/schema/validate_scenarios.py" "${scenarios[@]}"

echo "[smoke] 2/3 mock harness"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
"$PY" "$HERE/harness/runner.py" --out "$TMP"

echo "[smoke] 3/3 evidence-level scorecard"
"$PY" "$HERE/reporters/scorecard.py" --controls "$HERE/controls/agt-ac.csv" --from-scenarios "$SCEN_DIR" --out "$TMP"

echo "[smoke] OK"
