Adversarial completion review of Ohio street recovery, L2. End APPROVE / REFUTE / INSUFFICIENT-EVIDENCE, specific demonstrated defects only. Do not execute mutations. Technical verdict on supplied evidence; final audit and publication are operational gates maintained by lead.
Scope: active Ohio sites blank in baseline main bd57a08. 143 fills, no creates/deletes/status/tier/county/county_source changes; append 143 address evidence rows. Record tiers C102 U34 A6 B1. Evidence witnesses: inherited ITA government124, registry12, raw own_site7. 1740 blank candidates partition143 verified/1597 held, total1883 active site rows, street143->286 (7.59->15.19%). Three known FRS literal addresses passed plus injected city/ZIP/county/PO-box rejected. check.py passes 143 fills, only street/sources change, second build byte identical, conflicting new street refused. validate.py passes0errors. Unit suite221 tests OK, 1 existing skip. No scripts/ touched.
Governing controller rulings: inherited ITA government extract explicitly admissible without fresh bulk download (direct403/Jina401); correct CY2025 source URL and observed2026-11-01 with original filing date/establishment ID/extract SHA in notes. Initial suggested CY2024 URL was corrected before any fills. A/B sites require raw own-site address witness or HOLD. FRS-only address capped supports_C. No tier demotions. County_source unchanged because it describes county adjudication, not street presence.
Audit: original discovery sample found SITE-000809 County Hwy96 vs CO RD96; it is now held. Parser expanded to enforce conflicts against legacy Street(per Grok) notes and suite mismatches. The final deterministic Random(20261106)30-row sample completed: 0 address errors; ITA transcription0/22; independently corroborated14/30; not independently checkable16/30 (no exact/strong site-keyed FRS alternative). ITA transcription checked against banked extract; fresh FRS/own-site corroboration separately measured; uncheckable rows explicitly reported. Controller approved these separate rates rather than pretending fresh ITA bulk download. Review this audit method as well as code. Missing independent corroboration is reported, never called a successful raw fetch.
FRS first attempted301 IDs (6req/min throttling);22 responses retained after conservative retries; unavailable sources do not imply negative evidence. Brief source priority follows existing usable evidence (none quotes a street), fresh FRS, inherited exact/strong ITA, then own website. FRS+ITA or notes disagreements held. Fresh FRS keyed IDs come only from restore branch input; no registry links edited. Full unattainable Ontario/foreign no scope. No outside personal/licensed/private content.
Reproduction: python3 tasks/oh-street-address-2026-11-06/check.py; python3 tasks/oh-street-address-2026-11-06/build.py --apply; python3 scripts/validate.py; python3 tasks/oh-street-address-2026-11-06/audit.py (network and 12sec spacing). Source fetch logs and raw JSON retained in lane folder. Backups local only.
What could be wrong: local inherited packet transcription drift; notes address parser misses a conflict; normalized addresses falsely agree; website footer witnesses different location; registry supports wrong county/operator; idempotence or rebase overwrites; quote raw-check fails. Judge against exact supplied code and rows. Tools are unnecessary; all code and changed-row inputs follow.


FILE build.py
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


FILE own_sites.py
"""Raw-check operator home/contact pages for FRS candidate streets; bounded 3 URLs per operator."""
import concurrent.futures
import csv
import hashlib
import re
import subprocess
from html.parser import HTMLParser
from urllib.parse import urljoin,urlparse
from build import TASK,ROOT,read,write,norm,streetkey

class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[]; self.links=[]; self.skip=0
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style'): self.skip+=1
        if tag=='a':
            self.links.extend(v for k,v in attrs if k=='href' and re.search('contact|location',v,re.I))
    def handle_endtag(self,tag):
        if tag in ('script','style'): self.skip=max(0,self.skip-1)
    def handle_data(self,s):
        if not self.skip and s.strip(): self.parts.append(s.strip())

def page(url):
    r=subprocess.run(['curl','--fail','-L','--max-time','20','-A','Mozilla/5.0',url],capture_output=True)
    if r.returncode: raise ValueError('HTTP/transport failure '+str(r.returncode))
    p=Page();p.feed(r.stdout.decode(errors='replace'))
    return p,hashlib.sha256(r.stdout).hexdigest()

def main():
    sites={s['site_id']:s for s in read(TASK/'baseline.csv') if not s['street_address']}
    orgs={r['org_id']:r for p in (ROOT/'data').glob('organizations_*.csv') for r in read(p)}
    leads=[r for r in read(ROOT/'tasks/echo-frs-spine-2026-11-01/site_matches.csv') if r['site_id'] in sites and sites[r['site_id']]['verification_tier'] in ('A','B') and r['match_strength'] in ('exact','strong')]
    groups={}
    for r in leads: groups.setdefault(sites[r['site_id']]['org_id'],[]).append(r)
    def work(item):
        oid,rows=item; base=orgs[oid]['website']; todo=[base] if base else []; checked=[]; found={}
        for _ in range(3):
            if not todo: break
            url=todo.pop(0)
            if url in checked: continue
            checked.append(url)
            try:
                p,sha=page(url); text=' '.join(p.parts); key=streetkey(text)
                for r in rows:
                    addr=streetkey(r['street']); pos=key.find(addr)
                    if pos<0: continue
                    window=key[max(0,pos-100):pos+len(addr)+200]
                    if norm(r['city']) in window and r['zip'][:5] in window:
                        # Keep address-only text, never whole pages containing personal contacts.
                        house=re.escape(r['street'].split()[0]);zip_=re.escape(r['zip'][:5])
                        spans=re.findall(r'\b'+house+r'\b.{0,200}?\b'+zip_+r'(?:-\d{4})?',text)
                        quote=next((q for q in spans if addr in streetkey(q) and norm(r['city']) in streetkey(q)),'')
                        if quote and not re.search(r'@|\b\d{3}[-.]\d{3}[-.]\d{4}\b',quote):
                            found[r['site_id']]=dict(site_id=r['site_id'],url=url,quote=quote,sha256=sha,checked_urls=';'.join(checked),result='VERIFIED')
                for link in p.links:
                    u=urljoin(url,link)
                    if urlparse(u).hostname==urlparse(base).hostname and u not in checked and u not in todo: todo.append(u)
            except Exception: pass
            if len(found)==len({r['site_id'] for r in rows}): break
        return [found.get(r['site_id'],dict(site_id=r['site_id'],url=base,quote='',sha256='',checked_urls=';'.join(checked),result='STILL_UNCERTAIN')) for r in rows]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        out=[r for group in pool.map(work,groups.items()) for r in group]
    write(TASK/'own_site_checks.csv',out)
    print('Own-site rows',len(out),'verified',sum(r['result']=='VERIFIED' for r in out))

if __name__=='__main__':main()


FILE audit.py
"""Seeded 30-fill independent audit; inherited-ITA transcription and fresh corroboration reported separately."""
import json,random,time
from build import TASK,ROOT,read,write,facility,fetch,conflict,streetkey,norm
from own_sites import page
fills=[r for r in read(TASK/'verdicts.csv') if r['verdict']=='VERIFIED']
sample=random.Random(20261106).sample(sorted(fills,key=lambda r:r['site_id']),30)
sites={r['site_id']:r for r in read(TASK/'baseline.csv')}
ev={r['record_id']:r for r in read(TASK/'evidence.csv')}
ita=read(ROOT/'tasks/osha-ita-2026-11-01/site_matches.csv')
frs={}
for r in read(TASK/'registry_links_input.csv'):
    if r['registry']=='FRS':frs.setdefault(r['site_id'],r['registry_id'])
