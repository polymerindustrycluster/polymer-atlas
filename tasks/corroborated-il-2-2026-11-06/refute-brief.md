Final revised refute PR151 L11.45residueclusters=3Csites22evidence42holds. Codex3findingsfixed: explicitcuratedring1 MorrisresinproducerunderexistingSCHEMA§1precedent, backedby ITA120812polyethyleneresins andrawownMorrispageproductsLDPE/HDPE/LLDPE. OwnsupplementEVD270161quoteonlypagewords,nofederalaliases(07:20),rawreceipt/hashmorris_rawcheck.json;birthtiersstillCbecauseothermust-haveclaimsfederalC. SherwinMattesonstreet now21901CentralAvenue;originalfiledwholeaddressnotes;addressobservationlocalityonce. AlloriginalIDsunchanged,newEVD270161insideblock. validate0/check/known3/mutations/oldrows/replayPASS. Strict326unchanged68/797. Sourceonly3censusbelowplusnewownwitness;refuteringprecedentapplication/addressparser/citations/tierrestraint/IDs. ReturnAPPROVE|REFUTE. Previous3/21snapshot superseded.
SOURCE3
cluster_id,held_operator_id,held_operator_name,held_operator_status,successor,held_operator_domain,establishment_id,company_name,establishment_name,street,city,state,zip5,naics_code,industry_description,schema_2_2_signal,date_submitted,year_filing_for,prior_sites
LF-IL-00995,ORG-000033,LyondellBasell,active,,https://lyondellbasell.com,120812,Lyondellbasell,Lyondellbasell Morris Site,8805 North Tabler Rd,Morris,IL,60450,325211,Polyethylene resins manufacturing,P,2026-02-09,2025,[]
LF-IL-01004,ORG-000828,Evans Adhesive Corporation,active,,https://meridianadhesives.com/evans/,1266211,Evans Adhesives Prime Blend,Evans Adhesives Prime Blend,1300 Pratt Blvd Suite 200,Elk Grove Village,IL,60007,325520,"Pastes, adhesive, manufacturing",P,2026-02-03,2025,[]
LF-IL-01204,ORG-000132,The Sherwin-Williams Company,active,,https://www.sherwin-williams.com,347001,The Sherwin-Williams Company,USA IL Matteson Plant,"21901 Central Avenue, Matteson, IL 60443",Matteson,IL,60443,325510,Paint and Coating Manufacturing,P,2026-02-12,2025,"[{""site_id"": ""SITE-004937"", ""street"": ""5400 23RD AVE"", ""city"": ""Moline""}]"

OWN PROCESS RECEIPT
{
  "url": "https://www.lyondellbasell.com/en/locations/north-america/united-states/morris-site/",
  "quote": "The LyondellBasell Morris Plant produces Ethylene, Propylene, Low-Density Polyethylene, High-Density Polyethylene, and Linear Low-Density Polyethylene",
  "page": "build/l11-repair4-cache/frozen/0201921a87123e05c8c14766c17fe90b2d112e25ae7aadd2c831a0aa9c3f6baa.txt",
  "page_sha256": "0201921a87123e05c8c14766c17fe90b2d112e25ae7aadd2c831a0aa9c3f6baa",
  "raw": "yes",
  "fetched_at": "2026-11-06T11:33:51Z",
  "raw_sha256": "e410bc955b8ef9cad08bf3725423c0861f757010d498922436e3ea40e8372c66"
}

