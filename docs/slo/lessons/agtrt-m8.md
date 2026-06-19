# Lessons — agtrt M8

- **`html.escape(quote=True)` on EVERY interpolated field is the XSS control.** The product renders control ids / trap classes / remediation into HTML; any of those could carry a crafted `<script>` from an upstream scenario. Escaping at the render boundary (not trusting the data) is the CWE-79 fix the /slo-critique flagged (F-SEC-3).
- **"Offline + self-contained" is testable.** Assert the HTML has zero `http(s)://` / `<script src>` / CDN references — that proves it opens with no network and pulls no external code (no supply-chain or tracking surface in a shared artifact).
- **Evidence, not a score.** The product deliberately has no single "overall score" / pass badge — only per-control counts + evidence levels + the disclaimer. A test asserts the absence of "overall score" so the no-certification posture can't regress into a badge.
- **Stayed off M4's reporter.** M8 only READS the M4 scorecard JSON and adds `product/`; it doesn't modify `scorecard.py`, so it composes cleanly with M5/M7 (which also don't touch product/).
