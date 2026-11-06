#!/usr/bin/env python3
"""Apply sourced distinct-pair notes and own-site capability values; no merges without proof."""
import argparse,csv,importlib.util,json,sys
from pathlib import Path
from collections import defaultdict
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from shard_io import append_sorted
from health import read
spec=importlib.util.spec_from_file_location('recordfix',ROOT/'tasks/record-fixes-2026-11-03/build_fixes.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def write(p,rows):
 with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=rows[0],lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--data-dir',type=Path,default=ROOT/'data');ap.add_argument('--raw-check',action='store_true');a=ap.parse_args()
 packet=read(HERE/'evidence_packet.csv');edits=read(HERE/'edits.csv')
 assert len({r['evidence_id'] for r in packet})==len(packet)
 assert all(170066<=int(r['evidence_id'][4:])<=179999 for r in packet)
 if a.raw_check:
  assert m.has('Acme fiberglass construction','fiberglass construction') and not m.has('Acme unrelated metal','fiberglass construction')
  for r in packet:assert m.has(Path(r['raw_path']).read_text(),r['quote']),r['evidence_id']
  write(HERE/'rawcheck.csv',[dict(evidence_id=r['evidence_id'],raw='yes') for r in packet])
 assert {r['evidence_id'] for r in read(HERE/'rawcheck.csv') if r['raw']=='yes'}=={r['evidence_id'] for r in packet}
 shards={p:read(p) for p in sorted(a.data_dir.glob('organizations_*.csv')) if not p.name.endswith('_all.csv')};org={r['org_id']:(p,r) for p,rows in shards.items() for r in rows}
 held={}
 for path in a.data_dir.glob('evidence_*.csv'):
  for r in read(path):
   assert r['evidence_id'] not in held, 'duplicate global evidence ID'
   held[r['evidence_id']]=(path,r)
 ev={r['evidence_id']:r for r in packet}
 vocab=json.loads((ROOT/'docs/schema/vocab.json').read_text())['vocabularies'];touched=set();pending=defaultdict(list)
 for e in edits:
  assert e['field'] in {'notes','processes','materials'}
  path,r=org[e['org_id']];assert r[e['field']] in {e['old'],e['new']},('drift',e)
  proofs=[ev[x] for x in e['evidence_ids'].split(';')];assert proofs and any(x['record_id']==e['org_id'] for x in proofs)
  if e['field']!='notes':
   assert all(x['record_id']==e['org_id'] for x in proofs)
   assert set(e['new'].split(';'))<=set(vocab[e['field'].upper()]['values'])
   assert {x['value'] for x in proofs}==set(e['new'].split(';')) and all(x['field']==e['field'] and x['kind']=='capability' for x in proofs)
  else:
   assert all(x['kind']=='distinct' for x in proofs)
   peers={r['right'] if r['left']==e['org_id'] else r['left'] for r in read(HERE/'duplicate_verdicts.csv') if e['org_id'] in {r['left'],r['right']} and r['adjudication']=='distinct'}
   assert all(x['record_id'] in peers|{e['org_id']} for x in proofs)
   assert e['new'].startswith(e['old'])
  if r[e['field']]!=e['new']:r[e['field']]=e['new'];touched.add(path)
 for r in packet:
  path=a.data_dir/('evidence_'+org[r['record_id']][0].name);fields=list(read(path)[0]);entry={k:r[k] for k in fields}
  if r['evidence_id'] in held:assert held[r['evidence_id']]==(path,entry),('global evidence collision or wrong shard',r['evidence_id'])
  else:pending[path].append(entry)
 # All drift, vocabulary, proof and global-ID checks finish before any data write.
 for p in touched:write(p,shards[p])
 for p,rows in pending.items():append_sorted(p,rows,'evidence_id')
 print(f'{len(edits)} evidenced cells/{len({e["org_id"] for e in edits})} orgs; {len(packet)} evidence rows; no status or relationship changes')
if __name__=='__main__':main()
