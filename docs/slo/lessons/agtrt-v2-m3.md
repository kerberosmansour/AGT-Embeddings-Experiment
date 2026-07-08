# Lessons Learned - agtrt-v2 Milestone 3

## What changed
- Extended the scorecard with measurement metrics while preserving evidence-level reporting.

## Assumptions verified
- The L2 projection can expose canonical catch rate, evasion catch rate, evasion degradation, false-positive rate, and utility-preservation rate.
- Unmeasured live rows need their own count so live gaps are not hidden as control wins.

## Rules for the next milestone
- Join live result JSONL back to scenario metadata before reporting metrics.
