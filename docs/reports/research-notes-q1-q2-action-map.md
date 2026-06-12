# Research Notes Q1/Q2 Action Map

Issue: https://github.com/kerberosmansour/AGT-Embeddings-Experiment/issues/8

## Purpose

This is the closeout map for issue #8. It does not introduce a new detector,
corpus, or headline metric. It reconciles the original research notes with the
follow-up work now in the repo, then names what still has to happen before the
claims become stronger.

## TL;DR

- The old **92.5% @ 0 FP** co-equal ensemble idea was useful as a lead, but it
  was selected on mined test data. Issue #9 corrected it with a deterministic
  validator: strict co-equal is **86.85% @ 0 observed FP**, and the
  0.1%-validation-FPR variant ties Rec B at about **87.23%**.
- The useful improvement came from the normalizer lane, not from chasing the
  ensemble number. Issue #10's extended normalizer follow-up reports **88.72% @
  0 observed FP** for the robust Rec-B-shaped ensemble with the new normalizer.
- The false-positive honesty problem is still the main blocker. Round 7 now has
  hard benign controls, WS-C measurement, FP attribution, and a
  source-attributed reality-check intake, but those are still synthetic or
  payload-derived research arms, not real data validation.
- The next strongest claim needs a real-traffic or source-reviewed benign FP
  audit. Until then, every 0-FP result remains a synthetic-corpus or
  payload-derived-arm result, not a production/default-blocking claim.

## Q1 - Improvement Opportunities Disposition

| Original note | Disposition | Evidence | Status |
|---|---|---|---|
| Co-equal two-model ensemble might be a free win at 92.5% @ 0 FP. | Corrected. The shape is valid, but the 92.5% figure was test-set overfitting and is rejected. | `docs/slo/tickets/ticket-9-coequal-ensemble-validation.md`; `docs/reports/exp4-normalizer-ensemble-report.md`; `artifacts/exp4-coequal/` | Complete for current artifacts. |
| The residual is de-obfuscation-bound, not ensemble-bound. | Partially addressed. Encoding and rot13 improved; multilingual, compact/chunked word-boundary tricks, and delivery-layer attacks remain. | `docs/reports/exp4-normalizer-ensemble-report.md`; `docs/slo/tickets/ticket-10-normalizer-encoding-rot13.md`; `docs/RUNBOOK-round7-garak-corpus.md` | Partial. |
| Test-set overfitting risk must be eliminated before believing new headlines. | Institutionalized. The #9 validator requires `selected_on=validation`, and round-7 WS-C freezes tau on validation before test. | `meta/harness/exp4-coequal/validate_coequal.py`; `meta/harness/round7-garak/run_2x2.py`; `docs/slo/tickets/ticket-16-round7-ws-c-2x2-measurement.md` | Complete for current artifacts. |
| Synthetic FP ceiling blocks trust in 0-FP claims. | Still true. The current work mitigates it with hard benign controls and attribution, but does not replace real data. | `docs/proposals/round7-generator-proposal.md`; `docs/slo/tickets/ticket-15-round7-normalizer-fp-triage.md`; `docs/slo/tickets/ticket-17-reality-check-intake-validation.md` | Ongoing. |

## Corrected Metric Boundary

| Claim shape | Current honest wording |
|---|---|
| "92.5% catch @ 0 FP" | Reject as a test-derived ceiling. Do not use as a headline. |
| "Co-equal ensemble improves over Rec B" | Not supported after validation-freeze. Strict co-equal is about 86.85%; the 0.1%-validation-FPR variant ties Rec B at about 87.23%. |
| "Extended normalizer plus robust ensemble reaches 88.72%" | Accept only as validation-frozen synthetic-corpus evidence at 0 observed FP. It is not real-traffic validation. |
| "R1 / structural controls are safe at 0 FP" | Treat as a labels-perfect ceiling until hard benign and real benign traffic occupy the missing `untrusted+tool` surfaces. |

## Q2 - Synthetic Data Requirements Disposition

