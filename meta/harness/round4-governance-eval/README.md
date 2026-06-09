# round4-governance-eval

Validation helpers for future Round-4 governance metadata evaluation artifacts.

These helpers do not run AGT, score embeddings, call tools, import source
material, or change policy code. They only check that governance evidence is
metadata-only and shaped as action-outcome evidence rather than label-only
evidence.

Rows with `expected_action=quarantine` must carry `quarantine_intent=true`, but
the decision itself must still be one of the native Rust policy labels
(`allow`, `deny`, `requires_approval`, or `rate_limited`) so failures remain
auditable without inventing a non-existent quarantine enum.

Example:

```bash
python3 meta/harness/round4-governance-eval/validate-governance-eval.py \
  --manifest artifacts/governance-eval/manifest.json \
  --validation artifacts/governance-eval/validation.jsonl \
  --test artifacts/governance-eval/test.jsonl \
  --metrics artifacts/governance-eval/metrics.json
```

Passing this validator means the evidence shape is ready for independent audit.
It does not mean governance metadata works, embeddings help, AGT is protected,
or any production/security certification claim is valid.

The `rust-generator/` directory contains the source harness that produced the
migrated metadata artifacts from the migrated Round-4 embedding and rules
inputs. Running it rewrites `artifacts/governance-eval/`, so audits should run
it only from a clean worktree or compare the resulting diff immediately.
