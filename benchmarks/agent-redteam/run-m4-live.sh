#!/usr/bin/env bash
# AGT consolidated redteam M4 live batch.
#
# One preserved output directory contains the frozen sample manifest, live
# results, validation report, and raw-free evidence. Default row counts are set
# to clear the release failure bar: 30 per active attack stratum and 40 utility
# rows (0/40 false blocks gives a Wilson upper below 10%).
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

PY="$(pick_python)" || { echo "[m4-live] FAIL: no working python interpreter found" >&2; exit 1; }

if [ -n "${AGTRTC_M4_OUT:-}" ]; then
  OUT="$AGTRTC_M4_OUT"
  mkdir -p "$OUT"
else
  OUT="$(mktemp -d)"
fi

ATTACK_ROWS="${AGTRTC_M4_ATTACK_ROWS_PER_STRATUM:-30}"
UTILITY_ROWS="${AGTRTC_M4_UTILITY_ROWS:-40}"
MAX_CALLS="${AGTRTC_M4_MAX_LIVE_CALLS:-250}"
MODEL="${AGTRT_LIVE_MODEL:-claude-haiku-4-5}"

sample_args=(
  --out "$OUT"
  --attack-rows-per-stratum "$ATTACK_ROWS"
  --utility-rows "$UTILITY_ROWS"
  --max-live-calls "$MAX_CALLS"
)

if [ -n "${AGTRTC_M4_L1_REPORT:-}" ]; then
  sample_args+=(--l1-report "$AGTRTC_M4_L1_REPORT")
fi
if [ -n "${AGTRTC_M4_L1_RESULTS:-}" ]; then
  sample_args+=(--l1-results "$AGTRTC_M4_L1_RESULTS")
fi
if [ -n "${AGTRTC_M4_WAIVER_REASON:-}" ]; then
  sample_args+=(--waiver-reason "$AGTRTC_M4_WAIVER_REASON")
fi
if [ -n "${AGTRTC_M4_FAMILY:-}" ]; then
  sample_args+=(--family "$AGTRTC_M4_FAMILY")
fi

echo "[m4-live] 1/4 freeze sample manifest"
"$PY" "$HERE/adapters/goose/m4_batch.py" build-sample "${sample_args[@]}"

echo "[m4-live] 2/4 run bounded sandboxed live batch"
"$PY" "$HERE/adapters/goose/m4_batch.py" run "${sample_args[@]}" --model "$MODEL"

echo "[m4-live] 3/4 validate M4 failure bar"
"$PY" "$HERE/adapters/goose/m4_batch.py" validate --out "$OUT"

echo "[m4-live] 4/4 raw-free output hygiene"
"$PY" "$HERE/hygiene/raw_free_scan.py" "$OUT"

echo "[m4-live] OK out=$OUT"
