# AGT Red Team Measurement Suite v2

This directory holds the 240-row measurement suite. The original
`benchmarks/agent-redteam/scenarios/` directory remains the 24-row smoke suite.

Shape:

- 6 trap classes x 40 rows = 240 rows.
- Per trap class: 8 canonical positives, 16 evasion positives, 8 hard-benign
  negatives, 8 near-miss negatives.
- Every row carries `measurement_suite`, `scenario_kind`, `evasion_technique`,
  and `expected_control_behavior`.

Useful commands:

```bash
python benchmarks/agent-redteam/measurement/generate_measurement_scenarios.py
python benchmarks/agent-redteam/schema/validate_scenarios.py benchmarks/agent-redteam/measurement/scenarios/*.json
python benchmarks/agent-redteam/reporters/scorecard.py --controls benchmarks/agent-redteam/controls/agt-ac.csv --from-scenarios benchmarks/agent-redteam/measurement/scenarios --out /tmp/agtrt-l2
bash benchmarks/agent-redteam/run-measurement.sh
bash benchmarks/agent-redteam/run-measurement.sh --live
```

For bounded live slices, use:

```bash
bash benchmarks/agent-redteam/run-measurement.sh --live --limit=24
```

The live path is still opt-in and inherits the M6 sandbox/credential gates. Rows
without L3 traces are reported as unmeasured rather than silently counted as
control successes.
