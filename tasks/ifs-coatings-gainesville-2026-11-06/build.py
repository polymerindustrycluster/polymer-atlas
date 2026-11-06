"""Create SITE-019100, IFS Coatings - Gainesville, under ORG-013500 with its evidence. Idempotent; rerun on fresh main."""
import csv, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from shard_io import append_sorted
sys.path.insert(0, str(ROOT/'tasks/corroborated-tx-2-2026-11-06'))
from research import found  # house in-order word matcher
DATE, BY = '2026-11-06', 'claude-code ifs-coatings-gainesville-2026-11-06'
SITE, ORG = 'SITE-019100', 'ORG-013500'
CERT = 'https://www.ifscoatings.com/downloads/IFS-Coatings-Inc.-9001-Certificate-Exp-April-13-2029-2026.pdf'
FRS = 'https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id=110059616973'


def read(p):
    with open(p, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def witnessed(w, ita):
    """Raw check: own-site quote in order in the re-fetched certificate text; federal rows against stored extracts."""
    if w['witness'] == 'FRS':
        frs = json.loads((HERE/'frs_110059616973_2026-11-06.json').read_text())['Results']['FRSFacility'][0]
        census = json.loads((HERE/'census_county_2026-11-06.json').read_text())
        return (frs['CountyName'] == 'COOKE' and frs['FIPSCode'] == census['county']['GEOID'] == w['quote']
                and census['county']['BASENAME'] == 'Cooke' and census['input']['location'] == {'x': float(frs['Longitude83']), 'y': float(frs['Latitude83'])})
    if w['witness'].startswith('ITA:'):
        r = ita[w['witness'][4:]]
        ok = r['establishment_name'].startswith('IFS Coatings, Inc.') and r['street'] == '3601 N Interstate 35' and r['zip5'] == '76240'
        return ok and (w['quote'] == 'existence' or (r['naics_code'] == w['quote'] and r['industry_description'] == 'Powder coatings manufacturing'))
    return found((HERE/w['witness']).read_text(), w['quote'])


def site_row(header):
    v = dict(site_id=SITE, org_id=ORG, site_name='IFS Coatings - Gainesville', site_type='hq_and_plant', city='Gainesville', state='TX',
             zip='76240', county='Cooke', ring_primary='2', naics_primary='325510', naics_primary_source_type='government_filing',
             naics_confidence='medium', processes='coating_formulation', materials='coatings', operating_status='active',
             sources=(f'{CERT}; OSHA ITA Form 300A CY2025 establishment 73137 (IFS Coatings, Inc.(Texas)); '
                      f'OSHA inspection 346783756, https://www.osha.gov/ords/imis/establishment.inspection_detail?id=346783756; EPA FRS registry 110059616973 ({FRS})'),
             verification_tier='B', last_verified=DATE, created_by=BY,
             notes=(f'Created {DATE} (tasks/ifs-coatings-gainesville-2026-11-06) from held lead LF-TX-00505 (tasks/corroborated-tx-2-2026-11-06), whose settling fact '
                    '(parent of record) was met by ORG-013500 in PR #243. The operator\'s own ISO 9001 certificate names 3601 North I-35, Gainesville as its '
                    'design, manufacture, sales and central-function site. Federal records: OSHA ITA 73137, OSHA inspection 346783756 (NAICS 325510), '
                    'EPA FRS 110059616973 (325510 and 326299; FRS ZIP 76241, own site and OSHA 76240). County Cooke from the Census geocoder at the FRS facility point. '
                    'Tier B: federal record plus a re-fetched own-site witness (CAMPAIGN convention).'),
             street_address='3601 North I-35', county_source='physical_address', country='US')
    assert set(v) <= set(header)
    return {k: v.get(k, '') for k in header}


def main():
    ws = read(HERE/'witnesses.csv')
    ita = {r['establishment_id']: r for r in read(ROOT/'tasks/osha-ita-2026-11-01/establishments.csv')}
    ids = [w['evidence_id'] for w in ws]
    assert len(ids) == len(set(ids)) and all(332011 <= int(i[4:]) <= 332099 for i in ids)
    bad = [w['evidence_id'] for w in ws if not witnessed(w, ita)]
    assert not bad, ('raw witness failed', bad)
    data = ROOT/'data'
    orgs = {r['org_id']: r for r in read(data/'organizations_TX.csv')}
    assert orgs[ORG]['legal_name'] == 'IFS Coatings, Inc.' and orgs[ORG]['status'] == 'active', 'parent ORG-013500 missing'
    sites_all = {r['site_id']: (f.name, r) for f in data.glob('sites_*.csv') for r in read(f)}
    sp = data/'sites_TX.csv'; site = site_row(list(read(sp)[0]))
    assert sites_all.get(SITE, ('sites_TX.csv', site)) == ('sites_TX.csv', site), 'SITE-019100 collision or drift'
    assert not [s for f, s in sites_all.values() if s['state'] == 'TX' and s['city'].lower() == 'gainesville' and s['street_address'].startswith('3601')
                and s['site_id'] != SITE], 'a site already holds 3601 N I-35'
    held = {e['evidence_id']: (f.name, e) for f in sorted(data.glob('evidence_*.csv')) for e in read(f)}
    held.update({e['evidence_id']: ('archive_links.csv', e) for e in read(data/'archive_links.csv')})
    new = []
    for w in ws:
        note = {'own_site': 'Raw words in order (certificate re-fetched 2026-11-06): ' + w['quote'],
                'registry': 'FRS REST fetched 2026-11-06 (copy: tasks/ifs-coatings-gainesville-2026-11-06/frs_110059616973_2026-11-06.json); Census geocoder copy census_county_2026-11-06.json',
                'government_filing': 'ITA extract fields (name, street, ZIP, NAICS) checked against tasks/osha-ita-2026-11-01/establishments.csv'}[w['source_class']]
        e = dict(evidence_id=w['evidence_id'], record_table='sites', record_id=w['record_id'], claim_type=w['claim_type'], claim_detail=w['claim_detail'],
                 source_class=w['source_class'], source_ref=w['source_ref'], observed_date=DATE, tier_effect=w['tier_effect'], created_by=BY, notes=note)
        if e['evidence_id'] in held:
            assert held[e['evidence_id']] == ('evidence_sites_TX.csv', e), ('evidence ID collision', e['evidence_id'])
        else:
            new.append(e)
    if SITE not in sites_all: append_sorted(sp, [site], 'site_id')
    if new: append_sorted(data/'evidence_sites_TX.csv', new, 'evidence_id')
    print(f'{SITE} {"created" if SITE not in sites_all else "present"} under {ORG}; evidence appended {len(new)} of {len(ws)}')


if __name__ == '__main__':
    main()
