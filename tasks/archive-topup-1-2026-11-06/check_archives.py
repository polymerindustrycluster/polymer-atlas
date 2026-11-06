#!/usr/bin/env python3
"""Freeze up to500 candidates, freshly qualify each, and record every excluded row."""
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BASE=ROOT/'tasks/evidence-reverify-archive-2026-11-06'
sys.path.insert(0,str(BASE))
import run as house
from archive import same_page,same_capture,FIELDS
house.CACHE=ROOT/'build/l1-topup-1-cache'
house.CACHE.mkdir(exist_ok=True)
# Proof bodies survive worktree teardown here; override with ARCHIVE_TOPUP_PROOFS. restore_proofs.py rebuilds them from Wayback.
PROOFS=Path(os.environ.get('ARCHIVE_TOPUP_PROOFS','/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/archive-topup-1'))
PROOFS.mkdir(parents=True,exist_ok=True)


def main():
    frozen=(HERE/'candidates.csv').read_bytes()
    rows=house.read(HERE/'candidates.csv')
    verdicts=house.bound_verdicts()
    assert 0<len(rows)<=500 and len(rows)==len({r['evidence_id'] for r in rows})
    house.write(HERE/'archive_checks.csv',[],['evidence_id','archive_ref','quote_sha256','packet_sha256','checked_at'])
    pages={};passed=[];outcomes=[];observations=[]
    for r in rows:
        eid,ref=r['evidence_id'],r['archive_ref'];v=verdicts[eid]
        m=re.fullmatch(r'https://web\.archive\.org/web/(\d{14})/(https?://\S+)',ref)
        assert m and same_page(m[2],v['source_ref']) and v['judgment']=='SUPPORTED' and v['quote'],eid
        assert r['captured_at']==f'{m[1][:4]}-{m[1][4:6]}-{m[1][6:8]}',eid
        if ref not in pages:
            time.sleep(5)
            for attempt in range(3):
                f=house.fetch(ref,refresh=True,fallback=False)
                if f['status']=='ok':break
                if attempt<2:
                    a=f['attempts'][-1]
                    time.sleep(max(60*2**attempt,a.get('retry_after',0)) if a['status']=='429' else 10)
            proof=PROOFS/(hashlib.sha256(ref.encode()).hexdigest()+'.txt')
            if f['status']=='ok':proof.write_bytes((ROOT/f['page']).read_bytes())
            pages[ref]=(f,proof)
            observations.append(dict(archive_ref=ref,status=f['status'],effective_url=f['attempts'][-1]['effective_url'],checked_at=f['fetched_at'],page_sha256=hashlib.sha256(proof.read_bytes()).hexdigest() if f['status']=='ok' else '',proof=str(proof),http=f['attempts'][-1]['status']))
            house.write(HERE/'capture_checks.csv',observations,list(observations[0]))
            print('fresh captures',len(pages),'/',len({x['archive_ref'] for x in rows}),flush=True)
        f,proof=pages[ref]
        if f['status']!='ok':status='FETCH_FAILED'
        elif not same_capture(f['attempts'][-1]['effective_url'],ref):status='REPLAY_REDIRECT_HOLD'
        elif not house.on_page(v['quote'],proof):status='QUOTE_ABSENT'
        else:status='VERIFIED'
        outcomes.append(dict(evidence_id=eid,archive_ref=ref,status=status))
        if status=='VERIFIED':passed.append(r)
    assert (HERE/'candidates.csv').read_bytes()==frozen,'candidates changed during gate'
    house.write(HERE/'archive_links.csv',sorted(passed,key=lambda r:r['evidence_id']),FIELDS)
    house.write(HERE/'outcomes.csv',outcomes,['evidence_id','archive_ref','status'])
    packet_hash=hashlib.sha256((HERE/'archive_links.csv').read_bytes()).hexdigest()
    receipts=[dict(evidence_id=r['evidence_id'],archive_ref=r['archive_ref'],quote_sha256=hashlib.sha256(verdicts[r['evidence_id']]['quote'].encode()).hexdigest(),packet_sha256=packet_hash,checked_at=pages[r['archive_ref']][0]['fetched_at']) for r in passed]
    house.write(HERE/'archive_checks.csv',receipts,['evidence_id','archive_ref','quote_sha256','packet_sha256','checked_at'])
    assert len(outcomes)==len(rows) and len({r['evidence_id'] for r in outcomes})==len(rows)
    print('fresh gate',len(passed),'VERIFIED,',len(rows)-len(passed),'held /',len(rows),'candidates',flush=True)
    assert passed,'No newly verified archive; cannot apply an empty topup'


if __name__=='__main__':main()
