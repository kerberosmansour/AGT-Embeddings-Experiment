# Lessons Learned — r6c Milestone 1 (Gate 0 de-obfuscation)

## What changed
- New `normalize.py` (pure, idempotent, bounded de-obfuscation), `common.py`
  (shared scoring/metrics, extracted early — see below), `run_m1_gate0_rescore.py`,
  `validate-round6-cascade.py`, tests, and `requirements.lock` (hash-pinned).
- Re-ran the round-4 FP-zero kNN protocol on normalized text.

## Key result
- Test attack recall at the zero-FP operating point **tripled, 14.2% → 43.3%**,
  with benign FP rate still 0.0% and zero benign obfuscation-control FPs.
- Pure normalization in front of the *unchanged* round-4 scorer produced the
  entire gain — confirming the RFC-critique hypothesis that obfuscated attacks
  were scoring low (not uncertain) and so never reached a Gate-2-positioned
  de-obfuscation step.

## Design decisions and why
- **De-leet runs AFTER spacing/separator collapse**, not before: collapse
  merges single-char tokens into words that de-leet must then see. Putting
  de-leet first broke idempotency (caught by the 2,000-row property test).
- **Whitespace canonicalization before spacing collapse**: irregular spacing
  produced empty split tokens that hid single-char runs, making collapse
  non-idempotent across two passes.
- **base64/hex only on contiguous (space-free) blobs, printable-ratio guard
  only** (no English-benefit requirement) so nested encodings unwrap and ordinary
  prose — which always contains spaces — is never mistaken for a payload.
- **rot13 keeps the English-benefit guard** because it preserves length and
  printability; only a dictionary-style signal separates it from plain text.
- **Closed transform-tag enum** (F-SEC-2): tags are literal constants, asserted
  at construction and at artifact-write — attack text can never leak via a tag.

## Assumptions verified
- Idempotency and determinism hold over 2,000 corpus rows + 500 random strings.
- Plain/none bypass rows are ≥99.9% character-identical after normalization.
- Conservative guards keep all benign obfuscation controls and adjacent-security
  discussions FP-free at the FP-zero threshold.

## Assumptions still unresolved / residual
- **Word-boundary-destruction cluster** (chunked/compact/separator, ~600 attack
  rows) stays at 0% — needs word segmentation (dictionary/LM), deferred as a
  next-round transform. Separator-stripping alone is useless (turns
  separator_spaced into compact_plain, still unembeddable).
- **Multilingual** (320 rows) stays at 0% — needs translation, accepted residual.

## Deviation from runbook
- `common.py` (helper extraction) was scheduled for M2's refactor budget but
  created during M1 to avoid duplicating round-4 code. M2's refactor step is
  therefore already satisfied; M2 imports `common.py` directly. No behavior
  change to round-4 artifacts (separate files).
- Used a fresh Python 3.13 venv (`.venv-round6`, git-ignored) because the system
  interpreter is 3.14 and `statistics.pstdev` on a float list misbehaved there;
  switched margin stdev to `np.std`.

## Mistakes made
- First normalizer matched the base64 charset regex against whole sentences
  (spaces allowed), tagging prose as `decode_rejected`. Fixed with the
  contiguous-blob gate.

## Rules for the next milestone
- M2 head trains on these normalized embeddings; reuse `common.py` cache + kNN
  reference curve from M1 per-row margins.
- Keep the freeze-before-test discipline: freeze record written, then test.
- LOFO must retrain with frozen hyperparameters only.
