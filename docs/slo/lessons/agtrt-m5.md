# Lessons — agtrt M5

- **The hygiene scanner must NOT scan its own detectors.** `raw_free_scan.py`, `validate_scenarios.py`, and the test files legitimately contain secret REGEX patterns (`AKIA[0-9A-Z]{16}`, `sk-…`) and a planted test fixture. Scanning `.py` would be a guaranteed false positive. Scope the gate to DATA artifacts (`.json/.jsonl/.csv/.md/.txt`) via `is_scannable()`; document the exclusion as deliberate.
- **Anti-vacuity is the load-bearing test.** A raw-free gate that never fires is worse than none. The planted-secret test (a synthetic `AKIA…` in a temp artifact MUST fail the gate) proves the gate actually detects — not that it passes vacuously.
- **DW ledger shifted under the founder's M6–M8 expansion.** Only DW-001 (content-fixtures) is still filed out; DW-002 (Goose) and DW-003 (OpenCRE) are now BUILT milestones, so M5 files exactly one issue, not three.
- **PII heuristics are conservative.** Kept to high-signal shapes (AWS/PEM/OpenAI/Slack/GitHub tokens, SSN) to avoid false positives on synthetic data (AGT-AC ids, ASI tags). Heuristics can miss novel encodings — documented residual risk; synthetic-only discipline is the real backstop.
