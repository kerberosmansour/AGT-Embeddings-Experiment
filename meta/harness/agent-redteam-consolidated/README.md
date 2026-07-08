# AGT Consolidated Static Harness

This directory contains metadata-only harnesses for
`docs/RUNBOOK-agt-redteam-benchmark-consolidation.md`.

M3 provides the L1 static tier:

```bash
python3 meta/harness/agent-redteam-consolidated/run_l1_static.py --out /tmp/agtrtc-l1
python3 meta/harness/agent-redteam-consolidated/validate_l1_static.py /tmp/agtrtc-l1/l1_static_report.json
```

The artifacts are non-certifying, raw-free, and static-only. They may identify
families that should receive L3 live containment sampling later, but they do
not provide L3 evidence.
