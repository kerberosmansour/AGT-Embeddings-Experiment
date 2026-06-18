# AGT Red Team Agent Traps OpenCRE — Handoff

## Recommended Next Skill

`/slo-plan agt-redteam-agent-traps-opencre`

## Primary Route

`promote_to_runbook`

## Runbook Seed

Title: AGT Red Team benchmark harness and Agent Traps scenario schema.

Architecture sketch:

```text
benchmarks/agent-redteam/
  schema/
  scenarios/
  fixtures/
  harness/
  controls/
  reporters/
  adapters/
```

Milestones:

1. M1 schema + validator.
2. M2 Agent Traps smoke suite.
3. M3 content fixture pack.
4. M4 mock browser/tool/memory/audit/A2A harness.
5. M5 control-linked reporter.
6. M6 Goose adapter dry-run.
7. M7 upstream-ready docs and PR boundaries.

## Secondary Routes

| Candidate | Route |
|---|---|
| OpenCRE-backed AGT-AC catalog | `/slo-research` |
| Corpus gap report | `/slo-ticket-plan` |
| Content Injection fixture pack | `/slo-ticket-plan` |
| Evidence-level scorecard | `/slo-ideate` |
| Goose adapter contract | `/slo-ticket-plan` after harness |

## Evidence

The authoritative Experiment Book is `docs/slo/experiments/agt-redteam-agent-traps-opencre/EXPERIMENT.md`; scratch evidence lives under `experiments/agt-redteam-agent-traps-opencre/`.
