"""Shared helpers for build.py and check.py (people identifier URLs, owner rulings 2026-11-18 items 1 and 1b)."""
import csv, hashlib, html, io, os, re, sys, unicodedata
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PERSIST = "/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/people-identifier-urls-2026-11-18/"
sys.path.insert(0, os.path.join(REPO, "scripts"))
from people_url import has_account_identifier  # the function V-62 uses (urlsplit tokens, not a regex)
URL_COLS = ("public_profile_url", "lab_url", "sources")
ALLOWED_COLS = {"public_profile_url", "lab_url", "sources", "last_verified"}
EVD_LO, EVD_HI = 396100, 396199
TODAY = "2026-11-18"
CREATED_BY = "claude-code atlas-w18-peopleurl"
# Scrub forward (owner rulings 2026-11-18 items 1/1b, 2026-11-18b item 3; tasks/identifier-url-scrub-2026-11-19): the
# committed manifest.csv carries placeholders, the private persist copy the fetched URLs. build.py writes redact(persist)
# and check.py requires committed == redact(persist), so a replay never restores an account URL to tasks/.
# This is the one redactor: tasks/identifier-url-scrub-2026-11-19/scrub.py imports scan() from here (it must live in this
# folder, because scripts/run_task_checks.py replays this task's check at its own commit with only this folder overlaid).
_END = r"[^\s,;\"'()<>\[\]{}`|#\\]"  # a URL also ends at a table pipe, a fragment and a backslash
_UC = r"(?:(?<=//)|(?<![\w./-]))(?i:researchdirectory\.uc\.edu)\.?/p/[A-Za-z0-9]" + _END + "*"  # the host itself is the form
_OTHER = r"[\w.-]+\.[A-Za-z]{2,}\.?(?::\d+)?(?:/" + _END + r"*?)?(?:[?&](?:u|unid)=|/~)[A-Za-z0-9]" + _END + "*"
_TOKEN = re.compile(r"(?:https?://)?(?:" + _UC + "|" + _OTHER + ")")
_ACCOUNT = re.compile(r"([?&]u=|[?&]unid=|/~|(?i:researchdirectory\.uc\.edu)\.?/p/)([A-Za-z0-9][A-Za-z0-9._%-]*)")


def _placeholder(kind):
    return "<acct>" if kind == "/~" else "<shortname>" if kind.endswith("/p/") else "<id>"


def _redact_token(tok):
    """(redacted URL, accounts redacted, extra repeats of an account elsewhere in the same URL)."""
    values = [(m.group(1), m.group(2)) for m in _ACCOUNT.finditer(tok)]
    new = _ACCOUNT.sub(lambda m: m.group(1) + _placeholder(m.group(1)), tok)
    extra = 0
    for kind, v in values:
        new, k = re.subn(r"(?<![A-Za-z0-9])" + re.escape(v) + r"(?![A-Za-z0-9])", _placeholder(kind), new)
        extra += k
    return new, len(values), extra


def scan(text):
    """(text with every account in every URL replaced by its placeholder, accounts redacted, extra repeats)."""
    sites = extra = 0

    def sub(m):
        nonlocal sites, extra
        new, s, e = _redact_token(m.group(0))
        sites += s; extra += e
        return new
    return _TOKEN.sub(sub, text), sites, extra


def redact(text):
    return scan(text)[0]


def read_csv(text):
    return list(csv.DictReader(io.StringIO(text, newline="")))

def has_id(cell):
    return has_account_identifier(cell)

def sources_list(cell):
    return [s for s in (cell or "").split(";") if s]

def _clean(s):
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("–", "-").replace("—", "-")
    return " ".join(s.lower().split())

def manifest():
    """url -> sha256 (last fetch wins)."""
    return {r["url"]: r["sha256"] for r in csv.DictReader(open(PERSIST + "manifest.csv"))}

def page_text(sha):
    raw = open(PERSIST + sha, "rb").read()
    if hashlib.sha256(raw).hexdigest() != sha:
        raise ValueError(f"stored page {sha[:12]} does not match its sha256")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", raw.decode("utf-8", "ignore"), flags=re.S)
    return _clean(html.unescape(re.sub(r"<[^>]+>", " ", t)))

def in_order(text, segments):
    """Every segment is found, each after the end of the previous one."""
    pos = 0
    for seg in segments:
        i = text.find(_clean(seg), pos)
        if i < 0:
            return False
        pos = i + len(_clean(seg))
    return True

SEP = " … "  # joins quote segments in an evidence note; contact details between segments are omitted
