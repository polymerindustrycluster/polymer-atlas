"""Named gate for the code leads: uv run --with duckdb python tasks/pic18-process-from-codes-2026-11-22/check.py
Replays every lead from the lake by file and row (not from the scratch pair flags): code, street (same_street), locality, held name, suggested term. Then runs planted
defects, each of which must be rejected. Fails (never skips) when the lake is not mounted. Leads only: nothing here fills a record (owner ruling 2026-11-22)."""
import csv, hashlib, sys
import build as b
import frame as c
from derive_last_activity import same_street

SRC = {
 'osha_ita_establishment_filing': ('osha/osha_ita_*.parquet', "establishment_name, street_address, k_site_state, k_site_zip5, k_site_city_norm, naics_code, src_key, ''", '/ita/'),
 'sam_entity_registration': ('sam/sam_entities.parquet', "f012_legal_business_name, f016_physical_address_line_1, k_site_state, k_site_zip5, k_site_city_norm, f033_primary_naics, src_key, f013_dba_name", 'SAM_PUBLIC'),
}

def lake_row(con, cls, src_path, src_row):
    glob, cols, _ = SRC[cls]
    for f in sorted(b.LAKE.glob(glob)):
        r = con.execute(f"select {cols} from read_parquet('{f}') where src_path=? and src_row=?", [src_path, int(src_row)]).fetchone()
        if r: return dict(zip(('name', 'street', 'state', 'zip5', 'city', 'naics', 'key', 'alt'), r)), f
    return None, None

def verify(con, p, fr, orgs, eco, man):
    """'' when the lead holds, else why not."""
    cls = p['filing_class']
    if cls not in SRC or SRC[cls][2] not in p['src_path']: return 'source file is not the named filing class (ITA establishment filing or SAM registration)'
    s = fr.get(p['site_id'])
    if not s: return 'site not in the process-unknown frame'
    row, f = lake_row(con, cls, p['src_path'], p['src_row'])
    if not row: return 'no lake row at that file and row'
    if row['naics'] != p['naics'] or row['key'] != p['src_key']: return 'code or key differs from the lake row'
    rel = f.relative_to(b.LAKE).as_posix()
    if hashlib.sha256(f.read_bytes()).hexdigest() != man[rel]['parquet_sha256']: return 'lake parquet hash differs from MANIFEST'
    if not same_street(s['street_address'], row['street']): return 'not the site street (same_street)'
    if not b.locality_ok(s, row['state'], row['zip5'], row['city']): return 'locality differs'
    org = orgs.get(s['org_id']) or eco.get(s['org_id']) or {}
    keys = b.held_keys(s, org)
    if not (b.name_ok(row['name'], keys, s['city']) or (row['alt'] and b.name_ok(row['alt'], keys, s['city']))): return 'no held name matches the filed name'
    sug = b.SUGGEST.get(p['naics'])
    if not sug or sug[0] != p['suggested_term'] or sug[1] != p['table_tier']: return 'suggested term is not the table term for the code'
    return ''

def main():
    con = b.duck(); man = b.raw_manifest(); d = c.load(); fr = {s['site_id']: s for s in d['frame']}
    assert (len(d['frame']), len(d['unk'])) == (333, 322), 'frame size moved: rebaseline'
    rows = list(csv.DictReader(open(c.T / 'leads.csv', newline='')))
    assert rows, 'empty leads file'
    bad = [(r['site_id'], r['naics'], verify(con, r, fr, d['orgs'], d['eco'], man)) for r in rows]; bad = [x for x in bad if x[2]]
    assert not bad, bad
    _, fresh = b.leads()
    key = lambda rs: sorted((r['site_id'], r['naics'], r['filing_class'], str(r['src_row'])) for r in rs)
    assert key(fresh) == key(rows), 'leads.csv differs from a fresh build'
    ita = next(r for r in rows if r['filing_class'] == 'osha_ita_establishment_filing'); r0 = dict(ita)
    plants = {
        'registry code passed as a filing': {**r0, 'src_path': 'echo/2026-11-22-archive-snapshot/raw/frs_downloads.zip!FRS_NAICS_CODES.csv'},
        'SAM class label on an ITA row': {**r0, 'filing_class': 'sam_entity_registration'},
        'wrong NAICS on the row': {**r0, 'naics': '326199'},
        "term that is not the code's term": {**r0, 'suggested_term': 'ink_formulation'},
        'row number off by one': {**r0, 'src_row': str(int(r0['src_row']) + 1)},
        'site not in frame': {**r0, 'site_id': 'SITE-000335'},
        'filing of another street (site swapped)': {**r0, 'site_id': next(r['site_id'] for r in rows if r['site_id'] != r0['site_id'])},
    }
    for name, row in plants.items():
        assert verify(con, row, fr, d['orgs'], d['eco'], man), f'planted defect passed: {name}'
    print('OK: frame 333 sites / 322 orgs; %d lead rows (%d sites) replayed from the lake by file and row; %d planted defects rejected' % (len(rows), len({r['site_id'] for r in rows}), len(plants)))

if __name__ == '__main__':
    sys.exit(main())
