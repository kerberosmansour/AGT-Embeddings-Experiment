# Sources — AGT Red Team Benchmark Coverage Expansion

Access date: 2026-06-19.

## Repo-local artifacts

- `benchmarks/agent-redteam/scenarios/*.json` — current 24 scenario seed, four scenarios per trap class.
- `benchmarks/agent-redteam/schema/scenario.schema.json` — six trap-class enum and scenario field contract.
- `benchmarks/agent-redteam/schema/result.schema.json` — evidence-level enum: `L0_declared`, `L1_static`, `L2_mock_behavioural`, `L3_live_behavioural`.
- `benchmarks/agent-redteam/controls/agt-ac.csv` — 15 AGT-AC controls and preliminary OpenCRE relation column.
- `benchmarks/agent-redteam/controls/opencre/relations.csv` — current OpenCRE relation candidates.
- `benchmarks/agent-redteam/controls/opencre/validate_relations.py` — fail-honest relation validator.
- `docs/RUNBOOK-agt-redteam-agent-traps-opencre.md` — completed 8-milestone runbook and milestone tracker.
- `docs/slo/completion/agtrt-m1.md` through `docs/slo/completion/agtrt-m8.md` — milestone completion evidence.
- `docs/slo/research/agtrt-opencre-relations.md` — M7 OpenCRE relation research result.
- `docs/slo/experiments/agt-redteam-agent-traps-opencre/EXPERIMENT.md` — original Innovation Sandbox experiment book.

## External sources

- OpenCRE public site: https://www.opencre.org/
- OWASP/OpenCRE GitHub repository: https://github.com/OWASP/OpenCRE

## Notes

This research is intentionally repo-local plus OpenCRE-source anchored. It is not a market/competitor dossier. The question is benchmark coverage design, not product positioning.
