"""Check manifest yield, quotes and persisted cells; self-test three injected defects."""
import copy,csv,json,runpy
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
config=runpy.run_path(str(HERE/'build.py'));CACHE=config['CACHE']
CASES={'a','b','c-ppg','c-shw','d','e','f-k','f-s','f-n'}
def check(proposals,evidence):
    assert len(proposals)==len(evidence)==15
    assert len({e['evidence_id'] for e in evidence})==15
    assert {p['case'] for p in proposals}==CASES-{'a'}
    for p,e in zip(proposals,evidence):
        assert p['evidence_id']==e['evidence_id']
        assert p['record_id']==e['record_id']
        assert ' '.join(p['quote'].split()) in ' '.join((CACHE/(p['key']+'.txt')).read_text().split())
        assert p['quote'] in e['notes']
        assert 369000<=int(e['evidence_id'][4:])<=369499
    actual={r['evidence_id']:r for f in (ROOT/'data').glob('evidence_*.csv') for r in csv.DictReader(f.open())}
    for e in evidence:assert actual[e['evidence_id']]==e
    sites={r['site_id']:r for f in (ROOT/'data').glob('sites_*.csv') for r in csv.DictReader(f.open())}
    for rid,material in config['MATERIALS'].items():assert sites[rid]['materials']==material
    orgs={r['org_id']:r for f in (ROOT/'data').glob('organizations_*.csv') for r in csv.DictReader(f.open())}
    assert orgs['ORG-002044']['status']=='merged' and orgs['ORG-002044']['successor_org_id']=='ORG-000103'
    assert sites['SITE-000818']['operating_status']=='closed'
    assert orgs['ORG-001327']['parent_org_id']=='ORG-000430'
    assert all(orgs[r]['verification_tier']=='A' for r in ['ORG-000088','ORG-000132'])
if __name__=='__main__':
    p=json.loads((HERE/'proposals.json').read_text());e=json.loads((HERE/'evidence.json').read_text());check(p,e)
    for defect in ['lost_input','duplicate_id','invented_quote']:
        pp,ee=copy.deepcopy(p),copy.deepcopy(e)
        if defect=='lost_input':pp.pop()
        elif defect=='duplicate_id':ee[1]['evidence_id']=ee[0]['evidence_id']
        else:pp[0]['quote']='THIS QUOTE IS AN INJECTED FABRICATION'
        try:check(pp,ee)
        except AssertionError:print('rejected:',defect)
        else:raise AssertionError('silent pass: '+defect)
    print('PASS: 9 manifest cases; 15 proposals -> 15 evidence rows on 9 records; 2 material fills; 3 injected defects rejected')
    dispositions=list(csv.DictReader((HERE/'dispositions.csv').open()))
    assert len(dispositions)==len(CASES) and {r['case'] for r in dispositions}==CASES
    assert sum(r['verdict']=='VERIFIED-applied' for r in dispositions)==4
    assert sum(r['verdict']=='STILL_UNCERTAIN' for r in dispositions)==5
    assert len({e['record_id'] for e in e})==9
    print('Dispositions: 4 fully verified cases; 5 cases with named settling facts (3 also partially applied).')
    assert sum(r["record_table"]=="organizations" for r in e)==10
    assert sum(r["tier_effect"]=="supports_A" for r in e)==12
    assert sum(r["tier_effect"]=="supports_C" for r in e)==3
