# Corpus Gap Report (scratch)

This report is metadata-only. It intentionally does not include raw prompt text.

## Coverage Matrix

- Behavioural Control: 5 rows; controls AGT-AC-004, AGT-AC-005, AGT-AC-011, AGT-AC-012; fixtures mock_tool, text_only
- Cognitive State: 1 rows; controls AGT-AC-007; fixtures mock_tool
- Content Injection: 2 rows; controls AGT-AC-001, AGT-AC-003; fixtures fixture
- Human-in-the-Loop: 1 rows; controls AGT-AC-006; fixtures mock_tool
- Semantic Manipulation: 4 rows; controls AGT-AC-002, AGT-AC-014; fixtures text_only
- Systemic: 1 rows; controls AGT-AC-010; fixtures mock_tool

## Decision-Useful Gaps

- Add more Content Injection fixtures with human/agent view divergence.
- Add Systemic multi-agent propagation fixtures.
- Add Human-in-the-Loop approval bypass and approval fatigue fixtures.
- Increase Cognitive State multi-session memory poisoning examples.
- Separate hard-benign must-not-block controls from attack rows.
