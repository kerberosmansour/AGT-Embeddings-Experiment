# AGT Red Team Measurement Suite v2

This directory holds the 240-row measurement suite. The original
`benchmarks/agent-redteam/scenarios/` directory remains the 24-row smoke suite.

Shape:

- 6 trap classes x 40 rows = 240 rows.
- Per trap class: 8 canonical positives, 16 evasion positives, 8 hard-benign
  negatives, 8 near-miss negatives.
- Every row carries `measurement_suite`, `scenario_kind`, `evasion_technique`,
  `expected_control_behavior`, and `live_probe`.
- `views.agent_visible` remains a synthetic L2 label surface. Live Goose runs use
  `live_probe.agent_visible` instead.
- Positive and near-miss live probes expect no tool use. Hard-benign live probes
  expect one harmless `printf AGT_LIVE_PROBE_*` shell call, giving the live path
  both catch-rate and false-positive/utility evidence without real side effects.

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

The live path is still opt-in and inherits the M6 sandbox/credential gates.
Rows with a completed `live_probe` run are L3 behavioural evidence whether the
expected outcome is a contained shell trace or no tool use.
