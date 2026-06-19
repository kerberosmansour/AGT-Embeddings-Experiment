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

# Portable interpreter pick (DW-004). A `command -v` check is NOT enough on
# Windows: `python3` there is a Store-alias that PASSES `command -v` but does not
# actually run Python (it prints an install hint and exits non-zero), so the old
# `command -v "$PY" || PY=python` never fell back and the smoke failed (exit 49)
# under Git-Bash. Probe by ACTUALLY RUNNING each candidate; `PYTHON` overrides.
pick_python() {
  if [ -n "${PYTHON:-}" ]; then printf '%s\n' "$PYTHON"; return 0; fi
  local c
  for c in python3 python; do
    if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys' >/dev/null 2>&1; then
      printf '%s\n' "$c"; return 0
    fi
  done
  return 1
}
PY="$(pick_python)" || { echo "[smoke] FAIL: no working python interpreter found" >&2; exit 1; }

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
