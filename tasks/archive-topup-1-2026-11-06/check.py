"""Reconcile the frozen full500-row batch and immutable proof/receipt bindings."""
import hashlib
import re
from collections import Counter
from check_archives import HERE,ROOT,house,same_capture,same_page
from pathlib import Path

def main(applied=True):
    candidates=house.read(HERE/'candidates.csv')
    outcomes=house.read(HERE/'outcomes.csv')
    packet=house.read(HERE/'archive_links.csv')
    receipts=house.read(HERE/'archive_checks.csv')
    checks=house.read(HERE/'capture_checks.csv')
    before=house.read(HERE/'before.csv')
    canonical=house.read(ROOT/'data/archive_links.csv')
    verdicts=house.bound_verdicts()
    index=lambda rows:{r['evidence_id']:r for r in rows}
    for rows in (candidates,outcomes,packet,receipts,before,canonical):assert len(rows)==len(index(rows))
    ci,oi,pi,ri,bi,now=map(index,(candidates,outcomes,packet,receipts,before,canonical))
    assert len(candidates)==500
    assert set(ci)==set(oi)
    assert all(r['status'] in ('VERIFIED','FETCH_FAILED','REPLAY_REDIRECT_HOLD','QUOTE_ABSENT') and r['archive_ref']==ci[eid]['archive_ref'] for eid,r in oi.items())
    assert set(pi)==set(ri)=={eid for eid,r in oi.items() if r['status']=='VERIFIED'}
    assert pi and len(pi)<=500 and not set(pi)&set(bi)
    assert set(now)==set(bi)|set(pi) if applied else set(now) in (set(bi),set(bi)|set(pi))
    assert all(now[eid]==r for eid,r in bi.items()),'old link changed'
    assert all(ci[eid]==r and (eid not in now or now[eid]==r) for eid,r in pi.items()),'packet/canonical changed'
    refs={r['archive_ref']:r for r in checks}
    assert len(refs)==len(checks) and set(refs)=={r['archive_ref'] for r in candidates}
    digest=hashlib.sha256((HERE/'archive_links.csv').read_bytes()).hexdigest()
    for eid,r in pi.items():
        v=verdicts[eid];rc=ri[eid];f=refs[r['archive_ref']]
        assert v['judgment']=='SUPPORTED' and v['quote']
        m=re.fullmatch(r'https://web\.archive\.org/web/(\d{14})/(https?://\S+)',r['archive_ref'])
        assert m and same_page(m[2],v['source_ref'])
        assert f['status']=='ok' and f['http']=='200' and same_capture(f['effective_url'],r['archive_ref'])
        assert f['checked_at']==rc['checked_at'] and rc['archive_ref']==r['archive_ref']
        assert rc['packet_sha256']==digest and rc['quote_sha256']==hashlib.sha256(v['quote'].encode()).hexdigest()
        proof=Path(f['proof'])
        assert hashlib.sha256(proof.read_bytes()).hexdigest()==f['page_sha256']
        assert house.on_page(v['quote'],proof)
    print('Topup:',len(pi),'new links /',len({r['archive_ref'] for r in packet}),'captures;',len(outcomes)-len(pi),'held /',len(candidates),'frozen candidates')
    print('Outcomes:',dict(Counter(r['status'] for r in outcomes)))
    print('Prior',len(bi),'links preserved; canonical',len(now),'links; canonical quote/proof hashes PASS')

if __name__=='__main__':main()