BUILDER
#!/usr/bin/env python3
"""Apply the curated Illinois provisional C packet; reruns compare then skip exact rows."""
import argparse,csv,json,sys,hashlib
from collections import Counter,defaultdict
from pathlib import Path
H=Path(__file__).resolve().parent; ROOT=H.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from shard_io import append_sorted
from atlas import street_key
DATE='2026-11-06'; BY='codex atlas-L11-corr-il-2'
SOURCE='https://www.osha.gov/sites/default/largefiles/ITA_300A_Summary_Data_2025_through_08-31-2026.csv'
def read(p):
 with open(p,newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');ap.add_argument('--data-dir',type=Path,default=ROOT/'data');a=ap.parse_args();data=a.data_dir
 cs={r['cluster_id']:r for r in read(H/'input.csv')};vs=read(H/'verdicts.csv')
 assert len(vs)==len(cs)==45 and len({v['cluster_id'] for v in vs})==45
 assert set(cs)=={v['cluster_id'] for v in vs}
 assert set(v['verdict'] for v in vs)<={'VERIFIED','REJECT','STILL_UNCERTAIN','DUPLICATE_OF'}
 ita={r['establishment_id']:r for r in read(ROOT/'tasks/osha-ita-2026-11-01/establishments.csv')}
 orgs={r['org_id']:r for p in data.glob('organizations_*.csv') for r in read(p)}
 oldsites=[r for p in data.glob('sites_*.csv') for r in read(p)]
 out=defaultdict(list);eid=270140;alloc=[]
 for idx,v in enumerate(v for v in vs if v['verdict']=='VERIFIED'):
  c=cs[v['cluster_id']];oid=v['held_org_id'];org=orgs[oid];assert org['status']=='active' and not org['successor_org_id']
  fed=[ita[s[4:]] for s in c['sources_with_ids'].split(';') if s.startswith('ITA:')]
  assert fed and all(r['state']=='IL' for r in fed)
  f=fed[0];street=v['street'];assert street;assert f['schema_2_2_signal']=='P' and f['naics_code'][:3] in ('326','325')
  assert all(r['naics_code']==f['naics_code'] and street_key(r['street'])==street_key(f['street']) for r in fed)
  assert f['street'] and f['city'] and f['zip5']
  sid=f'SITE-{19020+idx:06d}';assert 19020+idx<=19999
  # A blank held street at the same parent/locality is an unresolved duplicate, not a free address.
  for s in oldsites:
   if s['site_id']==sid:continue
   assert not (s['state']=='IL' and street_key(s['street_address'])==street_key(street)),(c['cluster_id'],s['site_id'])
   assert not (s['org_id']==oid and s['state']=='IL' and s['city'].casefold()==f['city'].casefold() and not s['street_address']),(c['cluster_id'],s['site_id'])
  ring=v['ring_primary'];assert ring in ['1','2']
  ref=SOURCE+'#establishment_ID='+f['establishment_id']
  notes=f"CY2025 ITA establishment_ID {f['establishment_id']}; date_submitted {f['date_submitted']}; packet observed 2026-11-01, reviewed {DATE}. {v['reason']} Filed street as received: {f['street']}"
  witness=json.loads((H/'morris_rawcheck.json').read_text()) if c['cluster_id']=='LF-IL-00995' else None
  site_sources=ref+('; '+witness['url'] if witness else '')
  out['sites_IL.csv'].append(dict(site_id=sid,org_id=oid,site_name=org['legal_name']+' - '+f['city'],site_type='manufacturing_plant',street_address=street,city=f['city'],state='IL',zip=f['zip5'],country='US',ring_primary=ring,naics_primary=f['naics_code'],naics_primary_source_type='government_filing',naics_confidence='medium',operating_status='unknown',sources=site_sources,verification_tier='C',last_verified=DATE,created_by=BY,notes=f"{c['cluster_id']}; Provisional C; federal birth claims, with an own process witness only where cited. Operating evidence is CY2025 filing, not a 2026 observation. {notes}"))
  claims={
   'existence':f"ITA establishment {f['establishment_id']}: {f['establishment_name']}",
   'address':f"{street}, {f['city']}, IL {f['zip5']}, US; county left unset",
   'scope':f"Provisional ring_primary {ring}, manufacturing_plant; employer-reported NAICS {f['naics_code']} (SCHEMA 2.2 Primary); federal-only C per CAMPAIGN convention",
   'code':f"naics_primary {f['naics_code']}; government_filing, medium confidence",
   'parent':f"org_id {oid} ({org['legal_name']}); filed company_name {f['company_name']}; establishment_name {f['establishment_name']}",
   'activity':f"Manufacturing filing for CY{f['year_filing_for']}; current status unknown; filing activity at that vintage",
   'liveness':f"CY{f['year_filing_for']} filing submitted {f['date_submitted']}; does not assert live operating check in 2026"}
  for claim,detail in claims.items():
   assert eid<=279999
   out['evidence_sites_IL.csv'].append(dict(evidence_id=f'EVD-{eid:06d}',record_table='sites',record_id=sid,claim_type=claim,claim_detail=detail,source_class='government_filing',source_ref=ref,observed_date='2026-11-01',tier_effect='supports_C',created_by=BY,notes=notes));eid+=1
  if c['cluster_id']=='LF-IL-00995':
   assert witness['url']=='https://www.lyondellbasell.com/en/locations/north-america/united-states/morris-site/';p=ROOT/witness['page'];assert witness['raw']=='yes' and hashlib.sha256(p.read_bytes()).hexdigest()==witness['page_sha256'];assert witness['quote'] in ' '.join(p.read_text().split())
   out['evidence_sites_IL.csv'].append(dict(evidence_id='EVD-270161',record_table='sites',record_id=sid,claim_type='scope',claim_detail='"'+witness['quote']+'"',source_class='own_site',source_ref=witness['url'],observed_date=DATE,tier_effect='supports_C',created_by=BY,notes='Process witness for settled SCHEMA§1resin-production classification only; other birth claims remain federalC. Raw fetched '+witness['fetched_at']))
  alloc.append(dict(cluster_id=c['cluster_id'],site_id=sid,org_id=oid,establishment_id=f['establishment_id']))
 # Preflight every file before any write; conflicting IDs fail closed.
 for name,rows in out.items():
  key='site_id' if name.startswith('sites_') else 'evidence_id'
  assert len(rows)==len({r[key] for r in rows}),'duplicate generated ID'
  pattern='sites_*.csv' if key=='site_id' else 'evidence_*.csv'
  for other in data.glob(pattern):
   if other.name!=name:
    have={r[key] for r in read(other)}
    assert not any(r[key] in have for r in rows),('cross-shard ID collision',other.name)
 pending={}
 for name,rows in out.items():
  p=data/name;old=read(p);key='site_id' if name.startswith('sites_') else 'evidence_id';by={r[key]:r for r in old};header=list(old[0])
  for r in rows:
   if r[key] in by: assert by[r[key]]=={k:r.get(k,'') for k in header},('conflicting ID',r[key])
  pending[name]=[r for r in rows if r[key] not in by]
 if a.apply:
  for name,rows in pending.items():
   if rows:append_sorted(data/name,rows,'site_id' if name.startswith('sites_') else 'evidence_id')
 with open(H/'allocations.csv','w') as f:
  w=csv.DictWriter(f,fieldnames=list(alloc[0]),lineterminator='\n');w.writeheader();w.writerows(alloc)
 print(json.dumps({'worked_IL_clusters':len(vs),'verdicts':dict(Counter(v['verdict'] for v in vs)),'sites_C':len(alloc),'organizations_created':0,'evidence_rows':sum(len(r) for k,r in out.items() if k.startswith('evidence_')),'pending_rows':{k:len(v) for k,v in pending.items()}}))
if __name__=='__main__':main()

CHECK
"""Reconciliation, existing-row preservation, idempotence and injected collision checks."""
import csv,hashlib,io,json,shutil,subprocess,sys,tempfile
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from atlas import load_tables,dedupe
from build import read
STATE='IL';N=45;CREATES=3;BASE='9489b607c19b450c195c2353944c61719105e1f9'
cs=read(H/'input.csv');vs=read(H/'verdicts.csv');alloc=read(H/'allocations.csv');prior=read(H/'prior-input.csv')
def frame_check(vs):
 assert len(cs)==len(vs)==len({v['cluster_id'] for v in vs})==N
 assert {c['cluster_id'] for c in cs}=={v['cluster_id'] for v in vs}
frame_check(vs)
try:frame_check(vs[:-1]+[vs[0]])
except AssertionError:pass
else:raise AssertionError('injected duplicate verdict escaped')
assert not ({r['cluster_id'] for r in prior}&{r['cluster_id'] for r in cs})
universe={r['cluster_id'] for r in read(ROOT/'tasks/lead-fusion-2026-11-01/clusters.csv') if r['state']==STATE and r['class']=='CORROBORATED'}
assert universe=={r['cluster_id'] for r in prior+cs}
assert len(alloc)==CREATES==len({r['site_id'] for r in alloc})
assert len(read(H/'blind-input.csv'))==CREATES
site_by={r['site_id']:r for r in read(ROOT/'data/sites_IL.csv')};ev_by={r['evidence_id']:r for r in read(ROOT/'data/evidence_sites_IL.csv')}
def review_cures(morris,matteson,address,scope):
 assert morris['ring_primary']=='1','resin-production precedent regressed'
 assert matteson['street_address']=='21901 Central Avenue','street contains locality'
 assert address['claim_detail'].count('Matteson')==1,'locality repeated'
 assert 'produces' in scope['claim_detail'] and 'Low-Density Polyethylene' in scope['claim_detail'],'own process witness absent'
review_cures(site_by['SITE-019020'],site_by['SITE-019022'],ev_by['EVD-270155'],ev_by['EVD-270161'])
for bad in ['ring','street']:
 m=site_by['SITE-019020'].copy();a=site_by['SITE-019022'].copy()
 if bad=='ring':m['ring_primary']='2'
 else:a['street_address']+=' , Matteson, IL 60443'
 try:review_cures(m,a,ev_by['EVD-270155'],ev_by['EVD-270161'])
 except AssertionError:pass
 else:raise AssertionError('original refute defect escaped')

paths=[ROOT/'data'/('sites_'+STATE+'.csv'),ROOT/'data'/('evidence_sites_'+STATE+'.csv')]
for p,key in zip(paths,['site_id','evidence_id']):
 old=list(csv.DictReader(io.StringIO(subprocess.check_output(['git','show',BASE+':data/'+p.name],cwd=ROOT,text=True))))
 now={r[key]:r for r in read(p)};assert all(now[r[key]]==r for r in old),'changed existing row'
before=[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
subprocess.run([sys.executable,str(H/'build.py'),'--apply'],check=True)
assert before==[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
# Inject the motivating defect in another evidence shard; the builder must fail before ANY write.
with tempfile.TemporaryDirectory() as d:
 data=Path(d)/'data';shutil.copytree(ROOT/'data',data)
 rows=read(paths[1]);new=next(r for r in rows if r['record_id']==alloc[0]['site_id'])
 target=data/'evidence_people.csv'
 with target.open('a',newline='') as f:csv.DictWriter(f,fieldnames=list(new),lineterminator='\n').writerow(new)
 hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.csv')}
 result=subprocess.run([sys.executable,str(H/'build.py'),'--apply','--data-dir',str(data)],capture_output=True,text=True)
 assert result.returncode!=0 and 'cross-shard ID collision' in result.stderr,result.stderr
 assert hashes=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.csv')}
T=load_tables(ROOT/'data')
for name,oid in [('Plastipak Packaging, Inc.','ORG-001033'),('Advanced Drainage Systems, Inc.','ORG-000651'),('Lacks Enterprises, Inc.','ORG-003325')]:
 assert oid in {h['id'] for s in dedupe(T,name=name)['steps'] for h in s['hits']}
rows=read(paths[0]);ids={r['site_id'] for r in alloc};strict=lambda r:r['operating_status'] in ['active','unknown'] and r['verification_tier'] in ['A','B','C'] and r['naics_primary'].startswith('326')
after=sum(strict(r) for r in rows);before=sum(strict(r) for r in rows if r['site_id'] not in ids)
assert before==68 and after==before
result=dict(state=STATE,worked_clusters=N,creates_C=CREATES,evidence_rows=7*CREATES+1,known_answers=3,blind_census_size=CREATES,before_strict326=before,after_strict326=after,qcew2023_private_establishments326=797,strict_share_percent=100*after/797,delta=0)
(H/'check_results.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS',result)

Clean-checkout blocker fix: no private snapshot needed. Run acquire_morris.py then check.py as documented README. Public browser-UA curl + shipped house HTML extractor validates normalized reviewed whole-page hash (clock/whitespace only), quote and address before writing ignored cache. Both original raw/full-text hashes retained in morris_rawcheck.json as dated vintage receipts; canonical3sites22EVD unchanged. Missing cache/hash/quote still fail closed; source drift requires review. Fresh clone before-fix failure reproduced, fresh clone after acquisition/replay and malformed witness controls required. Re-review this one acquisition blocker plus namedcheck/validator/rowloss; original data cures unchanged.
