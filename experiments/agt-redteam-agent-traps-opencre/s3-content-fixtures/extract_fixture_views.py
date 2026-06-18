#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def human_view(text: str) -> str:
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"<[^>]+style=\"[^\"]*display\s*:\s*none[^\"]*\"[^>]*>.*?</[^>]+>", "", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+style=\"[^\"]*left\s*:\s*-9999px[^\"]*\"[^>]*>.*?</[^>]+>", "", text, flags=re.I | re.S)
    text = re.sub(r"aria-label=\"[^\"]*\"", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    text = re.sub(r"Hidden layer:.*", "", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", "", text)
    return " ".join(text.split())

def agent_view(text: str) -> str:
    comments = " ".join(re.findall(r"<!--\s*(.*?)\s*-->", text, flags=re.S))
    aria = " ".join(re.findall(r"aria-label=\"([^\"]*)\"", text))
    hrefs = " ".join(re.findall(r"\[[^\]]+\]\(([^\)]+)\)", text))
    stripped = re.sub(r"<[^>]+>", " ", text)
    return " ".join(part for part in " ".join([stripped, comments, aria, hrefs]).split())

def main() -> int:
    rows = []
    for path in sorted((ROOT / "fixtures").rglob("*")):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        h = human_view(text)
        a = agent_view(text)
        rows.append({
            "fixture": str(path.relative_to(ROOT)),
            "human_visible": h,
            "agent_visible": a,
            "divergence": h != a,
            "controls": ["AGT-AC-003"],
            "trap_class": "Content Injection",
        })
    report = {"fixtures": rows, "divergent_count": sum(1 for row in rows if row["divergence"])}
    (ROOT / "fixture_view_report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"fixtures": len(rows), "divergent_count": report["divergent_count"]}, sort_keys=True))
    return 0 if report["divergent_count"] >= 5 else 1

if __name__ == "__main__":
    raise SystemExit(main())
