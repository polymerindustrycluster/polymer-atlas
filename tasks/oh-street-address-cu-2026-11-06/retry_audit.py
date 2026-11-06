"""Retry only unavailable registry audit rows; retain the original failures and reassert the full gate."""
import json,time
from fetch import TASK,frs,read,write
rows=read(TASK/'audit.csv');sites={s['site_id']:s for s in read(TASK/'frame.csv')};ev={e['record_id']:e for e in read(TASK/'evidence.csv')};log=[]
for r in rows:
 if r['fresh_source_match']=='yes':continue
 old=r['detail'];s=sites[r['site_id']];e=ev[r['site_id']];street=e['claim_detail'].removeprefix('street_address ').split(', '+s['city']+', OH ',1)[0]
 try:
  f=frs.facility(frs.fetch(r['registry_id'],'audit_raw'),r['registry_id'])
  assert not frs.conflict(s,f),frs.conflict(s,f)
  assert frs.streetkey(f['LocationAddress'])==frs.streetkey(street),'fresh street disagrees'
  r.update(fresh_source_match='yes',detail='fresh identifier,street,city,ZIP,county,state agree on bounded retry',error='')
 except AssertionError as ex:r.update(detail=str(ex),error=str(ex))
 except Exception as ex:r.update(detail=str(ex),error='')
 log.append(dict(site_id=r['site_id'],registry_id=r['registry_id'],prior=old,after=r['detail'],result=r['fresh_source_match']))
 write(TASK/'audit.csv',rows);write(TASK/'audit_retry_log.csv',log);print(log[-1],flush=True);time.sleep(12)
summary=dict(accepted_fills=len(ev),sampled=len(rows),ita_sampled=sum(r['transcription']!='not_ITA' for r in rows),transcription_errors=sum(r['transcription']=='FAIL' for r in rows),fresh_source_matches=sum(r['fresh_source_match']=='yes' for r in rows),not_freshly_checkable=sum(r['fresh_source_match']=='no' and not r['error'] for r in rows),address_errors=sum(bool(r['error']) for r in rows))
(TASK/'audit_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary)
assert summary['address_errors']==0 and summary['transcription_errors']==0 and summary['fresh_source_matches']==len(rows)==min(30,len(ev))
