"""Curated correction cells; all source/identity/ID checks precede any canonical write."""
import argparse,csv,hashlib,json,sys
from collections import defaultdict
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from shard_io import append_sorted
from fetch import read,write,on_page
DATE='2026-11-06';BY='codex atlas-L11-creation-corrections'
KEYS=['GILKEY_TYPE','STOROPACK_OWN','STOROPACK_MUNICIPAL','EJP_DISRUPTION','EJP_WATCH','EJP_DATED','DART_TYPE','YOKO_OUTCOME','YOKO_BINDING']
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');ap.add_argument('--data-dir',type=Path,default=ROOT/'data');a=ap.parse_args();data=a.data_dir
 raw=read(H/'rawcheck.csv');r={x['key']:x for x in raw};assert len(raw)==len(r)==9 and set(r)==set(KEYS)
 expected_targets={'GILKEY_TYPE':'SITE-019018','STOROPACK_OWN':'SITE-019009','STOROPACK_MUNICIPAL':'SITE-019009','EJP_DISRUPTION':'SITE-018014','EJP_WATCH':'ORG-007011','EJP_DATED':'SITE-018014','DART_TYPE':'SITE-014003','YOKO_OUTCOME':'SITE-012023','YOKO_BINDING':'SITE-012023'}
 assert all(x['record_id']==expected_targets[x['key']] and x['record_table']==('organizations' if x['key']=='EJP_WATCH' else 'sites') for x in raw),'witness target mismatch'
 for x in raw:
  page=ROOT/x['page'];assert hashlib.sha256(page.read_bytes()).hexdigest()==x['page_sha256'],'frozen source hash changed'
  assert x['quote'] and on_page(x['quote'],page),('raw quote absent',x['key'])
  if x['source_date']:__import__('datetime').date.fromisoformat(x['source_date'])
 assert r['YOKO_OUTCOME']['source_date']=='2026-02-19' and on_page('February 19, 2026',ROOT/r['YOKO_OUTCOME']['page'])
 assert r['YOKO_OUTCOME']['quote']=='Y-TWS Spartanburg Plant Closed'
 assert on_page('570 Trelleborg Dr., Spartanburg, SC 29301',ROOT/r['YOKO_BINDING']['page'])
 assert on_page('10160 Virginia Avenue Chicago Ridge, IL 60415',ROOT/r['GILKEY_TYPE']['page'])
 assert on_page('150 S. Maple Street, Corona, CA 92878',ROOT/r['DART_TYPE']['page'])
 gate=read(H/'form5500_gate.csv');heldgate=[x for x in read(ROOT/'tasks/form5500-spine-2026-11-01/sponsors.csv') if x['ein']=='061316073']
 assert gate==heldgate and gate[0]['city']=='WAKEFIELD' and gate[0]['state']=='MA' and 'AUDUBON' in gate[0]['street_address']
 # The plan is corporate, not Spartanburg site evidence; WARN alone can never supply the outcome.
 base=read(H/'input.csv');orgbase=read(H/'organizations_input.csv')
 assert {x['site_id'] for x in base}=={'SITE-019018','SITE-019009','SITE-018014','SITE-014003','SITE-012023'}
 allsites=[(p.name,x) for p in data.glob('sites_*.csv') for x in read(p)];sites={x['site_id']:(n,x) for n,x in allsites};assert len(sites)==len(allsites)
 orgs={x['org_id']:(p.name,x) for p in data.glob('organizations_*.csv') for x in read(p)}
 evs=[(p.name,x) for p in data.glob('evidence_*.csv') for x in read(p)];ev={x['evidence_id']:(n,x) for n,x in evs};assert len(ev)==len(evs),'global EVD collision'
 assert orgs['ORG-001336'][1]['ultimate_parent_name']=='Yokohama Rubber Co., Ltd.'
 edits=defaultdict(dict);verdicts=[]
 changes={
 'SITE-019018':dict(site_type='sales_office'),
 'SITE-019009':dict(street_address='320 Craig Place'),
 'SITE-018014':{},
 'SITE-014003':dict(site_type='warehouse_distribution'),
 'SITE-012023':dict(operating_status='closed')}
 notes={
 'SITE-019018':'Own Chicago Ridge page explicitly labels Showroom/Office and window replacement. Physical type sales_office; showroom noted. Ring1 and local scope HOLD for owner battery per controller, no parent-process inheritance. Filed NAICS326199 retained as disputed historical filing, not proof of manufacturing. ITA114099 itself uses this Chicago Ridge street; no plant-elsewhere relocation inferred. Cincinnati factory already held SITE-000923.',
 'SITE-019009':'Street corrected to320 Craig Place from current own named Hillside location plus independently raw municipal Western Springs recycling guide; banked EPA110001337198 alsoPlace. ITA1082283 says320 Craig Road and remains retained as conflicting spelling, not claimed legal alias. No site-function/code/tier change; local manufacturing remains unconfirmed.',
 'SITE-018014':'Own statement published2026-09-26 reports substantial fire; EPA response update2026-10-01 dates event2026-09-25. Recovery follow-up queued via parentORG007011 monitor_watch. No operating-status inference/change; unknown retained.',
 'SITE-014003':'Current exact150SMaple own page describes Corona Distribution Center: warehouse_distribution replaces manufacturing_plant. Existing Ring1 is HOLD, not re-affirmed; owner battery required for producer-owned distribution site ring. ZIP92878own versus92880held remains unresolved/no ZIPedit. DistinctNMapleWARN is not this location; no closure inference.',
 'SITE-012023':'Closed confirmed by issuer Fiscal2025 briefing dated2026-02-19,p17: Y-TWS Spartanburg Plant Closed. Exact570TrelleborgDrive bound by official SCWARN report2025-03-03 and heldITA1059636. Closure actual day UNKNOWN; 2025-04-19 is projectedWARNdate only. status_source=https://www.y-yokohama.com/global/ir/pdf/document/25_4Qpresentation_en_transcripts.pdf; closure_confirmed_by=2026-02-19. CorporateForm5500EIN061316073 WakefieldMA sponsor is not site-specific operating evidence. Historicalplant retained, no deletion/relink, parent active status untouched.'}
 for b in base:
  sid=b['site_id'];name,now=sites[sid];old={k:b[k] for k in now};new=old.copy();new.update(changes[sid]);urls=list(dict.fromkeys(x['source_url'] for x in raw if x['record_table']=='sites' and x['record_id']==sid))
  new['sources']=old['sources']+';'+';'.join(urls);new['notes']=old['notes']+' | '+DATE+': '+notes[sid];new['last_verified']=DATE
  assert now in [old,new],('site preimage changed',sid);edits[name][sid]=new
  verdicts.append(dict(record_id=sid,verdict='VERIFIED',reason=notes[sid]))
 b=next(x for x in orgbase if x['org_id']=='ORG-007011');name,now=orgs[b['org_id']];old={k:b[k] for k in now};new=old.copy();new['monitor_watch']='true';new['notes']=old['notes']+' | '+DATE+': monitor_watch=true: South Haven fire2026-09-25, own statement2026-09-26; recovery/operations settling fact required. Queue flag only, no status/tier/date/liveness-floor change.'
 assert now in [old,new],('org preimage changed',b['org_id']);edits[name][b['org_id']]=new
 verdicts.append(dict(record_id=b['org_id'],verdict='VERIFIED',reason='Monitoring allocation only underSCHEMA4.4; dated SouthHaven disruption, no status/tier/date change.'))
 out=defaultdict(list);alloc=[]
 for slot,key in enumerate(KEYS):
  x=r[key];rid=x['record_id'];name=(sites if x['record_table']=='sites' else orgs)[rid][0];shard='evidence_'+name
  sc='government_filing' if key in ['STOROPACK_MUNICIPAL','EJP_DATED','YOKO_BINDING'] else 'own_site'
  e=dict(evidence_id=f'EVD-{278500+slot:06d}',record_table=x['record_table'],record_id=rid,claim_type=x['claim_type'],claim_detail='"'+x['quote']+'"',source_class=sc,source_ref=x['source_url'],observed_date=DATE,tier_effect=x['tier_effect'],created_by=BY,notes=f"Raw fetched {x['fetched_at']}; source published/revised {x['source_date'] or 'undated'}. "+x['note'])
  out[shard].append(e);alloc.append(dict(key=key,evidence_id=e['evidence_id'],record_id=rid,shard=shard))
 logs=[]
 for sid,label,question in [('SITE-019018','Gilkey Chicago Ridge showroom','Consumer window sales/showroom: admit producer sales office Ring3 or exclude retail/installation?'),('SITE-014003','Dart Corona distribution center','Producer-owned polymer-product distribution warehouse: Ring3 or other owner treatment?')]:
  logs.append(dict(date=DATE,entity=label+' '+sid,decision='HOLD ring/scope — owner battery pending',rule_cited='SCHEMA R9; §1/B14; AGENTS §2 rule9',researcher=BY,notes=question+' Correct physical site_type only; existing ring is unresolved, not reaffirmed. Source '+r['GILKEY_TYPE' if 'Gilkey' in label else 'DART_TYPE']['source_url']))
 oldlog=read(data/'inclusion_log.csv');pendinglog=[]
 for x in logs:
  same=[z for z in oldlog if z['entity']==x['entity'] and z['researcher']==BY]
  assert not same or same==[x],'inclusion seam collision'
  if not same:pendinglog.append(x)
 pending={}
 for name,rows in out.items():
  header=list(read(data/name)[0]);pending[name]=[]
  for e in rows:
   if e['evidence_id'] in ev:assert ev[e['evidence_id']]==(name,{k:e.get(k,'') for k in header}),('global ID collision',e['evidence_id'])
   else:pending[name].append(e)
 if a.apply:
  for name,byid in edits.items():
   rows=read(data/name);key='site_id' if name.startswith('sites_') else 'org_id';newrows=[byid.get(x[key],x) for x in rows]
   if rows!=newrows:write(data/name,newrows,list(rows[0]))
  for name,rows in pending.items():
   if rows:append_sorted(data/name,rows,'evidence_id')
  if pendinglog:
   with (data/'inclusion_log.csv').open('a',newline='') as f:csv.DictWriter(f,fieldnames=list(oldlog[0]),lineterminator='\n').writerows(pendinglog)
 write(H/'verdicts.csv',verdicts,['record_id','verdict','reason']);write(H/'allocations.csv',alloc,['key','evidence_id','record_id','shard'])
 print(json.dumps(dict(sites_reviewed=5,site_cells=sum(len(changes[x]) for x in changes),organization_watch_flags=1,evidence=9,owner_ring_holds=2,pending_evidence=sum(map(len,pending.values())),pending_seams=len(pendinglog))))
if __name__=='__main__':main()
