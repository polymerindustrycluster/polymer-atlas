#!/usr/bin/env python3
"""CI guard: no personal-account identifier URL in a tracked file under tasks/ or docs/.

Owner rulings 2026-11-18 items 1/1b and 2026-11-18b item 3 bar `?u=`, `?unid=`, `/~<account>` and
`researchdirectory.uc.edu/p/<shortname>` URLs. V-62 enforces them on people rows; the owner chose on 2026-11-19 to
guard tasks/ and docs/ as well, after one such URL reached main from a harness without the local pre-push scan.

A file is read by its BOM (UTF-8, UTF-16 or UTF-32), as UTF-16 when it has none but NUL in every other byte, else
as UTF-8. Each line is decoded (JSON `\\/`, `\\uXXXX`
and `\\xHH` escapes, `\\n` `\\t` `\\r`, HTML entities), and its percent-decoded copy is read too, so a URL carried inside another URL's
query (`?next=https%3A...`) is seen. Every URL-shaped substring is then taken wherever it sits: with a scheme or
scheme-relative (`//host/...`), or a bare `host.tld/...` or `host.tld?...`, inside quotes, a Markdown link or
`url=...`, three ways: ending at `;`, `,`, parentheses, brackets and apostrophes; running through `;`, `,` and
parentheses (path parameters such as `;jsessionid=`); and running through all of them (a whole CSV cell, a bracketed
query filter, `o'brien` in a path). A bare host may be an IPv4 address. In an HTML page with `<base href>`, every
href, src and action value is also judged resolved against that base. Each one is judged by scripts/people_url.url_has_account, the V-62 test, which also reads
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
from urllib.parse import unquote, urljoin

from people_url import url_has_account

ROOT = Path(__file__).resolve().parents[1]
HOST = r"(?:[\w.-]+\.[A-Za-z]{2,}|\d{1,3}(?:\.\d{1,3}){3})\.?(?::\d+)?[/?]"  # a bare host.tld or IPv4, then / or ?


def _url(stop):
    return re.compile(r"(?:[A-Za-z][A-Za-z0-9+.-]*:)?//" + stop + "+|" + HOST + stop + "*")


# strict; through ; , ( ); and wide, through brackets and apostrophes too (`?f[0]=1&unid=`, `/o'brien?u=`, a CSV cell)
URLS = tuple(_url(s) for s in (r"[^\s\"'`<>()\[\]{}|,;\\]", r"[^\s\"'`<>\[\]{}|\\]", r"[^\s\"`<>|\\]"))
# a URL carried inside another: a query value that is itself a URL (`?next=https://...`), or a scheme mid-path
NESTED = re.compile(r"(?<==)(?=(?:[A-Za-z][A-Za-z0-9+.-]*:)?//|" + HOST + ")"
                    r"|(?<=[^\w+.-])(?=[A-Za-z][A-Za-z0-9+.-]*://)")


def candidates(view):
    for rx in URLS:
        for u in rx.findall(view):
            yield u
            for m in NESTED.finditer(u):
                n = rx.match(u, m.start())
                if n:
                    yield n.group(0)
BASE = re.compile(r"<base\b[^>]*?\bhref\s*=\s*[\"']?([^\"'\s>]+)", re.I)
ATTR = re.compile(r"\b(?:href|src|action)\s*=\s*[\"']?([^\"'\s>]+)", re.I)
LOOSE = re.compile(r"u=|unid|~|researchdirectory", re.I)  # needed (after unquote) for any account form
FILE_HINT = re.compile(r"u|~|%7e|%75|\\x|&#|&tilde", re.I)  # coarse: every account form has a u or ~, plain or escaped
ESC = re.compile(r"\\u([0-9a-fA-F]{4})|\\x([0-9a-fA-F]{2})|\\[ntr]")  # JSON \n \t \r become a space
BOMS = ((b"\xef\xbb\xbf", "utf-8-sig"), (b"\xff\xfe\x00\x00", "utf-32"), (b"\x00\x00\xfe\xff", "utf-32"),
        (b"\xff\xfe", "utf-16"), (b"\xfe\xff", "utf-16"))


def decode(line):
    return html.unescape(ESC.sub(lambda m: chr(int(m.group(1) or m.group(2), 16)) if m.group(1) or m.group(2) else " ",
                                 line.replace("\\/", "/")))


def read(data):
    enc = next((e for b, e in BOMS if data.startswith(b)), None)
    if not enc and b"\0" in data:  # UTF-16 without a BOM (Python's utf-16-le, Node's utf16le): NUL in every other byte
        enc = "utf-16-le" if data[1::2].count(0) > len(data) // 4 else "utf-16-be" if data[::2].count(0) > len(data) // 4 else None
    return data.decode(enc or "utf-8", "replace")


def findings(text):
    """Line numbers (1-based) of lines holding an account URL."""
    if not FILE_HINT.search(text):
        return []
    base = BASE.search(text)  # a saved HTML page: links resolve against its <base href>
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        d = decode(line)
        if base and any(url_has_account(urljoin(html.unescape(base.group(1)), a)) for a in ATTR.findall(d)):
            out.append(i)
            continue
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
