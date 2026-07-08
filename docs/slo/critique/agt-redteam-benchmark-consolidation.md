# /slo-critique - AGT Red Team Benchmark Consolidation

Target: `docs/RUNBOOK-agt-redteam-benchmark-consolidation.md`.
Reviewer: mac-agent, four-persona rotation.
Date: 2026-07-08.

Threat-model contract: **degraded mode**. No
`docs/slo/design/agt-redteam-benchmark-consolidation-threat-model.slo.json` and
no Markdown threat-model artifact exist for this slug. I used the inline
`tm-agtrtc-abuse-1..6` rows in the runbook only as degraded references and make
no abuse-ID-stability claim.

Design persona: **applicable** because M5 can emit static HTML/Markdown reports.

## Findings

| id | persona | category | runbook section | finding | concrete scenario | recommendation |
|----|---------|----------|-----------------|---------|-------------------|----------------|
| C-ENG-0 | Eng | auto-fix | section 5.5, section 10 | Mechanical Markdown fixes applied: the Kani note used one inline-code span across nested backticks, and the final `/slo-critique` command was split across a line break. | A human or parser reads the Kani line as malformed inline code, then copies a broken next-step command from section 10. | Applied in `docs/RUNBOOK-agt-redteam-benchmark-consolidation.md`: made the Kani note plain prose and rendered the next-step command as one inline command. |
| C-CEO-1 | CEO | ask | section 5A rollout/review windows, M2, M3/M4 | The one-family M2 wedge is the first honest user-value proof, but the runbook calls it a "review window" rather than a hard stop/go gate before full-corpus scale and live sampling. | The assessing engineer runs M2, cannot use the joint report to decide whether the benchmark is actionable, and the team still spends the next cycle on M3 full-corpus artifacts and M4 live budget before discovering the report shape is wrong. | Add an explicit post-M2 checkpoint: M3 may start only after an assessing engineer can answer detector miss, containment miss, utility false block, and coverage backlog questions from the one-family report. Opportunity cost: this delays M3 by one feedback cycle, but prevents scaling the wrong report. |
| C-ENG-1 | Eng | ask | section 5B readiness, M2 contract | M2 claims it emits L3 rows, but section 5B says live adapter sandbox and model/API budget are blockers only for M4. That contradiction creates a fake-L3 path. | An implementer starts `/slo-execute M2` while budget/sandbox readiness is still blocked, uses mock traces to keep the smoke green, labels them `L3_live_behavioural`, and M5 later treats non-live evidence as live containment proof. | Before M2 execution, choose one contract and encode it in the readiness table, BDD, and failure bar: either M2 is explicitly L2/mock-only, or M2 is blocked on sandbox proof and a bounded live budget for its `<=30` calls. Do not allow a fallback that emits L3 without provider/model execution inside the OS sandbox. |
| C-ENG-2 | Eng | ask | M3 Failure Bar | M3 says hard-benign false-positive rate must not exceed "the pre-registered bar", but no numeric bar is registered in the runbook. | The L1 run finishes with hard-benign false positives; one maintainer picks a permissive threshold after reading results, another reports a stricter one, and both can claim compliance because the bar was never frozen. | Add a numeric M3 hard-benign FP bar before `/slo-execute M3`, for example `hard_benign_fp_wilson_upper <= 10%` or an explicit "no headline FP claim until a bar is frozen" rule. Add a BDD row that fails when the artifact lacks the bar or exceeds it. |
| C-SEC-1 | Security | ask | section 5B Threat Model Summary | **V17 Missing threat model**: the formal threat model is absent, so inline `tm-agtrtc-abuse-*` IDs are mitigations-only and not stable. Threat-model row: N/A because the frozen artifact is missing; degraded inline rows are at section 5B. Class status: residual process risk. | M4 adds a new sandbox-abuse row and renumbers the inline table; M5 tests still cite the old IDs, so a reviewer believes `tm-agtrtc-abuse-3` covers OS sandbox refusal when it now points to a different abuse case. | Before M1 or as an M1 deliverable, freeze the inline threat model into `docs/slo/design/agt-redteam-benchmark-consolidation-threat-model.md` or `.slo.json`, or explicitly add an M1 DoD that locks abuse IDs. Variant-analysis: N/A - planning artifact; `find docs/slo ... '*threat-model*' '*.slo.json'` returned no artifact for this slug. |
| C-SEC-2 | Security | ask | section 6 failure bar, section 5B Security Test Plan, M5 report gates | **V8 Data Protection / CWE-200 Information Exposure** under `tm-agtrtc-abuse-1`: the plan bans raw keys, live URLs, emails, secrets, and PII, but the current repo hygiene scanner only proves secret/PII-marker detection, not recursive forbidden-key or URL/email value detection. Class status: mitigated by metadata-only discipline, not eliminated. | A malicious payload contributor places raw prompt text under a permitted-looking `notes` or `agent_visible` field, or includes `https://live-target.example/...` in a generated JSON report. The scanner catches no AWS/OpenAI/GitHub/SSN marker, the M5 report passes, and raw attack material crosses the public/upstream boundary. | Add an M3/M5 raw-free validator that recursively parses JSON/JSONL/CSV/Markdown artifacts and rejects forbidden keys (`text`, `prompt`, `content`, `normalized_text`) plus URL/email patterns in string values, with planted BDD fixtures. Variant-analysis: ripgrep against `benchmarks/agent-redteam/hygiene/raw_free_scan.py` and `tests/test_hygiene.py` shows marker-only patterns today; no field-name or URL/email gate is present. |
| C-DES-1 | Design | ask | M4 outcome, M5 report/optional HTML | The report contract does not make skipped/unavailable L3 states first-class in the static report surface. Empty, partial, and budget-blocked states are a real UI/reporting surface here. | M4 records named skipped reasons because no live budget was approved; M5 renders the joint report without a visible "not run / skipped / unavailable" state, and a stakeholder reads missing L3 cells as zero failures or a clean run. | Add an M5 report requirement and BDD row for partial L3: every family/stratum must show `not_run`, `skipped`, or `unavailable` distinctly from `blocked`, `contained`, and `executed`; the no-certification banner must remain first-viewport content in HTML/Markdown. |

## Outcome-First Verdict

The runbook is structurally outcome-first: every milestone has a CLI/script
path, generated artifacts, and a cross-layer assertion from corpus/scenario
input to report row. I did not find outcome-test theatre.

The execution gate is conditional:

- M1 can proceed if the user accepts degraded threat-model mode, or if C-SEC-1
  is converted into an M1 deliverable.
- M2 should not proceed until C-ENG-1 is resolved, because fake L3 would poison
  the benchmark.
- M3 should not proceed until C-ENG-2 freezes the hard-benign FP bar.
- M5 should not be considered release-ready until C-SEC-2 and C-DES-1 are
  reflected in tests and report validation.

## Handoff

No high/critical security findings were emitted, so no expanded security
appendix is required. The auto-fix was documentation-only. All non-mechanical
findings are `ask` and wait for user acceptance or rejection before execution.
