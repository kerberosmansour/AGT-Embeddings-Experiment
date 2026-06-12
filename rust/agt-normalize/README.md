# agt-normalize (round-7 extension of AGT's `agentmesh::normalize`)

**Rust-first** extension of the content normalizer introduced by
[microsoft/agent-governance-toolkit#2991](https://github.com/microsoft/agent-governance-toolkit/pull/2991)
(RFC #2957). This crate is a **drop-in superset** of
`agent-governance-rust/agentmesh/src/normalize.rs`: the PR's transforms are
unchanged, so existing callers are unaffected; round-7 adds garak-derived
transforms. Upstreaming back into AGT is a file-replace plus the new tests (and
the matching Python parity port).

## What round-7 adds (each a new closed-enum `Transform`, each FP-guarded)

| Transform | garak vector | Guard |
|---|---|---|
| `AnsiEscape` | `ansiescape` (terminal hijack) | strips CSI/OSC8/OSC52 sequences; runs before the invisible-strip so the whole sequence goes, not just `ESC` |
| `UnicodeTag` | `encoding.InjectUnicodeTagChars`, `goodside` | folds U+E0000–E007F tag block to ASCII; keeps subdivision-flag (U+1F3F4) sequences |
| `VariationSelector` | `encoding.InjectUnicodeVariantSelectors` | strips VS after an **ASCII** base; keeps VS after emoji/symbol/CJK (the FP guard) |
| `SneakyBits` | `encoding.InjectSneakyBits` | decodes zero-width binary (U+200B/U+200C) **before** the invisible-strip deletes it |
| `Zalgo` | `encoding.InjectZalgo` | strips combining marks under a density guard (legit decomposed accents survive) |
| `Base32` | `encoding.InjectBase32` | RFC 4648, contiguous blob, printable-ratio guard |
| `Base85` | `encoding.InjectAscii85` | Ascii85, blob + distinctive-char guard (so base64 blobs aren't mis-read) |
| `Atbash` | `encoding.InjectAtbash` | length-preserving cipher; requires an English-benefit gain |
| `Morse` | `encoding.InjectMorse` | only when the text is wholly `.-/ ` shaped + English benefit |
| `Nato` | `encoding.InjectNato` | only when a **majority** of tokens are NATO words (≥4) |
| `Braille` | `encoding.InjectBraille` | Unicode braille → ASCII, pure-braille guard |

`Base16` is already covered by the PR's `Hex` decoder. `QuotedPrintable` and
`uuencode` are the next wave (same harness).

## Design constraints (inherited from the PR, kept)

- **No new crate deps** beyond `base64` (base32/85, morse, nato, braille, etc.
  are hand-rolled stdlib).
- **Deterministic + idempotent** (`round7_idempotent` test).
- **Benign-safe** — every aggressive transform fires only under its guard; the
  benign-safety tests (emoji/VS kept, accents not zalgo-stripped, NATO-word prose
  not decoded) are the contract that matters.
- **Closed `Transform` vocabulary** surfaced to every downstream control + audit.

## Build / test / run

```bash
cd rust/agt-normalize
cargo test                       # 33 tests (PR's originals + round-7)
echo '.. --. -. --- .-. .' | cargo run -q --bin agt-normalize
# -> {"text":"ignore","transforms":["Morse"]}
```

The CLI (stdin → `{text, transforms}` JSON) is how the Python research harness
drives the **Rust** normalizer for the round-7 A/B, so the measurement scores the
artifact that ships to AGT. See [`../../docs/RUNBOOK-round7-garak-corpus.md`](../../docs/RUNBOOK-round7-garak-corpus.md).

## Upstream path

1. This crate → replace `agentmesh/src/normalize.rs` (additive `Transform`
   variants; existing API unchanged).
2. Mirror the new transforms in AGT's Python `agent_os.normalize` and extend the
   cross-SDK parity vectors (the PR established 300-case Rust⇄Python parity).
