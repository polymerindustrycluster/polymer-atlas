"""Frozen frame, five-claim coverage, preservation/replay and fail-before-write checks."""
import csv,hashlib,importlib.util,io,json,shutil,subprocess,sys,tempfile
from collections import Counter
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[1];sys.path.insert(0,str(H))
from fetch import read,on_page,write
BASE=json.loads((H/'baseline.json').read_text())['base']
FRAME=json.loads((H/'baseline.json').read_text())['frozen_base']
inputs=read(H/'input.csv');vs=read(H/'verdicts.csv');alloc=read(H/'allocations.csv');raw=read(H/'rawcheck.csv')
assert len(inputs)==len(vs)==len({r['site_id'] for r in vs})==35
assert {r['site_id'] for r in inputs}=={r['site_id'] for r in vs}
assert Counter(r['verdict'] for r in vs)=={'VERIFIED':8,'STILL_UNCERTAIN':27}
ids={r['site_id'] for r in vs if r['verdict']=='VERIFIED'};newids={r['evidence_id'] for r in alloc}
assert len(ids)==len(raw)==8 and len(alloc)==len(newids)==40
known=json.loads((H/'known_answers.json').read_text());assert len(known)==3
for k in known:
 p=ROOT/k['page'];assert hashlib.sha256(p.read_bytes()).hexdigest()==k['page_sha256']
 assert on_page(k['expected'],p) and not on_page('ZZZ fabricated polymer plant 987',p)
for r in raw:
 p=ROOT/r['page'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r['page_sha256']
 assert all(on_page(r[k],p) for k in ['quote','city_quote','binding_quote'])
 assert not on_page(r['quote']+' ZZZ absent invented assertion 987',p)
ev=[r for p in (ROOT/'data').glob('evidence_*.csv') for r in read(p) if r['evidence_id'] in newids]
assert len(ev)==40
for sid in ids:
 rows=[r for r in ev if r['record_id']==sid]
 assert {r['claim_type'] for r in rows}=={'existence','address','scope','code','parent'} and all(r['tier_effect']=='supports_B' for r in rows)
 own=[r for r in rows if r['source_class']=='own_site'];assert len(own)==1 and own[0]['claim_type']=='scope'
 r=next(r for r in raw if r['site_id']==sid);assert own[0]['claim_detail']=='"'+r['quote']+'"'
# Freeze creation classes from the merged first packets, excluding retired slots and later PRs.
expected=set()
for task in ['corroborated-mi-il-2026-11-06','corroborated-il-2026-11-06']:
 rows=list(csv.DictReader(io.StringIO(subprocess.check_output(['git','show',FRAME+':tasks/'+task+'/allocations.csv'],cwd=ROOT,text=True))))
 made={r['site_id'] for r in rows};assert len(rows)==len(made)==(17 if 'mi-il' in task else 18)
 assert not(expected & made)
 expected|=made
assert expected=={r['site_id'] for r in inputs}
changed=subprocess.check_output(['git','diff',BASE,'--name-only','--','data'],cwd=ROOT,text=True).splitlines()
allowed={'data/sites_MI.csv','data/sites_IL.csv','data/evidence_sites_MI.csv','data/evidence_sites_IL.csv'}
# Other merged-main work since the frozen frame is allowed, but this pass changes four shards only.
result={}
for state,den in [('MI',819),('IL',797)]:
 n='data/sites_'+state+'.csv';old=list(csv.DictReader(io.StringIO(subprocess.check_output(['git','show',BASE+':'+n],cwd=ROOT,text=True))))
 now={r['site_id']:r for r in read(ROOT/n)}
 for r in old:
  if r['site_id'] not in ids:assert now[r['site_id']]==r
  else:
   assert {k:v for k,v in now[r['site_id']].items() if k not in ['verification_tier','sources','notes','last_verified']}=={k:v for k,v in r.items() if k not in ['verification_tier','sources','notes','last_verified']}
   assert now[r['site_id']]['verification_tier']=='B'
 en='data/evidence_sites_'+state+'.csv';olde=list(csv.DictReader(io.StringIO(subprocess.check_output(['git','show',BASE+':'+en],cwd=ROOT,text=True))))
 nowe={r['evidence_id']:r for r in read(ROOT/en)};assert all(nowe[r['evidence_id']]==r for r in olde)
 strict=lambda r:r['country']=='US' and r['operating_status'] in ['active','unknown'] and r['verification_tier'] in ['A','B','C'] and r['naics_primary'].startswith('326')
 before=sum(map(strict,old));after=sum(map(strict,now.values()));assert before==after
 result[state]=dict(strict_before=before,strict_after=after,qcew_2023_private_326=den,before_percent=100*before/den,after_percent=100*after/den)
paths=[ROOT/n for n in allowed];hashes=lambda:{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
before=hashes();subprocess.run([sys.executable,str(H/'build.py'),'--apply'],check=True);assert before==hashes()
spec=importlib.util.spec_from_file_location('quality_builder',H/'build.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
with tempfile.TemporaryDirectory() as tmp:
 data=Path(tmp)/'data';task=Path(tmp)/'task';shutil.copytree(ROOT/'data',data);shutil.copytree(H,task);mod.H=task
 def refuse():
  hashes=lambda:{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.csv')}
  before=hashes();sys.argv=['build.py','--apply','--data-dir',str(data)]
  try:mod.main()
  except (AssertionError,KeyError):pass
  else:raise AssertionError('injected defect escaped')
  assert hashes()==before
 selected=read(task/'selected.csv');selected[0]['quote']='';write(task/'selected.csv',selected,list(selected[0]));write(task/'rawcheck.csv',selected,list(selected[0]));refuse()
 shutil.copy2(H/'selected.csv',task/'selected.csv');shutil.copy2(H/'rawcheck.csv',task/'rawcheck.csv')
 receipt=read(task/'rawcheck.csv');receipt[0]['page_sha256']='0'*64;write(task/'rawcheck.csv',receipt,list(receipt[0]));write(task/'selected.csv',receipt,list(receipt[0]));refuse()
 shutil.copy2(H/'selected.csv',task/'selected.csv');shutil.copy2(H/'rawcheck.csv',task/'rawcheck.csv')
 selected=read(task/'selected.csv');selected[0]['city_quote']='ZZZ invented city';write(task/'selected.csv',selected,list(selected[0]));write(task/'rawcheck.csv',selected,list(selected[0]));refuse()
 shutil.copy2(H/'selected.csv',task/'selected.csv');shutil.copy2(H/'rawcheck.csv',task/'rawcheck.csv')
 target=data/'evidence_people.csv';row=ev[0].copy()
 with target.open() as f:header=next(csv.reader(f))
 with target.open('a') as f:csv.DictWriter(f,fieldnames=header,lineterminator='\n').writerow(row)
 refuse()
result.update(frame=35,promoted_sites_B=8,holds=27,new_evidence=40,known_answers=3,raw_census=8,old_evidence_preserved=True,replay_byte_identical=True,mutation_checks=['missing own scope','changed source hash','invented city','global EVD collision'])
(H/'check_results.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS',json.dumps(result))
