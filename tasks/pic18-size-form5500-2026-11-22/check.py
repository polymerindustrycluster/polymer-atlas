#!/usr/bin/env python3
"""Replay the Form 5500 follow-up packet from the raw store.
1. every packet.csv row is replayed from the raw file by path, sha256 and locator (the size sprint's replay: street equality on the sponsor mailing/location
   line, name class, count -> band, source date, frame membership, single active Atlas site);
2. the sponsor EIN is read from the replayed raw row, then ALL six national Form 5500 / 5500-SF files (plan years 2023-2025) are scanned for that EIN with no
   address filter: the scan must find exactly the filings listed in sponsor_plan_inventory.csv, each equal to its raw row;
3. build.py's two tests are re-run on the scanned filings and must reproduce packet.csv and holds.csv exactly;
4. --selftest plants a wrong band, a second positive plan and a newer return of the same plan; each must be caught.
usage: check.py --raw <store>/raw [--selftest] [--no-hash]"""
import argparse, csv, importlib.util, io, sys, zipfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
SIZE = HERE.parent / "pic18-size-sprint-2026-11-22"
sys.path.insert(0, str(SIZE))
import check as SC  # noqa: E402  (size sprint check: replay of one row)
import build as B  # noqa: E402
spec = importlib.util.spec_from_file_location("fbuild", HERE / "build.py"); F = importlib.util.module_from_spec(spec); spec.loader.exec_module(F)
csv.field_size_limit(10**9)
rd = lambda p: list(csv.DictReader(open(p, newline="", encoding="utf-8")))

def scan(raw, eins):
    """every filing under the EINs in the six national files, in the same shape as extract_ein.py"""
    out = []
    for kind, pre in (("5500", "F_5500"), ("SF", "F_5500_SF")):
        for y in (2023, 2024, 2025):
            fn = f"form5500/2026-11-22-archive-snapshot/raw/{pre}_{y}_Latest.zip"; mem = f"{pre.lower()}_{y}_latest.csv"
            with io.TextIOWrapper(zipfile.ZipFile(f"{raw}/{fn}").open(mem), encoding="utf-8-sig", errors="replace", newline="") as f:
                for i, r in enumerate(csv.DictReader(f), 1):
                    r = {k.lower(): v for k, v in r.items()}
                    ein = r["sf_spons_ein"] if kind == "SF" else r["spons_dfe_ein"]
                    if ein not in eins: continue
                    g = (lambda a, b: r.get(b if kind == "SF" else a, ""))
                    out.append(dict(ein=ein, pn=g("spons_dfe_pn", "sf_plan_num"), plan_name=g("plan_name", "sf_plan_name"), form=kind, file=fn, member=mem, row=i, rid=r["ack_id"],
                                    plan_year=g("form_plan_year_begin_date", "sf_plan_year_begin_date"), tax_prd=g("form_tax_prd", "sf_tax_prd"), active=g("tot_active_partcp_cnt", "sf_tot_act_partcp_eoy_cnt"),
                                    cb=r.get("collective_bargain_ind", "") if kind == "5500" else r.get("collectively_bargained", ""), pension=g("type_pension_bnft_code", "sf_type_pension_bnft_code"),
                                    welfare=g("type_welfare_bnft_code", "sf_type_welfare_bnft_code"), mail1=g("spons_dfe_mail_us_address1", "sf_spons_us_address1"), loc1=g("spons_dfe_loc_us_address1", "sf_spons_loc_us_address1")))
    return out

