"""Resumable fetcher for the PIC-18 air-permit scout. Caches live under S/persist/pic18-permit-canary-2026-11-18/.

  python3 fetch_permits.py search <pool.json>   # Ohio EPA eDocument search by printed Facility ID (from ECHO AIR_IDS)
  python3 fetch_permits.py docs                 # newest-first, <=6 non-draft docs per site, no stop at first hit

Route provenance (rule 14): the eDocument portal URL was returned by a web search and is linked from
ebiz.epa.ohio.gov; its search form fields were read from the fetched page; every ViewDocument URL fetched is a
docid returned by a search this script ran. The 10-digit Facility ID search value is the last 10 characters of
the ECHO AIR_IDS value (OH + 16 digits) already held in the ECHO exporter; it is a search term, and every bind
is re-verified against the facility ID, holder name and street printed in the permit itself.
"""
import datetime, hashlib, html, json, os, re, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import edoc_client as edoc

S = Path("/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/pic18-permit-canary-2026-11-18")
UA = "Mozilla/5.0 (compatible; AtlasSiteCorpus/1.0)"
MAX_DOCS = 6
F_SEC = "ctl00$search$KeywordPanel1$txtValue_0_1_111_1"; F_NAME = "ctl00$search$KeywordPanel1$txtValue_0_1_106_1"
F_COUNTY = "ctl00$search$KeywordPanel1$ddlValue_0_1_104_1"; F_PAGE = "ctl00$results$DocHitList$DocHitList_CurrentPageSize"
PERMIT = "111,144,145"  # the portal's own "Permit" document-type value

def hits_of(h):
    return [(m.group(1), html.unescape(m.group(2))) for m in re.finditer(r"popup\(&#39;ViewDocument\.aspx\?docid=(\d+)&#39;.*?>([^<]*)</a>", h)]

def run_search(fields):
    for attempt in range(3):
        try:
            s = edoc.Sess(); s.post({"ctl00$search$ddlDocType": PERMIT}, "ctl00$search$ddlDocType")
            d = {"ctl00$search$ddlDocType": PERMIT, "ctl00$search$btnSearch": "Search", F_PAGE: "250"}; d.update(fields); s.post(d)
            m = re.search(r"Search returned ([\d,]+) matching", s.h)
            return {"n": int(m.group(1).replace(",", "")) if m else None, "hits": hits_of(s.h)}
        except Exception as e:
            err = str(e); time.sleep(3)
    return {"err": err}

def pdate(t):
    m = re.search(r" - (\d+)/(\d+)/(\d{4}) - ", t)
    return datetime.date(int(m[3]), int(m[1]), int(m[2])) if m else datetime.date(1900, 1, 1)

def search(pool_path):
    pool = json.load(open(pool_path)); out_p = S / "ohio_epa_search_hits.json"
    out = json.load(open(out_p)) if out_p.exists() else {}
    for p in pool:
        if p["site_id"] in out: continue
        rec = {"site": p["site_id"], "frs": p["frs_ids"], "air": p["air"], "searches": []}
        for _, aid, _pt in p["air"]:
            for a in aid.split():
                if not re.fullmatch(r"OH\d{16}", a): rec["searches"].append({"fid": a[-10:], "err": "unexpected AIR_ID " + a}); continue
                rec["searches"].append({"fid": a[-10:], **run_search({F_SEC: a[-10:]})})
        out[p["site_id"]] = rec; json.dump(out, open(out_p, "w"), indent=1); print(p["site_id"], flush=True)

def fetch_doc(docid, J, done):
    if docid in done: return done[docid]
    pdf = S / "docs" / f"{docid}.pdf"; pdf.parent.mkdir(exist_ok=True)
    r = subprocess.run(["curl", "-sSL", "-m", "120", "-A", UA, "-o", str(pdf), "-w", "%{http_code} %{content_type}",
                        f"https://edocpub.epa.ohio.gov/publicportal/ViewDocument.aspx?docid={docid}"], capture_output=True, text=True)
    rec = {"docid": docid, "http": r.stdout.strip(), "bytes": pdf.stat().st_size if pdf.exists() else 0}
    if rec["bytes"]:
        rec["pdf_sha256"] = hashlib.sha256(pdf.read_bytes()).hexdigest()
        t = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True).stdout
        (S / "docs" / f"{docid}.txt").write_text(t)
        rec["text_sha256"] = hashlib.sha256(t.encode()).hexdigest(); rec["chars"] = len(t)
        rec["fetched_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    open(J, "a").write(json.dumps(rec) + "\n"); done[docid] = rec; return rec

def docs():
    hits = json.load(open(S / "ohio_epa_search_hits.json")); J = S / "fetch_journal_v2.jsonl"; done = {}
    if J.exists():
        for l in open(J): d = json.loads(l); done[d["docid"]] = d
    for site, v in hits.items():
        seen, cands = set(), []
        for x in v["searches"]:
            for d, t in x.get("hits", []):
                if d in seen or "DRAFT" in t or "CORRESPONDENCE" in t: continue
                seen.add(d); cands.append((pdate(t), d))
        for _, d in sorted(cands, reverse=True)[:MAX_DOCS]:
            fetch_doc(d, J, done)
        print(site, len(cands), flush=True)

if __name__ == "__main__":
    {"search": lambda: search(sys.argv[2]), "docs": docs}[sys.argv[1]]()
