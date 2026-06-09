# Round-4 Youden's J Provisional Tuning

Date: 2026-06-09
Owner: mac-agent
AgentBus task: `t_mq6vttc9_49_b40c9d32`
Status: completed metadata-only post-processing; provisional synthetic
Round-4 readout; Linux audit PASS with plateau-wording caveat on task
`t_mq6w37v8_780_3eb71bb9` / AgentBus #861

## Boundary

This is not a detector change, production threshold, AGT rule change, source
import, safety proof, certification, or release recommendation. It is a
metadata-only re-read of the existing Round-4 embedding sweep artifacts.

The task answers one narrow question:

```text
If we pick the validation threshold that maximizes Youden's J
(attack_recall - benign_fp_rate), what happens to the frozen test split?
```

## Inputs

| Artifact | SHA-256 |
|---|---|
| `validation-per-row.jsonl` | `ad031b5cef9cc6992d104e480265e390feff86a51f3b3bc9bb8462a2b42d9354` |
| `test-per-row.jsonl` | `b32cb78cbc4fd0352d59ed2b4e8a9fa94a32400dda6717e8a7c08e6ca6fe50fb` |
| `freeze-record.json` | `72429ea1222c9091c892f707bf326d3b5fda12de7371c39cd563125400934946` |
| `test-start-record.json` | `9371c84a7461c60b591a555f387dd579c27c0d392e8a32a1a31d4e17c837e26d` |

Migrated artifact:

```text
artifacts/embedding-sweep/youden-j-tuning.json
SHA-256: f5ef2011ccf824641b2bd45bd4f333dbc3c08769122ba1bb343943035d5cf99f
```

## Method

- Score field: `margin`.
- Positive predicate: `pred_attack = margin > threshold_tau`.
- Selection split: validation only.
- Objective: maximize `Youden's J = attack_recall - benign_fp_rate`.
- Tie-break: max J, then lower benign FP rate, then higher attack recall, then
  higher `threshold_tau`.
- Linux audit caveat: validation has a J-max plateau between adjacent validation
  margins `-0.00613308` and `-0.00605714`. The committed threshold
  `-0.00609511` is the explicit midpoint of that plateau, not literally the
  highest threshold implied by the earlier tie-break wording.
- Frozen test policy: apply the selected validation `threshold_tau` once to
  `test-per-row.jsonl`.

No raw text fields were read or emitted by this post-processing step.

## Three-Row Comparison

| Row | Threshold | Validation | Frozen test | Interpretation |
|---|---:|---|---|---|
| Current FP-zero operating point | `0.08026763573288917` | recall `0.218478`, FPR `0.000000`, J `0.218478`, FP `0` | recall `0.141848`, FPR `0.000000`, J `0.141848`, FP `0` | High-precision triage point; low recall. |
| Provisional Youden J-max | `-0.00609511` | recall `0.997464`, FPR `0.184835`, J `0.812628`, FP `763` | recall `0.882609`, FPR `0.163059`, J `0.719550`, FP `934` | Strong separation/catch-rate point, but too many benign FPs for default detector use. |
| AUC ceiling | n/a | ROC-AUC `0.918532`, PR-AUC `0.839878` | ROC-AUC `0.924454`, PR-AUC `0.856893` | Threshold-free ranking signal; not an operating point. |

## Base-Rate Precision

| Operating point | Split | Precision at 1:100 benign:attack | Wilson-derived 95% | Precision at 1:1000 benign:attack | Wilson-derived 95% |
|---|---|---:|---:|---:|---:|
| Current FP-zero | validation | `1.000000` | `0.686362-1.000000` | `1.000000` | `0.179547-1.000000` |
| Current FP-zero | test | `1.000000` | `0.661463-1.000000` | `1.000000` | `0.163452-1.000000` |
| Youden J-max | validation | `0.051202` | `0.048076-0.054495` | `0.005368` | `0.005025-0.005731` |
| Youden J-max | test | `0.051349` | `0.048015-0.054881` | `0.005384` | `0.005018-0.005773` |

