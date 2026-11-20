#!/usr/bin/env python3
"""Evidence backfill, URL-lead pilot (owner rulings 2026-11-20): re-observe the URL a zero-evidence record already
cites and propose existence / address / liveness rows from what the page says today.

    python build.py frame  <atlas repo> <corpus dir> [--n-org 25 --n-site 25]
    python build.py fetch  <corpus dir>
    python build.py match  <atlas repo> <corpus dir>

Frame: organizations + sites, tier A/B, active, zero evidence rows, citing a URL on the record's own domain
(sites: the operator org's website). Licensed hosts are never fetched. Seeded, stratified by table x tier.
Fetch: direct GET (no model), Jina reader only when the direct fetch fails. A failed fetch is an availability
signal, never a verdict. Match: deterministic string matching; every proposed row carries a verbatim quote cut
from the saved page text. A redirect off the cited host or any closure/acquisition phrase HOLDS the whole record
(owner ruling 2026-11-20: a weaker or conflicting witness is held for the owner, never written).
No data/ file is written here.
"""
import csv, glob, hashlib, html, json, os, random, re, sys, time, urllib.parse, urllib.request
from html.parser import HTMLParser
from pathlib import Path

SEED = 20261120
LICENSED = ("plasticsnews", "rubbernews", "dnb.com", "zoominfo", "dataaxle", "data-axle", "crainsdetroit")
SUFFIX = r"\b(incorporated|inc|llc|l l c|corporation|corp|company|co|ltd|limited|lp|l p|the|plc|gmbh|usa)\b"
CLOSURE = re.compile(r"ceased operations|permanently closed|closed (its|our) doors|no longer in business|out of business|"
                     r"has been acquired|was acquired by|were acquired by|now part of|is now a part of|acquired by|"
                     r"this domain (is|may be) for sale|domain is for sale|buy this domain|account suspended", re.I)
# an ownership-change phrase near the record's name is a parent/status lead for the owner, never a silent witness
ACQ = re.compile(r"acquisition of|acquired|acquires|acquiring|merger|merged with|now part of|a division of|"
                 r"a subsidiary of|wholly[- ]owned|sold (?:to|its)|divest", re.I)
COPYRIGHT = re.compile(r"(?:©|&copy;|copyright)\s*(?:\d{4}\s*[-–—]\s*)?(20\d\d)", re.I)
URL = re.compile(r"https?://[^\s;|,)\]\"']+")
STATES = {"AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado",
          "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
          "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana",
          "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
          "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
          "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York", "NC": "North Carolina",
          "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania",
          "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas",
          "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
          "WI": "Wisconsin", "WY": "Wyoming", "PR": "Puerto Rico"}


