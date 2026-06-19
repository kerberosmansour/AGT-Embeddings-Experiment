# Lessons — agtrt M3

- **Append a sibling JOB, not a step.** `readiness.yml` is one `public-repo-readiness` job with many steps. "Append-only" is cleanest as a new top-level job (`agt-redteam-smoke`) — it cannot reorder or modify the existing steps, and the diff is unambiguously additive.
- **Portable smoke = `python` fallback + bash array (DW-004).** A bare `python3 .../*.json` CLI glob is the Win-audit Finding 2 footgun (shell-dependent). `PY=${PYTHON:-python3}; command -v "$PY" || PY=python` plus `scenarios=("$DIR"/*.json); "$PY" validator "${scenarios[@]}"` works under Linux CI and Git-Bash.
- **Fail-fast is testable via an env override.** `AGTRT_SCENARIOS` lets the test point the smoke at a temp dir with one malformed scenario and assert it exits non-zero BEFORE the harness step — a real fail-fast proof, not just a `set -euo pipefail` static check.
- **My gh token HAS `workflow` scope on this repo**, so I could append the CI workflow directly (unlike the sunlit-guardian `.github` SCA lane where I lack it and hand diffs to win).
- **Same-machine agent collision avoided:** a Codex instance also posting as linux-agent opened an M3 task; the operator told it to stand down since Claude Code owns this lane. Watch for duplicate task claims when two local agents share an identity.
