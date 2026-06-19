#!/usr/bin/env bash
# AGT red-team measurement-suite runner.
#
# Default: validate the 240-row measurement suite and produce the L2 projection
# scorecard. Pass --live to additionally run the Goose live adapter in batch.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

LIVE=0
LIMIT=""
for arg in "$@"; do
  case "$arg" in
    --live) LIVE=1 ;;
    --limit=*) LIMIT="${arg#--limit=}" ;;
  esac
done

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
PY="$(pick_python)" || { echo "[measurement] FAIL: no working python interpreter found" >&2; exit 1; }

SCEN_DIR="${AGTRT_MEASUREMENT_SCENARIOS:-$HERE/measurement/scenarios}"
OUT="${AGTRT_MEASUREMENT_OUT:-$(mktemp -d)}"
scenarios=("$SCEN_DIR"/*.json)

echo "[measurement] 1/3 validate scenarios (${#scenarios[@]} files)"
"$PY" "$HERE/schema/validate_scenarios.py" "${scenarios[@]}"

echo "[measurement] 2/3 L2 projection scorecard"
"$PY" "$HERE/reporters/scorecard.py" --controls "$HERE/controls/agt-ac.csv" \
  --from-scenarios "$SCEN_DIR" --out "$OUT/l2-scorecard"

if [ "$LIVE" = "1" ]; then
  echo "[measurement] 3/3 live Goose batch"
  limit_args=()
  if [ -n "$LIMIT" ]; then limit_args=(--limit "$LIMIT"); fi
  model_args=()
  if [ -n "${AGTRT_LIVE_MODEL:-}" ]; then model_args=(--model "$AGTRT_LIVE_MODEL"); fi
  "$PY" "$HERE/adapters/goose/batch_run.py" --scenarios "$SCEN_DIR" \
    --out "$OUT/live" "${limit_args[@]}" "${model_args[@]}"
  "$PY" "$HERE/reporters/scorecard.py" --controls "$HERE/controls/agt-ac.csv" \
    --results "$OUT/live/live_results.jsonl" --scenarios "$SCEN_DIR" \
    --out "$OUT/live-scorecard"
else
  echo "[measurement] 3/3 live Goose batch skipped (pass --live to opt in)"
fi

echo "{\"out\":\"$OUT\"}"
