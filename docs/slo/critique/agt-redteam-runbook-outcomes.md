# /slo-critique — AGT redteam runbook (outcome-first reframe + M6–M8)

Target: `docs/RUNBOOK-agt-redteam-agent-traps-opencre.md` (PR #23, branch `slo/agt-redteam-runbook-outcomes`).
Reviewer: linux-agent running the four-persona rotation on its own founder-directed additions.
Threat-model contract: **degraded mode** — no `<slug>-threat-model.slo.json` exists; the threat model is inline in §5B (`tm-agtrt-abuse-1..7`). No abuse-ID-stability claim is made; IDs read from §5B as-authored.

## Findings

| id | persona | category | section | finding | concrete scenario | recommendation |
|----|---------|----------|---------|---------|-------------------|----------------|
| F-CEO-1 | CEO | hold-scope (founder-decided) | M8 | The scorecard *product* was `promote_to_idea` (value hypothesis unvalidated). Building it now risks a product no stakeholder has asked for. | Team ships M8's HTML scorecard; no external stakeholder ever consumes it; effort sunk. | Keep M8 to the minimal static HTML+MD wedge as specified; gate any further product investment on a real stakeholder request. Founder already chose to include it → noted, not blocking. |
| F-ENG-1 | Eng | ask → **auto-fixed** | M6 | "Hermetic sandbox" was asserted but the enforcement mechanism was unspecified — a Python-level/env-scan guard is bypassable by the live agent's real subprocess. | Engineer runs `--live`; the agent shells out and the in-process allowlist never sees it. | **Applied:** design rule + invariants now require OS-level enforcement (netns/container egress-deny, scrubbed env, no host fs mount) + an OS-layer egress test. |
| F-ENG-2 | Eng | ask → **auto-fixed** | M6 | M6's non-stdlib live deps would make the M3/M5 stdlib-only gate fail — self-contradiction. | `/slo-execute M6` adds `goose` import; the stdlib-only grep gate goes red on the very milestone that needs the dep. | **Applied:** static-gate row now scopes the stdlib-only gate to the default path (excludes `adapters/goose/`) + adds a dependency-audit gate for `adapters/goose/`. |
| F-ENG-3 | Eng | ask | M7 | OpenCRE snapshot provenance/license was unspecified. | A relations snapshot of unknown origin/license is committed; an upstream contribution later hits a license problem. | **Applied (partial):** design rule now requires source URL + retrieval date + CC-license recorded with the committed snapshot. |
| F-SEC-1 | Security | ask → **auto-fixed** (high) | M6 | Sandbox escape / SSRF (CWE-918): a live agent prompted by a trap can reach the cloud-metadata endpoint or write host files if the sandbox is not OS-enforced. | `--live` run; agent executes `curl http://169.254.169.254/latest/meta-data/iam/...` and exfiltrates a role credential. | **Applied:** OS-level egress default-deny incl. `169.254.169.254`, proven by a real-subprocess BDD row; `tm-agtrt-abuse-3` control is now OS-enforced. |
| F-SEC-2 | Security | ask → **auto-fixed** | M6 | Host-credential exposure: an env-var scan misses creds in `~/.aws/credentials` / OS keychain. | Engineer has AWS creds in `~/.aws`; the live agent reads the file and acts on prod. | **Applied:** sandbox runs scrubbed-env + **no host fs mount**; refuses to start if a host cred path is mountable; new BDD row. |
| F-SEC-3 | Security | ask → **auto-fixed** | M8 | Stored XSS (CWE-79): unescaped scenario/control fields rendered into the shareable HTML. | A contributor names a scenario `<script>fetch(...)</script>`; M8 renders it; a stakeholder opens `scorecard.html` and the script runs. | **Applied:** HTML-escape invariant + an XSS BDD row added to M8. |
| F-SEC-4 | Security | ask | §5B threat model | New M6/M8 surfaces (OS-sandbox-escape, HTML-injection) extend beyond the inline `tm-agtrt-abuse-1..7`. | A future reader treats §5B as complete and misses the M8 XSS surface. | At `/slo-execute`, extend the inline threat model (consider `tm-agtrt-abuse-8` HTML-injection, `tm-agtrt-abuse-9` OS-sandbox-escape) — or promote §5B to a `<slug>-threat-model.slo.json`. (Left for win/owner.) |
| F-DES-1 | Design | ask | M8 | The "evidence, not certification" disclaimer must be visually prominent, not buried. | A stakeholder skims the HTML, sees trap-class rows, and reads it as a pass/fail certification. | M8: render the `certification_claim:false` disclaimer at the top of the report, visually distinct. (Left for win/owner at execute.) |

## Outcome-first verdict (eng-lead lens, `tm-outcome-first-abuse-2` check)

No outcome-test theatre detected. Each `oc-1..oc-8` drives a real CLI/script entrypoint with concrete, engineer-visible assertions; the per-milestone Front-to-End Outcome Tests are per-stage (not one monolithic end-state test), and each milestone DoD gates on its stage-level F2E outcome. `oc-6` (live L3) is genuinely cross-layer. The reframe is genuinely outcome-first.

## Disposition

- F-ENG-1/2, F-SEC-1/2/3, F-ENG-3 (partial): **auto-applied** in this PR (correctness/security hardening of linux's own new milestones).
- F-CEO-1, F-SEC-4, F-DES-1: **ask** — left for win (file owner) to weigh at `/slo-critique` / `/slo-execute`; none block the reframe.

Next SLO step: win reviews+merges PR #23, runs `/slo-critique` in-repo, then `/slo-execute M1`.
