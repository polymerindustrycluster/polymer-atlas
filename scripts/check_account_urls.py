#!/usr/bin/env python3
"""CI guard: no personal-account identifier URL in a tracked file under tasks/ or docs/.

Owner rulings 2026-11-18 items 1/1b and 2026-11-18b item 3 bar `?u=`, `?unid=`, `/~<account>` and
`researchdirectory.uc.edu/p/<shortname>` URLs. V-62 enforces them on people rows; the owner chose on 2026-11-19 to
guard tasks/ and docs/ as well, after one such URL reached main from a harness without the local pre-push scan.
A URL token is judged by scripts/people_url.url_has_account, the same test as V-62. Only tokens that show one of the
account forms are tested, so prose such as `**[v1.15]**` (which the parser cannot read) is never judged.
Placeholders (`<id>`, `<acct>`, `<shortname>`) pass. data/ is out of scope: V-62 covers people rows and old
evidence rows are append-only. Prints path:line only, never the URL. Exit 1 on any finding.
"""
import re
import subprocess
import sys
from pathlib import Path

from people_url import url_has_account

ROOT = Path(__file__).resolve().parents[1]
# wider than people_url._TOKENS (data cells): a URL inside quotes, backticks, brackets or a Markdown link is still read
TOKENS = re.compile(r"[\s;,\"'`()\[\]<>|]+")
FORM = re.compile(r"[?&](?:u|unid)=[A-Za-z0-9]|/~[A-Za-z0-9]|researchdirectory\.uc\.edu\.?/p/[A-Za-z0-9]", re.I)


def findings(text):
    """Line numbers (1-based) of lines holding an account URL."""
    if not FORM.search(text):
        return []
    return [i for i, line in enumerate(text.splitlines(), 1)
            if FORM.search(line) and any(t and FORM.search(t) and url_has_account(t) for t in TOKENS.split(line))]


def main():
    out = subprocess.run(["git", "ls-files", "-z", "--", "tasks", "docs"], cwd=ROOT, capture_output=True, check=True).stdout
    paths = [p for p in out.decode().split("\0") if p]
    if not paths:
        sys.exit("check_account_urls: git ls-files listed no files under tasks/ or docs/; nothing inspected")
    bad = [f"{p}:{n}" for p in paths for n in findings((ROOT / p).read_bytes().decode("utf-8", "replace"))]
    for b in bad:
        print(f"{b}: personal-account identifier URL (?u=, ?unid=, /~ or researchdirectory.uc.edu/p/); redact it "
              "with tasks/identifier-url-scrub-2026-11-19/scrub.py's placeholders (owner rulings 2026-11-18, 2026-11-18b)")
    print(f"check_account_urls: {len(paths)} files inspected under tasks/ and docs/, {len(bad)} lines with an account URL")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
