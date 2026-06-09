# round4-embedding-sweep

Validation helpers for future Round-4 embedding/kNN sweep artifacts.

These helpers do not compute embeddings, select thresholds, import source
material, run AGT policy scoring, or inspect corpus row text. They only check
that a produced sweep artifact is shaped like the reviewed contract:

- freeze metadata exists and was selected on validation;
- per-row validation and test outputs are metadata-only JSONL;
- test rows are not accepted without a validation-selected freeze;
- neighbor evidence is represented by row IDs only;
- metrics include base-rate precision and adjacent-security benign FP signals.
- freeze/test-start/provenance SHA links accept byte-exact or CRLF-to-LF
  normalized hashes for cross-platform text checkouts.

Example:

```bash
python3 meta/harness/round4-embedding-sweep/validate-embedding-sweep.py \
  --freeze artifacts/embedding-sweep/freeze-record.json \
  --test-start artifacts/embedding-sweep/test-start-record.json \
  --validation artifacts/embedding-sweep/validation-per-row.jsonl \
  --test artifacts/embedding-sweep/test-per-row.jsonl \
  --validation-metrics artifacts/embedding-sweep/validation-metrics.json \
  --test-metrics artifacts/embedding-sweep/test-metrics.json \
  --provenance artifacts/embedding-sweep/provenance.json
```

Passing this validator means the artifact is audit-ready from a metadata and
provenance perspective. It does not mean the embedding signal is useful,
promoted, or production-ready.
