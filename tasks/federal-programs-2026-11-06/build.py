#!/usr/bin/env python3
"""Reconcile the held D10 packet; no canonical creates are authorized."""
import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import atlas


def read(path):
    with path.open(newline='',encoding='utf-8') as f:
        return list(csv.DictReader(f))


def plan(data):
    candidates,verdicts=read(HERE/'inputs.csv'),read(HERE/'verdicts.csv')
    assert len(candidates)==len(verdicts)==12
    assert len({r['candidate_id'] for r in candidates})==12
    assert {r['candidate_id'] for r in candidates}=={r['candidate_id'] for r in verdicts}
    assert Counter(r['verdict'] for r in verdicts)=={'DUPLICATE_OF':5,'STILL_UNCERTAIN':7}
    lift=next(r for r in verdicts if r['candidate_id']=='D10-08')
    assert lift['verdict']=='STILL_UNCERTAIN' and not lift['held_or_new_id']
    assert not read(HERE/'creates_ecosystem.csv') and not read(HERE/'evidence_rows.csv'), 'scope hold prohibits canonical creates/evidence'
    tables=atlas.load_tables(str(data))
    orgs={}
    for table,row in atlas.org_rows(tables):
        assert row['org_id'] not in orgs,'duplicate existing ORG ID'
        orgs[row['org_id']]=row
    for row in verdicts:
        if row['verdict']=='DUPLICATE_OF':
            assert row['held_or_new_id'] in orgs,'duplicate does not terminate at held ID'
    for name,domain,expected in [('MAGNET','manufacturingsuccess.org','ORG-000159'),
                                 ('IACMI','iacmi.org','ORG-002099'),
                                 ('REMADE Institute','remadeinstitute.org','ORG-002100')]:
        result=atlas.dedupe(tables,domain=domain,name=name)
        assert any(h['id']==expected for step in result['steps'] for h in step['hits']),expected
    retired=read(HERE/'retired_ids.csv')
    expected={'ORG-013300'}|{f'EVD-{n:06}' for n in range(296000,296006)}
    assert len(retired)==len(expected) and {r['record_id'] for r in retired}==expected
    held=set(orgs)|{r['evidence_id'] for r in tables['evidence'].rows}
    assert not expected&held,'retired unmerged ID already present; never remove a published record'
    manifest=json.loads((HERE/'withdrawn/manifest.json').read_text())
    for filename,digest in manifest['files'].items():
        assert hashlib.sha256((HERE/'withdrawn'/filename).read_bytes()).hexdigest()==digest,'withdrawn observations changed'
    return []


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--data-dir',type=Path,default=ROOT/'data')
    p.add_argument('--raw-check',action='store_true')
    p.add_argument('--apply',action='store_true')
    args=p.parse_args()
    assert not plan(args.data_dir)
    if args.raw_check:
        print('No admitted evidence rows; no source fetch. Prior raw6/6 research archived, not inclusion evidence.')
    print('PASS census12=0VERIFIED/5DUPLICATE/7STILL_UNCERTAIN; knownheld3/3; 7unmergedIDs retired; canonical changes0')


if __name__=='__main__':
    main()
