# Lessons — agtrt M1

- **Hyphen breaks `unittest discover`.** `benchmarks/agent-redteam/` (hyphen) is not an importable package name; `discover -s benchmarks/agent-redteam` returned 0 tests until `tests/__init__.py` was added. Kept the runbook's documented test command working by adding the package marker rather than renaming the dir.
- **Seed was faithful.** The s1 scratch schema/validator already matched the M1 contract (trap_class, success_conditions, views, AGT-AC controls). Productionizing = re-home + freeze + add structured error handling (catch `JSONDecodeError`/`OSError` → named reason, no traceback) + invariant/abuse tests + stdlib-only gate. No behavioural surprises.
- **Python 3.14 on the VM, runbook targets 3.12.** stdlib-only code (`json`, `re`, `pathlib`, `unittest`) is forward-compatible; oc-1 + tests green on 3.14. Flag for CI: pin setup-python 3.12 in M3 to match the operator-readiness row.
- **Raw-free/cert helpers live in the validator at M1** (concept only); the enforceable gate is M5. Kept them as pure functions the tests call, so the validator's main path stays schema-only (no premature M5 coupling).
