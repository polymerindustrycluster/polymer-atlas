"""Website finding v3, full run (owner OK 2026-11-04). Covers every active organization with no website and a USPS
HQ state, in the given worktree's data. Rule, from the v1/v2 pilots:
- Candidate: the first Serper result, outside directories, social sites and .gov/.edu, whose registrable domain
  contains a distinctive name token or the name's initials.
- Accept: the homepage (Jina Reader) carries every distinctive name token. There is no city check: pilot v2 showed that
  the held HQ city is often a plant the homepage does not name.
- The website recorded is the root domain (https://<registrable domain>/).
Serper responses are cached in serper_cache/, so the 100 pilot orgs cost nothing again. Writes website_run_v3.csv,
with columns org_id, legal_name, hq_city, hq_state, result, website, homepage_title, top_hosts.
    python -I website_run_v3.py <atlas worktree>"""
import csv, glob, json, os, re, sys, urllib.request
from pathlib import Path
H = Path(__file__).resolve().parent
wt = Path(sys.argv[1])
sys.path.insert(0, str(wt / "scripts"))
import atlas  # noqa: E402
src = (H / "website_pilot_v2.py").read_text(encoding="utf-8")
ns = {}
exec(re.search(r"(STATES = \{.*?\}\nGENERIC = \{.*?\}\n)", src, re.S).group(1), ns)  # constants only, no run block
STATES, GENERIC = ns["STATES"], ns["GENERIC"]
SKIP = re.compile(r"(linkedin|facebook|instagram|twitter|youtube|zoominfo|dnb\.|bloomberg|manta|bizapedia|opencorporates|yelp|"
                  r"mapquest|indeed|glassdoor|buzzfile|wikipedia|yellowpages|bbb\.org|crunchbase|govtribe|thomasnet|kompass|"
                  r"corporationwiki|signalhire|rocketreach|apollo|cbinsights|pitchbook|ziprecruiter|careerbuilder|simplyhired|"
                  r"zippia|builtin|industrynet|iqsdirectory|thebluebook|govcb|creditsafe|waze|loadconnect|wanderboat|vaia|"
                  r"futunn|rwbaird|arsenalcapital|printaccess|paintsupply|earcu|uspto|nhtsa|\.gov\b|\.gov/|\.edu\b|\.edu/|"
                  r"chamber|directory|jobs|careers\.|news\.|prnewswire|businesswire|globenewswire|leadiq|nsnlookup|importgenius|"
                  r"moovitapp|diversityjobs|sweets\.construction|biz2bizonline|infassure|amazon\.|desertcart|wemakeithere)", re.I)
env = dict(re.findall(r"^([A-Z0-9_]+)=(.*)$", Path(os.path.expanduser("~/.env")).read_text(encoding="utf-8"), re.M))
SERPER, JINA = env["SERPER_API_KEY"].strip(), env["JINA_API_KEY"].strip()
CACHE = H / "serper_cache"; CACHE.mkdir(exist_ok=True)


def serper(q, key):
    p = CACHE / f"{key}.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    req = urllib.request.Request("https://google.serper.dev/search", data=json.dumps({"q": q, "num": 10}).encode(),
                                 headers={"X-API-KEY": SERPER, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        res = json.loads(r.read())
    p.write_text(json.dumps(res), encoding="utf-8")
    return res


def jina(url):
    req = urllib.request.Request("https://r.jina.ai/" + url, headers={"Authorization": f"Bearer {JINA}", "User-Agent": "polymer-atlas/1.0"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read().decode("utf-8", "replace")


def root(host):  # registrable domain, good enough for .com/.net/.org/.us/.inc and similar; shortcut: no public-suffix list
    parts = host.split(".")
    return ".".join(parts[-3:]) if len(parts) >= 3 and parts[-2] in ("co", "com") and len(parts[-1]) == 2 else ".".join(parts[-2:])


orgs = []
for f in sorted(glob.glob(str(wt / "data" / "organizations_*.csv"))):
    for r in csv.DictReader(open(f, encoding="utf-8")):
        if r["status"] == "active" and not r["website"].strip() and r["hq_state"] in STATES:
            orgs.append(r)
orgs.sort(key=lambda r: r["org_id"])
print("pool:", len(orgs), "| cached already:", sum((CACHE / f"{r['org_id']}.json").exists() for r in orgs), flush=True)
OUT = H / "website_run_v3.csv"
FIELDS = ["org_id", "legal_name", "hq_city", "hq_state", "result", "website", "homepage_title", "top_hosts"]
done = {x["org_id"] for x in csv.DictReader(open(OUT, encoding="utf-8"))} if OUT.exists() else set()
fh = open(OUT, "a", newline="", encoding="utf-8")
wr = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
if not done:
    wr.writeheader()
print("resuming; already written:", len(done), flush=True)
out = []
for i, r in enumerate(orgs):
    if r["org_id"] in done:
        continue
    name, city, st, oid = r["legal_name"], r["hq_city"], r["hq_state"], r["org_id"]
    toks = [t for t in atlas.name_key(name).split() if t not in GENERIC and len(t) > 2] or atlas.name_key(name).split()
    initials = "".join(t[0] for t in atlas.name_key(name).split() if t not in ("and", "the"))
    row = {"org_id": oid, "legal_name": name, "hq_city": city, "hq_state": st, "result": "", "website": "", "homepage_title": "", "top_hosts": ""}
    try:
        res = serper(f'"{name}" {city} {st}', oid)
        org = res.get("organic", [])
        row["top_hosts"] = ";".join(o["link"].split("/")[2] for o in org[:4])
        cand = ""
        for o in org:
            host = re.sub(r"^www\.", "", re.match(r"https?://([^/]+)", o["link"]).group(1).lower())
            if SKIP.search(o["link"]):
                continue
            dom = root(host).split(".")[0].replace("-", "")
            if any(t in dom for t in toks) or (len(initials) >= 3 and dom.startswith(initials)):
                cand = f"https://{root(host)}/"; break
        if not cand:
            row["result"] = "no_candidate"
        else:
            page = jina(cand)
            m = re.search(r"^Title:\s*(.*)$", page, re.M)
            row["homepage_title"] = (m.group(1).strip() if m else "")[:120]
            sq = " " + atlas.squash(page) + " "
            row["website"] = cand
            row["result"] = "accept" if all(f" {t} " in sq for t in toks) else "reject_name_not_on_page"
    except Exception as e:
        row["result"] = f"error: {type(e).__name__}"
    out.append(row); wr.writerow(row); fh.flush()  # written per row, so a stop loses nothing
    if i % 50 == 0:
        print(i, oid, row["result"], row["website"], flush=True)
fh.close()
from collections import Counter
allrows = list(csv.DictReader(open(OUT, encoding="utf-8")))
assert len({x["org_id"] for x in allrows}) == len(allrows), "duplicate org rows in output"
print("DONE", len(allrows), "rows;", Counter(o["result"].split(":")[0] for o in allrows))
