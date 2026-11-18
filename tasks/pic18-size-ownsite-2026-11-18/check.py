"""Checker: recomputes every count, verifies each fill against its stored page, and proves it fails on injected defects."""
import copy,csv,hashlib,io,json,re,subprocess,sys,tempfile
from unittest.mock import patch
from collections import Counter
from pathlib import Path
from build import *
import build as B

SCHEMA_BANDS=[(1,9,'1-9'),(10,49,'10-49'),(50,99,'50-99'),(100,249,'100-249'),(250,499,'250-499'),(500,999,'500-999'),(1000,4999,'1000-4999'),(5000,10**9,'5000+')]  # SCHEMA §4.4, independent of build.band
def schema_band(n):return next(b for lo,hi,b in SCHEMA_BANDS if lo<=n<=hi)
def norm(t):return re.sub(r'\s+',' ',t)
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT,text=True)
def at(rev,path):return list(csv.DictReader(io.StringIO(git('show',f'{rev}:{path}'))))
MANIFEST=[r for r in read(CORPUS/'manifest.csv')]

def check_packet(fills,evs,verdicts,frame,orgs,sites):
 vid=[v['org_id'] for v in verdicts]
 assert len(vid)==len(set(vid)),'duplicate verdict'
 assert {f['org_id'] for f in frame}<=set(vid),'frame ID with no verdict: %s'%sorted({f['org_id'] for f in frame}-set(vid))
 assert set(vid)<={f['org_id'] for f in frame},'verdict outside the frame'
 fo={f['org_id']:f['ohio_only'] for f in frame}
 for v in verdicts:
  assert v['ohio_only']==fo[v['org_id']],'ohio_only differs from frame'
  assert v['disposition'] in ('applied','held','no_claim','held_lead') and v['verdict']==('VERIFIED' if v['disposition']=='applied' else 'STILL_UNCERTAIN')
  if v['quote']:
   m=[r for r in MANIFEST if r['org_id']==v['org_id'] and r['url']==v['url'] and r['status']=='ok']
   assert m,'URL not in the stored corpus (rule 14): '+v['url']
   r=m[0];assert r['sha256']==v['raw_sha256'],'manifest sha256 differs from the verdict'
   if r['raw_file']:assert hashlib.sha256((CORPUS/r['raw_file']).read_bytes()).hexdigest()==r['sha256'],'stored page sha256 mismatch'
   else:assert v['disposition']!='applied','only holds may rest on pass-2 reader text (no raw file)'
   assert v['observed_date']==r['fetched_at'][:10]
   assert norm(v['quote']) in norm((CORPUS/r['text_file']).read_text(errors='replace')),'quote not in its stored page: '+v['org_id']
  if v['disposition']=='applied':
   assert v['ohio_only']=='true','applied verdict on a non-Ohio-only organization'
   n=int(v['stated_count']);assert str(n) in [x.replace(',','') for x in re.findall(r'\d[\d,]*',v['quote'])],'stated count not in the quote'
   assert B.count_kind(v['quote'],n),'no exact count or closed range: '+v['org_id']
   assert schema_band(n)==v['band'],'band does not contain the quoted count'
 applied={v['org_id']:v for v in verdicts if v['disposition']=='applied'}
 assert {f['record_id'] for f in fills}==set(applied) and len(fills)==len(applied),'fills differ from applied verdicts'
 ev={e['record_id']:e for e in evs};assert len(ev)==len(evs)==len(fills)
 ids=[e['evidence_id'] for e in evs];assert len(set(ids))==len(ids) and all(FIRST_ID<=int(i[4:])<=LAST_ID for i in ids),'evidence ID outside the block'
 for f in fills:
  oid=f['record_id'];v=applied[oid];o=orgs[oid]
  assert f['record_table']=='organizations' and f['field']==FIELD,'write outside the organization band cell'
  assert fo[oid]=='true' and o['hq_state']=='OH' and sites.get(oid) and all(s['state']=='OH' for s in sites[oid]),'write to a non-Ohio-only organization'
  assert f['old']=='' and o[FIELD] in ('',f['new']),'write to a non-blank cell'
  assert f['new']==schema_band(int(v['stated_count']))==v['band'],'band does not contain the quoted count'
  e=ev[oid];assert e['claim_type']=='size_band' and e['source_class']=='own_site' and e['tier_effect']==('supports_U' if o['verification_tier']=='U' else 'supports_B')
  assert v['page_date'] and v['page_date'] in e['notes'],'page date missing from evidence notes'
  assert e['evidence_id']==f['evidence_id'] and e['source_ref']==v['url'] and e['observed_date']==v['observed_date']
  assert e['claim_detail'].startswith(f'{FIELD}={f["new"]};') and f'"{v["quote"]}"' in e['claim_detail'],'evidence quote differs from the verdict quote'

