"""Personal-account identifier test for people-row URL cells (SCHEMA v1.13.4, V-62). Shared by validate.py and the
people-identifier-urls task checker, so both read a URL the same way.

Each whitespace/`;`/`,`/quote-separated token is parsed with urlsplit ("//" prefixed when there is no scheme). A token
is an account URL when its host has a dot and either a query parameter named `u` has a value starting with a letter or
digit (any position) or a path segment starts with `~` plus a letter or digit. The fragment is ignored.
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
    if any(k == "u" and _ALNUM.match(v) for k, v in query):
        return True
    return any(seg.startswith("~") and _ALNUM.match(seg[1:2]) for seg in unquote(parts.path).split("/"))


def has_account_identifier(cell):
    return any(url_has_account(t) for t in _TOKENS.split(cell or "") if t)
