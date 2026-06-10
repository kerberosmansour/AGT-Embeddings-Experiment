# Upstream AGT PR Plan

Date: 2026-06-10
Owner: mac-agent
Status: planning contract; no upstream AGT code changes yet

## Team Feedback Adopted

The upstream path should be two PRs, in order:

1. Land the evaluation corpus and benchmark harness as a standalone test
   fixture.
2. Only after methodology review, land the embedding signal as an optional,
   default-off feature behind a flag.

The first PR has value even if AGT never adopts embeddings: it gives maintainers
a reproducible prompt-injection evaluation fixture for current and future
detectors. The second PR is blocked on methodology, because the corpus
generation and baseline pinning need to be credible before a detector path is
worth reviewing.

## Baseline Pin

The current evidence uses AGT's Rust prompt-injection detector as the
rules-only baseline. The migrated detector snapshot currently matches the local
AGT checkout:

| Item | Value |
|---|---|
| AGT checkout | local AGT checkout |
| Fresh AGT `origin/main` observed | `10a1cceb1bda63bc126fe054f0a13ff2ab93a42c` |
| Local checkout HEAD during read | `1bf359397df64aeb5285bdf5d609ade291c329b9` |
| Last detector-touching commit | `7c895824 feat(rust): configure prompt guard corpora and thresholds (#2440)` |
| Detector file | `agent-governance-rust/agentmesh/src/prompt_injection.rs` |
| Detector SHA-256 | `92ac1f855e03502886fffdfb8cf9eece8ce7c2bea268ecacb4ff6386cb345ab3` |
| Vendored experiment snapshot | same SHA-256 |

The fresh upstream baseline preflight is recorded in
`docs/methodology/agt-upstream-baseline-refresh.md`. Upstream `main` moved by
one non-detector dependency commit after the local checkout pin, but the
prompt-injection detector blob still matches the vendored experiment scorer.

The public file boundary for PR 1 is recorded in
`docs/methodology/upstream-pr1-public-file-manifest.md`.

The sanitized maintainer-facing PR draft is recorded in
`docs/methodology/upstream-pr1-pr-draft.md`.

The issue/PR cross-linking checklist is recorded in
`docs/methodology/upstream-pr1-issue-pr-linking.md`.

A read-only target-path dry run against current AGT `origin/main` is recorded in
`docs/methodology/upstream-pr1-target-path-dry-run.md`.

Before opening PR 1, rerun the rules-only baseline against a fresh AGT upstream
main and record:

- AGT commit SHA;
- detector file SHA-256;
- corpus manifest SHA-256;
- rules-only attack recall;
- rules-only benign false-positive rate;
- adjacent-security benign false-positive rate;
- the exact command used to reproduce the number.

The headline "about 1%" rules-only catch rate must not be treated as a general
AGT claim unless it is tied to this exact corpus, detector snapshot, and
reproduction command.

## PR 1: Standalone Evaluation Fixture

Goal: add a reproducible, low-risk benchmark fixture to AGT without changing
runtime behavior.

Proposed upstream target shape:

```text
benchmarks/
  prompt-injection/
    README.md
    corpus/
    harness/
    artifacts/
docs/
  benchmarks/
    prompt-injection-evaluation.md
```

If maintainers prefer existing paths, the same fixture can live under
`agent-governance-python/benchmarks/prompt_injection_eval/` with a docs page
under `docs/benchmarks/`. The important property is independence from runtime
feature code.

The current dry run found no root-level `benchmarks/` directory in AGT. That
means the preferred standalone path introduces a new repository convention;
Windows/native-semantics review should explicitly approve that choice or redirect
the fixture under an existing package benchmark path before PR staging.

Allowed contents:

- synthetic labelled prompt-injection corpus;
- manifest, split, leakage, and duplicate checks;
- baseline harness for AGT's existing Rust detector;
- source-review and matched-control gates informed by the Round-5
  source-scale pilot;
- metrics scripts for recall, false-positive rate, Wilson intervals, base-rate
  precision, and adjacent-security benign false positives;
- documentation that says this is research/evaluation evidence only.

Not allowed in PR 1:

- embedding runtime dependency;
- default threshold;
- policy-routing integration;
- production or certification language;
- claims about real-traffic performance;
- default blocking behavior.

Exit gate:

```bash
bash benchmarks/prompt-injection/run-smoke.sh
python3 benchmarks/prompt-injection/harness/check-corpus.py
python3 benchmarks/prompt-injection/harness/summarize-baseline.py
git diff --check
```

The PR summary should lead with the baseline-methodology boundary:

```text
This PR adds a standalone prompt-injection evaluation fixture. It does not add
an embedding detector or change AGT runtime behavior. The current rules-only
number is a corpus-specific baseline for this fixture, not a global claim about
AGT detection quality.
```

## Public Upstream Hygiene

This planning repository contains internal coordination notes. Do not copy this
document verbatim into an upstream Microsoft PR or issue.

Before opening an upstream PR:

- stage the change from a clean upstream branch/worktree;
- include only public fixture files, benchmark harness files, manifests,
  validators, and maintainer-facing documentation;
- exclude internal runbooks, coordination logs, task IDs, owner fields, local
  machine paths, and private branch names;
- write the PR title, PR body, commit messages, and issue comments as if they
  were authored directly by the project contributor, with no references to
  internal assistants, tooling, or coordination channels;
- use upstream-relative paths only;
- run a final text scan for internal markers before pushing or opening the PR.

Use `docs/methodology/upstream-pr1-public-file-manifest.md` as the file allowlist
and rewrite checklist for this step. Use
`docs/methodology/upstream-pr1-pr-draft.md` as a starting point for the PR
title/body only after the review gates pass and the baseline table is refreshed.
Use `docs/methodology/upstream-pr1-issue-pr-linking.md` for the issue text and
the issue-to-PR cross-link sequence.

## PR 2: Optional Embedding Signal

Goal: add an optional, auditable embedding evidence signal that can feed
review/routing logic, while leaving existing AGT behavior unchanged by default.

Hard prerequisite: PR 1 merged or explicitly accepted as the benchmark fixture.

Hard methodology prerequisite:

- corpus generation method is documented well enough for maintainers to review;
- family/group holdouts and duplicate checks are reproducible;
- baseline is rerun against current AGT main;
- thresholds are fit on validation only and frozen before test;
- no raw prompt text is emitted in per-row evaluation artifacts;
- review-load and false-positive costs are reported, not hidden.

Default posture:

- disabled by default;
- configured by explicit feature flag or config option;
- evidence-only unless a policy profile explicitly routes it;
- auditable score/margin output;
- no automatic hard block from embeddings alone;
- no hosted inference requirement.

Expected implementation shape:

```text
embedding signal -> risk/margin evidence -> AGT policy/review routing
```

Do not frame PR 2 as "embeddings replace rules." The evidence says the useful
path is additive: deterministic AGT controls remain the authority; embeddings
surface semantic cases that current rules miss.

## Round-5 Source-Scale Material

Round 5 is useful for PR 1 methodology, not PR 2 runtime behavior.

The sanitized migrated evidence is:

- `artifacts/source-scale-pilot/summary.json`;
- `docs/methodology/round5-source-scale-methodology.md`;
- `docs/reports/round5-source-scale-pilot.md`.

It records a 72-row source-scale pilot with 36 attack families, 18
adjacent-security benign families, 18 plain benign control families, zero
family/group/exact/near-duplicate cross-split leakage, and validation-only
threshold freeze before test scoring.

The pilot's embedding smoke result is intentionally not a headline claim: the
test split has only 12 attacks and 12 benign controls. Use it to show how AGT
could structure source-reviewed fixture generation; do not use it to claim
detector readiness.

For upstream AGT, the Round-5 pieces that belong in PR 1 are:

- source-record review schema;
- source-to-AGT expected-action mapping
  (`docs/methodology/source-to-agt-expected-action-mapping.md`);
- matched-control requirement;
- family/group/near-duplicate leakage gates;
- sanitized manifest and summary hashes;
- no-runtime-change documentation.

The raw scratch rows, internal audit notes, and embedding per-row outputs should
stay in this research repository unless maintainers explicitly request them.

## Methodology Blocker

The team feedback is right: the current corpus is useful, but the methodology
must be made boringly reviewable before PR 2.

Open questions to close:

| Question | Required answer before PR 2 |
|---|---|
| How were synthetic families generated? | Generator contract, seed, row caps, family templates, and mutation operators. |
| How is overfitting controlled? | Family/group split policy, held-out bypass classes, exact and near-duplicate leakage checks. |
| How are benign controls constructed? | Matched adjacent-security benign, quoted injection examples, docs/code fixtures, and legitimate imperative requests. |
| What is the baseline? | Current AGT rules-only detector at an exact commit and detector SHA. |
| What does "zero FP observed" mean? | A finite-sample observation on this corpus, with interval and base-rate caveat. |
| What is the production path? | Review/routing evidence only, optional/default-off, with governance metadata deciding action. |

## Current Interpretation

The strongest current product readout is:

- AGT's existing rules-only detector is intentionally high-precision and
  low-recall, so low recall on hard held-out examples is not surprising.
- The conservative embedding operating point catches a meaningful subset of
  attacks missed by rules with zero observed false positives on the frozen test
  split.
- That is enough to justify a reviewer/routing signal.
- It is not enough to justify default blocking.

## Agent Work Split

| Agent | Lane |
|---|---|
| Mac | Own PR 1 staging plan, baseline pin, harness packaging, and heavy local reproduction. |
| Linux | Audit corpus scope, reproducibility, leakage checks, and no-overclaim language. |
| Windows | Verify AGT semantics, current detector snapshot, path portability, and native vocabulary. |

The next AgentBus tasks should be PR 1 oriented. PR 2 should remain blocked
until PR 1's fixture and methodology are reviewed.
