#!/usr/bin/env python3
"""Replay the street trial from the raw store: every candidates.csv row by path + sha256 + locator (id, name, street, city equal to the
raw row; EPA date from the dated event row), then re-derive every site's disposition from the replayed rows and require it to equal
proposals.csv / holds.csv. --selftest plants (1) a candidate with a different street and (2) a stale date; both must be caught.
usage: check.py --dir . --raw <store>/raw [--selftest] [--no-hash]"""
import argparse, csv, hashlib, importlib.util, io, sys, zipfile
from collections import defaultdict
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "pic18-size-sprint-2026-11-22"))
spec = importlib.util.spec_from_file_location("tbuild", HERE / "build.py"); T = importlib.util.module_from_spec(spec); spec.loader.exec_module(T)
B = T.B
csv.field_size_limit(10**9)
MAP = {"osha_ita": ("id", ["establishment_name", "company_name"], "street_address", "city"), "osha_inspection": ("activity_nr", ["estab_name"], "site_address", "site_city"),
       "epa_rcra": ("id_number", ["facility_name"], "street_address", "city_name"), "epa_air": ("pgm_sys_id", ["facility_name"], "street_address", "city"),
       "epa_npdes": ("npdes_id", ["facility_name"], "location_address", "city"), "epa_frs": ("registry_id", ["fac_name"], "fac_street", "fac_city")}
EV = {"epa_rcra": ("id_number", "evaluation_start_date"), "epa_air": ("pgm_sys_id", "actual_end_date"), "epa_npdes": ("npdes_id", "actual_end_date")}

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 22), b""): h.update(c)
    return h.hexdigest()
def stream(path, member):
    with io.TextIOWrapper(zipfile.ZipFile(path).open(member), encoding="utf-8-sig", errors="replace", newline="") if member else open(path, newline="", encoding="utf-8-sig") as f:
        for i, r in enumerate(csv.DictReader(f), 1): yield i, {k.lower(): v for k, v in r.items()}
def loc(s):
    parts = s.split("|"); return parts[0], int(parts[1].split("=", 1)[1]), (parts[2].split("=", 1)[1] if len(parts) > 2 else "")
def fetch(raw, wants):
    """wants: {(file, member): set(rows)} -> {(file, member, row): rowdict}"""
    got = {}
    for (fn, mem), rs in wants.items():
        top = max(rs)
        for i, r in stream(f"{raw}/{fn[4:] if fn.startswith('raw/') else fn}", mem):
            if i in rs: got[(fn, mem, i)] = r
            if i >= top: break
    return got

def replay(rows, raw, do_hash, man):
    errs = []; wants = defaultdict(set)
    for r in rows:
        m, n, _ = loc(r["row_locator"]); wants[(r["source_file"], m)].add(n)
        if r["date_locator"]:
            f, m2, n2 = r["date_locator"].split("|")[0], r["date_locator"].split("|")[1], int(r["date_locator"].split("|")[2].split("=")[1]); wants[("raw/" + f, m2)].add(n2)
    got = fetch(raw, wants); hashes = {}
    for r in rows:
        tag = f"{r['site_id']} {r['source']}"; fn = r["source_file"]
        if man.get("./" + fn[4:]) != r["file_sha256"]: errs.append(f"{tag}: sha256 != MANIFEST for {fn}")
        if do_hash:
            hashes.setdefault(fn, sha(f"{raw}/{fn[4:]}"))
            if hashes[fn] != r["file_sha256"]: errs.append(f"{tag}: file hashes to {hashes[fn][:12]}")
        m, n, rid = loc(r["row_locator"]); raw_r = got.get((fn, m, n))
        if raw_r is None: errs.append(f"{tag}: no row {n} in {fn}"); continue
        idk, namek, sk, ck = MAP[r["source"]]
        if raw_r.get(idk, "") != rid: errs.append(f"{tag}: id {raw_r.get(idk)} != locator {rid}")
        if r["filing_name"] not in [raw_r.get(k, "") for k in namek]: errs.append(f"{tag}: name differs from the raw row")
        if raw_r.get(sk, "") != r["filing_street"] or raw_r.get(ck, "") != r["filing_city"]: errs.append(f"{tag}: street/city differ from the raw row: {raw_r.get(sk)!r}, {raw_r.get(ck)!r} vs {r['filing_street']!r}, {r['filing_city']!r}")
        if r["source"] in EV and r["date_locator"]:
            p = r["date_locator"].split("|"); er = got.get(("raw/" + p[0], p[1], int(p[2].split("=")[1])))
            if er is None or er.get(EV[r["source"]][0], "") != raw_r.get(idk, ""): errs.append(f"{tag}: dated event row is not this facility's")
            else:
                dv = er[EV[r["source"]][1]][:10]
                if __import__("datetime").datetime.strptime(dv, "%m/%d/%Y" if "/" in dv else "%m-%d-%Y").date().isoformat() != r["date"]: errs.append(f"{tag}: event date differs from the raw row")
        elif r["source"] == "osha_ita" and r["date"] != f"{int(float(raw_r['year_filing_for']))}-12-31": errs.append(f"{tag}: ITA year differs")
        elif r["source"] == "osha_inspection" and r["date"] != raw_r["open_date"][:10]: errs.append(f"{tag}: inspection date differs")
    return errs

