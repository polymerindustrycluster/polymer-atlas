"""Append only unambiguous organization UEIs from the retained SAM index."""
import csv,io,json,sqlite3,sys,hashlib
from pathlib import Path
from collections import defaultdict,Counter
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
CACHE=Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/sam-entity-scout')
PERSIST=CACHE.parent/'sam-uei-links';PERSIST.mkdir(exist_ok=True)
sys.path.insert(0,str(ROOT/'scripts'))
from atlas import org_name_fields,name_key,street_key
KNOWN=[('ORG-000194','RQJGN2NZMNC4'),('ORG-000317','VD1NLZGAJ2L4'),('ORG-000402','GM5MMNB6DGB8')]

def read(path):return list(csv.DictReader(path.open()))

def candidates():
 c=sqlite3.connect('file:'+str(CACHE/'sam.sqlite')+'?mode=ro',uri=True)
 orgs={};shards={}
 for p in sorted((ROOT/'data').glob('organizations_*.csv')):
  for r in read(p):assert r['org_id'] not in orgs;orgs[r['org_id']]=r;shards[r['org_id']]=p.stem
 pairs=defaultdict(set);witness=defaultdict(set);registrations=defaultdict(set)
 for p in sorted((ROOT/'data').glob('sites_*.csv')):
  for s in read(p):
   oid=s['org_id']
   if oid not in orgs:continue
   sk=street_key(s['street_address'])
   if not sk or not s['city']:continue
   names={name_key(n) for _,n in org_name_fields(orgs[oid])};names.discard('')
   for uei,nk,dk,city,state,evs,updated,status in c.execute('select uei,nk,dk,city,state,evs,updated,status from sam where sk=? and state=?',(sk,s['state'])):
    if not names & {nk} or city.casefold()!=s['city'].casefold():continue
    assert 'D&B' not in evs.upper() and len(updated)==8 and updated>='20220404'
    pairs[oid].add(uei);witness[(oid,uei)].add(s['site_id'])
    registrations[(oid,uei)].add((nk,dk,city.casefold(),state,sk))
 reverse=defaultdict(set)
 for oid,ueis in pairs.items():
  for uei in ueis:reverse[uei].add(oid)
 links=read(PERSIST/'registry_links.before.csv');existing=defaultdict(set);owners=defaultdict(set)
 for r in links:
  if r['registry']=='UEI':existing[r['org_id']].add(r['registry_id']);owners[r['registry_id']].add(r['org_id'])
 for oid,uei in KNOWN:assert uei in existing[oid] and uei in pairs[oid],('known answer failed',oid)
 new=[];holds=[]
 for oid in sorted(pairs):
  for uei in sorted(pairs[oid]):
   reason='existing UEI' if existing[oid] else 'multiple organization registrations' if len(pairs[oid])!=1 else 'multiple Atlas organizations' if len(reverse[uei]|owners[uei])>1 else 'multiple registration identities' if (len(registrations[(oid,uei)])!=1 or c.execute('select count(*) from sam where uei=?',(uei,)).fetchone()[0]!=1) else ''
   record=dict(org_id=oid,uei=uei,site_ids=';'.join(sorted(witness[(oid,uei)])),shard=shards[oid])
   if reason:holds.append(dict(record,reason=reason))
   else:new.append(record)
 return new,holds,pairs,shards

def main():
 path=ROOT/'data/registry_links.csv';backup=PERSIST/'registry_links.before.csv'
 if not backup.exists():backup.write_bytes(path.read_bytes())
 new,holds,pairs,shards=candidates()
 # Rebuild proposals from immutable pre-pass UEI baseline on reruns.
 baseline=read(backup);have={r['org_id'] for r in baseline if r['registry']=='UEI'}
 additions=read(HERE/'additions.csv') if (HERE/'additions.csv').exists() else [dict(org_id=r['org_id'],registry='UEI',registry_id=r['uei'],match_basis='sam_exact_uei',as_of='2026-11-01',site_id='') for r in new]
 assert not any(r['org_id'] in have for r in additions)
 if not (HERE/'additions.csv').exists():
  for name,rows in [('additions.csv',additions),('holds.csv',holds)]:
   with (HERE/name).open('w') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
 raw=backup.read_bytes();current=path.read_bytes();buf=io.StringIO();w=csv.DictWriter(buf,fieldnames=list(baseline[0]),lineterminator='\n');w.writerows(additions);target=raw+buf.getvalue().encode()
 assert current in (raw,target),'registry changed since backup; stop'
 path.write_bytes(target)
 summary=dict(known_answers=KNOWN,matching_org_uei_pairs=sum(map(len,pairs.values())),matching_organizations=len(pairs),appended_links=len(additions),held_pairs=len(read(HERE/'holds.csv')),by_shard=dict(sorted(Counter(shards[r['org_id']] for r in additions).items())),baseline_sha256=hashlib.sha256(raw).hexdigest())
 (HERE/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
if __name__=='__main__':main()
