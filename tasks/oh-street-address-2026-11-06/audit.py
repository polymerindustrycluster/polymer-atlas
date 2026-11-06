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
