#!/usr/bin/env python3
"""Apply reviewed desk-route website/capability witnesses, refusing drift and ID reuse."""
import argparse,csv,hashlib,importlib.util,json,sys
from collections import defaultdict
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from shard_io import append_sorted
from health import read
spec=importlib.util.spec_from_file_location('recordfix',ROOT/'tasks/record-fixes-2026-11-03/build_fixes.py');matcher=importlib.util.module_from_spec(spec);spec.loader.exec_module(matcher)
def write(path,rows):
 with path.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=rows[0],lineterminator='\n');w.writeheader();w.writerows(rows)
def digest(row):return hashlib.sha256(json.dumps(row,sort_keys=True).encode()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--data-dir',type=Path,default=ROOT/'data');p.add_argument('--raw-check',action='store_true');a=p.parse_args()
 packet=read(HERE/'evidence_packet.csv');edits=read(HERE/'edits.csv')
 assert len({r['evidence_id'] for r in packet})==len(packet)
 assert all(170144<=int(r['evidence_id'][4:])<=179999 for r in packet)
 if a.raw_check:
  assert matcher.has('manufacturer of PVC film','PVC film') and not matcher.has('manufacturer of metal','PVC film')
  for r in packet:assert matcher.has(Path(r['raw_path']).read_text(),r['quote']),r['evidence_id']
  write(HERE/'rawcheck.csv',[dict(evidence_id=r['evidence_id'],raw_sha256=digest(r)) for r in packet])
 checked={r['evidence_id']:r['raw_sha256'] for r in read(HERE/'rawcheck.csv')}
 assert checked=={r['evidence_id']:digest(r) for r in packet},'raw ledger is stale or incomplete'
 shards={p:read(p) for p in sorted(a.data_dir.glob('organizations_*.csv')) if not p.name.endswith('_all.csv')}
 org={r['org_id']:(p,r) for p,rows in shards.items() for r in rows}
 ev={}
 for path in a.data_dir.glob('evidence_*.csv'):
  for row in read(path):
   assert row['evidence_id'] not in ev, 'duplicate global evidence ID'
   ev[row['evidence_id']]=(path,row)
 byid={r['evidence_id']:r for r in packet};pending=defaultdict(list);touched=set()
 vocab=json.loads((ROOT/'docs/schema/vocab.json').read_text())['vocabularies']
 for e in edits:
  assert e['field'] in {'website','processes','materials'}
  path,row=org[e['org_id']];assert row[e['field']] in {e['old'],e['new']},('field drift',e)
  proof=[byid[i] for i in e['evidence_ids'].split(';')]
  assert proof and all(r['record_id']==e['org_id'] and r['field']==e['field'] for r in proof)
  if e['field']!='website':
   assert set(e['new'].split(';'))<=set(vocab[e['field'].upper()]['values'])
   assert {r['value'] for r in proof}==set(e['new'].split(';'))
   assert all(r['source_class'] in {'own_site','government_filing'} and r['claim_type']=='scope' for r in proof)
  else:assert len(proof)==1 and proof[0]['value']==e['new'] and e['new'].startswith('https://')
  if row[e['field']]!=e['new']:row[e['field']]=e['new'];touched.add(path)
 for r in packet:
  path=a.data_dir/('evidence_'+org[r['record_id']][0].name);fields=list(read(path)[0]);entry={k:r[k] for k in fields}
  if r['evidence_id'] in ev:assert ev[r['evidence_id']]==(path,entry),('global evidence ID collision or wrong shard',r['evidence_id'])
  else:pending[path].append(entry)
 # All prospective edits and evidence are checked before any canonical write.
 for path in touched:write(path,shards[path])
 for path,rows in pending.items():append_sorted(path,rows,'evidence_id')
 print(f'{len(edits)} evidenced cells on {len({r["org_id"] for r in edits})} organizations; {len(packet)} append-only evidence rows')
if __name__=='__main__':main()
