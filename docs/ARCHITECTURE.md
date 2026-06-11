# ARCHITECTURE — AGT Embeddings Experiment

Reality-first orientation for this repository as it exists today. Generated as
the prerequisite architecture doc for `docs/RUNBOOK-round6-cascade-experiment.md`.

## What this repository is

A research corpus and evidence pack answering one question: can an embedding +
nearest-neighbour signal give AGT (Microsoft agent-governance-toolkit) better
prompt-injection detection evidence than its rules-only detector, while staying
optional, tunable, and auditable?

It is **not** a product. It contains no runtime detector, no service, and no
production integration. Everything here is batch evaluation over a frozen
synthetic corpus.

## Components as they exist today

```
┌──────────────────────────────────────────────────────────────────────────┐
│ AGT-Embeddings-Experiment                                                │
│                                                                          │
│  corpus/round4/                          tools/agt-rules-baseline/       │
│  ├ injection-round4-large.jsonl  ──────▶ Rust CLI wrapping vendored AGT  │
│  │  (44,800 rows; exemplar_bank /        prompt_injection.rs rules       │
│  │   validation / test splits)           └▶ corpus/round4/rules-baseline │
│  ├ manifest-large.json                      -large-metrics.json          │
│  └ check-round4.py (hygiene)                                             │
│        │                                                                 │
│        ▼                                                                 │
│  meta/harness/round4-embedding-sweep/                                    │
│  └ run_round4_embedding_sweep.py                                         │
│     fastembed(bge-small-en-v1.5, local ONNX) ▶ kNN margin scoring        │
│     validation-first freeze ▶ single frozen-test evaluation              │
│        │                                                                 │
│        ▼                                                                 │
│  artifacts/embedding-sweep/   (metadata-only: ids, labels, margins,      │
│  ├ freeze-record.json          decisions, metrics — never raw text)      │
│  ├ validation/test-per-row.jsonl, *-metrics.json, youden-j-tuning.json   │
│        │                                                                 │
│        ▼                                                                 │
│  meta/harness/round4-governance-eval/  +  artifacts/governance-eval/     │
│     five policy arms (rules / embedding / policy gate / combinations)    │
│     over a stub tool-sink catalog                                        │
│                                                                          │
│  docs/  reports, methodology contracts, CLAIMS-LEDGER, upstream PR plan  │
└──────────────────────────────────────────────────────────────────────────┘
```

| Component | Responsibility | Stack |
|---|---|---|
| `corpus/round4/` | Frozen 44,800-row labelled corpus + manifest + hygiene checker | JSONL + Python |
| `tools/agt-rules-baseline/` | Rules-only baseline metrics from vendored AGT `prompt_injection.rs` | Rust |
| `meta/harness/round4-embedding-sweep/` | Embedding/kNN sweep runner + artifact validator | Python (fastembed, numpy, scikit-learn, psutil) |
| `meta/harness/round4-governance-eval/` | Governance policy-arm evaluation + validator | Python + Rust generator |
| `meta/harness/round5-*` | Round-5 source-scale pilot validators | Python |
| `artifacts/` | Committed metadata-only evidence (hashed, provenance-recorded) | JSON/JSONL |
| `docs/` | Reports, methodology contracts, claims ledger, runbooks | Markdown |

## Corpus row schema (fields relevant to experiments)

Every row carries: `id`, `text`, `attack_class` (8 attack families or
`benign`), `benign_subclass`, `bypass_class` (obfuscation variant), `split`
(`exemplar_bank` / `validation` / `test`), `family_id` / `group_id` (leakage
control), and governance metadata: `source_type`, `trust_level`, `risk_level`,
`contains_sensitive_sink`, `requires_tool_call`, `expected_action`.

`expected_action` and `risk_level` are **ground-truth annotations**, never
detector inputs. Splits: 28,504-row exemplar bank, 6,888 validation
(2,760 attacks / 4,128 benign), 9,408 test (3,680 attacks / 5,728 benign).

## Invariant conventions every experiment must follow

