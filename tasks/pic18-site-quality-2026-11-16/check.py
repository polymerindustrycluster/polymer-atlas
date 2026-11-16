"""Recompute census, enforce cell boundaries, replay, and three actual fault injections."""
from prep import *
import hashlib,io,tempfile,shutil
from build import plan,ALLOWED
from research import census
BASE=json.loads((H/'baseline.json').read_text())['base']
def old(p):return list(csv.DictReader(io.StringIO(subprocess.check_output(['git','show',BASE+':'+p],text=True))))
def check():
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
 result=dict(eligible_sites=len(ranking),worked_sites=len(v),promoted_sites=len(w),held_sites=len(v)-len(w),new_evidence=len(e),own_site_rows=sum(x['source_class']=='own_site' for x in e),government_rows=sum(x['source_class']=='government_filing' for x in e),injected_defects_rejected=3,replay_identical=True)
 (H/'check_results.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS',result)
if __name__=='__main__':check()
