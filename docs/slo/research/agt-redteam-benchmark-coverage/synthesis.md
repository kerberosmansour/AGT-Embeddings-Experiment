# Synthesis — AGT Red Team Benchmark Coverage Expansion

The current 24-scenario benchmark is a good smoke suite because it proves the schema, harness, scorecard, hygiene gate, OpenCRE validator, product renderer, and live-sandbox path all work end to end; it is not a strong measurement corpus because four rows per trap class cannot support stable catch-rate or false-positive claims, so the design must handle separate smoke and measurement suites because the repo-local scenario inventory is balanced but intentionally small.

The measurement suite should add negative examples as first-class rows, not as afterthoughts: four hard-benign and four near-miss rows per trap class gives every class a false-positive denominator while keeping the suite reviewable, so the design must handle `positive | hard_benign | near_miss` labels because the current schema and reports primarily exercise trap-positive rows.

A 120-row target is the Goldilocks expansion: 72 trap-positive rows, 24 hard-benign rows, and 24 near-miss rows across six trap classes; this is large enough for directional catch-rate / false-positive reporting and small enough to keep raw-free review discipline, so the design must handle class-balanced measurement without growing the CI smoke path because the current 24-row suite already serves the fast reproducibility role.

The benchmark should report catch rate and false-positive rate by trap class and by AGT-AC control, not just a single aggregate score; a single score would hide whether a control fails on memory, A2A, approval, or hidden-content traps, so the design must handle per-class and per-control metrics because the current control catalog covers 15 AGT-AC controls with uneven scenario counts.

The OpenCRE mapping layer should remain candidate-honest while coverage expands: unverified mappings must stay `candidate` until backed by committed OpenCRE references, so the design must handle mapping confidence separately from benchmark performance because `docs/slo/research/agtrt-opencre-relations.md` says every current relation is effectively candidate.

Live L3 should be sampled, not applied blindly to every row: the M6 path proves real-agent assessment can be safe, but each live run has cost, sandbox, and key-management overhead, so the design must handle L3 as a representative escalation layer because `docs/slo/completion/agtrt-m6.md` records one successful live trace, not a broad live study.

The next SLO work should be a focused follow-up runbook or ticket series for an AGT Red Team Measurement Suite v2: add outcome labels, author the 120-row suite, extend scorecard metrics, and gate hard-benign false positives, so the design must handle expansion as a measured second phase because the completed runbook explicitly shipped an instrument, not an exhaustive study.