def rd(p):
    with open(p, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def wr(p, rows):
    with open(p, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader(); w.writerows(rows)


def host(u):
    h = urllib.parse.urlparse(u if "://" in u else "http://" + u).netloc.lower().split(":")[0]
    return h[4:] if h.startswith("www.") else h


def same_site(a, b):
    return bool(a and b) and (a == b or a.endswith("." + b) or b.endswith("." + a))


def norm(s):
    s = html.unescape(s or "").lower().replace("&", " and ")
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", re.sub(SUFFIX, " ", s)).strip()


# ---------------------------------------------------------------- frame
def frame(atlas, corpus, n_org, n_site):
    data = Path(atlas) / "data"
    has_ev = {(r["record_table"], r["record_id"]) for f in glob.glob(str(data / "evidence_*.csv")) for r in rd(f)}
    orgs = {}
    for f in sorted(glob.glob(str(data / "organizations_*.csv"))):
        for r in rd(f):
            r["_shard"] = Path(f).stem.split("_", 1)[1]; orgs[r["org_id"]] = r
    cands = []
    for rid, r in orgs.items():
        if ("organizations", rid) in has_ev or r["verification_tier"] not in ("A", "B") or r["status"] != "active":
            continue
        cands.append(("organizations", rid, r["_shard"], r["verification_tier"], r["sources"], r.get("website", "")))
    for f in sorted(glob.glob(str(data / "sites_*.csv"))):
        for r in rd(f):
            if ("sites", r["site_id"]) in has_ev or r["verification_tier"] not in ("A", "B") or r["operating_status"] != "active":
                continue
            web = (orgs.get(r["org_id"]) or {}).get("website", "")
            cands.append(("sites", r["site_id"], Path(f).stem.split("_", 1)[1], r["verification_tier"], r["sources"], web))
    pool = []
    for table, rid, shard, tier, sources, web in cands:
        own = [u for u in URL.findall(sources or "") if same_site(host(u), host(web)) and not any(x in host(u) for x in LICENSED)]
        if own:
            pool.append({"record_table": table, "record_id": rid, "shard": shard, "tier": tier,
                         "website_host": host(web), "url": own[0].rstrip(".")})
    ids = [p["record_id"] for p in pool]
    assert len(ids) == len(set(ids)), "duplicate record ids in frame"
    random.seed(SEED)
    sample = []
    for table, n in (("organizations", n_org), ("sites", n_site)):
        for tier in ("A", "B"):
            stratum = [p for p in pool if p["record_table"] == table and p["tier"] == tier]
            k = min(len(stratum), n // 2 + (n % 2 if tier == "A" else 0))
            sample += random.sample(stratum, k)
    Path(corpus).mkdir(parents=True, exist_ok=True)
    wr(Path(corpus) / "frame.csv", pool); wr(Path(corpus) / "sample.csv", sample)
    from collections import Counter
    print("candidates (zero-row, A/B, active):", Counter(c[0] for c in cands))
    print("frame (own-domain URL lead):", Counter((p["record_table"], p["tier"]) for p in pool))
    print("sample:", Counter((p["record_table"], p["tier"]) for p in sample))


# ---------------------------------------------------------------- fetch
class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.out, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "svg"): self.skip += 1
        if tag in ("br", "p", "div", "li", "tr", "h1", "h2", "h3", "h4", "footer", "address", "td"): self.out.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg") and self.skip: self.skip -= 1

    def handle_data(self, d):
        if not self.skip: self.out.append(d)


def to_text(raw):
    p = Text(); p.feed(raw)
    t = html.unescape("".join(p.out))
    return re.sub(r"\n\s*\n+", "\n", re.sub(r"[ \t\r\f\v\xa0]+", " ", t)).strip()


def direct(u):
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                             "(KHTML, like Gecko) Chrome/130.0 Safari/537.36", "Accept": "text/html,*/*"})
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read(3_000_000)
        ctype = r.headers.get("Content-Type", "")
        return r.status, r.geturl(), body.decode(r.headers.get_content_charset() or "utf-8", "replace"), ctype


