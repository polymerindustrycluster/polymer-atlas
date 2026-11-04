"""Raw-check each finding's quote on its source_url (NAS Firecrawl helper from the local census repo; main content then
full page). Writes rawcheck.csv: item, raw (yes / no / unfetchable)."""
import csv, re, sys, unicodedata
from pathlib import Path
sys.path.insert(0, r"C:\Users\JohnSwanson\Documents\pic-github\polymer-faculty-census")
from tools.layer_b_fetch import call, env  # noqa: E402
HERE = Path(__file__).resolve().parent
fc, key = env("FIRECRAWL_BASE_URL").rstrip("/"), env("FIRECRAWL_NAS_API_KEY")
W = lambda s: re.findall(r"[a-z0-9]+", unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower())


def found(u, q):
    q, seen = W(q), False
    for main in (True, False):
        try:
            r = call(f"{fc}/v2/scrape", {"url": u, "formats": ["markdown"], "onlyMainContent": main},
                     {"Authorization": f"Bearer {key}"}, timeout=150)
            d = r.get("data") or {}
            p = W(d.get("markdown")) if (d.get("metadata") or {}).get("statusCode") == 200 else None
        except Exception:
            p = None
        if p:
            seen = True
            if q and any(p[i:i + len(q)] == q for i in range(len(p) - len(q) + 1)):
                return "yes"
    try:  # fallback route (owner OK 2026-11-04): Jina Reader, same word-sequence match
        import os, urllib.request
        jk = env("JINA_API_KEY")
        with urllib.request.urlopen(urllib.request.Request("https://r.jina.ai/" + u, headers={"Authorization": f"Bearer {jk}", "User-Agent": "polymer-atlas/1.0"}), timeout=90) as r:
            p = W(r.read().decode("utf-8", "replace"))
        if q and any(p[i:i + len(q)] == q for i in range(len(p) - len(q) + 1)):
            return "yes (jina_reader)"
        seen = True
    except Exception:
        pass
    return "no" if seen else "unfetchable"


out = []
for r in csv.DictReader(open(HERE / "findings.csv", encoding="utf-8")):
    if r["verdict"].strip() == "CONFIRMED" and r["source_url"].startswith("http"):
        out.append({"item": r["item"], "raw": found(r["source_url"].strip(), r["quote"])})
with open(HERE / "rawcheck.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["item", "raw"], lineterminator="\n"); w.writeheader(); w.writerows(out)
print(out)
