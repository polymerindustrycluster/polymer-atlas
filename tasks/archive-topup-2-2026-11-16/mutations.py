"""Three real gate defects must fail; restore each file byte-exact."""
from common import *
from check import main

def reject(path,bad):
    before=path.read_bytes()
    try:
        path.write_bytes(bad)
        try:main(applied=False)
        except (AssertionError,ValueError,KeyError):pass
        else:raise RuntimeError('injected defect silently passed')
    finally:path.write_bytes(before)

if __name__=='__main__':
    p=HERE/'inputs.csv';reject(p,p.read_bytes().replace(b'evidence_id,',b'broken_id,',1))
    results=[p for p in PROOFS.glob('*.json') if re.fullmatch(r'[0-9a-f]{64}\.json',p.name)]
    assert results,'need at least one durable result'
    p=results[0];r=json.loads(p.read_text());r['outcomes']=[];reject(p,json.dumps(r).encode())
    r=json.loads(p.read_text());r['url']='https://example.invalid/forged';reject(p,json.dumps(r).encode())
    print('3 injected defects rejected; originals restored')
