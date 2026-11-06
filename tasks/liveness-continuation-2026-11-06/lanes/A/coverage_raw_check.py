"""Named lane check: exact coverage, availability counts, dates, and primary raw quotes."""
import csv,re,gzip
from collections import Counter
from pathlib import Path
from research import HERE,Text,found

def check(rows,inputs,logs):
    ids=[r['org_id'] for r in rows];expected=[r['org_id'] for r in inputs]
    assert len(rows)==len(inputs)==72, 'input/verdict count'
    assert len(set(ids))==len(ids), 'duplicate verdict'
    assert ids==expected, 'missing, extra or rank-order mismatch'
    assert [r['rank'] for r in rows]==[r['rank'] for r in inputs], 'rank mismatch'
    counts=Counter(l['org_id'] for l in logs)
    assert set(counts)==set(expected), 'fetch coverage'
    for r,i in zip(rows,inputs):
        assert r['legal_name']==i['legal_name'], 'held identity changed'
        assert r['verdict'] in ('VERIFIED','STILL_UNCERTAIN','REJECT','DUPLICATE_OF')
        assert r['source_class'] in ('own_site','government_filing','registry','directory','press','platform_category','harvest_roster')
        assert int(r['fetch_count'])==counts[r['org_id']] and 1<=counts[r['org_id']]<=6, 'fetch accounting'
        assert len(r['finding'].split())>=10, 'missing adjudication'
        for key in ('source_date','observed_date'):
            assert not r[key] or re.fullmatch(r'\d{4}-\d{2}-\d{2}',r[key]), 'non-ISO date'
        if r['verdict']=='STILL_UNCERTAIN':
            assert len(r['settling_fact'].split())>=10 and len(set(r['settling_fact'].lower().split()))>=8, 'meaningless uncertainty'
        if r['verdict']=='VERIFIED':
            assert r['raw_check']=='yes' and counts[r['org_id']]<=5, 'verified lacks quote/refetch headroom'
            assert i['current_status'] not in ('closed','merged','acquired'), 'reactivation'
        if r['quote']:
            assert len(r['quote'].split())<=25, 'quote limit'
            p=Path(r['raw_cache_path']);b=p.read_bytes()
            if b.startswith(b'\x1f\x8b'):b=gzip.decompress(b)
            raw=b.decode('utf-8','replace');t=Text();t.feed(raw)
            assert found('\n'.join(t.parts),r['quote']) or found(raw,r['quote']), 'raw quote absent'
            matches=[l for l in logs if l['raw_cache_path']==str(p) and l['org_id']==r['org_id']]
            assert matches and matches[0]['http']=='200', 'quote from failed response'
        assert not r['successor_org_id'] and not r['proposed_status'], 'unexpected canonical/status motion'
    return Counter(r['verdict'] for r in rows)

if __name__=='__main__':
    rows=list(csv.DictReader(open(HERE/'verdicts.csv')));inputs=list(csv.DictReader(open(HERE/'input.csv')));logs=list(csv.DictReader(open(HERE/'fetch_log.csv')))
    result=check(rows,inputs,logs)
    mutations=[]
    for label,mutate in [('missing row',lambda rs:rs.pop()),('duplicate ID',lambda rs:rs[1].update(org_id=rs[0]['org_id'])),('absent quote',lambda rs:next(r for r in rs if r['quote']).update(quote='invented business witness that does not appear')),('empty uncertainty',lambda rs:next(r for r in rs if r['verdict']=='STILL_UNCERTAIN').update(settling_fact=''))]:
        changed=[r.copy() for r in rows];mutate(changed)
        try:check(changed,inputs,logs)
        except AssertionError:mutations.append(label+': caught')
        else:raise AssertionError('silent mutation pass: '+label)
    print('PASS coverage_raw_check:',len(rows),'/',len(inputs),'organizations;',dict(result))
    print('Fetches:',len(logs),'; organizations attempted:',len(set(l['org_id'] for l in logs)),'/72; quote-positive verdicts:',sum(r['raw_check']=='yes' for r in rows),'; VERIFIED:',result['VERIFIED'],'/72')
    print('HTTP:',dict(Counter(l['http'] for l in logs))); print('Mutations:', '; '.join(mutations))
