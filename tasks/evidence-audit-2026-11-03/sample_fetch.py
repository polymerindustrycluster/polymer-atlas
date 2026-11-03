"""Evidence audit, step 1: draw a seeded random sample of own_site evidence rows on main and fetch each cited page raw.

    python sample_fetch.py <atlas repo> <n> <out dir>
Writes <out>/sample.csv (evidence row + record name + fetch status + page file) and <out>/pages/<evd>.md.
Fetch: NAS Firecrawl, full page (onlyMainContent false). A failed fetch is recorded as such, never as a verdict."""
import csv, glob, random, re, sys
from pathlib import Path
sys.path.insert(0, r"C:\Users\JohnSwanson\Documents\pic-github\polymer-faculty-census")
from tools.layer_b_fetch import call, env  # noqa: E402

atlas, n, out = Path(sys.argv[1]), int(sys.argv[2]), Path(sys.argv[3])
(out / "pages").mkdir(parents=True, exist_ok=True)
rd = lambda p: list(csv.DictReader(open(p, encoding="utf-8")))
ev = [r for f in sorted(glob.glob(str(atlas / "data" / "evidence*.csv"))) for r in rd(f)]
own = [e for e in ev if e["source_class"] == "own_site" and not (e.get("withdrawn_date") or "").strip()]
url = lambda s: (re.search(r"https?://[^\s;|,)\]]+", s or "") or [None])[0]
with_url = [e for e in own if url(e["source_ref"])]
print(f"own_site rows {len(own)}; with a URL in source_ref {len(with_url)}")
random.seed(20261103)
sample = random.sample(with_url, n)
names = {}
for f in glob.glob(str(atlas / "data" / "*.csv")):
    for r in rd(f):
        for idk, nk in (("org_id", "legal_name"), ("site_id", "site_name"), ("program_id", "program_name"), ("person_id", "full_name")):
            if r.get(idk) and r.get(nk) and r[idk] not in names:
                names[r[idk]] = r[nk]
fc, key = env("FIRECRAWL_BASE_URL").rstrip("/"), env("FIRECRAWL_NAS_API_KEY")
rows = []
for i, e in enumerate(sample, 1):
    u = url(e["source_ref"])
    status, text = "", ""
    try:
        d = call(f"{fc}/v2/scrape", {"url": u, "formats": ["markdown"], "onlyMainContent": False},
                 {"Authorization": f"Bearer {key}"}, timeout=120)
        data = d.get("data") or {}
        code = (data.get("metadata") or {}).get("statusCode")
        text = data.get("markdown") or ""
        status = "ok" if code == 200 and len(text) > 200 else f"http_{code}" if code else "no_content"
    except Exception as ex:
        status = "fetch_error:" + type(ex).__name__
    page = out / "pages" / f"{e['evidence_id']}.md"
    if status == "ok":
        page.write_text(text[:40000], encoding="utf-8")
    rows.append({"evidence_id": e["evidence_id"], "record_table": e["record_table"], "record_id": e["record_id"],
                 "record_name": names.get(e["record_id"], ""), "claim_type": e["claim_type"],
                 "claim_detail": e["claim_detail"], "tier_effect": e["tier_effect"], "observed_date": e["observed_date"],
                 "created_by": e["created_by"], "url": u, "fetch_status": status,
                 "page_file": str(page) if status == "ok" else ""})
    if i % 25 == 0:
        print(i, "fetched", flush=True)
with open(out / "sample.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n"); w.writeheader(); w.writerows(rows)
from collections import Counter
print(Counter(r["fetch_status"].split(":")[0] for r in rows))
print(Counter(r["claim_type"] for r in rows))
