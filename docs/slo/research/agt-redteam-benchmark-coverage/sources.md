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
- Founder-supplied pasted draft in the working session — OWASP Agentic Scorecard proposal, including AIVSS/ASI mapping, static-vs-behavioural gap analysis, three-tier execution architecture, and prior-art pointers. Treated as founder-supplied draft context, not as an externally verified standard.

## External sources

- OpenCRE public site: https://www.opencre.org/
- OWASP/OpenCRE GitHub repository: https://github.com/OWASP/OpenCRE
- Google Doc shared by founder: https://docs.google.com/document/d/1fuGZ0cVy4Li44fveFI-qOS8luviFqdQkLbHwxdLqzuI/edit?tab=t.0 — access attempted 2026-06-19; browser fetch only exposed the Google Docs shell, so the local pasted draft above is the source used.
- AgentDojo paper / NeurIPS abstract: https://proceedings.neurips.cc/paper_files/paper/2024/hash/97091a5177d8dc64b1da8bf3e1f6fb54-Abstract-Datasets_and_Benchmarks_Track.html
- AgentDojo arXiv abstract: https://arxiv.org/abs/2406.13352
- AgentThreatBench / inspect_evals docs: https://ukgovernmentbeis.github.io/inspect_evals/evals/safeguards/agent_threat_bench/
- Promptfoo OWASP Agentic AI docs: https://www.promptfoo.dev/docs/red-team/owasp-agentic-ai/

## Notes

This research is intentionally repo-local plus OpenCRE-source anchored. It is not a market/competitor dossier. The question is benchmark coverage design, not product positioning.
