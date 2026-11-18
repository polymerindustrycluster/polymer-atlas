"""Personal-account identifier test for people-row URL cells (SCHEMA v1.13.4, widened at v1.15; V-62). Shared by validate.py and the
people-identifier-urls task checker, so both read a URL the same way.

Each whitespace/`;`/`,`/quote-separated token is parsed with urlsplit ("//" prefixed when there is no scheme). A token
is an account URL when its host has a dot and one of: a query parameter named `u` or `unid` has a value starting with a
letter or digit (any position); a path segment starts with `~` plus a letter or digit; or the host is exactly
researchdirectory.uc.edu (case-insensitive, one trailing root dot ignored) and the path is `/p/<value>` with the value
starting with a letter or digit (owner rulings 2026-11-18b item 3). The query key must be exactly `unid`. The fragment is
ignored. Placeholders (`unid=<id>`, `/p/<shortname>`) start with `<` and pass; `fisid_<id>` is accepted (owner rulings
2026-11-18b item 3; what the institution uses the number for is not established) and is not matched.
"""
import re
from urllib.parse import parse_qsl, unquote, urlsplit

_TOKENS = re.compile(r'[\s;,"]+')
_ALNUM = re.compile(r"[A-Za-z0-9]")


def url_has_account(token):
    u = token if "://" in token else "//" + token
    try:
        parts = urlsplit(u)
        host = parts.hostname or ""
        query = parse_qsl(parts.query, keep_blank_values=True)
    except ValueError:  # cannot be inspected: fail closed
        return True
    if "." not in host:
        return False
    if any(k in ("u", "unid") and _ALNUM.match(v) for k, v in query):
        return True
    segs = unquote(parts.path).split("/")
    if host.lower().rstrip(".") == "researchdirectory.uc.edu" and len(segs) >= 3 and segs[0] == "" and segs[1] == "p" and _ALNUM.match(segs[2][:1]):
        return True
    return any(seg.startswith("~") and _ALNUM.match(seg[1:2]) for seg in segs)


def has_account_identifier(cell):
    return any(url_has_account(t) for t in _TOKENS.split(cell or "") if t)
