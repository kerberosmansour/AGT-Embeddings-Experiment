# Completion Summary - agtrt-v2 Milestone 5

## Goal completed
- Linux and Mac reruns were coordinated through AgentBus and produced a clear readout.

## Runtime evidence
- Linux 24-row live slice: total 24, completed 24, L3 trace rows 0, no-trace rows 24, status counts `not_run:24`.
- Linux sandbox controls passed: egress deny, metadata deny, scrubbed environment, and no host home mount.
- Mac deterministic cross-check passed: 240 rows validate, L2 scorecard controls 15, failures 0.
- Mac live attempt failed closed as expected because `bwrap` is unavailable on Mac.

## Result
- The v2 suite is useful and comprehensive for L2 labelled measurement.
- It is not yet a meaningful L3 live benchmark until non-secret adversarial live probes replace placeholder `agent_visible` content.