for r in read(ROOT/'tasks/echo-frs-spine-2026-11-01/site_matches.csv'):
    if r['match_strength'] in ('strong','exact'):frs.setdefault(r['site_id'],r['registry_id'])
out=[]
for v in sample:
    s=sites[v['site_id']];e=ev[v['site_id']];error='';checked=False;detail='';url=''
    transcription='not_ITA'
    if e['source_class']=='government_filing':
        rows=[r for r in ita if r['site_id']==v['site_id'] and r['match_strength'] in ('exact','strong')]
        transcription='PASS' if any(streetkey(r['street'])==streetkey(v['street_address']) and norm(r['city'])==norm(s['city']) and r['zip5']==s['zip'][:5] for r in rows) else 'FAIL'
        if transcription=='FAIL':error='ITA transcription mismatch'
    try:
        if e['source_class']=='own_site':
            url=e['source_ref'];p,sha=page(url);quote=e['notes'].split('; quote: ')[1].removesuffix('. County, county_source and record tier unchanged.')
            assert norm(quote) in norm(' '.join(p.parts)),'own-site quote absent on refetch'
            checked=True;detail='fresh own page, exact quote checked; SHA-256 '+sha
        else:
            rid=frs.get(v['site_id'])
            if not rid:raise ValueError('no exact/strong site-keyed FRS record available')
            url='https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id='+rid+'&output=JSON'
            f=facility(fetch(rid,'audit_raw'),rid)
            mismatch=conflict(s,f)
            if mismatch:raise ValueError('FRS not corroborating: '+mismatch)
            if streetkey(f['LocationAddress'])!=streetkey(v['street_address']):
                error='independent FRS street disagrees: '+f['LocationAddress']
            else:checked=True;detail='fresh FRS corroboration'
            time.sleep(12)
    except Exception as ex:detail=str(ex)
    out.append(dict(site_id=v['site_id'],street_address=v['street_address'],source_class=e['source_class'],transcription=transcription,
                    independently_corroborated='yes' if checked else 'no',fresh_source_url=url,detail=detail,error=error))
    write(TASK/'audit.csv',out);print(v['site_id'],transcription,checked,error,detail,flush=True)
summary=dict(sampled=len(out),ita_sampled=sum(r['transcription']!='not_ITA' for r in out),transcription_errors=sum(r['transcription']=='FAIL' for r in out),
             independently_corroborated=sum(r['independently_corroborated']=='yes' for r in out),not_independently_checkable=sum(r['independently_corroborated']=='no' and not r['error'] for r in out),address_errors=sum(bool(r['error']) for r in out))
