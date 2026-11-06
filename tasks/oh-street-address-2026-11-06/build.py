#!/usr/bin/env python3
"""L2 FRS street recovery. Fetch -> inspect verdicts -> apply; never changes tiers/counties."""
import argparse
import csv
import json
import re
import subprocess
import sys
import time
from pathlib import Path

TASK = Path(__file__).resolve().parent
ROOT = TASK.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from shard_io import append_sorted
FRSU = 'https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id='
DATE = '2026-11-06'

def read(p):
    with open(p, newline='') as f:
        return list(csv.DictReader(f))

def write(p, rows, fields=None):
    with open(p, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields or list(rows[0]), lineterminator='\n')
        w.writeheader(); w.writerows(rows)

def norm(v):
    return ' '.join(re.findall(r'[A-Z0-9]+', v.upper()))

def streetkey(v):
    aliases = {'STREET':'ST','ROAD':'RD','DRIVE':'DR','AVENUE':'AVE','COURT':'CT','PARKWAY':'PKWY',
               'EAST':'E','WEST':'W','NORTH':'N','SOUTH':'S','HIGHWAY':'HWY','BOULEVARD':'BLVD'}
    return ' '.join(aliases.get(t,t) for t in norm(v).split())

def fetch(rid, folder='raw'):
    p = TASK / folder / (rid + '.json'); p.parent.mkdir(exist_ok=True)
    r = subprocess.run(['curl','--fail','-L','--max-time','45','-A','Mozilla/5.0',FRSU+rid+'&output=JSON'], capture_output=True)
    if r.returncode:
        raise ValueError('FRS fetch failed: '+str(r.returncode))
    data = json.loads(r.stdout)
    p.write_bytes(r.stdout)
    return data

def facility(data, rid):
    records = data['Results']['FRSFacility']
    assert len(records) == 1 and records[0]['RegistryId'] == rid, 'missing/ambiguous registry identifier'
    return records[0]

def conflict(s, f):
    if norm(f.get('CityName') or '') != norm(s['city']): return 'city conflict'
    if not re.fullmatch(r'\d{5}(?:-\d{4})?', s['zip']) or f['ZipCode'][:5] != s['zip'][:5]: return 'ZIP conflict/missing'
    if f['StateAbbr'] != 'OH': return 'state conflict'
    if norm(f.get('CountyName') or '') != norm(s['county'].removesuffix(' County')): return 'county conflict/missing'
    street = f.get('LocationAddress') or ''
    if not re.match(r'^\d+\s+\S+',street) or re.search(r'\bP\.?\s*O\.?\s*BOX\b|POST OFFICE|RURAL ROUTE',street,re.I): return 'non-physical/ambiguous street'
    return ''

def known():
    cases = [('110000745766','160 Parker Ct','Chardon','44024'),
             ('110000391415','350 N Buckeye St','Bellevue','44811'),
             ('110000383941','555 W Linfoot St','Wauseon','43567')]
    out=[]
    for rid,street,city,zip_ in cases:
        f=facility(fetch(rid,'known_raw'),rid)
        assert streetkey(f['LocationAddress']) == streetkey(street), f
        assert norm(f['CityName']) == norm(city) and f['ZipCode'][:5]==zip_, f
        s=dict(city=city,zip=zip_,county=f['CountyName'])
        assert not conflict(s,f)
        for field,value in [('city','WRONG CITY'),('zip','00000'),('county','WRONG COUNTY')]:
            assert conflict(dict(s,**{field:value}),f), field
        assert conflict(s,dict(f,LocationAddress='PO BOX 99'))
        out.append(dict(registry_id=rid,expected_street=street,actual_street=f['LocationAddress'],result='PASS'))
    write(TASK/'known_answers.csv',out)
    print('Known answers: 3/3; injected city/ZIP/county/PO-box defects rejected')

