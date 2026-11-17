"""Check exact payload, source identity, append-only delta and injected defects."""
import csv,copy,json,hashlib,sqlite3
from collections import Counter
from build import ROOT,HERE,CACHE,PERSIST,KNOWN,read,candidates

def verify(rows,expected,baseline):
 assert len({r['org_id'] for r in rows})==len(rows)
 assert len({r['registry_id'] for r in rows})==len(rows)
 old={r['org_id'] for r in baseline if r['registry']=='UEI'}
 assert all(r['org_id'] not in old and r['registry']=='UEI' and r['match_basis']=='sam_exact_uei' and r['as_of']=='2026-11-01' and not r['site_id'] for r in rows)
 c=sqlite3.connect('file:'+str(CACHE/'sam.sqlite')+'?mode=ro',uri=True)
 for r in rows:
  source=list(c.execute('select evs,updated from sam where uei=?',(r['registry_id'],)))
  assert len(source)==1 and 'D&B' not in source[0][0].upper() and len(source[0][1])==8 and source[0][1]>='20220404'
 assert rows==expected,'payload differs from exact matcher'

def main():
 new,holds,pairs,shards=candidates();baseline=read(PERSIST/'registry_links.before.csv')
 expected=[dict(org_id=r['org_id'],registry='UEI',registry_id=r['uei'],match_basis='sam_exact_uei',as_of='2026-11-01',site_id='') for r in new]
 rows=read(HERE/'additions.csv');verify(rows,expected,baseline)
 assert read(HERE/'holds.csv')==holds
 raw=(PERSIST/'registry_links.before.csv').read_bytes();actual=(ROOT/'data/registry_links.csv').read_bytes()
 assert actual.startswith(raw)
 assert read(ROOT/'data/registry_links.csv')==baseline+rows
 summary=json.loads((HERE/'summary.json').read_text())
 assert summary['known_answers']==[list(k) for k in KNOWN]
 assert summary['matching_org_uei_pairs']==sum(map(len,pairs.values()))==len(new)+len(holds)
 assert summary['matching_organizations']==len(pairs)
 assert summary['appended_links']==len(rows)
 assert summary['held_pairs']==len(holds)
 assert summary['by_shard']==dict(Counter(shards[r['org_id']] for r in rows))
 assert summary['baseline_sha256']==hashlib.sha256(raw).hexdigest()
 for label in ['phantom UEI','second UEI','reused UEI']:
  bad=copy.deepcopy(rows)
  if label=='phantom UEI':bad[0]['registry_id']='000000000000'
  elif label=='second UEI':bad[1]['org_id']=bad[0]['org_id']
  else:bad[1]['registry_id']=bad[0]['registry_id']
  try:verify(bad,expected,baseline)
  except AssertionError:print('caught:',label)
  else:raise AssertionError('silent defect pass: '+label)
 print(f'PASS: {len(KNOWN)} known answers; {len(rows)} additions; {len(holds)} holds; source and append-only checks; 3 injected defects')
if __name__=='__main__':main()
