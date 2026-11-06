"""Census, source witnesses, all-data preservation, replay and CLI zero-write faults."""
import collections
import csv
import hashlib
import io
import json
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path
import build as b
import discover as d


def digest(data):
    return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.csv')}


def main():
    base=(d.HERE/'base.txt').read_text().strip()
    inputs=b.read(d.HERE/'inputs.csv');proposals=b.read(d.HERE/'proposals.csv');checks=b.read(d.HERE/'rawcheck.csv');verdicts=b.read(d.HERE/'verdicts.csv')
    assert len(inputs)==len(verdicts)==len({r['org_id'] for r in verdicts})==2061
    assert {r['org_id'] for r in inputs}=={r['org_id'] for r in verdicts}
    assert {r['org_id'] for r in proposals}=={r['org_id'] for r in verdicts if r['verdict']=='VERIFIED'}
    assert all(r['verdict'] in {'VERIFIED','STILL_UNCERTAIN'} for r in verdicts)
    outcomes=b.read(d.HERE/'raw-outcomes.csv')
    assert len(outcomes)==len({r['org_id'] for r in outcomes})
    assert sum(r['result']=='PASS' for r in outcomes)==len(proposals)==len(checks)
    requests=json.loads((d.HERE/'raw-requests.json').read_text())
    assert len(requests)==len(outcomes)
    frame={r['org_id']:r for r in inputs}
    for record in requests:
        owner=d.domain(frame[record['org_id']]['website'] if '://' in frame[record['org_id']]['website'] else 'https://'+frame[record['org_id']]['website'])
        assert all(d.own_url(r['url'],owner) for r in record['attempts']), 'external/LinkedIn request logged'
        assert 1<=len(record['attempts'])<=6
    pages=json.loads((d.HERE/'discovery.json').read_text())
    owners=d.domain_owners()
    expected={r['website'] for r in inputs if r['website'] and r['status']=='active' and len(owners.get(d.domain(r['website'] if '://' in r['website'] else 'https://'+r['website']),set()))==1}
    assert {p['website'] for p in pages}==expected and len(pages)==len(expected), 'discovery URL census incomplete'
    for page in pages:
        owner=d.domain(page['website'] if '://' in page['website'] else 'https://'+page['website'])
        assert all(d.own_url(r['url'],owner) for r in page['attempts'])
    assert all(x['check']=='PASS' for x in json.loads((d.HERE/'known-answers.json').read_text()))
    for bad in ['https://www.linkedin.com/in/test-person/','https://evil.example/company/foo/','https://www.linkedin.com/company/%2E%2E/']:
        assert not d.canonical(bad)
    assert not d.Links('<body class="theme-header-footer"><a href="https://www.linkedin.com/company/fabricated/">body</a></body>').links
    assert not d.Links('<footer><a href>empty</a></footer>').links
    with tempfile.TemporaryDirectory() as tmp:
        data=Path(tmp)
        archive=subprocess.check_output(['git','archive',base+':data'],cwd=d.ROOT)
        with tarfile.open(fileobj=io.BytesIO(archive)) as t:
            t.extractall(data,filter='data')
        before=digest(data)
        encoded,n=b.plan(data,proposals,inputs,checks)
        assert n==len(proposals)
        for path,value in encoded.items():
            path.write_bytes(value)
        expected_bytes=digest(data)
        assert expected_bytes==digest(d.ROOT/'data'), 'canonical all-data differs from exact navigation-only projection'
        changed={k for k in before if before[k]!=expected_bytes[k]}
        assert changed and all(k.startswith('organizations_') for k in changed)
        encoded,n=b.plan(data,proposals,inputs,checks)
        assert not encoded and n==0 and expected_bytes==digest(data), 'replay changed data'
        sample=proposals[0]
        path=next(p for p in data.glob('organizations_*.csv') if any(r['org_id']==sample['org_id'] for r in b.read(p)))
        original=path.read_bytes()
        for fault in ['navigation_conflict','entity_preimage']:
            rows=b.read(path)
            row=next(r for r in rows if r['org_id']==sample['org_id'])
            if fault=='navigation_conflict':
                row['linkedin_url']='https://www.linkedin.com/company/fabricated-other/'
            else:
                row['legal_name']='Fabricated Other Entity'
            with path.open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
            snapshot=digest(data)
            result=subprocess.run([sys.executable,str(d.HERE/'build.py'),'--apply','--data-dir',str(data)],capture_output=True,text=True)
            assert result.returncode and digest(data)==snapshot,(fault,result.stderr)
            path.write_bytes(original)
            print(fault,'refused before any CSV write')
        poisoned=[dict(r) for r in proposals];poisoned[0]['linkedin_url']='https://www.linkedin.com/company/fabricated-other/'
        try:
            b.plan(data,poisoned,inputs,checks)
        except AssertionError:
            pass
        else:
            raise AssertionError('identity-poisoned packet accepted')
    print('PASS',len(proposals),'navigation cells;',len(inputs),'frame outcomes;',len(changed),'shards; all other canonical bytes/keys/fields preserved, byte replay, 3 zero-write negatives, LinkedIn request exclusion.')
    print('By cohort',dict(collections.Counter(r['cohort'] for r in proposals)),'by frozen tier',dict(collections.Counter(r['verification_tier'] for r in proposals)))


if __name__=='__main__':
    main()