def run(do_fetch=False, apply=False):
    sites=read(ROOT/'data/sites_OH.csv'); byid={s['site_id']:s for s in sites}
    # Frozen blank cohort survives a second application and main rebases.
    baseline=TASK/'baseline.csv'
    if not baseline.exists(): write(baseline,[s for s in sites if s['operating_status']=='active'])
    initial=read(baseline); blanks={s['site_id']:s for s in initial if not s['street_address']}
    links=[r for r in read(TASK/'registry_links_input.csv') if r['registry']=='FRS' and r['site_id'] in blanks]
    ids=sorted({r['registry_id'] for r in links})
    if do_fetch:
        def one(rid):
            try: facility(fetch(rid),rid); return rid,'OK'
            except Exception as e: return rid,str(e)
        results=[]
        for rid in ids:
            if (TASK/'raw'/f'{rid}.json').exists():
                results.append((rid,'OK')); continue
            result=one(rid); results.append(result)
            print(rid,result[1],flush=True)
            time.sleep(11)
        write(TASK/'fetch_log.csv',[dict(registry_id=k,result=v) for k,v in results])
    existing=read(ROOT/'data/evidence_sites_OH.csv')
    own={r['site_id']:r for r in read(TASK/'own_site_checks.csv') if r['result']=='VERIFIED'}
    ita={r['establishment_id']:r for r in read(ROOT/'tasks/osha-ita-2026-11-01/establishments.csv')}
    matches=[r for r in read(ROOT/'tasks/osha-ita-2026-11-01/site_matches.csv') if r['site_id'] in blanks and r['match_strength'] in ('exact','strong')]
    candidates={sid:[] for sid in blanks}; reasons={sid:[] for sid in blanks}
    for r in links:
        sid=r['site_id'];rid=r['registry_id'];s=blanks[sid]
        path=TASK/'raw'/f'{rid}.json'
        if not path.exists(): continue
        try:
            f=facility(json.loads(path.read_text()),rid)
            why=conflict(s,f)
            if why: reasons[sid].append('FRS '+rid+': '+why)
            if r['org_id'] != s['org_id']: reasons[sid].append('FRS link operator conflict')
            candidates[sid].append(dict(street=f['LocationAddress'],source_class='registry',ref=FRSU+rid+'&output=JSON',date=DATE,
                notes=f"EPA FRS registry {rid}; fetched {DATE}; raw copy tasks/oh-street-address-2026-11-06/raw/{rid}.json",rid=rid))
        except Exception as e: reasons[sid].append('FRS malformed: '+str(e))
    for m in matches:
        s=blanks[m['site_id']]; r=ita[m['establishment_id']]; sid=s['site_id']
        assert m['street']==r['street'] and m['city']==r['city'] and m['zip5']==r['zip5']
        if norm(r['city']) != norm(s['city']) or not s['zip'] or s['zip'][:5] != r['zip5']:
            reasons[sid].append('ITA city/ZIP conflict/missing'); continue
        if m['org_id']!=s['org_id']: reasons[sid].append('ITA operator conflict');continue
        if not re.match(r'^\d+\s+\S+',r['street']) or re.search(r'\bP\.?\s*O\.?\s*BOX\b',r['street'],re.I):
            reasons[sid].append('ITA non-physical street');continue
        candidates[sid].append(dict(street=r['street'],source_class='government_filing',
            ref='https://www.osha.gov/sites/default/largefiles/ITA_300A_Summary_Data_2025_through_08-31-2026.csv',date='2026-11-01',
            notes=f"OSHA ITA CY2025 establishment_ID {r['establishment_id']}; date_submitted {r['date_submitted']}; owner-supplied filtered extract SHA-256 69c0d987d453471293b092640b392eaef44b21cb55446a1c9b69ad8b54bf703a; inherited packet exception authorized by controller 2026-11-06",rid=''))
    verdicts=[]; fills=[]; evidence=[]
    for allocation,(sid,s) in enumerate(sorted(blanks.items())):
        cs=candidates[sid]; why=reasons[sid]
        keys={streetkey(c['street']) for c in cs}
        if len(keys)>1: why.append('sources disagree on street')
        street=cs[0]['street'] if cs else ''
        witness=own.get(sid)
        if witness and streetkey(street) not in streetkey(witness['quote']): witness=None
        if s['verification_tier'] in ('A','B') and not witness: why.append('current A/B tier requires own-site address witness (controller ruling)')
        if not cs: why.append('need site-keyed physical street witness with agreeing city and ZIP; none available in this pass')
        leads=re.findall(r'(?i)(?:Address[^:]{0,120}:|at)\s*(\d+\s+[^,;()]+),\s*'+re.escape(s['city']),s['notes'])
        m=re.search(r'(?i)\bstreet(?:\s*\([^)]*\))?:\s*(.+)',s['notes'])
        if m:
            noted=re.split(r'\.\s+(?=PASS|BAND|CERT|Ring|INTEGRATION|Parcel|Re-pointed|NAICS|Source|\[)',m[1])[0].rstrip('. ')
            leads.append(noted)
        if street and any(streetkey(x)!=streetkey(street) for x in leads): why.append('notes address disagrees; adjudication required')
        v=dict(site_id=sid,verdict='STILL_UNCERTAIN' if why else 'VERIFIED',street_address=street,
               registry_ids=';'.join(sorted({c['rid'] for c in cs if c['rid']})),reason='; '.join(sorted(set(why))),evidence_id='')
        if not why:
            chosen=cs[0] # FRS precedes inherited ITA
            if witness:
                chosen=dict(street=street,source_class='own_site',ref=witness['url'],date=DATE,notes='Raw checked '+DATE+'; SHA-256 '+witness['sha256']+'; quote: '+witness['quote'])
            eid=f'EVD-{150000+allocation:06d}';v['evidence_id']=eid;fills.append(v)
            effect='supports_C' if chosen['source_class']=='registry' else 'supports_A'
            evidence.append(dict(evidence_id=eid,record_table='sites',record_id=sid,claim_type='address',
                claim_detail=f"street_address {street}, {s['city']}, OH {s['zip']}",source_class=chosen['source_class'],source_ref=chosen['ref'],
                observed_date=chosen['date'],tier_effect=effect,created_by='atlas-L2-oh-address',notes=chosen['notes']+'. County, county_source and record tier unchanged.'))
        verdicts.append(v)
    assert len(verdicts)==len({v['site_id'] for v in verdicts})==len(blanks)
    write(TASK/'verdicts.csv',verdicts);write(TASK/'holds.csv',[v for v in verdicts if v['verdict']!='VERIFIED'],list(verdicts[0]))
    write(TASK/'evidence.csv',evidence)
    if apply:
        paths=[ROOT/'data/sites_OH.csv',ROOT/'data/evidence_sites_OH.csv']
        (TASK/'backups').mkdir(exist_ok=True)
        for p in paths:
            b=TASK/'backups'/p.name
            if not b.exists():b.write_bytes(p.read_bytes())
        evbyid={e['evidence_id']:e for e in existing}; additions=[]
        for v,ev in zip(fills,evidence):
            s=byid[v['site_id']];old=blanks[v['site_id']]
            for k in ('city','zip','county','org_id','verification_tier','county_source'):assert s[k]==old[k],(v['site_id'],k)
            assert s['operating_status']=='active' and s['street_address'] in ('',v['street_address'])
            s['street_address']=v['street_address']
            if ev['source_ref'] not in s['sources']:s['sources']+='; '+ev['source_ref']
            if ev['evidence_id'] in evbyid:assert evbyid[ev['evidence_id']]==ev,'evidence collision'
            else:additions.append(ev)
        if additions:append_sorted(paths[1],additions,'evidence_id')
        write(paths[0],sites)
    summary=dict(active_sites=len(initial),before_filled=sum(bool(s['street_address']) for s in initial),fills=len(fills),
                 after_filled=sum(bool(s['street_address']) for s in initial)+len(fills),blank_sites=len(blanks),holds=len(blanks)-len(fills),
                 frs_sites=len({r['site_id'] for r in links}),ita_sites=len({r['site_id'] for r in matches}))
    (TASK/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary)

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--known',action='store_true'); ap.add_argument('--fetch',action='store_true'); ap.add_argument('--apply',action='store_true'); args=ap.parse_args()
    if args.known: known()
    else: run(args.fetch,args.apply)
