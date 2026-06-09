# Contributing

Thank you for helping improve the AGT prompt-injection embeddings experiment.
This repository is research evidence, not a production detector.

## Useful Contributions

- Reproduce the existing metrics from the committed corpus and artifacts.
- Add methodology critique, especially around false positives, base-rate effects,
  threshold choice, or corpus diversity.
- Propose additional AGT prompt-injection attack families or benign security
  discussion negatives.
- Compare alternative local embedding models or nearest-neighbour strategies.
- Improve validators, manifests, provenance checks, or platform portability.
- Tighten documentation where a claim is ambiguous or too strong.

## Out Of Scope

- Claims that the embedding layer is production-ready.
- Changes that make embeddings a default blocking path.
- Claims of certification, benchmark coverage, governance readiness, or real
  traffic validation.
- Unrelated product tracks or unrelated data-classification experiments.
- Raw secrets, live credentials, customer data, or private prompts.
- Source imports that are not explicitly captured in the provenance docs.

## Development Setup

Use the existing checked-in tools and artifacts. Do not rely on sibling checkouts
unless a command explicitly asks for one.

```bash
python3 corpus/round4/check-round4.py \
  --corpus corpus/round4/injection-round4-large.jsonl \
  --manifest corpus/round4/manifest-large.json

cargo check --manifest-path tools/agt-rules-baseline/Cargo.toml

python3 meta/harness/round4-embedding-sweep/validate-embedding-sweep.py \
  --manifest artifacts/embedding-sweep/provenance.json \
  --validation artifacts/embedding-sweep/validation-per-row.jsonl \
  --test artifacts/embedding-sweep/test-per-row.jsonl

python3 meta/harness/round4-governance-eval/validate-governance-eval.py \
  --manifest artifacts/governance-eval/manifest.json \
  --validation artifacts/governance-eval/validation.jsonl \
  --test artifacts/governance-eval/test.jsonl \
  --metrics artifacts/governance-eval/metrics.json

python3 meta/harness/round5-agt-value-add/validate-round5-agt-value-add-report.py \
  meta/harness/round5-agt-value-add/round5-agt-value-add-report.example.json
```

## Evidence Discipline

Every metric claim should point to a committed artifact, validator, or claims
ledger row. Synthetic rows must be described as synthetic. If a result shows a
tradeoff, include both sides of the tradeoff.

When in doubt, prefer narrower wording. The project is more useful when its
limits are visible.

## Pull Request Checklist

- The change is AGT prompt-injection scoped.
- The relevant validator or check command was run.
- New artifacts are metadata-only and do not contain private/raw operational
  data.
- Claims remain optional, default-off, additive, and research-only.
- `git diff --check` passes.
