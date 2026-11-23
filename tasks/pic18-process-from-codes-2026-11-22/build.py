"""Part B builder. Read-only on data/ and on the lake. Replays matches from the 2026-11-22 lake with the repo's own matchers
(atlas.street_key via derive_last_activity.same_street, atlas.name_key / site_name_key / org_name_fields), not the source-map scratch flags.
Writes leads.csv (owner ruling 2026-11-22: SCHEMA 2.4 stands, a code is a lead and fills nothing) and summary.json."""
import csv, json, os, re, sys, hashlib
from pathlib import Path
import frame as c
sys.path.insert(0, str(c.ROOT / 'scripts'))
from atlas import street_key, name_key, site_name_key, org_name_fields, squash  # noqa: E402
from derive_last_activity import same_street  # noqa: E402
import codes
LAKE = Path(os.environ.get('ATLAS_LAKE', '/Volumes/johnpswan/work/GAC/polymer-atlas/atlas-store/lake/2026-11-22'))
SUFFIX = {'inc', 'incorporated', 'llc', 'corp', 'corporation', 'co', 'company', 'ltd', 'limited', 'lp', 'llp', 'holdings', 'holding', 'group', 'us', 'usa', 'north america', 'americas'}
PRODUCTION = {'manufacturing_plant', 'hq_and_plant'}
PRODUCTION_FOR = {'mold_tool_making': PRODUCTION | {'tool_shop'}}  # a tool shop is where molds are made
FROM_YEAR = 2023  # the filings the lake holds as current (CY2023 to CY2025); an older filing does not speak for the plant today

def duck():
    import duckdb
    if not (LAKE / 'MANIFEST.csv').exists(): raise SystemExit(f'lake not readable at {LAKE}: the gate fails rather than skips')
    return duckdb.connect()

def held_keys(s, org):
    ks = {site_name_key(s['site_name'], s['city'])}
    ks |= {name_key(v) for _, v in org_name_fields(org) if v}
    return {k for k in ks if k}

def name_ok(source_name, keys, city=''):
    # shortcut: the source-side locality strip uses the repo's site_name_key with the site's own city; exact words only
    sks = {name_key(source_name), site_name_key(source_name, city)} - {''}
    if any(x in keys or x.replace(' ', '') in {k.replace(' ', '') for k in keys} for x in sks): return 'name_key equal'
    sk = site_name_key(source_name, city) or name_key(source_name)
    for k in keys:
        if sk.startswith(k + ' ') and all(t in SUFFIX for t in re.findall(r'\S+', sk[len(k):].strip())) : return 'held name leads, suffix only'
    return ''

def locality_ok(s, state, zip5, city):
    return state == 'OH' and (zip5 and zip5 == (s['zip'] or '')[:5] or squash(city) == squash(s['city']))

def raw_manifest():
    return {r['parquet_path']: r for r in csv.DictReader(open(LAKE / 'MANIFEST.csv', newline=''))}

