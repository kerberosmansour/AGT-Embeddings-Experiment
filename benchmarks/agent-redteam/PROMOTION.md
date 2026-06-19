# AGT Red Team Benchmark — Promotion / PR Boundary

This benchmark is built to be contributed upstream **without a monolithic PR and without leaking raw content**. It produces **evidence, not a certification**.

## PR boundary sequence (each PR is independently reviewable)

1. **PR1 — Scenario schema + validator** (`schema/`, `scenarios/`). Raw-free fixtures; no runtime behaviour.
2. **PR2 — Mock red-team harness + trace schema** (`harness/`). Deterministic, side-effect-free; no live tools/providers.
3. **PR3 — Reproducible smoke + CI** (`run-smoke.sh`, readiness job). Append-only.
4. **PR4 — Control-linked evidence-level reporter** (`reporters/`, `controls/`). `certification_claim: false`.
5. **PR5 — Raw-free hygiene gate + this PROMOTION.md** (`hygiene/`).

## Deferred routes (filed as issues, NOT built into the core PRs)

- **DW-001 — content-injection fixture pack** → `/slo-ticket-plan` issue. **Risk to flag in that ticket (tm-agtrt-abuse-2):** a fixture/extractor can *hide* agent-visible content (render/parse divergence), producing false comfort — the fixtures work must assert the human-visible vs agent-visible channels independently so hidden content cannot pass unseen.

## Now built IN this benchmark (founder directive 2026-06-19, previously deferred)

- **M6 — live Goose adapter** (sandboxed L3). Real-agent assessment in an OS-enforced sandbox (egress-deny, scrubbed env, no host fs mount); opt-in `--live`; default path stays mock/L2.
- **M7 — OpenCRE relation research** + a fail-honest relation validator.
- **M8 — shareable scorecard product** (offline HTML+MD, raw-free, no certification).

## Safety posture (holds across every PR)

- **Raw-free**: no raw attack payload, secret, or PII in any committed/generated artifact — enforced by `hygiene/raw_free_scan.py` (fail-closed; anti-vacuity tested).
- **No certification**: every report carries `certification_claim: false`; evidence levels (L0–L3), never a badge/score.
- **No upstream PR is opened by this runbook** — it only files the deferred-route issues and prepares the boundary; a human opens the upstream PRs.
- **No edits to the experiment scratch** (`experiments/agt-redteam-agent-traps-opencre/**`) — read-only seed.
