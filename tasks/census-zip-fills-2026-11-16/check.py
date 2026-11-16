"""Check ZIP-only diff independently against retained Census responses."""
import copy,csv,json,hashlib,subprocess
import build as b
tables=b.baseline();res=b.responses()
original=[r for n,rows in tables.items() if n!='sites_INTL.csv' for r in rows if r['street_address'].strip()]
assert len(original)==len(res)==5631
expected={r['site_id']:res[r['site_id']][4].rsplit(',',1)[1].strip() for r in original if not r['zip'].strip() and res[r['site_id']][2:4]==['Match','Exact']}
def validate(new):
 actual={}
 for name,old in tables.items():
  assert len(old)==len(new[name])
  for a,z in zip(old,new[name]):
   assert a.keys()==z.keys() and a['site_id']==z['site_id']
   for k in a:
    if a[k]!=z[k]:
     assert k=='zip' and not a[k].strip(), 'nonblank or other field changed'
     actual[a['site_id']]=z[k]
 assert actual==expected, 'Exact ZIP diff'
new={n:b.read(b.R/'data'/n) for n in tables};validate(new)
known=b.read(b.P/'known_answers.csv');assert len(known)==3
for k in known:
 r=next(r for r in original if r['site_id']==k['site_id']);assert r['zip']==k['zip']==res[r['site_id']][4].rsplit(',',1)[1].strip();assert res[r['site_id']][2:4]==['Match','Exact']
for defect in range(3):
 bad=copy.deepcopy(new)
 if defect==0:
  r=next(r for rows in bad.values() for r in rows if r['site_id'] in expected);r['zip']='00000' if r['zip']!='00000' else '99999'
 if defect==1:
  sid=known[0]['site_id'];next(r for rows in bad.values() for r in rows if r['site_id']==sid)['zip']='00000'
 if defect==2:next(iter(bad.values()))[0]['city']='injected city'
 try:validate(bad)
 except AssertionError:pass
 else:raise AssertionError(f'injected defect {defect} passed')
props=b.read(b.P/'proposals.csv');holds=b.read(b.P/'holds.csv')
assert {r['site_id']:r['zip'] for r in props}==expected and len(props)==len(expected)
assert all(r['disposition']=='applied' for r in props) and all(r['disposition']=='held' for r in holds)
assert {r['site_id'] for r in holds}=={r['site_id'] for r in original if not r['zip'].strip()}-set(expected)
stats=json.loads((b.P/'summary.json').read_text());assert stats==dict(frame=len(original),fills=len(expected),holds=len(holds),tiers=dict(b.Counter(r['verification_tier'] for r in original if r['site_id'] in expected)))
assert len(expected)==348 and len(holds)==125 and sum(not r['zip'].strip() for r in original)==473
for p in b.P.glob('response_*.csv'):assert p.read_bytes()==(b.R/'tasks/census-geocode-2026-11-16'/p.name).read_bytes()
before={n:hashlib.sha256((b.R/'data'/n).read_bytes()).hexdigest() for n in tables}
subprocess.run(['python3',str(b.P/'build.py')],check=True,capture_output=True)
assert before=={n:hashlib.sha256((b.R/'data'/n).read_bytes()).hexdigest() for n in tables}
print('PASS: 5631 inputs, 348 Exact ZIP fills, 125 holds; ZIP-only full diff; 3 known answers; 3 rejected defects; raw copies; idempotence')
