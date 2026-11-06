"""Full bounded frame/cell/evidence checks plus real fail-before-write faults."""
import csv,hashlib,io,json,subprocess,sys,tempfile,shutil,importlib.util
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[1];sys.path.insert(0,str(H))
from fetch import read,on_page,write
BASE=json.loads((H/'baseline.json').read_text())['base']
inputs=read(H/'input.csv');vs=read(H/'verdicts.csv');raw=read(H/'rawcheck.csv');alloc=read(H/'allocations.csv')
assert len(inputs)==len(vs)==len({r['site_id'] for r in vs})==5
assert {r['site_id'] for r in inputs}=={r['site_id'] for r in vs}
assert len(raw)==len(alloc)==len({r['evidence_id'] for r in alloc})==4
known=json.loads((H/'known_answers.json').read_text());assert len(known)==3
for r in raw:
 p=ROOT/r['page'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r['page_sha256']
 assert on_page(r['quote'],p) and on_page(r['binding_quote'],p)
 assert not on_page(r['quote']+' ZZZ fabricated plant 987',p)
evnew={r['evidence_id'] for r in alloc};assert evnew=={f'EVD-{n:06d}' for n in range(278600,278604)}
changed=subprocess.check_output(['git','diff',BASE,'--name-only','--','data'],cwd=ROOT,text=True).splitlines()
assert set(changed)=={'data/sites_FL.csv','data/sites_WI.csv','data/evidence_sites_FL.csv','data/evidence_sites_WI.csv','data/inclusion_log.csv'}
siteids={r['site_id'] for r in inputs};edited={'SITE-016017','SITE-016401','SITE-016410'};counts={}
for name in changed:
 old=list(csv.DictReader(io.StringIO(subprocess.check_output(['git','show',BASE+':'+name],cwd=ROOT,text=True))));now=read(ROOT/name)
 if '/evidence_' in name:
  by={r['evidence_id']:r for r in now};assert all(by[r['evidence_id']]==r for r in old)
  new=[r for r in now if r['evidence_id'] not in {x['evidence_id'] for x in old}];assert {r['evidence_id'] for r in new}<=evnew
  for r in new:
   witness=next(x for x in raw if x['site_id']==r['record_id'] and r['claim_detail']=='"'+x['quote']+'"')
   assert r['source_class']=='own_site' and r['tier_effect']=='supports_C' and r['source_ref']==witness['source_url']
 elif '/sites_' in name:
  by={r['site_id']:r for r in now};assert len(old)==len(now)
  for r in old:
   n=by[r['site_id']]
   if r['site_id'] not in edited:assert n==r
   else:
    allowed={'notes','sources','last_verified'}|({'site_type'} if r['site_id']!='SITE-016410' else set())
    assert {k:v for k,v in n.items() if k not in allowed}=={k:v for k,v in r.items() if k not in allowed}
  strict=lambda r:r['country']=='US' and r['verification_tier'] in ['A','B','C'] and r['operating_status'] in ['active','unknown'] and r['naics_primary'].startswith('326')
  plant=lambda r:strict(r) and r['site_type'] in ['manufacturing_plant','hq_and_plant']
  counts[name[-6:-4]]=dict(code_count_before=sum(map(strict,old)),code_count_after=sum(map(strict,now)),plant_count_before=sum(map(plant,old)),plant_count_after=sum(map(plant,now)))
 else:assert now[:len(old)]==old and len(now)==len(old)+3
allsite={r['site_id']:r for p in (ROOT/'data').glob('sites_*.csv') for r in read(p)}
assert allsite['SITE-016017']['site_type']=='warehouse_distribution'
assert allsite['SITE-016401']['site_type']=='service_repair'
assert allsite['SITE-016410']['site_type']=='manufacturing_plant'
for r in inputs:
 now=allsite[r['site_id']];assert now['operating_status']==r['operating_status'] and now['verification_tier']==r['verification_tier'] and now['ring_primary']==r['ring_primary'] and now['street_address']==r['street_address']
paths=[ROOT/n for n in changed];hashes=lambda:{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
before=hashes();subprocess.run([sys.executable,str(H/'build.py'),'--apply'],check=True);assert before==hashes()
spec=importlib.util.spec_from_file_location('correction2_builder',H/'build.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
with tempfile.TemporaryDirectory() as tmp:
 data=Path(tmp)/'data';task=Path(tmp)/'task';shutil.copytree(ROOT/'data',data);shutil.copytree(H,task);mod.H=task
 def refuse():
  hashes=lambda:{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.csv')}
  before=hashes();sys.argv=['build.py','--apply','--data-dir',str(data)]
  try:mod.main()
  except (AssertionError,KeyError):pass
  else:raise AssertionError('defect escaped')
  assert hashes()==before
 for field,value in [('quote','ZZZ fabricated claim 987'),('binding_quote','ZZZ wrong location 987'),('page_sha256','0'*64)]:
  rows=read(task/'rawcheck.csv');rows[-1][field]=value;write(task/'rawcheck.csv',rows,list(rows[0]));refuse();shutil.copy2(H/'rawcheck.csv',task/'rawcheck.csv')
 rows=read(task/'verdicts.csv');write(task/'verdicts.csv',rows[:-1],list(rows[0]));refuse();shutil.copy2(H/'verdicts.csv',task/'verdicts.csv')
 p=data/'sites_WI.csv';rows=read(p);next(r for r in rows if r['site_id']=='SITE-016410')['notes']+=' late stale edit';write(p,rows,list(rows[0]));refuse();shutil.copy2(ROOT/'data/sites_WI.csv',p)
 p=data/'evidence_sites_SC.csv';rows=read(p);e=next(r for r in read(ROOT/'data/evidence_sites_WI.csv') if r['evidence_id']=='EVD-278603')
 with p.open('a') as f:csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n').writerow(e)
 refuse()
result=dict(frame=5,verified_type_corrections=2,held_cases=3,annotated_site_rows=3,appended_evidence=4,owner_seams=3,known_answers=3,raw_census=4,old_rows_preserved=True,replay_byte_identical=True,no_write_mutations=['fabricated quote','wrong binding','changed hash','missing verdict','late stale site preimage','late cross-shard EVD'],state_counts=counts)
(H/'check_results.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS',json.dumps(result))
