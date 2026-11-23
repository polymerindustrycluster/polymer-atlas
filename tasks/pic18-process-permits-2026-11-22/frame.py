"""Frame for the PIC-18 Ohio EPA air-permit process lane (2026-11-22). Reads the repo tree at HEAD and the Parquet lake; writes frame.csv.

  uv run --with duckdb python frame.py

Unit: Atlas sites with state OH, county in PIC-18 (scripts/regions.py), operating_status active, tier A-C, `processes` empty/unknown at the
site AND at its organization. A candidate Ohio EPA air facility ID comes from two routes:
  frs : an Atlas FRS registry link (the site's own, or an organization-level one when the organization has exactly one frame-eligible site)
        -> lake echo_air_facilities REGISTRY_ID -> PGM_SYS_ID (OH + 16 digits; the portal search value is its last 10 characters);
  lake: a lake echo_air_facilities row in OH whose street is the site's (derive_last_activity.same_street) and whose name is the site's or
        its organization's held name (atlas.name_key equal, or the earlier permit lane's holder_ok token rule).
The ID is only a search term: build.py binds every permit on its printed Facility ID, holder and street.
"""
import csv, io, json, subprocess, sys
from collections import defaultdict
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]; sys.path.insert(0, str(ROOT / "scripts"))
from regions import PIC18
from atlas import name_key, squash
from derive_last_activity import same_street
LAKE = "/Volumes/johnpswan/work/GAC/polymer-atlas/atlas-store/lake/2026-11-22"
LEGAL = {"inc", "llc", "co", "corp", "corporation", "company", "ltd", "lp"}   # the earlier lane's holder_ok rule (canary build.py)
def toks(x): return {w for w in squash(x).split() if w not in LEGAL}
def name_ok(a, names):
    t = toks(a)
    return any(n and (n <= t or t <= n) for n in (toks(x) for x in names))
def _git(*a): return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True, check=True).stdout
BASE = _git("merge-base", "HEAD", "origin/main").strip()   # the frame is read at the merge-base, so applying this lane's writes does not change it
def rd(p):
    p = Path(p)
    if p.is_relative_to(ROOT / "data"): return list(csv.DictReader(io.StringIO(_git("show", f"{BASE}:data/{p.name}"), newline="")))
    return list(csv.DictReader(open(p, newline="", encoding="utf-8")))
def unk(v): return not {t.strip() for t in (v or "").split(";") if t.strip() and t.strip() != "unknown"}

def atlas():
    names = _git("ls-tree", "--name-only", BASE, "data/").split()
    sites = [r for n in names if Path(n).name.startswith("sites_") for r in rd(ROOT / n)]
    orgs = {r["org_id"]: r for n in names if Path(n).name.startswith("organizations_") for r in rd(ROOT / n)}
    for r in rd(ROOT / "data/ecosystem.csv"): orgs.setdefault(r["org_id"], r)   # the harness's fallback for non-organization entities
    return sites, orgs

def frame_sites(sites, orgs):
    el = [s for s in sites if s["state"] == "OH" and s["county"] in PIC18 and s["operating_status"] == "active" and s["verification_tier"] in ("A", "B", "C") and s["verification_tier"]]
    return [s for s in el if unk(s["processes"]) and unk((orgs.get(s["org_id"]) or {}).get("processes"))], el

