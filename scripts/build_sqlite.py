#!/usr/bin/env python3
"""Build build/polymer-atlas.db from the canonical CSVs. Stdlib only.
The CSVs are the source of truth; this file is a generated artifact."""
import csv, sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "build" / "polymer-atlas.db"
TABLES = {"organizations": "organizations.csv", "sites": "sites.csv",
          "ecosystem": "ecosystem.csv", "inclusion_log": "inclusion_log.csv",
          "registry_links": "registry_links.csv", "members": "members.csv",
          "people": "people.csv"}

OUT.parent.mkdir(exist_ok=True)
if OUT.exists():
    OUT.unlink()
con = sqlite3.connect(OUT)
for table, fname in TABLES.items():
    with open(ROOT / "data" / fname, newline="", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        cols = rdr.fieldnames
        rows = [[(r[c] or None) for c in cols] for r in rdr]
    coldef = ", ".join(f'"{c}" TEXT' for c in cols)
    con.execute(f'CREATE TABLE "{table}" ({coldef})')
    con.executemany(f'INSERT INTO "{table}" VALUES ({",".join("?" * len(cols))})', rows)
    print(f"{table}: {len(rows)} rows")
con.execute("CREATE VIEW ohio_sites AS SELECT * FROM sites WHERE state='OH'")
# [v1.2] Membership presentation layer: one row per website-listed member,
# record fields joined where a record exists; member-only rows keep NULLs.
con.execute("""CREATE VIEW pic_members AS
SELECT m.member_row_id,
       m.display_name,
       m.member_tier,
       m.record_class,
       m.org_id,
       COALESCE(o.legal_name, e.legal_name) AS record_name,
       COALESCE(o.ring_primary, '5') AS ring_primary,
       COALESCE(o.verification_tier, e.verification_tier) AS verification_tier,
       m.member_since,
       m.membership_source_url,
       m.snapshot_date
FROM members m
LEFT JOIN organizations o ON m.record_class = 'organization' AND o.org_id = m.org_id
LEFT JOIN ecosystem e ON m.record_class = 'ecosystem' AND e.org_id = m.org_id""")
# Supporting indexes for the v1.1/v1.2 structures.
for stmt in (
    "CREATE INDEX idx_org_pic_member ON organizations(pic_member)",
    "CREATE INDEX idx_eco_pic_member ON ecosystem(pic_member)",
    "CREATE INDEX idx_links_org ON registry_links(org_id)",
    "CREATE INDEX idx_links_registry ON registry_links(registry, registry_id)",
    "CREATE INDEX idx_members_org ON members(org_id)",
    "CREATE INDEX idx_people_inst ON people(institution_org_id)",
    "CREATE INDEX idx_sites_street ON sites(street_address)",
):
    con.execute(stmt)
con.commit(); con.close()
print(f"Built {OUT}")
