#!/usr/bin/env bash
# AGTRTC M5 release gate wrapper.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat <<'USAGE'
usage: run-release-gate.sh --l1-report PATH --l1-results PATH --m4-dir DIR --out DIR [--scenario-set DIR]

Renders the M5 joint release evidence report from validated L1 and M4 artifacts.
The output is non-certifying and metadata-only.
USAGE
}

if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
  usage
  exit 0
fi

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

PY="$(pick_python)" || { echo "[release-gate] FAIL: no working python interpreter found" >&2; exit 1; }

SCENARIO_SET="$HERE/scenarios"
ARGS=()
while [ "$#" -gt 0 ]; do
  case "$1" in
    --scenario-set)
      SCENARIO_SET="$2"
      shift 2
      ;;
    --l1-report|--l1-results|--m4-dir|--out)
      ARGS+=("$1" "$2")
      shift 2
      ;;
    *)
      echo "[release-gate] unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

"$PY" "$HERE/reporters/release_gate.py" "${ARGS[@]}" --scenario-set "$SCENARIO_SET"
