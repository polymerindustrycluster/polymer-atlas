#!/usr/bin/env python3
"""Named L3 completion check: exact census, applied creates, raw quotes, T3 and unique reserved IDs."""
import csv, hashlib, importlib.util, json
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def read(p):
    with open(p,newline='') as f:return list(csv.DictReader(f))
def census(source,verdicts):
    assert Counter(r['cluster_id'] for r in verdicts)==Counter(r['cluster_id'] for r in source), 'missing/duplicated verdict'
    assert len({r['cluster_id'] for r in verdicts})==len(verdicts)
    assert all(r['verdict'] in {'VERIFIED','REJECT','STILL_UNCERTAIN','DUPLICATE_OF'} and r['deciding_fact'] for r in verdicts)
def main():
    source=[r for r in read(ROOT/'tasks/lead-fusion-2026-11-01/clusters.csv') if r['state'] in ('MO','SC','LA') and r['class']=='STRONG']
    verdicts=read(HERE/'verdicts.csv');census(source,verdicts)
    assert {r['cluster_id']:r for r in read(HERE/'input.csv')}=={r['cluster_id']:r for r in source}, 'input facts changed'
    for defect in (verdicts[:-1],verdicts+[verdicts[0]],verdicts[:-1]+[verdicts[0]]):
        try:census(source,defect)
        except AssertionError:pass
        else:raise AssertionError('census gate failed injected defect')
    raw={r['cluster_id']:r for r in read(HERE/'rawcheck.csv')}
    for v in verdicts:
        if v['verdict']=='VERIFIED':assert v['own_quote']==raw[v['cluster_id']]['quote'] and v['own_url']==raw[v['cluster_id']]['url']
    evidence=[r for p in (ROOT/'data').glob('evidence_*.csv') for r in read(p)]
    lane=[r for r in evidence if r['created_by']=='atlas-L3-strong-mo-sc-la']
    assert len(lane)==279, ('lane evidence total',len(lane))
    for extra in read(HERE/'supplements.csv'):
        assert extra['raw']=='yes'
        assert any(extra['quote'] in e['claim_detail'] and extra['source_url']==e['source_ref'] for e in lane),extra

    allocations=[r for st in ('MO','SC','LA') for r in read(HERE/f'allocations_{st}.csv')]
    assert Counter(r['cluster_id'] for r in allocations)==Counter(r['cluster_id'] for r in verdicts if r['verdict']=='VERIFIED')
    assert len(allocations)==19 and sum(r['new_org']=='true' for r in allocations)==15
    sites={r['site_id']:r for p in (ROOT/'data').glob('sites_*.csv') for r in read(p)}
    for r in allocations:
        s=sites[r['site_id']];assert s['org_id']==r['org_id'] and s['verification_tier']==r['tier']
        assert raw[r['cluster_id']]['raw']=='yes'
        assert 12000<=int(r['site_id'][5:])<=12999
    for pattern,key in [('organizations_*.csv','org_id'),('sites_*.csv','site_id'),('evidence_*.csv','evidence_id')]:
        ids=[r[key] for p in (ROOT/'data').glob(pattern) for r in read(p)]
        assert len(ids)==len(set(ids)),(pattern,'duplicate ids')
    spec=importlib.util.spec_from_file_location('qcew',ROOT/'scripts/build_qcew_denominators.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    nums=m.atlas_numerators(str(ROOT));before=json.loads((HERE/'qcew-before.json').read_text());after={}
    for st,b in before.items():
        n=nums[(st,'326')][1];assert n>b['strict_before'],(st,n,b)
        delta=sum(sites[r['site_id']]['naics_primary'].startswith('326') for r in allocations if sites[r['site_id']]['state']==st)
        assert n-b['strict_before']==delta,(st,'unreconciled numerator delta',delta)
        after[st]={**b,'strict_after':n,'share_before':b['strict_before']/float(b['qcew_2023']),'share_after':n/float(b['qcew_2023'])}
    (HERE/'qcew-after.json').write_text(json.dumps(after,indent=2)+'\n')
    print('PASS: 36/36 exact STRONG verdicts; census defects 3/3 caught;',len(allocations),'applied sites; IDs unique; NAICS 326 strict/QCEW rises in MO/SC/LA')
    print(json.dumps(after,indent=2))
if __name__=='__main__':main()
