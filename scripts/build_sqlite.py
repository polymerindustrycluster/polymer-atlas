#!/usr/bin/env python3
"""Build build/polymer-atlas.db from the canonical CSVs. Stdlib only.
The CSVs are the source of truth; this file is a generated artifact."""
import csv, sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "build" / "polymer-atlas.db"
TABLES = {
          "ecosystem": "ecosystem.csv", "inclusion_log": "inclusion_log.csv",
          "registry_links": "registry_links.csv", "members": "members.csv",
          "people": "people.csv", "programs": "programs.csv",
          "events": "events.csv", "event_participation": "event_participation.csv",
          "evidence": "evidence.csv", "relationships": "relationships.csv",
          "site_capabilities": "site_capabilities.csv"}

OUT.parent.mkdir(exist_ok=True)
if OUT.exists():
    OUT.unlink()
con = sqlite3.connect(OUT)

# [pass 14 Stage C] Sharded tables: built from the shard glob union
# (SCHEMA Appendix C); merged exports emitted to build/ as release
# artifacts, globally ID-sorted, never committed to data/.
import glob as _glob
for table, idcol in (("organizations", "org_id"), ("sites", "site_id")):
    files = sorted(_glob.glob(str(ROOT / "data" / f"{table}_*.csv")))
    cols, rows_all, counts = None, [], {}
    for fp in files:
        with open(fp, newline="", encoding="utf-8") as f:
            rdr = csv.DictReader(f)
            cols = rdr.fieldnames
            part = list(rdr)
        counts[Path(fp).stem] = len(part)
        rows_all.extend(part)
    coldef = ", ".join(f'"{c}" TEXT' for c in cols)
    con.execute(f'CREATE TABLE "{table}" ({coldef})')
    con.executemany(f'INSERT INTO "{table}" VALUES ({",".join("?" * len(cols))})',
                    [[(r[c] or None) for c in cols] for r in rows_all])
    print(f"{table}: {len(rows_all)} rows from shards " +
          ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    merged = sorted(rows_all, key=lambda r: r[idcol])
    with open(OUT.parent / f"{table}_all.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(merged)
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
# [v1.3] Program layer: program rows joined to the institution's legal_name
# (institutions live in ecosystem or organizations).
con.execute("""CREATE VIEW institution_programs AS
SELECT p.*,
       COALESCE(e.legal_name, o.legal_name) AS institution_name
FROM programs p
LEFT JOIN ecosystem e ON e.org_id = p.institution_org_id
LEFT JOIN organizations o ON o.org_id = p.institution_org_id""")
# [v1.5] Events layer: who showed up where (series + edition + role).
con.execute("""CREATE VIEW org_event_participation AS
SELECT p.org_id,
       COALESCE(o.legal_name, e.legal_name) AS org_name,
       p.event_id,
       ev.name AS event_name,
       p.edition_year,
       p.edition_name,
       p.role,
       p.role_detail
FROM event_participation p
JOIN events ev ON ev.event_id = p.event_id
LEFT JOIN organizations o ON o.org_id = p.org_id
LEFT JOIN ecosystem e ON e.org_id = p.org_id""")
# [v1.6] Integrity & capability layer views.
con.execute("""CREATE VIEW record_evidence AS
SELECT e.*,
       CASE e.record_table
         WHEN 'organizations' THEN (SELECT legal_name FROM organizations o WHERE o.org_id = e.record_id)
         WHEN 'ecosystem' THEN (SELECT legal_name FROM ecosystem x WHERE x.org_id = e.record_id)
         WHEN 'sites' THEN (SELECT site_name FROM sites s WHERE s.site_id = e.record_id)
         WHEN 'programs' THEN (SELECT program_name FROM programs p WHERE p.program_id = e.record_id)
       END AS record_name
FROM evidence e""")
con.execute("""CREATE VIEW org_liveness_watch AS
SELECT * FROM organizations
WHERE monitor_watch = 'true' OR COALESCE(liveness_signal, '') <> ''""")
con.execute("""CREATE VIEW org_relationships AS
SELECT r.relationship_id,
       r.from_org_id,
       COALESCE(o1.legal_name, e1.legal_name) AS from_name,
       r.relationship_type,
       r.to_org_id,
       COALESCE(o2.legal_name, e2.legal_name) AS to_name,
       r.effective_from,
       r.effective_to,
       r.basis
FROM relationships r
LEFT JOIN organizations o1 ON o1.org_id = r.from_org_id
LEFT JOIN ecosystem e1 ON e1.org_id = r.from_org_id
LEFT JOIN organizations o2 ON o2.org_id = r.to_org_id
LEFT JOIN ecosystem e2 ON e2.org_id = r.to_org_id""")
con.execute("""CREATE VIEW tier1_organizations AS
SELECT * FROM organizations WHERE COALESCE(tier1_qualifier, '') <> ''""")
con.execute("""CREATE VIEW org_capability_rollup AS
SELECT c.org_id,
       COALESCE(o.legal_name, e.legal_name) AS org_name,
       c.capability_type,
       c.term,
       COUNT(DISTINCT c.site_id) AS site_count,
       MAX(c.observed_date) AS latest_observed_date
FROM site_capabilities c
LEFT JOIN organizations o ON o.org_id = c.org_id
LEFT JOIN ecosystem e ON e.org_id = c.org_id
WHERE COALESCE(c.withdrawn_date, '') = ''
GROUP BY c.org_id, c.capability_type, c.term""")
con.execute("""CREATE VIEW site_capability_detail AS
SELECT s.site_id,
       s.site_name,
       s.city,
       s.state,
       c.*
FROM site_capabilities c
JOIN sites s ON s.site_id = c.site_id""")
con.execute("""CREATE VIEW site_groups AS
SELECT s.site_group_id,
       s.site_id,
       s.site_name,
       s.org_id,
       s.city,
       s.state
FROM sites s
WHERE COALESCE(s.site_group_id, '') <> ''""")
# Supporting indexes for the v1.1/v1.2 structures.
for stmt in (
    "CREATE INDEX idx_org_pic_member ON organizations(pic_member)",
    "CREATE INDEX idx_eco_pic_member ON ecosystem(pic_member)",
    "CREATE INDEX idx_links_org ON registry_links(org_id)",
    "CREATE INDEX idx_links_registry ON registry_links(registry, registry_id)",
    "CREATE INDEX idx_members_org ON members(org_id)",
    "CREATE INDEX idx_people_inst ON people(institution_org_id)",
    "CREATE INDEX idx_sites_street ON sites(street_address)",
    "CREATE INDEX idx_programs_inst ON programs(institution_org_id)",
    "CREATE INDEX idx_programs_type ON programs(program_type)",
    "CREATE INDEX idx_events_organizer ON events(organizer_org_id)",
    "CREATE INDEX idx_part_event ON event_participation(event_id)",
    "CREATE INDEX idx_part_org ON event_participation(org_id)",
    "CREATE INDEX idx_part_year ON event_participation(edition_year)",
    "CREATE INDEX idx_evidence_record ON evidence(record_table, record_id)",
    "CREATE INDEX idx_evidence_claim ON evidence(record_table, record_id, claim_type)",
    "CREATE INDEX idx_evidence_class ON evidence(source_class)",
    "CREATE INDEX idx_org_liveness ON organizations(liveness_signal)",
    "CREATE INDEX idx_org_watch ON organizations(monitor_watch)",
    "CREATE INDEX idx_rel_from ON relationships(from_org_id)",
    "CREATE INDEX idx_rel_to ON relationships(to_org_id)",
    "CREATE INDEX idx_rel_type ON relationships(relationship_type)",
    "CREATE INDEX idx_org_tier1 ON organizations(tier1_qualifier)",
    "CREATE INDEX idx_cap_site ON site_capabilities(site_id)",
    "CREATE INDEX idx_cap_org ON site_capabilities(org_id)",
    "CREATE INDEX idx_cap_term ON site_capabilities(capability_type, term)",
    "CREATE INDEX idx_sites_group ON sites(site_group_id)",
    "CREATE INDEX idx_sites_county_source ON sites(county_source)",
):
    con.execute(stmt)
con.commit(); con.close()
print(f"Built {OUT}")
