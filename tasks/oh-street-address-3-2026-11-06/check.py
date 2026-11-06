"""Check real fill boundary/replay and fail-before-write on street and cross-shard ID collisions."""
import contextlib,hashlib,io,shutil,tempfile
from pathlib import Path
import build
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 root=build.ROOT;selected,verdicts,ev=build.plan()
 assert len(ev)==38,'frozen acceptance count changed; inspect before revising'
 with tempfile.TemporaryDirectory() as tmp:
  build.ROOT=Path(tmp);(build.ROOT/'data').mkdir()
  for p in (root/'data').glob('evidence_*.csv'):shutil.copyfile(p,build.ROOT/'data'/p.name)
  shutil.copyfile(root/'data/sites_OH.csv',build.ROOT/'data/sites_OH.csv')
  frozen={r['site_id']:r for r in selected};before=build.read(build.ROOT/'data/sites_OH.csv')
  for r in before:
   if r['site_id'] in frozen:
    old=frozen[r['site_id']]
    for k in r:r[k]=old[k]
  build.write(build.ROOT/'data/sites_OH.csv',before)
  p=build.ROOT/'data/evidence_sites_OH.csv'
  build.write(p,[r for r in build.read(p) if r['created_by']!='atlas-L2-oh-address-3'])
  with contextlib.redirect_stdout(io.StringIO()):build.run(apply=True)
  after=build.read(build.ROOT/'data/sites_OH.csv');changed=0
  assert len(before)==len(after)
  for a,b in zip(before,after):
   fields={k for k in a if a[k]!=b[k]}
   assert fields <= {'street_address','sources'},(a['site_id'],fields)
   if fields:
    changed+=1;assert not a['street_address'] and b['street_address'] and a['operating_status']=='active'
  assert changed==38
  paths=list((build.ROOT/'data').glob('*.csv'));hashes={p.name:digest(p) for p in paths}
  with contextlib.redirect_stdout(io.StringIO()):build.run(apply=True)
  assert hashes=={p.name:digest(p) for p in paths},'not byte-idempotent'
  target=next(r for a,r in zip(before,after) if not a['street_address'] and r['street_address'])
  original=target['street_address'];target['street_address']='999 WRONG ROAD';build.write(build.ROOT/'data/sites_OH.csv',after)
  hashes={p.name:digest(p) for p in paths}
  try:
   with contextlib.redirect_stdout(io.StringIO()):build.run(apply=True)
  except AssertionError:pass
  else:raise AssertionError('street conflict overwritten')
  assert hashes=={p.name:digest(p) for p in paths},'wrote before conflict refusal'
  target['street_address']=original;build.write(build.ROOT/'data/sites_OH.csv',after)
  foreign=build.ROOT/'data/evidence_sites_ZZ.csv';build.write(foreign,[ev[0]])
  paths=list((build.ROOT/'data').glob('*.csv'));hashes={p.name:digest(p) for p in paths}
  try:
   with contextlib.redirect_stdout(io.StringIO()):build.run(apply=True)
  except AssertionError:pass
  else:raise AssertionError('foreign-shard evidence collision accepted')
  assert hashes=={p.name:digest(p) for p in paths},'wrote before global collision refusal'
 build.ROOT=root
 print('PASS 38 fills; street/sources only; byte-idempotent; street and foreign-ID mutations rejected before canonical writes')
if __name__=='__main__':main()