def matches(con, frame, orgs, eco):
    """-> list of dicts, one per matched lake row (ITA filings and SAM registrations) for frame sites."""
    by_key = {}
    for s in frame:
        k = street_key(s['street_address'])
        if k: by_key.setdefault(k, []).append(s)
    keys = list(by_key)
    out = []
    con.execute("create temp table k(k varchar)"); con.executemany('insert into k values (?)', [(x,) for x in keys])
    q = {
      'osha_ita': f"select src_path, src_row, src_key, establishment_name, street_address, k_site_street_key, k_site_state, k_site_zip5, k_site_city_norm, naics_code, year_filing_for, company_name from read_parquet('{LAKE}/osha/osha_ita_*.parquet', union_by_name=true) where k_site_street_key in (select k from k) and k_site_state='OH'",
      'sam': f"select src_path, src_row, src_key, f012_legal_business_name, f016_physical_address_line_1, k_site_street_key, k_site_state, k_site_zip5, k_site_city_norm, f033_primary_naics, f010_last_update_date, f013_dba_name from read_parquet('{LAKE}/sam/sam_entities.parquet') where k_site_street_key in (select k from k) and k_site_state='OH'",
    }
    for src, sql in q.items():
        for r in con.execute(sql).fetchall():
            if src == 'osha_ita':
                path, row, key, name, street, _, st, z, city, naics, yr, comp = r; alt = ''
            else:
                path, row, key, name, street, _, st, z, city, naics, yr, alt = r
            for s in by_key[street_key(street)]:
                org = orgs.get(s['org_id']) or eco.get(s['org_id']) or {}
                if not same_street(s['street_address'], street) or not locality_ok(s, st, z, city): continue
                basis = name_ok(name, held_keys(s, org), s['city']) or (name_ok(alt, held_keys(s, org), s['city']) if alt else '') or 'NOT HELD'
                out.append(dict(site_id=s['site_id'], org_id=s['org_id'], source=src, src_path=path, src_row=int(row), src_key=key, name_as_filed=name,
                                street_as_filed=street, naics=(naics or '').strip(), year=(yr or '')[:4], name_basis=basis))
    return out

SUGGEST = {**{k: (v[0], 'T1') for k, v in codes.T1.items()}, **{k: (v[0], 'T2') for k, v in codes.T2.items()}}
CODE_TITLE = {r['code_value']: r['code_title'] for r in csv.DictReader(open(c.ROOT / 'data/ref_codes.csv')) if r['code_system'] == 'NAICS'}
CODE_TITLE['333511'] = 'Industrial Mold Manufacturing'  # SCHEMA 2.2 line 539

def leads():
    """One row per (site, code, source class): matched on street, locality and a held name; the code maps to a suggested 3.1 term. Leads only."""
    d = c.load(); con = duck(); rows = [r for r in matches(con, d['frame'], d['orgs'], d['eco']) if r['name_basis'] != 'NOT HELD' and r['naics'] in SUGGEST]
    by = {s['site_id']: s for s in d['frame']}; g = {}
    for r in rows: g.setdefault((r['site_id'], r['naics'], r['source']), []).append(r)
    out = []
    for (sid, code, src), rs in sorted(g.items()):
        pick = max(rs, key=lambda r: (r['year'], r['src_row'])); s = by[sid]
        out.append(dict(site_id=sid, org_id=s['org_id'], site_name=s['site_name'], tier=s['verification_tier'], site_type=s['site_type'], naics=code, code_title=CODE_TITLE.get(code, ''),
                        suggested_term=SUGGEST[code][0], table_tier=SUGGEST[code][1], filing_class='osha_ita_establishment_filing' if src == 'osha_ita' else 'sam_entity_registration',
                        newest_year=pick['year'], n_rows=len(rs), src_path=pick['src_path'], src_row=pick['src_row'], src_key=pick['src_key'], name_as_filed=pick['name_as_filed'],
                        street_as_filed=pick['street_as_filed'], name_basis=pick['name_basis'], site_street=s['street_address'], naics_in_atlas=s['naics_primary'], naics_in_atlas_source=s['naics_primary_source_type']))
    return d, out

def write(name, rows):
    with open(c.T / name, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

if __name__ == '__main__':
    d, out = leads(); write('leads.csv', out)
    sm = dict(frame_sites=len(d['frame']), frame_orgs=len(d['unk']), lead_rows=len(out), lead_sites=len({r['site_id'] for r in out}), lead_orgs=len({r['org_id'] for r in out}),
              by_filing_class={k: len({r['org_id'] for r in out if r['filing_class'] == k}) for k in sorted({r['filing_class'] for r in out})},
              by_table_tier={k: len({r['org_id'] for r in out if r['table_tier'] == k}) for k in ('T1', 'T2')},
              by_term={k: len({r['org_id'] for r in out if r['suggested_term'] == k}) for k in sorted({r['suggested_term'] for r in out})})
    (c.T / 'summary.json').write_text(json.dumps(sm, indent=1)); print(json.dumps(sm, indent=1))
