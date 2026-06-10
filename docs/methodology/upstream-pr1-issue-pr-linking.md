# Upstream PR1 Issue And PR Linking

Status: pre-open checklist
Date: 2026-06-10

This note prepares the issue/PR cross-linking step for the future upstream AGT
PR 1. It is not itself upstream content. Use it only after the PR 1 review
gates pass and the baseline pin has been refreshed against current upstream
`main`.

## Preconditions

- Reproducibility/no-overclaim review has passed.
- Target-path/native-semantics review has passed.
- The future upstream branch contains only the public fixture package.
- The rules-only baseline table has been refreshed if upstream `main` moved.
- The final public scan is clean.

## Suggested Issue Title

```text
Add a prompt-injection evaluation fixture
```

## Suggested Issue Body

```markdown
## Summary

This issue tracks adding a standalone prompt-injection evaluation fixture for
AGT.

The fixture would provide:

- a synthetic labelled prompt-injection corpus;
- manifest and corpus hygiene checks;
- a baseline harness for the existing Rust prompt-injection detector;
- summary metrics for the rules-only detector on this fixture;
- documentation for reproducing the benchmark and interpreting its limits.

## Scope

This is an evaluation fixture only. It does not propose a runtime behavior
change, embedding detector, default threshold, policy-routing integration, or
default blocking behavior.

## Why

AGT's existing rules layer is intentionally high-precision and low-recall. A
standalone fixture would make that trade-off measurable on a reproducible
benchmark and give future prompt-injection detector changes a stable baseline.

## Acceptance Criteria

- The fixture can be run from the repository with documented commands.
- Corpus split, duplicate, and leakage checks are reproducible.
- Baseline metrics are tied to an exact AGT commit, detector file hash, corpus
  manifest hash, and command.
- Documentation states that results are corpus-specific and not a general claim
  about AGT detection quality.
- No AGT runtime behavior changes are included.
```

## Suggested PR Cross-Link Text

Use one of these in the PR body after the issue exists:

```markdown
Refs #ISSUE_NUMBER
```

Use this only if maintainers want the issue closed automatically when PR 1
merges:

```markdown
Closes #ISSUE_NUMBER
```

## Suggested Issue Comment After PR Opens

```markdown
Tracking PR: #PR_NUMBER
```

## Order Of Operations

1. Refresh `origin/main` in the upstream AGT checkout.
2. Create a clean upstream PR branch from current `origin/main`.
3. Stage only the public PR 1 fixture files.
4. Run the fixture validation and final public scan.
5. Create or identify the issue.
6. Open the PR with `Refs #ISSUE_NUMBER` unless maintainers explicitly want
   auto-close semantics.
7. Comment on the issue with `Tracking PR: #PR_NUMBER`.
8. Confirm the PR body and issue comment link each other correctly.

## Final Check

Before posting the issue or PR body, scan the exact text to be submitted for:

```bash
rg -n "RUNBOOK|task id|owner:|local checkout|/Users/|private branch|coordination log|internal coordination|assistant|tooling reference" issue-body.md pr-body.md
```

The scan should return no output.

## Wording Guardrails

- Say "standalone prompt-injection evaluation fixture".
- Say "synthetic labelled corpus".
- Say "corpus-specific baseline".
- Say "no runtime behavior change".
- Do not say or imply "production detector", "default block", "real traffic",
  or "embedding runtime".
