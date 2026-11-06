"""Exact residual-frame/verdict coverage; failures and uncertainties may never masquerade as activity."""
import csv
import hashlib
from datetime import date
from collections import Counter
from pathlib import Path

HERE=Path(__file__).resolve().parent

def read(path):
    with open(path,newline='',encoding='utf-8') as f:return list(csv.DictReader(f))

def validate(queue,verdicts):
    ids=[r['org_id'] for r in queue]
    assert len(ids)==len(set(ids))==144
    assert len(verdicts)==144 and Counter(r['org_id'] for r in verdicts)==Counter(ids)
    rank={r['org_id']:r['rank'] for r in queue}
    for r in verdicts:
        assert r['rank']==rank[r['org_id']]
        assert r['verdict'] in ('VERIFIED','REJECT','STILL_UNCERTAIN','DUPLICATE_OF')
        assert r['finding'].strip()
        if r.get('source_date'):
            assert len(r['source_date'])==10
            date.fromisoformat(r['source_date'])
        assert 0<int(r['fetch_count'])<=6
        if r['verdict']=='STILL_UNCERTAIN':assert r['settling_fact'].strip()
        if r['verdict']=='VERIFIED':
            assert r['source_url'].startswith('https://') or r['source_url'].startswith('http://')
            assert r['quote'].strip() and r['raw_check']=='yes'
            assert r['observed_date']=='2026-11-06'
        if r.get('proposed_status') in ('closed','acquired','merged','idled'):
            assert r['source_date'] and r['quote'].strip() and r['raw_check']=='yes'
            assert r.get('grain_hold','').lower() not in ('true','yes','1')

if __name__=='__main__':
    assert hashlib.sha256((HERE/'queue.csv').read_bytes()).hexdigest()=='47f1ab283a34a8b7a5a2ade730ae471ea67d125d40952e71d7e73e1925533a02'
    queue=read(HERE/'queue.csv')
    verdicts=read(HERE/'verdicts.csv')
    validate(queue,verdicts)
    from git_gate import assert_data_unchanged
    assert_data_unchanged(HERE.parents[1])
    raw_rows=read(HERE/'lead_rawcheck.csv')
    assert len(raw_rows)==len({(r['org_id'],r['source_url'],r['quote']) for r in raw_rows})
    audit={(r['org_id'],r['source_url'],r['quote']):r for r in read(HERE/'lead_rawcheck.csv')}
    assert {r['verdict'] for r in verdicts}<={'VERIFIED','STILL_UNCERTAIN'}, 'Closure/duplicate verdict needs its own evidence gate'
    import glob
    canonical={r['org_id']:r for path in glob.glob(str(HERE.parents[1]/'data/organizations_*.csv'))+[str(HERE.parents[1]/'data/ecosystem.csv')] for r in read(path)}
    for r in verdicts:
        if r['verdict']=='VERIFIED':assert canonical[r['org_id']]['status']=='active'
        if r['verdict']=='VERIFIED':assert audit[(r['org_id'],r['source_url'],r['quote'])]['raw_check']=='yes'
        assert not r['proposed_status'] and not r['successor_org_id']
    counts=Counter()
    for path in [HERE/'lead_fetch_log.csv',HERE/'lanes/A/fetch_log.csv',HERE/'lanes/B/fetch_log.csv']:
        counts.update(r['org_id'] for r in read(path))
    assert set(counts)=={r['org_id'] for r in queue} and max(counts.values())<=6
    assert sum(counts.values())==352
    print('PASS: 144 original residual IDs, exact one-verdict coverage, meaningful holds/raw witnesses; all final positives lead-refetched; zero committed/staged/working/untracked data mutations')
    print(Counter(r['verdict'] for r in verdicts))
