"""Seeded source transcription directly against the official ZIP; optional fresh REST is a separate witness."""
import hashlib,json,random,re,time,zipfile
from fetch import TASK,frs,read,write
from fetch_bulk import CACHE,FIELDS,helper,facility
from build import identity
source=json.loads((TASK/'bulk_manifest.json').read_text())['source']
evidence=read(TASK/'evidence_proposed.csv');admitted={e['record_id'] for e in read(TASK/'evidence.csv')}
sample=random.Random(20261106).sample(sorted(evidence,key=lambda e:e['record_id']),min(30,len(evidence)))
sites={r['site_id']:r for r in read(TASK/'frame.csv')}
ids={re.search(r'REGISTRY_ID (\d+);',e['notes'])[1] for e in sample};found={rid:[] for rid in ids}
archive=CACHE/source['file'];assert archive.stat().st_size==source['size'] and helper.sha256(archive)==source['sha256']
count=0
with zipfile.ZipFile(archive) as z:
 members=[n for n in z.namelist() if n.lower().endswith('.csv')];assert len(members)==1
 for row in helper.csv_rows(z,members[0]):
  count+=1
  if row.get('REGISTRY_ID') in ids:found[row['REGISTRY_ID']].append({k:row.get(k) or '' for k in FIELDS})
assert count==source['row_count']==source['independent_count'],'archive row yield differs from manifest'
out=[]
rest_proof={r['site_id']:r for r in read(TASK/'audit_rest.csv')}
for e in sample:
 sid=e['record_id'];s=sites[sid];rid=re.search(r'REGISTRY_ID (\d+);',e['notes'])[1];error='';fresh='not_checked';detail=''
 raw=found[rid];assert len(raw)==1,'missing/duplicate archive ID'
 banked=json.loads((TASK/'bulk_raw'/(rid+'.json')).read_text())
 assert raw==banked,'banked projection differs from exact official CSV row'
 f=facility(raw,rid);street=e['claim_detail'].removeprefix('street_address ').split(', '+s['city']+', OH ',1)[0]
 assert identity(s,f) and not frs.conflict(s,f) and street==f['LocationAddress'],'bulk transcription/binding differs'
 # These three prior fresh audits remain separate REST observations; no archive row is labeled freshly updated.
 prior=rest_proof.get(sid)
 path=TASK/'audit_raw'/(rid+'.json')
 try:
  if prior and prior['fresh_source_match']=='yes' and path.exists():
   other=frs.facility(json.loads(path.read_text()),rid);detail='prior same-task fresh REST audit, retained independently'
  else:
   try:other=frs.facility(frs.fetch(rid,'bulk_audit_rest_raw'),rid)
   finally:time.sleep(12)
   detail='fresh optional REST re-fetch'
  fields=('LocationAddress','CityName','ZipCode','CountyName','StateAbbr')
  if not identity(s,other):error='REST identity differs from held operator'
  for field in fields:
   left=other.get(field) or '';right=f.get(field) or ''
   if not left:continue
   normalize=frs.streetkey if field=='LocationAddress' else (lambda x:x[:5]) if field=='ZipCode' else frs.norm
   if normalize(left)!=normalize(right):error='fresh REST disagrees on '+field
  fresh='yes' if not error and not frs.conflict(s,other) else 'incomplete' if not error else 'disagrees'
 except Exception as ex:fresh='unavailable';detail=str(ex)
 out.append(dict(site_id=sid,registry_id=rid,bulk_transcription='PASS',bulk_row_sha256=hashlib.sha256(json.dumps(raw[0],sort_keys=True).encode()).hexdigest(),fresh_rest_match=fresh,rest_detail=detail,error=error))
 write(TASK/'audit.csv',out);print(sid,'bulk PASS','REST',fresh,error,flush=True)
summary=dict(original_candidates=len(evidence),sampled=len(out),accepted_fills=len(admitted),archive_rows_reconciled=count,bulk_transcription_errors=0,fresh_rest_matches=sum(r['fresh_rest_match']=='yes' for r in out),rest_unavailable=sum(r['fresh_rest_match']=='unavailable' for r in out),rest_incomplete=sum(r['fresh_rest_match']=='incomplete' for r in out),address_disagreements=sum(bool(r['error']) for r in out),source_download_date=source['date'],source_is_address_effective_date=False)
(TASK/'audit_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary)
assert len(out)==min(30,len(evidence)) and all(not r['error'] for r in out if r['site_id'] in admitted)
