# Critique — RUNBOOK-round6-cascade-experiment

Date: 2026-06-11
Target: `docs/RUNBOOK-round6-cascade-experiment.md` (line refs from that file as of this commit)
Rotation: CEO → Eng lead → Security → Design (skipped, no UI surface)

**Degraded-mode notice (security pass)**: no `docs/slo/design/*-threat-model.{md,slo.json}`
exists for this runbook. The security persona reviewed against the runbook's
embedded §5B Threat Model Summary (`tm-r6c-abuse-1/2/3`, lines ~204–218) per
the skill's degraded-mode rule. No abuse-ID-stability claim is made; IDs are
treated as runbook-local. This is recorded as finding F-SEC-3 rather than a
hard halt (research-corpus repo, no service surface).

**Architecture-coherence notice (eng pass)**: no `docs/slo/design/<slug>-code-map.md`
exists; coherence was checked against `docs/ARCHITECTURE.md` instead. Exemplar /
anti-exemplar and AI-tolerance rows are present in every milestone Contract
Block — no drift found there.

## Findings

| id | persona | category | runbook section | finding | concrete scenario | recommendation |
|----|---------|----------|-----------------|---------|-------------------|----------------|
| F-CEO-1 | CEO | ask | M5 Files Allowed To Change / report contract (§17 M5, ~L1083+) | Selective expansion: the runbook never states what decision each verdict combination drives. M5 forbids upstream PR drafting (correct) but defines no decision hook, and the in-flight RFC drafts + `docs/UPSTREAM-PR-PLAN.md` cite round-4 numbers that round 6 will supersede. | The experiment accepts at M4; the report sits in the repo; the community RFC ships with stale round-4 figures and the upstream PR2 plan never picks up the new evidence — the experiment's outcome changes nothing. | Add a short "Decision hook" subsection to M5's report contract: verdict-combination → next action table (M4 accept → PR2 proposal updated with round-6 artifacts; M4 overlap-kill → negative-result publication + encoder-upgrade runbook; etc.) and add `docs/UPSTREAM-PR-PLAN.md` to M5's files-allowed list for a one-line evidence-pointer update. |
| F-CEO-2 | CEO | ask | §2 M5 row (L82) + M1 Notes (~L485) | Scope-risk acceptance is implicit: the pipeline can fully "accept" with the multilingual bypass class still at 0% catch (it is a bypass class, not an attack family, so the per-family floor never sees it; Gate 0 deliberately has no translation transform). | An attacker translates "ignore all previous instructions" into German in an indirect-injection document; every stage passes it; the published report reads as a success with the gap visible only deep in a bypass-class table. | Keep translation out of scope (hold), but make the acceptance explicit: add "multilingual bypass class is an accepted residual of this round" to §2 M5's accept cell and to the M5 report's caveats-first section, with a future-work pointer (multilingual exemplars or multilingual-capable encoder in the next round). |
| F-ENG-1 | eng | ask | M4 Context + Outputs (§17 M4, ~L870–905) | Hidden assumption: Gate-2 arms are trained on the *validation* uncertain lane, but validation lane membership is partially in-sample for the M2 head (selected on validation) while test lane membership is out-of-sample — the training and evaluation lanes are drawn from different distributions, compounding the M2→M3→M4 validation-reuse chain. | The floor arm's coefficients fit a validation-uncertain population that is smaller/cleaner than the test-uncertain population; the floor−control delta on test lands at 3.8pt; the §2 ≥5pt bar kills the cascade for a protocol artifact rather than a real absence of signal, and nobody can tell which. | Add a pre-registered lane-shift diagnostic to M4's outputs: validation-vs-test uncertain-lane composition table (lane size, attack/benign mix, score distribution distance), and add one sentence to the §2 M4 kill cell: a kill verdict must cite the lane-shift table to distinguish protocol artifact from genuine shared-blind-spot before the negative result is published. |
| F-ENG-2 | eng | ask | M1 normalize.py contract + BDD table (§17 M1, ~L335–470) | Missing failure mode: decode-sniff has no validity guard. Base64/hex sniffing will fire on benign high-entropy rows (`high_entropy_structured_data`, 400 test rows) and "decode" them into mojibake, moving their embeddings unpredictably. | A benign row carrying a base64-encoded API payload is decoded to binary garbage, embeds near nothing in the benign exemplar bank, crosses τ′, and produces exactly the benign obfuscation-control FP that the §2 M1 side-condition forbids — Gate 0 fails its accept bar through its own transform. | Add a decode-acceptance rule to the `normalize.py` contract: a sniffed decode is kept only if the output is valid UTF-8 with ≥90% printable characters, else original text is kept with tag `decode_rejected`. Add a matching BDD row (invalid-input category) and include `high_entropy_structured_data` FP count as a named column in the M1 report. |
| F-ENG-3 | eng | ask | M2 Contract Block, resource-bounds row (§17 M2, ~L540) | Hidden assumption: the embedding cache key uses a manually-maintained "normalize version tag" — a human must remember to bump it. | A developer tweaks the homoglyph map during M2 debugging, forgets the bump; M2 trains and freezes on stale embeddings; the freeze record's provenance silently lies about the normalization that produced the vectors. | Replace the manual tag with the SHA-256 of `normalize.py` file content (plus the corpus manifest hash already specified) as the cache key, computed at runtime — staleness becomes structurally impossible. One-line contract edit. |
| F-ENG-4 | eng | ask | §2 M3 row (L80) | Internal inconsistency: the M3 second accept condition ("uncertain lane ≤2% of benign at 1:1000") is implied by the first — if α_pass=1% coverage holds, benign in (uncertain ∪ flag) ≤~1% < 2% by construction. The bar is toothless, while the real review-cost risk (queue precision) is reported but not gated. | Coverage holds at 0.9% benign-in-uncertain; the second condition auto-passes; at 1:1000 prevalence the review queue is 98%+ false alarms (precision <1%); M3 "accepts" while describing an unstaffable review lane — the exact single-dial failure this runbook exists to escape. | Replace the second M3 accept condition with the bar pre-registered in the design conversation: "review-queue precision at 1:1000 prevalence ≥5%" (attacks/(attacks+benign) among uncertain-lane items). Keep the ≤2% lane-size number as a reported metric, not a gate. |
| F-ENG-5 | eng | ask | M4 step 6 + test-metrics output (§17 M4, ~L905, L1005) | Post-hoc freedom: "error-overlap ratio" has multiple defensible formulas (miss-side, FP-side, pooled; conditioning on pass-lane only vs all non-flag) and the runbook pins none of them. | After test results exist, the analyst computes three overlap variants, one lands under 1.5× and gets reported — the §2 independence verdict becomes selectable rather than pre-registered. | Pin the formulas in M4's Contract Block now: miss-side = P(arm fails to flag │ attack ∧ G1 pass-lane) vs P(arm fails to flag │ attack, all-lanes shadow); FP-side analogue for benign; §2 bar applies to the *worse* of the two ratios. Add both as named fields in `test-metrics.json`. |
| F-ENG-6 | eng | auto-fix | §2 table (L73–83) | The gates' independence is implicit: nothing states that a later kill does not retroactively invalidate earlier accepts, or that M4's headline can fail while M1–M3 accepts stand as published results. | A reader of the final report treats the M4 overlap-kill as discrediting the M2 head result, which survives on its own and feeds the encoder-upgrade redirect. | Add one clarifying sentence under the §2 table. **Applied inline** (see runbook L84). |
| F-SEC-1 | security | ask | M1 Step-by-Step step 1 + §5B Operator Readiness (~L196, L474) | **V10 — vulnerable/unvetted dependency (supply chain)**, bug-class-catalog V10. No threat-model row covers supply chain (gap in embedded §5B — see F-SEC-3); class status: **residual** — `pip install fastembed psutil` pins versions but not hashes; PyPI version pins are substitutable. Variant analysis: `rg -n "pip install" docs/ meta/` → 2 sites (M1 step 1, M2 inherits env); no lockfile or hash manifest exists anywhere in the repo — the absence is the finding. | A maintainer of a transitive dependency of `fastembed` ships a compromised point release within the pinned range on the day of env restore; the M1 runner executes it locally with repo write access; committed round-6 artifacts and freeze-record hashes are generated by tampered code, poisoning the evidence chain the upstream PR relies on. Impact: research-integrity loss, dev-machine compromise; no secret/PII exposure (none present). | Pin by hash: generate `meta/harness/round6-cascade/requirements.lock` (`pip freeze` + `--require-hashes` format) during M1 env restore, commit it, install with `pip install --require-hashes -r requirements.lock`, and record the lock SHA-256 in `provenance.json`. Add a §5B Security Test Plan row for it. Class moves residual → mitigated. |
| F-SEC-2 | security | ask | M1 normalize.py transform tags (§17 M1, Files table ~L440) | **V7 — log injection / unstructured event data** (closest catalog class), cites `tm-r6c-abuse-3` (raw text leakage into committed artifacts); class status: **mitigated, not eliminated** — forbidden-field checks scan field *names*, but transform tags are free-form strings constructed in code; a tag that interpolates input fragments (e.g., `decode_rejected:<prefix>`) would carry attack text into committed per-row artifacts past the field-name check. Variant analysis: N/A — code does not exist yet (design-time constraint); enforcement point named instead. | A developer adds `f"decode_rejected:{raw[:32]}"` for debuggability during M1 implementation; per-row JSONL now contains 32-char fragments of synthetic attack payloads; the artifact ships in the public repo and the metadata-only guarantee in README is false. | Eliminate the class structurally: declare transform tags as a closed enum in `normalize.py` (no string construction), assert membership at write time, and extend the validator + `test_artifact_hygiene.py` to reject any per-row tag value outside the enum. One contract-row edit in M1's invariants. |
| F-SEC-3 | security | defer | §5B Threat Model Summary (~L204) | **V17 — missing threat model** (formal): no `/slo-architect` threat model or `.slo.json` exists; the runbook's inline §5B summary is the only source, so `tm-r6c-abuse-N` IDs have no frozen schema and future critiques cannot guarantee ID stability. Class status: **mitigated** by the inline summary; residual = ID-drift risk across future runbooks. | A round-7 runbook reuses `tm-r6c-abuse-2` for a different abuse case; cross-references in critique files and BDD tables silently point at the wrong scenario. | Defer: acceptable for this research repo now. If a round-7 runbook is opened, freeze the IDs into `docs/slo/design/round6-cascade-threat-model.slo.json` first. No action required for this runbook. |
| F-DES-0 | design | hold-scope | — | Design pass skipped: no UI surface anywhere in the runbook (batch harness + docs). | — | — |