def jina(u):
    key = os.environ.get("JINA_API_KEY") or ""
    if not key:
        sys.path.insert(0, r"C:\Users\JohnSwanson\Documents\pic-github\polymer-faculty-census")
        from tools.layer_b_fetch import env
        key = env("JINA_API_KEY")
    req = urllib.request.Request("https://r.jina.ai/" + u, headers={"Authorization": "Bearer " + key, "X-Return-Format": "text"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status, r.read(3_000_000).decode("utf-8", "replace")


def fetch(corpus):
    corpus = Path(corpus); (corpus / "pages").mkdir(exist_ok=True)
    out = []
    for i, s in enumerate(rd(corpus / "sample.csv"), 1):
        u, rec = s["url"], {"record_id": s["record_id"], "url": s["url"], "route": "", "status": "", "final_url": "",
                            "sha256": "", "retrieved": time.strftime("%Y-%m-%d"), "page_file": ""}
        text = ""
        try:
            code, final, raw, ctype = direct(u)
            rec.update(route="direct", final_url=final)
            if "html" in ctype or raw.lstrip().startswith("<"):
                text = to_text(raw)
            rec["status"] = "ok" if code == 200 and len(text) > 200 else f"thin_{code}"
        except Exception as ex:
            rec.update(route="direct", status="fetch_error:" + type(ex).__name__)
        if rec["status"] != "ok":
            try:
                code, text = jina(u)
                rec.update(route="jina", final_url=u, status="ok" if code == 200 and len(text) > 200 else f"thin_{code}")
            except Exception as ex:
                rec["status"] += "|jina_error:" + type(ex).__name__
        if rec["status"] == "ok":
            p = corpus / "pages" / f"{s['record_id']}.txt"
            p.write_text(text, encoding="utf-8")
            rec.update(page_file=p.name, sha256=hashlib.sha256(text.encode("utf-8")).hexdigest())
        out.append(rec)
        print(i, s["record_id"], rec["route"], rec["status"], flush=True)
    wr(corpus / "fetch.csv", out)


# ---------------------------------------------------------------- match
def window(text, a, b, pad=70):
    q = text[max(0, a - pad):min(len(text), b + pad)]
    return re.sub(r"\s+", " ", q).strip()


ABBR = {"ind": r"ind(?:ustries|ustrial|ustry)?", "mfg": r"(?:mfg|manufacturing)", "intl": r"(?:intl|international)",
        "bros": r"(?:bros|brothers)", "assoc": r"assoc(?:iates|iation)?", "prod": r"prod(?:ucts)?", "tech": r"tech(?:nologies|nology)?",
        "eng": r"eng(?:ineering)?", "mach": r"mach(?:ine|inery)?"}
# between name tokens: punctuation, optionally with connector or corporate-suffix words (the page may spell them out)
GAP = r"[\W_]+(?:(?:and|the|incorporated|inc|llc|corporation|corp|company|co|ltd)[\W_]+)*"


def names_of(*raw):
    out = []
    for n in raw:
        for part in re.split(r"\s+(?:dba|d/b/a|d\.b\.a\.)\s+", n or "", flags=re.I):
            if part.strip():
                out.append(part.strip())
    return out


def find_name(text, names):
    for n in names:
        toks = [t for t in norm(n).split() if t != "and"]
        if not toks or len("".join(toks)) < 5:
            continue
        pat = r"\b" + GAP.join(ABBR.get(t, re.escape(t)) for t in toks) + r"\b"
        m = re.search(pat, text, re.I)
        if m:
            return n, m
    return None, None


def near_name(text, names, rx, dist=150):
    """First rx hit within dist chars of any name occurrence, as a quote; None when the phrase is never near the name."""
    spans = []
    for n in names:
        toks = [t for t in norm(n).split() if t != "and"]
        if toks and len("".join(toks)) >= 5:
            spans += [m.span() for m in re.finditer(r"\b" + GAP.join(ABBR.get(t, re.escape(t)) for t in toks) + r"\b", text, re.I)]
    for h in rx.finditer(text):
        if any(h.start() - dist <= b and a <= h.end() + dist for a, b in spans):
            return window(text, h.start(), h.end(), 80)
    return None


def selftest():
    assert near_name("Acme announced today the acquisition of Monadnock Non-Wovens LLC, a maker", ["Monadnock Non-Wovens LLC"], ACQ)
    assert not near_name("Monadnock Non-Wovens makes media." + " x" * 200 + " we acquired a new press", ["Monadnock Non-Wovens"], ACQ)
    hit = lambda name, page: find_name(page, names_of(name))[1] is not None
    assert hit("Freedom Mold & Machine LLC", "Freedom Mold Machine")
    assert hit("Slome Belting & Supply Co", "Slome Belting & Supply - Hose and Belt Distributor")
    assert hit("Engineering Mechanics Corporation of Columbus", "Engineering Mechanics Corporation of Columbus provides")
    assert hit("3B Medical, Inc. dba React Health", "Solutions | React Health Skip")
    assert hit("C & J Ind", "C&J Industries | Plastic Injection Molding")
    assert not hit("Acme Plastics Inc", "Acme Rubber Company makes hoses")
    assert not hit("Ace Mfg", "Acetone manufacturing")
    assert find_street("1010 Industrial Pkwy. N., Brunswick, 44212", "1010 Industrial Pkwy N", "Brunswick")
    assert not find_street("1010 Industrial Pkwy. N., Medina, 44256", "1010 Industrial Pkwy N", "Brunswick")
    assert find_city_state("685 S. Chestnut St. Ravenna, OH 44266", "Ravenna", "OH")
    assert not find_city_state("Ravenna, Italy", "Ravenna", "OH")
    assert CLOSURE.search("Acme is now a part of BigCo") and not CLOSURE.search("We acquire new customers daily")
    print("selftest ok")


def find_city_state(text, city, st):
    if not city or not st:
        return None
    full = STATES.get(st.upper(), st)
    pat = re.escape(city) + r",?\s+(?:" + re.escape(st) + r"|" + re.escape(full) + r")\b\.?(?:\s+\d{5}(?:-\d{4})?)?"
    hits = list(re.finditer(pat, text, re.I))
    hits.sort(key=lambda m: 0 if re.search(r"\d{5}", m.group(0)) else 1)  # prefer a hit carrying a ZIP
    return hits[0] if hits else None


def find_street(text, street, city):
    m = re.match(r"\s*(\d+[A-Za-z]?)\s+(.*)", street or "")
    if not m or not city:
        return None
    num = m.group(1)
    words = [w for w in re.findall(r"[A-Za-z]+", m.group(2)) if len(w) > 2 and w.lower() not in
             ("north", "south", "east", "west", "street", "avenue", "road", "drive", "boulevard", "parkway", "lane",
              "court", "highway", "suite", "ste", "blvd", "pkwy", "hwy", "the")]
    if not words:
        return None
    for h in re.finditer(r"\b" + re.escape(num) + r"\b[^\n]{0,40}?\b" + re.escape(words[0]) + r"\b", text, re.I):
        tail = text[h.end():h.end() + 160]
        if re.search(re.escape(city), tail, re.I):
            c = re.search(re.escape(city), tail, re.I)
            return h.start(), h.end() + c.end()
    return None


def match(atlas, corpus, plant=None):
    data, corpus = Path(atlas) / "data", Path(corpus)
    recs = {}
    for f in glob.glob(str(data / "organizations_*.csv")) + glob.glob(str(data / "sites_*.csv")):
        for r in rd(f):
            recs[r.get("site_id") or r["org_id"]] = r
    orgs = {k: v for k, v in recs.items() if k.startswith("ORG-")}
    fetched = {r["record_id"]: r for r in rd(corpus / "fetch.csv")}
    rows, ledger = [], []
    for s in rd(corpus / "sample.csv"):
        rid, f = s["record_id"], fetched[s["record_id"]]
        r = recs[rid]
        led = {"record_table": s["record_table"], "record_id": rid, "tier": s["tier"], "url": s["url"], "verdict": "", "reason": "",
               "claims": ""}
        if f["status"] != "ok":
            led.update(verdict="NO_FETCH", reason=f["status"]); ledger.append(led); continue
        if f["route"] == "direct" and not same_site(host(f["final_url"]), host(s["url"])):
            led.update(verdict="HOLD", reason=f"redirected off cited host to {f['final_url']}"); ledger.append(led); continue
        text = (corpus / "pages" / f["page_file"]).read_text(encoding="utf-8")
        cl = CLOSURE.search(text)
        if cl:
            led.update(verdict="HOLD", reason="closure/acquisition phrase: " + window(text, cl.start(), cl.end(), 60))
            ledger.append(led); continue
        if s["record_table"] == "organizations":
            names = names_of(r["legal_name"], *(r.get("trade_names") or "").split(";"))
            city, st = r.get("hq_city", ""), r.get("hq_state", "")
            op = r
        else:
            op = orgs.get(r["org_id"], {})
            names = names_of(r["site_name"], op.get("legal_name", ""), *(op.get("trade_names") or "").split(";"))
            city, st = r.get("city", ""), r.get("state", "")
        if plant and rid in plant:  # planted defect: score this record against another record's page
            text = (corpus / "pages" / fetched[plant[rid]]["page_file"]).read_text(encoding="utf-8")
        nm, m = find_name(text, names)
        if not m:
            led.update(verdict="NO_WITNESS", reason="no record or operator name on the page"); ledger.append(led); continue
        acq = near_name(text, names, ACQ)
        if acq:
            led.update(verdict="HOLD", reason="ownership-change phrase near the name: " + acq); ledger.append(led); continue
        base = {"record_table": s["record_table"], "record_id": rid, "source_class": "own_site", "source_ref": f["final_url"] or s["url"],
                "observed_date": f["retrieved"], "tier_effect": "supports_A", "created_by": "claude-code-evd-backfill-url-pilot"}
        note = f"Raw re-fetch {f['retrieved']} via {f['route']}; page sha256 {f['sha256'][:16]}; URL was already cited in the record's sources; record tier unchanged."
        got = []
        if s["record_table"] == "organizations":
            rows.append({**base, "claim_type": "existence", "claim_detail": f"legal/trade name '{nm}'; quote: {window(text, m.start(), m.end())}", "notes": note})
            got.append("existence")
            cs = find_city_state(text, city, st)
            if cs:
                rows.append({**base, "claim_type": "address", "claim_detail": f"hq_city {city}, hq_state {st}; quote: {window(text, cs.start(), cs.end())}",
                             "notes": note + " County left blank: not evidenced on the page."})
                got.append("address")
        else:
            sp = find_street(text, r.get("street_address", ""), city)
            if not sp:
                led.update(verdict="NO_WITNESS", reason="operator page does not print this site's street address"); ledger.append(led); continue
            q = window(text, *sp)
            rows.append({**base, "claim_type": "existence", "claim_detail": f"{op.get('legal_name', nm)} site at {r.get('street_address')}, {city}, {st} on the operator's own page; quote: {q}", "notes": note})
            rows.append({**base, "claim_type": "address", "claim_detail": f"street_address {r.get('street_address')}, {city}, {st}; quote: {q}",
                         "notes": note + " County left blank: not evidenced on the page."})
            got += ["existence", "address"]
        years = [int(y) for y in COPYRIGHT.findall(text)]
        if years and max(years) >= 2025:
            best = max(COPYRIGHT.finditer(text), key=lambda x: int(x.group(1)))
            rows.append({**base, "claim_type": "liveness", "claim_detail": f"own site live at {f['retrieved']} with current copyright year {best.group(1)}; quote: {window(text, best.start(), best.end(), 40)}",
                         "notes": note + " Live-site witness only: not a dated production event."})
            got.append("liveness")
        led.update(verdict="WITNESS", claims=";".join(got)); ledger.append(led)
    if plant:  # planted run: report what the swapped records produced, write nothing
        leaked = [x for x in rows if x["record_id"] in plant]
        print("PLANTED rows emitted (must be 0):", len(leaked), [l for l in ledger if l["record_id"] in plant])
        return len(leaked)
    for x in rows:  # every quote must be verbatim in the saved page (whitespace-collapsed)
        page = re.sub(r"\s+", " ", (corpus / "pages" / f"{x['record_id']}.txt").read_text(encoding="utf-8"))
        assert x["claim_detail"].split("quote: ", 1)[1] in page, x["record_id"]
    if rows:
        wr(corpus / "packet_rows.csv", rows)
    wr(corpus / "ledger.csv", ledger)
    from collections import Counter
    print("ledger:", Counter(l["verdict"] for l in ledger))
    print("rows by claim:", Counter(x["claim_type"] for x in rows))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "frame":
        a = sys.argv[2:]
        n_org = int(a[a.index("--n-org") + 1]) if "--n-org" in a else 25
        n_site = int(a[a.index("--n-site") + 1]) if "--n-site" in a else 25
        frame(a[0], a[1], n_org, n_site)
    elif cmd == "fetch":
        fetch(sys.argv[2])
    elif cmd == "match":
        selftest()
        if "--plant" in sys.argv:  # --plant A:B,C:D scores record A against B's page
            pairs = dict(x.split(":") for x in sys.argv[sys.argv.index("--plant") + 1].split(","))
            sys.exit(1 if match(sys.argv[2], sys.argv[3], pairs) else 0)
        match(sys.argv[2], sys.argv[3])
