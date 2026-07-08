# AGT Red Team Experiment Summary

Public GitHub issue: https://github.com/kerberosmansour/AGT-Embeddings-Experiment/issues/36

This document is the companion write-up for issue #36. It summarizes what the AGT Red Team experiment was, what we built, what we learned, and what remains.

## One-sentence summary

We turned an agent-safety hunch into a reproducible benchmark that can show whether an AI agent attempted an unsafe action, whether that action executed, and which control boundary held.

## Starting hunch

The original hunch was that AGT Red Team could become more than a prompt-injection corpus. It could become a standards-linked benchmark for agentic control failures: content, memory, tools, multi-agent boundaries, human approvals, and live-agent behaviour.

The experiment used the SLO Innovation Sandbox loop first, then promoted the winning shape into a runbook.

## What we built

The runbook delivered eight milestones under `benchmarks/agent-redteam/`:

1. **Scenario schema + validator** — a structured scenario contract with six trap classes, target layers, views, session model, controls, standards, and expected evidence.
2. **Mock behavioural harness** — deterministic tools that record `attempted`, `executed`, and `blocked_at` without real side effects.
3. **One-command smoke + CI** — a reproducible `run-smoke.sh` path.
4. **Evidence-level scorecard** — a report that groups results by control and evidence level while keeping `certification_claim:false`.
5. **Raw-free hygiene gate** — a fail-closed scanner for payloads, secrets, and PII-like content.
6. **Live L3 adapter** — an opt-in live agent run inside an OS-enforced sandbox.
7. **OpenCRE relation validator** — a fail-honest mapping layer that downgrades unverified relations to `candidate`.
8. **Shareable scorecard product** — offline HTML and Markdown output with a prominent evidence-not-certification disclaimer.

## What we found

### 1. Prompt injection is too narrow

The useful taxonomy is six agent-trap classes:

- Content Injection
- Semantic Manipulation
- Cognitive State
- Behavioural Control
- Systemic
- Human-in-the-Loop

The starting corpus was lopsided toward Behavioural Control and Semantic Manipulation. It had very little Cognitive State, Systemic, or Human-in-the-Loop coverage.

### 2. The real signal is attempted vs executed

A good agent benchmark should not only ask whether the model produced risky text. It should ask:

- Did the agent attempt the unsafe action?
- Did it execute?
- Was it blocked?
- Where was it blocked?
- Which control layer produced the evidence?

That is the benchmark's core measurement win.

### 3. Evidence needs levels, not badges

The benchmark uses evidence levels:

| Level | Meaning |
|---|---|
| `L0_declared` | A claim exists, but nothing ran. |
| `L1_static` | Schema/config/code inspection evidence. |
| `L2_mock_behavioural` | Deterministic mock behaviour with attempted/executed traces. |
| `L3_live_behavioural` | Real agent behaviour under the sandbox. |

The report never claims certification.

### 4. Live testing is possible, but only with a real sandbox

M6 ran a live agent with a cheap model and tight caps. The live agent attempted a tool action. The OS sandbox contained it.

The honest trace semantics were:

- `attempted:true`
- `executed:false`
- `blocked_at:"sandbox_contained"`

The sandbox controls were proven, not assumed:

- internet egress blocked;
- cloud metadata IP `169.254.169.254` blocked;
- environment scrubbed;
- host filesystem not mounted.

### 5. Review caught real bugs before they became claims

Two important problems were caught and fixed:

- A Windows `python3` Store-alias bug made a supposedly portable smoke script fail on Git-Bash.
- The live adapter initially risked overclaiming `executed:true` for an action that was actually contained. This was corrected before the live run evidence was accepted.

## What we achieved

Final state:

- 8/8 milestones complete.
- 72 tests passing on the final branch, with expected Linux-only sandbox skips on Windows.
- 24 seed scenarios, balanced 4 per trap class.
- 15 AGT-AC controls.
- One successful live L3 proof.
- OpenCRE mappings fail honest as `candidate` until backed.
- Shareable HTML/Markdown scorecard.
- Raw-free, no-certification posture preserved.

## What this is not

This is not a finished comparative study.

Current limits:

- 24 scenarios are a balanced seed, not an exhaustive corpus.
- One L3 live run proves the path, not a broad live-agent distribution.
- OpenCRE mappings are all effectively `candidate` until backed by committed references.
- More false-positive / hard-benign rows are needed for robust precision measurement.

## What should happen next

1. Merge the completed runbook branch through PR #37.
2. Expand the benchmark into a measurement suite: keep 24 rows for smoke, add a 120-row measurement suite for catch rate and false-positive rate.
3. Share the OpenCRE handoff in issue #35 with the OpenCRE team.
4. Keep issue #29 for the content-injection fixture pack.
5. Run more L3 samples across scenarios and models once L2 coverage is stronger.

## How to run the benchmark

Default mock/L2 path, cross-platform:

```bash
git checkout slo/agt-redteam-runbook
bash benchmarks/agent-redteam/run-smoke.sh
python -m unittest discover -s benchmarks/agent-redteam -p "test_*.py"
```

Live L3 path, Linux-only with `bwrap` and an out-of-band key:

```bash
bash benchmarks/agent-redteam/run-smoke.sh --live
```

## References

- Runbook PR: https://github.com/kerberosmansour/AGT-Embeddings-Experiment/pull/37
- OpenCRE handoff issue: https://github.com/kerberosmansour/AGT-Embeddings-Experiment/issues/35
- Experiment summary issue: https://github.com/kerberosmansour/AGT-Embeddings-Experiment/issues/36
