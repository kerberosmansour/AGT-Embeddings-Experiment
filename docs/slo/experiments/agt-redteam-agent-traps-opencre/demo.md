# AGT Red Team Agent Traps OpenCRE — Demo Pack

## One-Sentence Magic

AGT Red Team can move from prompt-injection rows to a standards-linked agent-trap benchmark: every scenario maps to controls, candidate OpenCRE relations, evidence level, and remediation, and can be tested first in deterministic mocks before any live-agent run.

## Reproduce The Evidence

```bash
python3 experiments/agt-redteam-agent-traps-opencre/s1-schema/validate_scenarios.py \
  experiments/agt-redteam-agent-traps-opencre/s1-schema/examples/*.json
python3 experiments/agt-redteam-agent-traps-opencre/s3-content-fixtures/extract_fixture_views.py
python3 experiments/agt-redteam-agent-traps-opencre/s4-mock-tools/mock_tools.py
```

## Evidence Locations

| Evidence | Location |
|---|---|
| Scenario schema + 24 examples | `experiments/agt-redteam-agent-traps-opencre/s1-schema/` |
| Metadata-only gap map | `experiments/agt-redteam-agent-traps-opencre/s2-gap-map/` |
| Content fixture divergence pack | `experiments/agt-redteam-agent-traps-opencre/s3-content-fixtures/` |
| Mock attempted/executed tool traces | `experiments/agt-redteam-agent-traps-opencre/s4-mock-tools/` |
| AGT-AC control mapping pack | `experiments/agt-redteam-agent-traps-opencre/s5-opencre/` |
| Evidence-level scorecard prototype | `experiments/agt-redteam-agent-traps-opencre/s6-scorecard/` |
| Goose adapter dry-run contract | `experiments/agt-redteam-agent-traps-opencre/s7-goose-adapter/` |
| Promotion split | `experiments/agt-redteam-agent-traps-opencre/s8-promotion/` |

## Security Posture

This is internal, scratch-only, synthetic evidence. It does not claim official OWASP/OpenCRE certification, does not run Goose or live tools, and does not open an upstream PR.