def check_tree(base,fills,evs):
 """Diff the whole data tree against base: only the fills' cells and the appended evidence rows may differ."""
 changed=[p for p in git('diff','--name-only',base,'--','data').split()]
 now={r['org_id']:r[FIELD] for p in (ROOT/'data').glob('organizations_*.csv') for r in read(p)}
 state={now[f['record_id']]==f['new'] for f in fills}
 assert len(state)==1,'mixed applied/blank state'
 if state=={False}:
  assert not changed,'data differs from base before apply: %s'%changed;return 'pre-apply'
 want={f'data/organizations_{sh}.csv' for sh in {f['shard'] for f in fills}}|{f'data/evidence_organizations_{sh}.csv' for sh in {f['shard'] for f in fills}}
 assert set(changed)==want,'unexpected files changed: %s'%sorted(set(changed)^want)
 for sh in {f['shard'] for f in fills}:
  b=at(base,f'data/organizations_{sh}.csv');n=read(ROOT/f'data/organizations_{sh}.csv');mine={f['record_id']:f for f in fills}
  assert [r['org_id'] for r in b]==[r['org_id'] for r in n],'row loss, extra row or reorder'
  for x,y in zip(b,n):
   assert x['org_id']==y['org_id']
   for k in x:
    if x[k]!=y[k]:assert k==FIELD and x['org_id'] in mine and x[k]=='' and y[k]==mine[x['org_id']]['new'],f'unauthorized edit {x["org_id"]}.{k}'
  assert [r for r in read(ROOT/f'data/sites_{sh}.csv')]==at(base,f'data/sites_{sh}.csv') if (ROOT/f'data/sites_{sh}.csv').exists() else True,'site row touched'
  be=at(base,f'data/evidence_organizations_{sh}.csv');ne=read(ROOT/f'data/evidence_organizations_{sh}.csv')
  assert ne==sorted(be+[e for e in evs if e['record_id'] in mine],key=lambda e:e['evidence_id']),'evidence append mismatch'
 return 'applied'

def count_probes(verdicts,frame,orgs,sites):
 """Predicate probes, then the GLI promotion: it must fail for the missing exact count only, and pass when that predicate is disabled."""
 for q,n,want in [('We employ over 340 people and at most 500 people.',340,None),('We employ over 340 people and at most 500 people.',500,None),
  ('We employ over 340 people and produce fewer than 400 parts per day.',340,None),('We employ over 340 people and produce fewer than 400 parts per day.',400,None),
  ('We employ at least 60 people.',60,None),('We have 60+ employees.',60,None),('We employ nearly 60 people.',60,None),
  ('They currently employ about 60 people that process 15,000 tons.',60,'exact'),('We employ ~30 people that work 2 shifts/5 days per week.',30,'exact'),
  ('We employ ~30 people that work 2 shifts/5 days per week.',2,None),('Our team of 50 to 99 employees',50,'closed_range'),('Our team of 40 to 60 employees',40,None),('about 1,000 people',1000,'exact')]:
  got=B.count_kind(q,n);assert got==want,f'count_kind probe {q!r} n={n}: got {got}, want {want}'
 print('count probes: over/at most/fewer-than/at least/N+/nearly and wrong-noun counts all None; exact and closed-range forms accepted')
 V=copy.deepcopy(verdicts);g=next(v for v in V if v['org_id']=='ORG-000416')
 assert g['page_date'],'GLI keeps its real page date'
 g.update(disposition='applied',verdict='VERIFIED',stated_count='340',band='250-499')
 with patch.object(B,'count_kind',lambda q,n:'exact'):F,E,_=B.plan(V,check_existing=False)  # the full packet GLI would produce
 assert any(f['record_id']=='ORG-000416' for f in F)
 try:check_packet(F,E,V,frame,orgs,sites)
 except AssertionError as ex:
  assert 'no exact count or closed range' in str(ex) and 'ORG-000416' in str(ex),'rejected for a different reason: '+str(ex);print('injected defect rejected (GLI "over 340" promoted, real page date, own evidence row):',str(ex)[:60])
 else:raise AssertionError('silent pass: GLI over 340')
 with patch.object(B,'count_kind',lambda q,n:'exact'):check_packet(F,E,V,frame,orgs,sites)
 print('with the exact-count predicate disabled the same GLI packet passes: that predicate is the only reason for the rejection')

