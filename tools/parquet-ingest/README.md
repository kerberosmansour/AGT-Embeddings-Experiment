# parquet-ingest

Small Rust helper for research intake: convert Parquet files to line-delimited
JSON without pulling the dependency into the normalizer crate.

```bash
cargo run --manifest-path tools/parquet-ingest/Cargo.toml -- \
  --schema data.parquet

cargo run --manifest-path tools/parquet-ingest/Cargo.toml -- \
  data.parquet --output data.jsonl --limit 1000
```

Python-side tooling lives in the repo root `requirements-parquet.txt`.
