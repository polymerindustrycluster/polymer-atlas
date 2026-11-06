"""Frozen-frame reconciliation, raw binding, append-only/replay, no-write mutation gates."""
import csv,hashlib,importlib.util,io,json,shutil,subprocess,sys,tempfile
from collections import Counter
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[1];sys.path.insert(0,str(H))
from fetch import read,on_page
BASE='18a8f8aae6a8a2cd9a71a2d68e6b0e8d856c4589'
leads=list(csv.DictReader(io.StringIO(subprocess.check_output(['git','show','a012caa:tasks/evidence-reverify-archive-oh-pa-2026-11-06/repair_leads.csv'],cwd=ROOT,text=True))))
expected=[r for r in leads if r['judgment'] in ['NOT_SUPPORTED','WRONG_PAGE','PARTIAL']]
assert read(H/'input.csv')==expected and len(expected)==269
prior=list(csv.DictReader(io.StringIO(subprocess.check_output(['git','show','agent/codex/evidence-repair-3:tasks/evidence-repair-3-2026-11-06/input.csv'],cwd=ROOT,text=True))))
assert not ({r['evidence_id'] for r in prior}&{r['evidence_id'] for r in expected})
vs=read(H/'verdicts.csv');alloc=read(H/'allocations.csv');raw=read(H/'rawcheck.csv')
assert len(vs)==269==len({r['evidence_id'] for r in vs})
assert {r['evidence_id'] for r in vs}=={r['evidence_id'] for r in expected}
assert Counter(r['verdict'] for r in vs)=={'VERIFIED':62,'STILL_UNCERTAIN':207}
assert len(raw)==len(alloc)==62==len({r['evidence_id'] for r in alloc})
for r in raw:
 p=ROOT/r['page'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r['page_sha256'];assert on_page(r['quote'],p)
 assert not on_page(r['quote']+' ZZZ ABSENT INJECTED DEFECT 999',p)
assert len(json.loads((H/'known_answers.json').read_text()))==3
# Every pre-existing canonical row, including all weak evidence, is preserved against the branch's main baseline.
changed=subprocess.check_output(['git','diff',BASE,'--name-only','--','data'],cwd=ROOT,text=True).splitlines()
assert len(changed)==6 and all('/evidence_' in n for n in changed)
for n in changed:
 old=list(csv.DictReader(io.StringIO(subprocess.check_output(['git','show',BASE+':'+n],cwd=ROOT,text=True))))
 now={r['evidence_id']:r for r in read(ROOT/n)};assert all(now[r['evidence_id']]==r for r in old)
paths=[ROOT/n for n in changed];before=[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
subprocess.run([sys.executable,str(H/'build.py'),'--apply'],check=True)
assert before==[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
# Use isolated data and a task copy; mutations must reject BEFORE touching any canonical file.
spec=importlib.util.spec_from_file_location('repair_builder',H/'build.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
with tempfile.TemporaryDirectory() as d:
 data=Path(d)/'data';shutil.copytree(ROOT/'data',data);task=Path(d)/'task';shutil.copytree(H,task);mod.H=task
 def write(name,rows):
  with (task/name).open('w') as f:
   w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
 def refuse():
  hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.csv')};sys.argv=['build.py','--apply','--data-dir',str(data)]
  try:mod.main()
  except (AssertionError,KeyError):pass
  else:raise AssertionError('mutation escaped')
  assert hashes=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.csv')}
 selected=read(task/'selected.csv');selected[0]['quote']+=' ZZZ absent';write('selected.csv',selected);refuse()
 shutil.copy2(H/'selected.csv',task/'selected.csv')
 receipt=read(task/'rawcheck.csv');receipt[0]['page_sha256']='0'*64;write('rawcheck.csv',receipt);refuse()
 shutil.copy2(H/'rawcheck.csv',task/'rawcheck.csv')
 target=data/'evidence_people.csv';new=read(paths[0])[0].copy();new['evidence_id']=alloc[0]['evidence_id']
 with target.open('a',newline='') as f:csv.DictWriter(f,fieldnames=list(new),lineterminator='\n').writerow(new)
 refuse()
result=dict(frame=269,repaired_evidence=62,holds=207,shards=6,known_answers=3,raw_checks=62,mutation_checks=['fabricated quote','changed frozen source hash','global duplicate EVD'],existing_rows_unchanged=True,replay_byte_identical=True)
(H/'check_results.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS',result)
