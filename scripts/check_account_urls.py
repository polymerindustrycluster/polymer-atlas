#!/usr/bin/env python3
"""CI guard: no personal-account identifier URL in a tracked file under tasks/ or docs/.

Owner rulings 2026-11-18 items 1/1b and 2026-11-18b item 3 bar `?u=`, `?unid=`, `/~<account>` and
`researchdirectory.uc.edu/p/<shortname>` URLs. V-62 enforces them on people rows; the owner chose on 2026-11-19 to
guard tasks/ and docs/ as well, after one such URL reached main from a harness without the local pre-push scan.

A file is read by its BOM (UTF-8, UTF-16 or UTF-32; UTF-8 otherwise). Each line is decoded (JSON `\\/`, `\\uXXXX`
and `\\xHH` escapes, HTML entities), and its percent-decoded copy is read too, so a URL carried inside another URL's
query (`?next=https%3A...`) is seen. Every URL-shaped substring is then taken wherever it sits: with a scheme or
scheme-relative (`//host/...`), or a bare `host.tld/...` or `host.tld?...`, inside quotes, a Markdown link or
`url=...`, and both ending at `;`, `,` and parentheses and running through them (path parameters such as
`;jsessionid=`). Each one is judged by scripts/people_url.url_has_account, the V-62 test, which also reads
percent-encoding and ports, when its percent-decoded text shows `u=`, `unid`, `~` or the UC host. This is a guard
against accidental leaks in ordinary file formats; no pattern check can stop deliberate obfuscation. Placeholders (`<id>`, `<acct>`, `<shortname>`) pass.
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
def _url(stop):
    return re.compile(r"(?:[A-Za-z][A-Za-z0-9+.-]*:)?//" + stop + "+|[\\w.-]+\\.[A-Za-z]{2,}\\.?(?::\\d+)?[/?]" + stop + "*")


URLS = (_url(r"[^\s\"'`<>()\[\]{}|,;\\]"), _url(r"[^\s\"'`<>\[\]{}|\\]"))  # strict, and through ; , ( )
# a URL carried inside another: a query value that is itself a URL (`?next=https://...`), or a scheme mid-path
NESTED = re.compile(r"(?<==)(?=(?:[A-Za-z][A-Za-z0-9+.-]*:)?//|[\w.-]+\.[A-Za-z]{2,}\.?(?::\d+)?[/?])"
                    r"|(?<=[^\w+.-])(?=[A-Za-z][A-Za-z0-9+.-]*://)")


def candidates(view):
    for rx in URLS:
        for u in rx.findall(view):
            yield u
            for m in NESTED.finditer(u):
                n = rx.match(u, m.start())
                if n:
                    yield n.group(0)
LOOSE = re.compile(r"u=|unid|~|researchdirectory", re.I)  # needed (after unquote) for any account form
FILE_HINT = re.compile(r"u|~|%7e|%75|%55|\\x|&#|&tilde", re.I)  # coarse: every account form has a u or ~, plain or escaped
ESC = re.compile(r"\\u([0-9a-fA-F]{4})|\\x([0-9a-fA-F]{2})")
BOMS = ((b"\xef\xbb\xbf", "utf-8-sig"), (b"\xff\xfe\x00\x00", "utf-32"), (b"\x00\x00\xfe\xff", "utf-32"),
        (b"\xff\xfe", "utf-16"), (b"\xfe\xff", "utf-16"))


def decode(line):
    return html.unescape(ESC.sub(lambda m: chr(int(m.group(1) or m.group(2), 16)), line.replace("\\/", "/")))


def read(data):
    enc = next((e for b, e in BOMS if data.startswith(b)), "utf-8")
    return data.decode(enc, "replace")


def findings(text):
    """Line numbers (1-based) of lines holding an account URL."""
    if not FILE_HINT.search(text):
        return []
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        d = decode(line)
        views = (d, unquote(d))
        if not any(LOOSE.search(v) for v in views):
            continue
        # url_has_account prefixes "//" when there is no "://", so a scheme-relative URL is passed without its own "//"
        if any(LOOSE.search(unquote(u)) and url_has_account(u[2:] if u.startswith("//") else u)
               for v in views for u in candidates(v)):
            out.append(i)
    return out


def main():
    out = subprocess.run(["git", "ls-files", "-z", "--", "tasks", "docs"], cwd=ROOT, capture_output=True, check=True).stdout
    paths = [p for p in out.decode().split("\0") if p]
    if not paths:
        sys.exit("check_account_urls: git ls-files listed no files under tasks/ or docs/; nothing inspected")
    bad = [f"{p}:{n}" for p in paths for n in findings(read((ROOT / p).read_bytes()))]
    for b in bad:
        print(f"{b}: personal-account identifier URL (?u=, ?unid=, /~ or researchdirectory.uc.edu/p/); redact it "
              "with tasks/identifier-url-scrub-2026-11-19/scrub.py's placeholders (owner rulings 2026-11-18, 2026-11-18b)")
    print(f"check_account_urls: {len(paths)} files inspected under tasks/ and docs/, {len(bad)} lines with an account URL")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