## Category tally

- auto-fix: 1 (F-ENG-6 — applied inline)
- ask: 8 (F-CEO-1, F-CEO-2, F-ENG-1…5, F-SEC-1, F-SEC-2)
- defer: 1 (F-SEC-3)
- hold-scope: 1 (F-DES-0, procedural)

## Resolution (2026-06-11)

All 8 ask findings **accepted by the user** and applied to the runbook:

| id | landed as |
|---|---|
| F-CEO-1 | M5 report Decision-hook section (verdict→next-action table); `docs/UPSTREAM-PR-PLAN.md` added to M5 allow-list (evidence-pointer line only) |
| F-CEO-2 | §2 M5 accept cell + M5 report caveats: multilingual 0% = accepted residual with future-work pointer |
| F-ENG-1 | M4 outputs gain `lane-shift-diagnostic.json`; §2 M4 kill cell requires citing it before publishing a negative result |
| F-ENG-2 | M1 decode-acceptance rule (≥90% printable UTF-8 else `decode_rejected`); new BDD row; `high_entropy_structured_data` named column in M1 report |
| F-ENG-3 | M2 embedding-cache key = SHA-256 of `normalize.py` content (runtime-computed) + corpus manifest hash |
| F-ENG-4 | §2 M3 second bar replaced with review-queue precision ≥5% at 1:1000; lane size ≤2% demoted to reported metric; M3 Evidence Log updated |
| F-ENG-5 | M4 pinned overlap formulas (`overlap_miss_side`, `overlap_fp_side`; bar on the worse); §2 M4 text updated |
| F-ENG-6 | (auto-fix) §2 gate-independence note added |
| F-SEC-1 | M1 step 1: hash-pinned `requirements.lock` + `pip install --require-hashes`; §5B SCA row updated; lock SHA in provenance. V10 residual → mitigated |
| F-SEC-2 | M1 invariant (6): closed transform-tag enum, write-time assertion, validator + hygiene enforcement; new BDD row. tm-r6c-abuse-3 path eliminated |

F-SEC-3 remains deferred (freeze `.slo.json` before any round-7 runbook).
Critique complete — `/slo-execute M1` is unblocked.

## CEO scope summary

Mode: **hold scope overall** — the five-milestone shape, the out-of-scope list
(no AnnotatorDispatcher build, no real-traffic claims, no encoder swap), and
M5's aggregation-only isolation are right-sized for a research round. The two
asks are surgical: a decision hook so the outcome drives something (F-CEO-1)
and explicit acceptance of the multilingual residual (F-CEO-2). No expansion
recommended; no milestone reordering — the dependency chain (normalize → head
→ buckets → gate 2) is real and the "aha" placement at M4 is forced, not
buried by accident.
