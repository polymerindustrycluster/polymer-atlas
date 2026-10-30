"""Read-only integrity checks for the Audit 8 publication packet.
Run only once final packet artifacts exist; no canonical files are modified.
"""
import csv, hashlib, json
from pathlib import Path
P=Path(__file__).resolve().parent

def read(name): return json.loads((P/name).read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    identities=read('identity_only.json')
    ids=[r['record_id'] for r in identities]
    assert len(ids)==len(set(ids))==65
    freeze=read('VERDICT_FREEZE.json')
    verdicts=[]
    for filename,digest in freeze['files'].items():
        p=P/filename
        assert sha(p)==digest,(filename,'freeze hash mismatch')
        obj=json.loads(p.read_text())
        verdicts.extend(obj if isinstance(obj,list) else obj['records'])
    assert len(verdicts)==65
    assert {r['record_id'] for r in verdicts}==set(ids)
    assert len({r['record_id'] for r in verdicts})==65
    for r in verdicts:
        assert r['verdict'] in {'VERIFIED','REJECT','STILL_UNCERTAIN','DUPLICATE_OF'},r['record_id']
        assert r.get('reason'),r['record_id']
        if r['verdict']=='STILL_UNCERTAIN':
            assert r.get('unresolved_fields'),r['record_id']
        fetched={f['url'].rstrip('/') for f in r.get('fetch_log',[])}
        for ob in r.get('observations',[]):
            assert ob.get('source_url') and ob.get('source_name'),(r['record_id'],'uncitable observation')
            assert ob.get('accessed_date'),(r['record_id'],'undated observation')
            assert ob['source_url'].rstrip('/') in fetched,(r['record_id'],'unlogged source')
    comparisons=read('comparison.json')['records']
    assert len(comparisons)==65 and {r['record_id'] for r in comparisons}==set(ids)
    for r in comparisons:
        assert r['grade'] in {'agreement','field_error','creation_error','unresolved'}
        if r['grade'] in {'field_error','creation_error'}:
            assert r.get('findings'),r['record_id']
            for f in r['findings']:
                assert f.get('field') and f.get('settling_source_url'),r['record_id']
    sample=read('sample_metadata.json')
    assert len(sample['sample'])==65
    assert {r['record_id'] for r in sample['sample']}==set(ids)
    assert sum(x['sample_n'] for x in sample['strata'])==65
    assert sum(x['population_n'] for x in sample['strata'])==1972
    assert sum(x['sample_n']*(x['population_n']/x['sample_n']) for x in sample['strata'])==1972
    for r in sample['sample']:
        assert 0 < r['inclusion_probability'] <= 1
    with (P/'evidence_drafts.csv').open(newline='') as f:
        evidence=list(csv.DictReader(f))
    assert evidence
    assert all(not r.get('evidence_id') for r in evidence),'Lane allocated IDs'
    assert all(r['record_id'] in set(ids) for r in evidence)
    print(f'PASS: 65 unique samples, 65 frozen verdicts, 65 comparison grades; {len(evidence)} ID-free evidence drafts; strata population 1,972.')
if __name__=='__main__': main()
