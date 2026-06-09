# AgentBus Work Split

This file mirrors the tasks posted on AgentBus for the AGT embeddings migration.

## Lanes

| Agent | Lane | Must Not Do |
|---|---|---|
| mac-agent | Own target repo plan, AGT-only source file allowlist, initial migration commits | bulk-copy unrelated material or start model work before audit |
| linux-agent | Audit migrated corpus/artifacts for reproducibility, leakage, and scope cleanliness | approve moving artifacts without rerunning validators |
| win-agent | Verify AGT Rust detector/policy vocabulary and Windows-path reproducibility | introduce non-native policy labels |
| coworker-agent | Review narrative clarity and no-overclaim wording | turn research metrics into deployment claims |

## Proposed AgentBus Tasks

| Task | Assignee | Output |
|---|---|---|
| M0 target-repo scope review | linux-agent | Confirm docs contain only AGT prompt-injection scope and no banned material. |
| M1 corpus/baseline migration | mac-agent | Copy AGT-only corpus/check/baseline files and rerun validation. |
| M1 corpus/baseline audit | linux-agent | Recompute row counts, leakage checks, rules-only metrics. |
| M2 embedding evidence migration | mac-agent | Copy embedding sweep artifacts, validator, and Youden J readout. |
| M2 embedding audit | linux-agent | Recompute Youden J and base-rate precision from migrated artifacts. |
| M3 AGT semantics readback | win-agent | Confirm rules and policy vocabulary line up with AGT. |
| M4 narrative review | coworker-agent | Confirm README/narrative follows claims ledger and no-claim language. |

## Current Status

M0 Mac planning is complete on branch `slo/agt-embeddings-migration-plan`
at commit `a30d190`.

| Task | Status |
|---|---|
| `t_mq71r9f5_617_538deaeb` | Mac M0 planning complete |
| `t_mq71v5mw_336_e47046cc` | Linux M0 audit claimed |
| `t_mq71v5ox_409_a5bdb2d8` | Windows M0 readback claimed |
| `t_mq71v5tr_583_709fa2d1` | Coworker M0 narrative review open |
| `t_mq71v5yi_754_f5fe9b34` | Mac M1 migration open, blocked by the three M0 reviews |

Mac posted AgentBus message `869` asking the review owners to complete or post
blockers. M1 must not start until the M0 review tasks are done.
