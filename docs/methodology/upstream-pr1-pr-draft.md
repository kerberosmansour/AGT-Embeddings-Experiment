# Upstream PR1 Draft

Status: maintainer-facing draft; peer delta ACKs complete
Date: 2026-06-10

This draft is a sanitized starting point for a future upstream AGT pull request.
It should be rechecked against fresh upstream `main` before use. The
target-path/native-semantics and reproducibility/no-overclaim reviews have
passed with caveats recorded in the private readiness notes; do not open the
pull request until the final publish-time scans also pass.

## Suggested Title

```text
Add a prompt-injection evaluation fixture
```

Alternative:

```text
Add a prompt-injection benchmark corpus and baseline harness
```

## Suggested PR Body

```markdown
## Summary

This PR adds a standalone prompt-injection evaluation fixture. It does not
change AGT runtime behavior.

Included:

- a synthetic labelled prompt-injection corpus for benchmark evaluation;
- manifest and corpus hygiene checks for split, duplicate, and leakage review;
- a baseline harness for AGT's existing Rust prompt-injection detector;
- summary metrics for the rules-only detector on this fixture;
- documentation describing the reproduction path and claim boundaries.

Not included:

- no embedding detector;
- no runtime dependency;
- no default threshold;
- no policy-routing integration;
- no production or real-traffic performance claim;
- no default blocking behavior.

## Baseline Boundary

The rules-only metrics in this PR are corpus-specific benchmark results. They
should not be read as a general statement about AGT detection quality.

AGT's existing rules layer is intentionally high-precision and low-recall. This
fixture is meant to make that trade-off measurable on a hard synthetic
evaluation set and to give future detector changes a reproducible baseline.

Before merge, this baseline should be pinned to the exact AGT commit, detector
file hash, corpus manifest hash, and command used to reproduce it.

## Current Baseline Snapshot

| Item | Value |
|---|---|
| AGT base commit checked | `730ffbb060c44362485b786c63aa08439c49d7e1` |
| Detector file | `agent-governance-rust/agentmesh/src/prompt_injection.rs` |
| Detector SHA-256 | `92ac1f855e03502886fffdfb8cf9eece8ce7c2bea268ecacb4ff6386cb345ab3` |
| Smoke manifest SHA-256 | `e3f13f6de459391952b00b14ebaae3d83510581265ac3099b62af565a14753f6` |
| Smoke corpus SHA-256 | `238636ed671f1909f0610ef62b4bb438f801670cdadfd681ab8d9a7397b8bbc1` |
| Corpus rows | `280` |
| Attack rows | `110` |
| Benign rows | `170` |
| Rules-only attack recall | `7 / 110 = 0.063636` |
| Rules-only benign false-positive rate | `16 / 170 = 0.094118` |

These are smoke-fixture numbers only. If upstream `main` has moved or the
fixture is regenerated, refresh this table before opening or merging.

## Validation

```bash
bash benchmarks/prompt-injection/run-smoke.sh
git diff --check
find benchmarks/prompt-injection docs/benchmarks \
  -type f \( -name '*.pyc' -o -path '*/target/*' -o -path '*/__pycache__/*' \) -print
```

## Review Questions

- Is `benchmarks/prompt-injection/` the right location for this fixture?
- Should the large corpus be checked in, generated on demand, or kept outside
  the initial PR until maintainers review size and CI cost?
- Should the Rust baseline harness live under the benchmark fixture, or should
  it be wired into an existing AGT benchmark/test convention?
- Are the corpus hygiene checks sufficient for a first fixture PR, or should
  additional source-review or matched-control checks be required before merge?

## Follow-Up

If this benchmark fixture is accepted, a later PR can propose an optional,
default-off embedding evidence signal. That follow-up should remain separate
from this fixture PR and should not change default AGT behavior.
```

## Before Opening

- Copy only the files listed in
  `docs/methodology/upstream-pr1-public-file-manifest.md`.
- Rewrite paths to upstream-relative locations.
- Remove local checkout paths and private branch names.
- Regenerate corpus manifests and summaries after the upstream path rewrite.
- Rerun `bash benchmarks/prompt-injection/run-smoke.sh` against fresh upstream
  `main`.
- Replace the preflight table if any commit, hash, artifact, or metric changed.
- Keep large corpus artifacts out of the first PR unless maintainers want them.
- Do not include internal runbooks, coordination notes, task identifiers, owner
  metadata, scratch files, model outputs, caches, or build outputs.

## Final Public Scan

Run these checks on the future upstream PR branch before pushing:

```bash
rg -n "RUNBOOK|task id|owner:|local checkout|/Users/|private branch|coordination log|internal coordination|Codex|Claude|AgentBus|SunLit" \
  benchmarks/prompt-injection docs/benchmarks
find benchmarks/prompt-injection docs/benchmarks \
  -type f \( -name '*.pyc' -o -path '*/target/*' -o -path '*/__pycache__/*' \) -print
git diff --check
```

The first two commands should return no output.

## Wording Guardrails

- Say "standalone evaluation fixture", not "runtime detector change".
- Say "corpus-specific baseline", not "AGT generally catches only 1%".
- Say "synthetic labelled corpus", not "real traffic".
- Say "optional follow-up evidence signal", not "replacement detector".
- Say "review/routing evidence" for future embedding work, not "default block".
