# AGT Embeddings Experiment

This repository is the standalone home for the AGT prompt-injection embeddings
experiment.

The core question:

```text
Can an embedding + nearest-neighbour signal give AGT better prompt-injection
detection evidence than the current rules-only detector, while staying optional,
tunable, and auditable?
```

## Current Evidence Snapshot

These are the migration targets from the completed AGT-only research track:

| Approach | Catch rate | False positive rate | Notes |
|---|---:|---:|---|
| AGT rules-only baseline | about `1%` | about `8%` | Current detector catches obvious patterns but misses most held-out attacks. |
| Embeddings at Youden's J point | about `88%` | about `16%` | Strong separation point, too noisy for default blocking. |
| Embeddings at zero-FP point | about `14%` | `0%` observed | Conservative high-confidence routing signal. |

The work is not proposing default auto-blocking. The embedding signal is an
optional, default-off, auditable layer that can feed downstream policy or review
routing.

## What This Repo Should Contain

- AGT prompt-injection corpus generation and metadata-only validation tools.
- AGT rules-only baseline runner and result artifacts.
- Embedding/kNN evaluation scripts and frozen readouts.
- Youden's J tuning evidence and base-rate precision notes.
- Governance/value-add comparison reports for AGT arms such as `rules_only`,
  `embedding_only`, `policy_only_gate`, and `policy_plus_embedding`.
- Reproducibility instructions and audit checklists.

## What This Repo Should Not Contain

- unrelated product research tracks;
- unrelated data-classification experiments;
- raw secrets, live credentials, or customer data;
- production safety, certification, or benchmark-coverage claims.

## Migration And Packaging Status

Migration status and claim mapping live in:

- [`docs/RUNBOOK-agt-embeddings-migration.md`](docs/RUNBOOK-agt-embeddings-migration.md)
- [`docs/CLAIMS-LEDGER.md`](docs/CLAIMS-LEDGER.md)
- [`docs/AGENTBUS-WORKSPLIT.md`](docs/AGENTBUS-WORKSPLIT.md)

The AGT-only migration gates are complete through M4. The remaining work is
public-repo packaging and any future experiment follow-up, not promotion to a
production/default-blocking detector.

## Community And Security

- [`CONTRIBUTING.md`](CONTRIBUTING.md)
- [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md)
- [`SECURITY.md`](SECURITY.md)
- [`CITATION.cff`](CITATION.cff)
