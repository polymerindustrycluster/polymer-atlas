#!/usr/bin/env python3
"""Stream the raw EPA ECHO/FRS zips to an Ohio-only cache (never writes into the store). One row per Ohio facility with its
row locator and, for RCRA / ICIS-AIR / NPDES, the latest dated compliance event (evaluation, FCE/PCE, inspection) with ITS locator.
FRS rows are undated (no date column in FRS_FACILITIES).
usage: extract_epa.py <store>/raw <out_csv>"""
import csv, io, sys, zipfile
from datetime import datetime
csv.field_size_limit(10**9)
RAW, OUT = sys.argv[1], sys.argv[2]; BASE = "echo/2026-11-22-archive-snapshot/raw/"
def stream(zipname, member):
    with io.TextIOWrapper(zipfile.ZipFile(RAW + "/" + BASE + zipname).open(member), encoding="utf-8-sig", errors="replace", newline="") as f:
        for i, r in enumerate(csv.DictReader(f), 1): yield i, r
def iso(s):
    for fmt in ("%m/%d/%Y", "%m-%d-%Y", "%Y-%m-%d"):
        try: return datetime.strptime(s.strip()[:10], fmt).date().isoformat()
        except ValueError: pass
    return ""
FAM = [  # family, zip, facility member, id, name, street, city, state, zip, event member, event id, event date
    ("rcra", "rcra_downloads.zip", "RCRA_FACILITIES.csv", "ID_NUMBER", "FACILITY_NAME", "STREET_ADDRESS", "CITY_NAME", "STATE_CODE", "ZIP_CODE", "RCRA_EVALUATIONS.csv", "ID_NUMBER", "EVALUATION_START_DATE"),
    ("air", "ICIS-AIR_downloads.zip", "ICIS-AIR_FACILITIES.csv", "PGM_SYS_ID", "FACILITY_NAME", "STREET_ADDRESS", "CITY", "STATE", "ZIP_CODE", "ICIS-AIR_FCES_PCES.csv", "PGM_SYS_ID", "ACTUAL_END_DATE"),
    ("npdes", "npdes_downloads.zip", "ICIS_FACILITIES.csv", "NPDES_ID", "FACILITY_NAME", "LOCATION_ADDRESS", "CITY", "STATE_CODE", "ZIP", "NPDES_INSPECTIONS.csv", "NPDES_ID", "ACTUAL_END_DATE"),
    ("frs", "frs_downloads.zip", "FRS_FACILITIES.csv", "REGISTRY_ID", "FAC_NAME", "FAC_STREET", "FAC_CITY", "FAC_STATE", "FAC_ZIP", None, None, None)]
out = []
for fam, z, mem, cid, cn, cs, cc, cst, czip, emem, eid, edate in FAM:
    rows = {}
    for i, r in stream(z, mem):
        if r[cst].strip().upper() == "OH":
            rows.setdefault(r[cid], []).append(dict(family=fam, file=BASE + z, member=mem, row=i, id=r[cid], name=r[cn], street=r[cs], city=r[cc], zip=r[czip], event_date="", event_file="", event_member="", event_row=""))
    if emem:
        best = {}
        for i, r in stream(z, emem):
            k = r[eid]
            if k in rows:
                d = iso(r[edate])
                if d and d > best.get(k, ("",))[0]: best[k] = (d, i)
        for k, (d, i) in best.items():
            for x in rows[k]: x.update(event_date=d, event_file=BASE + z, event_member=emem, event_row=i)
    for v in rows.values(): out.extend(v)
    print(fam, "facilities", sum(len(v) for v in rows.values()), file=sys.stderr)
with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
