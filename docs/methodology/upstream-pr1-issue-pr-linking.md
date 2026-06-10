# Upstream PR1 Issue And PR Linking

Status: pre-open checklist; PR1 staged locally; peer delta ACKs complete
Date: 2026-06-10

This note prepares the issue/PR cross-linking step for the future upstream AGT
PR 1. It is not itself upstream content. Use it only after the PR 1 review
gates pass and the baseline pin has been refreshed against current upstream
`main`.

## Current Staging State

The AGT PR1 fixture has been staged as a local commit only:

| Item | Value |
|---|---|
| Staging worktree | `agent-governance-toolkit-pr1-evaluation-fixture` |
| Branch | `pr1/prompt-injection-evaluation-fixture` |
| Local commit | `df898735 Add prompt-injection evaluation fixture` |
| Base commit | `730ffbb060c44362485b786c63aa08439c49d7e1` |

No upstream issue, upstream PR, or AGT branch push has been performed yet.

## Preconditions

- Reproducibility/no-overclaim review has passed.
- Target-path/native-semantics review has passed.
- The staged upstream branch contains only the public fixture package.
- The smoke baseline table has been refreshed if upstream `main` moved or the
  fixture was regenerated.
- The final public scan is clean.
- The final readback AgentBus tasks have passed or their caveats are recorded:
  - Linux reproducibility/no-overclaim readback:
    `t_mq7t9c5g_596_f69cf150`;
  - Windows path/native-semantics readback:
    `t_mq7t9c7j_671_b4a9d3b6`.
- The post-amend delta readbacks have also passed or their caveats are recorded:
  - Linux delta ACK:
    `t_mq7vvaj8_164_5e665234`;
  - Windows delta ACK:
    `t_mq7vvaky_226_4175f6c1`.

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

1. Confirm the recorded readback caveats remain acceptable for publication.
2. Refresh `origin/main` in the upstream AGT checkout.
3. If `origin/main` moved, rebase or recreate the PR branch from current
   `origin/main` and rerun the smoke fixture.
4. Confirm the branch still contains only the public PR 1 fixture files.
5. Run the fixture validation and final public scan.
6. Create or identify the issue.
7. Push the AGT fixture branch only after human approval to publish.
8. Open the PR with `Refs #ISSUE_NUMBER` unless maintainers explicitly want
   auto-close semantics.
9. Comment on the issue with `Tracking PR: #PR_NUMBER`.
10. Confirm the PR body and issue comment link each other correctly.

## Final Check

Before posting the issue or PR body, scan the exact text to be submitted for:

```bash
rg -n "RUNBOOK|task id|owner:|local checkout|/Users/|private branch|coordination log|internal coordination|Codex|Claude|AgentBus|SunLit" \
  issue-body.md pr-body.md
```

The scan should return no output.

## Wording Guardrails

- Say "standalone prompt-injection evaluation fixture".
- Say "synthetic labelled corpus".
- Say "corpus-specific baseline".
- Say "no runtime behavior change".
- Do not say or imply "production detector", "default block", "real traffic",
  or "embedding runtime".
