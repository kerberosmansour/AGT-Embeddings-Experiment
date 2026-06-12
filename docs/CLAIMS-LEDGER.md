# Claims Ledger

This ledger maps the public narrative to the evidence that must be migrated
into this repository.

Current migrated evidence is split across:

- M1 corpus/rules baseline: target commit `25f8d06`.
- M2 embedding/kNN sweep and Youden's J readout: target commit `834da55`.
- M3 governance metadata/value-add readout: this M3 migration commit.

## Narrative Claims And Evidence

| Narrative claim | Current evidence | Source artifact to migrate | Status |
|---|---|---|---|
| AGT rules-only detector has low recall on the hard held-out set. | `180 / 17600 = 0.010227` attack recall. | `corpus/round4/rules-baseline-large-metrics.json` | Migrated in M1; Linux and Windows readbacks PASS. |
| AGT rules-only detector has material false positives on benign examples. | `2136 / 27200 = 0.078529` benign false-positive rate. | `corpus/round4/rules-baseline-large-metrics.json` | Migrated in M1; Linux and Windows readbacks PASS. |
| The evaluation corpus has 44,800 labelled examples. | `row_count=44800`; split counts `28504 / 6888 / 9408`. | `corpus/round4/manifest-large.json`; `corpus/round4/check-large-summary.json` | Migrated in M1; leakage checks PASS. |
| The split avoids family/group leakage. | Family leaks `0`; group leaks `0`; exact normalized cross-split leaks `0`; near-duplicate cross-split leaks `0`. | `corpus/round4/check-large-summary.json` | Migrated in M1; independent audit PASS. |
| Embedding/kNN at Youden's J catches about 88% on frozen test. | Test recall `0.882609` at threshold `-0.00609511`. | `artifacts/embedding-sweep/youden-j-tuning.json`; `docs/reports/round4-youden-j-tuning.md` | Migrated in M2 with plateau-midpoint caveat; Linux M2 audit PASS. |
| Embedding/kNN at Youden's J has about 16% false positives. | Test FPR `0.163059`, FP `934 / 5728`. | `artifacts/embedding-sweep/youden-j-tuning.json`; `docs/reports/round4-youden-j-tuning.md` | Migrated in M2; Linux M2 audit PASS. |
| Conservative embedding point has zero observed false positives. | Test recall `0.141848`, FPR `0.0`, FP `0`. | `artifacts/embedding-sweep/test-metrics.json`; `artifacts/embedding-sweep/youden-j-tuning.json`; `docs/reports/round4-mac-embedding-sweep-evidence.md` | Migrated in M2; Linux M2 audit PASS. |
| Youden's J is a dial, not a default threshold recommendation. | Plateau-midpoint caveat recorded; no production threshold claim. | `docs/reports/round4-youden-j-tuning.md` | Migrated in M2; report frames J-max as a review-load stress point. |
| Embeddings should augment AGT policy, not replace it. | On frozen test, `policy_plus_embedding` reduced unsafe-action success vs `policy_only_gate` by `0.040761` absolute with unchanged hard-block FP `0.139665` and approval-load FP `0.0`. Validation still has `80` critical allows. | `artifacts/governance-eval/metrics.json`; `docs/reports/round4-governance-eval-evidence.md` | Migrated in M3; Linux M3 audit PASS. Research readout only; not default blocking or production evidence. |
| Round 5 improves methodology for source-reviewed fixture generation. | 72 source-mapped synthetic rows, 72 families, matched controls, zero family/group/exact/near-duplicate split leakage, validation-only freeze before test scoring. | `artifacts/source-scale-pilot/summary.json`; `docs/methodology/round5-source-scale-methodology.md`; `docs/reports/round5-source-scale-pilot.md` | Migrated as sanitized methodology evidence. It does not update headline detector metrics. |

## Baseline Pinning Requirement

The "about 1%" rules-only catch-rate claim is the most important number to
anchor before upstreaming. It means:

```text
AGT Rust prompt-injection detector at a specific commit and detector-file hash,
scored on this synthetic hard held-out corpus, caught 180 of 17,600 attack rows.
```

It does not mean AGT generally catches only 1% of prompt-injection attacks.
Before any AGT PR is opened, rerun the rules-only harness against fresh AGT
upstream `main` and record the commit SHA, detector SHA-256, command, corpus
manifest hash, and resulting TP/FP rates. Current preflight:
fresh AGT `origin/main` was
`730ffbb060c44362485b786c63aa08439c49d7e1`, and `prompt_injection.rs`
matched the experiment vendored snapshot with SHA-256
`92ac1f855e03502886fffdfb8cf9eece8ce7c2bea268ecacb4ff6386cb345ab3`.
See `docs/methodology/agt-upstream-baseline-refresh.md`.

## Wording Guardrails

- Say "labelled examples" or "technique-labelled examples" unless reviewed
  source-derived artifacts are included.
- Say "synthetic research corpus" where the evidence comes from generated rows.
- Say "optional/default-off signal" rather than "replacement detector."
- Say "review/routing signal" rather than "auto-blocking."
- Say "not validated on real traffic" until that evidence exists.
- Say "not production safety evidence" until separate deployment evidence
  exists.

## Evidence Gaps Before Stronger Claims

