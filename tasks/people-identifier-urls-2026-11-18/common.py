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
