# Round-7 Eight Improvements Analysis

Status: pilot implementation evidence, not a production/default-blocking claim.

Artifacts:

- `artifacts/round7-garak/improvements-pilot/manifest.json`
- `artifacts/round7-garak/improvements-pilot/metrics.json`
- `artifacts/round7-garak/improvements-pilot/test-per-row.jsonl`
- `artifacts/round7-garak/improvements-pilot/hard-benign-stress-per-row.jsonl`
- `meta/harness/round7-garak/run_improvements.py`
- `meta/harness/round7-garak/validate_round7_improvements.py`

Artifacts are metadata-only: row IDs, row hashes, normalized hashes, scores,
decisions, class labels for analysis, and aggregate metrics. Raw row text and
normalized text are used in memory only.

## Plain-English Result

The eight improvements move Round-7 from **45.1% catch / 6.3% FP** to
**89.2% catch / 0.0% FP** on the refreshed frozen pilot test split.

Final line:

- catch: 174 / 195 attack rows;
- pilot FP: 0 / 96 benign rows;
- hard-benign stress FP: 0 / 572 extra benign rows;
- remaining misses: 21 semantic-only user-source rows, all `direct_override`
  or `jailbreak`.

The practical lesson is sharper now: route controls can cover tool output,
prompt leakage, package provenance, terminal rendering, memory, and RAG
authority at zero pilot FP. They still do not solve user-origin semantic
overrides and jailbreaks without a separate semantic/policy-evidence control.

## Generator Fix

Before this run, the large Round-7 profile failed its own near-duplicate check
on a few benign encoded-asset rows. I fixed the generator so benign encoded
assets carry more scenario-specific texture. The large profile now passes and is
used only for:

- expanded exemplar-bank training from split-clean `exemplar_bank` rows;
- hard-benign stress FP measurement from split-clean extra benign `test` rows.

The pilot headline still uses validation-frozen thresholds and scores the pilot
test split once.

## Stepwise Results

| Step | What changed | Catch | Pilot FP | Hard-benign stress FP | Delta from previous |
|---|---|---:|---:|---:|---:|
| `00_baseline_fixed_recb` | Fixed Round-4-bank Rec B + legacy R1 | 88 / 195 = **45.1%** | 6 / 96 = **6.3%** | 4 / 572 = **0.7%** | baseline |
| `01_tool_output_authority_boundary` | Tool output facts-only authority boundary | 120 / 195 = **61.5%** | 6 / 96 = **6.3%** | 4 / 572 = **0.7%** | +32 catch |
| `02_output_stage_leakage_scan` | Narrow output leakage/exfil scan | 142 / 195 = **72.8%** | 6 / 96 = **6.3%** | 4 / 572 = **0.7%** | +22 catch |
| `03_package_provenance_verifier` | Package registry/provenance verifier | 151 / 195 = **77.4%** | 6 / 96 = **6.3%** | 4 / 572 = **0.7%** | +9 catch |
| `04_expanded_round7_in_domain_training` | Larger split-clean Round-7 bank | 150 / 195 = **76.9%** | 6 / 96 = **6.3%** | 0 / 572 = **0.0%** | +1 catch, -2 catch |
| `05_r1_prime_intent_gate` | Replace legacy R1 with R1-prime | 150 / 195 = **76.9%** | 0 / 96 = **0.0%** | 0 / 572 = **0.0%** | -6 FP |
| `06_hard_benign_expansion_guard` | Hard-benign guard and stress arm | 150 / 195 = **76.9%** | 0 / 96 = **0.0%** | 0 / 572 = **0.0%** | no movement |
| `07_terminal_escape_parser` | Terminal-control parser/escalation | 162 / 195 = **83.1%** | 0 / 96 = **0.0%** | 0 / 572 = **0.0%** | +12 catch |
| `08_memory_rag_taint_authority` | Memory/RAG taint authority labels | 174 / 195 = **89.2%** | 0 / 96 = **0.0%** | 0 / 572 = **0.0%** | +12 catch |

## Lessons By Improvement

### 1. Tool-output authority boundary

This is still the cleanest first build. It added 32 catches with no new FPs:
22 `tool_result_injection` rows and 10 terminal/tool-output rows.

Next action: implement a facts-only tool-result contract. Tool output may report
observations, but must not create policy, approve actions, or request privileged
tools.

### 2. Output-stage leakage scan

After tightening placeholder matching, the output scan added exactly the
`prompt_leakage` lift: +22 catches with no new FPs.

Next action: keep it narrow. It should scan for protected context, canaries,
secret placeholders, policy text, and outbound sinks; it should not flag every
privileged-tool mention in policy documentation.

### 3. Package provenance verifier

The provenance verifier added 9 package-hallucination catches with no new FPs.

Next action: route package suggestions through registry existence, namespace
risk, typosquat distance, maintainer/reputation, and source allowlists.

### 4. Expanded Round-7 in-domain training

The larger bank did not improve headline catch in this order; it gained one
direct override and lost two jailbreak rows. Its useful effect was FP robustness:
hard-benign stress FP dropped from 4 / 572 to 0 / 572.

Next action: keep expanded training, but treat it as calibration/robustness
support, not the main recall engine.

### 5. R1-prime intent gate

R1-prime cleared all 6 pilot FPs from benign tool workflows without losing catch
in this build order.

Next action: replace legacy R1. The rule should require intent/provenance/sink
risk, not just `untrusted + requires_tool_call`.

### 6. Hard-benign expansion guard

No movement after R1-prime and the expanded bank, but the stress arm is now
first-class: 572 extra benign rows scored at 0 FP on the final line.

Next action: keep adding hard benigns, especially benign tool workflows,
terminal logs, package installs, quoted examples, policy docs, encoded assets,
and carrier documents.

### 7. Terminal escape parser

The redesigned terminal parser added 12 catches with no new FPs. The key change
was treating terminal rendering as a separate surface and canonicalizing common
encodings before policy escalation.

Next action: build a real render sanitizer that strips/escapes terminal-control
bytes, emits tags, and escalates only when hidden/unsafe intent is present.

### 8. Memory/RAG taint authority labels

The memory/RAG control added 12 catches with no new FPs. This closed the
`memory_poisoning` bucket in the pilot.

Next action: make taint/authority labels explicit. Memory and retrieved content
can provide facts; they cannot authorize durable trust, future approvals, or
privileged tool use.

## Residual Risk

Final misses:

| Attack class | Misses |
|---|---:|
| `direct_override` | 11 |
| `jailbreak` | 10 |

These are user-source semantic attacks with no tool, sink, package, terminal,
memory, or RAG authority handle. The next improvement is not another route
guard. It needs a semantic policy/evidence classifier for override/jailbreak
intent, calibrated against benign roleplay, fiction, security discussion, and
ordinary imperative requests.

## Reproduction

Run:

```bash
python3 corpus/round7/generate-round7.py --profile pilot --out scratch/round7-pilot.jsonl --manifest scratch/round7-pilot-manifest.json
python3 corpus/round7/generate-round7.py --profile large --out scratch/round7-large.jsonl --manifest scratch/round7-large-manifest.json
.venv-round6/bin/python meta/harness/round7-garak/run_improvements.py --profile pilot --out-dir artifacts/round7-garak/improvements-pilot
python3 meta/harness/round7-garak/validate_round7_improvements.py artifacts/round7-garak/improvements-pilot/manifest.json
python3 meta/harness/round7-garak/test_round7_improvements.py
```
