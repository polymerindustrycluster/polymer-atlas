"""Recompute receipt, check complete diff, and exercise three injected defects."""
import csv,json,subprocess,copy
import build as b
P=b.P;R=b.R
base=b.read(P/'baseline.csv');res=b.responses()
counties={(r['STATEFP'],r['COUNTYFP']):r['COUNTYNAME'] for r in csv.DictReader((P/'counties.txt').open(),delimiter='|')}
props,holds,mm=b.products(base,res,counties)
assert props==b.read(P/'proposals.csv') and holds==b.read(P/'holds.csv') and mm==b.read(P/'county_mismatches.csv')
expected={(p['site_id'],p['field']):p['after'] for p in props}
actual={}
frame=[]
for path in sorted((R/'data').glob('sites_*.csv')):
 old=list(csv.DictReader(subprocess.check_output(['git','show',f'be2e6084d430f1e6f9de0f66289b1d3c2570e255:data/{path.name}'],text=True).splitlines()))
 new=b.read(path);assert len(old)==len(new)
 assert [r['site_id'] for r in old]==[r['site_id'] for r in new]
 for a,z in zip(old,new):
  if path.name!='sites_INTL.csv' and a['street_address'].strip():frame.append(dict(a,shard=path.name))
  for k in a:
   if a[k]!=z[k]:
    assert not a[k] and k in ('latitude','longitude','geocode_precision')
    actual[(a['site_id'],k)]=z[k]
assert frame==base and actual==expected
known=b.read(P/'known_answers.csv');assert len(known)==3
for k in known:
 a=next(x for x in base if x['site_id']==k['site_id']);assert res[a['site_id']][2]=='Match';assert b.distance(a,res[a['site_id']])<=200
# Missing response, duplicate frame ID, and malformed coordinates must fail.
for defect in range(3):
 bad=copy.deepcopy(res);bb=copy.deepcopy(base)
 if defect==0:bad.pop(next(iter(bad)))
 if defect==1:bb.append(bb[0])
 if defect==2:
  sid=next(s for s,r in bad.items() if r[2:4]==['Match','Exact']);bad[sid][5]='999,999'
 try:b.products(bb,bad,counties)
 except (AssertionError,ValueError):pass
 else:raise AssertionError(f'injected defect {defect} passed')
stats=json.loads((P/'summary.json').read_text())
assert stats['frame']==len(frame) and stats['changed_sites']==len({p['site_id'] for p in props}) and stats['county_mismatches']==len(mm) and stats['holds']==len(holds)
assert stats['fields']==dict(b.Counter(p['field'] for p in props))
assert stats['results']==dict(b.Counter('/'.join(r[2:4]) for r in res.values()))
assert stats['pic18_mismatches']==sum(r['pic18']=='True' for r in mm)
assert stats['tiers']==dict(b.Counter(next(x['verification_tier'] for x in base if x['site_id']==s) for s in {p['site_id'] for p in props}))
assert len(base)==5631 and sum(not r['latitude'] or not r['longitude'] for r in base)==2504 and sum(not r['zip'] for r in base)==473
print('PASS: full frame, response yield, all data fields, packets, counts, three known answers, three injected defects')
