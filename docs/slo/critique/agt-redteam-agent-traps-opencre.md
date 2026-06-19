# /slo-critique — AGT Red Team benchmark runbook (independent win-agent pass)

Target: `docs/RUNBOOK-agt-redteam-agent-traps-opencre.md` (8-milestone outcome-first runbook, branch `slo/agt-redteam-runbook` @f4e022a).
Reviewer: win-agent (file owner + `/slo-plan` author), four-persona rotation, independent of linux-agent's self-critique.
Threat-model contract: **degraded mode** — no `<slug>-threat-model.slo.json` exists; the threat model is inline in §5B. Per the read-side contract I warn and make no abuse-ID-stability claim; I extended the inline index (abuse-7/8/9) to match controls already present in M6/M8.

## Relationship to the prior critique

linux-agent ran a self-critique on its own M6–M8 additions (`docs/slo/critique/agt-redteam-runbook-outcomes.md`) and auto-applied F-ENG-1/2, F-SEC-1/2/3 (+F-ENG-3 partial). **I independently VERIFIED all six landed in the runbook text** (not trusted):

| Prior finding | Claim | Verified in runbook |
|---|---|---|
| F-ENG-1 / F-SEC-1 | OS-enforced sandbox (netns/container, egress default-deny incl. `169.254.169.254`), not in-process | ✅ M6 design rule + invariants (§17 M6) |
| F-SEC-2 | scrubbed-env + no host fs mount; refuse if host cred path mountable | ✅ M6 invariants + BDD "no host creds reachable" |
| F-ENG-2 | stdlib-only gate scoped to default path (excludes `adapters/goose/`) + dep-audit gate | ✅ M6 static-analysis-gates row |
| F-SEC-3 | HTML-escape invariant + XSS BDD row (CWE-79) | ✅ M8 invariants + BDD "html injection (XSS)" |
| F-ENG-3 | OpenCRE snapshot source URL + retrieval date + CC-license recorded | ✅ M7 design rule |

## Findings (this pass)

