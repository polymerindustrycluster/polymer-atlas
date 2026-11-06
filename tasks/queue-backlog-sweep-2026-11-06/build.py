"""Frozen packet application. Preflight all rows/IDs before any mutation; replay-safe."""
import argparse,csv,io,sys
from collections import defaultdict
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from shard_io import append_sorted

def read(p):
 with open(p,newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
def write(p,rows):
 buf=io.StringIO();w=csv.DictWriter(buf,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows);p.write_text(buf.getvalue())
def generated_edges(orgs):
 # House derivation: dedupe-hq-2 build.edge; SCHEMA4.14.2, canonical columns alone generate edge/type/date.
 edges=[]
 for r in orgs:
  if r['successor_org_id']:
   assert r['status'] in ('acquired','merged')
   edges.append(dict(relationship_id=f'REL-{460+len(edges):06d}',from_org_id=r['org_id'],relationship_type={'acquired':'successor_of','merged':'merged_into'}[r['status']],to_org_id=r['successor_org_id'],effective_from=r['status_date'] if r['status']=='acquired' else '',effective_to='',basis=f"Generated from {r['org_id']}.successor_org_id with status={r['status']} (SCHEMA4.14.2 canonical-column parity).",source_ref=f"organizations.csv: {r['org_id']}.successor_org_id + status",created_by='codex queue-backlog-sweep-2026-11-06',notes='Controller REL460–469 allocation BOARD10:35; historical predecessor under SCHEMA5.2, not legal closure.'))
 assert len(edges)<=10
 return edges

def apply(data):
 raw=read(HERE/'rawcheck.csv');src=read(HERE/'sources.csv')
 assert len(raw)==len(src)==16 and {r['key'] for r in raw}=={r['key'] for r in src}
 for s in src:
  rr=next(r for r in raw if r['key']==s['key']);assert rr['raw']=='yes' and all(rr[k]==s[k] for k in ('url','quote')),'unchecked source'
 orgs=read(HERE/'organizations.csv');ev=read(HERE/'evidence.csv');edits=read(HERE/'edits.csv')
 assert len(orgs)==1 and orgs[0]['org_id']=='ORG-013200'
 for e in ev:
  if e['source_class']=='own_site':
   quote=e['claim_detail'].split('raw quote: "',1)[1].rsplit('"',1)[0]
   assert e['claim_detail']=='raw quote: "'+quote+'"', 'own_site claim exceeds literal source observation'
 assert len(ev)==16 and all(310000<=int(e['evidence_id'][4:])<=314999 for e in ev)
 assert {e['claim_type'] for e in ev if e['record_id']=='ORG-013200'}=={'existence','address','scope','code','parent'}
 assert orgs[0]['successor_org_id']=='ORG-000007' and orgs[0]['status']=='acquired' and orgs[0]['verification_tier']=='U'
 plans=defaultdict(list)
 plans['organizations_OH.csv'].extend(orgs);plans['relationships.csv'].extend(generated_edges(orgs))
 pending_ids=[r['evidence_id'] for r in ev]
 assert len(pending_ids)==len(set(pending_ids)), 'cross-packet evidence ID collision'
 for e in ev:
  ee=dict(e);shard=ee.pop('shard');plans[shard].append(ee)
 # Global ID census across shards, including ecosystem's shared organization namespace.
 indices={}
 for pattern,key in [('organizations_*.csv','org_id'),('ecosystem.csv','org_id'),('evidence_*.csv','evidence_id'),('relationships.csv','relationship_id')]:
  for f in data.glob(pattern):
   for r in read(f):
    assert r[key] not in indices,'existing duplicate ID'
    indices[r[key]]=(f.name,r)
 additions=[]
 for name,rows in plans.items():
  key='org_id' if name.startswith('organizations') else 'relationship_id' if name=='relationships.csv' else 'evidence_id'
  assert len({r[key] for r in rows})==len(rows),'packet duplicate ID'
  for r in rows:
   prior=indices.get(r[key]);assert prior is None or prior==(name,r),'ID collision/drift: '+r[key]
  additions.append((data/name,[r for r in rows if r[key] not in indices],key))
 assert 'ORG-000007' in indices,'missing successor'
 updates={}
 for e in edits:
  name=e['file'];rows=updates.setdefault(name,read(data/name));hit=[r for r in rows if r['site_id']==e['record_id']]
  assert len(hit)==1,'missing/duplicate edit target'
  r=hit[0];assert r[e['field']] in (e['before'],e['after']),'preimage drift: '+e['record_id']+'.'+e['field']
  r[e['field']]=e['after']
 for path,rows,key in additions:
  if rows:append_sorted(path,rows,key)
 for name,rows in updates.items():write(data/name,rows)
 print('PASS apply: 1 U acquired predecessor / 1 generated successor_of / 8 existing sites / 22 cell edits / 16 evidence (idempotent)')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--data-dir',type=Path,default=ROOT/'data');apply(p.parse_args().data_dir)
