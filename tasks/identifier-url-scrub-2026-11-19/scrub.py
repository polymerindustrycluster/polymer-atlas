#!/usr/bin/env python3
"""Scrub personal account identifiers from URLs in task and docs files (owner rulings 2026-11-18 items 1/1b and
2026-11-18b item 3, "scrub forward"; owner choice 2026-11-19: scrub, then guard tasks/ and docs/ in CI).

Extends tasks/identifier-url-scrub-2026-11-18/scrub.py (which covered `?u=` and `/~`) to the two forms ruled on
2026-11-18b. In every URL that carries an account:
  `?u=<value>` / `&u=<value>`        -> `?u=<id>` / `&u=<id>`
  `?unid=<value>` / `&unid=<value>`  -> `?unid=<id>` / `&unid=<id>`
  `/~<account>`                      -> `/~<acct>`
  `researchdirectory.uc.edu/p/<v>`   -> `researchdirectory.uc.edu/p/<shortname>`
and any other occurrence of the same value inside that URL gets the same placeholder. Nothing outside the URL changes.
Scope: every tracked file under tasks/ and docs/ (never data/: people rows are under V-62, evidence rows are append-only).
The authority for "still carries an account" is scripts/people_url.py, the helper V-62 uses; the run fails if any
redacted file still has one by that test.
Usage: scrub.py [--apply]  -- without --apply it only counts. --apply writes manifest.csv and refuses to overwrite it.
"""
import argparse, csv, hashlib, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from check_account_urls import findings  # noqa: E402  (the CI guard: same token test as V-62)

sys.path.insert(0, str(ROOT / "tasks" / "people-identifier-urls-2026-11-18"))
from common import scan  # noqa: E402  (the one redactor, shared with that task's manifest build and check)

MANIFEST = Path(__file__).resolve().parent / "manifest.csv"


def tracked():
    out = subprocess.run(["git", "ls-files", "-z", "--", "tasks", "docs"], cwd=ROOT, capture_output=True, check=True).stdout
    return [p for p in out.decode().split("\0") if p]


def selftest():
    # synthetic accounts, filled in at run time ({A}) so this file never holds an account URL for the CI guard to flag
    cases = {
        "see https://x.example.edu/people?unid={A}&x=1 now": "see https://x.example.edu/people?unid=<id>&x=1 now",
        "https://researchdirectory.uc.edu/p/{A}": "https://researchdirectory.uc.edu/p/<shortname>",
        "a;www.math.example.edu/~{A}/{A}-cv.pdf;b": "a;www.math.example.edu/~<acct>/<acct>-cv.pdf;b",
        "https://x.example.edu/?u={A}": "https://x.example.edu/?u=<id>",
        "https://researchdirectory.uc.edu/p/<shortname> stays": "https://researchdirectory.uc.edu/p/<shortname> stays",
        "**[v1.15]** and fisid_123 stay": "**[v1.15]** and fisid_123 stay",
        # Codex r1: nothing past a table pipe, nothing in a fragment, no UC host inside another site's path
        "https://x.example.org/?u={A}|{A}": "https://x.example.org/?u=<id>|{A}",
        "https://x.example.org/#?u={A}": "https://x.example.org/#?u={A}",
        "https://x.example.org/researchdirectory.uc.edu/p/{A}": "https://x.example.org/researchdirectory.uc.edu/p/{A}",
        # Codex r2: the value repeated earlier in the URL, and a bare UC host (common.redact is now this same scan)
        "https://x.example.org/{A}?unid={A}": "https://x.example.org/<id>?unid=<id>",
        "researchdirectory.uc.edu/p/{A}": "researchdirectory.uc.edu/p/<shortname>",
    }
    for src, want in cases.items():
        src, want = src.replace("{A}", "jq9"), want.replace("{A}", "jq9")
        assert ("jq9" not in want) or not findings(want), want  # what stays must be allowed
        assert ("jq9" not in src) or ("jq9" in want) or findings(src), src  # each redacted account is one the guard sees
        got = scan(src)[0]
        assert got == want, (src, got)
        assert not findings(got), got
    print("selftest OK:", len(cases), "cases")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.apply and MANIFEST.exists():
        sys.exit("manifest.csv exists: the scrub was already applied; restore the base files before re-applying")
    rows, total_sites, total_extra = [], 0, 0
    for p in tracked():
        f = ROOT / p
        try:
            text = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            if findings(f.read_bytes().decode("utf-8", "replace")):
                sys.exit(f"FAIL: {p} is not UTF-8 and carries an account; redact it by hand")
            continue
        new, sites, extra = scan(text)
        if not sites:
            continue
        left = findings(new)
        if left:
            sys.exit(f"FAIL: {p} still carries an account after redaction (lines {left})")
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
