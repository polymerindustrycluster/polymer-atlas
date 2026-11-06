"""Create ORG-013500 IFS Coatings, Inc. and re-point SITE-006097 (Ardmore) to it. Idempotent; rerun on fresh main."""
import csv, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from shard_io import append_sorted
sys.path.insert(0, str(ROOT/'tasks/corroborated-tx-2-2026-11-06'))
from research import found  # house in-order word matcher
PERSIST = Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/ifs-coatings-parent-2026-11-06')
DATE, BY = '2026-11-06', 'claude-code ifs-coatings-parent-2026-11-06'
ORG, SITE, OLD = 'ORG-013500', 'SITE-006097', 'ORG-002633'
CERT = 'https://www.ifscoatings.com/downloads/IFS-Coatings-Inc.-9001-Certificate-Exp-April-13-2029-2026.pdf'
NOTE = (f' Re-pointed {DATE} from {OLD} Ifs Industries Inc. to {ORG} IFS Coatings, Inc. (tasks/ifs-coatings-parent-2026-11-06): '
        "the operator's own ISO 9001 certificate lists 3430 Cypert Way as an IFS Coatings, Inc. manufacturing and warehousing site; "
        "ITA 73266 shares its EIN with IFS Coatings' Gainesville filing (ITA 73137) and not with Ifs Industries; "
        "Ifs Industries' own contact page lists no Oklahoma plant. The 2026-11-04 placement was a flagged judgment call, not evidence.")


def read(p):
    with open(p, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def write(p, rows):
    with open(p, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n'); w.writeheader(); w.writerows(rows)


def witnessed(w, ita):
    """Raw check: own_site quote in order in the stored page text; government rows against the ITA extract."""
    if w['witness'].startswith('ITA:'):
        r = ita[w['witness'][4:]]
        if w['claim_type'] == 'code':
            return r['naics_code'] == w['quote'] and r['industry_description'] == 'Powder coatings manufacturing'
        return (r['ein'] == ita['73137']['ein'] == w['quote'] and r['establishment_name'].startswith('IFS Coatings, Inc.')
                and ita['962374']['ein'] != w['quote'] and ita['962374']['company_name'].startswith('IFS Industries'))
    src = HERE/w['witness'] if (HERE/w['witness']).exists() else PERSIST/w['witness']
    return found(src.read_text(), w['quote'])


def org_row(header):
    v = dict(org_id=ORG, legal_name='IFS Coatings, Inc.', entity_type='corporation_private', ring_primary='2',
             hq_city='Gainesville', hq_state='TX', hq_country='US', hq_in_scope='national_us',
             naics_primary='325510', naics_primary_source_type='government_filing',
             naics_primary_source_name='OSHA ITA Form 300A CY2025 establishment 73137', naics_confidence='medium',
             processes='coating_formulation', materials='coatings', website='https://www.ifscoatings.com/',
             description_1line='Powder coating manufacturer (thermosetting and thermoplastic powders) with plants in Gainesville, TX and Ardmore, OK (NAICS 325510).',
             pic_relevance='potential_member', status='active',
             sources=f'{CERT}; https://www.ifscoatings.com/about-us/; OSHA ITA Form 300A CY2025 establishments 73137 (Gainesville) and 73266 (Ardmore)',
             verification_tier='C', last_verified=DATE, created_by=BY, monitor_watch='false',
             notes=(f'Created {DATE} (tasks/ifs-coatings-parent-2026-11-06) as the operator of {SITE} Ardmore, OK, which main had placed under {OLD} '
                    'Ifs Industries Inc. (Reading PA adhesives). Own ISO 9001 certificate names IFS Coatings, Inc. with central functions at 3601 North I-35, '
                    'Gainesville, TX and a second site at 3430 Cypert Way, Ardmore. Distinct legal entity from Ifs Industries (different EINs in OSHA ITA). '
                    'No primary source found for common ownership, so parent_org_id is empty. Tier C at birth (AGENTS §3 step 5). '
                    'Gainesville plant held as lead LF-TX-00505 (tasks/corroborated-tx-2-2026-11-06); its site create is a follow-up.'))
    assert set(v) <= set(header)
    return {k: v.get(k, '') for k in header}


def main():
    ws = read(HERE/'witnesses.csv')
    ita = {r['establishment_id']: r for r in read(ROOT/'tasks/osha-ita-2026-11-01/establishments.csv')}
    ids = [w['evidence_id'] for w in ws]
    assert len(ids) == len(set(ids)) and all(332000 <= int(i[4:]) <= 332099 for i in ids)
    bad = [w['evidence_id'] for w in ws if not witnessed(w, ita)]
    assert not bad, ('raw witness failed', bad)
    data = ROOT/'data'
    held = {e['evidence_id']: (f.name, e) for f in sorted(data.glob('evidence_*.csv')) for e in read(f)}
    held.update({e['evidence_id']: ('archive_links.csv', e) for e in read(data/'archive_links.csv')})
    orgs_all = {r['org_id'] for f in data.glob('organizations_*.csv') for r in read(f)} | {r['org_id'] for r in read(data/'ecosystem.csv')}
    # Site re-point (only org_id, sources, notes, last_verified).
    sp = data/'sites_OK.csv'; sites = read(sp); s = next(r for r in sites if r['site_id'] == SITE)
    assert s['org_id'] in (OLD, ORG) and s['street_address'] == '3430 Cypert Way' and s['city'] == 'Ardmore'
    s['org_id'] = ORG
    if CERT not in s['sources']: s['sources'] += f'; IFS Coatings, Inc. ISO 9001:2015 certificate 112094.00 (DEKRA), {CERT}'
    if NOTE.strip() not in s['notes']: s['notes'] += NOTE
    s['last_verified'] = DATE
    # Organization create.
    op = data/'organizations_TX.csv'; org = org_row(list(read(op)[0]))
    existing = {r['org_id']: r for r in read(op)}
    assert ORG in existing or ORG not in orgs_all, 'ORG id collision in another shard'
    assert existing.get(ORG, org) == org, 'ORG-013500 differs from the packet'
    # Evidence rows.
    shard = {'organizations': data/'evidence_organizations_TX.csv', 'sites': data/'evidence_sites_OK.csv'}
    new = {k: [] for k in shard}
    for w in ws:
        note = ('Raw words in order: ' + w['quote']) if w['source_class'] == 'own_site' else f"ITA extract field value {w['quote']} checked against tasks/osha-ita-2026-11-01/establishments.csv"
        e = dict(evidence_id=w['evidence_id'], record_table=w['record_table'], record_id=w['record_id'], claim_type=w['claim_type'],
                 claim_detail=w['claim_detail'], source_class=w['source_class'], source_ref=w['source_ref'], observed_date=DATE,
                 tier_effect='supports_C', created_by=BY, notes=note)
        if e['evidence_id'] in held:
            assert held[e['evidence_id']] == (shard[w['record_table']].name, e), ('evidence ID collision', e['evidence_id'])
        else:
            new[w['record_table']].append(e)
    write(sp, sites)
    if ORG not in existing: append_sorted(op, [org], 'org_id')
    for k, rows in new.items():
        if rows: append_sorted(shard[k], rows, 'evidence_id')
    print(f'{ORG} {"created" if ORG not in existing else "present"}; {SITE} -> {ORG}; evidence appended {sum(map(len, new.values()))} of {len(ws)}')


if __name__ == '__main__':
    main()
