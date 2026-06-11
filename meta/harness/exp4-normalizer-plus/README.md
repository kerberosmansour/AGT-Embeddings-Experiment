# Ticket #10 — normalizer encoding/rot13 extension (result)

Extends the Gate-0 normalizer (`meta/harness/round6-cascade/normalize.py`) with
percent/URL-encoding, `\uXXXX` unicode-escape, and HTML-entity decoders (plus a
slightly widened rot13 path), each behind the same printable-ratio + English-
benefit acceptance guard so benign data is not mangled.

## Result (FP-zero operating point, frozen-test protocol)

| metric | before (round-6 Gate 0) | after (extended) |
|---|---:|---:|
| **encoding** bypass-class catch | 35.3% | **62.4%** (+27.1) |
| rot13 | 37.9% | 39.2% (+1.3) |
| overall zero-FP recall | 43.3% | **49.0%** (+5.7) |
| benign false-positives | 0 | **0** |
| benign obfuscation-control FP | 0 | **0** |

Out-of-scope classes unchanged as expected: multilingual 0%, compact/chunked/
separator 0% (word-boundary problem, needs segmentation).

## Accept criteria — met

- encoding + rot13 catch rises at FP-zero ✓
- benign obfuscation-control FP stays ~0 ✓ (0)
- idempotency / determinism / plain-identity property tests green ✓ (24 tests)

## Run

```
.venv-round6/bin/python meta/harness/exp4-normalizer-plus/run_bypass_remeasure.py
```

Writes `artifacts/exp4-normalizer-plus/bypass-remeasure.json`. Re-embeds the
corpus with the updated normalizer (no model run cached — normalize.py SHA
changed); does not touch the committed round-6 `m1-gate0` artifacts.

## Note

The round-6 `m1-gate0` freeze record's `normalize_sha256` now differs from the
live `normalize.py` — expected: that record is the frozen evidence of round 6;
this ticket is the forward improvement. The committed round-6 artifacts are
byte-identical (not regenerated).
