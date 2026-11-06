"""Paced seeded fresh FRS audit, plus inherited-ITA transcription when applicable."""
import csv,json,random,re,time
from fetch import TASK,ROOT,frs,read,write
from build import identity
evidence=read(TASK/'evidence_proposed9.csv');admitted={e['record_id'] for e in read(TASK/'evidence.csv')};sites={s['site_id']:s for s in read(TASK/'frame.csv')}
links=read(TASK/'registry_links_input.csv')+read(TASK/'frs_notes_leads.csv');sample=random.Random(20261106).sample(sorted(evidence,key=lambda e:e['record_id']),min(30,len(evidence)))
ita=read(ROOT/'tasks/osha-ita-2026-11-01/site_matches.csv')
out=[]
for e in sample:
 sid=e['record_id'];s=sites[sid];transcription='not_ITA';error='';detail='';corroborated=False
 street=e['claim_detail'].removeprefix('street_address ').split(', '+s['city']+', OH ',1)[0]
 if e['source_class']=='government_filing':
  transcription='PASS' if any(m['site_id']==sid and m['match_strength'] in ('exact','strong') and frs.streetkey(m['street'])==frs.streetkey(street) and frs.norm(m['city'])==frs.norm(s['city']) and m['zip5']==s['zip'][:5] for m in ita) else 'FAIL'
  if transcription=='FAIL':error='ITA transcription mismatch'
 rid=re.search(r'registry_id=(\d+)',e['source_ref'])[1] if e['source_class']=='registry' else next(r['registry_id'] for r in links if r['site_id']==sid)
 try:
  f=frs.facility(frs.fetch(rid,'audit_raw'),rid);mismatch=frs.conflict(s,f)
  if not identity(s,f):raise ValueError('fresh FRS operator identity differs')
  if mismatch:raise ValueError('FRS not corroborating: '+mismatch)
  if frs.streetkey(f['LocationAddress'])!=frs.streetkey(street):error='fresh FRS street disagrees: '+f['LocationAddress']
  else:corroborated=True;detail='fresh identifier,street,city,ZIP,county,state agree'
 except Exception as ex:detail=str(ex)
 out.append(dict(site_id=sid,source_class=e['source_class'],registry_id=rid,transcription=transcription,fresh_source_match='yes' if corroborated else 'no',detail=detail,error=error))
 write(TASK/'audit.csv',out);print(sid,corroborated,error,detail,flush=True);time.sleep(12)
summary=dict(original_candidates=len(evidence),accepted_fills=len(admitted),sampled=len(out),ita_sampled=sum(r['transcription']!='not_ITA' for r in out),transcription_errors=sum(r['transcription']=='FAIL' for r in out),
             fresh_source_matches=sum(r['fresh_source_match']=='yes' for r in out),not_freshly_checkable=sum(r['fresh_source_match']=='no' and not r['error'] for r in out),address_errors=sum(bool(r['error']) for r in out))
(TASK/'audit_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary)
assert len(out)==min(30,len(evidence)) and summary['address_errors']==0 and summary['transcription_errors']==0
# Registry fill rows require their own cited FRS source to re-fetch, not the inherited-bulk exception.
assert all(r['fresh_source_match']=='yes' for r in out if r['source_class']=='registry' and r['site_id'] in admitted),'registry audit source unavailable'
