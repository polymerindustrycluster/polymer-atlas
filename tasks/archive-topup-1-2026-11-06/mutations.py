"""Check missing receipt, forged packet and substituted proof fail BEFORE canonical writes."""
import subprocess
import sys
from check_archives import HERE,ROOT,house

def reject(name,mutate):
    target=HERE/name
    before=target.read_bytes()
    canonical=(ROOT/'data/archive_links.csv').read_bytes()
    try:
        rows=house.read(target);fields=list(rows[0]);mutate(rows)
        house.write(target,rows,fields)
        r=subprocess.run([sys.executable,str(HERE/'build.py')],capture_output=True,text=True)
        assert r.returncode!=0 and 'AssertionError' in r.stderr,(name,r.stdout,r.stderr)
        assert (ROOT/'data/archive_links.csv').read_bytes()==canonical,'rejection wrote canonical data'
        print(name,'injected fault rejected before writes')
    finally:target.write_bytes(before)

reject('archive_checks.csv',lambda r:r.pop())
reject('archive_links.csv',lambda r:r[0].update(archive_ref=r[0]['archive_ref']+'?forged=1'))
reject('capture_checks.csv',lambda r:r[0].update(page_sha256='0'*64))
print('3 real-builder no-write mutations PASS')
