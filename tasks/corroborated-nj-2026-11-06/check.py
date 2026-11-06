#!/usr/bin/env python3
"""Named census/source/ID/T3 boundary check; --negative-controls proves collision preflight fails before writes."""
import argparse,csv,hashlib,importlib.util,io,json,shutil,subprocess,tempfile,sys
from collections import Counter
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[1]
def read(p):
 with open(p,newline='') as f:return list(csv.DictReader(f))
def census(source,vs):
 assert len(source)==len(vs)==91 and len({r['cluster_id'] for r in vs})==91
 assert Counter(r['cluster_id'] for r in source)==Counter(r['cluster_id'] for r in vs)
 assert all(r['verdict'] in {'VERIFIED','REJECT','STILL_UNCERTAIN','DUPLICATE_OF'} and r['reason'] for r in vs)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--negative-controls',action='store_true');a=ap.parse_args()
 source=[r for r in read(ROOT/'tasks/lead-fusion-2026-11-01/clusters.csv') if r['class']=='CORROBORATED' and r['state'] in ('NJ',)]
 vs=read(H/'verdicts.csv');census(source,vs)
 assert {r['cluster_id']:r for r in source}=={r['cluster_id']:r for r in read(H/'input.csv')}
 for bad in [vs[:-1],vs+[vs[0]],vs[:-1]+[vs[0]]]:
  try:census(source,bad)
  except AssertionError:pass
  else:raise AssertionError('census mutation escaped')
 alloc=[r for st in ['NJ'] for r in read(H/f'allocations_{st}.csv')]
 assert Counter(r['cluster_id'] for r in alloc)==Counter(r['cluster_id'] for r in vs if r['verdict']=='VERIFIED')
 ita={r['establishment_id']:r for r in read(ROOT/'tasks/osha-ita-2026-11-01/establishments.csv')}
 sites={r['site_id']:r for p in (ROOT/'data').glob('sites_*.csv') for r in read(p)}
 sys.path.insert(0,str(H));from prep import same_street
 assert not same_street('','') and not same_street('#6 Capper Drive','')
 assert same_street('126 Glassmaster Road','126 Glassmaster Rd')
 for r in vs:
  if r['verdict']=='DUPLICATE_OF':
   c=next(c for c in source if c['cluster_id']==r['cluster_id']);site=sites[r['duplicate_of']]
   assert site['state']==c['state'] and same_street(site['street_address'],c['street']),'invalid duplicate street link'
  else:assert not r['duplicate_of'],'non-duplicate target'
 ev=[r for p in (ROOT/'data').glob('evidence_*.csv') for r in read(p)]
 lane=[r for r in ev if r['created_by']=='atlas-L3-corroborated-nj']
 assert len(alloc)==5 and len(lane)==36,(len(alloc),len(lane))
 for r in alloc:
  s=sites[r['site_id']];f=ita[r['establishment_id']]
  assert (s['org_id'],s['verification_tier'],s['operating_status'],s['country'])==(r['org_id'],'C','unknown','US')
  for col,k in [('street_address','street'),('city','city'),('state','state'),('zip','zip5'),('naics_primary','naics_code')]:assert s[col]==f[k],(r['site_id'],col)
  claims=[e for e in lane if e['record_id']==r['site_id']]
  assert {e['claim_type'] for e in claims}=={'existence','address','scope','code','parent','activity','liveness'}
  assert all(e['source_class']=='government_filing' and e['tier_effect']=='supports_C' and e['observed_date']=='2026-11-01' and e['source_ref'].endswith('#establishment_ID='+f['establishment_id']) for e in claims)
 def registrant(e):
  matches=[ita[r['establishment_id']] for r in alloc if r['org_id']==e['record_id'] and e['source_ref'].endswith('#establishment_ID='+r['establishment_id'])]
  assert len(matches)==1 and e['source_class']=='government_filing' and e['tier_effect']=='supports_A' and e['claim_type']=='existence' and e['observed_date']=='2026-11-01'
  assert e['claim_detail']=='Federal registrant trade_names: '+matches[0]['company_name'].strip(),'registrant source binding'
 aliases=[e for e in lane if e['record_table']=='organizations']
 for e in aliases:registrant(e)
 assert len(aliases)==1
 try:registrant({**aliases[0],'claim_detail':aliases[0]['claim_detail']+' fabricated alias'})
 except AssertionError:pass
 else:raise AssertionError('false registrant alias escaped')
 for pat,key in [('sites_*.csv','site_id'),('organizations_*.csv','org_id'),('evidence_*.csv','evidence_id')]:
  ids=[r[key] for p in (ROOT/'data').glob(pat) for r in read(p)];assert len(ids)==len(set(ids)),pat
 for e in lane:assert 309000<=int(e['evidence_id'][4:])<=309999
 # Compare against the same pinned main used for branch creation, never a moving remote ref.
 base=json.loads((H/'baseline.json').read_text())['commit'];expected_aliases={}
 orgs={r['org_id']:r for p in (ROOT/'data').glob('organizations_*.csv') for r in read(p)}
 for r in alloc:
  oid=r['org_id'];name=ita[r['establishment_id']]['company_name'].strip()
  if name!=orgs[oid]['legal_name']:expected_aliases.setdefault(oid,set()).add(name)
 paths=subprocess.check_output(['git','diff','--name-only',base,'--','data/'],cwd=ROOT,text=True).splitlines();added_sites=[];added_evidence=[];alias_edits=set()
 for path in paths:
  old=list(csv.DictReader(io.StringIO(subprocess.check_output(['git','show',base+':'+path],cwd=ROOT,text=True))));now=read(ROOT/path);key=list(old[0])[0];by={r[key]:r for r in now};assert len(by)==len(now)
  for r in old:
   assert r[key] in by,('old row lost',path,r[key])
   new=by[r[key]];diff={k for k in r if r[k]!=new[k]}
   if diff:
    assert key=='org_id' and r[key] in expected_aliases and diff=={'trade_names'},('old row changed',path,r[key],diff)
    parts=lambda x:{v.strip() for v in x.split(';') if v.strip()}
    assert parts(new['trade_names'])==parts(r['trade_names'])|expected_aliases[r[key]];alias_edits.add(r[key])
  oldids={r[key] for r in old};fresh=[r for r in now if r[key] not in oldids]
  assert all(r['created_by']=='atlas-L3-corroborated-nj' for r in fresh),('foreign create',path)
  if key=='site_id':added_sites.extend(r['site_id'] for r in fresh)
  elif key=='evidence_id':added_evidence.extend(r['evidence_id'] for r in fresh)
  else:assert not fresh,('unexpected create class',path)
 assert set(added_sites)=={r['site_id'] for r in alloc} and set(added_evidence)=={r['evidence_id'] for r in lane}
 spec=importlib.util.spec_from_file_location('q',ROOT/'scripts/build_qcew_denominators.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 nums=m.atlas_numerators(str(ROOT));before=json.loads((H/'qcew-before.json').read_text());after={}
 for st,b in before.items():
  delta=sum(sites[r['site_id']]['naics_primary'].startswith('326') for r in alloc if r['state']==st)
  now=nums[(st,'326')][1];assert delta>0 and now-b['strict']==delta,(st,delta,now,b)
  after[st]={**b,'strict_after':now,'added_326':delta,'share_before':b['strict']/b['qcew'],'share_after':now/b['qcew']}
 (H/'qcew-after.json').write_text(json.dumps(after,indent=2)+'\n')
 if a.negative_controls:
  with tempfile.TemporaryDirectory() as d:
   data=Path(d)/'data';shutil.copytree(ROOT/'data',data)
   for wrong,key,target in [(data/'sites_AL.csv','site_id',alloc[0]['site_id']),(data/'evidence_sites_AL.csv','evidence_id',lane[0]['evidence_id'])]:
    original=wrong.read_bytes();rows=read(wrong);injected={**rows[0],key:target}
    if key=='site_id':injected['street_address']='999 COLLISION ROAD'
    with wrong.open('a',newline='') as f:csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n').writerow(injected)
    before_bytes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.csv')}
    run=subprocess.run([sys.executable,str(H/'build.py'),'--state',alloc[0]['state'],'--data-dir',str(data),'--apply'],capture_output=True,text=True)
    assert run.returncode and 'conflicting ID' in run.stderr,run.stderr
    assert before_bytes=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.csv')},'collision wrote data'
    wrong.write_bytes(original)
   wrong=data/'organizations_AL.csv';original=wrong.read_bytes();rows=read(wrong)
   other=next(r for r in rows if r['status']=='active' and not r['successor_org_id'])
   other['trade_names']=(other['trade_names']+'; '+ita[alloc[0]['establishment_id']]['company_name']).strip('; ')
   with wrong.open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
   before_bytes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.csv')}
   run=subprocess.run([sys.executable,str(H/'build.py'),'--state','NJ','--data-dir',str(data),'--apply'],capture_output=True,text=True)
   assert run.returncode and 'ambiguous filed operator' in run.stderr,run.stderr
   assert before_bytes=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.csv')}
   wrong.write_bytes(original)
 print('PASS exact91 census;3 census defects caught;5C sites/36 evidence bound to ITA; unique/reserved IDs; T3 reconciled',json.dumps(after))
 if a.negative_controls:print('PASS injected SITE/EVD collisions and ambiguous filed operator refused before any data write')
if __name__=='__main__':main()
