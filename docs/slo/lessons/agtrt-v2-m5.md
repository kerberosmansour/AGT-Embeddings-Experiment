# Lessons Learned - agtrt-v2 Milestone 5

## What changed
- Linux and Mac ran the coordinated AgentBus verification for the 240-row suite.
- Mac found and fixed a Bash 3.2 portability bug in `run-measurement.sh`.

## Assumptions verified
- The deterministic 240-row L2 suite is stable on Windows, Linux, and Mac.
- Linux bwrap live execution reaches the provider and preserves sandbox honesty.
- The current v2 live leg is vacuous: placeholder `agent_visible` content does not induce any tool use.

## Assumptions still unresolved
- We do not yet know L3 catch rates for the six trap classes because the suite lacks non-secret adversarial live probes.

## Rules for the next milestone
- Add real, non-secret live probes per evasion family before spending a full 240-row L3 run.
- Keep L2 corpus labels and L3 live prompts separate so raw-free placeholders do not make live testing meaningless.
