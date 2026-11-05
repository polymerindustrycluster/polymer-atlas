"""Raw-check every evidence and fields quote from the record-fix lanes (NAS Firecrawl: main content, then full page).
Writes <task>/rawcheck.csv: lane, kind, row index, url, raw (yes / no / unfetchable)."""
import csv, glob, re, sys, unicodedata
from pathlib import Path
sys.path.insert(0, r"C:\Users\JohnSwanson\Documents\pic-github\polymer-faculty-census")
from tools.layer_b_fetch import call, env  # noqa: E402
task = Path(sys.argv[1])
fc, key = env("FIRECRAWL_BASE_URL").rstrip("/"), env("FIRECRAWL_NAS_API_KEY")
W = lambda s: re.findall(r"[a-z0-9]+", unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower())
cache = {}


def pages(u):
    for main in (True, False):
        if (u, main) not in cache:
            try:
                r = call(f"{fc}/v2/scrape", {"url": u, "formats": ["markdown"], "onlyMainContent": main},
                         {"Authorization": f"Bearer {key}"}, timeout=150)
                data = r.get("data") or {}
                cache[(u, main)] = W(data.get("markdown")) if (data.get("metadata") or {}).get("statusCode") == 200 else None
            except Exception:
                cache[(u, main)] = None
        if cache[(u, main)]:
            yield cache[(u, main)]


def jina(u):  # fallback route (2026-11-04): Jina Reader, same word-sequence match
    if ("jina", u) not in cache:
        try:
            import urllib.request
            req = urllib.request.Request("https://r.jina.ai/" + u, headers={"Authorization": f"Bearer {env('JINA_API_KEY')}", "User-Agent": "polymer-atlas/1.0"})
            with urllib.request.urlopen(req, timeout=90) as r:
                cache[("jina", u)] = W(r.read().decode("utf-8", "replace"))
        except Exception:
            cache[("jina", u)] = None
    return cache[("jina", u)]


def found(u, q):
    q, seen = W(q), False
    for p in list(pages(u.strip())) + [jina(u.strip())]:
        if not p:
            continue
        seen = True
        if q and any(p[i:i + len(q)] == q for i in range(len(p) - len(q) + 1)):
            return "yes"
    return "no" if seen else "unfetchable"


# Resumable (2026-11-05): each row is written as it is checked, and a re-run skips rows already in rawcheck.csv, so a
# memory kill loses at most one row.
OUT, FIELDS = task / "rawcheck.csv", ["lane", "kind", "idx", "org_id", "url", "raw"]
done = {(r["lane"], r["kind"], r["idx"]) for r in csv.DictReader(open(OUT, encoding="utf-8"))} if OUT.exists() else set()
fh = open(OUT, "a", newline="", encoding="utf-8")
w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
if not done:
    w.writeheader()
for lane in sorted(glob.glob(str(task / "lanes" / "F*"))):
    for kind in ("evidence", "fields", "duplicates"):
        p = Path(lane) / f"{kind}.csv"
        if not p.exists():
            continue
        for i, r in enumerate(csv.DictReader(open(p, encoding="utf-8"))):
            if (Path(lane).name, kind, str(i)) in done:
                continue
            u = (r.get("source_url") or "").strip()
            w.writerow({"lane": Path(lane).name, "kind": kind, "idx": i, "org_id": r["org_id"], "url": u,
                        "raw": found(u, r.get("quote", "")) if u.startswith("http") else "no_url"})
            fh.flush()
fh.close()
from collections import Counter
rows = list(csv.DictReader(open(OUT, encoding="utf-8")))
assert len({(r["lane"], r["kind"], r["idx"]) for r in rows}) == len(rows), "duplicate rows in rawcheck.csv"
print(len(rows), "rows;", Counter((o["kind"], o["raw"]) for o in rows))
