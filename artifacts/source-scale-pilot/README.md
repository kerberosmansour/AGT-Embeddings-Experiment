# Source-Scale Pilot Summary

This directory contains sanitized Round-5 source-scale pilot metadata.

It intentionally does not include raw prompt/source rows. The pilot is useful
for methodology review: source-record review gates, matched controls,
family-based splits, leakage checks, validation-only threshold freeze, and
metadata-only embedding outputs.

It is not a performance claim, production claim, benchmark-coverage claim, or
permission to add runtime embedding behavior to AGT.

Files:

- `summary.json`: counts, hashes, validation outcomes, and conservative metric
  summary for the 72-row source-scale pilot.