(TASK/'audit_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary)
assert summary['address_errors']==0 and len(out)==30


FILE check.py
"""Named L2 mutation-boundary and idempotence check; no canonical writes."""
import contextlib
import hashlib
import io
import shutil
import tempfile
from pathlib import Path
import build

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    root=build.ROOT
    with tempfile.TemporaryDirectory() as tmp:
        build.ROOT=Path(tmp);(build.ROOT/'data').mkdir()
        for name in ('sites_OH.csv','evidence_sites_OH.csv'):
            shutil.copyfile(root/'data'/name,build.ROOT/'data'/name)
        for name in ('establishments.csv','site_matches.csv'):
            p=build.ROOT/'tasks/osha-ita-2026-11-01'/name;p.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(root/'tasks/osha-ita-2026-11-01'/name,p)
        frozen={r['site_id']:r for r in build.read(build.TASK/'baseline.csv')}
        base=build.read(build.ROOT/'data/sites_OH.csv')
        base=[frozen.get(r['site_id'],r) for r in base]
        build.write(build.ROOT/'data/sites_OH.csv',base)
        ev=build.read(build.ROOT/'data/evidence_sites_OH.csv')
        build.write(build.ROOT/'data/evidence_sites_OH.csv',[r for r in ev if r['created_by']!='atlas-L2-oh-address'])
        before=build.read(build.ROOT/'data/sites_OH.csv')
        with contextlib.redirect_stdout(io.StringIO()): build.run(apply=True)
        after=build.read(build.ROOT/'data/sites_OH.csv')
        changed=0
        assert len(before)==len(after)
        for a,b in zip(before,after):
            fields={k for k in a if a[k]!=b[k]}
            assert fields <= {'street_address','sources'},(a['site_id'],fields)
            if fields:
                changed+=1
                assert not a['street_address'] and b['street_address'] and a['operating_status']=='active'
        paths=list((build.ROOT/'data').glob('*.csv'));hashes=[digest(p) for p in paths]
        with contextlib.redirect_stdout(io.StringIO()):build.run(apply=True)
        assert hashes==[digest(p) for p in paths],'not idempotent'
        # Inject a new street conflict: reapplication must refuse instead of overwriting.
        target=next(r for a,r in zip(before,after) if not a['street_address'] and r['street_address'])
        target['street_address']='999 WRONG ROAD';build.write(build.ROOT/'data/sites_OH.csv',after)
        try:
            with contextlib.redirect_stdout(io.StringIO()):build.run(apply=True)
        except AssertionError:pass
        else:raise AssertionError('injected street conflict was silently overwritten')
        print(f'PASS: {changed} fills; only street/sources change; second build byte-identical; injected street conflict refused')
    build.ROOT=root

if __name__=='__main__':main()


Row URL alias ITA2025=full CY2025 URL from build.py; FRS:<ID>&output=JSON=full FRSU prefix from build.py plus ID.
CHANGED ROWS tab-separated: site_id | site_name | city ZIP county tier | new street | witness class | date | source URL | legacy notes street

SITE-000228 | Advanced Polymer Coatings — Avon | Avon 44011 Lorain U | 951 Jaycox Rd. | government_filing | 2026-11-01 | ITA2025 | 951 Jaycox Rd. PASS 8 (2026-10-29) mechanical sweep lane 2: NAICS 325510 coded from capability 
SITE-000239 | Allpass Corporation — Madison | Madison 44057 Lake C | 222 N. Lake St. | government_filing | 2026-11-01 | ITA2025 | 222 North Lake Street. BAND-SOURCE: employee_band_site=10-49 from OSHA ITA Form 300A CY2025, fi
SITE-000240 | Alttran — Hudson | Hudson 44236 Summit C | 5285 HUDSON DR. | government_filing | 2026-11-01 | ITA2025 | 5285 Hudson Drive. CERT-SITE (own site, observed 2026-11-01): iso_9001. BAND-SOURCE: employee_b
SITE-000258 | Barentz — Avon | Avon 44011 Lorain U | 1390 Jaycox Road | government_filing | 2026-11-01 | ITA2025 | 1390 Jaycox Road. Ring 3 subtype: distribution. PASS 8 (2026-10-29) mechanical sweep lane 2: NA
SITE-000262 | Biothane Coated Webbing — North Ridgeville | North Ridgeville 44039 Lorain C | 34655 Mills Road | government_filing | 2026-11-01 | ITA2025 | 34655 MILLS ROAD. BAND-SOURCE: employee_band_site=10-49 from OSHA ITA Form 300A CY2025, filed 2
SITE-000278 | Carbon Polymers Company — Lodi | Lodi 44254 Medina C | 104 Lee Street | government_filing | 2026-11-01 | ITA2025 | 104 Lee Street. BAND-SOURCE: employee_band_site=10-49 from OSHA ITA Form 300A CY2025, filed 202
SITE-000287 | Chardon Rubber Company — Chardon | Chardon 44024 Geauga B | 373 Washington Street | own_site | 2026-11-06 | https://chardoncp.com/ | 373 Washington St.. Re-pointed pass 4: successor occupant Chardon Custom Polymers (packets 03 +
Raw checked 2026-11-06; SHA-256 69f86117482e93b4eeeff1b3366760a1386a157d29b17e92fba30148f9fa149b; quote: 373 Washington St. Chardon OH 44024. County, county_source and record tier unchanged.
SITE-000289 | Chem Tech — Middlefield | Middlefield 44062 Geauga U | 14875 Bonner Dr. | government_filing | 2026-11-01 | ITA2025 | 14875 Bonner Drive. INTEGRATION PASS 3 2026-10-28 (spatial dedupe S03): duplicate site row SITE
SITE-000298 | Colonial Machine — Kent | Kent 44240 Portage C | 1041 Mogadore Road | government_filing | 2026-11-01 | ITA2025 | 1041 Mogadore Road. Parcel corroboration 2026-10-29 (pass 6 §3.3, pilot): Portage fabric parcel
SITE-000319 | Degussa Initiators — Elyria | Elyria 44035 Lorain U | 555 Garden Street | government_filing | 2026-11-01 | ITA2025 | 555 Garden Street. [Dedupe 2026-10-28: site re-pointed ORG-000300 -> ORG-000618 per global dedu
SITE-000329 | Dreco — North Ridgeville | North Ridgeville 44039 Lorain C | 7887 Root Road | government_filing | 2026-11-01 | ITA2025 | 7887 Root Rd. BAND-SOURCE: employee_band_site=10-49 from OSHA ITA Form 300A CY2025, filed 2026-
SITE-000331 | Duo-Corp — North Lima | North Lima 44452 Mahoning C | 280 Miley Road | government_filing | 2026-11-01 | ITA2025 | 280 Miley Road. BAND-SOURCE: employee_band_site=10-49 from OSHA ITA Form 300A CY2025, filed 202
SITE-000335 | Dura-Line — Elyria | Elyria 44035 Lorain A | 860 Garden St. | own_site | 2026-11-06 | https://www.duraline.com/contact/ | 860 Garden St.. INTEGRATION 2026-10-28 (verification wave 2, §18): 860 Garden St is the HDPE co
Raw checked 2026-11-06; SHA-256 cc0b0a049af111a570f0291dfb3a7b224c9a3c1c381d75398d8b7bbfbbec70aa; quote: 860 Garden St., Elyria, OH, 44035. County, county_source and record tier unchanged.
SITE-000338 | Duramax Marine — Hiram | Hiram 44234 Geauga A | 17990 Great Lakes Pkwy | own_site | 2026-11-06 | https://www.duramaxmarine.com/ | 17990 Great Lakes Parkway. INTEGRATION 2026-10-28 (verification wave 2, §17): County Portage ->
Raw checked 2026-11-06; SHA-256 6dc07c9f2622998c9a0144053cb2b243a1449559a5b4256167aca92b6567827f; quote: 17990 Great Lakes Parkway, Hiram, Ohio 44234. County, county_source and record tier unchanged.
SITE-000361 | Flambeau, Inc. — Middlefield | Middlefield 44062 Geauga C | 15981 Valplast Street | government_filing | 2026-11-01 | ITA2025 | 15981 Valplast Street. PASS 8 (2026-10-29) mechanical sweep lane 2: NAICS 326199 coded from cap
SITE-000363 | Flavorseal — Avon | Avon 44011 Lorain C | 35179 Avon Commerce Parkway | government_filing | 2026-11-01 | ITA2025 | 35179 Avon Commerce Parkway. BAND-SOURCE: employee_band_site=50-99 from OSHA ITA Form 300A CY20
SITE-000371 | Freeman Manufacturing & Supply Company — Avon | Avon 44011 Lorain A | 1101 Moore Road | own_site | 2026-11-06 | https://www.freemansupply.com/ | 1101 Moore Road. INTEGRATION 2026-10-28 (verification wave 2, §16): Ring 2 -> 3 (distribution) 
Raw checked 2026-11-06; SHA-256 b3f770220d41b7e47dbe7ed1e92f58c193a1a5d6f14990d31795a5501fab6dec; quote: 1101 Moore Road, Avon, Ohio 44011. County, county_source and record tier unchanged.
SITE-000411 | Iten Defense — Ashtabula | Ashtabula 44004 Ashtabula U | 3500 N Ridge Rd W | government_filing | 2026-11-01 | ITA2025 | 3500 North Ridge Road West.
SITE-000420 | JACO Manufacturing Co. | Berea 44017 Cuyahoga C | 468 Geiger St | government_filing | 2026-11-01 | ITA2025 | 468 Geiger Street. INTEGRATION PASS 3 2026-10-28 (spatial dedupe S11): duplicate site row SITE-
SITE-000464 | McCann Plastics — North Canton | North Canton 44720 Summit C | 5600 Mayfair Road | government_filing | 2026-11-01 | ITA2025 | 5600 Mayfair Road. INTEGRATION PASS 3 2026-10-28 (county adjudication): county corrected Stark 
SITE-000470 | Mickey Thompson Tire and Wheels — Stow | Stow 44224 Summit U | 4651 Prosper Drive | government_filing | 2026-11-01 | ITA2025 | 4651 Prosper Drive.
SITE-000490 | Neff-Perkins Company — Middlefield | Middlefield 44062 Geauga C | 16080 Industrial PKWY | government_filing | 2026-11-01 | ITA2025 | 16080 Industrial Pkwy. BAND-SOURCE: employee_band_site=50-99 from OSHA ITA Form 300A CY2025, fi
SITE-000505 | Oldcastle Infrastructure (IPG - Middlefield) | Middlefield 44062 Geauga C | 16125 Industrial PKWY | government_filing | 2026-11-01 | ITA2025 | 16125 Industrial Parkway. BAND-SOURCE: employee_band_site=50-99 from OSHA ITA Form 300A CY2025,
SITE-000523 | Pacific Management Holdings, LLC d/b/a Pharmacy-Lite Packaging | Elyria 44035 Lorain C | 250 Warden Ave | government_filing | 2026-11-01 | ITA2025 | 250 Warden Ave.. BAND-SOURCE: employee_band_site=50-99 from OSHA ITA Form 300A CY2025, filed 20
SITE-000531 | Plastics R Unique — Wadsworth | Wadsworth 44281 Medina C | 330 Grandview Ave. | government_filing | 2026-11-01 | ITA2025 | 330 Grandview Ave. BAND-SOURCE: employee_band_site=10-49 from OSHA ITA Form 300A CY2025, filed 
SITE-000558 | Premix-Hadlock Composites - Geneva | Geneva 44041 Ashtabula C | 110 N Eagle St | government_filing | 2026-11-01 | ITA2025 | 110 N. Eagle Street. BAND-SOURCE: employee_band_site=50-99 from OSHA ITA Form 300A CY2025, file
SITE-000559 | Pretium Packaging | Cleveland 44135 Cuyahoga C | 14801 Emery Avenue | government_filing | 2026-11-01 | ITA2025 | 14801 Emery Avenue. BAND-SOURCE: employee_band_site=100-249 from OSHA ITA Form 300A CY2025, fil
SITE-000569 | Qnity Cleveland Laird Plant — Cleveland | Cleveland 44102 Cuyahoga C | 4707 Detroit Avenue | government_filing | 2026-11-01 | ITA2025 | 4707 Detroit Ave. BAND-SOURCE: employee_band_site=100-249 from OSHA ITA Form 300A CY2025, filed
SITE-000579 | Refcotec — Orrville | Orrville 44667 Wayne U | 542 Collins Blvd | government_filing | 2026-11-01 | ITA2025 | 542 Collins Boulevard. BAND-SOURCE: employee_band_site=10-49 from OSHA ITA Form 300A CY2025, fi
SITE-000584 | Rhein Chemie — Chardon | Chardon 44024 Geauga C | 145 Parker court | government_filing | 2026-11-01 | ITA2025 | 145 Parker Court. BAND-SOURCE: employee_band_site=10-49 from OSHA ITA Form 300A CY2025, filed 2
SITE-000608 | Shin-Etsu Silicones of America, Inc. — Akron | Akron 44305 Summit A | 1150 Damar Drive | own_site | 2026-11-06 | https://www.shinetsusilicones.com/ | 1150 Damar Drive. INTEGRATION 2026-10-28 (verification wave 2, §3): site_type -> hq_and_plant (
Raw checked 2026-11-06; SHA-256 26eb3d82dcb2b7e5a59ce5658e0e6253a51ccf075fee2fa58288df06267a454a; quote: 1150 Damar Drive Akron, Ohio 44305-1201. County, county_source and record tier unchanged.
SITE-000615 | Soft-lite — Streetsboro | Streetsboro 44241 Portage C | 10250 Philipp Pkwy | government_filing | 2026-11-01 | ITA2025 | 10250 Philipp Parkway. INTEGRATION PASS 3 2026-10-28 (spatial dedupe S16): duplicate site row S
SITE-000621 | Spencer Industries Incorporated — Elyria | Elyria 44035 Lorain C | 708 Lowell St | government_filing | 2026-11-01 | ITA2025 | 708 Lowell St. BAND-SOURCE: employee_band_site=10-49 from OSHA ITA Form 300A CY2025, filed 2026
SITE-000625 | Spunfab Ltd — Cuyahoga Falls | Cuyahoga Falls 44223 Summit C | 175 Muffin Lane | government_filing | 2026-11-01 | ITA2025 | 175 Muffin Lane. INTEGRATION PASS 3 2026-10-28 (spatial dedupe S17): duplicate site row SITE-00
SITE-000627 | Steere Enterprises — Tallmadge | Tallmadge 44278 Summit A | 285 Commerce St | own_site | 2026-11-06 | https://www.steere.com/ | 285 Commerce St.. CERT-SITE (own site, observed 2026-11-01): iatf_16949; iso_14001; iso_9001.
Raw checked 2026-11-06; SHA-256 21d51a63e9f1a9eec9a5c9359f09f68eed8a8f3ab5c4a106e4eb4fbfa4dc7472; quote: 285 Commerce St., Tallmadge, OH 44278. County, county_source and record tier unchanged.
SITE-000630 | Storopack, Inc. - Cleveland | Cleveland 44111 Cuyahoga C | 3135 Berea Road | government_filing | 2026-11-01 | ITA2025 | 3135 Berea Road. [Dedupe 2026-10-28: site re-pointed ORG-000591 -> ORG-001128 per global dedupe
SITE-000651 | Treemen Industries — Boardman | Boardman 44512 Mahoning C | 691 McClurg Rd. | government_filing | 2026-11-01 | ITA2025 | 691 McClurg Road. CERT-SITE (own site, observed 2026-11-01): iso_9001. BAND-SOURCE: employee_ba
SITE-000655 | Tri-Craft, Inc. — Middleburg Heights | Middleburg Heights 44130 Cuyahoga C | 17941 ENGLEWOOD DR | government_filing | 2026-11-01 | ITA2025 | 17941 Englewood Drive. CERT-SITE (own site, observed 2026-11-01): iso_9001. BAND-SOURCE: employ
SITE-000658 | Tymex Plastics — Cleveland | Cleveland 44105 Cuyahoga C | 5300 Harvard Avenue | government_filing | 2026-11-01 | ITA2025 | 5300 Harvard Ave.. BAND-SOURCE: employee_band_site=50-99 from OSHA ITA Form 300A CY2025, filed 
SITE-000673 | West & Barker — Niles | Niles 44446 Trumbull C | 950 SUMMIT AVENUE | government_filing | 2026-11-01 | ITA2025 | 950 Summit Ave.. BAND-SOURCE: employee_band_site=10-49 from OSHA ITA Form 300A CY2025, filed 20
SITE-000681 | Yokohama TWS North America, Inc. — Akron | Akron 44306 Summit C | 1501 Exeter Road | government_filing | 2026-11-01 | ITA2025 | 1501 Exeter Road. INTEGRATION 2026-10-28 (verification wave 2, §25b): Moved ORG-000638 -> ORG-0
SITE-000691 | A Packaging Group — Defiance | Defiance 43512 Defiance U | 25925 Commerce Dr | government_filing | 2026-11-01 | ITA2025 | 25925 Commerce Drive. Parcel corroboration 2026-10-29 (pass 6 §3.3): OGRIP StateParcelID 39039-
SITE-000698 | Advanced Drainage Systems (New Miami) | Hamilton 45011 Butler U | 2650 Hamilton Eaton Road | government_filing | 2026-11-01 | ITA2025 | 2650 Hamilton-Eaton Road. BAND-SOURCE: employee_band_site=100-249 from OSHA ITA Form 300A CY202
SITE-000701 | Advanced Technology Products — Milford Center | Milford Center 43045 Union C | 190 N. Mill Street | government_filing | 2026-11-01 | ITA2025 | 190 N Mill Street. NAICS adjudication 2026-10-29 pass 5 (Phase 3): 326121 → 326220 (ADOPT_THIRD
SITE-000721 | Americas Styrenics — Marietta | Marietta 45750 Washington C | 17401 State Route 7 | government_filing | 2026-11-01 | ITA2025 | 17401 State Route 7. BAND-SOURCE: employee_band_site=50-99 from OSHA ITA Form 300A CY2025, file
SITE-000738 | Tigerpoly Manufacturing, Inc. - Grove City | Grove City 43123-9271 Franklin U | 6231 Enterprise Pkwy | government_filing | 2026-11-01 | ITA2025 | 6231 Enterprise Parkway. INTEGRATION PASS 3 2026-10-28 (signals packet §3): site renamed from '
SITE-000753 | Baerlocher U.S.A. — Cincinnati | Cincinnati 45232 Hamilton C | 5890 Highland Ridge Drive | government_filing | 2026-11-01 | ITA2025 | 5890 Highland Ridge Drive. Ring 3 subtype: machinery_equipment. BAND-SOURCE: employee_band_site
SITE-000764 | Bob Sumerel Tire Co — Dover | Dover 44622 Tuscarawas C | 204 Deeds Dr. | government_filing | 2026-11-01 | ITA2025 | 204 Deeds Dr.. BAND-SOURCE: employee_band_site=10-49 from OSHA ITA Form 300A CY2025, filed 2026
SITE-000769 | Bryan Plastics Processing, LLC — Bryan | Bryan 43506 Williams U | 721 East Edgerton Street | government_filing | 2026-11-01 | ITA2025 | 721 East Edgerton Street. Ring 3 subtype: distribution. BAND-SOURCE: employee_band_site=10-49 f
SITE-000774 | Building Composites — Moraine | Moraine 45439 Montgomery C | 2299 Arbor Blvd | government_filing | 2026-11-01 | ITA2025 | 2299 Arbor Blvd.. BAND-SOURCE: employee_band_site=50-99 from OSHA ITA Form 300A CY2025, filed 2
SITE-000775 | BWAY Corporation-Monroe — Monroe | Monroe 45050 Butler C | 980 Deneen Ave. | government_filing | 2026-11-01 | ITA2025 | 980 Deneen Avenue. BAND-SOURCE: employee_band_site=10-49 from OSHA ITA Form 300A CY2025, filed 
SITE-000799 | US Coexcell — Maumee | Maumee 43537 Lucas C | 640 Mingo Drive | government_filing | 2026-11-01 | ITA2025 | 640 Mingo Dr.. CERT-SITE (own site, observed 2026-11-01): iso_9001. BAND-SOURCE: employee_band_
SITE-000814 | Cook Composites & Polymers Co. — Sandusky | Sandusky 44870 Erie C | 1321 First Street | government_filing | 2026-11-01 | ITA2025 | 1321 First Street. NAICS adjudication 2026-10-29 pass 5 (Phase 3): KEEP_ATLAS — atlas value 325
SITE-000817 | Cooper Standard (Bowling Green Seal) | Bowling Green 43402 Wood C | 1175 N Main St | government_filing | 2026-11-01 | ITA2025 | 1175 N Main St. NAICS adjudication 2026-10-29 pass 5 (Phase 3): 326220 → 326291 (ADOPT_GOVERNME
SITE-000823 | Corvac Composites — Greenfield | Greenfield 45123 Highland U | 1025 N. Washington St | government_filing | 2026-11-01 | ITA2025 | 1025 N. Washington St.. BAND-SOURCE: employee_band_site=100-249 from OSHA ITA Form 300A CY2025,
SITE-000828 | Crane Plastics — Columbus | Columbus 43207 Franklin C | 2141 FAIRWOOD AVENUE | registry | 2026-11-06 | FRS:110000382318&output=JSON | 2141 Fairwood Ave.. [Dedupe 2026-10-28: site re-pointed ORG-000765 -> ORG-000825 per global ded
SITE-000833 | Creative Liquid Coatings, Inc. Montpelier | Montpelier 43543 Williams C | 1701 Magda Dr. | government_filing | 2026-11-01 | ITA2025 | 1701 Magda Dr. BAND-SOURCE: employee_band_site=250-499 from OSHA ITA Form 300A CY2025, filed 20
SITE-000834 | Creative Plastic Concepts — Sycamore | Sycamore 44882 Wyandot C | 206 South Griffith St. | government_filing | 2026-11-01 | ITA2025 | 206 S Griffith St. BAND-SOURCE: employee_band_site=100-249 from OSHA ITA Form 300A CY2025, file
SITE-000838 | Crown Plastics — Harrison | Harrison 45030 Hamilton C | 116 May Drive | government_filing | 2026-11-01 | ITA2025 | 116 May Drive. INTEGRATION PASS 3 2026-10-28 (spatial dedupe S30): duplicate site row SITE-0008
SITE-000842 | Curbell Plastics, Inc. Cincinnati | Cincinnati 45240 Hamilton U | 11145 Ashburn Road | government_filing | 2026-11-01 | ITA2025 | 11145 Ashburn Road. Ring 3 subtype: distribution. BAND-SOURCE: employee_band_site=10-49 from OS
SITE-000844 | Custom Molded Products, LLC — Wilmington | Wilmington 45177 Clinton C | 92 Grant St. | government_filing | 2026-11-01 | ITA2025 | 92 Grant Street. BAND-SOURCE: employee_band_site=50-99 from OSHA ITA Form 300A CY2025, filed 20
SITE-000849 | DDP SPECIALTY ELECTRONIC MATERIALS US 5, LLC — West Alexandria | West Alexandria 45381 Preble U | 10 s Electric st | government_filing | 2026-11-01 | ITA2025 | 10 S ELECTRIC ST. BAND-SOURCE: employee_band_site=10-49 from OSHA ITA Form 300A CY2025, filed 2
SITE-000850 | Deceuninck North America — Monroe | Monroe 45050 Butler C | 351 North Garver Road | government_filing | 2026-11-01 | ITA2025 | 351 North Garver Road. NAICS adjudication 2026-10-29 pass 5 (Phase 3): 325211 → 326121 (ADOPT_T
SITE-000866 | Haviland Drainage Products | Haviland 45851 Paulding C | 100 W. Main St | government_filing | 2026-11-01 | ITA2025 | 100 West Main Street. Parcel flag 2026-10-29 (pass 6 §3.4): county consistent on every candidat
SITE-000871 | DuPont — Circleville | Circleville 43113 Pickaway U | 800 DUPONT RD | registry | 2026-11-06 | FRS:110000381881&output=JSON | 800 Dupont Rd. Parcel corroboration 2026-10-29 (pass 6 §3.3): OGRIP StateParcelID 39129-J24-0-0
SITE-000887 | Emery Oleochemicals — Cincinnati | Cincinnati 45232 Hamilton C | 4900 Este Avenue | government_filing | 2026-11-01 | ITA2025 | 4900 Este Avenue. Ring 3 subtype: machinery_equipment. PASS 8 (2026-10-29) mechanical sweep lan
SITE-000891 | Engineered Profiles, Ironton | Ironton 45638 Lawrence U | 575 Private Road 1125 | government_filing | 2026-11-01 | ITA2025 | 575 Private Rd 1125. BAND-SOURCE: employee_band_site=50-99 from OSHA ITA Form 300A CY2025, file
SITE-000894 | Evans Adhesive Corporation — Columbus | Columbus 43220 Franklin U | 925 OLD HENDERSON ROAD | registry | 2026-11-06 | FRS:110000382595&output=JSON | 925 Old Henderson Road. PASS 8 (2026-10-29) mechanical sweep lane 2: NAICS 325520 coded from ca
SITE-000898 | Fabohio — Uhrichsville | Uhrichsville 44683 Tuscarawas C | 521 E 7th St | government_filing | 2026-11-01 | ITA2025 | 521 East 7th Street. BAND-SOURCE: employee_band_site=10-49 from OSHA ITA Form 300A CY2025, file
SITE-000905 | Findlay Vinyl — Findlay | Findlay 45840 Hancock C | 115 Stanford Parkway | government_filing | 2026-11-01 | ITA2025 | 115 Stanford Parkway. BAND-SOURCE: employee_band_site=50-99 from OSHA ITA Form 300A CY2025, fil
SITE-000906 | First Choice Packaging — Fremont | Fremont 43420 Sandusky C | 1501 W State Street | government_filing | 2026-11-01 | ITA2025 | 1501 West State Street.
SITE-000918 | Franklin Adhesives & Polymers — Columbus | Columbus 43207 Franklin C | 2020 BRUCK STREET | registry | 2026-11-06 | FRS:110000382345&output=JSON | 2020 Bruck St. NAICS adjudication 2026-10-29 pass 5 (Phase 3): 325211 → 325520 (ADOPT_GOVERNMEN
SITE-000923 | Gilkey Window Company, Inc. Cincinnati — Cincinnati | Cincinnati 45241 Hamilton C | 3625 Hauck Rd. | government_filing | 2026-11-01 | ITA2025 | 3625 Hauck Road.
SITE-000934 | Greenfield Precision Plastics, LLC — Greenfield | Greenfield 45123 Highland C | 175 Industrial Park Drive | government_filing | 2026-11-01 | ITA2025 | 175 Industrial Park Dr.. BAND-SOURCE: employee_band_site=10-49 from OSHA ITA Form 300A CY2025, 
SITE-000945 | HAVERHILL CHEMICALS LLC — Haverhill | Haverhill 45636 Scioto U | 1019 Haverhill-Ohio Furnace Rd | government_filing | 2026-11-01 | ITA2025 | 1019 Haverhill-Ohio Furnace Rd. NAICS adjudication 2026-10-29 pass 5 (Phase 3): 325211 → 325194
SITE-000947 | HBD/Thermoid, Inc. — Bellefontaine | Bellefontaine 43311 Logan C | 1301 W SANDUSKY AVE | registry | 2026-11-06 | FRS:110000382933&output=JSON | 1301 W. Sandusky Avenue. BAND-SOURCE: employee_band_site=100-249 from OSHA ITA Form 300A CY2025
SITE-000953 | Huhtamaki New Vienna Operations — New Vienna | New Vienna 45159 Highland C | 5566 New Vienna Rd | government_filing | 2026-11-01 | ITA2025 | 5566 New Vienna Road. INTEGRATION PASS 3 2026-10-28 (county adjudication): county corrected Cli
SITE-000957 | ILLINOIS TOOL WORKS — Bryan | Bryan 43506 Williams U | 730 East South Street | government_filing | 2026-11-01 | ITA2025 | 730 East South Street. BAND-SOURCE: employee_band_site=50-99 from OSHA ITA Form 300A CY2025, fi
SITE-000960 | Industrial Recyclers — Sidney | Sidney 45365 Shelby C | 2640 Campbell Rd | government_filing | 2026-11-01 | ITA2025 | 2640 Campbell Road. Ring 3 subtype: recycling_recovery. BAND-SOURCE: employee_band_site=50-99 f
SITE-000962 | Ineos USA — Lima | Lima 45804 Allen C | 1900 Fort Amanda Road | government_filing | 2026-11-01 | ITA2025 | 1900 Fort Amanda Road. BAND-SOURCE: employee_band_site=100-249 from OSHA ITA Form 300A CY2025, 
SITE-000966 | Integris Composites — Hebron | Hebron 43025 Licking C | 1051 O'Neill Drive | government_filing | 2026-11-01 | ITA2025 | 1051 O'Neill Drive. CERT-SITE (own site, observed 2026-11-01): as9100; iso_9001. BAND-SOURCE: e
SITE-000970 | Intertape Polymer Group (Springfield) | Springfield 45505 Clark C | 1800 E Pleasant St | government_filing | 2026-11-01 | ITA2025 | 1800 E. Pleasant St.. BAND-SOURCE: employee_band_site=50-99 from OSHA ITA Form 300A CY2025, fil
SITE-000972 | IPL Inc. — Urbana | Urbana 43078 Clark C | 1765 W. County Line Road | government_filing | 2026-11-01 | ITA2025 | 1765 W County Line Rd. INTEGRATION PASS 3 2026-10-28 (county adjudication): county corrected Ch
SITE-000986 | Kamco Industries, Inc. West Unity | West Unity 43570 Williams C | 1001 E. Jackson St. | government_filing | 2026-11-01 | ITA2025 | 1001 East Jackson Street. Parcel flag 2026-10-29 (pass 6 §3.4): county consistent on every cand
SITE-000991 | Klockner Pentaplast of America, Inc. — Greenville | Greenville 45331 Darke C | 1671 Martindale Rd. | government_filing | 2026-11-01 | ITA2025 | 1671 Martindale Road. INTEGRATION PASS 3 2026-10-28 (spatial dedupe S37): duplicate site row SI
SITE-000996 | Krom International — Celina | Celina 45822 Mercer C | 441 Grand lake rd | government_filing | 2026-11-01 | ITA2025 | 441 Grand Lake Road. BAND-SOURCE: employee_band_site=10-49 from OSHA ITA Form 300A CY2025, file
SITE-000997 | Kurz-Kasch Inc. — Newcomerstown | Newcomerstown 43832 Tuscarawas C | 199 E. State Street | government_filing | 2026-11-01 | ITA2025 | 199 E State St. BAND-SOURCE: employee_band_site=50-99 from OSHA ITA Form 300A CY2025, filed 202
SITE-001007 | LRBG Chemicals USA, Inc. — Toledo | Toledo 43606 Lucas C | 2112 SYLVAN AVE. | registry | 2026-11-06 | FRS:110000384003&output=JSON | 2112 Sylvan Avenue. INTEGRATION PASS 3 2026-10-28 (spatial dedupe S24): duplicate site row SITE
SITE-001010 | Magnum Magnetics Corporation - Devola | Marietta 45750 Washington U | 801 Masonic Park Road | government_filing | 2026-11-01 | ITA2025 | 801 Masonic Park Road. NAICS adjudication 2026-10-29 pass 5 (Phase 3): 326299 → 332999 (ADOPT_G
SITE-001031 | Michelman — Cincinnati | Cincinnati 45236 Hamilton C | 9080 Shell Road | government_filing | 2026-11-01 | ITA2025 | 9080 Shell Road. Ring 3 subtype: machinery_equipment. PASS 8 (2026-10-29) mechanical sweep lane
SITE-001033 | Midwest Molding, Inc. — Plain City | Plain City 43064 Union C | 8400 Industrial Parkway | government_filing | 2026-11-01 | ITA2025 | 8400 Industrial Parkway. INTEGRATION PASS 3 2026-10-28 (county adjudication): county corrected 
SITE-001044 | Moore Industries — Montpelier | Montpelier 43543 Williams C | 1317 Henricks Drive | government_filing | 2026-11-01 | ITA2025 | 1317 Henricks Dr. CERT-SITE (own site, observed 2026-11-01): iso_9001. BAND-SOURCE: employee_ba
SITE-001049 | MTNA - Marysville | Marysville 43040 Union U | 15000 Industrial Pkwy | government_filing | 2026-11-01 | ITA2025 | 15000 Industrial Parkway.
SITE-001053 | Nagase Chemtex America — Delaware | Delaware 43015 Delaware U | 100 Innovation Court | government_filing | 2026-11-01 | ITA2025 | 100 Innovation Ct.. PASS 8 (2026-10-29) mechanical sweep lane 2: NAICS 325510 coded from capabi
SITE-001061 | New Tech Plastics, Inc. — Covington | Covington 45318 Miami C | 1300 Mote Drive | government_filing | 2026-11-01 | ITA2025 | 1300 Mote Dr. Parcel corroboration 2026-10-29 (pass 6 §3.3): OGRIP StateParcelID 39109-H19-0115
SITE-001065 | Nifco America Corp. — Canal Winchester | Canal Winchester 43110 Fairfield C | 8015 DOVE PKWY | government_filing | 2026-11-01 | ITA2025 | 8015 Dove Parkway. INTEGRATION PASS 3 2026-10-28 (county adjudication): county corrected Frankl
SITE-001070 | Nox US — Fostoria | Fostoria 44830 Seneca C | 931 South Springville Avenue | government_filing | 2026-11-01 | ITA2025 | 931 South Springville Ave.. NAICS adjudication 2026-10-29 pass 5 (Phase 3): 326112 → 326199 (AD
SITE-001083 | ORBIS Urbana | Urbana 43078 Champaign C | 200 Elm Street | government_filing | 2026-11-01 | ITA2025 | 200 Elm Street. [Dedupe 2026-10-28: site re-pointed ORG-001004 -> ORG-000474 per global dedupe 
SITE-001098 | Pinnacle Industrial Enterprises — Bowling Green | Bowling Green 43402 Wood C | 513 Napoleon Rd | government_filing | 2026-11-01 | ITA2025 | 513 Napoleon Road. CERT-SITE (own site, observed 2026-11-01): iso_9001. BAND-SOURCE: employee_b
SITE-001104 | Plas-tec — Edon | Edon 43518 Williams C | 601 W INDIANA ST | government_filing | 2026-11-01 | ITA2025 | 601 W INDIANA ST. NAICS adjudication 2026-10-29 pass 5 (Phase 3): 326191 → 326199 (ADOPT_GOVERN
SITE-001126 | Polysource LLC dba Epsilyte — Piqua | Piqua 45356 Miami C | 555 E Statler Road | government_filing | 2026-11-01 | ITA2025 | 555 East Statler Rd.. BAND-SOURCE: employee_band_site=50-99 from OSHA ITA Form 300A CY2025, fil
SITE-001130 | Pretium Leipsic — Leipsic | Leipsic 45856 Putnam U | 150 S. Werner Street | government_filing | 2026-11-01 | ITA2025 | 150 S. Werner Street. [Dedupe 2026-10-28: site re-pointed ORG-001047 -> ORG-000523 per global d
SITE-001132 | Profusion Industries — Marietta | Marietta 45750 Washington C | 700 BF Goodrich Road | government_filing | 2026-11-01 | ITA2025 | 700 BF Goodrich Road. NAICS adjudication 2026-10-29 pass 5 (Phase 3): KEEP_ATLAS — atlas value 
SITE-001135 | Proto Plastics, Inc. — Tipp City | Tipp City 45371 Miami C | 316 Park Ave | government_filing | 2026-11-01 | ITA2025 | 316 Park Avenue. INTEGRATION PASS 3 2026-10-28 (spatial dedupe S43): duplicate site row SITE-00
SITE-001136 | ProVia New Philadelphia Facility | New Philadelphia 44663 Tuscarawas U | 629 Wabash Ave. NW | government_filing | 2026-11-01 | ITA2025 | 629 Wabash Ave NW. BAND-SOURCE: employee_band_site=50-99 from OSHA ITA Form 300A CY2025, filed 
SITE-001153 | Rage Corp. — Hilliard | Hilliard 43026 Franklin C | 3949 lyman dr | government_filing | 2026-11-01 | ITA2025 | 3949 Lyman Drive. NAICS adjudication 2026-10-29 pass 5 (Phase 3): 325211 → 326199 (ADOPT_GOVERN
SITE-001163 | Revere Plastics Systems — Clyde | Clyde 43410 Sandusky C | 401 E. ELM ST. | registry | 2026-11-06 | FRS:110000383175&output=JSON | 401 E. Elm Street. BAND-SOURCE: employee_band_site=250-499 from OSHA ITA Form 300A CY2025, file
SITE-001164 | Rhetech Colors — Sandusky | Sandusky 44870 Erie C | 2901 W. Monroe Street | government_filing | 2026-11-01 | ITA2025 | 2901 W. Monroe Street. NAICS adjudication 2026-10-29 pass 5 (Phase 3): 325211 → 325991 (ADOPT_T
SITE-001166 | Ridge Corporation — Pataskala | Pataskala 43062 Licking C | 1201 Etna Parkway | government_filing | 2026-11-01 | ITA2025 | 1201 Etna Parkway. BAND-SOURCE: employee_band_site=50-99 from OSHA ITA Form 300A CY2025, filed 
SITE-001169 | Rieke — New Albany | New Albany 43054 Franklin U | 8200 Innovation Campus Way West | government_filing | 2026-11-01 | ITA2025 | 8200 Innovation Campus Way West. PASS 8 (2026-10-29) mechanical sweep lane 2: NAICS 326199 code
SITE-001181 | Rowmark — Findlay | Findlay 45840 Hancock U | 5409 Hamlet Drive | government_filing | 2026-11-01 | ITA2025 | 5409 Hamlet Drive. BAND-SOURCE: employee_band_site=50-99 from OSHA ITA Form 300A CY2025, filed 
SITE-001182 | Royal Building Products — Columbus | Columbus 43207 Franklin U | 1441 Universal Rd | government_filing | 2026-11-01 | ITA2025 | 1441 Universal Road. PASS 8 (2026-10-29) mechanical sweep lane 2: NAICS 326199 coded from capab
SITE-001188 | Rudolph Bros. & Co. — Canal Winchester | Canal Winchester 43110 Fairfield U | 6550 Oley Speaks Way | government_filing | 2026-11-01 | ITA2025 | 6550 Oley Speaks Way. Ring 3 subtype: tooling_mold_die. INTEGRATION PASS 3 2026-10-28 (county a
SITE-001192 | Savare Specialty Adhesives — Delaware | Delaware 43015 Delaware U | 1201 South Houk Road | government_filing | 2026-11-01 | ITA2025 | 1201 S Houk Rd. PASS 8 (2026-10-29) mechanical sweep lane 2: NAICS 325520 coded from capability
SITE-001194 | Schupan Aluminum & Plastic Sales — Toledo | Toledo 43605 Lucas U | 1663 Tracy Road | government_filing | 2026-11-01 | ITA2025 | 1663 Tracy Road. Ring 3 subtype: distribution. PASS 8 (2026-10-29) mechanical sweep lane 2: NAI
SITE-001196 | Sealed Air — Ashland | Ashland 44805 Ashland U | 1817 Masters Ave | government_filing | 2026-11-01 | ITA2025 | 1817 Masters Avenue. PASS 8 (2026-10-29) mechanical sweep lane 2: NAICS 326113 coded from capab
SITE-001199 | Sekisui Kasei USA Inc. — Kenton | Kenton 43326 Hardin C | 13950 US Hwy 68 | government_filing | 2026-11-01 | ITA2025 | 13950 US Highway 68. BAND-SOURCE: employee_band_site=10-49 from OSHA ITA Form 300A CY2025, file
SITE-001205 | Sika Corp. — Marion | Marion 43302 Marion C | 1682 MARION-WILLIAMSPORT RD | registry | 2026-11-06 | FRS:110000382844&output=JSON | 1682 Marion Williamsport Rd. BAND-SOURCE: employee_band_site=100-249 from OSHA ITA Form 300A CY
SITE-001206 | Silgan Plastics — Ottawa | Ottawa 45875 Putnam C | 690 Woodland Drive | government_filing | 2026-11-01 | ITA2025 | 690 Woodland Drive. BAND-SOURCE: employee_band_site=100-249 from OSHA ITA Form 300A CY2025, fil
SITE-001208 | Sonoco (Franklin, OH - Flexible Pkg - E017) | Franklin 45005 Warren U | 708 South Ave | government_filing | 2026-11-01 | ITA2025 | 708 South Avenue. BAND-SOURCE: employee_band_site=100-249 from OSHA ITA Form 300A CY2025, filed
SITE-001209 | Southeastern Container — Bowling Green | Bowling Green 43402 Wood C | 307 Industrial Parkway | government_filing | 2026-11-01 | ITA2025 | 307 Industrial Parkway. BAND-SOURCE: employee_band_site=50-99 from OSHA ITA Form 300A CY2025, f
SITE-001216 | Standridge Color — Defiance | Defiance 43512 Defiance C | 1160 Integrity Dr | government_filing | 2026-11-01 | ITA2025 | 1160 Integrity Drive. CERT-SITE (own site, observed 2026-11-01): iso_9001. BAND-SOURCE: employe
SITE-001220 | Storopack — Cincinnati | Cincinnati 45246 Butler C | 4758 Devitt Dr. | government_filing | 2026-11-01 | ITA2025 | 4758 Devitt Drive. INTEGRATION PASS 3 2026-10-28 (county adjudication): county corrected Hamilt
SITE-001221 | Storopack, Inc.- Cincinnati Distribution Center | Cincinnati 45246 Butler U | 4663 Dues Dr. | government_filing | 2026-11-01 | ITA2025 | 4663 Dues Drive. INTEGRATION PASS 3 2026-10-28 (county adjudication): county corrected Hamilton
SITE-001223 | Style Crest Enterprises — Fremont | Fremont 43420 Sandusky C | 600 HAGERTY DR. | registry | 2026-11-06 | FRS:110000383246&output=JSON | 600 HAGERTY DR.. BAND-SOURCE: employee_band_site=100-249 from OSHA inspection record, opened 20
SITE-001224 | SumiRiko Inc. — Bluffton | Bluffton 45817 Allen C | 320 Snider Rd | government_filing | 2026-11-01 | ITA2025 | 320 Snider Road. BAND-SOURCE: employee_band_site=500-999 from OSHA ITA Form 300A CY2025, filed 
SITE-001236 | Tech Intl — Johnstown | Johnstown 43031-0486 Licking C | 200 E. COSHOCTON ST. | registry | 2026-11-06 | FRS:110000381532&output=JSON | 200 East Coshocton Street. INTEGRATION PASS 3 2026-10-28 (spatial dedupe S48): duplicate site r
SITE-001244 | Tetra Mold & Tool, Inc. — New Carlisle | New Carlisle 45344 Clark C | 51 Quick Rd | government_filing | 2026-11-01 | ITA2025 | 51 Quick Rd.. BAND-SOURCE: employee_band_site=10-49 from OSHA ITA Form 300A CY2025, filed 2026-
SITE-001246 | TH Plastics - Bowling Green | Bowling Green 43402 Wood C | 843 Miller Drive | government_filing | 2026-11-01 | ITA2025 | 843 Miller Drive. INTEGRATION PASS 3 2026-10-28 (spatial dedupe S49): duplicate site row SITE-0
SITE-001247 | TH Plastics - Findlay Ohio | Findlay 45840 Hancock C | 101 Bentley Court | government_filing | 2026-11-01 | ITA2025 | 101 Bentley Court. BAND-SOURCE: employee_band_site=100-249 from OSHA ITA Form 300A CY2025, file
SITE-001249 | Thaman Rubber Co. — Cincinnati | Cincinnati 45241 Hamilton C | 3280 Hageman St | government_filing | 2026-11-01 | ITA2025 | 3280 Hageman St.. Ring 3 subtype: distribution. BAND-SOURCE: employee_band_site=50-99 from OSHA
SITE-001252 | Titan Tire — Bryan | Bryan 43506 Williams C | 927 SOUTH UNION STREET | registry | 2026-11-06 | FRS:110000383460&output=JSON | 927 S Union St. BAND-SOURCE: employee_band_site=100-249 from OSHA ITA Form 300A CY2025, filed 2
SITE-001270 | Uni-Grip Incorporated — Upper Sandusky | Upper Sandusky 43351 Wyandot C | 9823 STATE HIGHWAY 53 N | government_filing | 2026-11-01 | ITA2025 | 9823 State Highway 53 North. BAND-SOURCE: employee_band_site=50-99 from OSHA ITA Form 300A CY20
SITE-001275 | United States Plastic — Lima | Lima 45801 Allen C | 1390 Neubrecht Road | government_filing | 2026-11-01 | ITA2025 | 1390 Neubrecht Rd.. Ring 3 subtype: distribution. BAND-SOURCE: employee_band_site=100-249 from 
SITE-001281 | Ventek Solutions — Findlay | Findlay 45840 Hancock C | 1900 Industrial Drive | government_filing | 2026-11-01 | ITA2025 | 1900 Industrial Drive. INTEGRATION PASS 3 2026-10-28 (spatial dedupe S28): duplicate site row S
SITE-001284 | Versa Pak — Celina | Celina 45822 Mercer C | 500 Staeger Rd | government_filing | 2026-11-01 | ITA2025 | 500 Staeger Road. NAICS adjudication 2026-10-29 pass 5 (Phase 3): KEEP_ATLAS — atlas value 3261
SITE-001290 | Vinylmax OH — Hamilton | Hamilton 45011 Butler C | 2921 McBride Ct | government_filing | 2026-11-01 | ITA2025 | 2921 McBride Ct. BAND-SOURCE: employee_band_site=250-499 from OSHA ITA Form 300A CY2025, filed 
SITE-001292 | Washington Penn Plastic Co., Inc. — Wapakoneta | Wapakoneta 45895 Auglaize C | 14097 Cemetery Rd | government_filing | 2026-11-01 | ITA2025 | 14097 Cemetery Road. BAND-SOURCE: employee_band_site=50-99 from OSHA ITA Form 300A CY2025, file
SITE-001303 | World Class Plastics, Inc. — Russells Point | Russells Point 43348 Logan C | 7695 State Route 708 | government_filing | 2026-11-01 | ITA2025 | 7695 State Route 708. CERT-SITE (own site, observed 2026-11-01): iso_9001. BAND-SOURCE: employe
SITE-001304 | Yamashita Rubber/YUSA Corp — Washington Court House | Washington Court House 43160 Fayette U | 151 JAMISON RD. SW | registry | 2026-11-06 | FRS:110000382194&output=JSON | 151 Jamison Rd SW. PASS 8 (2026-10-29) mechanical sweep lane 2: NAICS 326291 coded from capabil
SITE-001828 | Performance Plastics Ltd. (now part of Pexco) | Cincinnati 45209 Hamilton C | 4435 Brownway Ave. | government_filing | 2026-11-01 | ITA2025 | 4435 Brownway Ave. BAND-SOURCE: employee_band_site=50-99 from OSHA ITA Form 300A CY2025, filed 
SITE-001838 | Polymerics, Inc. | Kent 44240 Portage A | 1540 St Clair Ave | own_site | 2026-11-06 | http://www.polymericsinc.com | 1540 ST CLAIR AVE. BAND-SOURCE: employee_band_site=10-49 from OSHA ITA Form 300A CY2025, filed 
Raw checked 2026-11-06; SHA-256 ee3890e959c2cf2374c2ef1a67c19693978553306deed5dfdce67e709d8e3122; quote: 1540 St. Clair Avenue • Kent, Ohio 44240. County, county_source and record tier unchanged.
SITE-002081 | DayGlo Avon site | Avon 44011 Lorain C | 38620 Chester Rd. | government_filing | 2026-11-01 | ITA2025 | 38620 Chester Rd. BAND-SOURCE: employee_band_site=1-9 from OSHA ITA Form 300A CY2025, filed 202