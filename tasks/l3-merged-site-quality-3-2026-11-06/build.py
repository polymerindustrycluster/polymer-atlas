#!/usr/bin/env python3
"""Reproduce the final nine quality holds; never write canonical data."""
import argparse,csv,hashlib,importlib.util,json
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[1]
spec=importlib.util.spec_from_file_location('raw',ROOT/'tasks/strong-waves-mo-sc-la-2026-11-06/prepare.py');raw=importlib.util.module_from_spec(spec);spec.loader.exec_module(raw)
def read(p):
 with open(p,newline='') as f:return list(csv.DictReader(f))
def receipt(r):
 p=Path(r.get('raw_text_path',r.get('path','')));t=p.read_text()
 assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'],'raw hash mismatch'
 assert raw.contains(t,r['quote']),'raw quote absent'
 assert not raw.contains(t,r['quote']+' fabricatedholdproof7731'),'negative quote accepted'
def packet():
 frame=read(H/'input.csv');holds=read(H/'holds.csv');sources=json.loads((H/'holds-sources.json').read_text())
 assert len(frame)==len(holds)==len(sources)==9
 ids={r['site_id'] for r in frame};assert len(ids)==9
 assert ids=={r['site_id'] for r in holds}=={r['site_id'] for r in sources},'under-returned census'
 assert all(r['verdict']=='STILL_UNCERTAIN' and r['reason'] for r in holds),'unapproved promotion'
 assert json.loads((H/'selected.json').read_text())==[],'unapproved selection'
 current={r['site_id']:r for p in (ROOT/'data').glob('sites_*.csv') for r in read(p)}
 assert all(current[r['site_id']]==r for r in frame),'held site changed'
 for r in sources:receipt(r)
 known=json.loads((H/'known-answers.json').read_text());assert len(known)==3
 for r in known:receipt(r)
 return holds
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');ap.parse_args();rows=packet()
 with (H/'verdicts.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
 print('9 merged sites: 0 promotions, 9 holds; 0 canonical writes; 9 raw receipts + 3 known answers')
if __name__=='__main__':main()
