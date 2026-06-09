# Open Source Readiness

This checklist tracks public-repository packaging. It is separate from migration
evidence and must not change artifact claims.

## Present Files

- `LICENSE`: MIT license.
- `README.md`: research scope, evidence snapshot, and red lines.
- `CONTRIBUTING.md`: contribution and evidence-change checklist.
- `CODE_OF_CONDUCT.md`: participation expectations.
- `SECURITY.md`: vulnerability and artifact-hygiene reporting policy.
- `CITATION.cff`: citation metadata.

## Public Boundary

Before public release, verify that:

- the upstream AGT path is described as two PRs: fixture first, optional
  embedding signal second;
- the embedding signal is described as optional, default-off, additive, and
  auditable;
- the rules-only baseline number is tied to the exact corpus, AGT commit, and
  detector hash;
- governance/value-add evidence remains `needs_more_play` research evidence;
- no production safety, default-blocking, certification, benchmark coverage,
  governance-readiness, detector-promotion, policy-promotion, source-import, or
  real-traffic validation claim is added;
- no raw secrets, live credentials, customer data, local caches, virtual
  environments, or build outputs are present;
- corpus and artifact files remain metadata-only where required by the existing
  validators and reports.

## Final Packaging Checks

Run these before tagging or making the repository public:

```bash
git diff --check
bash corpus/round4/run-smoke.sh
python3 meta/harness/round4-embedding-sweep/validate-embedding-sweep.py \
  --provenance artifacts/embedding-sweep/provenance.json \
  --freeze artifacts/embedding-sweep/freeze-record.json \
  --validation artifacts/embedding-sweep/validation-per-row.jsonl \
  --test artifacts/embedding-sweep/test-per-row.jsonl \
  --validation-metrics artifacts/embedding-sweep/validation-metrics.json \
  --test-metrics artifacts/embedding-sweep/test-metrics.json
python3 meta/harness/round4-governance-eval/validate-governance-eval.py \
  --manifest artifacts/governance-eval/manifest.json \
  --validation artifacts/governance-eval/validation.jsonl \
  --test artifacts/governance-eval/test.jsonl \
  --metrics artifacts/governance-eval/metrics.json
python3 meta/harness/round5-agt-value-add/validate-round5-agt-value-add-report.py \
  meta/harness/round5-agt-value-add/round5-agt-value-add-report.example.json
```

If any check changes metrics or claim strength, treat it as new evidence work
and route it through the AgentBus audit split before publishing.

## Upstream PR Readiness

Before opening an AGT PR:

- rerun the rules-only baseline against fresh AGT upstream `main`;
- record AGT commit SHA and detector file SHA-256;
- keep PR 1 to corpus, manifest, validators, baseline harness, and docs;
- keep PR 2 blocked until methodology review is complete;
- ensure PR 2, if opened later, is disabled by default and evidence-only unless
  a policy profile explicitly routes it.
