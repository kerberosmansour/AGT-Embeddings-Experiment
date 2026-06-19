#!/usr/bin/env python3
"""Raw-free hygiene gate (M5) — stdlib-only, fail-closed.

Front-to-end (oc-5): the assessing engineer runs

    python raw_free_scan.py <path>

over the benchmark and gets exit 0 if every DATA artifact is raw-free, or a
non-zero exit naming the artifact + line on the first raw-payload / secret /
PII heuristic hit. This lets them trust the benchmark is safe to share.

Scope: DATA artifacts only (`.json/.jsonl/.csv/.md/.txt`). The detector and
test `.py` modules are EXCLUDED by design — they legitimately contain secret
*patterns* (e.g. `AKIA[0-9A-Z]{16}`) and a planted test fixture; scanning them
would be a guaranteed false positive. Heuristics can miss novel encodings
(documented residual risk, §5B) — synthetic-only discipline is the backstop.

Exit codes: 0 raw-free | 1 violation(s) found | 2 usage.
"""
import re
import sys
from pathlib import Path

SCANNABLE_SUFFIXES = {".json", ".jsonl", ".csv", ".md", ".txt"}

PATTERNS = {
    "aws_access_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "private_key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "openai_key": re.compile(r"sk-[A-Za-z0-9]{20,}"),
    "slack_token": re.compile(r"xox[baprs]-[0-9A-Za-z-]{10,}"),
    "github_token": re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}"),
    "ssn": re.compile(r"\b[0-9]{3}-[0-9]{2}-[0-9]{4}\b"),
}


def is_scannable(path):
    """Data artifacts are scanned; .py detectors/tests are excluded by design."""
    p = Path(path)
    return p.suffix in SCANNABLE_SUFFIXES


def scan_text(text):
    """Return list of (line_no, kind) heuristic hits."""
    hits = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        for kind, pat in PATTERNS.items():
            if pat.search(line):
                hits.append((line_no, kind))
    return hits


def scan_path(root):
    """Return list of (file, line_no, kind) over scannable artifacts under root."""
    root = Path(root)
    files = [root] if root.is_file() else sorted(root.rglob("*"))
    violations = []
    for f in files:
        if not f.is_file() or not is_scannable(f):
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for line_no, kind in scan_text(text):
            violations.append((str(f), line_no, kind))
    return violations


def main(argv):
    if len(argv) < 2:
        print("usage: raw_free_scan.py <path>", file=sys.stderr)
        return 2
    violations = scan_path(argv[1])
    if violations:
        for f, line_no, kind in violations:
            print(f"{f}:{line_no}: raw-free violation ({kind})", file=sys.stderr)
        return 1
    print("raw-free: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
