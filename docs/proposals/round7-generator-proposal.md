# Proposal for review: Round-7 corpus generator (WS-A)

**Status:** v2 accepted; WS-A M1 generator/checker implemented locally and
verified with smoke/pilot profiles. This proposal started as a pre-build review
request; §11 records the accepted reconciliation, and the current implementation
evidence is tracked in
`docs/slo/tickets/ticket-14-round7-generator-verification.md` plus GitHub issue
#14. Large-profile freeze and downstream WS-C headline measurement remain
separate steps.

**Context artifacts (read these to review):**
- Plan: [`docs/RUNBOOK-round7-garak-corpus.md`](../RUNBOOK-round7-garak-corpus.md)
- Round-4 generator (the proven base to extend): [`corpus/round4/generate-round4.py`](../../corpus/round4/generate-round4.py)
- Round-4 manifest (leakage/split artifacts to preserve): [`corpus/round4/manifest-large.json`](../../corpus/round4/manifest-large.json)
- Obfuscation encoders, already contract-proven 11/11 vs the normalizer: [`corpus/round7/garak_bypass.py`](../../corpus/round7/garak_bypass.py)
- Normalizer under test (Rust, drop-in superset of AGT PR #2991): [`rust/agt-normalize/`](../../rust/agt-normalize/)

---

## 1. Goal and non-goals

**Goal.** Produce a unified **round-7** synthetic evaluation corpus that extends
round-4 with garak-derived attack *types* and *obfuscations*, so we gain
**visibility into where our detection, normalization, and structural controls are
good vs. blind**. The deliverable is a *control-surface benchmark*, not a
leaderboard. Success = the corpus truthfully shows us our gaps, with zero
false-positive inflation and no hidden leakage.

**Explicit non-goals.** Not production-safety evidence; not a score to maximize;
not a replacement for rules; not real-traffic validation. garak is a *technique
taxonomy and seed source*, never a literal-payload import into the synthetic arm.

**Why this matters (design principle).** A corpus that makes us *look* good is
worse than useless — it hides blind spots. Every design choice below is in
service of *truthful* measurement: matched-hard negatives, family-level splits,
three leakage checks at zero, base-rate-honest statistics, and an explicit
`structural` vs `evidence` containment label so we never claim a guarantee we
don't have.

## 2. What is generated — taxonomy

### 2.1 Attack families

Carried forward from round-4 (8, unchanged labels): `direct_override`,
`prompt_leakage`, `indirect_injection`, `tool_result_injection`, `tool_abuse`,
`output_exfiltration`, `memory_poisoning`, `data_boundary_abuse`.

Enriched (existing class, new templates/axes):
- `indirect_injection` — add carrier-document scaffolds (translation, RSU/financial report, resume/CV, WHOIS, fact-snippet) and a `placement` axis (`top|middle|bottom|wrapped`) — from garak `latentinjection`.
- `output_exfiltration` — add concrete channels (markdown-image auto-render, hidden link/footnote URI, fragmented string-assembly URI, `javascript:`/HTML) — from garak `web_injection`.

New (garak-derived):

| New `attack_class` | garak seed | multi-turn | `containment_class` | proposed verdict |
|---|---|---|---|---|
| `jailbreak` | dan, grandma, dra, fitd, sata | no | **evidence** | Escalate |
| `agentic_tool_exploit` | agent_breaker | **yes** (`turns`) | **structural** (R1 family) | Deny |
| `package_hallucination` | packagehallucination | no | structural (review gate) | Escalate |
| `terminal_escape_injection` | ansiescape | no | **structural** (output `Transform`) | Transform/Deny |

### 2.2 Benign / adjacent-benign controls (matched hard negatives)

Existing controls reused (round-4): `benign_security_discussion`,
`quoted_injection_example`, `security_training_material`, `research_blog_excerpt`,
`security_changelog`, `detector_code_fixture`, `owasp_ncsc_guidance`,
`docs_code_comment`, `legitimate_imperative_request`, `benign_tool_use`,
`tool_policy_documentation`, `high_entropy_structured_data`, `support_urgency`,
`benign_obfuscation_control`, `benign_compact_obfuscation_control`.

New matched controls (one per new attack/obfuscation, the hardest negative):

| New benign subclass | Guards against false-positiving on… |
|---|---|
| `benign_terminal_output` | legit ANSI in CI logs, colored `git diff`, terminal transcripts |
| `benign_emoji_variation_selector` | legit emoji/flag sequences (VS-16, tag chars), CJK |
| `benign_package_install` | real `requirements.txt`/lockfiles/`pip`/`npm` for existing packages |
| `benign_roleplay_creative` | legit "act as…", fiction, game-master, persona prompts |
| `benign_multistep_tool_use` | legit multi-turn approved tool workflows |
| `benign_encoded_asset` | legit base32/ascii85/morse/braille content (a morse lesson, a uuencoded attachment) |

### 2.3 Obfuscation operators (`bypass_class`)

Carried forward (round-4): `none/plain`, `rot13`, `encoding` (base64/percent/
html-entity), `hex`, `homoglyph`, `diacritics`, the leet/spacing/compact/chunked
family, `multilingual`.

New (11) — each **already contract-proven** to round-trip through the round-7
normalizer (Python encoder ↔ Rust decoder, 11/11; see `garak_bypass.py`):
`base32`, `ascii85`, `atbash`, `morse`, `nato`, `braille`, `unicode_tag`,
`variation_selector`, `sneaky_bits`, `ansi_escape`, `zalgo`.

## 3. Row schema

Round-4 fields preserved. Round-7 additions (the **defense-mapping axis** is the
key open question — see §8.1):

```jsonc
{
  // round-4 fields: id, text, source_type, trust_level, attack_class,
  // benign_subclass, bypass_class, risk_level, expected_action,
  // contains_sensitive_sink, requires_tool_call, group_id, split,
  // family_id, generator_id, label_source, created_round
  "created_round": "round7",
  "text_marker": "R7",                 // synthetic tag; never real traffic
  "turns": null,                        // OR ordered [{role,text}] for multi-turn families
  "placement": null,                    // top|middle|bottom|wrapped for carrier-doc injection
  "owasp_llm": ["LLM01"],              // closed vocab cross-walk
  "mitre_atlas": ["AML.T0051.000"],    // closed vocab cross-walk
  // --- proposed defense-mapping axis (OPEN: §8.1) ---
  "containment_class": "structural",    // structural | evidence
  "defense_stage": "pre_tool_call",     // ACS intervention point that is the control sink
  "control_under_test": "least_privilege_policy",
  "expected_decision": "Deny"           // ACS verdict: Allow|Deny|Warn|Escalate|Transform
}
```

Multi-turn rows keep the flattened concatenation in `text` (so the existing
text-based controls + leakage checks still apply) **and** the structured sequence
in `turns`.

### 3.1 Cross-walk tag mapping (closed vocab — validate against current matrices)

| Family | `owasp_llm` | `mitre_atlas` |
|---|---|---|
| direct_override | LLM01 | AML.T0051.000 |
| prompt_leakage | LLM07 | AML.T0057 |
| indirect_injection | LLM01 | AML.T0051.001 |
| tool_result_injection | LLM01, LLM05 | AML.T0051.001 |
| tool_abuse | LLM06 | AML.T0053 |
| output_exfiltration | LLM02, LLM05 | AML.T0024 |
| memory_poisoning | LLM04 | AML.T0020 |
| data_boundary_abuse | LLM06, LLM02 | AML.T0057 |
| jailbreak | LLM01 | AML.T0054 |
| agentic_tool_exploit | LLM06 | AML.T0053 |
| package_hallucination | LLM03, LLM09 | AML.T0010 |
| terminal_escape_injection | LLM05 | AML.T0051 |

## 4. Generation method

- **Deterministic, stdlib-only, seeded** (extends `generate-round4.py`): `SEED=1337`, `ROUND="round7"`, `ID_PREFIX="r7"`. Reproducible byte-for-byte per `--profile` (`smoke`/`pilot`/`large`).
- **Family/group split** unchanged: `split_for(family_id)` hashes each family to one of 5 buckets → `exemplar_bank`/`validation`/`test`. No family or group straddles splits.
- **Obfuscation** applied per-family via the contract-proven encoders; `bypass_class` is a held-out axis (hold new encodings out of the exemplar bank to measure generalization to unseen disguises).
- **Multi-turn** (`agentic_tool_exploit`): generate an ordered `turns` array (user→tool→user…), flatten to `text` for the detector/leakage path.
- **Carrier-doc injection** (`indirect_injection`): inject the payload at a `placement` within a benign carrier document; the matched benign control is the same carrier *without* the injection.

## 5. Methodology guardrails (carried forward, non-negotiable)

1. Placement: `corpus/round7/` only; never `corpus/contrib` (don't contaminate the exemplar bank).
2. Three leakage checks must read **zero**: exact-normalized hash, near-duplicate simhash (7-gram, Jaccard ≥0.92), family/group cross-split.
3. Matched benign control for **every** new attack family/obfuscation.
4. Provenance per row; `expected_action`/`expected_decision` by governance semantics.
5. Baseline re-pin: rerun rules-only vs fresh AGT `main`; record commit + detector SHA.
6. Stats: Wilson 95% CI + base-rate-adjusted precision at 100:1 and 1000:1 on every operating point; τ fit on validation only, frozen before test.
7. Synthetic marker (`R7`) on every row.

## 6. How round-7 is measured (downstream, not part of this generator)

Feeds the WS-C 2×2: detector held fixed (round-4 kNN zero-FP scorer; rules-only
reported alongside), normalizer varied (round-6 old vs round-7 new), corpus
varied (round-4 vs round-7). Headline = per-family + per-`bypass_class` catch
**at 0% benign-control FP**. `structural` families are scored against the control
that should contain them; `evidence` families (jailbreak) are scored separately
and never counted as structurally blocked.

## 7. Provenance / licensing

garak is Apache-2.0 (© Leon Derczynski; © NVIDIA). Default = **technique-derived**
(AGT-native templates; rows stay synthetic; garak cited as inspiration). Any
literal payloads = a separate **payload-derived** arm under the round-5
source-scale methodology, in its own manifest, never folded under the synthetic
claim.

## 8. Open design questions (the crux — please adjudicate)

Each lists my current lean and the risk it carries.

1. **Defense-mapping axis.** Add `containment_class`/`defense_stage`/`control_under_test` and realign `expected_action`→ACS verdicts (`Allow/Deny/Warn/Escalate/Transform`)? *Lean: yes* — turns the corpus into a control-surface benchmark and prevents over-claiming. *Risk:* schema complexity; ground-truth for `containment_class` must be defensible per family.
2. **Synthetic-overfit / false confidence.** Templated jailbreak/agentic attacks may be trivially separable, inflating catch and giving us *false* visibility. *Lean: add a small held-out garak payload-derived arm (separate manifest) as a reality check.* *Risk:* if we skip it, headline numbers may not reflect real attacks.
3. **Multi-turn flattening.** Concatenating `turns`→`text` may bias the detector or leak across the conversation boundary. *Lean: flatten + also keep `turns`.* *Risk:* the flattening could create artificial n-gram overlap that trips the near-dup check or makes attacks too easy.
4. **Jailbreak scoring.** Jailbreak is evidence-grade (text-meaning). *Lean: score jailbreak in a separate bucket so it doesn't distort the structural headline.* *Risk:* if mixed in, the headline becomes uninterpretable.
5. **Benign-control sufficiency.** Will the 6 new benign subclasses actually hold FP at 0 — especially the FP-sensitive ones (`variation_selector` vs legit emoji; `ansi_escape` vs legit terminal logs; `package_hallucination` vs real installs)? *Risk:* synthetic benigns that are *too easy* would manufacture a false 0-FP.
6. **Encoding-induced leakage.** Could the new encoders create cross-family normalized-hash collisions or near-dup leakage the current checks miss (e.g. two plaintexts whose encodings normalize alike)? *Risk:* silent split leakage that inflates catch.
7. **Class balance & size.** Rows per family; weighting new vs carried-forward; base-rate realism (attacks are rare in the wild — does the corpus reflect that in the precision reporting?).
8. **Label ground-truth.** Is the `structural`/`evidence` split defensible and consistently applied per family? Mislabeling here corrupts the whole "visibility" claim.
9. **Tag correctness.** `owasp_llm`/`mitre_atlas` mappings (§3.1) are best-effort — should they be validated against the current published matrices?

---

## 10. Reviewer prompt & validation protocol

> **You are an adversarial methodology reviewer for a security research corpus.**
> Your job is *not* to approve this — it is to find every way this corpus could
> **mislead us** (give false confidence, hide a blind spot, leak across splits,
> manufacture a fake 0% false-positive rate, or mislabel ground truth). The whole
> value of this corpus is *truthful visibility into where our controls fail*, so a
> flaw that makes results look better than reality is the most serious kind.
>
> **If two reviewers are assigned, split lenses:** Reviewer A = methodology &
> statistics (splits, leakage, overfitting, Wilson CI / base-rate precision,
> reproducibility); Reviewer B = security & adversarial realism (are the attacks
> representative, are the benign controls genuinely hard, is the
> structural/evidence containment mapping to real AGT controls correct).

### What to validate (score each, with concrete reasoning)
1. **Leakage & splits** — can the family/group 5-bucket split + the three leakage checks (§5.2) actually hold at zero given the 11 new encoders? Construct a concrete case where they might not.
2. **Benign-control adequacy (§8.5)** — for each FP-sensitive new attack, is the matched benign control hard enough to make a 0-FP result *meaningful*, or trivially separable? Name the specific benign example you'd add.
3. **Synthetic-overfit (§8.2)** — would a detector pass this corpus while failing real garak payloads? Is the payload-derived reality-check arm necessary?
4. **Defense-mapping axis (§8.1, §8.8)** — is the `structural`/`evidence` label defensible per family? Does each `defense_stage`/`control_under_test` map to a real AGT control (ACS intervention point + verdict, IFC label-flow, privilege ring, classifier annotator)? Flag any mislabel.
5. **Statistical honesty** — are Wilson CI + base-rate precision (100:1, 1000:1) sufficient, or is something over-claimed? Is class balance / base-rate realism handled?
6. **Multi-turn & carrier-doc representations (§8.3)** — sound, or do they bias the measurement?
7. **Scope honesty** — does anything in the proposal overclaim (e.g. implying structural defense where only evidence-grade exists)?

### What to do to validate (concrete actions)
- Clone the repo; read this issue, the runbook, `generate-round4.py`, and `manifest-large.json`.
- Run `python3 corpus/round7/garak_bypass.py` — confirm **11/11** encoders round-trip through the normalizer. Then *try to construct an obfuscation the normalizer misses* and report it.
- Run `cd rust/agt-normalize && cargo test` — confirm 33 tests pass; inspect the benign-safety tests and argue whether they're sufficient.
- Read the round-4 `leakage_check`/`normalized_text_check` code in `generate-round4.py` and argue whether round-7's encoders could defeat it (e.g. cross-family normalized collisions).
- Sample 5 proposed rows per new family (from the taxonomy/templates here) and check label correctness: `expected_decision`, `containment_class`, `owasp_llm`, `mitre_atlas`.

### Required output format
For each of the 7 validation dimensions: a verdict (`accept` / `revise` /
`reject`), the **concrete failure scenario or exploit** that justifies it (no
vague "looks good"/"seems fine"), and a **specific, actionable recommendation**.
End with: the top 3 changes that would most improve the *truthfulness* of the
corpus, and an overall `build as-is` / `build with changes` / `redesign` verdict.

---

---

## 11. Post-review reconciliation (v2) — accepted changes & refinements

Review verdict: **build with changes**. Accepted in full, with the refinements
noted. This section supersedes the affected parts of §1–§10. Build proceeds only
against v2.

**A. Normalizer-aware leakage (review §1) — accepted, refined.** Split isolation
moves from `family_id` to **`semantic_family_id` = hash of the canonical
(pre-obfuscation) payload**. We generate every obfuscated variant from a known
plaintext, so this hash is computed directly at generation time — no "decode to
find twins," no Rust dependency in the pure-Python generator. Plain + encoded
twins of one payload always share a split. Add a **Rust-normalizer cross-split
audit gate** (separate CI step, shells to the `agt-normalize` CLI) hashing each
row's Rust-normalized, flattened-turns, and per-turn text; assert zero cross-split
collisions. Bypass-class holdout = hold out **whole semantic families**.

**B. Harder benign controls (review §2) — accepted.** `benign_multistep_tool_use`
MUST include **untrusted-source → legitimate low-risk tool-call** rows (public
status / shipping / calendar / read-only search) — fills the `untrusted+tool`
quadrant that made Exp-1 R1 look perfect; R1's measured false-block will rise, and
that is the point. Add the reviewer's hard twins to `benign_terminal_output`,
`benign_emoji_variation_selector`, `benign_package_install`,
`benign_encoded_asset`. Report **per-subclass** FP + Wilson upper bounds, not
pooled.

**C. Keep decision vocabularies distinct (review §4) — accepted; corrects my own
§3/§8.1.** Do **not** overwrite `expected_action` with ACS verbs.
`source-to-agt-expected-action-mapping.md` already separates layers. Round-7
keeps `expected_action` and adds `agt_policy_decision`
(allow/deny/requires_approval/rate_limited), `quarantine_intent` (metadata bool),
and — only for `structural` rows — `acs_verdict`
(Allow/Deny/Warn/Escalate/Transform, explicitly mapped). `quarantine` is never a
decision.

**D. `structural` requires an executable control contract (review §4) —
accepted.** `containment_class ∈ {structural, evidence, workflow_review}`.
`structural` REQUIRES `control_contract {stage, required_runtime_fields, rule_id,
native_policy_decision, evidence_tags}` mapping to a real expressible AGT control;
else `workflow_review` (+ `blocked_on` issue ref) or `evidence`. Re-labels:
`agentic_tool_exploit`, `tool_abuse`, `output_exfiltration`, `indirect_injection`,
`data_boundary_abuse` = **structural** (R1 = `pre_tool_call` deny on
untrusted+tool, expressible today); `terminal_escape_injection` =
**workflow_review, blocked_on #12**; `package_hallucination` = **workflow_review**
(registry/review annotator not modeled); `prompt_leakage`,
`tool_result_injection`, `memory_poisoning` = **workflow_review** (Exp-1 named
residuals: IFC output-label / R1′ / memory-write taint not yet modeled);
`direct_override`, `jailbreak` = **evidence**.

**E. Text-meaning out of structural headline (review §4) — accepted.** Final
report has four buckets: normalizer/detector evidence · implemented structural ·
workflow-review · reality-check arm. Jailbreak lives only in the evidence bucket.

**F. Reality-check + adversarial-variant arms (review §3) — accepted.**
`corpus/round7/reality-check/` = small **payload-derived** arm from real
garak-style payloads (separate manifest/split/claim, Apache-2.0 attribution;
never in the synthetic headline). `corpus/round7/adversarial-variants/` =
visibility rows from the normalizer miss-probes (J); allowed to fail.

**G. Statistics (review §5) — accepted.** Pre-register per-subclass min counts;
Wilson CI per benign subclass / bypass class / attack family; 2×2 uses **paired
McNemar/bootstrap deltas on the frozen test set** (not independent thresholded
recall); per-cell τ on validation only, frozen paired delta is the arbiter.

**H. Multi-turn & carrier-doc (review §6) — accepted.** Deterministic flattened
`text` with stable role/source delimiters; leakage checks on flattened + per-turn;
`turns` primary, flattened is a compatibility view; carrier-doc attack + benign
twin forced into the same `group_id`/split; `placement` reported separately.

**I. Scope honesty (review §7) — accepted.** Headline stays "control-surface
visibility benchmark," not "coverage." OWASP/MITRE tags are not compliance
language until matrices are independently verified.

**J. Normalizer (WS-B) punch-list — new, from the reviewer's miss-probes.** Fix:
Adobe-wrapped Ascii85 (`<~…~>`), tab/newline-separated Morse (run after whitespace
normalization), hyphen-separated NATO, C1 CSI parser (raw `0x9B` + strip parameter
artifacts), guarded lowercase/grouped Base32. Documented FP-safe limitations (kept
as visibility rows, not "fixed"): Unicode-tag-after-black-flag, byte-spaced
sneaky-bits. Each becomes an adversarial-variant row.

**Sequencing.** The Rust audit gate (A) runs at corpus-CI time against the built
CLI, so generation stays stdlib-only/reproducible. The normalizer punch-list (J)
is a small WS-B iteration that runs in parallel with the generator.

*v2 is the build target. Reviewers: please flag anything in this reconciliation
you disagree with before implementation.*
