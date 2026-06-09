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

Branch: `slo/agt-embeddings-migration-plan`

Latest M2 evidence commit: `834da55`

| Task | Status |
|---|---|
| `t_mq71r9f5_617_538deaeb` | Mac M0 planning complete. |
| `t_mq71v5mw_336_e47046cc` | Linux M0 audit complete. |
| `t_mq71v5ox_409_a5bdb2d8` | Windows M0 AGT semantics readback complete. |
| `t_mq71v5tr_583_709fa2d1` | Coworker M0 narrative/no-overclaim review complete. |
| `t_mq71v5yi_754_f5fe9b34` | Mac M1 corpus/rules-baseline migration complete at `ab553ad`. |
| `t_mq72y2lp_989_ab02723f` | Linux M1 audit PASS; led to provenance hardening at `c85abd1`. |
| `t_mq72ny6x_713_44a17c25` | Windows M1 readback found moving sibling-checkout reproducibility drift. |
| `t_mq733glf_403_77a96c7a` | Mac vendored AGT detector source fix complete at `25f8d06`. |
| `t_mq73coxn_115_37c7fbae` | Linux vendored-source readback PASS. |
| `t_mq73cowb_67_a8cdaba8` | Windows vendored-source readback PASS. |
| `t_mq73kl0b_275_d516d4a6` | Mac M2 embedding/kNN evidence migration complete at `834da55`. |
| `t_mq73npxm_626_160bb634` | Linux M2 audit PASS at branch head `1612f83`. |
| `t_mq740luk_860_aaa9f8b3` | Mac companion claims/work-split refresh complete. |
| `t_mq74ar60_312_af4f2e02` | Mac post-audit docs status flip complete. |
| `t_mq73yofr_903_4c4745ba` | Windows formal M2 readback unblocked by Linux M2 audit. |
| `t_mq73t4ms_956_577bd965` | Coworker public-scope/no-overclaim gate unblocked by M2 migration. |
| `t_mq723syj_811_2288a4fe` | Open-source readiness policy task remains separate from migration evidence. |

M2 scope is intentionally limited to embedding/kNN artifacts, validator harness,
and reports. AGT policy/value-add artifacts remain M3.
