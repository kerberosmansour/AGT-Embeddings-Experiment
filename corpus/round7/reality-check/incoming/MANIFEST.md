# Round 7 reality-check incoming manifest

Generated source-separated JSONL drop for the payload-derived reality-check arm.

Total JSONL rows: 2,213. All rows are from Apache-2.0 or MIT sources.
Unknown-license and proprietary datasets are excluded from this intake.

## Files

- `agentdojo-agentic-attacks.jsonl`: 325 rows; license=MIT; origin tags=AgentDojo
- `bipia-code-payloads.jsonl`: 100 rows; license=MIT; origin tags=Microsoft
- `garak-jailbreaks.jsonl`: 677 rows; license=Apache-2.0; origin tags=NVIDIA
- `garak-output-and-carriers.jsonl`: 37 rows; license=Apache-2.0; origin tags=NVIDIA
- `garak-system-prompt-extraction.jsonl`: 28 rows; license=Apache-2.0; origin tags=NVIDIA
- `giskard-prompt-injections.jsonl`: 35 rows; license=MIT; origin tags=Giskard-AI
- `jailbreakbench-artifacts.jsonl`: 816 rows; license=MIT; origin tags=JailbreakBench
- `open-prompt-injection-templates.jsonl`: 150 rows; license=MIT; origin tags=Open-Prompt-Injection
- `payloadsallthethings-prompt-injection.jsonl`: 43 rows; license=MIT; origin tags=PayloadsAllTheThings
- `pint-example-positives.jsonl`: 2 rows; license=MIT; origin tags=Lakera

## Source Links

- NVIDIA garak: https://github.com/NVIDIA/garak (Apache-2.0)
- AgentDojo: https://github.com/ethz-spylab/agentdojo (MIT)
- Microsoft BIPIA: https://github.com/microsoft/BIPIA (MIT)
- JailbreakBench artifacts: https://github.com/JailbreakBench/artifacts (MIT)
- Giskard prompt-injections: https://github.com/Giskard-AI/prompt-injections (MIT)
- PayloadsAllTheThings Prompt Injection: https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Prompt%20Injection (MIT)
- Open-Prompt-Injection: https://github.com/liu00222/Open-Prompt-Injection (MIT)
- Lakera PINT benchmark example file: https://github.com/lakeraai/pint-benchmark (MIT)

## License Gate

- Include only Apache-2.0 and MIT sources in `incoming/`.
- Do not add unknown-license, proprietary, NC-only, or unclear redistribution
  sources to this folder.
- If a useful unknown-license dataset is found, keep it outside the intake and
  document it as research-only until license clearance exists.

## Redaction Notes

- Live-looking emails, URLs, API keys, tokens, passwords, IBANs, long phone/account numbers, and card-like numbers are replaced with placeholders.
- Explicit harmful goals in JailbreakBench/GCG-style rows are replaced with `[HARMFUL_GOAL]`; some sensitive categories are replaced with `[DISALLOWED_CONTENT_CATEGORY]`, `[ILLEGAL_CONTENT_CATEGORY]`, or `[HARMFUL_SUBJECT]`.
- WHOIS carrier rows preserve field shape but reduce real registry values to labels plus placeholders.
- Placeholder rows are intentionally noted in-row. For benchmark runs that need
  realistic fake values, generate a separate synthetic-variation arm with
  `corpus/round7/reality-check/make_synthetic_variations.py`; see
  `corpus/round7/reality-check/SYNTHETIC_VARIATIONS.md`.

## Novelty supplement (linux-agent, 2026-06-11)

Six rows added to fill confirmed **zero-coverage** gaps — structurally-novel 2024
techniques the bulk sources above and our normalizer (leet/base64/homoglyph/
spacing/morse/…) do not handle. These are **structure-faithful, redacted
representative** rows (the published technique *wrapper* with the harmful target
reduced to `[HARMFUL_GOAL]`/`[HARMFUL_BEHAVIOR]`), not bulk dataset extracts —
the detector-relevant signal is the wrapper shape, not harmful content. Each
`why_novel` names the specific blind spot.

- `artprompt.jsonl`: 2 rows; license=MIT; origin=ArtPrompt (UW-NSL, ACL 2024) — ascii-art cloze masking; per-token normalizers never rebuild the masked word.
- `cipherchat-selfcipher.jsonl`: 2 rows; license=MIT; origin=CipherChat (RobustNLP, ICLR 2024) — SelfCipher (no real encoding, pure role frame) + Caesar "cipher-expert / do not translate" wrapper.
- `bon-jailbreaking.jsonl`: 2 rows; license=MIT; origin=Best-of-N (Hughes et al., 2024) — per-sample random capitalization / char-scramble / noise augmentation that defeats canonical-form matching.

### Source Links (novelty supplement)

- ArtPrompt: https://github.com/uw-nsl/ArtPrompt (MIT)
- CipherChat: https://github.com/RobustNLP/CipherChat (MIT)
- Best-of-N Jailbreaking: https://github.com/jplhughes/bon-jailbreaking (MIT)

Excluded (license not Apache-2.0/MIT-verifiable at intake time): FlipAttack
(no LICENSE file at source), llm-past-tense (no LICENSE file at source) — kept
out of `incoming/` per the license gate until clearance.
