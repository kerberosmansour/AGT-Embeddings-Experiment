---
name: agt-redteam-benchmark-consolidation
researched: 2026-07-08
---

# Research Synthesis - AGT Red Team Benchmark Consolidation

AgentDojo and CyberSecEval show that agent benchmarks need executable
environments, not just static prompt labels; PINT and this repo's round-4/round-7
corpus show that detector benchmarks need broad, leakage-checked negative and
attack distributions; the design must handle both static detector breadth and
live action evidence because S1, S5, S9, R1, R4, and R15.

The repo already has the two halves of the desired benchmark: `corpus/round4/`
and round-7 harnesses provide frozen corpus/scoring discipline, while
`benchmarks/agent-redteam/` provides scenario validation, L2/L3 evidence levels,
scorecard reporting, hygiene, and optional live adapter seams; the design must
handle a bridge layer rather than a rewrite because R4-R16.

The direct competitors each optimize one layer: PINT scores detector decisions,
garak/PyRIT orchestrate red-team probes, AgentDojo runs live agent tasks, and
JailbreakBench hardens reproducibility; the design must handle joint
`detection verdict x action outcome` reporting because S1-S7.

Round-7 repo evidence shows that old detector/control narratives do not survive
harder benigns and new agentic families: Rec B pilot evidence has materially
high false positives, and the stepwise ceiling points to structural controls
such as tool-output authority, output leakage scanning, package provenance, and
terminal parsing; the design must handle false-positive utility and route-level
containment because R13 and R14.

The attached proposal's two-tier design is the right cost boundary: full corpus
at L1 static, stratified sample at L3 live, and benign utility arm at action
level; the design must handle evidence-level separation as a hard invariant
because R3, R6, R8, R11, and R12.

External governance sources do not make benchmark results compliance evidence,
but they do supply risk vocabulary for prompt injection, excessive agency,
insecure output, agentic workflows, and risk management; the design must handle
non-certification language and standards mapping as report metadata because
S10-S14 and R3.

The first implementation wedge should not attempt all 44.8k rows at L3. It
should prove indirect injection end-to-end with two or three templates, a fixed
payload sample, corpus/scenario hashes, L1 detector results, L3 sandbox traces,
and a joint scorecard; the design must handle a one-family slice before scale
because the proposal, R9, R11, and R14.
