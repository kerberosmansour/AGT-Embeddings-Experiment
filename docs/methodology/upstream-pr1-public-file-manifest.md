# Upstream PR1 Public File Manifest

Status: packaging guardrail
Date: 2026-06-10

This manifest defines the public file boundary for a future upstream AGT PR
that adds a standalone prompt-injection evaluation fixture. It is intentionally
stricter than this research repository: the upstream PR should contain only the
fixture, harness, manifests, validators, and maintainer-facing documentation
needed to reproduce the baseline.

Do not copy this research repository wholesale into AGT.

## Public PR Shape

Preferred upstream shape, subject to maintainer feedback:

```text
benchmarks/
  prompt-injection/
    README.md
    run-smoke.sh
    corpus/
      injection-smoke.jsonl
      manifest-smoke.json
      check-smoke-summary.json
    harness/
      check-corpus.py
      generate-corpus.py
      summarize-baseline.py
      agt-rules-baseline/
        Cargo.toml
        Cargo.lock
        src/main.rs
    artifacts/
      rules-baseline-smoke-summary.json
      rules-baseline-smoke-metrics.json
docs/
  benchmarks/
    prompt-injection-evaluation.md
```

If maintainers want the large corpus checked into AGT, add the large artifacts
below after review. Otherwise, keep the large corpus reproducible from the
generator and commit only the smoke fixture for CI speed.

```text
benchmarks/prompt-injection/corpus/injection-large.jsonl
benchmarks/prompt-injection/corpus/manifest-large.json
benchmarks/prompt-injection/corpus/check-large-summary.json
benchmarks/prompt-injection/artifacts/rules-baseline-large-summary.json
benchmarks/prompt-injection/artifacts/rules-baseline-large-metrics.json
```

The current sizes are approximately:

| File | Size |
|---|---:|
| `corpus/round4/injection-round4-smoke.jsonl` | 208K |
| `corpus/round4/rules-baseline-smoke.jsonl` | 196K |
| `corpus/round4/injection-round4-large.jsonl` | 32M |
| `corpus/round4/rules-baseline-large.jsonl` | 23M |

Do not include per-row large baseline output unless maintainers explicitly want
it. The summary and metrics files are usually enough for a baseline PR.

## Source-To-Public Mapping

Translate from this research repository into upstream paths rather than copying
paths and wording verbatim.

| Research source | Upstream destination | Notes |
|---|---|---|
| `corpus/round4/run-smoke.sh` | `benchmarks/prompt-injection/run-smoke.sh` | Rewrite paths to upstream-relative locations. |
| `corpus/round4/check-round4.py` | `benchmarks/prompt-injection/harness/check-corpus.py` | Rename for public clarity. |
| `corpus/round4/generate-round4.py` | `benchmarks/prompt-injection/harness/generate-corpus.py` | Keep deterministic generation and split controls. |
| `corpus/round4/summarize-baseline.py` | `benchmarks/prompt-injection/harness/summarize-baseline.py` | Keep Wilson interval and base-rate precision reporting. |
| `corpus/round4/injection-round4-smoke.jsonl` | `benchmarks/prompt-injection/corpus/injection-smoke.jsonl` | Preferred CI fixture. |
| `corpus/round4/manifest-smoke.json` | `benchmarks/prompt-injection/corpus/manifest-smoke.json` | Regenerate after upstream path changes. |
| `corpus/round4/check-smoke-summary.json` | `benchmarks/prompt-injection/corpus/check-smoke-summary.json` | Regenerate after upstream path changes. |
| `corpus/round4/rules-baseline-smoke-summary.json` | `benchmarks/prompt-injection/artifacts/rules-baseline-smoke-summary.json` | Metadata-only summary. |
| `corpus/round4/rules-baseline-smoke-metrics.json` | `benchmarks/prompt-injection/artifacts/rules-baseline-smoke-metrics.json` | Public CI metric. |
| `tools/agt-rules-baseline/Cargo.toml` | `benchmarks/prompt-injection/harness/agt-rules-baseline/Cargo.toml` | Rewrite dependency to use the in-repo AGT Rust crate. |
| `tools/agt-rules-baseline/Cargo.lock` | `benchmarks/prompt-injection/harness/agt-rules-baseline/Cargo.lock` | Regenerate if dependency layout changes. |
| `tools/agt-rules-baseline/src/main.rs` | `benchmarks/prompt-injection/harness/agt-rules-baseline/src/main.rs` | Remove vendored-source import and use AGT crate imports. |
| `docs/methodology/source-to-agt-expected-action-mapping.md` | `docs/benchmarks/prompt-injection-evaluation.md` section | Summarize native policy vocabulary only. |
| `docs/methodology/round5-source-scale-methodology.md` | `benchmarks/prompt-injection/README.md` methodology section | Use as guidance, not as a headline result. |
| `docs/methodology/agt-upstream-baseline-refresh.md` | PR body and benchmark README facts | Rewrite without local paths or internal task metadata. |

## Explicitly Excluded

These files and directories must not appear in the Microsoft-facing PR:

- `docs/RUNBOOK-*`;
- `docs/AGENTBUS-WORKSPLIT.md`;
- `docs/reports/*`;
- `docs/methodology/m3-governance-value-add-source-map.md`;
- `docs/methodology/upstream-pr1-public-file-manifest.md`;
- any internal coordination log, owner field, task identifier, local machine
  path, private branch name, or assistant/tooling reference;
- `artifacts/embedding-sweep/*`;
- `artifacts/governance-eval/*`;
- raw source-scale scratch rows or source-record review files;
- `tools/agt-rules-baseline/vendor/*`;
- `tools/agt-rules-baseline/target/*`;
- `__pycache__/`, `.pytest_cache/`, virtual environments, model caches, and
  other generated local build outputs.

Round-5 source-scale material may inform methodology wording, but only the
sanitized summary facts should be used. The tiny pilot is not a detector
performance claim.

## Required Rewrite Rules

- Replace research-internal names like `round4` in public headings with
  `prompt-injection evaluation fixture`; internal IDs may remain only inside
  stable row IDs if changing them would break manifests.
- Replace local absolute paths with upstream-relative paths.
- Remove owner, task, coordination, and local checkout fields from public docs.
- Keep the rules-only baseline tied to exact corpus, detector hash, and command.
- State clearly that PR1 does not add embeddings, default thresholds, policy
  routing, production behavior, or default blocking.
- Do not describe AGT's detector as generally catching only 1% of attacks; say
  the number is corpus-specific for this fixture.
- Do not introduce non-native AGT policy decisions.

## Final Public Scan

Run a final scan on the AGT PR branch before pushing:

```bash
rg -n "RUNBOOK|task id|owner:|local checkout|/Users/|private branch|coordination log|assistant|tooling reference" \
  benchmarks/prompt-injection docs/benchmarks
find benchmarks/prompt-injection docs/benchmarks \
  -type f \( -name '*.pyc' -o -path '*/target/*' -o -path '*/__pycache__/*' \) -print
git diff --check
```

The first two commands should return no output. If they find anything, fix the
PR branch before opening the PR.

## Review Gate

Do not open PR1 until:

- the Windows/native-semantics review agrees that the public paths and AGT Rust
  imports are idiomatic for the upstream repo;
- the Linux/reproducibility review agrees that the smoke fixture, metrics, and
  no-overclaim wording are reproducible;
- the final public scan above is clean.
