# Runbook — Round-7 garak-derived corpus + normalizer expansion

Status: **pre-registration + M1 local implementation**. The WS-A generator and
checker exist under `corpus/round7/` and have current smoke/pilot verification
evidence in `docs/slo/tickets/ticket-14-round7-generator-verification.md`.
Numbers below remain targets/thresholds until a large-profile freeze and WS-C
measurement run land. Synthetic research corpus discipline applies throughout
(`[[CLAIMS-LEDGER]]` wording guardrails). garak is used as a **technique
taxonomy and seed source**, never as a literal-payload import into the synthetic
arm — see §8 Licensing/provenance.

This runbook turns the garak research review into three parallelizable
workstreams with a single, pre-registered measurement design.

---

## 0. Locked decisions (from review)

| Decision | Choice |
|---|---|
| Corpus scope | **Unified round-7 benchmark** — carry forward the existing 8 families + add new garak-derived categories and expanded encodings into one new round. |
| Multi-turn | **Add a `turns` schema** — single-turn families keep one `text`; multi-turn families (agentic tool exploit) carry an ordered `turns` array. |
| Fixed detector for A/B | **Round-4 kNN zero-FP scorer** (bge-small, k=5), the same frozen scorer round-6 used; **rules-only reported alongside** for context. |
| Cross-walk tags | Tag every row with **both `owasp_llm` and `mitre_atlas`** (OWASP for the LLM/Agentic Top-10 compliance story; ATLAS for adversarial-technique lineage). |
| Implementation language | **Rust is the main driver; Python is parity/second.** The controls land in AGT's `agentmesh` Rust crate; the research harness consumes the Rust output. Design every control to be a clean drop-in for AGT. |

