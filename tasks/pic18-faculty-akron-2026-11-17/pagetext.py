"""Shared page-text and quote helpers (frame.py, verdicts.py, check.py all use these, so the check is not self-confirming on a different parser)."""
import html, re
from pathlib import Path
P = Path("/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/pic18-faculty-akron-2026-11-17")
def text(sha):
    h = (P / sha).read_bytes().decode("utf-8", "replace")
    h = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", h, flags=re.S)
    return " ".join(html.unescape(re.sub(r"<[^>]+>", "\n", h)).split())
def squash(s):
    return " ".join(s.replace("’", "'").replace("“", '"').replace("”", '"').split())
def quote_in(q, sha):
    return squash(q) in squash(text(sha))

def redact(url):
    """Committed files never carry the UA network id in profile URLs (?u=<id>); the persist manifest keeps the real URL."""
    return re.sub(r"([?&]u=)[^&#\s,;]+", r"\1<id>", url)
