#!/usr/bin/env python3
"""Raw-check the ownership lanes: re-fetch each source_url (Firecrawl main content, then full page, then Jina Reader)
and match the quote as a word sequence. Resumable: rows already in rawcheck.csv are skipped and each new row is
written as it is checked, so a stopped run loses at most one row.
    python3 tasks/ownership-status-2-2026-11-05/rawcheck_tool.py
"""
import csv, re, sys, unicodedata, urllib.request
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, r"C:\Users\JohnSwanson\Documents\pic-github\polymer-faculty-census")
from tools.layer_b_fetch import call, env  # noqa: E402
fc, key = env("FIRECRAWL_BASE_URL").rstrip("/"), env("FIRECRAWL_NAS_API_KEY")
W = lambda s: re.findall(r"[a-z0-9]+", unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower())


def pages(u):
    for main in (True, False):
        try:
            r = call(f"{fc}/v2/scrape", {"url": u, "formats": ["markdown"], "onlyMainContent": main}, {"Authorization": f"Bearer {key}"}, timeout=150)
            d = r.get("data") or {}
            if (d.get("metadata") or {}).get("statusCode") == 200:
                yield W(d.get("markdown"))
        except Exception:
            pass
    try:
        req = urllib.request.Request("https://r.jina.ai/" + u, headers={"Authorization": f"Bearer {env('JINA_API_KEY')}", "User-Agent": "polymer-atlas/1.0"})
        with urllib.request.urlopen(req, timeout=90) as resp:
            yield W(resp.read().decode("utf-8", "replace"))
    except Exception:
        pass


def found(u, q):
    q, seen = W(q), False
    for p in pages(u):
        seen = True
        if q and any(p[i:i + len(q)] == q for i in range(len(p) - len(q) + 1)):
            return "yes"
    return "no" if seen else "unfetchable"


OUT = HERE / "rawcheck.csv"
done = {r["org_id"] for r in csv.DictReader(open(OUT, encoding="utf-8"))} if OUT.exists() else set()
fh = open(OUT, "a", newline="", encoding="utf-8")
w = csv.DictWriter(fh, fieldnames=["org_id", "outcome", "raw", "source_url"], lineterminator="\n")
if not done:
    w.writeheader()
for f in sorted(HERE.glob("lanes/O*_out.csv")):
    for r in csv.DictReader(open(f, encoding="utf-8")):
        if r["org_id"] in done:
            continue
        u, q = (r["source_url"] or "").strip(), (r["quote"] or "").strip()
        w.writerow({"org_id": r["org_id"], "outcome": r["outcome"], "raw": found(u, q) if u.startswith("http") and q else "no_quote", "source_url": u})
        fh.flush(); done.add(r["org_id"])
fh.close()
from collections import Counter
rows = list(csv.DictReader(open(OUT, encoding="utf-8")))
assert len({r["org_id"] for r in rows}) == len(rows), "duplicate org rows in rawcheck.csv"
print(len(rows), "rows;", Counter((r["outcome"], r["raw"]) for r in rows))
