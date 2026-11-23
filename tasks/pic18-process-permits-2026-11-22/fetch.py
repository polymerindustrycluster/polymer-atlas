"""Fetch for the canary: Ohio EPA eDocument search by the 10-digit Facility ID, newest six non-draft documents per facility. Reuses the
earlier lane's fetch_permits.py (same documented portal route; no URL is guessed: every ViewDocument docid comes from a search this run made).
Caches (PDFs, text, journals) live under S/persist/process-permits-2026-11-22/ and never enter the repo (cover letters name individuals).

  python3 fetch.py draw               # write canary_sites.csv (seed 20261122)
  python3 fetch.py search|docs        # resumable
"""
import csv, importlib.util, json, random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
P = Path("/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/process-permits-2026-11-22")
spec = importlib.util.spec_from_file_location("fp", ROOT / "tasks/pic18-permit-canary-2026-11-18/fetch_permits.py"); fp = importlib.util.module_from_spec(spec); spec.loader.exec_module(fp)
fp.S = P; (P / "docs").mkdir(parents=True, exist_ok=True)
SEED, N = 20261122, 25

def new_frame():
    """Frame sites with an air ID that were neither examined as a retrievable permit (earlier lane) nor already searched in the earlier pool."""
    old = {r["site_id"] for r in csv.DictReader(open(ROOT / "tasks/pic18-permit-canary-2026-11-18/pool.csv"))}
    return sorted(r["site_id"] for r in csv.DictReader(open(HERE / "frame.csv")) if r["air_ids"] and r["site_id"] not in old)

def draw():
    ids = new_frame(); pick = sorted(random.Random(SEED).sample(ids, min(N, len(ids))))
    fr = {r["site_id"]: r for r in csv.DictReader(open(HERE / "frame.csv"))}
    with open(HERE / "canary_sites.csv", "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n"); w.writerow(["site_id", "air_ids", "routes", "tier"]); [w.writerow([s, fr[s]["air_ids"], fr[s]["routes"], fr[s]["tier"]]) for s in pick]
    print(len(ids), "new frame sites;", len(pick), "drawn")

def search(k=0, n=1):
    """k of n: worker k takes every n-th site and writes search_hits_k.json; `merge` joins them (one portal session per worker)."""
    out_p = P / (f"search_hits_{k}.json" if n > 1 else "search_hits.json"); out = json.load(open(out_p)) if out_p.exists() else {}
    for i, r in enumerate(csv.DictReader(open(HERE / "canary_sites.csv"))):
        if i % n != k or r["site_id"] in out: continue
        out[r["site_id"]] = {"site": r["site_id"], "searches": [{"fid": a[-10:], "air_id": a, **fp.run_search({fp.F_SEC: a[-10:]})} for a in r["air_ids"].split(";")]}
        json.dump(out, open(out_p, "w"), indent=1); print(r["site_id"], [x.get("n", x.get("err")) for x in out[r["site_id"]]["searches"]], flush=True)

def merge():
    out = {}
    for p in sorted(P.glob("search_hits*.json")): out.update(json.load(open(p)))
    json.dump(out, open(P / "search_hits_all.json", "w"), indent=1); print(len(out), "sites")

def docs():
    hits = json.load(open(P / "search_hits_all.json")); J = P / "fetch_journal.jsonl"; done = {}
    if J.exists():
        for l in open(J): d = json.loads(l); done[d["docid"]] = d
    for site, v in hits.items():
        seen, cands = set(), []
        for x in v["searches"]:
            for d, t in x.get("hits", []):
                if d in seen or "DRAFT" in t or "CORRESPONDENCE" in t: continue
                seen.add(d); cands.append((fp.pdate(t), d))
        for _, d in sorted(cands, reverse=True)[:fp.MAX_DOCS]: fp.fetch_doc(d, J, done)
        print(site, len(cands), flush=True)

if __name__ == "__main__": {"draw": draw, "search": lambda: search(*map(int, sys.argv[2:4])) if len(sys.argv) > 3 else search(), "merge": merge, "docs": docs}[sys.argv[1]]()
