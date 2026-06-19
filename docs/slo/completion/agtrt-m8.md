# Completion Summary — agtrt M8 (Shareable evidence scorecard product)

**Outcome delivered (oc-8):** the assessing engineer generates a shareable scorecard (HTML+MD) from a run and hands it to a stakeholder, who reads it as honest evidence-level results — not a certification. Offline, raw-free, no badge.

## Evidence

| Step | Command | Result |
|---|---|---|
| oc-8 front-to-end | `python product/render.py scorecard_report.json -o out/` | `out/scorecard.html` + `.md`, `certification_claim:false`, exit 0 |
| No certification (abuse-4) | scan HTML+MD | `certification_claim` + "not a certification" shown; zero cert terms; no "overall score" badge |
| HTML-escaped (CWE-79) | a control id `<script>alert(1)</script>` | rendered as `&lt;script&gt;…` — no executable injection |
| Offline + raw-free | scan HTML | zero external `http(s)`/CDN/`<script src>` refs; opens with no network |
| Empty run | zero results | empty-but-valid; disclaimer still present |
| Full tests | unittest discover | 46 passed (this branch: M1–M4 + win M3 fix + M8) |
| Static | `py_compile` + `git diff --check` | clean |

## What landed (M8 file allow-list)
- `product/render.py` — stdlib renderer (no JS framework, no server); `html.escape` on every interpolated field; prominent `certification_claim:false` disclaimer; self-contained inline CSS; HTML + Markdown.
- `tests/test_product.py` — 5 tests (oc-8, no-cert, XSS-escape, offline, empty-run).

## Design note
Renders **evidence levels, never a single mystery score or a pass/cert badge**. Built on the M4 reporter's JSON; no telemetry, no external references — opens offline and is safe to share.

## DoD: met (outcome-first — oc-8 passes front-to-end). Tracker M8 → `done`. **M8 is the terminal milestone for the linux lane.**
