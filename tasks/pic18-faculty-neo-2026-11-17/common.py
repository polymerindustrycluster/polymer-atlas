import csv, re, unicodedata, os
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
def norm(n):
    n = unicodedata.normalize("NFKD", n).encode("ascii", "ignore").decode().lower()
    n = re.sub(r"\b(dr|phd|ph\.d|md|ms|bs|mba|scd|jr|sr|ii|iii)\b\.?", " ", n)
    n = re.sub(r"[^a-z ]", " ", n)
    return " ".join(n.split())
def toks(n):
    t = norm(n).split(); return (t[0], t[-1]) if t else ("", "")
def people():
    return list(csv.DictReader(open(os.path.join(REPO, "data/people.csv"))))

import html as _html, hashlib
PERSIST = "/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/pic18-faculty-neo-2026-11-17/"
def _clean(s):
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"').replace("–", "-").replace("—", "-")
    return " ".join(s.lower().split())
def page_text(sha):
    """Visible text of a stored witness, whitespace-collapsed, quotes normalized."""
    t = open(PERSIST + sha, errors="ignore").read()
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    return _clean(_html.unescape(t))
def quote_in(sha, quote):
    return _clean(quote) in page_text(sha)
def sha_ok(sha):
    return hashlib.sha256(open(PERSIST + sha, "rb").read()).hexdigest() == sha
def manifest():
    return {r["url"]: r["sha256"] for r in csv.DictReader(open(PERSIST + "manifest.csv"))}

CASE_DIR_SHA = "3b2f97896"  # prefix resolved below
MISSING = []
def case_entries():
    """Entries of the stored CWRU engineering directory page, keyed on profile anchors (not on 'Email:')."""
    f = [x for x in os.listdir(PERSIST) if x.startswith("3b2f9789")][0]
    t = open(PERSIST + f, errors="ignore").read()
    labs, seen = [], set()
    for m in re.finditer(r'<a [^>]*href="(/engineering/about/faculty-and-staff-directory/[^"]+)"[^>]*>(.*?)</a>', t, flags=re.S):
        lab = " ".join(_html.unescape(re.sub(r"<[^>]+>", " ", m.group(2))).split())
        if lab and "@" not in lab and m.group(1) not in seen: seen.add(m.group(1)); labs.append((lab, m.group(1)))
    t2 = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
    L = [l.strip() for l in _html.unescape(re.sub(r"<[^>]+>", "\n", t2)).split("\n") if l.strip()]
    pos = []; k = L.index(labs[0][0]); kept = []
    for lab, href in labs:
        try: k = L.index(lab, k); pos.append(k); kept.append((lab, href)); k += 1
        except ValueError: MISSING.append(lab)  # anchor whose name never appears as a line: reported, not guessed
    labs = kept
    out = []
    for i, (lab, href) in enumerate(labs):
        end = pos[i + 1] if i + 1 < len(labs) else len(L)
        body = [x for x in L[pos[i] + 1:end] if x != "Email:" and "@" not in x and not x.startswith(("Phone", "Fax"))]
        out.append((lab.split(",")[0], href, " | ".join(body)))
    assert len(out) == len(labs)
    return out
