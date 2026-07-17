# AGT Consolidated Static Harness

This directory contains metadata-only harnesses for
`docs/RUNBOOK-agt-redteam-benchmark-consolidation.md`.

M3 provides the L1 static tier:

```bash
python3 corpus/round7/generate-round7.py \
  --profile large \
  --out scratch/round7-large.jsonl \
  --manifest scratch/round7-large-manifest.json
python3 meta/harness/agent-redteam-consolidated/run_l1_static.py --out /tmp/agtrtc-l1
python3 meta/harness/agent-redteam-consolidated/validate_l1_static.py /tmp/agtrtc-l1/l1_static_report.json
```

The generated Round-7 corpus lives under the git-ignored `scratch/` directory.
Corpus-backed integration tests skip with the command above when those two
inputs are absent; deterministic smoke and unit tests continue to run.

The artifacts are non-certifying, raw-free, and static-only. They may identify
families that should receive L3 live containment sampling later, but they do
not provide L3 evidence.
