"""Recompute frame + verdict counts, re-verify witnesses, prove street-only diff and replay, and fail on injected defects."""
import contextlib,hashlib,io,re,shutil,subprocess,tempfile
from collections import Counter
from pathlib import Path
import build,scout
from scout import read,write,ROOT,TASK
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT,text=True).strip()
BASE=git('merge-base','HEAD','origin/main')
def at(path):
 import csv;return list(csv.DictReader(io.StringIO(subprocess.check_output(['git','show',f'{BASE}:{path}'],cwd=ROOT,text=True))))
def street_only(base,after,ids):
 assert len(base)==len(after),'row count changed'
 for a,b in zip(base,after):
  assert a['site_id']==b['site_id'],'row order changed'
  d={k for k in a if a[k]!=b[k]}
  if a['site_id'] in ids:assert d=={'street_address'} and a['street_address']=='','non-street or non-blank edit '+a['site_id']+str(d)
  else:assert not d,'unexpected edit '+a['site_id']
KNOWN_DIFF=['SITE-000132','SITE-000518','SITE-000603','SITE-000889','SITE-000983','SITE-001122','SITE-001137','SITE-001606','SITE-001940']  # 7 Route streets, 1 one-digit number, 1 frame false positive (README)
def reconcile(frame_ids,ind):
 assert set(ind)<=set(frame_ids),'independent count has sites outside the frame'
 d=sorted(set(frame_ids)^set(ind));assert d==KNOWN_DIFF,'frame vs independent count differ unexpectedly: %s'%d
 assert len(frame_ids)==len(ind)+len(KNOWN_DIFF),'count arithmetic';return d
def live_equals(live,base,verd):
 exp={v['site_id']:v['street'] for v in verd if v['verdict']=='VERIFIED'};assert len(live)==len(base)
 for a,b in zip(base,live):
  e=dict(a)
  if a['site_id'] in exp:e['street_address']=exp[a['site_id']]
  assert e==b,'live site table != expected for '+a['site_id']
def digests(root):return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((root/'data').glob('*.csv'))}
def expect_fail(label,fn):
 try:fn()
 except AssertionError as e:return str(e)
 raise SystemExit('DEFECT SURVIVED: '+label)
def main():
 base=at('data/sites_OH.csv');fr=scout.frame_rows(base);ind=scout.independent_count(base)
 frame=read(TASK/'frame.csv');verd=read(TASK/'verdicts.csv')
 assert [r['site_id'] for r in frame]==[s['site_id'] for s in fr]==[v['site_id'] for v in verd],'frame != recomputed frame / verdicts'
 diff=reconcile([s['site_id'] for s in fr],ind)
 verified=[v for v in verd if v['verdict']=='VERIFIED'];holds=Counter(v['hold_class'] for v in verd if v['verdict']!='VERIFIED')
 assert all(v['verdict'] in ('VERIFIED','STILL_UNCERTAIN','REJECT') for v in verd)
 assert len(verified)+sum(holds.values())==len(verd)==len(fr) and all(v['settling_fact'] for v in verd if v['verdict']!='VERIFIED')
 ids={v['site_id'] for v in verified};_,ev=build.plan()  # plan() re-verifies raw bytes, sha256, quotes, city, labels, collisions
 assert len(ev)==len(ids)
 live=read(ROOT/'data/sites_OH.csv');live_equals(live,base,verd)
 held={e['evidence_id']:e for e in read(ROOT/'data/evidence_sites_OH.csv')};base_ev={e['evidence_id'] for e in at('data/evidence_sites_OH.csv')}
 mine={i for i in held if i.startswith('EVD-395')};assert mine=={e['evidence_id'] for e in ev} and all(held[e['evidence_id']]==e for e in ev) and not mine&base_ev and all(395000<=int(i[4:])<=395999 for i in mine),'evidence block'
 assert all(i in held for i in base_ev),'evidence row lost'
 with tempfile.TemporaryDirectory() as d:
  r=Path(d);(r/'data').mkdir()
  for p in (ROOT/'data').glob('evidence_*.csv'):shutil.copyfile(p,r/'data'/p.name)
  ep=r/'data/evidence_sites_OH.csv';write(ep,[e for e in read(ep) if not e['evidence_id'].startswith('EVD-395')],list(held[next(iter(held))]))
  write(r/'data/sites_OH.csv',base);build.DATA=r/'data'
  with contextlib.redirect_stdout(io.StringIO()):build.run(True,backup=False)
  after=read(r/'data/sites_OH.csv');street_only(base,after,ids);live_equals(after,base,verd);h1=digests(r)
  assert h1['sites_OH.csv']==hashlib.sha256((ROOT/'data/sites_OH.csv').read_bytes()).hexdigest() and h1['evidence_sites_OH.csv']==hashlib.sha256((ROOT/'data/evidence_sites_OH.csv').read_bytes()).hexdigest(),'replay != live tables'
  with contextlib.redirect_stdout(io.StringIO()):build.run(True,backup=False)
  assert h1==digests(r),'replay changed bytes'
  # injected defects, each must fail
  own=next(v for v in verified if v['source_class']=='own_site');fed=next(v for v in verified if v['source_class']!='own_site')
  def mut(k,val,row):
   m=[dict(v) for v in verd];x=next(y for y in m if y['site_id']==row['site_id']);x[k]=val;return m
  msgs={}
  msgs['wrong street']=expect_fail('wrong street',lambda:build.plan(mut('street','999 Wrong Street',own)))
  msgs['altered quote']=expect_fail('altered quote',lambda:build.plan(mut('quote',own['quote']+' invented words',own)))
  msgs['mailing-labeled address']=expect_fail('mailing',lambda:build.plan(mut('quote','Mailing Address: '+own['quote'],own)))
  msgs['city differs']=expect_fail('city',lambda:build.plan(mut('quote',own['quote'].replace(own['city'],'Elsewhere'),own)))
  msgs['bad sha']=expect_fail('sha',lambda:build.plan(mut('sha256','0'*64,fed)))
  rows=[dict(s) for s in after];x=next(s for s in rows if s['site_id']==own['site_id']);x['zip']='00000'
  msgs['non-street column edit']=expect_fail('column',lambda:street_only(base,rows,ids))
  rows=[dict(s) for s in after];x=next(s for s in rows if s['site_id']==own['site_id']);x['street_address']='1 Overwritten St'
  assert x['street_address']!=own['street'];rows2=[dict(s) for s in base];y=next(s for s in rows2 if s['site_id']==own['site_id']);y['street_address']='1 Old St'
  msgs['overwrite of non-blank street']=expect_fail('overwrite',lambda:street_only(rows2,rows,ids))
  lv=[dict(s) for s in live];x=next(s for s in lv if s['site_id']==own['site_id']);x['street_address']=''
  msgs['missing street edit in live table']=expect_fail('missing edit',lambda:live_equals(lv,base,verd))
  msgs['frame count off by one']=expect_fail('frame off by one',lambda:reconcile([s['site_id'] for s in fr][1:],ind))
  assert h1==digests(r),'writes during rejection'
  build.DATA=ROOT/'data'
 print('PASS frame=%d (independent regex count %d; symmetric difference %s) verified=%d holds=%d %s; street-only diff, byte replay, %d injected defects rejected'%(len(fr),len(ind),diff,len(verified),sum(holds.values()),dict(holds),len(msgs)))
if __name__=='__main__':main()
