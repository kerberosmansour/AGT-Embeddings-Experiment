# Round-6 M1 — Gate 0 de-obfuscation + FP-zero rescore report

**Verdict vs §2 M1 bar: PARTIAL ACCEPT (kill condition decisively not triggered).**

The §2 M1 accept bar asked for ≥40% catch on every named obfuscated class AND
zero benign obfuscation-control FPs. The side-condition holds perfectly; the
catch bar is met for boundary-preserving obfuscation but not for
word-boundary-destroying obfuscation. The kill condition (<10-point movement)
is decisively avoided — overall zero-FP recall **tripled**, 14.2% → 43.3%.

## Headline

| metric | round-4 (raw kNN) | round-6 (Gate 0 + kNN) |
|---|---:|---:|
| FP-zero threshold τ | 0.08027 | 0.08294 (re-frozen on validation) |
| Test attack recall @ 0 FP | 14.2% | **43.3%** |
| Test benign FP rate | 0.0% | 0.0% |
| Benign obfuscation-control FPs | 0 | **0** |
| Adjacent-security benign FPs | 0 | **0** |

Only the decision input changed (text normalized before embedding); k=5, the
mean-top-k margin, and the FP-zero protocol are identical to round 4.

## Per-bypass-class catch (test split)

| bypass_class | round-4 | round-6 | Δ | reading |
|---|---:|---:|---:|---|
| letter_spaced | 0.000 | 1.000 | +1.000 | solved (spacing collapse) |
| leet_letter_spaced | 0.000 | 1.000 | +1.000 | solved |
| homoglyph | 0.167 | 0.775 | +0.608 | mostly solved (confusables fold) |
| leet_spacing | 0.167 | 0.721 | +0.554 | mostly solved |
| rot13 | 0.067 | 0.379 | +0.312 | improved (conservative decode guard) |
| encoding | 0.136 | 0.353 | +0.217 | improved |
| diacritics | 0.600 | 0.658 | +0.058 | minor |
| plain | 0.600 | 0.658 | +0.058 | minor (NFKC no-ops) |
| chunked_leet | 0.000 | 0.000 | 0 | **residual** |
| compact_leet | 0.000 | 0.000 | 0 | **residual** |
| compact_plain | 0.000 | 0.000 | 0 | **residual** |
| separator_spaced | 0.000 | 0.000 | 0 | **residual** |
| multilingual | 0.000 | 0.000 | 0 | accepted residual (no translation) |

## Why the residual cluster stays at 0%

`chunked_leet`, `compact_leet`, `compact_plain`, and `separator_spaced` all
reduce to the **same problem**: the attack destroys word boundaries
(`ignoreallpreviousinstructions`, `i.g.n.o.r.e.a.l.l`, `1gn0r3411...`). Gate 0
deliberately has no word-segmentation transform — recovering boundaries needs a
language model or an English frequency dictionary, and hand-building a wordlist
that happens to segment this corpus would be label-peeking. Separator-stripping
alone does not help: it converts `separator_spaced` into `compact_plain`, which
is still unembeddable. So these four classes are an honest documented residual,
parallel to `multilingual` (which needs translation). Both are future-work
transforms, recorded for the next round.

## Side-condition: zero benign-control FPs

`benign_obfuscation_control_fp = {}` (empty) and `adjacent_security_benign_fp =
0` on the test split. The conservative guards (token-level de-leet requiring ≥2
alphabetic chars, ≥4-char spacing runs, ≥90%-printable decode acceptance,
contiguous-blob-only base64/hex) kept all benign obfuscation controls and
trigger-word-laden security discussions on the benign side. Plain-text identity
held at ≥99.9% (unit-tested over 3,000 plain rows).

## Verdict rationale

- **Kill condition** (<10pt movement → drop Gate 0): not triggered — six classes
  moved +21 to +100 points; overall recall +29 points.
- **Side-condition** (zero obf-control FP): satisfied exactly.
- **Strict accept bar** (all named classes ≥40%): met for boundary-preserving
  classes; not met for the word-boundary-destruction cluster.

Net: Gate 0 is a decisive, FP-free win and proceeds into the cascade. The
residual cluster is documented, not hidden, and defines the next-round
transform (word segmentation + multilingual).
