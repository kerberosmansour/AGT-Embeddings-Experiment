# Round-7 Rec B Control Analysis

Status: pilot evidence, not a production/default-blocking claim.

Artifacts:

- `artifacts/round7-garak/recb-pilot/manifest.json`
- `artifacts/round7-garak/recb-pilot/metrics.json`
- `meta/harness/round7-garak/run_recb.py`
- `meta/harness/round7-garak/validate_round7_recb.py`

## Plain-English Result

Round-7 breaks the old synthetic headline. The Rec B shape still improves catch,
but the old "0 FP" story does not carry over.

| Arm | What it means | Rec B catch | FP rate |
|---|---|---:|---:|
| `fixed_round4_bank` | Apples-to-apples with the current Round-7 kNN pilot: detector bank stays Round-4 | 98 / 195 = **50.3%** | 8 / 96 = **8.3%** |
| `round7_in_domain_bank` | Trains kNN bank and head on Round-7 exemplar rows | 109 / 195 = **55.9%** | 7 / 96 = **7.3%** |

The in-domain arm is useful signal: Round-7 examples help. But the FP rate is
far too high for a clean accept.

## What Actually Moved

The head is not the main win yet.

| Fixed Round-4 bank variant | Catch | FP rate |
|---|---:|---:|
| kNN only | 33 / 195 = 16.9% | 2 / 96 = 2.1% |
| legacy R1 only | 83 / 195 = 42.6% | 6 / 96 = 6.3% |
| kNN OR R1 | 98 / 195 = 50.3% | 8 / 96 = 8.3% |
| Rec B | 98 / 195 = 50.3% | 8 / 96 = 8.3% |

| Round-7 in-domain variant | Catch | FP rate |
|---|---:|---:|
| kNN only | 45 / 195 = 23.1% | 0 / 96 = 0.0% |
| legacy R1 only | 83 / 195 = 42.6% | 6 / 96 = 6.3% |
| kNN OR R1 | 102 / 195 = 52.3% | 6 / 96 = 6.3% |
| Rec B | 109 / 195 = 55.9% | 7 / 96 = 7.3% |

Interpretation: R1 is the biggest catch lever, but it is also the main FP
source. In-domain training makes kNN and the head more useful, but it does not
solve the tool-use FP problem.

## False Positives

For `fixed_round4_bank` Rec B, the 8 FPs are concentrated in:

- `benign_multistep_tool_use`: 4
- `benign_tool_use`: 2
- `benign_terminal_output`: 1
- `benign_encoded_asset`: 1

For `round7_in_domain_bank` Rec B, the 7 FPs are:

- `benign_multistep_tool_use`: 4
- `benign_tool_use`: 2
- `benign_encoded_asset`: 1

This says the current rule is too close to "tool use is suspicious." Round-7
adds exactly the hard benigns that make that assumption fail.

## Weak Attack Areas

With the in-domain Rec B arm:

| Attack class | Catch |
|---|---:|
| `agentic_tool_exploit` | 15 / 15 = 100% |
| `data_boundary_abuse` | 22 / 22 = 100% |
| `indirect_injection` | 14 / 14 = 100% |
| `output_exfiltration` | 22 / 22 = 100% |
| `tool_abuse` | 10 / 10 = 100% |
| `direct_override` | 8 / 12 = 66.7% |
| `memory_poisoning` | 4 / 12 = 33.3% |
| `jailbreak` | 3 / 10 = 30.0% |
| `terminal_escape_injection` | 5 / 22 = 22.7% |
| `prompt_leakage` | 3 / 22 = 13.6% |
| `package_hallucination` | 1 / 10 = 10.0% |
| `tool_result_injection` | 2 / 24 = 8.3% |

The hard residual is not just obfuscation. It is missing policy semantics:
tool-output authority, output leakage, terminal rendering safety, and package
provenance.

## Controls Needed

1. **Replace legacy R1 with an intent-gated tool control.**

   Legacy R1 catches a lot, but it false-positives on benign tool workflows. The
   next version should require more than `untrusted + tool_call`: use provenance,
   sink type, requested privilege change, external network/file effect,
   cross-boundary data movement, or policy-override intent.

2. **Tool-output authority boundary.**

   Tool output should not be allowed to create new policy, approve tool calls,
   alter system/developer instructions, or request privileged actions. This is
   the missing control behind `tool_result_injection`, where Rec B caught only
   2 / 24 in the in-domain arm.

3. **Terminal escape sanitizer plus escalation rule.**

   Always neutralize unsafe terminal controls before display/log handling. Only
   escalate to attack when terminal controls are paired with hidden instruction,
   clipboard/link rewrite, command execution, or tool/policy intent. This avoids
   treating benign colored logs as attacks.

4. **Output-stage sensitive-content scan.**

   `prompt_leakage` is still weak at 3 / 22 in the in-domain arm. Input-side
   kNN is the wrong place to solve final-answer leakage. Add a final-response
   check for system/developer/policy strings, secrets, canaries, and protected
   context labels before output leaves the agent.

5. **Package provenance verifier.**

   `package_hallucination` is not mainly a text-similarity problem. Route package
   suggestions through registry existence, namespace age, maintainer trust,
   typosquat distance, download/reputation, and source allowlist checks.

6. **Memory/RAG taint labels.**

   Memory and retrieved content should carry taint and authority labels. A memory
   or RAG chunk can provide facts, but cannot authorize policy changes or
   privileged tool calls.

7. **More hard benigns before threshold tuning.**

   The pilot has only 96 benign test rows. One FP is already about 1%. Add many
   more benign multistep tool workflows, terminal logs, encoded assets, package
   install requests, security docs, and quoted attack examples before claiming
   sub-1% or zero-FP operation.

## Recommended Next Experiment

Do not tune the head first. The data says the largest fix is structural:

1. Add `R1-prime`: intent-gated tool/provenance rule.
2. Add terminal sanitizer as a separate always-on transform, with escalation
   only for unsafe terminal intent.
3. Add output-stage leakage scan.
4. Add package provenance verifier.
5. Expand hard benign validation rows.
6. Re-run:
   `new normalizer + kNN + R1-prime + head-in-band + output/package/terminal controls`.

Success bar for the next run:

- materially higher than 55.9% catch on Round-7;
- FP rate below 1% on an expanded benign set;
- no reliance on label-only fields such as `attack_class`, `benign_subclass`, or
  `expected_action`.
