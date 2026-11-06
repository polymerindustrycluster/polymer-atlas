"""Full correction census, baseline preservation and adversarial no-write gates."""
import csv,hashlib,importlib.util,io,json,shutil,subprocess,sys,tempfile
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[1];sys.path.insert(0,str(H))
from fetch import read,write,on_page
BASE=json.loads((H/'baseline.json').read_text())['application_base']
raw=read(H/'rawcheck.csv');alloc=read(H/'allocations.csv');verdicts=read(H/'verdicts.csv')
assert len(raw)==len(alloc)==9 and len(verdicts)==6==len({r['record_id'] for r in verdicts})
assert {r['record_id'] for r in verdicts}=={r['site_id'] for r in read(H/'input.csv')}|{'ORG-007011'}
known=json.loads((H/'known_answers.json').read_text());assert len(known)==3 and {r['key'] for r in known}=={'GILKEY_TYPE','DART_TYPE','YOKO_OUTCOME'}
for r in raw:
 p=ROOT/r['page'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r['page_sha256'];assert on_page(r['quote'],p)
 assert not on_page(r['quote']+' ZZZ invented source words 987',p)
sites={r['site_id']:r for p in (ROOT/'data').glob('sites_*.csv') for r in read(p)}
assert sites['SITE-019018']['site_type']=='sales_office' and sites['SITE-019018']['ring_primary']=='1'
assert sites['SITE-014003']['site_type']=='warehouse_distribution' and sites['SITE-014003']['ring_primary']=='1' and sites['SITE-014003']['zip']=='92880'
assert sites['SITE-019009']['street_address']=='320 Craig Place'
assert sites['SITE-018014']['operating_status']=='unknown'
assert sites['SITE-012023']['operating_status']=='closed'
assert 'closure_confirmed_by=2026-02-19' in sites['SITE-012023']['notes'] and 'actual day UNKNOWN' in sites['SITE-012023']['notes']
org=next(r for p in (ROOT/'data').glob('organizations_*.csv') for r in read(p) if r['org_id']=='ORG-007011')
assert org['monitor_watch']=='true'
original=next(r for r in read(H/'organizations_input.csv') if r['org_id']=='ORG-007011')
assert {k:v for k,v in org.items() if k not in ['monitor_watch','notes']}=={k:original[k] for k in org if k not in ['monitor_watch','notes']}
newids={r['evidence_id'] for r in alloc};assert len(newids)==9 and all(278500<=int(e[4:])<=279999 for e in newids)
evidence=[r for p in (ROOT/'data').glob('evidence_*.csv') for r in read(p) if r['evidence_id'] in newids];assert len(evidence)==9
for e in evidence:
 r=next(r for r in raw if r['record_id']==e['record_id'] and e['claim_detail']=='"'+r['quote']+'"')
 assert e['source_ref']==r['source_url']
# Compare every changed canonical table to the integration baseline, never just the selected sample.
changed=subprocess.check_output(['git','diff',BASE,'--name-only','--','data'],cwd=ROOT,text=True).splitlines()
assert len(changed)==11
expected={r['site_id']:r for r in read(H/'input.csv')};watch='ORG-007011';count={}
for name in changed:
 old=list(csv.DictReader(io.StringIO(subprocess.check_output(['git','show',BASE+':'+name],cwd=ROOT,text=True))));now=read(ROOT/name)
 if '/evidence_' in name:
  by={r['evidence_id']:r for r in now};assert all(by[r['evidence_id']]==r for r in old);assert set(by)-{r['evidence_id'] for r in old}<=newids
 elif '/sites_' in name:
  by={r['site_id']:r for r in now};assert len(old)==len(now)
  for r in old:
   n=by[r['site_id']]
   if r['site_id'] not in expected:assert n==r
   else:
    allowed={'sources','notes','last_verified'}
    allowed|={'site_type'} if r['site_id'] in ['SITE-019018','SITE-014003'] else {'street_address'} if r['site_id']=='SITE-019009' else {'operating_status'} if r['site_id']=='SITE-012023' else set()
    assert {k:v for k,v in n.items() if k not in allowed}=={k:v for k,v in r.items() if k not in allowed}
  st=name[-6:-4];strict=lambda r:r['country']=='US' and r['verification_tier'] in ['A','B','C'] and r['operating_status'] in ['active','unknown'] and r['naics_primary'].startswith('326')
  plants=lambda r:strict(r) and r['site_type'] in ['manufacturing_plant','hq_and_plant']
  count[st]=dict(code_count_before=sum(map(strict,old)),code_count_after=sum(map(strict,now)),manufacturing_type_count_before=sum(map(plants,old)),manufacturing_type_count_after=sum(map(plants,now)))
 elif '/organizations_' in name:
  by={r['org_id']:r for r in now};assert len(old)==len(now);assert all(by[r['org_id']]==r for r in old if r['org_id']!=watch)
 elif name=='data/inclusion_log.csv':
  assert now[:len(old)]==old and len(now)==len(old)+2 and all('HOLD ring/scope' in r['decision'] for r in now[len(old):])
 else:raise AssertionError('unowned canonical file '+name)
paths=[ROOT/n for n in changed];hashes=lambda:{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
before=hashes();subprocess.run([sys.executable,str(H/'build.py'),'--apply'],check=True);assert hashes()==before
spec=importlib.util.spec_from_file_location('correction_builder',H/'build.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
with tempfile.TemporaryDirectory() as tmp:
 data=Path(tmp)/'data';task=Path(tmp)/'task';shutil.copytree(ROOT/'data',data);shutil.copytree(H,task);mod.H=task
 def refuse():
  hashes=lambda:{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.csv')}
  before=hashes();sys.argv=['build.py','--apply','--data-dir',str(data)]
  try:mod.main()
  except (AssertionError,KeyError):pass
  else:raise AssertionError('mutation escaped')
  assert hashes()==before
 for mode in ['missing outcome','WARN date as outcome','source hash','invented quote']:
  rows=read(task/'rawcheck.csv')
  if mode=='missing outcome':rows=[r for r in rows if r['key']!='YOKO_OUTCOME']
  elif mode=='WARN date as outcome':next(r for r in rows if r['key']=='YOKO_OUTCOME')['source_date']='2025-04-19'
  elif mode=='source hash':rows[0]['page_sha256']='0'*64
  else:rows[0]['quote']='ZZZ invented source words 987'
  write(task/'rawcheck.csv',rows,list(rows[0]));refuse();shutil.copy2(H/'rawcheck.csv',task/'rawcheck.csv')
 p=data/'evidence_people.csv';row=evidence[0].copy()
 with p.open() as f:header=next(csv.reader(f))
 with p.open('a') as f:csv.DictWriter(f,fieldnames=header,lineterminator='\n').writerow(row)
 refuse()
result=dict(sites=5,organization_watch_flags=1,new_evidence=9,inclusion_seams=2,physical_type_changes=2,street_corrections=1,closures_confirmed_by_date=1,status_unchanged_EastJordan=True,known_answers=3,raw_census=9,replay_byte_identical=True,old_evidence_preserved=True,no_write_mutations=5,state_counts=count)
(H/'check_results.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS',json.dumps(result))
