"""Fetch every exhibitor-list URL (rendered, full page, NAS Firecrawl), save markdown, and pull candidate exhibitor
names from link text whose target looks like an exhibitor/booth detail page. Writes <out>/pages/*.md and
<out>/names.csv (roster key, name, link) plus a per-roster yield line."""
import csv, hashlib, re, sys
from pathlib import Path
sys.path.insert(0, r"C:\Users\JohnSwanson\Documents\pic-github\polymer-faculty-census")
from tools.layer_b_fetch import call, env  # noqa: E402
src, out = Path(sys.argv[1]), Path(sys.argv[2])
(out / "pages").mkdir(parents=True, exist_ok=True)
fc, key = env("FIRECRAWL_BASE_URL").rstrip("/"), env("FIRECRAWL_NAS_API_KEY")
LINK = re.compile(r"\[([^\]\n]{2,90})\]\((https?://[^)\s]+)\)")
DETAIL = re.compile(r"exhibitor[-_]?details|exhid=|/exhibitors?/[^/?#]+|ebooth|booth|company-profile|/exhibitor/", re.I)
SKIP = re.compile(r"^(view|more|details|booth|exhibitor|exhibitors|floor ?plan|see all|website|map|add|login|register|\d+)$", re.I)
rows, report = [], []
for r in csv.DictReader(open(src, encoding="utf-8")):
    u = r["exhibitor_list_url"].strip()
    f = out / "pages" / (hashlib.sha1(u.encode()).hexdigest()[:16] + ".md")
    try:
        d = call(f"{fc}/v2/scrape", {"url": u, "formats": ["markdown"], "onlyMainContent": False, "waitFor": 4000},
                 {"Authorization": f"Bearer {key}"}, timeout=180)
        md = (d.get("data") or {}).get("markdown") or ""
    except Exception as e:
        md = ""
    f.write_text(md, encoding="utf-8")
    names = {}
    for text, link in LINK.findall(md):
        t = re.sub(r"\s+", " ", text).strip(" *_#")
        if DETAIL.search(link) and not SKIP.match(t) and not t.startswith("!"):
            names.setdefault(t, link)
    for n, l in names.items():
        rows.append({"key": r["key"], "year": r["year"], "roster_url": u, "name": n, "link": l})
    report.append(f"{r['key'][:40]:40} {len(md):7} chars {len(names):4} names  {u[:70]}")
with open(out / "names.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["key", "year", "roster_url", "name", "link"], lineterminator="\n"); w.writeheader(); w.writerows(rows)
print("\n".join(report)); print("total names", len(rows))