def rederive(rows, sel_sites, orgs, sites):
    active = [s for s in sites if s["operating_status"] == "active"]; sd = {s["site_id"]: s for s in sites}; res = {}
    by = defaultdict(list)
    for r in rows: by[r["site_id"]].append(r)
    for sid in sel_sites:
        s = sd[sid]; held_all = B.held_names(s, orgs); held_own = {k: v for k, v in held_all.items() if not v.startswith("parent:")}
        cands = []
        for r in by[sid]:
            nm, _ = B.name_class(held_own, [r["filing_name"]]) if r["source"] != "osha_ita" else B.name_class(held_own, [r["filing_name"]])
            cands.append(dict(family=r["family"], source=r["source"], name=r["filing_name"], street=r["filing_street"], zip=r["filing_zip"], date=r["date"], name_match=r["name_match"], counts=r["counts_toward_proposal"]))
        n = sum(1 for t in active if t["org_id"] == s["org_id"] and B.squash(t["city"]) == B.squash(s["city"]) and t["state"] == s["state"])
        res[sid] = T.decide(s, n, cands)
    return res

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dir", default=str(HERE)); ap.add_argument("--raw", required=True); ap.add_argument("--selftest", action="store_true"); ap.add_argument("--no-hash", action="store_true"); a = ap.parse_args()
    d = Path(a.dir); rows = list(csv.DictReader(open(d / "candidates.csv"))); frame = [r["site_id"] for r in csv.DictReader(open(d / "frame.csv"))]
    props = {r["site_id"]: r for r in csv.DictReader(open(d / "proposals.csv"))}; holds = {r["site_id"]: r for r in csv.DictReader(open(d / "holds.csv"))}
    man = {}
    for ln in open(f"{a.raw}/MANIFEST.sha256"): h, _, p = ln.rstrip("\n").partition("  "); man[p] = h
    orgs, sites = B.load_atlas(); errs = replay(rows, a.raw, not a.no_hash, man)
    der = rederive(rows, frame, orgs, sites)
    for sid, (disp, reason, detail, key) in der.items():
        if disp == "proposal" and (sid not in props or props[sid]["proposed_street_key"] != key): errs.append(f"{sid}: re-derived proposal {key!r} not in proposals.csv")
        if disp == "hold" and (sid not in holds or holds[sid]["reason"] != reason): errs.append(f"{sid}: re-derived hold {reason} not in holds.csv")
    if set(props) | set(holds) != set(frame) or set(props) & set(holds): errs.append("proposals + holds do not partition the 25-site frame")
    print(f"replayed {len(rows)} candidate rows, re-derived {len(frame)} sites: {len(errs)} failures"); [print("  FAIL", e) for e in errs[:40]]
    bad = bool(errs)
    if a.selftest and props:
        sid = next(iter(props)); mine = [dict(r) for r in rows if r["site_id"] == sid and r["counts_toward_proposal"] == "yes"]
        p1 = [dict(mine[0])]; p1[0]["filing_street"] = "1 Planted Street"
        c1 = any("street/city differ" in e for e in replay(p1, a.raw, False, man))
        others = [dict(r) for r in rows if r["site_id"] == sid]
        for r in others:
            if r["counts_toward_proposal"] == "yes" and r["family"] == "epa": r["filing_street"] = "99 Planted Avenue"; break
        c2 = rederive(others, [sid], orgs, sites)[sid][0] != "proposal"
        print("selftest planted wrong street caught on replay:", c1, "| a disagreeing second source stops a proposal:", c2); bad = bad or not (c1 and c2)
    sys.exit(1 if bad else 0)
if __name__ == "__main__": main()
