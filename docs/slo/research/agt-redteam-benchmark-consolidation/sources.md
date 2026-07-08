---
name: agt-redteam-benchmark-consolidation
researched: 2026-07-08
---

# Sources - AGT Red Team Benchmark Consolidation

## External sources

| ID | Source | URL | Retrieved | Tier | Claim status | Used for |
|---|---|---|---|---:|---|---|
| S1 | AgentDojo GitHub README | https://github.com/ethz-spylab/agentdojo | 2026-07-08 | 2 | verified | Dynamic agent benchmark, MIT license, run/results surface. |
| S2 | AgentDojo OpenReview / NeurIPS listing via README | https://openreview.net/forum?id=m1YYAQjO3w | 2026-07-08 | 4 | verified | Prior art: environment for prompt-injection attacks and defenses. |
| S3 | NVIDIA garak GitHub README | https://github.com/NVIDIA/garak | 2026-07-08 | 2 | verified | Red-team scanner coverage: hallucination, leakage, injection, jailbreaks, etc. |
| S4 | garak website | https://garak.ai/ | 2026-07-08 | 2 | verified | garak is open-source and actively updated. |
| S5 | Lakera PINT Benchmark GitHub README | https://github.com/lakeraai/pint-benchmark | 2026-07-08 | 2 | verified | Prompt-injection detector benchmark, MIT license, hard negatives, multilingual coverage. |
| S6 | Microsoft PyRIT GitHub README | https://github.com/microsoft/PyRIT | 2026-07-08 | 2 | verified | Open-source AI red-team framework, MIT license. |
| S7 | JailbreakBench NeurIPS 2024 abstract | https://proceedings.neurips.cc/paper_files/paper/2024/hash/63092d79154adebd7305dfd498cbff70-Abstract-Datasets_and_Benchmarks_Track.html | 2026-07-08 | 4 | verified | Reproducibility, threat model, scoring framework, leaderboard. |
| S8 | Meta PurpleLlama GitHub README | https://github.com/meta-llama/PurpleLlama | 2026-07-08 | 2 | verified | CyberSecEval/PurpleLlama scope and benchmark licensing. |
| S9 | CyberSecEval 4 documentation | https://meta-llama.github.io/PurpleLlama/CyberSecEval/docs/intro | 2026-07-08 | 1 | verified | CyberSecEval 4 prompt injection, code interpreter, autonomous offensive cyber, and defensive benchmarks. |
| S10 | OWASP Top 10 for LLM Applications | https://owasp.org/www-project-top-10-for-large-language-model-applications/ | 2026-07-08 | 3 | verified | Prompt injection, excessive agency, insecure output, and LLM risk categories. |
| S11 | OWASP Agentic Security Initiative | https://genai.owasp.org/initiatives/agentic-security-initiative/ | 2026-07-08 | 3 | verified | Agentic security scope: autonomous agents and multi-step workflows. |
| S12 | OWASP Top 10 for Agentic Applications 2026 | https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/ | 2026-07-08 | 3 | verified | Agentic risk governance reference and operational framing. |
| S13 | OWASP Agentic AI Threats and Mitigations | https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/ | 2026-07-08 | 3 | verified | Threat-model-based agentic threats and mitigations. |
| S14 | NIST AI Risk Management Framework page | https://www.nist.gov/itl/ai-risk-management-framework | 2026-07-08 | 3 | verified | GenAI profile release and voluntary risk-management framing. |

## Repo-local sources

| ID | Source file | Claim status | Used for |
|---|---|---|---|
| R1 | `README.md` | verified | 44,800-row corpus, 17,600 attacks, 27,200 benigns, round-6/exp1 headline results and claim boundaries. |
| R2 | `docs/ARCHITECTURE.md` | verified | Current repo architecture, frozen-test discipline, metadata-only artifacts, baseline metrics. |
| R3 | `docs/CLAIMS-LEDGER.md` | verified | Wording guardrails and evidence gaps before stronger claims. |
| R4 | `docs/RUNBOOK-agt-redteam-agent-traps-opencre.md` | verified | Existing Agent Traps harness, evidence ladder, scenario schema, front-to-end outcome framing. |
| R5 | `benchmarks/agent-redteam/schema/scenario.schema.json` | verified | Existing scenario fields and trap-class enum. |
| R6 | `benchmarks/agent-redteam/schema/result.schema.json` | verified | Existing evidence-level enum. |
| R7 | `benchmarks/agent-redteam/harness/runner.py` | verified | Existing L2 mock behavioural trace generation. |
| R8 | `benchmarks/agent-redteam/reporters/scorecard.py` | verified | Existing scorecard, no-certification invariant, evidence-level reporting. |
| R9 | `benchmarks/agent-redteam/run-smoke.sh` | verified | Existing one-command validation, harness, scorecard, hygiene, optional live path. |
| R10 | `docs/RUNBOOK-round7-garak-corpus.md` | verified | Round-7 corpus, normalizer, and 2x2 measurement design. |
| R11 | `docs/slo/tickets/ticket-16-round7-ws-c-2x2-measurement.md` | verified | Round-7 2x2 harness contract and pilot evidence. |
| R12 | `docs/slo/tickets/ticket-17-reality-check-intake-validation.md` | verified | Reality-check intake gates, 2,213 row validation summary, Apache-2.0/MIT-only rule. |
| R13 | `docs/reports/round7-recb-control-analysis.md` | verified | Round-7 Rec B FP/catch findings and structural-control recommendations. |
| R14 | `docs/reports/round7-ceiling-stepwise-analysis.md` | verified | Stepwise ceiling results and implementation order. |
| R15 | `corpus/round4/manifest-large.json` | verified | Corpus counts, split counts, leakage/duplicate checks. |
| R16 | `artifacts/round7-garak/pilot-knn/manifest.json` | verified | Pilot 2x2 kNN measurement cells and headline status. |
| R17 | `scratch/round7-reality-check-summary.json` | verified | Reality-check intake aggregate counts and public-safe status. |

## Research gaps

- Direct pricing for scanner platforms is not needed for this runbook because
  the selected comparison set is open-source or benchmark-public; live model
  API costs remain run-dependent and must be recorded per L3 run.
- The Agent Traps taxonomy is present in the existing repo schema and proposal;
  this dossier uses OWASP ASI references as the external governance anchor
  rather than reusing secondary summaries of the paper.