def compute():
    """-> (rows, stats). Pure: reads the repo tree and the lake, writes nothing."""
    import duckdb   # lazy: build.py imports atlas() from here and needs no lake
    sites, orgs = atlas(); fr, el = frame_sites(sites, orgs)
    per_org = defaultdict(int)
    for s in fr: per_org[s["org_id"]] += 1
    frs = defaultdict(list)
    for r in rd(ROOT / "data/registry_links.csv"):
        if r["registry"] == "FRS": frs[r["org_id"]].append((r["registry_id"], r["site_id"]))
    c = duckdb.connect()
    fac = c.execute(f"select PGM_SYS_ID, REGISTRY_ID, FACILITY_NAME, STREET_ADDRESS, CITY, ZIP_CODE, AIR_OPERATING_STATUS_DESC from '{LAKE}/echo/echo_air_facilities.parquet' where STATE='OH' and PGM_SYS_ID like 'OH%'").fetchall()
    by_reg = defaultdict(list); by_street = defaultdict(list)
    for f in fac:
        by_reg[f[1]].append(f)
        by_street[squash(f[3]).split(" ")[0] if f[3] else ""].append(f)
    done = {r["site_id"] for r in rd(ROOT / "tasks/pic18-permit-lane-2026-11-18/sites.csv")}
    out = []
    for s in sorted(fr, key=lambda x: x["site_id"]):
        o = orgs[s["org_id"]]; names = [s["site_name"], o.get("legal_name") or o.get("name", ""), *[x.strip() for x in (o.get("trade_names") or "").split(";") if x.strip()]]
        ids = {}   # pgm_sys_id -> {routes, facility name/street}
        for rid, sid in frs.get(s["org_id"], []):
            if sid not in ("", s["site_id"]) or (sid == "" and per_org[s["org_id"]] != 1): continue
            for f in by_reg.get(rid, []): ids.setdefault(f[0], {"routes": set(), "f": f})["routes"].add("frs")
        for f in by_street.get(squash(s["street_address"]).split(" ")[0] if s["street_address"] else "~", []):
            if not same_street(s["street_address"], f[3]): continue
            exact = name_key(f[2]) in {name_key(n) for n in names}
            if exact or name_ok(f[2], names):
                d = ids.setdefault(f[0], {"routes": set(), "f": f}); d["routes"].add("lake"); d["exact"] = d.get("exact", False) or exact
        out.append({"site_id": s["site_id"], "org_id": s["org_id"], "tier": s["verification_tier"], "site_name": s["site_name"], "street_address": s["street_address"], "city": s["city"],
                    "county": s["county"], "air_ids": ";".join(sorted(ids)), "routes": ";".join(sorted({r for v in ids.values() for r in v["routes"]})),
                    "route_per_id": ";".join(f"{k}:{'+'.join(sorted(v['routes']))}" for k, v in sorted(ids.items())),
                    "lake_name_match": ";".join(f"{k}:{'exact' if v.get('exact') else 'token_rule'}" for k, v in sorted(ids.items()) if "lake" in v["routes"]),
                    "done_2026_11_18": "Y" if s["site_id"] in done else "N", "ech_status": ";".join(sorted({v["f"][6] or "" for v in ids.values()}))})
    withid = [r for r in out if r["air_ids"]]
    has = {r["site_id"] for r in withid}; fr_by = {s["site_id"]: s for s in fr}
    lead = sum(any(f[3] and fr_by[sid]["street_address"] and same_street(fr_by[sid]["street_address"], f[3]) for f in by_street.get(squash(fr_by[sid]["street_address"]).split(" ")[0] if fr_by[sid]["street_address"] else "~", []))
               for sid in fr_by if sid not in has)
    old = {r["site_id"] for r in rd(ROOT / "tasks/pic18-permit-canary-2026-11-18/pool.csv")}
    kinds = [x.split(":")[1] for r in out for x in r["lake_name_match"].split(";") if x]
    shared = {}
    for r in withid:
        for a in r["air_ids"].split(";"): shared.setdefault(a, []).append(r["site_id"])
    shared = {a: v for a, v in shared.items() if len(v) > 1}
    stats = {"pic18_active_ac_sites": len(el), "frame_no_process_site_and_org": len(fr), "frame_blank_street": sum(not (s["street_address"] or "").strip() for s in fr),
             "frame_with_air_id": len(withid), "distinct_air_ids": len({a for r in withid for a in r["air_ids"].split(";")}), "lake_matches_name_key_exact": kinds.count("exact"), "lake_matches_token_rule_only": kinds.count("token_rule"),
             "air_ids_shared_by_two_sites": {a: v for a, v in shared.items()}, "same_street_name_mismatch_no_id": lead,
             "sites_with_id_from_frs": sum(any("frs" in x.split(":")[1].split("+") for x in r["route_per_id"].split(";") if x) for r in withid),
             "sites_with_id_from_lake": sum(any("lake" in x.split(":")[1].split("+") for x in r["route_per_id"].split(";") if x) for r in withid),
             "frs_only": sum(r["routes"] == "frs" for r in withid), "lake_only": sum(r["routes"] == "lake" for r in withid), "both": sum(r["routes"] == "frs;lake" for r in withid),
             "with_id_done_2026_11_18": sum(r["done_2026_11_18"] == "Y" for r in withid),
             "with_id_searched_2026_11_18_no_permit": sum(r["done_2026_11_18"] == "N" and r["site_id"] in old for r in withid),
             "with_id_new": sum(r["site_id"] not in old for r in withid)}
    return out, stats

def main():
    out, stats = compute()
    with open(HERE / "frame.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]), lineterminator="\n"); w.writeheader(); w.writerows(out)
    json.dump(stats, open(HERE / "frame_stats.json", "w"), indent=1); print(json.dumps(stats, indent=1))

if __name__ == "__main__": main()