| Stronger claim | Missing evidence |
|---|---|
| Validated on real traffic. | Real traffic sample, privacy review, and false-positive audit. |
| Source-derived public examples are folded in. | Reviewed source-derived pilot artifacts and independent audit. |
| Ready for default blocking. | Review-load budget, policy evaluation, and false-positive proof at realistic prevalence. |
| Governance integration is ready. | Validation split still has critical allows; needs policy/harness iteration plus independent audit. |
| Upstream optional embedding feature is ready. | PR 1 benchmark fixture review plus documented generation methodology and fresh AGT baseline pin. |

## Issue #8 Research Notes Action Map

Evidence: `docs/reports/research-notes-q1-q2-action-map.md`.

Issue #8 is now treated as an action map, not as a headline metric source. The
old 92.5% co-equal ensemble figure is rejected as test-set overfitting; the
validation-frozen follow-up evidence is the #9 correction and the #10
normalizer-backed 88.72% synthetic-corpus result at 0 observed FP. Round-7 hard
benign controls and the Apache-2.0/MIT reality-check intake improve visibility,
but they do not replace the missing real-data false-positive audit.

Guardrail: do not collapse synthetic, payload-derived reality-check, and real
traffic claims into one bucket. Use paths, hashes, aggregate counts, and
validation commands in public summaries; do not publish raw payload examples.

## Round-6 Cascade Claims (additive; round-4 rows above unchanged)

Evidence: `docs/reports/round6-cascade-report.md`,
`artifacts/round6-cascade/m1..m5/`, harness `meta/harness/round6-cascade/`.
All numbers are frozen-test synthetic-corpus research evidence with
pre-registered accept/kill thresholds (runbook §2).

| Public claim | Evidence | §2 verdict |
|---|---|---|
| De-obfuscation in front of scoring triples zero-FP catch (14.2%→43.3%) with 0 benign-control FPs. | `m1-gate0/test-metrics.json` | M1 partial accept |
| Every attack family is caught end-to-end (round-4's tool_abuse 0%→37.7%, prompt_leakage 0%→100%). | `m5-summary/summary-metrics.json` per_family_end_to_end | M5 per-family floors PASS |
| A trained head does not beat kNN at deployable FPR on this corpus. | `m2-head/test-metrics.json` dominance grid | M2 head NOT SUPPORTED |
| Head generalizes to unseen families (LOFO median 71.6%, 0 families <5%). | `m2-head/lofo-metrics.json` | M2 LOFO PASS |
| Conformal pass-lane coverage transfers (benign escape 1.20%, 1% in Wilson); review queue 5.07% precise at 1:1000. | `m3-buckets/test-metrics.json` | M3 ACCEPT |
| The two-gate independence assumption is refuted (miss-side overlap 2.76×). | `m4-gate2/test-metrics.json` overlap_ratios | M4 independence NOT MET |
| Free AGT metadata ≈ full metadata (floor +3.8pt over score; ceiling +0.1pt over floor). | `m4-gate2/test-metrics.json` deltas | M4 floor-control NOT MET (real but <5pt) |
| End-to-end 80% catch @ ≤1% FPR is structurally unreachable (ceiling 64.4%). | `m4-gate2/test-metrics.json` | M4 headline NOT MET |

### Round-6 wording guardrails
- The cascade is a detection/triage layer **inside** AGT's deterministic
  governance boundary — never call it the security boundary.
- Do **not** claim the two gates are independent; on this corpus they share
  blind spots.
- "free-tier Gate 2" = fields every AGT deployment has; the ceiling integration
  is not worth it on this evidence.

## Experiment 1 — Structural Auto-Block Ceiling (additive)

Evidence: `docs/reports/exp1-structural-autoblock-report.md`,
`artifacts/exp1-structural/`, harness `meta/harness/exp1-structural/`.
Frozen-test synthetic-corpus, **labels-perfect ceiling** (governance labels are
exact on synthetic data; not a production guarantee). No embedding model run —
reuses the committed round-6 zero-FP decision.

| Public claim | Evidence | Verdict |
|---|---|---|
| Fully-automated stack (embedding zero-FP ∨ R1) blocks 81% of attacks at 0% false-block, no human review. | `artifacts/exp1-structural/by-technique.json`, `by-benign.json` | deployable stack |
| R1 (untrusted source + tool call) blocks 100% of tool_abuse, output_exfiltration, indirect_injection, data_boundary_abuse at 0% false-block. | `by-technique.json` | PASS (captain-obvious) |
| R2 (sensitive-sink + non-user) is too broad: 100% false-block on high_entropy_structured_data and tool_policy_documentation, zero extra attacks → discarded. | `by-benign.json`, `verdicts.json` | rule rejected by safety bar |
| Containment lifts the detection-capped families ≥30pt (tool_abuse +67, exfiltration +53). | `verdicts.json` | PASS |
| Residual below 60% combined: prompt_leakage (needs IFC output-label), tool_result_injection (needs R1′ for tool-output), memory_poisoning (needs memory-write taint). | `verdicts.json`, report | named residual |

### Wording guardrails
- Call it the "labels-perfect ceiling"; real-world tracks labeling coverage.
- R1 is auto-blockable because it fires on structural facts, never on text meaning.
- Do not present R2-style rules as safe without per-benign measurement.
