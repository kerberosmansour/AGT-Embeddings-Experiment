# Completion Summary — agtrt M4 (Control-linked evidence-level reporter)

**Outcome delivered (oc-4):** the assessing engineer runs the full chain and gets an evidence-level scorecard (JSON+MD) by trap class / AGT-AC control / evidence level, with a hard `certification_claim:false` — actionable, honest, no badge.

## Evidence

| Step | Command | Result |
|---|---|---|
| oc-4 front-to-end | `bash run-smoke.sh` (now ends in the reporter) | `{"certification_claim":false,"controls":15,"failures":0}`, `[smoke] OK`, exit 0 |
| Full tests | unittest discover | 39 passed (16 M1 + 9 M2 + 5 M3 + 9 M4) |
| No overclaim (abuse-4) | scan JSON+MD | zero certification terms; renders "evidence, not a certification" |
| Hard-benign not failed (abuse-6) | AGT-AC-014 pass | `failures:0`, not counted as a failure |
| Missing field / bad enum | result without `evidence_level` / `L9` | `ResultError`, non-zero, no default |
| Unmapped control | `AGT-AC-999` | reported under `unmapped_controls`, not dropped |
| Static | `py_compile` + `git diff --check` | clean |

## What landed (M4 file allow-list)
- `controls/agt-ac.csv` — read-only 15-control AGT-AC catalog (from s5), raw-free.
- `reporters/scorecard.py` — stdlib aggregator by trap class / control / evidence level; hard `certification_claim:false`; `ResultError` fail-closed; JSON + Markdown with the no-certification disclaimer; `--results` or `--from-scenarios`.
- `run-smoke.sh` — appended the report step (validate → harness → **report**).
- `tests/test_reporter.py` — 9 tests (oc-4, no-cert, hard-benign, missing-field, unknown-enum, unmapped-control, empty-results).

## Invariants
`certification_claim is False` (literal); `evidence_level ∈ {L0..L3}` closed enum; no L3 produced from mock results; missing field ⇒ structured error; unmapped control surfaced, not dropped; renders evidence levels, never a single score/badge.

## DoD: met (outcome-first — oc-4 passes front-to-end). Tracker M4 → `done`.
