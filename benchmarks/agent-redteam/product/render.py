#!/usr/bin/env python3
"""Shareable evidence-scorecard product renderer (M8) — stdlib-only.

Front-to-end (oc-8): the assessing engineer runs

    python render.py <scorecard_report.json> -o <out_dir>

and gets `out/scorecard.html` (self-contained, offline) + `out/scorecard.md`
they can hand to a stakeholder. The artifact renders EVIDENCE LEVELS with a
prominent `certification_claim: false` disclaimer — never a certification, a
pass/fail badge, or a single mystery score. Every interpolated field is
HTML-escaped (no XSS via a crafted scenario/control name, CWE-79). No external
script/style/network — it opens offline and is raw-free.

Exit codes: 0 ok | 1 input error | 2 usage.
"""
import argparse
import html
import json
import sys
from pathlib import Path

_CSS = (
    "body{font-family:system-ui,sans-serif;max-width:48rem;margin:2rem auto;padding:0 1rem}"
    ".disclaimer{border:2px solid #b45309;background:#fffbeb;padding:.75rem 1rem;border-radius:.5rem}"
    "table{border-collapse:collapse;width:100%}td,th{border:1px solid #ddd;padding:.25rem .5rem;text-align:left}"
    "code{background:#f3f4f6;padding:.1rem .3rem;border-radius:.2rem}"
)


def _e(value):
    """HTML-escape any interpolated value (CWE-79)."""
    return html.escape(str(value), quote=True)


def render_html(report):
    cert = str(report.get("certification_claim", False)).lower()
    rows = "".join(
        f"<tr><td><code>{_e(cid)}</code></td><td>{_e(count)}</td></tr>"
        for cid, count in report.get("controls", {}).items()
    ) or "<tr><td colspan=2><em>no results</em></td></tr>"
    remediation = "".join(f"<li>{_e(note)}</li>" for note in report.get("remediation", []))
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>AGT Red Team — Evidence Scorecard</title>
<style>{_CSS}</style></head>
<body>
<h1>AGT Red Team — Evidence Scorecard</h1>
<p class="disclaimer"><strong>This is evidence, not a certification.</strong>
<code>certification_claim: {_e(cert)}</code>.
Results are graded by evidence level (L0–L3), not a pass/fail badge or a single score.</p>
<ul>
<li>status: <code>{_e(report.get('status', ''))}</code></li>
<li>trap classes covered: {_e(', '.join(report.get('trap_classes', [])) or '(none)')}</li>
<li>evidence levels: {_e(', '.join(report.get('evidence_levels', [])) or '(none)')}</li>
<li>failures: {_e(report.get('failures', 0))}</li>
</ul>
<h2>Control coverage (AGT-AC)</h2>
<table><thead><tr><th>Control</th><th>Count</th></tr></thead><tbody>{rows}</tbody></table>
<h2>Remediation</h2>
<ul>{remediation or '<li>(none)</li>'}</ul>
</body></html>
"""


def render_md(report):
    cert = str(report.get("certification_claim", False)).lower()
    lines = [
        "# AGT Red Team — Evidence Scorecard",
        "",
        f"> **This is evidence, not a certification.** `certification_claim: {cert}`. "
        "Evidence levels (L0–L3), not a pass/fail badge or a single score.",
        "",
        f"- status: `{report.get('status', '')}`",
        f"- trap classes covered: {', '.join(report.get('trap_classes', [])) or '(none)'}",
        f"- evidence levels: {', '.join(report.get('evidence_levels', [])) or '(none)'}",
        f"- failures: {report.get('failures', 0)}",
        "",
        "## Control coverage (AGT-AC)",
    ]
    controls = report.get("controls", {})
    lines += [f"- `{cid}`: {count}" for cid, count in controls.items()] or ["- (no results)"]
    lines += ["", "## Remediation"]
    lines += [f"- {note}" for note in report.get("remediation", [])] or ["- (none)"]
    return "\n".join(lines) + "\n"


def main(argv):
    parser = argparse.ArgumentParser(prog="render.py")
    parser.add_argument("scorecard", help="scorecard_report.json from the M4 reporter")
    parser.add_argument("-o", "--out", required=True)
    try:
        args = parser.parse_args(argv[1:])
    except SystemExit:
        return 2
    try:
        report = json.loads(Path(args.scorecard).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"input error: {exc}", file=sys.stderr)
        return 1
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "scorecard.html").write_text(render_html(report), encoding="utf-8")
    (out / "scorecard.md").write_text(render_md(report), encoding="utf-8")
    print(json.dumps({"rendered": ["scorecard.html", "scorecard.md"],
                      "certification_claim": report.get("certification_claim", False)},
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
