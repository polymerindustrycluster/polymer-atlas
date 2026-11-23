#!/usr/bin/env python3
"""All filings (Form 5500 and 5500-SF, plan years 2023-2025, every state) under a list of sponsor EINs, no address filter. Streams the raw zips; never writes into the store.
usage: extract_ein.py <store>/raw <eins.csv (site_id,ein)> <out.csv>"""
import csv, io, sys, zipfile
csv.field_size_limit(10**9)
RAW, EINS, OUT = sys.argv[1:4]
want = {r["ein"] for r in csv.DictReader(open(EINS))}
out = []
for kind, pre in (("5500", "F_5500"), ("SF", "F_5500_SF")):
    for y in (2023, 2024, 2025):
        fn = f"form5500/2026-11-22-archive-snapshot/raw/{pre}_{y}_Latest.zip"; mem = f"{pre.lower()}_{y}_latest.csv"
        with io.TextIOWrapper(zipfile.ZipFile(f"{RAW}/{fn}").open(mem), encoding="utf-8-sig", errors="replace", newline="") as f:
            for i, r in enumerate(csv.DictReader(f), 1):
                r = {k.lower(): v for k, v in r.items()}
                ein = r["sf_spons_ein"] if kind == "SF" else r["spons_dfe_ein"]
                if ein not in want: continue
                g = (lambda a, b: r.get(b if kind == "SF" else a, ""))
                out.append(dict(ein=ein, pn=g("spons_dfe_pn", "sf_plan_num"), plan_name=g("plan_name", "sf_plan_name"), form=kind, file=fn, member=mem, row=i, rid=r["ack_id"],
                                plan_year=g("form_plan_year_begin_date", "sf_plan_year_begin_date"), tax_prd=g("form_tax_prd", "sf_tax_prd"),
                                active=g("tot_active_partcp_cnt", "sf_tot_act_partcp_eoy_cnt"), cb=r.get("collective_bargain_ind", "") if kind == "5500" else r.get("collectively_bargained", ""),
                                pension=g("type_pension_bnft_code", "sf_type_pension_bnft_code"), welfare=g("type_welfare_bnft_code", "sf_type_welfare_bnft_code"),
                                sponsor=g("sponsor_dfe_name", "sf_sponsor_name"), received=r["date_received"],
                                mail1=g("spons_dfe_mail_us_address1", "sf_spons_us_address1"), mailcity=g("spons_dfe_mail_us_city", "sf_spons_us_city"), mailzip=g("spons_dfe_mail_us_zip", "sf_spons_us_zip"),
                                loc1=g("spons_dfe_loc_us_address1", "sf_spons_loc_us_address1"), loccity=g("spons_dfe_loc_us_city", "sf_spons_loc_us_city")))
with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
print("filings", len(out), "EINs", len({o["ein"] for o in out}), file=sys.stderr)