| Requirement from #8 | What now exists | Remaining gap |
|---|---|---|
| Hard benign negatives: legitimate `untrusted+tool` flows. | Round-7 proposal requires `benign_multistep_tool_use`, including untrusted-source legitimate low-risk tool calls. | Needs larger freeze and a real/source-reviewed benign arm to estimate production FP. |
| Hard benign negatives: mid-range benign. | WS-C pilot and #15 attribution make pilot FPs visible instead of hiding them. | Needs calibration against a bigger, less templated benign distribution. |
| Hard benign negatives: sensitive sinks / handles that are still benign. | Round-7 hard-negative philosophy names matched controls and per-subclass FP reporting. | Needs source-scale examples where handles do not predict attack-ness. |
| Decorrelated attacks without obvious structural handles. | Round-7 separates `structural`, `workflow_review`, and `evidence` containment classes so text-meaning attacks do not inflate structural coverage. | Needs more real-world semantic attacks and benign lookalikes, especially jailbreak and direct-override variants. |
| Multilingual on both attack and benign sides. | Still named as a residual; current normalizer intentionally does not translate. | Open. Needs bilingual benign controls and a deliberate non-translation policy decision. |
| Delivery vectors: markup, CSS, Markdown, LaTeX, image metadata. | Experiment 2 / Gate-0++ issue draft defines the data and measurement shape. #12 covers output render hazards for terminal controls. | Not yet implemented as a full corpus arm; issue still needs filing/building beyond the draft. |
| Under-represented categories: semantic manipulation and RAG/in-context poisoning. | Round-7 adds jailbreak, agentic tool exploit, package hallucination, and terminal escape buckets; #13 defines outbound-stage semantic evidence. | RAG poisoning and richer semantic-manipulation families still need their own corpus slices. |
| Round-4 hygiene wrapper: holdouts, leakage checks, frozen splits, metadata-only artifacts. | Round-7 generator/checker and WS-C validator carry forward split leakage, normalized duplicate, Rust-normalizer audit, and metadata-only checks. | Large-profile freeze and independent audit still pending. |
| Real-world reality check. | `corpus/round7/reality-check/` now has an Apache-2.0/MIT-only, redacted, source-attributed intake plus synthetic variation smoke evidence. | Rows still need downstream labeling/folding into the payload-derived arm and FP/catch reporting separate from the synthetic headline. |

## AGT Design Implications

The experiment should stay AGT-shaped:

- Inbound detection uses the Rust-first normalizer contract from
  `rust/agt-normalize/` and records transform tags as evidence.
- Deterministic structural controls can justify `Deny` only when the runtime
  fields express the control contract, for example untrusted content attempting
  a sensitive tool action.
- Output byte/render hazards belong to #12's render-safe sanitizer and ACS
  `Transform`, not the full inbound canonicalizer.
- Outbound semantic scanning belongs to #13 as default-off evidence routed to
  `Escalate` or `Warn`, not as a default blocking boundary.

## Recommended Next Lanes

| Lane | Recommendation | Why |
|---|---|---|
| Micro | Use this action map as the issue #8 closeout reference and stop repeating 92.5% except as a rejected overfit number. | Prevents stale metrics from contaminating future summaries. |
| Milestone | Run a larger round-7 freeze with the hard benign slices first-class, then rerun WS-C with #15-style FP attribution. | This directly attacks the synthetic FP ceiling identified in Q2. |
| Fresh runbook | Design a real/source-reviewed benign FP validation arm, privacy-reviewed and source-attributed, with no raw examples in public artifacts. | This is the missing evidence for any stronger false-positive claim. |
| Fresh runbook | File/build the Gate-0++ delivery-layer corpus from the Experiment 2 draft. | Current plain-text corpora cannot measure markup/CSS/Markdown/LaTeX delivery attacks. |
| Fresh runbook | Build the outbound corpus/harness from #13 after #12 sanitizer shape is fixed. | Separates deterministic render safety from semantic outbound risk evidence. |

## Public-Safety, License, And Data Boundary

- Public GitHub and AgentBus updates should point to file paths, aggregate
  counts, hashes, and validation commands only.
- No raw payload-derived examples should be pasted into public issues or this
  report.
- The payload-derived reality-check arm must stay separate from the synthetic
  headline and limited to Apache-2.0 or MIT sources unless a later legal review
  deliberately expands the license set.
- Synthetic variations are useful only when they preserve the attack/control
  shape and record their parent provenance. They do not become real data.

## Closeout Recommendation For #8

Treat #8 as mapped to action, not fully solved. The completed follow-ups corrected
the ensemble claim, strengthened the normalizer path, added round-7 hard benign
methodology, and created a reality-check intake. The unresolved blocker is still
the same one #8 identified: credible false-positive validation on realistic benign
traffic.