1. **Frozen-test discipline**: all selection (k, thresholds, model choices,
   calibration) happens on `validation` against the `exemplar_bank`; the
   `test` split is scored exactly once per frozen configuration, recorded in a
   freeze record before test scoring starts.
2. **Metadata-only artifacts**: committed artifacts never contain raw prompt
   text (`text`, `raw_text`, `prompt`, `content` are forbidden output fields).
   Rows are referenced by `id` and hashes.
3. **Provenance records**: each artifact directory carries provenance (model
   SHA-256, package versions, host info) and validators
   (`validate-*.py`) that re-check structure and hashes.
4. **No production claims**: synthetic-corpus results are research evidence
   only; no default-blocking, certification, or real-traffic claims.
5. **Local-only inference**: embedding model runs via local ONNX
   (`.cache/fastembed/`); network use is model download only.

## Key established results (evidence baseline for new rounds)

| Signal | Catch rate | FP rate | Source |
|---|---:|---:|---|
| AGT rules-only | ~1% | ~8% | `corpus/round4/rules-baseline-large-metrics.json` |
| kNN margin, FP-zero point (τ=0.0803) | 14.2% | 0.0% observed | `artifacts/embedding-sweep/test-metrics.json` |
| kNN margin, Youden point (τ=-0.0061) | 88.3% | 16.3% | same |
| Policy gate only (governance arm) | 65.2% prevention | 14.0% hard-block FP | `artifacts/governance-eval/metrics.json` |
| Policy + embedding | 69.3% prevention | 14.0% hard-block FP | same |

Known blind spots at the FP-zero point: tool_abuse 0/600, prompt_leakage 0/80,
indirect_injection 1.7%, multilingual 0/320; chunked/compact/letter-spaced
bypass classes 0%. Youden-point false positives concentrate in
`benign_compact_obfuscation_control` (600), `tool_policy_documentation` (185),
`benign_obfuscation_control` (149).

### Round-6 cascade results (built; see `docs/reports/round6-cascade-report.md`)

| Stage | Result | §2 verdict |
|---|---|---|
| Gate 0 de-obfuscation | zero-FP recall 14.2%→43.3%, 0 obf-control FP | partial accept |
| Gate 1 trained head | does not beat kNN at deployable FPR | not supported |
| Gate 1 LOFO | median held-out TPR@1%FPR 0.716, 0 families <5% | pass |
| Three-bucket conformal route | benign escape 1.20% (coverage holds), queue precision 5.07%@1:1000 | accept |
| Gate 2 governance ablation | free metadata ≈ full; independence refuted (overlap 2.76); end-to-end 64.4% | bars not met |
| Per-family floors | no family at 0% (tool_abuse 37.7%, prompt_leakage 100%) | pass |

Round-6 harness: `meta/harness/round6-cascade/`; artifacts:
`artifacts/round6-cascade/m1..m5/`. New round-6 components — `normalize.py`
(Gate 0), `common.py` (shared scoring), `head.py`, `buckets.py`, `gate2.py`,
per-milestone runners, `validate-round6-cascade.py`.

### Experiment 1 — structural auto-block ceiling (built; `docs/reports/exp1-structural-autoblock-report.md`)

Fully-automated stack = round-6 Gate-0 + kNN @ zero-FP **OR** deterministic
structural rules (facts only, no text meaning). Headline: **embedding ∨ R1 = 81%
catch @ 0% false-block**; R1 blocks the four action families at 100%; R2 found
too-broad and discarded; residual = prompt_leakage / tool_result_injection /
memory_poisoning. Labels-perfect synthetic ceiling. Harness:
`meta/harness/exp1-structural/` (`rules.py`, `run_exp1_eval.py`,
`validate-exp1.py`); artifacts: `artifacts/exp1-structural/`. No embedding model
run — reuses committed round-6 zero-FP decisions.

## Environment

- Python 3.14 (system) with `numpy`, `scikit-learn` installed; harness runs
  additionally need `fastembed` and `psutil` (versions recorded in
  `artifacts/embedding-sweep/provenance.json`).
- Rust stable for `tools/agt-rules-baseline` (not needed for embedding rounds).
- Embedding model cache under `.cache/fastembed/` (git-ignored).
