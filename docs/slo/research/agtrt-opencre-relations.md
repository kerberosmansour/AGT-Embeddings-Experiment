# AGT-AC ↔ OpenCRE Relation Research (agtrt M7)

## Goal
Make the benchmark's control mappings **honest**: every AGT-AC → OpenCRE relation is only as strong as its committed evidence. Unverified relations are visibly `candidate` — no false authority, no implied OpenCRE/OWASP endorsement.

## Method
1. Scenarios → AGT-AC controls (M1/M4, `controls/agt-ac.csv`).
2. AGT-AC controls → OpenCRE common-requirement targets, each with a relation in the closed vocabulary `exact | broad | narrow | related | candidate` (`controls/opencre/relations.csv`).
3. `validate_relations.py` computes the **effective** relation: equal to the claim ONLY if a committed `backing_ref` exists, otherwise downgraded to `candidate` (fail-honest).

## OpenCRE source provenance
- **Source**: OpenCRE (Open Common Requirement Enumeration) — <https://www.opencre.org/>.
- **License**: OpenCRE content is openly licensed (Creative Commons); any committed snapshot must record its CC license + retrieval date.
- **Retrieval date / committed snapshot**: **NOT YET COMMITTED.** No verified OpenCRE snapshot is committed in this repo, so no relation currently carries a `backing_ref`. This is the honest gap, not an omission to paper over.

## Finding (current, honest)
With no committed OpenCRE snapshot, **all 15 AGT-AC relations are `candidate`** (effective). The s5 scratch mapping aspirationally claimed `broad`/`related` for 9 of them; the validator downgrades those to `candidate` because they lack committed backing. To upgrade a relation beyond `candidate`, a future contribution must (a) commit a licensed OpenCRE snapshot and (b) add a `backing_ref` (CRE id) per relation; `validate_relations.py` then reports it as `verified`.

## Candidate agentic CRE gaps (from s5, still open)
- Render/parse divergence for hidden content (AGT-AC-003).
- Agent memory write/read integrity + traceback (AGT-AC-007).
- A2A delegation + message integrity (AGT-AC-010).
- Evidence-level reporting for agent-control benchmarks (AGT-AC-015).

These are genuine candidate gaps to propose upstream (via the deferred OpenCRE research/contribution track), not existing CREs.

## No-overclaim invariant
The report carries `certification_claim: false` and zero endorsement language. A relation may NEVER present as `exact`/`broad`/`narrow`/`related` without a committed `backing_ref`; the validator enforces this by downgrading to `candidate`.