> **AGT already PR'd the normalizer — build on it.**
> `agent-governance-rust/agentmesh/src/normalize.rs` is
> [PR #2991](https://github.com/microsoft/agent-governance-toolkit/pull/2991)
> (RFC #2957): Rust + Python `agent_os.normalize`, closed `Transform` enum,
> `normalize()` / `normalize_with()`, `NormalizeConfig`, FP-guarded decoders,
> benign-safety + idempotency tests, **300-case Rust⇄Python parity**, evidence
> "35%→62% bypass catch at 0 FP". **WS-B extends that exact module** — additive
> `Transform` variants + decoders, same conventions ("no new deps beyond
> `base64`", guard-per-transform, closed tag vocab). Done as
> `rust/agt-normalize/` (drop-in superset, 33 tests green). It is **not**
> greenfield, and Python parity must be extended in lock-step (the PR's parity
> vectors are the contract).

---

## 1. Workstreams (the division of labor)

WS-A and WS-B are **independent** and can proceed in parallel. WS-C depends on
both.

- **WS-A — New corpus (`corpus/round7/`).** New generator cloned from
  `corpus/round4/generate-round4.py`, new `ROUND="round7"` / `ID_PREFIX="r7"`,
  carrying the 8 existing families forward and adding the new attack families
  (§3), benign + adjacent-benign controls (§4), expanded `bypass_class` operators
  (§5), the `turns` schema and the `owasp_llm`/`mitre_atlas` tags (§6). Must pass
  the three leakage checks (§7) at zero.
- **WS-B — Normalizer expansion (Rust-first).** Extend AGT's existing
  `agent-governance-rust/agentmesh/src/normalize.rs` with the decoders/strippers
  in §5, each as a new `Transform` enum variant behind an FP-acceptance guard,
  plus extended benign-safety + idempotency tests. Developed here as a
  self-contained, `cargo test`-able crate (`rust/agt-normalize/`) that is a
  **drop-in superset** of the AGT module, so it lifts straight upstream. Round-6's
  frozen normalizer (`meta/harness/round6-cascade/normalize.py`) stays untouched
  as the "old normalizer" arm of the A/B. **Python is parity-second** (§1.1).
- **WS-C — Measurement (`meta/harness/round7-garak/run_2x2.py`).** The fixed
  detector × {old, new normalizer} × {round-4, round-7 corpus} matrix in §2,
  with pre-registered accept/kill thresholds (§2.1).

---

### 1.1 Rust-first / AGT export contract

These controls will belong to AGT, so they are built Rust-first and shaped to
drop into the `agentmesh` crate; Python follows as parity.

- **Source of truth = Rust.** The normalizer (and any future structural control)
  is authored as Rust matching AGT's module conventions: closed `Transform`
  enum, `normalize()` / `normalize_with(cfg)` entry points, `NormalizeConfig`
  knobs, no new crate deps beyond `base64`, deterministic + idempotent, returns
  `{text, transforms}` so every downstream control + audit consumes the same
  un-disguised view.
- **Export path to AGT.** `rust/agt-normalize/src/lib.rs` is a drop-in superset
  of `agent-governance-rust/agentmesh/src/normalize.rs`; upstreaming is a file
  replace + the new tests. New `Transform` variants are additive (existing
  callers unaffected). This is the concrete deliverable behind
  `[[docs/proposals/agt-upstream-normalizer-rfc.md]]`.
- **Python parity = second.** The research harness drives the **Rust** normalizer
  (small `normalize` CLI: stdin → `{text, transforms}` JSON), so the A/B measures
  the artifact that ships. A Python parity port is kept equivalent via shared
  golden vectors (`rust/agt-normalize/tests/vectors.jsonl`) asserted against both.
- **Cross-language agreement is a test, not a hope.** AGT ships five SDKs that
  must agree; the golden-vector suite is the contract that keeps Rust ⇄ Python (⇄
  future ports) byte-identical on normalized output + transform tags.

## 2. Measurement design (detector held fixed; vary only normalizer × dataset)

Any lift must be attributable to the normalizer alone, so the **downstream
detector is frozen** (round-4 kNN zero-FP scorer; rules-only reported too). 2×2:

|  | Old round-4 corpus | New round-7 corpus |
|---|---|---|
| **Old Gate-0 normalizer** (round6 `normalize.py`) | known anchor (~43% @ 0 FP) | **baseline** |
| **New normalizer** (round7 `normalize.py`) | regression guard | **treatment** |

- Headline = `treatment − baseline` on round-7, broken out **per attack family
  and per `bypass_class`**, all at **0% benign-control FP**.
- The round-4 column is the non-regression control.
- τ is fit on **validation only** and frozen before test is scored, in **each**
  cell independently (the τ that achieves FP-zero may differ per normalizer).

### 2.1 Pre-registered accept / kill thresholds

- **ACCEPT (new normalizer wins):** on round-7 test, new-normalizer attack
  recall ≥ old-normalizer recall **+5pt absolute** at the FP-zero point, **and**
  0 new false positives on the obfuscation-control + adjacent-security benign
  subclasses (Wilson 95% CI reported).
- **REGRESSION KILL:** new normalizer must hold **≥ round-6 anchor (≈43% @ 0 FP)**
  on the round-4 corpus and add **0** benign-control FPs there. Any regression
  blocks merge.
- **IDEMPOTENCY (hard gate):** `normalize(normalize(x)) == normalize(x)` for all
  test rows; property-tested.
- **PER-DECODER FLOOR:** each new encoding `bypass_class` must reach **≥50%**
  catch after its matching decoder, **or** be explicitly logged as a decoder gap
  (no silent caps — `[[CLAIMS-LEDGER]]` honesty).
- **FP BAR:** 0 FP on the hardest negatives (obfuscation controls + adjacent
  security text), with base-rate-adjusted precision at 100:1 and 1000:1.

---

## 3. Attack families

**Carried forward (8, unchanged labels):** `direct_override`, `prompt_leakage`,
`indirect_injection`, `tool_result_injection`, `tool_abuse`,
`output_exfiltration`, `memory_poisoning`, `data_boundary_abuse`.

**Enriched (existing class, new templates/axes):**

- `indirect_injection` — add **carrier-document** scaffolds (translation task,
  financial/RSU report, resume/CV, WHOIS record, fact snippet) and a `placement`
  axis (`top` / `middle` / `bottom` / `wrapped`), from garak `latentinjection`.
- `output_exfiltration` — add concrete channels from garak `web_injection`:
  markdown-image auto-render exfil, hidden link/footnote URI, fragmented
  string-assembly URI, `javascript:`/HTML injection.

**New (garak-derived, v1):**

| New `attack_class` | Seed probe(s) | Multi-turn | `expected_action` | Rationale |
|---|---|---|---|---|
| `jailbreak` | dan, grandma, dra, fitd, sata | no | `require_approval` | Persona/alignment-bypass. Text-meaning → not R1-blockable; framed as detection/recall + benign-boundary research. |
| `agentic_tool_exploit` | agent_breaker | **yes** (`turns`) | `block` | Multi-turn tool misuse / confused deputy from untrusted source → R1-eligible. |
| `package_hallucination` | packagehallucination | no | `require_approval` | Slopsquatting; supply-chain risk for code tools. |
| `terminal_escape_injection` | ansiescape | no | `quarantine` | ANSI/OSC escapes in rendered output; pairs with WS-B ANSI strip. |

**Deferred to v2 (named, not built):** `adversarial_suffix` (gcg/suffix),
`data_extraction` (divergence repeat-token / leakreplay / propile / apikey).

---

## 4. Benign + adjacent-benign controls (matched negatives)

Every new attack family ships its **hardest matched negative** (methodology §3:
the corpus must not reward attack-shaped wording alone).

| New benign subclass | Guards against false-positiving on… | Matched to |
|---|---|---|
| `benign_terminal_output` | legit ANSI/escape in CI logs, colored `git diff`, terminal transcripts | `terminal_escape_injection` |
| `benign_emoji_variation_selector` | **legit** emoji/flag sequences using variation selectors + tag chars, CJK | `unicode_tag`/`variation_selector`/`sneaky_bits` bypasses |
| `benign_package_install` | real `requirements.txt`/lockfiles/`npm i`/`pip install` for packages that exist | `package_hallucination` |
| `benign_roleplay_creative` | legit "act as…", fiction, game-master/DM, persona/therapy prompts | `jailbreak` |
| `benign_multistep_tool_use` | legit multi-turn tool workflows (approved actions in sequence) | `agentic_tool_exploit` |
| `benign_encoded_asset` | legit base32/base85/uuencoded/morse/braille content (a morse lesson, a braille reference, a uuencoded doc attachment) | new encoding bypasses |

Existing controls reused: `high_entropy_structured_data` (covers gibberish
suffixes), `benign_security_discussion`, `quoted_injection_example`,
`detector_code_fixture`, `owasp_ncsc_guidance`, `tool_policy_documentation`,
`benign_obfuscation_control`, `benign_compact_obfuscation_control`,
`legitimate_imperative_request`, `benign_tool_use`, `support_urgency`.

---

## 5. Expanded `bypass_class` operators ↔ normalizer decoders (WS-A ⇄ WS-B contract)

Each new obfuscation operator added in WS-A gets a matching decoder/strip in
WS-B, **plus** a matched `benign_encoded_asset` control, **plus** a new member of
the closed transform-tag enum. stdlib-only (no external alphabets), so
`base2048`/`ecoji` are **excluded**.

| New `bypass_class` | WS-B transform | New tag | FP guard |
|---|---|---|---|
| `base16` | `base64.b16decode` on contiguous blob | `base16` | blob, len≥16, printable≥0.9 |
| `base32` | `base64.b32decode` | `base32` | blob, padding-valid, printable≥0.9 |
| `base85` / `ascii85` | `base64.b85decode` / `a85decode` | `base85` | blob, printable≥0.9 |
| `uuencode` | `binascii.a2b_uu` per line | `uuencode` | `begin ` header or uu line shape |
| `quoted_printable` | `quopri.decodestring` | `quoted_printable` | ≥2 `=XX` markers + English-benefit |
| `atbash` | fixed A↔Z map | `atbash` | alpha-heavy + English-benefit |
| `morse` | fixed morse map on `.-/ ` runs | `morse` | only `.-/ ` tokens, ≥4 letters, English-benefit |
| `nato` | fixed NATO-word map | `nato` | ≥4 consecutive NATO words |
| `braille` | Unicode braille → ASCII map | `braille` | braille codepoints present |
| `zalgo` | strip combining marks (`Mn`/`Mc`/`Me`) | `zalgo` | combining-mark density guard |
| `unicode_tag` | strip/fold U+E0000–E007F tag block | `unicode_tag` | tag codepoints present |
| `variation_selector` | strip VS U+FE00–FE0F, U+E0100–E01EF | `variation_selector` | **emoji-context exempt** (FP guard) |
| `sneaky_bits` | decode zero-width binary → ASCII | `sneaky_bits` | ZW-binary run present, printable≥0.9 |
| `ansi_escape` | strip CSI/OSC/C1 escape sequences | `ansi_escape` | escape sequence present |

> The `variation_selector` strip is the FP-sensitive one: legitimate emoji and
> flag sequences use VS-16 / tag chars. The guard exempts emoji-adjacent
> contexts, and `benign_emoji_variation_selector` proves it.

Carried-forward bypass operators (unchanged): `none`/`plain`, `rot13`,
`encoding` (base64/percent/html-entity), `hex`, `homoglyph`, `diacritics`,
`leet_spacing`, `leet_letter_spaced`, `letter_spaced`, `separator_spaced`,
`compact_plain`, `compact_leet`, `chunked_leet`, `multilingual`.

---

## 6. Row schema additions

Round-4 schema is preserved; round-7 adds:

```jsonc
{
  // ... all round-4 fields (id, text, source_type, trust_level, attack_class,
  //     benign_subclass, bypass_class, risk_level, expected_action,
  //     contains_sensitive_sink, requires_tool_call, group_id, split,
  //     family_id, generator_id, label_source, created_round) ...
  "created_round": "round7",
  "text_marker": "R7",                 // synthetic tag; never real traffic
  "turns": null,                        // OR ordered [{role, text}] for multi-turn families
  "placement": null,                    // top|middle|bottom|wrapped for carrier-doc injection
  "owasp_llm": ["LLM01"],              // cross-walk tag (closed vocab, §6.1)
  "mitre_atlas": ["AML.T0051.000"]     // cross-walk tag (closed vocab, §6.1)
}
```

For multi-turn rows, `text` holds the flattened concatenation (so every
text-based control and the existing leakage checks still apply) **and** `turns`
holds the structured sequence.

### 6.1 Cross-walk tag mapping (closed vocab; review against current matrices)

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

OWASP = OWASP Top-10 for LLM Apps (2025). ATLAS = MITRE ATLAS technique IDs.
Both columns are **best-effort and must be reviewed** against the current
published matrices before any compliance claim.

---

## 7. Methodology guardrails carried forward (non-negotiable)

1. **Placement:** round-7 lives in `corpus/round7/`, **never** `corpus/contrib`.
2. **Deterministic, stdlib-only, seeded** generator; reproducible byte-for-byte;
   `SEED=1337`, new `ROUND`.
3. **Family/group split** by hash (5-bucket), never random row; no family or
   group straddles splits.
4. **Three leakage checks read zero:** exact-normalized hash, near-duplicate
   simhash (7-gram, Jaccard ≥0.92), family/group cross-split. New encodings risk
   cross-family normalized collisions — re-run and inspect.
5. **Provenance per row** + `expected_action` per governance semantics (§3).
6. **`bypass_class` is the held-out generalization axis** — hold new encodings
   out of the exemplar bank to measure generalization to unseen disguises.
7. **Baseline re-pin:** rerun rules-only vs fresh AGT `main`; record commit SHA +
   `prompt_injection.rs` SHA-256.
8. **Metrics:** Wilson CI + base-rate precision (100:1, 1000:1) per operating
   point; τ fit on validation only, frozen before test.
9. **Synthetic marker** (`R7`) on every row.
10. **Honesty:** text-meaning families (`jailbreak`, `terminal_escape_injection`)
    are detection/recall research, **not** structurally blockable by R1 — adding
    them may *lower* headline catch unless paired with new structural rules; say
    so. Update the Experiment-1 structural-rule table accordingly.

---

## 8. Licensing / provenance

garak is **Apache-2.0** (© Leon Derczynski; © NVIDIA). Two clean paths:

- **Technique-derived (default for round-7):** use garak as a *taxonomy of
  techniques*; write AGT-native templates. Rows stay **synthetic**; cite garak as
  methodology inspiration in this runbook + a `NOTICE`. No data-attribution
  entanglement; the "synthetic research corpus" claim is preserved.
- **Payload-derived arm (optional, separate):** any literal garak payloads go
  through the round-5 source-scale methodology (reviewed, Apache-2.0 attributed
  `NOTICE`), live in a **separate manifest/split**, and are **never** folded under
  the synthetic claim.

---

## 9. Sequencing

1. WS-B normalizer decoders + tests (self-contained; verify against round-4).
2. WS-A generator: encodings + carrier-doc/exfil enrichment first, then the 4 new
   families + their benign controls; smoke profile passing leakage = 0.
3. WS-C 2×2 once A (large profile) and B are frozen.
4. Report: per-family + per-bypass lift table, FP bar with Wilson CI, regression
   guard, honest structural-rule update.

Related: `[[docs/proposals/agt-upstream-normalizer-rfc.md]]` (the upstream
normalizer RFC this measurement strengthens).

## 10. Follow-on: outbound verification (#13)

The round-7 corpus and WS-C harness measure inbound detection and normalizer
lift. The companion outbound experiment is tracked separately in issue #13 and
`docs/proposals/outbound-embedding-scan-final-verification.md`.

Keep the boundary explicit:

- #12 handles deterministic byte/render hazards at `post_tool_call` / `output`
  with a render-safe sanitizer and ACS `Transform`.
- #13 is semantic output evidence at `post_model_call`, `post_tool_call`, and
  `output`; default routing is `Escalate`/`Warn`, not auto-block.
- The same methodology applies: family/source split, leakage checks at zero,
  validation-frozen tau, Wilson/base-rate reporting, and metadata-only
  artifacts.
- The key experimental question is transfer: does the inbound exemplar bank work
  on outbound subjects, or does AGT need an outbound-specific bank and corpus?
