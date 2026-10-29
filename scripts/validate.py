#!/usr/bin/env python3
"""Validate the Polymer Atlas CSVs. Stdlib only. Exit 1 on any error.

Checks (v1 gate, per AGENTS.md / docs/SCHEMA.md §4.7):
- org_id / site_id format and uniqueness
- ring_primary in 1..5; verification_tier in A/B/C/U
- every record has >=1 source; tier A/B records must have last_verified
- NAICS, when present, must carry source_type + confidence
- Ohio sites must have a county
- sites.org_id must exist in organizations.csv or ecosystem.csv
- multi-value fields use ';' (no '|' or ',' inside a cell is enforced by CSV parsing)
"""
import csv, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
errors, warnings = [], []

def rows(name):
    with open(DATA / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

orgs = rows("organizations.csv")
sites = rows("sites.csv")
eco = rows("ecosystem.csv")

org_ids = set()
for i, r in enumerate(orgs, 2):
    oid = r["org_id"].strip()
    if not re.fullmatch(r"ORG-\d{6}", oid):
        errors.append(f"organizations.csv:{i} bad org_id {oid!r}")
    if oid in org_ids:
        errors.append(f"organizations.csv:{i} duplicate org_id {oid}")
    org_ids.add(oid)
    if r["ring_primary"].strip() not in {"1", "2", "3", "4", "5"}:
        errors.append(f"organizations.csv:{i} {oid} ring_primary not 1-5")
    if r["verification_tier"].strip() not in {"A", "B", "C", "U"}:
        errors.append(f"organizations.csv:{i} {oid} bad verification_tier")
    if not r["sources"].strip():
        errors.append(f"organizations.csv:{i} {oid} has no source")
    if r["verification_tier"].strip() in {"A", "B"} and not r["last_verified"].strip():
        errors.append(f"organizations.csv:{i} {oid} tier A/B without last_verified")
    if r["naics_primary"].strip():
        if not r["naics_primary_source_type"].strip() or not r["naics_confidence"].strip():
            errors.append(f"organizations.csv:{i} {oid} NAICS without provenance/confidence")
    if not r["description_1line"].strip():
        warnings.append(f"organizations.csv:{i} {oid} missing description_1line")
    succ = r.get("successor_org_id", "").strip()
    if succ and succ not in org_ids and succ == oid:
        errors.append(f"organizations.csv:{i} {oid} is its own successor")

eco_ids = {r["org_id"].strip() for r in eco}
all_ids = org_ids | eco_ids

site_ids = set()
for i, r in enumerate(sites, 2):
    sid = r["site_id"].strip()
    if not re.fullmatch(r"SITE-\d{6}", sid):
        errors.append(f"sites.csv:{i} bad site_id {sid!r}")
    if sid in site_ids:
        errors.append(f"sites.csv:{i} duplicate site_id {sid}")
    site_ids.add(sid)
    if r["org_id"].strip() not in all_ids:
        errors.append(f"sites.csv:{i} {sid} org_id {r['org_id']!r} not found")
    if r["state"].strip() == "OH" and not r["county"].strip():
        # Owner ruling 2026-10-29: a blank county is permitted ONLY when the
        # site is explicitly queued for the parcel layer (notes carry the
        # marker "parcel candidate queue"). Any other blank Ohio county is
        # an error — the exception marks a pending state, never missing data.
        if "parcel candidate queue" in r["notes"]:
            warnings.append(f"sites.csv:{i} {sid} Ohio site without county (parcel candidate queue — permitted, owner ruling 2026-10-29)")
        else:
            errors.append(f"sites.csv:{i} {sid} Ohio site without county")
    if r["verification_tier"].strip() not in {"A", "B", "C", "U"}:
        errors.append(f"sites.csv:{i} {sid} bad verification_tier")
    if not r["sources"].strip():
        errors.append(f"sites.csv:{i} {sid} has no source")

for w in warnings:
    print(f"WARN  {w}")
for e in errors:
    print(f"ERROR {e}")
print(f"\n{len(orgs)} organizations, {len(sites)} sites, {len(eco)} ecosystem rows checked.")
if errors:
    print(f"FAILED with {len(errors)} error(s).")
    sys.exit(1)
print("OK — validation passed.")
