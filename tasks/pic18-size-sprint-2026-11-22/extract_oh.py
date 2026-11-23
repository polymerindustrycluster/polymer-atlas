#!/usr/bin/env python3
"""Stage 1 of build.py: stream the raw store and keep only Ohio-address rows, each with a row locator
(file path under raw/, 1-based data-row ordinal in that file, and the file's own id). Never writes into the store.
usage: extract_oh.py <store_raw_dir> <out_dir> ita|insp|f5500"""
import csv, gzip, io, os, sys, zipfile
csv.field_size_limit(10**9)
RAW, OUT, WHAT = sys.argv[1], sys.argv[2], sys.argv[3]
SNAP = "{}/2026-11-22-archive-snapshot"
os.makedirs(OUT, exist_ok=True)

def rows_of(zf_or_path, member=None):
    if member is None:
        f = open(zf_or_path, newline="", encoding="utf-8-sig", errors="replace")
    else:
        f = io.TextIOWrapper(zipfile.ZipFile(zf_or_path).open(member), encoding="utf-8-sig", errors="replace", newline="")
    with f:
        for i, r in enumerate(csv.DictReader(f), 1):
            yield i, {k.lower(): v for k, v in r.items()}

def write(name, cols, rows):
    with open(f"{OUT}/{name}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(cols)
        for r in rows: w.writerow([r.get(c, "") for c in cols])

if WHAT == "ita":
    out = []
    base = f"{RAW}/osha/" + SNAP.format("") .lstrip("/")
    d = f"{RAW}/osha/2026-11-22-archive-snapshot/raw/ita"
    for fn in sorted(os.listdir(d)):
        if not (fn.endswith(".zip") or fn.endswith(".csv")): continue
        zp = f"{d}/{fn}"
        mem = zipfile.ZipFile(zp).namelist()[0] if fn.endswith(".zip") else None
        for i, r in rows_of(zp, mem):
            if (r.get("state") or "").strip().upper() != "OH": continue
            r.update(file=f"osha/2026-11-22-archive-snapshot/raw/ita/{fn}", member=mem or "", row=i,
                     rid=r.get("id", ""), submitted=r.get("date_submitted") or r.get("created_timestamp", ""))
            out.append(r)
    write("ita_oh", ["file", "member", "row", "rid", "year_filing_for", "establishment_name", "company_name", "ein", "street_address", "city", "state", "zip_code", "annual_average_employees", "size", "ein", "submitted", "change_reason"], out)
elif WHAT == "insp":
    out = []
    zp = f"{RAW}/osha/2026-11-22-archive-snapshot/raw/OSHA_inspection.zip"
    for mem in sorted(zipfile.ZipFile(zp).namelist()):
        for i, r in rows_of(zp, mem):
            if (r.get("site_state") or "").strip().upper() != "OH": continue
            r.update(file="osha/2026-11-22-archive-snapshot/raw/OSHA_inspection.zip", member=mem, row=i, rid=r.get("activity_nr", ""))
            out.append(r)
    write("insp_oh", ["file", "member", "row", "rid", "estab_name", "site_address", "site_city", "site_state", "site_zip", "nr_in_estab", "open_date", "insp_type"], out)
elif WHAT == "f5500":
    out = []
    for kind, pre in (("5500", "F_5500"), ("SF", "F_5500_SF")):
        for y in (2023, 2024, 2025):
            zp = f"{RAW}/form5500/2026-11-22-archive-snapshot/raw/{pre}_{y}_Latest.zip"
            mem = f"{pre.lower()}_{y}_latest.csv"
            for i, r in rows_of(zp, mem):
                if kind == "5500":
                    st = {(r.get("spons_dfe_mail_us_state") or "").upper(), (r.get("spons_dfe_loc_us_state") or "").upper()}
                    if "OH" not in st: continue
                    rec = dict(sponsor=r["sponsor_dfe_name"], dba=r.get("spons_dfe_dba_name", ""), mail1=r["spons_dfe_mail_us_address1"], mail2=r["spons_dfe_mail_us_address2"], mailcity=r["spons_dfe_mail_us_city"], mailst=r["spons_dfe_mail_us_state"],
                               loc1=r["spons_dfe_loc_us_address1"], loc2=r["spons_dfe_loc_us_address2"], loccity=r["spons_dfe_loc_us_city"], locst=r["spons_dfe_loc_us_state"],
                               ein=r["spons_dfe_ein"], plan_name=r.get("plan_name", ""), pn=r["spons_dfe_pn"], cb=r.get("collective_bargain_ind", ""), pension=r.get("type_pension_bnft_code", ""), welfare=r.get("type_welfare_bnft_code", ""), active=r.get("tot_active_partcp_cnt", ""), boy=r.get("tot_partcp_boy_cnt", ""),
                               plan_year=r["form_plan_year_begin_date"], tax_prd=r.get("form_tax_prd", ""), received=r["date_received"])
                else:
                    st = {(r.get("sf_spons_us_state") or "").upper(), (r.get("sf_spons_loc_us_state") or "").upper()}
                    if "OH" not in st: continue
                    rec = dict(sponsor=r["sf_sponsor_name"], dba=r.get("sf_sponsor_dfe_dba_name", ""), mail1=r["sf_spons_us_address1"], mail2=r["sf_spons_us_address2"], mailcity=r["sf_spons_us_city"], mailst=r["sf_spons_us_state"],
                               loc1=r["sf_spons_loc_us_address1"], loc2=r["sf_spons_loc_us_address2"], loccity=r["sf_spons_loc_us_city"], locst=r["sf_spons_loc_us_state"],
                               ein=r["sf_spons_ein"], plan_name=r.get("sf_plan_name", ""), pn=r.get("sf_plan_num", ""), cb="", pension=r.get("sf_type_pension_bnft_code", ""), welfare=r.get("sf_type_welfare_bnft_code", ""), active=r.get("sf_tot_act_partcp_eoy_cnt", ""), boy=r.get("sf_tot_partcp_boy_cnt", ""),
                               plan_year=r["sf_plan_year_begin_date"], tax_prd=r.get("sf_tax_prd", ""), received=r["date_received"])
                rec.update(file=f"form5500/2026-11-22-archive-snapshot/raw/{pre}_{y}_Latest.zip", member=mem, row=i, rid=r["ack_id"], form=kind)
                out.append(rec)
    write("f5500_oh", ["file", "member", "row", "rid", "form", "sponsor", "dba", "mail1", "mail2", "mailcity", "mailst", "loc1", "loc2", "loccity", "locst", "ein", "plan_name", "pn", "cb", "pension", "welfare", "active", "boy", "plan_year", "tax_prd", "received"], out)
print(WHAT, "kept", len(out))
