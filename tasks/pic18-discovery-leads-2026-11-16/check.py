"""Reconcile the 80-lead frame, source bytes, packet coverage and replay."""
import copy,hashlib,json,re,tempfile,shutil
import build
from research import Text

def check(verdicts=None,witnesses=None):
 from frame import derive
 frame=build.read(build.P/'frame.csv'); derived,counts=derive();assert frame==derived,'merged rank frame'
 v=build.read(build.HERE/'verdicts.csv') if verdicts is None else verdicts
 assert len(frame)==len(v)==80,'input yield'
 assert {r['rank'] for r in frame}=={r['rank'] for r in v} and len({r['rank'] for r in v})==80,'rank coverage'
 assert [float(r['jobs']) for r in frame]==sorted((float(r['jobs']) for r in frame),reverse=True),'ranking'
 for name,digest in json.loads((build.HERE/'inputs.json').read_text()).items():assert hashlib.sha256((build.P/name).read_bytes()).hexdigest()==digest,'input drift'
 ws=build.read(build.HERE/'witnesses.csv') if witnesses is None else witnesses
 for w in ws:
  p=build.P/'verified'/w['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==w['sha256'],'source drift'
  t=Text();t.feed(p.read_text());words=lambda s:re.findall(r'\w+',s.lower());assert ' '.join(words(w['quote'])) in ' '.join(words(' '.join(t.parts))),'quote absent'
 geo=json.loads((build.P/'verified/mvp-county.json').read_text())['result']['addressMatches'];assert len(geo)==1 and geo[0]['matchedAddress']=='15005 ENTERPRISE WAY, MIDDLEFIELD, OH, 44062' and geo[0]['geographies']['Counties'][0]['NAME']=='Geauga County','county'
 es=build.read(build.HERE/'evidence_orgs.csv')+build.read(build.HERE/'evidence_sites.csv');assert not es,'withdrawn evidence'
 for w in json.loads((build.HERE/'overlap_witnesses.json').read_text()):
  p=build.P/'verified'/w['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==w['sha256'],'overlap source drift'
  t=Text();t.feed(p.read_text());assert w['quote'] in ' '.join(' '.join(t.parts).split()),'overlap quote absent'
 for tab,fn,key in [('organizations','creates_orgs.csv','org_id'),('sites','creates_sites.csv','site_id')]:
  for row in build.read(build.HERE/fn):assert {'existence','scope','address'}<={e['claim_type'] for e in es if e['record_table']==tab and e['record_id']==row[key]},'evidence coverage'
 assert all(r['disposition']=='held' for r in v),'all proposals held'
 assert next(r for r in v if r['rank']=='23')['verdict']=='STILL_UNCERTAIN'
 build.plan(build.ROOT/'data')
 return {x:sum(r['verdict']==x for r in v) for x in ['VERIFIED','DUPLICATE_OF','STILL_UNCERTAIN']}
if __name__=='__main__':
 print(check())
 v=build.read(build.HERE/'verdicts.csv');w=build.read(build.HERE/'witnesses.csv')
 for badv,badw in [(v[:-1],w),(v[:-1]+[v[0]],w),(v,[dict(x,quote='invented nonexisting factory quotation') if i==0 else x for i,x in enumerate(w)])]:
  try:check(badv,badw)
  except AssertionError:pass
  else:raise AssertionError('injected defect passed')
 with tempfile.TemporaryDirectory() as tmp:
  d=build.Path(tmp)/'data';shutil.copytree(build.ROOT/'data',d)
  for p,k,rows in build.plan(d):
   if rows:build.append_sorted(p,rows,k)
  hashes=lambda:{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in d.glob('*.csv')}
  before=hashes();assert all(not rows for _,_,rows in build.plan(d));assert hashes()==before
 print('PASS 80/80 input yield; 3 injected defects refused; zero data additions; county; byte-identical replay')

 # Prove the withdrawn builder refuses resurrection of a retired create.
 with tempfile.TemporaryDirectory() as tmp:
  packet=build.Path(tmp);original=build.HERE
  for p in original.glob('*.csv'):shutil.copyfile(p,packet/p.name)
  rows=build.read(build.ROOT/'data/organizations_OH.csv');bad=dict(rows[0],org_id='ORG-014100')
  with (packet/'creates_orgs.csv').open('w') as f:
   import csv
   w=csv.DictWriter(f,fieldnames=list(bad));w.writeheader();w.writerow(bad)
  build.HERE=packet
  try:
   try:build.plan(build.ROOT/'data')
   except AssertionError as e:assert str(e)=='withdrawn create must remain empty'
   else:raise AssertionError('retired create resurrection passed')
  finally:build.HERE=original
 print('PASS retired-create resurrection rejected')