def derive(inputs, inv, eins, sites):
    res = F.evaluate(inputs, inv, eins, sites)
    return {r["p"]["site_id"]: ("survive" if not r["why"] else r["why"][0][0]) for r in res}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--raw", required=True); ap.add_argument("--selftest", action="store_true"); ap.add_argument("--no-hash", action="store_true"); ap.add_argument("--base-data"); a = ap.parse_args()
    packet = rd(HERE / "packet.csv"); holds = {r["site_id"]: r for r in rd(HERE / "holds.csv")}; inputs = rd(HERE / "inputs_28.csv"); inv_pub = rd(HERE / "sponsor_plan_inventory.csv")
    orgs, sites = B.load_atlas(a.base_data); fr_ids = {r["site_id"] for r in rd(SIZE / "frame.csv")}
    man = {}
    for ln in open(f"{a.raw}/MANIFEST.sha256"): h, _, p = ln.rstrip("\n").partition("  "); man[p] = h
    errs = []
    # 1. replay the surviving rows (and the held candidates' selected rows) from the raw files
    cand = [dict(p, r13_source="3", source="form5500") for p in inputs]
    errs += SC.run(cand, a.raw, orgs, sites, fr_ids, man, not a.no_hash)
    if {p["site_id"] for p in packet} | set(holds) != {p["site_id"] for p in inputs} or {p["site_id"] for p in packet} & set(holds): errs.append("packet + holds do not partition the 28 candidates")
    # 2. EIN of each selected row, then the full national scan
    got = SC.fetch_rows(a.raw, cand); eins = {}
    for p in cand:
        m, n, _ = SC.parse_loc(p["row_locator"]); r = got[(p["source_file"], m)][n]; eins[p["site_id"]] = r.get("spons_dfe_ein") or r.get("sf_spons_ein")
    inv = scan(a.raw, set(eins.values()))
    keys = {(r["file"], r["member"], r["row"], r["rid"]) for r in inv}
    pub = {(r["row_locator"].split("|")[0], r["row_locator"].split("|")[1], r["row_locator"].split("|")[2]) for r in inv_pub}
    scanned = {(r["member"], f"row={r['row']}", f"id={r['rid']}") for r in inv}
    if scanned != pub: errs.append(f"the national scan finds {len(scanned)} filings under the 28 EINs, the published inventory lists {len(pub)}; differences {len(scanned ^ pub)}")
    # 3. the tests, re-run from the scan
    der = derive(inputs, inv, eins, sites)
    for sid, v in der.items():
        mine = "survive" if sid in {p["site_id"] for p in packet} else holds[sid]["reason"]
        if v != mine: errs.append(f"{sid}: the scan gives {v}, the packet says {mine}")
    print(f"replayed {len(cand)} selected rows; national scan found {len(inv)} filings under {len(set(eins.values()))} EINs; survivors {sum(1 for v in der.values() if v == 'survive')} of {len(der)}: {len(errs)} failures"); [print("  FAIL", e) for e in errs[:30]]
    bad = bool(errs)
    if a.selftest:
        sid = next(p["site_id"] for p in packet); ein = eins[sid]
        bad_band = [dict(cand[0], band=next(b for b in B.BANDS if b != cand[0]["band"]))]
        c1 = any("bands to" in e for e in SC.run(bad_band, a.raw, orgs, sites, fr_ids, man, False))
        extra = dict(next(r for r in inv if r["ein"] == ein), pn="599", rid="PLANTED1", active="12", plan_year="2025-01-01", tax_prd="2025-12-31")
        c2 = derive(inputs, inv + [extra], eins, sites)[sid] == "f5500_multiple_plans"
        sel = next(r for r in inv if r["ein"] == ein and r["rid"] == next(p for p in inputs if p["site_id"] == sid)["row_locator"].split("id=")[1])
        newer = dict(sel, rid="PLANTED2", plan_year="2026-01-01", tax_prd="2026-12-31", mail1="1 Planted Rd", loc1="")
        c3 = derive(inputs, inv + [newer], eins, sites)[sid] == "newer_return_of_same_plan"
        print("selftest wrong band caught:", c1, "| a second positive plan number holds the sponsor:", c2, "| a newer return of the same plan holds the older filing:", c3); bad = bad or not (c1 and c2 and c3)
    sys.exit(1 if bad else 0)
if __name__ == "__main__": main()
