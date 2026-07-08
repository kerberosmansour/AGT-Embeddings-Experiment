---
name: agt-redteam-benchmark-consolidation
researched: 2026-07-08
incomplete: false
---

# Research Dossier - AGT Red Team Benchmark Consolidation

## Market

The immediate user is an engineer or security reviewer evaluating an AI agent
before shipping or upstreaming safety claims. The market proxy is the active
open-source benchmark ecosystem around agent prompt injection, LLM red-team
scanning, jailbreak robustness, and AI security governance: AgentDojo, garak,
PINT, PyRIT, JailbreakBench, and CyberSecEval all publish frameworks or
benchmarks for pieces of the problem (sources S1-S9). The gap this repo can own
is narrower and sharper: a benchmark that reports detector outcomes and
sandboxed action outcomes together, with evidence levels and no certification
claim (sources R4-R9, R13-R14).

## Direct competitors

| Name | Price | Key feature | Gap vs our wedge |
|---|---|---|---|
| AgentDojo | Free/open-source MIT project; live model/API costs depend on the runner (S1). | Dynamic environments for evaluating prompt-injection attacks and defenses against LLM agents, with benchmark scripts and published result inspection (S1, S2). | Strong live-agent environment, but it does not make this repo's 44.8k corpus a detector-layer payload dimension or report AGT-specific evidence levels. |
| Lakera PINT Benchmark | Free/open-source MIT benchmark repo (S5). | Neutral prompt-injection detector benchmark with hard negatives, multilingual attacks, benchmark scores, and custom detector hooks (S5). | Strong detector benchmark, but indirect detection and action containment are outside its primary scope; it does not report `detected -> executed` or `undetected -> contained`. |
| NVIDIA garak | Open-source scanner; run costs depend on selected model/provider (S3, S4). | Red-team scanner probing hallucination, leakage, prompt injection, misinformation, toxicity, jailbreaks, and more (S3). | Broad scanner/probe framework, but not a versioned AGT scenario artifact joining corpus manifests, scenario-set hashes, and action traces. |
| Microsoft PyRIT | Free/open-source MIT framework; run costs depend on targets/providers (S6). | Extensible framework for proactive risk identification in generative AI systems (S6). | Useful orchestration framework, but not a benchmark release format with frozen corpus/scenario hashes and stratified L1/L3 evidence. |
| JailbreakBench | Open benchmark artifacts and framework; run costs depend on evaluated models (S7). | Reproducible jailbreak evaluation with threat model, scoring functions, artifacts, and leaderboard (S7). | Strong reproducibility model for jailbreaks, but it is model-output-focused rather than AGT action-containment-focused. |

## Adjacent tools

| Name | Why adjacent, not direct | Can they pivot into us? |
|---|---|---|
| Meta PurpleLlama / CyberSecEval | Covers LLM security benchmarks including prompt injection, code interpreter, vulnerability exploitation, phishing, autonomous offensive cyber operations, and defensive capabilities (S8, S9). | Yes, at suite level, but its breadth means the AGT-specific detector/action joint matrix remains a distinct local wedge. |
| OWASP Top 10 for LLM Applications | Governance taxonomy for LLM application risks, including prompt injection, insecure output handling, excessive agency, and sensitive information disclosure (S10). | No; it supplies risk categories, not an executable benchmark. |
| OWASP Agentic Security Initiative / Agentic Top 10 | Governance and threat-model framing for autonomous agents and multi-step workflows (S11-S13). | No; it supplies standards vocabulary and risk framing, not corpus/scenario execution machinery. |
| NIST AI RMF / GenAI Profile | Voluntary risk-management framing for generative AI, with GenAI-specific profile released July 26, 2024 (S14). | No; it supplies governance language and risk-management expectations, not benchmark implementation. |

## Technical prior art

- AgentDojo: prior art for dynamic, environment-backed agent attack evaluation
  with utility/security tension (S1, S2).
- PINT: prior art for detector benchmarks with hard negatives, multilingual
  coverage, and third-party detector hooks (S5).
- JailbreakBench: prior art for reproducible open benchmark artifacts, threat
  model, scoring functions, and leaderboard methodology (S7).
- CyberSecEval 4: prior art for multi-domain AI cybersecurity benchmark suites,
  including prompt injection, code interpreter, autonomous offensive cyber, and
  defensive capability tests (S9).
- Repo-local Agent Traps harness: existing scenario schema, evidence ladder,
  scorecard, raw-free hygiene gate, and optional live adapter under
  `benchmarks/agent-redteam/` (R4-R9).
- Repo-local round-7 measurement harness: existing normalizer x corpus 2x2
  measurement and stepwise control analysis (R10-R16).

## Regulatory / legal

- **License/provenance**: payload-derived reality-check rows are committed only
  when source license is Apache-2.0 or MIT and summaries remain aggregate-only;
  ticket #17 validates 2,213 rows, 10 files, 0 errors, and `public_safe: true`
  (R12, R17).
- **Certification language**: repo claims must say synthetic research corpus,
  optional/default-off signal, review/routing signal, not validated on real
  traffic, and not production safety evidence until separate evidence exists
  (R3).
- **Governance framing**: OWASP LLM and agentic guidance plus NIST AI RMF are
  relevant references for risk taxonomy and non-certification language, but they
  do not convert benchmark results into compliance evidence (S10-S14).
- **Raw payload handling**: committed/public outputs must be metadata-only or
  aggregate-only. Generated reports must not include raw `text`, `prompt`,
  `content`, normalized text, live URLs, emails, credentials, or PII (R2, R3,
  R11-R12).

## Open questions that research did not answer

- The exact production-representative L3 sampling cost is not known until the
  one-family slice measures live adapter latency and per-scenario cost.
- The authoritative Agent Traps taxonomy source should be pinned if the project
  intends to claim parity with a specific paper version; this runbook can still
  proceed because the repo already has a trap-class enum and scenario coverage.
- The full L3 per-stratum sample size may need to vary by family cost, but the
  runbook can set a minimum: `n >= 30` per active stratum because 0 failures in
  30 trials puts the one-sided 95% upper bound near 10%.
