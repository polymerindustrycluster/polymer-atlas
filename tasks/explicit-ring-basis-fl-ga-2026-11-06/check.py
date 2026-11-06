#!/usr/bin/env python3
import csv,hashlib,json,runpy,subprocess,sys,tempfile,shutil
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[1]
sys.path.insert(0,str(H));from build import read
base=(H/'BASE').read_text().strip();audit=read(H/'audit.csv');assert len(audit)==len({r['site_id'] for r in audit})==11
cohort=[]
for state,task in [('FL','corroborated-fl-ga'),('GA','corroborated-ga')]:
 sites={r['site_id']:r for r in read(R/f'data/sites_{state}.csv')}
 a=read(R/f'tasks/{task}-2026-11-06/allocations.csv');cohort+=a
 expected={r['site_id'] for r in a if not sites[r['site_id']]['naics_primary'].startswith('326')}
 assert expected=={r['site_id'] for r in audit if r['state']==state}
 assert len(expected)==(4 if state=='FL' else 7)
 assert all(sites[k]['naics_primary'] in {'325510','325520'} and sites[k]['ring_primary']=='2' for k in expected)
 mapping=runpy.run_path(str(R/f'tasks/{task}-2026-11-06/build.py'))['ring_for_naics']
 for code,ring in [('326199','1'),('325510','2'),('325520','2'),('325991','2'),('325212','2')]:assert mapping(code)==ring
 for code in ['325211','325998','325999']:
  try:mapping(code);raise AssertionError('blanket fallback admitted')
  except ValueError:pass
assert len(cohort)==37 and len({r['site_id'] for r in cohort})==37
expected_ids={r['evidence_id'] for r in audit};new_ids=set()
for state in ['FL','GA']:
 for table in ['sites','evidence_sites']:
  fn=f'{table}_{state}.csv';old=list(csv.DictReader(subprocess.check_output(['git','show',base+':data/'+fn],text=True).splitlines()));key=list(old[0])[0];new={r[key]:r for r in read(R/'data'/fn)}
  assert all(new.get(r[key])==r for r in old),(fn,'existing row changed')
  added=set(new)-{r[key] for r in old}
  if table=='sites':assert not added
  else:
   new_ids|=added
   for k in added:
    r=new[k];a=next(a for a in audit if a['evidence_id']==k)
    assert r['claim_type']=='scope' and r['source_class']=='government_filing' and r['tier_effect']=='supports_C'
    assert a['naics_primary'] in r['claim_detail'] and a['establishment_id'] in r['source_ref']
assert new_ids==expected_ids and len(new_ids)==11
files=[R/f'data/evidence_sites_{s}.csv' for s in ['FL','GA']];before=[hashlib.sha256(p.read_bytes()).hexdigest() for p in files]
subprocess.run([sys.executable,str(H/'build.py'),'--apply'],check=True,capture_output=True);assert before==[hashlib.sha256(p.read_bytes()).hexdigest() for p in files]
with tempfile.TemporaryDirectory() as d:
 data=Path(d)/'data';shutil.copytree(R/'data',data);p=data/'evidence_organizations_OH.csv';rows=read(p);row=dict(rows[0]);row['evidence_id']='EVD-206000'
 with p.open('a') as f:
  w=csv.DictWriter(f,fieldnames=list(row),lineterminator='\n');w.writerow(row)
 before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.csv')}
 r=subprocess.run([sys.executable,str(H/'build.py'),'--data-dir',str(data),'--apply'],capture_output=True)
 assert r.returncode!=0 and b'conflicting ID' in r.stderr
 assert before=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.csv')}
print(json.dumps({'merged_create_census':37,'fallback_derived_FL':4,'fallback_derived_GA':7,'wrong_ring_values':0,'explicit_scope_rows_appended':11,'prior_rows_preserved':True,'ring_known_and_HOLD_controls':'PASS','replay':'PASS','cross_table_collision_no_write':'PASS'}))
