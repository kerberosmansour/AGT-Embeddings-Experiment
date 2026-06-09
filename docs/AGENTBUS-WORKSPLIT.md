# AgentBus Work Split

This file mirrors the tasks posted on AgentBus for the AGT embeddings migration.

## Lanes

| Agent | Lane | Must Not Do |
|---|---|---|
| mac-agent | Own target repo plan, AGT-only source file allowlist, initial migration commits | bulk-copy unrelated material or start model work before audit |
| linux-agent | Audit migrated corpus/artifacts for reproducibility, leakage, scope cleanliness, and public no-overclaim wording | approve moving artifacts without rerunning validators |
| win-agent | Verify AGT Rust detector/policy vocabulary, Windows-path reproducibility, and native AGT semantics in public wording | introduce non-native policy labels |
| coworker-agent | Retired/unavailable as of post-M2 coordination | accept new blocking gates |

Coworker replacement rule: release-facing narrative/no-overclaim review is now
an active-agent split. Linux is the primary public-scope/no-overclaim reviewer;
Windows is the AGT semantics/native-vocabulary reviewer; Mac coordinates and
migrates artifacts, but does not self-approve release-facing claims it wrote.

## Proposed AgentBus Tasks

| Task | Assignee | Output |
|---|---|---|
| M0 target-repo scope review | linux-agent | Confirm docs contain only AGT prompt-injection scope and no banned material. |
| M1 corpus/baseline migration | mac-agent | Copy AGT-only corpus/check/baseline files and rerun validation. |
| M1 corpus/baseline audit | linux-agent | Recompute row counts, leakage checks, rules-only metrics. |
| M2 embedding evidence migration | mac-agent | Copy embedding sweep artifacts, validator, and Youden J readout. |
| M2 embedding audit | linux-agent | Recompute Youden J and base-rate precision from migrated artifacts. |
| M3 AGT semantics readback | win-agent | Confirm rules and policy vocabulary line up with AGT. |
| M4 narrative review | linux-agent primary, win-agent semantics readback | Confirm README/narrative follows claims ledger, no-claim language, and native AGT vocabulary. |

## Current Status

Branch: `slo/agt-embeddings-migration-plan`

Latest M2 evidence commit: `834da55`
Latest M3 evidence commit: `de5ade7`

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
| `t_mq73yofr_903_4c4745ba` | Windows formal M2 readback PASS. |
| `t_mq73t4ms_956_577bd965` | Historical coworker public-scope/no-overclaim gate completed before coworker retirement. |
| `msg 936` | Coworker replacement announced: Linux owns public no-overclaim review, Windows owns AGT semantics wording, Mac coordinates. |
| `t_mq74f8nx_613_be2ae943` | Windows M3 governance/value-add migration complete at `de5ade7`. |
| `t_mq74fnf1_733_021a4d90` | Linux M3 audit PASS at branch head `1fb73b2`. |
| `t_mq74hd8m_854_ce07671d` | Replacement public-scope/no-overclaim gate in progress for Linux after M3. |
| `t_mq74hd9q_894_2e0b4d5a` | Replacement AGT semantics/native-vocabulary gate open for Windows after M3. |
| `t_mq74i0rp_349_85a66332` | Mac coworker replacement docs update complete. |
| `t_mq74rcku_558_1ac8a184` | Mac runbook M4 ownership cleanup complete at `d42b661`. |
| `t_mq74ujpr_775_f09cbf2e` | Mac M3 source-map support complete at `0daeee5`; used as migration checklist for M3. |
| `t_mq723syj_811_2288a4fe` | Open-source readiness policy task remains separate from migration evidence. |

M2 scope is intentionally limited to embedding/kNN artifacts, validator harness,
and reports. M3 adds governance metadata/value-add evidence as research-only
readout and does not create a default-blocking or production-readiness claim.
The M3 source map lives at
`docs/methodology/m3-governance-value-add-source-map.md` and is a migration
checklist, not migrated evidence.
