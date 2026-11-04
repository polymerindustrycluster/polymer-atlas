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


def found(u, q):
    q, seen = W(q), False
    for p in pages(u.strip()):
        seen = True
        if q and any(p[i:i + len(q)] == q for i in range(len(p) - len(q) + 1)):
            return "yes"
    return "no" if seen else "unfetchable"


out = []
for lane in sorted(glob.glob(str(task / "lanes" / "F*"))):
    for kind in ("evidence", "fields", "duplicates"):
        p = Path(lane) / f"{kind}.csv"
        if not p.exists():
            continue
        for i, r in enumerate(csv.DictReader(open(p, encoding="utf-8"))):
            u = (r.get("source_url") or "").strip()
            out.append({"lane": Path(lane).name, "kind": kind, "idx": i, "org_id": r["org_id"], "url": u,
                        "raw": found(u, r.get("quote", "")) if u.startswith("http") else "no_url"})
with open(task / "rawcheck.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0]), lineterminator="\n"); w.writeheader(); w.writerows(out)
from collections import Counter
print(Counter((o["kind"], o["raw"]) for o in out))
