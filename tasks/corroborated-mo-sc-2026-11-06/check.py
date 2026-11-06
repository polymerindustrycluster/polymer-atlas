#!/usr/bin/env python3
"""Named census/source/ID/T3 boundary check; --negative-controls proves collision preflight fails before writes."""
import argparse,csv,hashlib,importlib.util,io,json,shutil,subprocess,tempfile,sys
from collections import Counter
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[1]
def read(p):
 with open(p,newline='') as f:return list(csv.DictReader(f))
def census(source,vs):
 assert len(source)==len(vs)==143 and len({r['cluster_id'] for r in vs})==143
 assert Counter(r['cluster_id'] for r in source)==Counter(r['cluster_id'] for r in vs)
 assert all(r['verdict'] in {'VERIFIED','REJECT','STILL_UNCERTAIN','DUPLICATE_OF'} and r['reason'] for r in vs)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--negative-controls',action='store_true');a=ap.parse_args()
 source=[r for r in read(ROOT/'tasks/lead-fusion-2026-11-01/clusters.csv') if r['class']=='CORROBORATED' and r['state'] in ('MO','SC')]
 vs=read(H/'verdicts.csv');census(source,vs)
 assert {r['cluster_id']:r for r in source}=={r['cluster_id']:r for r in read(H/'input.csv')}
 for bad in [vs[:-1],vs+[vs[0]],vs[:-1]+[vs[0]]]:
  try:census(source,bad)
  except AssertionError:pass
  else:raise AssertionError('census mutation escaped')
 alloc=[r for st in ['MO','SC'] for r in read(H/f'allocations_{st}.csv')]
 assert Counter(r['cluster_id'] for r in alloc)==Counter(r['cluster_id'] for r in vs if r['verdict']=='VERIFIED')
 ita={r['establishment_id']:r for r in read(ROOT/'tasks/osha-ita-2026-11-01/establishments.csv')}
 sites={r['site_id']:r for p in (ROOT/'data').glob('sites_*.csv') for r in read(p)}
 ev=[r for p in (ROOT/'data').glob('evidence_*.csv') for r in read(p)]
 lane=[r for r in ev if r['created_by']=='atlas-L3-corroborated-mo-sc']
 assert len(alloc)==10 and len(lane)==74,(len(alloc),len(lane))
 for r in alloc:
  s=sites[r['site_id']];f=ita[r['establishment_id']]
  assert (s['org_id'],s['verification_tier'],s['operating_status'],s['country'])==(r['org_id'],'C','unknown','US')
  for col,k in [('street_address','street'),('city','city'),('state','state'),('zip','zip5'),('naics_primary','naics_code')]:assert s[col]==f[k],(r['site_id'],col)
  claims=[e for e in lane if e['record_id']==r['site_id']]
  assert {e['claim_type'] for e in claims}=={'existence','address','scope','code','parent','activity','liveness'}
  assert all(e['source_class']=='government_filing' and e['tier_effect']=='supports_C' and e['observed_date']=='2026-11-01' and e['source_ref'].endswith('#establishment_ID='+f['establishment_id']) for e in claims)
 for pat,key in [('sites_*.csv','site_id'),('organizations_*.csv','org_id'),('evidence_*.csv','evidence_id')]:
  ids=[r[key] for p in (ROOT/'data').glob(pat) for r in read(p)];assert len(ids)==len(set(ids)),pat
 for e in lane:assert 300000<=int(e['evidence_id'][4:])<=309999
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
 print('PASS exact143 census;3 census defects caught;10C sites/74 evidence bound to ITA; unique/reserved IDs; T3 reconciled',json.dumps(after))
 if a.negative_controls:print('PASS injected cross-shard SITE and EVD collisions refused before any data write')
if __name__=='__main__':main()
