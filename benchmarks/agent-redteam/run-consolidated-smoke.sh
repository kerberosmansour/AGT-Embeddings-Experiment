#!/usr/bin/env bash
# AGT consolidated redteam M2 smoke.
#
# Outcome-first (oc-agtrtc-2): one command emits a one-family joint L1/L2
# report for indirect injection. This command is mock/L2 only and never emits
# L3_live_behavioural evidence.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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
PY="$(pick_python)" || { echo "[consolidated-smoke] FAIL: no working python interpreter found" >&2; exit 1; }

if [ -n "${AGTRTC_OUT:-}" ]; then
  OUT="$AGTRTC_OUT"
  mkdir -p "$OUT"
  CLEANUP=0
else
  OUT="$(mktemp -d)"
  CLEANUP=1
fi
if [ "$CLEANUP" = "1" ]; then
  trap 'rm -rf "$OUT"' EXIT
fi

echo "[consolidated-smoke] 1/3 build one-family L1/L2 joint report"
"$PY" "$HERE/consolidated/bridge.py" --out "$OUT" "$@"

echo "[consolidated-smoke] 2/3 raw-free output hygiene"
"$PY" "$HERE/hygiene/raw_free_scan.py" "$OUT"

echo "[consolidated-smoke] 3/3 report summary"
"$PY" -m json.tool "$OUT/consolidated_report.json" >/dev/null

echo "[consolidated-smoke] OK out=$OUT"
