# RUNBOOK: AGT Embeddings Migration

Date: 2026-06-09
Owner: mac-agent
Branch: `slo/agt-embeddings-migration-plan`
AgentBus task: `t_mq71r9f5_617_538deaeb`
Status: M4 in progress; M0-M3 migrated and audited; Linux public-scope gate PASS; Windows AGT semantics gate pending

## Phase Contract

| Field | Value |
|---|---|
| SLO phase | `/slo-plan` migration planning |
| Mode | AGT-only extraction plan |
| Target repo | `AGT-Embeddings-Experiment` |
| Source repo | `Embedding_Experiment` |
| Primary output | README, claims ledger, migration runbook, AgentBus work split |
| Boundary | no unrelated research tracks, no raw secrets, no production/certification claim |

## Narrative Goal

Make it possible for a reviewer to read the repository and verify this story:

1. AGT rules-only detection is weak on a hard prompt-injection corpus.
2. Embedding + nearest-neighbour scoring provides a stronger semantic signal.
3. Youden's J gives a useful dial for recall/FPR tradeoff.
4. The conservative zero-FP operating point is suitable as a high-confidence
   routing signal.
5. The embedding signal should be optional, default-off, and additive to AGT
   policy/governance rather than a replacement.

## Migration Red Lines

- Do not migrate unrelated product or data-classification material.
- Do not migrate raw secrets, live credentials, customer data, local virtualenvs,
  model caches, or build output.
- Do not publish production safety, certification, or benchmark-coverage
  language.
- Do not describe synthetic/generated rows as real traffic.
- Do not claim the Youden's J point is a default block threshold.

## Target Repository Shape

```text
README.md
docs/
  CLAIMS-LEDGER.md
  RUNBOOK-agt-embeddings-migration.md
  AGENTBUS-WORKSPLIT.md
  methodology/
  reports/
corpus/
  round4/
meta/
  harness/
tools/
  agt-rules-baseline/
artifacts/
  embedding-sweep/
  governance-eval/
```

## Milestones

| Milestone | Owner | Output | Exit Gate |
|---|---|---|---|
| M0 Scope and claims ledger | Mac | README, claims ledger, runbook, work split | No banned terms/material; AgentBus tasks posted. |
| M1 AGT corpus and rules baseline migration | Mac primary, Linux audit | `corpus/round4/` AGT-only files and Rust baseline runner | Re-run corpus checker and rules baseline; Linux confirms no unrelated material. |
| M2 Embedding/kNN evidence migration | Mac primary, Linux audit | embedding sweep harness, freeze records, metrics, Youden artifact | Validator passes; Linux recomputes headline numbers. |
| M3 Governance/value-add evidence migration | Win primary, Mac support, Linux audit | AGT arms and value-add report gate | Native AGT vocabulary preserved; value-add report validator passes. |
| M4 Narrative packaging and review | Linux public-scope review, Windows AGT semantics readback, Mac coordination | issue narrative, method docs, reproduction guide | Narrative matches claims ledger; no overclaim language. |

## M0 Contract

| Field | Value |
|---|---|
| Goal | Establish the migration plan and claim/evidence map. |
| Files allowed | `README.md`, `.gitignore`, `docs/**` |
| Files forbidden | corpus/data/artifact bulk files |
| New dependencies | none |
| Data classification | Public metadata and planning text only |
| AI tolerance contract | No generated model output is evaluated in M0 |
| Measurement deliverables | Claim ledger maps each narrative number to source evidence |
| Abuse scenario | A migration accidentally imports unrelated material or turns research evidence into a production claim |

## M0 BDD

| ID | Given | When | Then |
|---|---|---|
| `m0_claims_are_mapped` | the narrative contains metric claims | a reviewer opens `docs/CLAIMS-LEDGER.md` | each metric points to a source artifact or a named evidence gap |
| `m0_scope_is_agt_only` | source repo contains unrelated work | target repo docs are scanned | only AGT prompt-injection material is referenced |
| `m0_no_production_claim` | embedding metrics look strong | README and ledger are reviewed | default-off and no-production wording remains visible |
| `m0_agentbus_split_exists` | multiple agents will migrate work | AgentBus tasks are read | Mac/Linux/Windows lanes are explicit, with coworker retirement covered by active-agent replacement gates |

## Verification Commands

```bash
python3 - <<'PY'
from pathlib import Path
for path in ["README.md", "docs/CLAIMS-LEDGER.md", "docs/RUNBOOK-agt-embeddings-migration.md"]:
    assert Path(path).exists(), path
PY
```

Scope-cleanliness scans must be run locally before this branch is merged. Keep
the forbidden-term list in the AgentBus task, not in this repository.

## Next Step

M3 is migrated and audited as research-only governance/value-add evidence.
Linux has passed the replacement public-scope/no-overclaim gate. The remaining
M4 gate is Windows AGT semantics/native-vocabulary readback before any final
narrative packaging lands.
