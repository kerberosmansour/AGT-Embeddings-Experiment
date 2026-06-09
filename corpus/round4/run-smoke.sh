#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

CORPUS="corpus/round4/injection-round4-smoke.jsonl"
MANIFEST="corpus/round4/manifest-smoke.json"
CHECK_SUMMARY="corpus/round4/check-smoke-summary.json"
PER_ROW="corpus/round4/rules-baseline-smoke.jsonl"
RULES_SUMMARY="corpus/round4/rules-baseline-smoke-summary.json"
RULES_METRICS="corpus/round4/rules-baseline-smoke-metrics.json"
RUST_MANIFEST="tools/agt-rules-baseline/Cargo.toml"

echo "[round4] compile Python helpers"
python3 -m py_compile \
  corpus/round4/generate-round4.py \
  corpus/round4/check-round4.py \
  corpus/round4/summarize-baseline.py

echo "[round4] regenerate smoke corpus + manifest"
python3 corpus/round4/generate-round4.py --profile smoke

echo "[round4] validate corpus hygiene"
python3 corpus/round4/check-round4.py \
  "$CORPUS" \
  --manifest "$MANIFEST" \
  --summary-json "$CHECK_SUMMARY" \
  >/tmp/round4-check-smoke.out
tail -n 1 /tmp/round4-check-smoke.out

echo "[round4] compile Rust AGT scorer"
cargo check --manifest-path "$RUST_MANIFEST"

echo "[round4] regenerate Rust AGT rules baseline"
cargo run --manifest-path "$RUST_MANIFEST" -- \
  "$CORPUS" \
  --per-row "$PER_ROW" \
  --summary "$RULES_SUMMARY" \
  >/tmp/round4-rules-baseline.out

echo "[round4] rebuild Wilson/base-rate metrics"
python3 corpus/round4/summarize-baseline.py \
  "$RULES_SUMMARY" \
  --out "$RULES_METRICS"

echo "[round4] assert metadata-only evidence outputs"
python3 - "$PER_ROW" "$RULES_SUMMARY" "$RULES_METRICS" <<'PY'
import json
import sys
from pathlib import Path

per_row, summary, metrics = [Path(p) for p in sys.argv[1:]]

for lineno, line in enumerate(per_row.read_text(encoding="utf-8").splitlines(), 1):
    if not line.strip():
        continue
    row = json.loads(line)
    if "text" in row:
        raise SystemExit(f"{per_row}:{lineno}: raw text field leaked into per-row evidence")

for path in (summary, metrics):
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("raw_text_in_output") is not False:
        raise SystemExit(f"{path}: raw_text_in_output must be false")

print("metadata-only evidence: PASS")
PY

echo "[round4] smoke reproduction complete"
