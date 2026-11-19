#!/usr/bin/env python3
"""CI guard: no personal-account identifier URL in a tracked file under tasks/ or docs/.

Owner rulings 2026-11-18 items 1/1b and 2026-11-18b item 3 bar `?u=`, `?unid=`, `/~<account>` and
`researchdirectory.uc.edu/p/<shortname>` URLs. V-62 enforces them on people rows; the owner chose on 2026-11-19 to
guard tasks/ and docs/ as well, after one such URL reached main from a harness without the local pre-push scan.

Each line is decoded first (JSON `\\/` and `\\uXXXX` escapes, HTML entities). Every URL-shaped substring is then
taken wherever it sits: with a scheme or scheme-relative (`//host/...`), or a bare `host.tld/...` or `host.tld?...`,
inside quotes, a Markdown link or `url=...`. Each one is judged by scripts/people_url.url_has_account, the V-62 test,
which also reads percent-encoding and ports. A substring is only judged when its percent-decoded text shows `u=`,
`unid`, `~` or the UC host, so ordinary links are never parsed. Placeholders (`<id>`, `<acct>`, `<shortname>`) pass.
data/ is out of scope: V-62 covers people rows and old evidence rows are append-only. Prints path:line only, never
the URL. Exit 1 on any finding.
"""
import html
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

from people_url import url_has_account

ROOT = Path(__file__).resolve().parents[1]
STOP = r"[^\s\"'`<>()\[\]{}|,;\\]"
URL = re.compile(r"(?:[A-Za-z][A-Za-z0-9+.-]*:)?//" + STOP + "+|[\\w.-]+\\.[A-Za-z]{2,}\\.?(?::\\d+)?[/?]" + STOP + "*")
LOOSE = re.compile(r"u=|unid|~|researchdirectory", re.I)  # needed (after unquote) for any account form
FILE_HINT = re.compile(r"u=|unid|~|%7e|%75|\\u00|&#|&tilde|researchdirectory", re.I)
U_ESC = re.compile(r"\\u([0-9a-fA-F]{4})")


def decode(line):
    return html.unescape(U_ESC.sub(lambda m: chr(int(m.group(1), 16)), line.replace("\\/", "/")))


def findings(text):
    """Line numbers (1-based) of lines holding an account URL."""
    if not FILE_HINT.search(text):
        return []
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        if not FILE_HINT.search(line):
            continue
        # url_has_account prefixes "//" when there is no "://", so a scheme-relative URL is passed without its own "//"
        if any(LOOSE.search(unquote(u)) and url_has_account(u[2:] if u.startswith("//") else u) for u in URL.findall(decode(line))):
            out.append(i)
    return out


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
