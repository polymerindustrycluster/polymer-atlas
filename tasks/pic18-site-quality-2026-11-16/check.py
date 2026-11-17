"""Recompute census, enforce cell boundaries, replay, and three actual fault injections."""
from prep import *
import hashlib,io,tempfile,shutil
from build import plan,ALLOWED
from research import census
BASE=json.loads((H/'baseline.json').read_text())['base']
def old(p):return list(csv.DictReader(io.StringIO(subprocess.check_output(['git','show',BASE+':'+p],text=True))))
def check_federal(task=H):
 witnesses=read(task/'federal_witnesses.csv');assert len(witnesses)==3
 by={r['establishment_id']:r for r in witnesses};assert len(by)==len(witnesses)
 evidence=[e for e in read(task/'evidence.csv') if e['source_class']=='government_filing']
 assert len(evidence)==9 and {e['source_ref'].split('establishment_ID=')[1] for e in evidence}==set(by)
 source=R/'tasks/osha-ita-2026-11-01/establishments.csv'
 digest=hashlib.sha256(source.read_bytes()).hexdigest()
 originals={r['establishment_id']:r for r in read(source) if r['establishment_id'] in by}
 assert set(originals)==set(by)
 sites={r['site_id']:r for r in read(task/'input.csv')}
 orgs={r['org_id']:r for p in (R/'data').glob('organizations_*.csv') for r in read(p)}
 from atlas import name_key,street_key
 for key,w in by.items():
  assert w['source_file']==str(source.relative_to(R)) and w['source_sha256']==digest
  assert {k:v for k,v in w.items() if k not in {'source_file','source_sha256'}}==originals[key]
 for e in evidence:
  w=by[e['source_ref'].split('establishment_ID=')[1]];site=sites[e['record_id']];org=orgs[site['org_id']]
  assert name_key(w['company_name']) in {name_key(org['legal_name']),*(name_key(t) for t in org['trade_names'].split(';') if t)}
  assert street_key(w['street'])==street_key(site['street_address']) and w['state']==site['state'] and w['zip5']==site['zip'] and w['naics_code']==site['naics_primary']
  expected={'existence':w['company_name']+'; '+w['street']+', '+w['city']+', '+w['state']+' '+w['zip5'],
            'code':'NAICS '+w['naics_code']+'; government_filing; filed '+w['date_submitted'],
            'parent':'Filed operator '+w['company_name']+'; held operator '+org['legal_name']}
  assert e['claim_detail']==expected[e['claim_type']],('government claim differs from witness',e['evidence_id'])
 assert all({e['claim_type'] for e in evidence if e['record_id']==sid}=={'existence','code','parent'} for sid in {e['record_id'] for e in evidence})
 return len(witnesses),len(evidence)
def check():
 assert check_federal()==(3,9)
 ev=[r for p in (R/'data').glob('evidence_*.csv') for r in read(p) if not 379000<=int(r['evidence_id'][4:])<=380999]
 ranking=rank(old('data/sites_OH.csv'),ev)
 assert [{k:str(v) for k,v in x.items()} for x in ranking]==read(H/'ranking.csv') and len(ranking)==326
 assert [r['site_id'] for r in ranking[:80]]==[r['site_id'] for r in read(H/'input.csv')]
 v,w,e=census();assert [{k:str(z) for k,z in x.items()} for x in v]==read(H/'verdicts.csv') and w==read(H/'witnesses.csv') and e==read(H/'evidence.csv')
 assert len(v)==80 and len(w)==3 and len(e)==18 and sum(x['applied']=='no' for x in v)==77
 selected={x['site_id'] for x in w};newids={x['evidence_id'] for x in e}
 for p in (R/'data').glob('*.csv'):
  name='data/'+p.name
  if p.name=='sites_OH.csv':
   before={s['site_id']:s for s in old(name)};now=read(p);assert len(now)==len(before)
   for s in now:
    b=before[s['site_id']];diff={k for k in b if b[k]!=s[k]}
    assert diff<=ALLOWED and (bool(diff)==(s['site_id'] in selected))
  elif p.name=='evidence_sites_OH.csv':
   now=read(p);assert [r for r in now if r['evidence_id'] not in newids]==old(name)
   assert [r for r in now if r['evidence_id'] in newids]==sorted(e,key=lambda r:r['evidence_id'])
  else:assert p.read_bytes()==subprocess.check_output(['git','show',BASE+':'+name])
 sites,pending=plan();assert sites==read(R/'data/sites_OH.csv') and not pending
 with tempfile.TemporaryDirectory() as td:
  task=Path(td)
  for p in H.glob('*.csv'):shutil.copy2(p,task/p.name)
  for file,field,value in [('witnesses.csv','quote','fabricated zebra 7731'),('witnesses.csv','raw_sha256','0'*64),('verdicts.csv','site_id','SITE-999999')]:
   rows=read(task/file);rows[-1][field]=value;write(task/file,rows)
   try:plan(task=task)
   except (AssertionError,KeyError):pass
   else:raise AssertionError('defect escaped '+field)
   shutil.copy2(H/file,task/file)
 with tempfile.TemporaryDirectory() as td:
  task=Path(td)
  for p in H.glob('*.csv'):shutil.copy2(p,task/p.name)
  for file,field,value in [('federal_witnesses.csv','naics_code','999999'),('federal_witnesses.csv','source_sha256','0'*64),('evidence.csv','claim_detail','fabricated federal quote')]:
   rows=read(task/file)
   target=next(r for r in rows if file!='evidence.csv' or r['source_class']=='government_filing')
   target[field]=value;write(task/file,rows)
   try:check_federal(task)
   except (AssertionError,KeyError):pass
   else:raise AssertionError('federal defect escaped '+field)
   shutil.copy2(H/file,task/file)
 result=dict(federal_witness_rows=3,federal_claims_verified=9,federal_injected_defects_rejected=3,eligible_sites=len(ranking),worked_sites=len(v),promoted_sites=len(w),held_sites=len(v)-len(w),new_evidence=len(e),own_site_rows=sum(x['source_class']=='own_site' for x in e),government_rows=sum(x['source_class']=='government_filing' for x in e),injected_defects_rejected=3,replay_identical=True)
 (H/'check_results.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS',result)
if __name__=='__main__':check()
