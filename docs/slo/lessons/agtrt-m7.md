# Lessons — agtrt M7

- **Honest > impressive.** The s5 scratch claimed `broad`/`related` OpenCRE relations for 9 controls. Without a committed, licensed OpenCRE snapshot to back them, the only honest output is `candidate` for all 15. The validator ENFORCES this (downgrade-without-backing) rather than presenting aspirational claims as verified — exactly the "no false authority" the founder asked for.
- **The gap IS the finding.** "No verified OpenCRE snapshot is committed" is a legitimate research deliverable, documented in the write-up with the upgrade path (commit snapshot + add `backing_ref`). Don't fabricate backing to make the numbers look better.
- **Provenance fields are mandatory** (critique F-ENG-3): source URL + license (OpenCRE is CC) + retrieval date — recorded even when the retrieval is a documented TODO.
- **M7 is independent of M5/M6** — it branches off canonical (M1–M4) and touches only `controls/opencre/**` + a research doc + its test, so it composes with the open M5 (#30) without conflict. The M5 hygiene gate (not on this branch) will scan the opencre artifacts once both merge; manual raw-free grep confirms they're clean meanwhile.
