#!/usr/bin/env python3
"""Apply the bounded own-site capability packet; refuse drift and ID reuse."""
import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
sys.path.insert(0,str(HERE.parent/'pic18-record-health-2026-11-06'))
from shard_io import append_sorted
from health import read
import importlib.util
spec=importlib.util.spec_from_file_location('first_pass',HERE.parent/'pic18-record-health-2026-11-06/build.py')
first=importlib.util.module_from_spec(spec);spec.loader.exec_module(first)
matcher,write=first.matcher,first.write

def main():
 p=argparse.ArgumentParser();p.add_argument('--data-dir',type=Path,default=ROOT/'data');p.add_argument('--raw-check',action='store_true');a=p.parse_args()
 packet=read(HERE/'evidence_packet.csv');edits=read(HERE/'edits.csv')
 assert len({r['evidence_id'] for r in packet})==len(packet)
 assert all(170012<=int(r['evidence_id'][4:])<=179999 for r in packet)
 if a.raw_check:
  assert matcher.has('Our nylon material','nylon') and not matcher.has('nylon machinery','nylon material')
  for r in packet:assert matcher.has(Path(r['raw_path']).read_text(),r['quote']),r['evidence_id']
  write(HERE/'rawcheck.csv',[dict(evidence_id=r['evidence_id'],raw='yes') for r in packet])
 assert {r['evidence_id'] for r in read(HERE/'rawcheck.csv') if r['raw']=='yes'}=={r['evidence_id'] for r in packet}
 vocab=json.loads((ROOT/'docs/schema/vocab.json').read_text())['vocabularies']
 paths={p:read(p) for p in sorted(a.data_dir.glob('organizations_*.csv')) if not p.name.endswith('_all.csv')}
 org={r['org_id']:(p,r) for p,rows in paths.items() for r in rows}
 ev={r['evidence_id']:r for p in a.data_dir.glob('evidence_*.csv') for r in read(p)}
 pending=defaultdict(list);touched=set()
 for e in edits:
  assert e['field'] in {'processes','materials'}
  vals=e['new'].split(';');assert set(vals)<=set(vocab[e['field'].upper()]['values'])
  supporting=[r for r in packet if r['record_id']==e['org_id'] and r['field']==e['field']]
  assert {r['value'] for r in supporting}==set(vals),e
  path,row=org[e['org_id']];assert row[e['field']] in {e['old'],e['new']},('drift',e)
  if row[e['field']]!=e['new']:row[e['field']]=e['new'];touched.add(path)
 for r in packet:
  path=a.data_dir/('evidence_'+org[r['record_id']][0].name)
  fields=list(read(path)[0]);entry={k:r[k] for k in fields}
  if r['evidence_id'] in ev:assert ev[r['evidence_id']]==entry,'evidence collision'
  else:pending[path].append(entry)
 for path in touched:write(path,paths[path])
 for path,rows in pending.items():append_sorted(path,rows,'evidence_id')
 print(f'{len(edits)} capability cells on {len({e["org_id"] for e in edits})} organizations; {len(packet)} evidence rows')
if __name__=='__main__':main()
