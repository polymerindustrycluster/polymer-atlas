#!/usr/bin/env python3
"""Check docs/ACQUISITION.md: every experiments-log row names an existing repo path or a known controller packet,
and the page carries no thread id, local path or spend figure. Run: python3 tasks/acquisition-record-2026-11-24/check.py"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs" / "ACQUISITION.md"
PACKETS = {"overture-pic18-2026-11-24", "google-places-pic18-2026-11-24", "requote-pilot-2026-11-24",
           "requote-all-2026-11-24", "matcher-eval-2026-11-22"}  # controller packets outside the repo
LEAKS = re.compile(r"thr_[a-z0-9]{6,}|/Users/|\.bb/|~/workspace|\btokens?\b|\$\d|per 1,000", re.I)


def log_rows(text):
    sec = text.split("## 3. Experiments log", 1)[1].split("\n## ", 1)[0]
    rows = [l for l in sec.splitlines() if l.startswith("| 20")]
    return [[c.strip() for c in l.strip().strip("|").split(" | ")] for l in rows]


def problems(text, root=ROOT):
    out = []
    rows = log_rows(text)
    if not rows:
        return ["no experiments-log rows found"]
    for r in rows:
        if len(r) != 7:
            out.append(f"{r[0]}: expected 7 columns, got {len(r)}")
            continue
        where = r[6]
        if "controller packet" in where:
            names = set(re.findall(r"`([^`]+)`", where))
            if not names or not names <= PACKETS:
                out.append(f"{r[0]} {where}: unknown controller packet")
            continue
        paths = re.findall(r"`([^`]+)`", where)
        if not paths:
            out.append(f"{r[0]}: where names no folder or file")
        out += [f"{r[0]}: {p} does not exist" for p in paths if not (root / p).exists()]
    out += [f"leak pattern: {m.group(0)}" for m in LEAKS.finditer(text)]
    return out


if __name__ == "__main__":
    text = DOC.read_text()
    bad = problems(text)
    # defect injection: a missing folder and a leaked thread id must both be caught
    fake = text.replace("`tasks/websites-2026-11-04`", "`tasks/no-such-folder-2026-01-01`", 1) + " thr_abc123xyz9"
    assert len(problems(fake)) >= 2, "injected defects were not caught"
    print(f"{len(log_rows(text))} experiments-log rows; {len(bad)} problems")
    for b in bad:
        print("  ", b)
    sys.exit(1 if bad else 0)