def builder_faults(base):
 """Run the real apply() in a temp tree seeded from the base shards, with a truncated input and a failure between writes."""
 names=['organizations_OH.csv','sites_OH.csv','evidence_organizations_OH.csv'];keep=(B.ROOT,B.D,B.os.replace)
 for case in ('truncated input shard','failure between shard writes'):
  with tempfile.TemporaryDirectory() as t:
   B.ROOT=Path(t);B.D=B.ROOT/'packet';B.D.mkdir();(B.D/'verdicts.csv').write_bytes((D/'verdicts.csv').read_bytes());(B.ROOT/'data').mkdir()
   try:
    for n in names:(B.ROOT/'data'/n).write_text(git('show',f'{base}:data/{n}'))
    org=B.ROOT/'data'/'organizations_OH.csv';rows=read(org)
    if case=='truncated input shard':write(org,rows[:-1],list(rows[0]))
    before={n:(B.ROOT/'data'/n).read_bytes() for n in names};fills,evs,_=B.plan()
    if case=='truncated input shard':
     try:B.apply(fills,evs,base)
     except AssertionError as ex:print('injected builder defect rejected:',case,'->',str(ex)[:60])
     else:raise AssertionError('silent pass: '+case)
     assert before=={n:(B.ROOT/'data'/n).read_bytes() for n in names} and not list((B.ROOT/'data').glob('*.stage')),'truncated input changed data or left a stage file'
    else:
     calls=[]
     def flaky(a,b):
      if str(b).endswith('.stage'):return keep[2](a,b)  # shard_io's own atomic staging
      calls.append(1)
      if len(calls)==2:raise OSError('interrupted between writes')
      return keep[2](a,b)
     try:
      with patch.object(B.os,'replace',flaky):B.apply(fills,evs,base)
     except OSError as ex:print('injected builder defect handled:',case,'->',ex)
     else:raise AssertionError('silent pass: '+case)
     now={r['org_id']:r[FIELD] for r in read(org)};ev={e['evidence_id'] for e in read(B.ROOT/'data'/'evidence_organizations_OH.csv')}
     assert all(now[f['record_id']]=='' for f in fills) and {e['evidence_id'] for e in evs}<=ev,'interrupted apply left a cell without its evidence or evidence missing'
     assert not list((B.ROOT/'data').glob('*.stage')),'stage files left behind'
     B.apply(fills,evs,base)  # a retry must succeed
     now={r['org_id']:r[FIELD] for r in read(org)};assert all(now[f['record_id']]==f['new'] for f in fills),'retry did not fill'
     print('retry after failure succeeded: cells filled, evidence present')
   finally:B.ROOT,B.D,B.os.replace=keep

