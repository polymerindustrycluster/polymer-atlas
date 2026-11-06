"""Named L2 mutation-boundary and idempotence check; no canonical writes."""
import contextlib
import hashlib
import io
import shutil
import tempfile
from pathlib import Path
import build

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    root=build.ROOT
    with tempfile.TemporaryDirectory() as tmp:
        build.ROOT=Path(tmp);(build.ROOT/'data').mkdir()
        for name in ('sites_OH.csv','evidence_sites_OH.csv'):
            shutil.copyfile(root/'data'/name,build.ROOT/'data'/name)
        for name in ('establishments.csv','site_matches.csv'):
            p=build.ROOT/'tasks/osha-ita-2026-11-01'/name;p.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(root/'tasks/osha-ita-2026-11-01'/name,p)
        frozen={r['site_id']:r for r in build.read(build.TASK/'baseline.csv')}
        base=build.read(build.ROOT/'data/sites_OH.csv')
        base=[frozen.get(r['site_id'],r) for r in base]
        build.write(build.ROOT/'data/sites_OH.csv',base)
        ev=build.read(build.ROOT/'data/evidence_sites_OH.csv')
        build.write(build.ROOT/'data/evidence_sites_OH.csv',[r for r in ev if r['created_by']!='atlas-L2-oh-address'])
        before=build.read(build.ROOT/'data/sites_OH.csv')
        with contextlib.redirect_stdout(io.StringIO()): build.run(apply=True)
        after=build.read(build.ROOT/'data/sites_OH.csv')
        changed=0
        assert len(before)==len(after)
        for a,b in zip(before,after):
            fields={k for k in a if a[k]!=b[k]}
            assert fields <= {'street_address','sources'},(a['site_id'],fields)
            if fields:
                changed+=1
                assert not a['street_address'] and b['street_address'] and a['operating_status']=='active'
        paths=list((build.ROOT/'data').glob('*.csv'));hashes=[digest(p) for p in paths]
        with contextlib.redirect_stdout(io.StringIO()):build.run(apply=True)
        assert hashes==[digest(p) for p in paths],'not idempotent'
        # Inject a new street conflict: reapplication must refuse instead of overwriting.
        target=next(r for a,r in zip(before,after) if not a['street_address'] and r['street_address'])
        target['street_address']='999 WRONG ROAD';build.write(build.ROOT/'data/sites_OH.csv',after)
        try:
            with contextlib.redirect_stdout(io.StringIO()):build.run(apply=True)
        except AssertionError:pass
        else:raise AssertionError('injected street conflict was silently overwritten')
        print(f'PASS: {changed} fills; only street/sources change; second build byte-identical; injected street conflict refused')
    build.ROOT=root

if __name__=='__main__':main()
