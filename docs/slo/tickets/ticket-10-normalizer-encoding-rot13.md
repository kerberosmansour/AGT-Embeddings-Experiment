# Ticket #10 — Extend Gate-0 normalizer for encoding + rot13

Source issue: https://github.com/kerberosmansour/AGT-Embeddings-Experiment/issues/10
Target branch: `slo/issues-9-10-detection-improvements` (shared with #9)
Stack: Python 3.13 batch harness (reuses round-6 `common.py`; no new deps)

## Smallest user-visible outcome

The Gate-0 normalizer decodes more encoding/rot13 disguises, so the embedding
detector catches more of those attacks **at the same zero-false-positive
operating point**, without flagging legitimate obfuscated/structured benign data.

## Sizing gate

| Row | Value |
|---|---|
| One user-visible outcome | yes — higher encoding/rot13 catch at FP-zero |
| Changed files | 4 (`normalize.py`, new runner, new test, workpad/ticket docs) |
| Public surfaces | 1 (`normalize.normalize()` — behaviour extended, signature stable) |
| Migration | none |
| New dependency | none (stdlib `urllib.parse`, `html`, `codecs`) |
| One PR can review | yes |

Fits a single ticket.

## Compact architecture delta

`normalize.py` gains additional decode transforms inside the existing
`_decode_layers` path (depth ≤ 2, printable-ratio ≥ 0.90 acceptance guard
unchanged). New transforms: percent/URL-encoding, `\uXXXX` / `\xNN` escapes,
HTML entities (`&#NN;`, `&#xNN;`, named). The closed transform-tag enum (`TAGS`)
is extended with the new tag(s). A new measurement runner re-runs the round-6
FP-zero protocol on normalized text and emits a before/after per-bypass-class
table. No change to k, margin formula, exemplar bank, or thresholds protocol.

## Contract block

| Field | Value |
|---|---|
| Files allowed to change | `meta/harness/round6-cascade/normalize.py`; NEW `meta/harness/exp4-normalizer-plus/{run_bypass_remeasure.py, README.md}`; `meta/harness/round6-cascade/test_normalize.py` (add decode tests) |
| Files to read first | `meta/harness/round6-cascade/normalize.py`, `run_m1_gate0_rescore.py`, `common.py`; `artifacts/round6-cascade/m1-gate0/test-metrics.json` (baseline bypass table) |
| New files allowed | the runner + its README; ticket doc; lessons/completion |
| New dependencies | none (stdlib only) |
| Migration allowed | no |
| Compatibility commitments | `normalize()` signature unchanged; idempotency + determinism + plain-identity property tests stay green; existing round-6 artifacts byte-identical (the runner writes to a NEW dir, does not regenerate m1) |
| Data classification | Public (synthetic corpus, metadata-only) |
| Proactive controls | C3 Validate Input (bounded decode depth ≤2, printable-ratio guard), C8 Protect Data Everywhere (metadata-only artifacts), C9 Security Logging (structured tags) |
| Abuse scenarios | `tm-10-abuse-1`: a crafted input nests decodes to blow up output → existing 4× output cap + depth≤2 bound holds (BDD row). `tm-10-abuse-2`: a decode tag interpolates input text → tags stay a closed enum (assert) |
| Resource bounds | decode depth ≤ 2 (unchanged); output ≤ 4× input (unchanged); single-pass per transform |
| Invariants/assertions | idempotency `normalize(normalize(x))==normalize(x)`; determinism; closed tag enum membership asserted; decode-acceptance guard (≥90% printable UTF-8) applies to every new decoder |
| Debugger expectation | inspect each new decoder on one crafted + one benign sample before the full run |
| Static-analysis gates | `py_compile`; `python3 -m unittest test_normalize`; round-4 `check-round4.py` green |
| Reversibility / rollback | pure-additive transforms; revert = drop the new decode branches; runner writes to a new artifact dir only |
| Exemplar to copy | existing `_try_decode_once` / `_decode_layers` structure in `normalize.py`; `run_m1_gate0_rescore.py` FP-zero protocol |
| Anti-exemplar | do NOT decode strings containing spaces as base64 (prose guard); do NOT add a transform that mangles benign high-entropy data; do NOT loosen the printable-ratio guard |
| AI tolerance contract | ai_component: true (feeds a model detector). Accepted variance: none — deterministic decoders. Eval evidence: before/after per-bypass-class catch + benign-control FP. Retry/fallback: none. Must-never: over-decode benign structured data; raw text in artifacts. Sample budget: existing splits, one re-measure |
| Forbidden shortcuts | no decoding without the printable-ratio acceptance guard; no new tag outside the closed enum; no test-split threshold selection |

## BDD scenarios

| Scenario | Category | Given | When | Then |
|---|---|---|---|---|
| percent-encoding | happy path | `%69%67%6e%6f%72%65 all previous` | normalize | contains "ignore"; tag `percent` |
| unicode-escape | happy path | `ignore all` | normalize | "ignore"; tag `unicode_escape` |
| HTML entity | happy path | `&#105;&#103;&#110;&#111;&#114;&#101; all` | normalize | "ignore"; tag `html_entity` |
| nested encode | resource bound / `tm-10-abuse-1` | base64(percent(text)) | normalize | decodes ≤ depth 2; bounded; no error |
| benign high-entropy untouched | invalid input | random non-text high-entropy blob | normalize | NOT decoded (printable guard); original kept, tag `decode_rejected` |
| idempotency | invariant | corpus sample + random strings | `normalize(normalize(x))` | equals `normalize(x)` |
| closed tag enum | abuse `tm-10-abuse-2` | any output | tags checked | every tag ∈ `TAGS` |

## Validation plan

| Check | Command | Expected |
|---|---|---|
| Unit/property tests | `python3 -m unittest test_normalize` (in harness dir) | green incl. new decode + idempotency |
| Re-measure | `python3 meta/harness/exp4-normalizer-plus/run_bypass_remeasure.py` | before/after per-bypass-class table; FP-zero benign-control FP ~0 |
| Corpus hygiene | `python3 corpus/round4/check-round4.py corpus/round4/injection-round4-large.jsonl` | PASS |
| Compile | `python3 -m py_compile <changed files>` | clean |

## Accept / kill

- **Accept:** encoding + rot13 bypass-class catch **rises** at the FP-zero point,
  AND benign obfuscation-control FP stays ~0, AND idempotency/determinism/plain-
  identity property tests stay green.
- **Kill/flag:** if any new decoder raises benign-control FP above ~0, drop or
  tighten that decoder (report which).

## Out of scope

Multilingual; delivery-vector / Gate-0++ (HTML/Markdown/CSS/LaTeX) — separate,
gated on Experiment-2 data.
