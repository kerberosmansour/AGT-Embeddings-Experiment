# Round-4 AGT Rules Baseline

Rust scratch harness for scoring Round-4 JSONL rows with the real AGT Rust
prompt-injection detector.

This crate path-includes the sibling AGT checkout's
`agent-governance-rust/agentmesh/src/prompt_injection.rs`, matching the
Windows Round-3 harness pattern. It is for experiment evidence only; production
integration belongs in AGT.

```bash
cargo run --manifest-path tools/agt-rules-baseline/Cargo.toml -- \
  corpus/round4/injection-round4-smoke.jsonl \
  --per-row corpus/round4/rules-baseline-smoke.jsonl \
  --summary corpus/round4/rules-baseline-smoke-summary.json
```

Output intentionally excludes raw row text. Findings use AGT rule IDs / hashes.
