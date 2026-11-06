"""Compile the frozen, manually reviewed promotion/hold packet; no canonical writes."""
import csv,hashlib,json,sys
from pathlib import Path
from research import found,read
P=Path(__file__).resolve().parent;ROOT=P.parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from atlas import name_key
def write(p,rows,fields=None):
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields or list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 frame=read(P/'input.csv');before={r['site_id']:r for r in json.loads((P/'before.json').read_text())['sites']}
 witnesses={r['site_id']:r for r in read(P/'witnesses.csv')};fetches={r['source_id']:r for r in read(P/'fetches.csv')}
 ita={r['establishment_id']:r for r in read(ROOT/'tasks/osha-ita-2026-11-01/establishments.csv')}
 orgs={r['org_id']:r for p in (ROOT/'data').glob('organizations_*.csv') for r in read(p)}
 allocations={}
 for slug in ['corroborated-fl-ga','corroborated-ga','corroborated-ny','corroborated-in','corroborated-wi']:
  for a in read(ROOT/f'tasks/{slug}-2026-11-06/allocations.csv'):
   assert a['site_id'] not in allocations;allocations[a['site_id']]=a
 assert len(frame)==len(before)==len(allocations)==75 and set(before)==set(allocations)
 assert len(witnesses)==31 and set(witnesses)<=set(before)
 holds={r['site_id']:r for r in read(P/'holds.csv')};assert set(holds)==set(before)-set(witnesses)
 evidence=[];edits=[];verdicts=[];raw=[];gov=[];eligibility=[];reservations=[]
 for index,r in enumerate(frame):
  sid=r['site_id'];s=before[sid];oid=s['org_id'];start=207000+index*10
  reservations.append(dict(site_id=sid,evidence_start=f'EVD-{start:06d}',evidence_end=f'EVD-{start+9:06d}'))
  if sid not in witnesses:
   verdicts.append(dict(site_id=sid,state=s['state'],verdict='STILL_UNCERTAIN',reason=holds[sid]['settling_fact']));continue
  w=witnesses[sid];source=fetches[w['source_id']];text=Path(source['cache_file']).read_text()
  assert source['fetch']=='loaded' and found(text,w['quote']),('raw quote',sid)
  assert not found(text,w['quote']+' fabricated L7 defect'),('negative control',sid)
  assert hashlib.sha256(Path(source['cache_file']).read_bytes()).hexdigest()==source['raw_sha256']
  a=allocations[sid];f=ita[a['establishment_id']];o=orgs[oid]
  assert a['org_id']==oid and f['state']==s['state'] and f['city'].casefold()==s['city'].casefold() and f['zip5']==s['zip']
  assert f['naics_code']==s['naics_primary'] and f['reliability']=='ok' and f['size_code_vs_avg_employees']=='consistent'
  names={name_key(o['legal_name']),*(name_key(t.removesuffix(' (federal registrant name)').strip()) for t in o['trade_names'].split(';'))}
  assert name_key(f['company_name']) in names,('filed operator',sid,f['company_name'])
  fields=['establishment_id','company_name','establishment_name','street','city','state','zip5','naics_code','industry_description','date_submitted','year_filing_for','reliability','size_code_vs_avg_employees']
  gov.append({'site_id':sid,**{k:f[k] for k in fields}})
  eligibility.append(dict(site_id=sid,org_id=oid,source_ref=source['url'],issuer_basis=w['issuer_basis'],site_binding=w['site_binding'],parent_org_id=o['parent_org_id'],ultimate_parent_name=o['ultimate_parent_name']))
  ref='https://www.osha.gov/sites/default/largefiles/ITA_300A_Summary_Data_2025_through_08-31-2026.csv#establishment_ID='+f['establishment_id']
  notes=f"Re-observed banked CY2025 filing; establishment_ID {f['establishment_id']}; date_submitted {f['date_submitted']}; packet observed2026-11-01, reviewed2026-11-06 under controller inherited-source authorization. Provisional operating evidence at filing vintage; no fresh2026 operating-status assertion."
  claims={
   'existence':f"Filed establishment_name {f['establishment_name']}; company_name {f['company_name']}",
   'address':f"{s['street_address']}, {s['city']}, {s['state']} {s['zip']}, US; county remains unset",
   'code':f"naics_primary {f['naics_code']}; government_filing, medium confidence",
   'parent':f"Recorded operator org_id {oid} ({o['legal_name']}); filed company_name {f['company_name']}",
   'activity':f"CY{f['year_filing_for']} establishment activity: {f['industry_description']}",
   'liveness':f"CY{f['year_filing_for']} establishment filing submitted {f['date_submitted']}; operating evidence at filing vintage, no2026 live-operation check"}
  for offset,(claim,detail) in enumerate(claims.items()):
   evidence.append(dict(evidence_id=f'EVD-{start+offset:06d}',record_table='sites',record_id=sid,claim_type=claim,claim_detail=detail,source_class='government_filing',source_ref=ref,observed_date='2026-11-01',tier_effect='supports_B',created_by='codex atlas-L7-site-quality',notes=notes))
  eid=f'EVD-{start+6:06d}'
  evidence.append(dict(evidence_id=eid,record_table='sites',record_id=sid,claim_type='scope',claim_detail=w['quote'],source_class='own_site',source_ref=source['url'],observed_date='2026-11-06',tier_effect='supports_B',created_by='codex atlas-L7-site-quality',notes=f"Raw words checked2026-11-06. Witness vintage: {w['witness_vintage']}. Site-specific context and issuer recorded in task source_eligibility.csv. No certification-currency or current operating-status claim."))
  raw.append(dict(evidence_id=eid,site_id=sid,source_id=w['source_id'],source_ref=source['url'],quote=w['quote'],cache_file=source['cache_file'],raw_sha256=source['raw_sha256'],raw_check='PASS',witness_vintage=w['witness_vintage']))
  edits.append(dict(site_id=sid,state=s['state'],field='verification_tier',old='C',new='B'))
  additions=[source['url']]
  existing=[x.strip() for x in s['sources'].split(';') if x.strip()]
  new='; '.join(existing+[x for x in additions if x not in existing])
  if new!=s['sources']:edits.append(dict(site_id=sid,state=s['state'],field='sources',old=s['sources'],new=new))
  verdicts.append(dict(site_id=sid,state=s['state'],verdict='VERIFIED',reason='C→B: raw own-site polymer activity and re-observed government must-have claims; source dates retained; no status/identity/type motion.'))
 for name,rows in [('evidence_packet',evidence),('edits',edits),('verdicts',verdicts),('rawcheck',raw),('government_review',gov),('source_eligibility',eligibility),('id_reservations',reservations)]:write(P/(name+'.csv'),rows)
 print('Packet:',len(frame),'sites;',len(witnesses),'C→B;',len(holds),'holds;',len(evidence),'evidence;',len(edits),'cells')
if __name__=='__main__':main()
