"""Recompute the lead union, source yield, column boundary and replay; inject real defects."""
import csv,io,subprocess,sqlite3,tempfile,shutil,hashlib,contextlib
from pathlib import Path
import build
from regions import PIC18

def at(path):return list(csv.DictReader(io.StringIO(subprocess.check_output(['git','show','ef32b5b:'+path],text=True))))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 root=build.ROOT;frame=build.read(build.TASK/'frame.csv');proposals,ev=build.plan();base=at('data/sites_OH.csv');eligible={s['site_id'] for s in base if s['operating_status']=='active' and s['verification_tier'] in ('A','B','C') and s['county'] in PIC18 and not s['street_address']}
 ppp={r['site_id'] for r in build.read(build.S/'ppp-loan-scout/matches.csv')}
 db=sqlite3.connect(build.S/'sam-entity-scout/sam.sqlite');sam={r[0] for r in db.execute("select record_id from matches where class='name+city'")}
 assert {s['site_id'] for s in frame}==eligible&(ppp|sam),'independent input yield mismatch'
 assert len(build.read(build.TASK/'leads.csv'))==254
 assert len(eligible)==419 and len(frame)==173 and len(ev)==23 and len(proposals)-len(ev)==150
 applied={e['record_id'] for e in ev};assert len(applied)==len(ev)
 assert sum(e['source_class']=='own_site' for e in ev)==13
 assert sum(e['source_class']=='government_filing' for e in ev)==10
 for r in proposals:
  assert r['disposition'] in ('applied','held') and (r['site_id'] in applied)==(r['disposition']=='applied')
 with tempfile.TemporaryDirectory() as d:
  build.ROOT=Path(d);(build.ROOT/'data').mkdir()
  for p in (root/'data').glob('evidence_*.csv'):shutil.copyfile(p,build.ROOT/'data'/p.name)
  build.write(build.ROOT/'data/sites_OH.csv',base)
  ep=build.ROOT/'data/evidence_sites_OH.csv';build.write(ep,[e for e in build.read(ep) if e['created_by']!=build.CREATOR])
  with contextlib.redirect_stdout(io.StringIO()):build.run(True)
  after=build.read(build.ROOT/'data/sites_OH.csv');assert len(after)==len(base)
  for a,b in zip(base,after):
   diff={k for k in a if a[k]!=b[k]};assert diff==({'street_address'} if a['site_id'] in applied else set()),(a['site_id'],diff)
  paths=list((build.ROOT/'data').glob('*.csv'));hashes={p.name:digest(p) for p in paths}
  with contextlib.redirect_stdout(io.StringIO()):build.run(True)
  assert hashes=={p.name:digest(p) for p in paths},'replay changed bytes'
  original=build.read
  # Each mutation reaches the real planner before any canonical write.
  for field,value in [('street','999 Wrong Street'),('quote','invented quote never on source'),('fresh_sha256','0'*64)]:
   mutated=[dict(r) for r in proposals];r=next(r for r in mutated if r['disposition']=='applied' and r['source_class']=='own_site');r[field]=value
   build.read=lambda p:mutated if Path(p)==build.TASK/'proposals.csv' else original(p)
   try:
    with contextlib.redirect_stdout(io.StringIO()):build.run(True)
   except AssertionError:pass
   else:raise AssertionError('mutation survived: '+field)
   finally:build.read=original
   assert hashes=={p.name:digest(p) for p in paths},'write before rejection'
 build.ROOT=root
 # The actual integrated tree must match the replay at the cell/evidence boundary.
 live={s['site_id']:s for s in build.read(root/'data/sites_OH.csv')}
 for s in base:
  expected=dict(s)
  if s['site_id'] in applied:expected['street_address']=next(r['street'] for r in proposals if r['site_id']==s['site_id'])
  assert live[s['site_id']]==expected
 held={e['evidence_id']:e for e in build.read(root/'data/evidence_sites_OH.csv')}
 assert all(held[e['evidence_id']]==e for e in ev)
 print('PASS: 419 eligible sites; 173 lead-bearing sites; 23 street fills (13 own-site, 10 federal); 150 holds; exact street-only diff; byte-idempotent; 3 defects rejected before writes.')
if __name__=='__main__':main()
