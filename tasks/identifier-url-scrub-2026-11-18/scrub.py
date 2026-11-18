#!/usr/bin/env python3
"""Scrub personal account identifiers from URLs in historical task files (owner rulings 2026-11-18 items 1/1b, "scrub forward").

In every URL that carries an account, `?u=<value>` / `&u=<value>` becomes `?u=<id>` / `&u=<id>`, `/~<account>` becomes
`/~<acct>`, and any other occurrence of that same value inside the same URL (for example a filename `name-<acct>.html`)
becomes `<acct>` or `<id>` too. Nothing outside the URL changes.
Scope: every tracked file under tasks/ and docs/ (never data/; people rows are remediated by their own lane under V-62).
Usage: scrub.py [--apply]  -- without --apply it only counts. --apply writes manifest.csv (path, sites, extra in-URL
repeats, sha256 before and after) and refuses to overwrite an existing manifest.
"""
import argparse, csv, hashlib, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = Path(__file__).resolve().parent / "manifest.csv"
# a URL token (scheme optional) that carries an account; it ends at whitespace, a comma, a quote, a bracket or a backtick,
# so Markdown prose after `)` is never part of it
TOKEN = re.compile(r"(?:https?://)?[\w.-]+\.[A-Za-z]{2,}(?::\d+)?(?:/[^\s,\"'()<>\[\]`]*?)?(?:[?&]u=|/~)[A-Za-z0-9][^\s,\"'()<>\[\]`]*")
ACCOUNT = re.compile(r"([?&]u=|/~)([A-Za-z0-9][A-Za-z0-9._%-]*)")


def tracked():
    out = subprocess.run(["git", "ls-files", "-z", "--", "tasks", "docs"], cwd=ROOT, capture_output=True, check=True).stdout
    return [p for p in out.decode().split("\0") if p]


def redact_token(tok):
    """Return (redacted token, accounts redacted, extra repeats of an account elsewhere in the token)."""
    values = [(m.group(1), m.group(2)) for m in ACCOUNT.finditer(tok)]
    new = ACCOUNT.sub(lambda m: m.group(1) + ("<acct>" if m.group(1) == "/~" else "<id>"), tok)
    extra = 0
    for kind, v in values:
        rep = re.compile(r"(?<![A-Za-z0-9])" + re.escape(v) + r"(?![A-Za-z0-9])")
        new, k = rep.subn("<acct>" if kind == "/~" else "<id>", new)
        extra += k
    return new, len(values), extra


def scan(text):
    sites = extra = 0

    def sub(m):
        nonlocal sites, extra
        new, s, e = redact_token(m.group(0))
        sites += s; extra += e
        return new
    return TOKEN.sub(sub, text), sites, extra


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    if a.apply and MANIFEST.exists():
        sys.exit("manifest.csv exists: the scrub was already applied; restore the base files before re-applying")
    rows, total_sites, total_extra = [], 0, 0
    for p in tracked():
        f = ROOT / p
        try:
            text = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue  # binary: no line-level URL to rewrite
        new, sites, extra = scan(text)
        if not sites:
            continue
        if scan(new)[1]:
            sys.exit(f"FAIL: {p} still carries an account after redaction")
        total_sites += sites; total_extra += extra
        rows.append((p, sites, extra, hashlib.sha256(text.encode()).hexdigest(), hashlib.sha256(new.encode()).hexdigest()))
        if a.apply:
            f.write_text(new, encoding="utf-8")
    if a.apply and rows:
        with open(MANIFEST, "w", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["path", "sites", "extra_in_url", "sha256_before", "sha256_after"])
            w.writerows(rows)
    print(f"{'APPLIED' if a.apply else 'DRY'}: {total_sites} sites (+{total_extra} repeats inside the same URLs) in {len(rows)} files")


if __name__ == "__main__":
    main()
