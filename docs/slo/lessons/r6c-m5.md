# Lessons Learned — r6c Milestone 5 (reporting + closeout)

## What changed
- Aggregation-only milestone (no scoring; import manifest asserts head/gate2/
  buckets/fastembed/sklearn not loaded). Produced per-family / per-bypass
  end-to-end floors, hard-negative FP table, and the 9-line §2 verdict table.
- Wrote `docs/reports/round6-cascade-report.md`; updated README Evidence
  Snapshot (additive), CLAIMS-LEDGER (additive section), ARCHITECTURE.md,
  UPSTREAM-PR-PLAN.md (evidence pointer).

## Key result
- **No attack family at 0%** in the shipped (floor-arm) cascade config —
  round-4's tool_abuse (0%→37.7%) and prompt_leakage (0%→100%) are fixed.
  Per-family floor PASS.
- Cascade end-to-end (floor arm): recall 64.3% @ 0.87% hard FPR.
- Hard-negative adjacent-security FPs are small (9 across ~3200 rows:
  docs_code_comment 7, owasp_ncsc_guidance 2) — recorded, not hidden.

## Honest "success" framing for the report
- 4 accept/pass + 1 partial + 4 not-met. The cascade's grand claims (head>kNN,
  gate independence, 80%@1%) fail; the component that mattered (Gate 0) and
  generalization (LOFO) and routing (M3) succeed; every §2 question got a clean
  measured answer. Negative results are reported with equal prominence.

## Method caveat carried from M4
- fp-side overlap (83) is a structural artifact of the empty flag lane; the
  report headlines the miss-side ratio (2.76) as the meaningful independence
  number and states the artifact explicitly.

## Closeout
- Full suite 48 tests green; validator all PASS; existing round-4/governance
  artifacts byte-identical; caches/venv git-ignored; no vectors or raw text in
  any committed artifact.
