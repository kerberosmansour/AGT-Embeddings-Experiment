# Lessons — e1sab M1 (structural rules + combined-stack eval)

## Headline
- Deployable captain-obvious stack = **embedding(zero-FP) OR R1 = 81% block @ 0% false-block.**
- **R1** (untrusted + tool call) blocks **100% of the four action families**
  (tool_abuse, output_exfiltration, indirect_injection, data_boundary_abuse)
  at **0% false-block** — exactly the families detection capped on in round 6.
- **R2** (sensitive-sink + non-user) is a trap: **100% false-block** on
  `high_entropy_structured_data` and `tool_policy_documentation`, **0** extra
  attacks. The per-rule benign measurement is what caught it — "captain obvious"
  must be measured against benign traffic, not assumed.

## Residual (3 families < 60%, each with a named fix)
- prompt_leakage 0% → no tool call (it's an output) → needs IFC output-label rule.
- tool_result_injection 37% → source is `tool_output` not `untrusted` → R1′ treating tool-output as semi-trusted.
- memory_poisoning 48% → write not flagged as untrusted tool call → memory-write taint rule.

## Design / correctness
- No model run: reused committed `m1-gate0` `pred_attack` (zero-FP decision).
- Ground-truth fields (`expected_action`,`risk_level`) asserted out of every rule.
- Validator recomputes every by-technique rate from the per-row file (exact match).
- Rules fixed before the run; deterministic; round-4/round-6 artifacts byte-identical.

## Method note
- Pre-registered "combined" used R4 (R1∨R2) and failed safety (14% FP) because of
  R2. Reported honestly, then derived the corrected deployable stack (emb∨R1).
  The failure of the pre-registered union is itself the finding.
