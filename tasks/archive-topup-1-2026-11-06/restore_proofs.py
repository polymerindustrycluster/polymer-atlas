"""Rebuild the 42 immutable proof bodies by re-fetching each Wayback capture, one at a time.

Writes <PROOFS>/<sha256(archive_ref)>.txt only when the body's sha256 equals the recorded page_sha256;
a differing body goes to <name>.mismatch.txt and is reported row by row. Never edits data/ or the CSVs.
"""
import hashlib
import sys
import time
from check_archives import HERE,ROOT,PROOFS,house,same_capture

sha=lambda b:hashlib.sha256(b).hexdigest()
house.CACHE=ROOT/'build/l1-topup-1-restore-cache'
house.CACHE.mkdir(parents=True,exist_ok=True)

def main():
    rows=house.read(HERE/'capture_checks.csv');log=[];bad=0
    for n,r in enumerate(rows,1):
        ref=r['archive_ref'];proof=PROOFS/(sha(ref.encode())+'.txt')
        if r['status']!='ok':
            print(n,'SKIP recorded',r['status'],ref);continue
        if proof.exists() and sha(proof.read_bytes())==r['page_sha256']:
            print(n,'HAVE',ref);continue
        for attempt in range(3):
            time.sleep(5)
            f=house.fetch(ref,refresh=True,fallback=False);a=f['attempts'][-1]
            if f['status']=='ok':break
            if attempt<2:time.sleep(max(60*2**attempt,a.get('retry_after',0)) if a['status']=='429' else 10)
        if f['status']!='ok':
            bad+=1;print(n,'FETCH_FAILED http',a['status'],'exit',a['exit'],ref,flush=True)
            log.append((ref,r['page_sha256'],'','FETCH_FAILED'));continue
        body=(ROOT/f['page']).read_bytes();got=sha(body)
        ok=got==r['page_sha256'] and same_capture(a['effective_url'],ref)
        (proof if ok else proof.with_suffix('.mismatch.txt')).write_bytes(body)
        if not ok:bad+=1
        print(n,'OK' if ok else 'MISMATCH',ref,'recorded',r['page_sha256'][:12],'got',got[:12],'effective',a['effective_url'],flush=True)
        log.append((ref,r['page_sha256'],got,'OK' if ok else 'MISMATCH'))
    house.write(PROOFS/'restore_log.csv',[dict(archive_ref=a,recorded=b,recomputed=c,result=d) for a,b,c,d in log],['archive_ref','recorded','recomputed','result'])
    print('restored',sum(d=='OK' for *_,d in log),'; not restored',bad,'of',len(rows),'capture rows')
    return bad

if __name__=='__main__':sys.exit(1 if main() else 0)
