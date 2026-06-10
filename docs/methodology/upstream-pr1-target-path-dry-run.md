# Upstream PR1 Target-Path Dry Run

Status: read-only upstream orientation
Date: 2026-06-10

This note records a read-only check of the current upstream AGT tree before PR 1
staging. It does not replace the final baseline rerun and does not edit the AGT
repository.

## Current Upstream Snapshot

| Item | Value |
|---|---|
| AGT `origin/main` observed | `730ffbb060c44362485b786c63aa08439c49d7e1` |
| Local AGT checkout state | local `main` behind `origin/main` by 2 commits; unrelated untracked local docs present |
| Detector file checked | `agent-governance-rust/agentmesh/src/prompt_injection.rs` |
| Detector SHA-256 at `origin/main` | `92ac1f855e03502886fffdfb8cf9eece8ce7c2bea268ecacb4ff6386cb345ab3` |
| Last detector-touching commit | `7c89582420b667fa93b3030180b618b7c208a02f` |

The latest upstream branch moved from the earlier preflight commit, but the Rust
prompt-injection detector blob still matches the experiment scorer snapshot.
The large rules-only metrics were not rerun in this dry run.

## Commands Used

```bash
git -C <local-agt-checkout> fetch origin main --prune
git -C <local-agt-checkout> rev-parse origin/main
git -C <local-agt-checkout> \
  show origin/main:agent-governance-rust/agentmesh/src/prompt_injection.rs \
  | shasum -a 256
git -C <local-agt-checkout> \
  ls-tree -r --name-only origin/main
```

## Existing Benchmark Conventions Observed

- AGT has a release/manual benchmark workflow at `.github/workflows/benchmarks.yml`.
- That workflow currently runs Python benchmarks from:
  - `agent-governance-python/agent-os/benchmarks/`;
  - `agent-governance-python/agent-sre/benchmarks/`.
- The main benchmark documentation is `docs/BENCHMARKS.md`.
- A small prompt-injection benchmark already exists at
  `agent-governance-python/agent-os/benchmarks/injection_benchmark.py`, but it
  exercises the Python Agent OS detector, not the Rust `agentmesh` detector.
- Rust prompt-injection code and tests live under:
  - `agent-governance-rust/agentmesh/src/prompt_injection.rs`;
  - `agent-governance-rust/agentmesh/tests/prompt_injection.rs`;
  - `agent-governance-rust/agentmesh/tests/prompt_defense_compat.rs`.
- No root-level `benchmarks/` directory was observed at current `origin/main`.
- No Rust `benches/` directory was observed under `agent-governance-rust/agentmesh/`.

## Path Options For PR 1

| Option | Shape | Pros | Cons |
|---|---|---|---|
| A | `benchmarks/prompt-injection/**` plus `docs/benchmarks/prompt-injection-evaluation.md` | Clean standalone fixture; keeps benchmark independent from runtime packages. | Introduces a new root-level benchmark directory convention. |
| B | `agent-governance-rust/agentmesh/benchmarks/prompt-injection/**` plus docs under `docs/` | Keeps the fixture close to the Rust detector being measured. | Introduces a new Rust-local benchmark convention. |
| C | `agent-governance-python/agent-os/benchmarks/prompt_injection_fixture/**` plus docs under `docs/` | Aligns with existing benchmark workflow and existing Python prompt-injection benchmark location. | Awkward for a Rust-detector baseline harness unless the fixture is treated as cross-language data. |

The current research manifest prefers Option A because PR 1 is a standalone
evaluation fixture, not a runtime package feature. Windows/native-semantics
review should explicitly approve Option A or redirect to Option B/C before the
upstream branch is staged.

## Recommended Staging Interpretation

Until maintainers or the Windows/native-semantics review say otherwise:

1. Keep PR 1 standalone and public-facing.
2. Use Option A as the default staging path.
3. Keep the Rust baseline harness inside the fixture package.
4. Rewrite the harness to import the in-repo AGT Rust crate instead of vendoring
   `prompt_injection.rs`.
5. Keep the large corpus out of the first PR unless maintainers accept the size.
6. Add docs that point from `docs/BENCHMARKS.md` or `docs/benchmarks/` to the
   fixture without presenting it as a production detector benchmark.

## Before Opening PR 1

- Create a clean worktree or branch from current `origin/main`.
- Do not use the dirty local `main` checkout for staging.
- Refresh the detector SHA and rerun the rules-only baseline if the detector
  file or corpus artifact changes.
- Run the final public scan from
  `docs/methodology/upstream-pr1-public-file-manifest.md`.
- Wait for the Linux reproducibility/no-overclaim gate and the
  Windows/native-semantics gate to pass.