## False-Positive Shape

The provisional J-max point moves the experiment from "nearly no alerts but low
recall" to "catch most attacks but create a large review load."

Validation J-max benign FPs:

- total: `763`
- `tool_policy_documentation`: `400`
- `benign_compact_obfuscation_control`: `200`
- `benign_obfuscation_control`: `162`
- `high_entropy_structured_data`: `1`

Frozen test J-max benign FPs:

- total: `934`
- `benign_compact_obfuscation_control`: `600`
- `tool_policy_documentation`: `185`
- `benign_obfuscation_control`: `149`

## Interpretation

The J-max result is useful because it proves the embedding margin carries a
large amount of ranking/separation signal on the synthetic Round-4 corpus. It
is not useful as a default production threshold by itself: at realistic base
rates, the precision collapses to about `5.1%` at 1 attack per 100 benign and
about `0.54%` at 1 attack per 1000 benign.

This supports a two-threshold or routed design:

- keep the FP-zero point as the high-confidence triage/readout baseline;
- treat the J-max point as a provisional analysis/review-load stress point;
- use future realistic public examples and AGT policy metadata before any
  threshold is promoted beyond research.

## AGT Reporting Lens For M2

For the AGT team, the M2 reporting question is not just "which embedding
threshold wins?" It is:

```text
Do embeddings add measurable value over the existing AGT rules-only detector,
and at what TP/FP or review-load cost?
```

Every AGT-facing M2 report should include the same split, same base-rate
assumptions, and the same no-claim language:

| Stack arm | What it answers | Required TP/FP fields |
|---|---|---|
| `rules_only` | How the existing rules stack behaves before embeddings. | attack caught / attack total, attack recall, benign FP / benign total, FP per 1k benign, adjacent-security FP. |
| `embedding_only` | Whether the embedding margin adds ranking signal by itself. | same fields, reported at FP-zero and any dialled threshold such as J-max. |

The J-max threshold should be reported as a dial, not a recommendation: it shows
that much higher catch rate is available, but with a very large benign FP/review
load. A future AGT policy run can decide whether that point is useful as a
review queue, severity boost, or abstain band; it should not be described as a
default block threshold.

AGT policy/value-add arms are intentionally deferred to M3. They should be
migrated only with the matching outcome-level artifacts and an independent audit.

## Verification

```bash
python3 meta/harness/round4-embedding-sweep/validate-embedding-sweep.py \
  --freeze artifacts/embedding-sweep/freeze-record.json \
  --test-start artifacts/embedding-sweep/test-start-record.json \
  --validation artifacts/embedding-sweep/validation-per-row.jsonl \
  --test artifacts/embedding-sweep/test-per-row.jsonl \
  --validation-metrics artifacts/embedding-sweep/validation-metrics.json \
  --test-metrics artifacts/embedding-sweep/test-metrics.json \
  --provenance artifacts/embedding-sweep/provenance.json
```

Result:

```text
round4_embedding_sweep_artifact: PASS
```

## Linux Audit Result

Linux completed the exact-provenance audit on AgentBus #861 / task
`t_mq6w37v8_780_3eb71bb9` and marked the readout PASS for provisional synthetic
metadata-only use.

Verified:

- `validate-embedding-sweep.py` PASS.
- validation/test per-row SHA-256 hashes match the committed artifacts.
- migrated `youden-j-tuning.json` SHA-256 is
  `f5ef2011ccf824641b2bd45bd4f333dbc3c08769122ba1bb343943035d5cf99f`.
- raw-key scan over validation/test JSONL PASS with `0` denied raw keys.
- independent recompute at threshold `-0.00609511` matches committed validation
  and frozen-test metrics.
- base-rate precision at 1:100 and 1:1000 benign:attack matches.
- framing remains provisional/synthetic, review-load stress point only.

Caveat:

- future method text should say "J-max plateau midpoint" or emit the plateau
  interval. This is not a blocker for the current artifact because the threshold
  is explicit, selected without test labels, and applied once to the frozen test
  split.
