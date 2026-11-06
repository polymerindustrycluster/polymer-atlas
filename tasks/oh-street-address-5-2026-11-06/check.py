"""Check real fill boundary/replay and fail-before-write on street and cross-shard ID collisions."""
import contextlib,hashlib,io,shutil,tempfile
from pathlib import Path
import build
from fetch import mailing_posture
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 root=build.ROOT;selected,verdicts,ev=build.plan()
 quote='1293 South Main Street Akron, Ohio 44301'
 for prefix in ('You can reach us by mail at this address: ','Mailing address: ','Postal address: '):assert mailing_posture(prefix+quote,quote)=='mailing-only context'
 assert not mailing_posture('Email us. Physical address: '+quote,quote)
 cases=[
  ('Elyria','Street: 710 Taylor Street, Elyria, OH 44035','710 Taylor Street'),
  ('Struthers','Street: 276 State Street, Struthers (company contact page). Converted from a verdict','276 State Street'),
  ('Avon','Street: 34910 Commerce Way (address per FDA establishment registration; verified). FDA FEI 123','34910 Commerce Way'),
  ('Youngstown','Street (per Grok): 3745 Hendricks Rd. county UNVERIFIED — Grok county_check=TRUE','3745 Hendricks Rd'),
  ('Ashland','Street (per Grok): 2040 Cellar Drive. Address confirmed 2026-10-29: source','2040 Cellar Drive'),
  ('Avon Lake','Street: 33490 Pin Oak Pkwy, Avon Lake. Co-located with distinct company','33490 Pin Oak Pkwy'),
  ('Test City','Street: 191 American Blvd, Suite 100, Test City (company contact page)','191 American Blvd, Suite 100')]
 for city,notes,expected in cases:
  leads=build.note_streets(dict(city=city,notes=notes));assert leads and build.key(leads[-1])==build.key(expected),(leads,expected)
 assert build.key(cases[-1][2])!=build.key('191 American Blvd Suite 300'),'unit distinction erased'
 for sid in ('SITE-001316','SITE-001317','SITE-001416','SITE-001417','SITE-001418'):
  row=next(v for v in verdicts if v['site_id']==sid);assert row['verdict']=='STILL_UNCERTAIN' and 'site-specific binding' in row['reason'],sid
 for sid in ('SITE-001419','SITE-001524','SITE-001579'):
  assert next(v for v in verdicts if v['site_id']==sid)['verdict']=='STILL_UNCERTAIN',sid

 assert len(ev)==25,'frozen source-adjudication yield changed; inspect before revising'
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
  build.write(p,[r for r in build.read(p) if r['created_by']!='atlas-L2-oh-address-5'])
  with contextlib.redirect_stdout(io.StringIO()):build.run(apply=True)
  after=build.read(build.ROOT/'data/sites_OH.csv');changed=0
  assert len(before)==len(after)
  for a,b in zip(before,after):
   fields={k for k in a if a[k]!=b[k]}
   assert fields <= {'street_address','sources'},(a['site_id'],fields)
   if fields:
    changed+=1;assert not a['street_address'] and b['street_address'] and a['operating_status']=='active'
  assert changed==25
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
 print(f'PASS {len(ev)} fills; street/sources only; byte-idempotent; street and foreign-ID mutations rejected before canonical writes')
if __name__=='__main__':main()
