"""Recompute frame, URL yield and every immutable proof binding; fail closed."""
from collections import Counter
from common import *

def main(applied=True):
    inputs=house.read(HERE/'inputs.csv')
    assert inputs==[{k:str(v) for k,v in r.items()} for r in frame()],'frozen frame changed'
    from common import FRAME_COUNTS
    assert FRAME_COUNTS==json.loads((HERE/'frame_counts.json').read_text()),'frame exclusion counts changed'
    grouped={}
    for r in inputs:grouped.setdefault(r['url'],[]).append(r)
    assert len(grouped)==1500
    results=[json.loads(p.read_text()) for p in PROOFS.glob('*.json') if re.fullmatch(r'[0-9a-f]{64}\.json',p.name)]
    assert len(results)==len({r['url'] for r in results})
    journal=[json.loads(line) for line in (PROOFS/'journal.jsonl').read_text().splitlines()]
    assert len(journal)==len(results)==len({r['url'] for r in journal}),'journal/result yield mismatch'
    ri={r['url']:r for r in results}
    assert all(j['url'] in ri and j['links']==len(ri[j['url']]['links']) and j['status']==ri[j['url']]['status'] for j in journal),'journal/result mismatch'
    current={e['evidence_id']:e for e in eligible()}
    packet=[];outcomes=[]
    for r in results:
        assert r['url'] in grouped
        expected={e['evidence_id']:e for e in grouped[r['url']]}
        assert len(r['outcomes'])==len(expected) and {o['evidence_id'] for o in r['outcomes']}==set(expected)
        links={x['evidence_id']:x for x in r['links']}
        assert len(links)==len(r['links'])
        assert set(links)=={o['evidence_id'] for o in r['outcomes'] if o['status']=='VERIFIED'}
        for eid,l in links.items():
            e=expected[eid];ref=l['archive_ref']
            assert eid in current and current[eid]['source_ref']==e['url'] and house.quote(current[eid])==e['quote'],eid
            m=re.fullmatch(r'https://web\.archive\.org/web/(\d{14})/(https?://\S+)',ref)
            assert m and same_page(m[2],e['url'])
            assert l['captured_at']==f'{m[1][:4]}-{m[1][4:6]}-{m[1][6:8]}'
            checks=[c for c in r['checks'] if c['archive_ref']==ref and c['status']=='ok' and c['http']=='200' and same_capture(c['effective_url'],ref)]
            assert checks
            proof=PROOFS/(sha(ref.encode())+'.txt')
            assert sha(proof.read_bytes())==checks[-1]['page_sha256']
            assert e['quote'] and house.on_page(e['quote'],proof)
        packet+=r['links'];outcomes+=r['outcomes']
    assert len(packet)==len({r['evidence_id'] for r in packet})
    old=house.read(HERE/'before.csv');now=house.read(ROOT/'data/archive_links.csv')
    assert len(now)==len({r['evidence_id'] for r in now})
    expected={r['evidence_id']:r for r in old+packet}
    assert len(expected)==len(old)+len(packet)
    assert all(expected[r['evidence_id']]==r for r in now)
    assert {r['evidence_id'] for r in now}==({r['evidence_id'] for r in old+packet} if applied else {r['evidence_id'] for r in old})
    counts=dict(tried_urls=len(results),archived_urls=sum(bool(r['links']) for r in results),links=len(packet),snapshots=len({r['archive_ref'] for r in packet}),worked_evidence=len(outcomes),failures=dict(Counter(o['status'] for o in outcomes if o['status']!='VERIFIED')),url_failures=dict(Counter(';'.join(sorted({o['status'] for o in r['outcomes']})) for r in results if not r['links'])),url_route_outcomes=dict(Counter(r['status'] for r in results)),replay_http_outcomes=dict(Counter(c['http'] for r in results for c in r['checks'])),pending_urls=1500-len(results))
    if applied and (HERE/'counts.json').exists():
        assert counts==json.loads((HERE/'counts.json').read_text()),'published counts differ'
    print(json.dumps(counts,sort_keys=True))
    return packet,outcomes,counts
if __name__=='__main__':main()