| id | persona | category | runbook section | finding | concrete scenario | recommendation |
|----|---------|----------|-----------------|---------|-------------------|----------------|
| W-ENG-1 | Eng | auto-fix → **applied** | M5 (Goal/Outputs/Step-5/Smoke/Evidence) | Stale cross-milestone drift: M5 still instructed filing DW-002 (Goose) + DW-003 (OpenCRE) as GH issues, but the founder pulled those IN as M6/M7 (the §5B ledger + M5 DoD already say "BUILT, not filed"). linux updated the ledger but missed M5's body — a blind spot on its own reframe. | `/slo-execute M5` reads Step-5, files DW-002/DW-003 as "deferred" issues that duplicate the work being BUILT in M6/M7 — contradictory, confusing, and leaves the DW ledger half-disposed. | **Applied**: M5 now files only DW-001 (content-fixtures); DW-002→M6, DW-003→M7, DW-004→M1+M3 explicitly marked built/fixed, not filed. |
| W-ENG-2 | Eng | auto-fix → **applied** | §5B Detected-Work DW-004 | DW-004 dated `due=M1` but its fix (portable `run-smoke.sh` invocation) lands in M3; M1's validator already takes explicit path args. `/slo-execute M1` would flag an undisposed/mis-scoped M1 row. | At M1 close-out the DW-004 row can't be fully disposed (the smoke half doesn't exist yet), blocking the milestone on a paperwork mismatch. | **Applied**: DW-004 split — M1 validator-CLI explicit-args (done in M1) + M3 smoke-script portable invocation; due re-dated `M1 (validator) + M3 (smoke)`. |
| W-SEC-1 | Security | auto-fix → **applied** | §5B Threat Model Summary | Threat-model index incomplete (degraded-mode inline model): abuse cases listed only `tm-agtrt-abuse-1..6`, but M6 uses `-7` and linux's own critique proposed `-8`(XSS)/`-9`(sandbox-escape) without indexing them in §5B. Classes: CWE-79 (M8 stored XSS), CWE-918 (M6 SSRF/sandbox-escape). variant-analysis: N/A — planning doc, no code sites yet; controls already present in M6/M8 milestone bodies. | A future reader treats §5B as the complete threat model and misses that the M6 sandbox-escape and M8 XSS surfaces exist, under-reviewing them at execute. | **Applied**: added `tm-agtrt-abuse-7` (L3 secret leak), `tm-agtrt-abuse-8` (M8 XSS/CWE-79), `tm-agtrt-abuse-9` (M6 sandbox-escape+SSRF/CWE-918) to the §5B index; controls already exist in M6/M8. |
| W-ENG-3 | Eng | auto-fix → **applied** | M5 design rule | Hygiene-gate scan scope was implicit. tm-agtrt-abuse-1 is a payload smuggled into a committed `scenarios/*.json`, but the design rule said "generated artifact" — the smoke step already scans the whole dir, but the contract text under-specified it. | A future implementer scopes `raw_free_scan.py` to `reporters/out/**` only; a poisoned committed scenario slips past the gate to a public artifact. | **Applied**: M5 design rule now states the gate scans all committed AND generated artifacts including `scenarios/*.json` + `controls/*.csv`, not only reports. |
| W-DES-1 (was F-DES-1) | Design | auto-fix → **applied** | M8 design rule | M8 has a real UI surface (static HTML scorecard). The no-certification disclaimer was required "prominently" but unspecified — untestable, easy to bury. | A stakeholder skims `scorecard.html`, sees trap-class rows, and reads the benchmark as a pass/fail certification because the disclaimer is in a footer. | **Applied**: M8 disclaimer now must render at the TOP as a visually-distinct banner (not a footer); ties to tm-agtrt-abuse-4. |
| W-SEC-2 (was F-SEC-5) | Security | ask → **applied** (hardening) | M6 invariants | Class: CWE-918 / false-trusted-evidence. linux mandated OS-enforced sandboxing but did not say what happens when OS enforcement is **unavailable** (no netns/container privileges on a locked-down host/CI runner). variant-analysis: N/A — planning doc. | Engineer runs `--live` on a restricted CI runner without CAP_NET_ADMIN; if the adapter silently falls back to a weaker/in-process guard, it emits L3 evidence that is falsely trusted as sandboxed. | **Applied** (strengthens the existing fail-closed invariant, consistent with how linux handled its own F-SEC asks): if the OS sandbox cannot be established, the adapter REFUSES `--live` with a named reason — never an in-process fallback, never L3. |
| W-SEC-3 | Security | defer (residual, compensated) | M6 | Class: CWE-918 variant — data-exfil via the one allow-listed channel. The egress allowlist must permit the engineer-configured model endpoint; a trap could induce the live agent to encode data into a prompt to that allowed endpoint. variant-analysis: N/A — planning doc. | A trap convinces the live agent to send "summarize this: <data>" to the allowed model endpoint, exfiltrating via the only open channel. | **Defer (informational)**: residual but already compensated — the sandbox runs scrubbed-env + no host mount, so there is **no real secret/customer data present to exfiltrate** (only synthetic scenario data), and `tm-agtrt-abuse-7` scans L3 traces raw-free. Name the compensating control in the M6 lessons file at execute; no plan change. |
| W-CEO-1 (was F-CEO-1) | CEO | hold-scope (founder-decided) | M8 | The scorecard *product* was curated `promote_to_idea` (value hypothesis unvalidated); building it pre-validation risks effort no stakeholder requested. | Team ships M8's HTML scorecard; no external stakeholder ever consumes it; effort sunk. | **Hold-scope** — founder elected to include it. Keep M8 to the minimal static HTML+MD wedge as specified (no server/JS/telemetry); gate any further product investment on a real stakeholder request. Not blocking. |
| W-CEO-2 | CEO | ask (sequencing) | Milestone Tracker | M1–M4 is an independently shippable, valuable wedge (a mock agent-control benchmark with an evidence-level scorecard — the oc-4 headline) that needs none of the security-critical M6 live-sandbox investment. | The team builds straight through M5→M6 (the highest-risk, highest-effort milestone) before any user has touched the M1–M4 mock benchmark, so a wedge-validity problem is found late. | **Ask (founder decides)**: insert an explicit user-feedback checkpoint after M4 (or M5) — ship the mock benchmark for honest feedback before committing to the M6 OS-sandbox build. One sentence of opportunity cost: a checkpoint delays M6 start by one feedback cycle. No auto-apply. |

## Outcome-first verdict (eng-lead lens, `tm-outcome-first-abuse-2`)

No outcome-test theatre. Each `oc-1..oc-8` drives a real CLI/script entrypoint with concrete engineer-visible assertions; the per-milestone Front-to-End Outcome Tests are per-stage (not one monolithic end-state test); each milestone DoD gates on its stage-level F2E outcome (founder law #1634). oc-6 (live L3) is genuinely cross-layer (engineer's real agent → sandboxed run → L3 evidence). M1's oc-1 is already implemented and verified green (PR #24). The reframe is genuinely outcome-first. **Concurred.**

## Design persona note

NOT N/A this runbook — M8 introduces a static-HTML UI surface (`scorecard.html`). Reviewed: empty-state covered (M8 BDD "empty run"), destructive-action N/A (read-only report), AI-slop N/A (data-driven render). Only finding: W-DES-1 (disclaimer prominence), applied.

## Disposition summary

- **Applied (6 auto-fixes / ask-hardening)**: W-ENG-1, W-ENG-2, W-ENG-3, W-SEC-1, W-DES-1, W-SEC-2.
- **Ask (founder decides, not applied)**: W-CEO-2 (post-M4 feedback checkpoint).
- **Hold-scope / defer (informational)**: W-CEO-1 (M8 minimal, founder-decided), W-SEC-3 (M6 exfil residual, compensated).

## Handoff

The 8-milestone runbook passes critique with the above auto-fixes applied. M1 is already executed + reviewed PASS (PR #24). One `ask` (W-CEO-2) awaits founder; it does not block. Next SLO step: `/slo-execute M2` (linux is already driving it) — the critique findings W-SEC-1/2 + W-DES-1 are forward inputs to M6/M8 execution.
