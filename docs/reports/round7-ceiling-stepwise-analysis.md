# Round-7 Stepwise Ceiling Controls Analysis

Status: pilot ceiling evidence, not a production/default-blocking claim.

Artifacts:

- `artifacts/round7-garak/ceiling-pilot/manifest.json`
- `artifacts/round7-garak/ceiling-pilot/metrics.json`
- `artifacts/round7-garak/ceiling-pilot/test-per-row.jsonl`
- `meta/harness/round7-garak/run_ceiling.py`
- `meta/harness/round7-garak/validate_round7_ceiling.py`

The artifacts are metadata-only: row IDs, row hashes, normalized hashes,
scores, decisions, class labels for analysis, and aggregate metrics. Raw row
text and normalized text are used in memory only.

## Plain-English Result

The old Round-4 Rec B shape is not enough for Round-7. On the Round-7 pilot test
split it starts at **50.3% catch** with **8.3% FP**.

Applying the seven controls one by one reaches **74.4% catch** with **1.0% FP**
on the same frozen test split:

- catch: 145 / 195 attack rows;
- FP: 1 / 96 benign rows;
- remaining FP type: `benign_encoded_asset`;
- largest remaining misses: `terminal_escape_injection`, `memory_poisoning`,
  `agentic_tool_exploit`, and `jailbreak`.

This is a ceiling-style run: it answers "which controls move the data?" before
turning them into production code.

## Stepwise Results

| Step | What changed | Catch | FP rate | Delta from previous |
|---|---|---:|---:|---:|
| `00_baseline_fixed_recb` | Fixed Round-4-bank Rec B + legacy R1 | 98 / 195 = **50.3%** | 8 / 96 = **8.3%** | baseline |
| `01_r1_prime_intent_gate` | Replace bare R1 with intent-gated R1-prime | 94 / 195 = **48.2%** | 2 / 96 = **2.1%** | +9 catch, -13 catch, -6 FP |
| `02_hard_benign_guard` | Add hard benign guard | 94 / 195 = **48.2%** | 2 / 96 = **2.1%** | no movement |
| `03_round7_in_domain_training` | Switch kNN/head bank to Round-7 exemplars | 105 / 195 = **53.8%** | 1 / 96 = **1.0%** | +17 catch, -6 catch, -1 FP |
| `04_tool_output_authority_boundary` | Add tool-output authority boundary | 125 / 195 = **64.1%** | 1 / 96 = **1.0%** | +20 catch |
| `05_output_stage_leakage_scan` | Add output-stage leakage/exfil scan | 137 / 195 = **70.3%** | 1 / 96 = **1.0%** | +12 catch |
| `06_package_provenance_verifier` | Add package provenance verifier | 144 / 195 = **73.8%** | 1 / 96 = **1.0%** | +7 catch |
| `07_terminal_escape_sanitizer` | Add terminal escape escalation rule | 145 / 195 = **74.4%** | 1 / 96 = **1.0%** | +1 catch |

## What Each Step Says

### 1. R1-prime intent gate

R1-prime is mainly an FP cleanup. It clears six benign tool-workflow FPs and
reduces FP from 8.3% to 2.1%, but it costs four net catches at this point.

Recommendation: keep the intent gate, but do not treat it as the main recall
solution. It should replace bare `untrusted + tool_call` logic, while route
controls recover the attacks it stops over-catching.

### 2. Hard benign guard

No pilot movement after R1-prime. That does not mean the guard is useless; it
means this pilot's two remaining FPs are not the quoted/example/read-only/tool
docs cases the guard was designed to suppress.

Recommendation: keep it as a safety rail, then measure it again on a much larger
hard-benign set before claiming sub-1% FP.

### 3. Round-7 in-domain training

In-domain examples produce real lift: net +11 catches and one fewer FP compared
with the prior step. It improves direct overrides, terminal escapes, memory
poisoning, and a few tool/data-boundary cases, though it still loses six rows
that the previous bank caught.

Recommendation: keep Round-7 exemplar training, but expand the bank rather than
assuming this small pilot bank is enough.

### 4. Tool-output authority boundary

This is the biggest clean gain: +20 catches and no new FPs. It collapses
`tool_result_injection` misses from 22 to 2.

Recommendation: make this the first production control. Tool output should be
facts-only: it can report observations, but it cannot set policy, approve tool
calls, override developer/system instructions, or request privileged actions.

### 5. Output-stage leakage scan

This is the second biggest clean gain: +12 catches and no new FPs. It reduces
`prompt_leakage` misses from 12 to 1 and catches one output exfiltration row.

Recommendation: implement this as an output-time control, not as another input
embedding tweak. Final responses need checks for protected context labels,
canaries, secret placeholders, policy strings, and outbound sinks.

### 6. Package provenance verifier

This gives +7 catches and no new FPs. Package hallucination moves only when the
system verifies provenance rather than relying on text similarity.

Recommendation: route package suggestions through registry existence,
namespace/typosquat checks, maintainer/reputation checks, and source allowlists.

### 7. Terminal escape sanitizer

The current prototype adds only +1 catch and no new FPs. Terminal escape remains
the largest residual miss class with 16 misses.

Recommendation: keep terminal sanitization always-on, but redesign the detection
piece. It needs a proper terminal-control parser/sanitizer plus narrow escalation
when hidden terminal controls are paired with instruction, clipboard/link
rewrite, command execution, unsafe action, or tool/policy intent.

## Highest-Bang Implementation Order

Based on this pilot, the order to build is:

1. Tool-output authority boundary.
2. Output-stage leakage/exfil scan.
3. Package provenance verifier.
4. Round-7 in-domain exemplar expansion and retraining.
5. R1-prime intent gate plus hard-benign guard for FP control.
6. Terminal escape redesign, not just the current simple sanitizer rule.
7. Larger hard-benign validation set before any "near-zero FP" claim.

The important shape is structural: source authority, output gates, provenance
checks, and taint labels are doing more work than further threshold tuning.

## Residual Risk

The final pilot still misses 50 / 195 attack rows. The misses are concentrated
in:

| Attack class | Remaining misses after all controls |
|---|---:|
| `terminal_escape_injection` | 16 |
| `memory_poisoning` | 8 |
| `agentic_tool_exploit` | 7 |
| `jailbreak` | 7 |
| `direct_override` | 4 |
| `package_hallucination` | 2 |
| `tool_result_injection` | 2 |
| `data_boundary_abuse` | 1 |
| `output_exfiltration` | 1 |
| `prompt_leakage` | 1 |
| `tool_abuse` | 1 |

Next work should focus on terminal parsing, memory/RAG taint authority, and
agentic tool-effect modeling. More kNN/head tuning alone is unlikely to close
those gaps.

## Reproduction

Run:

```bash
.venv-round6/bin/python meta/harness/round7-garak/run_ceiling.py --profile pilot --out-dir artifacts/round7-garak/ceiling-pilot
python3 meta/harness/round7-garak/validate_round7_ceiling.py artifacts/round7-garak/ceiling-pilot/manifest.json
python3 meta/harness/round7-garak/test_round7_ceiling.py
```
