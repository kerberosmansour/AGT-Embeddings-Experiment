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

M0 planning is in progress on branch `slo/agt-embeddings-migration-plan`.
