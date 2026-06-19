# Completion Summary — agtrt M7 (OpenCRE relation research + validator)

**Outcome delivered (oc-7):** the assessing engineer's control mappings carry honest, verified relation quality — any relation without committed OpenCRE backing is downgraded to `candidate`. No false authority.

## Evidence

| Step | Command | Result |
|---|---|---|
| oc-7 front-to-end | `python controls/opencre/validate_relations.py --relations relations.csv --controls ../agt-ac.csv` | `verified:0 candidate:15 downgraded:9 cert:false`, exit 0 |
| Downgrade unproven | a `broad` claim with no backing | effective → `candidate` |
| Verified when backing | a claim with a `backing_ref` | effective = claim; `verified` count rises |
| Unknown relation | `relation:"bogus"` | `RelationError`, non-zero |
| Unknown control id | `AGT-AC-999` | reported under `unmapped_controls`, not dropped |
| No endorsement | report scan | zero certification/official-OpenCRE terms |
| Full tests | unittest discover | 47 passed |
| raw-free | grep over opencre artifacts | clean (M5 gate will cover it once both merge) |

## What landed (M7 file allow-list)
- `controls/opencre/relations.csv` — 15 AGT-AC → OpenCRE relation claims + `backing_ref` (all empty — no committed snapshot yet).
- `controls/opencre/validate_relations.py` — stdlib fail-honest validator: effective = claim only with backing, else `candidate`; `RelationError` on bad vocab; reports verified/candidate/downgraded + unmapped.
- `docs/slo/research/agtrt-opencre-relations.md` — methodology + **provenance** (OpenCRE source URL + CC license + retrieval-date GAP) + the honest finding.
- `tests/test_relations.py` — 5 tests (oc-7, downgrade, verified-with-backing, bad-vocab, unmapped, no-endorsement).

## Honest finding
No verified OpenCRE snapshot is committed, so all 15 relations are `candidate` (9 aspirational `broad`/`related` claims downgraded). Upgrading requires committing a licensed snapshot + per-relation `backing_ref`.

## DoD: met (outcome-first — oc-7 passes front-to-end). Tracker M7 → `done`.
