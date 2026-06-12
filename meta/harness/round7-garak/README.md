# Round-7 Garak 2x2 Harness

WS-C measurement harness for issue #16. It compares:

| | Round-4 corpus | Round-7 corpus |
|---|---|---|
| Old Gate-0 normalizer | regression anchor | baseline |
| New AGT Rust normalizer | non-regression guard | treatment |

The fixed detector bank is the round-4 exemplar split. Each cell selects a
zero-benign-FP threshold on validation, writes the freeze record, then scores
test rows once.

## Smoke

```bash
python3 meta/harness/round7-garak/run_2x2.py --profile smoke
python3 meta/harness/round7-garak/validate_round7_garak.py artifacts/round7-garak/smoke/manifest.json
```

`--profile smoke` defaults to `metadata-smoke`, a deterministic contract scorer.
It proves the AGT-shaped artifact/freeze/matrix workflow without requiring a
local embedding model. It is not the headline measurement.

## Real kNN Measurement

```bash
python3.13 -m venv .venv-round6
.venv-round6/bin/pip install --require-hashes -r meta/harness/round6-cascade/requirements.lock

.venv-round6/bin/python meta/harness/round7-garak/run_2x2.py --profile smoke --scorer knn --out-dir artifacts/round7-garak/smoke-knn
python3 meta/harness/round7-garak/validate_round7_garak.py artifacts/round7-garak/smoke-knn/manifest.json

.venv-round6/bin/python meta/harness/round7-garak/run_2x2.py --profile pilot --scorer knn --out-dir artifacts/round7-garak/pilot-knn
python3 meta/harness/round7-garak/validate_round7_garak.py artifacts/round7-garak/pilot-knn/manifest.json
```

`--scorer knn` uses the round-4 bge-small kNN margin protocol via the round-6
harness helpers and requires local `fastembed` dependencies/model cache.

## Public-Safe Output

Artifacts contain row IDs, row hashes, labels, transform tags, metrics, and
breakdowns only. Raw row text and normalized text are never serialized.
