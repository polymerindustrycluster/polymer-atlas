"""Append manually verified claim repairs; preserve weak rows and all record fields."""
import argparse,csv,json,sys,hashlib
from collections import defaultdict,Counter
from pathlib import Path
from urllib.parse import urlsplit
H=Path(__file__).resolve().parent;ROOT=H.parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from shard_io import append_sorted
from fetch import read,on_page
DATE='2026-11-06';BY='codex atlas-L11-evidence-repair-4'
def host(u):return (urlsplit(u).hostname or '').lower().removeprefix('www.')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');ap.add_argument('--data-dir',type=Path,default=ROOT/'data');a=ap.parse_args();data=a.data_dir
 inputs=read(H/'input.csv');weak=read(H/'checked.csv');selected=read(H/'selected.csv');raw=read(H/'rawcheck.csv')
 assert len(inputs)==len(weak)==len({r['evidence_id'] for r in weak})==269
 assert {r['evidence_id'] for r in inputs}=={r['evidence_id'] for r in weak}
 assert len(selected)==len({r['evidence_id'] for r in selected})==len(raw)
 checked={r['evidence_id']:r for r in raw};approved={r['evidence_id']:r for r in selected};out=defaultdict(list);verdicts=[];alloc=[]
 all_ev=[(p.name,r) for p in data.glob('evidence_*.csv') for r in read(p)]
 canonical={r['evidence_id']:(name,r) for name,r in all_ev};assert len(canonical)==len(all_ev),'existing duplicate evidence ID'
 orgs={r['org_id']:r for p in data.glob('organizations_*.csv') for r in read(p)};sites={r['site_id']:r for p in data.glob('sites_*.csv') for r in read(p)}
 for slot,w in enumerate(weak):
  shard,current=canonical[w['evidence_id']]
  assert all(w[k]==v for k,v in current.items()),('weak row changed',w['evidence_id'])
  r=approved.get(w['evidence_id']);reason='HOLD: no semantically approved replacement within cited page and bounded same-domain discovery; requires own page explicitly supporting '+w['claim_detail']+'. Site claims need physical facility binding; certification claims need current edition/certificate.'
  if not r:
   dh={x['evidence_id']:x['reason'] for x in read(H/'domain_holds.csv')}
   reason=dh.get(w['evidence_id'],reason)
   verdicts.append(dict(evidence_id=w['evidence_id'],verdict='STILL_UNCERTAIN',record_id=w['record_id'],reason=reason));continue
  f=checked[w['evidence_id']];assert f['raw']=='yes' and all(f[k]==r[k] for k in r)
  assert hashlib.sha256((ROOT/f['page']).read_bytes()).hexdigest()==f['page_sha256'],'frozen source bytes changed'
  assert on_page(r['quote'],ROOT/f['page']),('raw quote missing',w['evidence_id'])
  owner=sites[w['record_id']]['org_id'] if w['record_table']=='sites' else w['record_id'];domain=host(orgs[owner]['website']);source=host(r['source_url'])
  assert domain and (source==domain or source.endswith('.'+domain)),('not own domain',w['evidence_id'],source,domain)
  # Claim details contain only the page's actual words; prior-row linkage stays in notes.
  eid=f'EVD-{276000+slot:06d}';assert int(eid[4:])<=279999
  out[shard].append(dict(evidence_id=eid,record_table=w['record_table'],record_id=w['record_id'],claim_type=w['claim_type'],claim_detail='"'+r['quote']+'"',source_class='own_site',source_ref=r['source_url'],observed_date=DATE,tier_effect=w['tier_effect'],created_by=BY,notes=f"Answers {w['evidence_id']}; claim assessed independently, raw re-fetched {f['fetched_at']}. {r['note']}"))
  assert w['tier_effect'] in ['supports_A','supports_B','supports_C']
  alloc.append(dict(weak_evidence_id=w['evidence_id'],evidence_id=eid,shard=shard,record_id=w['record_id']))
  verdicts.append(dict(evidence_id=w['evidence_id'],verdict='VERIFIED',record_id=w['record_id'],reason=r['note']))
 assert len(verdicts)==269 and len({r['evidence_id'] for r in alloc})==len(alloc)
 pending={}
 for name,rows in out.items():
  header=list(read(data/name)[0]);pending[name]=[]
  for r in rows:
   if r['evidence_id'] in canonical:
    oldname,old=canonical[r['evidence_id']];assert oldname==name and old=={k:r.get(k,'') for k in header},('global collision',r['evidence_id'])
   else:pending[name].append(r)
 if a.apply:
  for name,rows in pending.items():
   if rows:append_sorted(data/name,rows,'evidence_id')
 for filename,rows in [('verdicts.csv',verdicts),('allocations.csv',alloc)]:
  with open(H/filename,'w') as f:
   w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
 print(json.dumps(dict(inputs=269,verdicts=dict(Counter(r['verdict'] for r in verdicts)),new_evidence=len(alloc),shards=len(out),pending=sum(map(len,pending.values())))))
if __name__=='__main__':main()