def main():
 base=sys.argv[1] if len(sys.argv)>1 else git('merge-base','HEAD','origin/main').strip()
 fills=read(D/'fills.csv');evs=read(D/'evidence_rows.csv');verdicts=read(D/'verdicts.csv');frame=read(D/'frame.csv');orgs,shard,sites=load()
 # yield against an independent count of the input: the controller's frame file, and the stored corpus
 fj=json.loads((S/'briefs/w1118b/frames.json').read_text())['size_screen']
 assert [(x['org_id'],str(x['ohio_only']).lower()) for x in fj]==[(f['org_id'],f['ohio_only']) for f in frame],'frame.csv differs from the controller frame'
 assert len(frame)==37 and sum(f['ohio_only']=='true' for f in frame)==20
 assert all(any(r['org_id']==f['org_id'] and r['status']=='ok' for r in MANIFEST) for f in frame),'frame org with no stored page'
 check_packet(fills,evs,verdicts,frame,orgs,sites);mode=check_tree(base,fills,evs)
 c=Counter(v['disposition'] for v in verdicts)
 assert json.loads((D/'counts.json').read_text())==dict(frame=37,ohio_only=20,dispositions=dict(c),fills=len(fills),evidence_rows=len(evs),fills_by_band=dict(Counter(f['new'] for f in fills)))
 assert sum(c.values())==37 and c['applied']==len(fills)
 assert sum(1 for v in verdicts if v['ohio_only']=='false')==17 and not any(v['disposition']=='applied' for v in verdicts if v['ohio_only']=='false')
 # injected defects: every one must be rejected
 def inject(name,fn):
  F,E,V,O,SI=map(copy.deepcopy,(fills,evs,verdicts,orgs,sites));fn(F,E,V,O,SI)
  try:check_packet(F,E,V,frame,O,SI)
  except AssertionError as ex:print('injected defect rejected:',name,'->',str(ex)[:70]);return
  raise AssertionError('silent pass: '+name)
 def wrong_band(F,E,V,O,SI):F[0]['new']='100-249'
 def wrong_band_both(F,E,V,O,SI):F[0]['new']=V[0]['band']='100-249'
 def non_ohio_only(F,E,V,O,SI):
  v=next(v for v in V if v['org_id']=='ORG-000030');v.update(disposition='applied',verdict='VERIFIED',stated_count='600',band='500-999')
  F.append(dict(F[0],record_id='ORG-000030',new='500-999',old='',evidence_id='EVD-396399'));E.append(dict(E[0],record_id='ORG-000030',evidence_id='EVD-396399'))

 def sites_not_ohio(F,E,V,O,SI):SI[F[0]['record_id']][0]['state']='PA'
 def nonblank_cell(F,E,V,O,SI):O[F[0]['record_id']][FIELD]='1-9'
 def site_write(F,E,V,O,SI):F[0].update(record_table='sites',field='employee_band_site')
 def wrong_role(F,E,V,O,SI):
  v=next(v for v in V if v['org_id']=='ORG-000564');v.update(stated_count='2',band='1-9');F[0].update(new='1-9') if F[0]['record_id']=='ORG-000564' else None;next(f for f in F if f['record_id']=='ORG-000564').update(new='1-9')
 def quote_missing(F,E,V,O,SI):V[0]['quote']='We employ forty people in a building not on this page'
 def frame_no_verdict(F,E,V,O,SI):V.pop(5)
 for n,fn in [('band not containing the count',wrong_band),('band and verdict both moved off the count',wrong_band_both),('write to non-Ohio-only org',non_ohio_only),('write to org with a non-Ohio site',sites_not_ohio),('write to non-blank cell',nonblank_cell),('write to a site row',site_write),('count with the wrong role (two shifts read as 2 employees)',wrong_role),('quote not in stored page',quote_missing),('frame ID without a verdict',frame_no_verdict)]:inject(n,fn)
 builder_faults(base);count_probes(verdicts,frame,orgs,sites)
 if mode=='applied':
  snap={p:p.read_bytes() for p in (ROOT/'data').glob('*OH.csv')}
  subprocess.run([sys.executable,str(D/'build.py'),'--apply'],check=True,stdout=subprocess.DEVNULL)
  assert all(p.read_bytes()==b for p,b in snap.items()),'apply not idempotent'
 print(f'PASS ({mode}): {len(fills)} fills, {len(evs)} evidence rows, 37 frame verdicts, 12 injected defects rejected')
if __name__=='__main__':main()
