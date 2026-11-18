#!/usr/bin/env python3
"""Scrub personal account identifiers from URLs in historical task files (owner rulings 2026-11-18 items 1/1b, "scrub forward").

`?u=<value>` / `&u=<value>` becomes `?u=<id>` and `/~<account>` becomes `/~<acct>`; everything else on the line is unchanged.
Document-sharing links on *.widen.net carry a share token, not a person, and are left alone.
Scope: tracked files under tasks/ and docs/ (never data/; people rows are remediated by their own lane under V-62).
Usage: scrub.py [--apply] [--base REV]  -- without --apply it only counts. Writes manifest.csv (path, matches, sha256 at base, after).
"""
import argparse, csv, hashlib, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
URL = re.compile(r"(?:https?://)?([\w.-]+\.[A-Za-z]{2,})(?::\d+)?(?:/[^\s,\"]*?)?(?:[?&]u=|/~)[A-Za-z0-9][A-Za-z0-9._%-]*")
VALUE = re.compile(r"([?&]u=|/~)[A-Za-z0-9][A-Za-z0-9._%-]*$")
KEEP_HOST = re.compile(r"(?:^|\.)widen\.net$")


def tracked():
    out = subprocess.run(["git", "ls-files", "-z", "--", "tasks", "docs"], cwd=ROOT, capture_output=True, check=True).stdout
    return [p for p in out.decode().split("\0") if p and not p.startswith(str(HERE.relative_to(ROOT)))]


def redact(m):
    if KEEP_HOST.search(m.group(1)):
        return m.group(0)
    return VALUE.sub(lambda v: v.group(1) + ("<id>" if v.group(1) != "/~" else "<acct>"), m.group(0))


def scan(text):
    hits = [m for m in URL.finditer(text) if not KEEP_HOST.search(m.group(1))]
    return hits, URL.sub(redact, text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    rows, total, changed_sites = [], 0, 0
    for p in tracked():
        f = ROOT / p
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, IsADirectoryError):
            continue  # binary files cannot carry a line-level URL we would rewrite
        hits, new = scan(text)
        if not hits:
            continue
        total += len(hits)
        after_hits, _ = scan(new)
        changed_sites += len(hits) - len(after_hits)
        before_sha = hashlib.sha256(text.encode()).hexdigest()
        after_sha = hashlib.sha256(new.encode()).hexdigest()
        rows.append((p, len(hits), before_sha, after_sha))
        if a.apply:
            f.write_text(new, encoding="utf-8")
    if changed_sites != total:
        sys.exit(f"FAIL: {total} sites matched but {changed_sites} redacted")
    if a.apply:
        with open(HERE / "manifest.csv", "w", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["path", "sites", "sha256_before", "sha256_after"])
            w.writerows(rows)
    print(f"{'APPLIED' if a.apply else 'DRY'}: {total} sites in {len(rows)} files; {changed_sites} redacted")


if __name__ == "__main__":
    main()
