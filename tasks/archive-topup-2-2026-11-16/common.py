"""Reuse the top-up 1 transport, quote matcher and exact replay admission rule."""
import csv, io, hashlib, json, re, sys, os, subprocess
from urllib.parse import urlsplit
from types import SimpleNamespace
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'tasks/evidence-reverify-archive-2026-11-06'))
import run as house
import discovery
from archive import FIELDS,same_page,same_capture
PROOFS=Path(os.environ.get('ARCHIVE_TOPUP_PROOFS','/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/archive-topup-2'))
PROOFS.mkdir(parents=True,exist_ok=True)
house.CACHE=ROOT/('build/archive-topup-2-cache'+os.environ.get('ARCHIVE_WORKER',''))
house.CACHE.mkdir(parents=True,exist_ok=True)
discovery.CACHE=house.CACHE
def byte_run(args, **kwargs):
    kwargs.pop('text',None)
    result=subprocess.run(args,**kwargs)
    for attr in ('stdout','stderr'):
        value=getattr(result,attr)
        if isinstance(value,bytes):setattr(result,attr,value.decode('utf-8',errors='replace'))
    return result
house.subprocess=discovery.subprocess=SimpleNamespace(run=byte_run)
def valid_url(url):
    try:
        p=urlsplit(url)
        return p.scheme in ('http','https') and bool(p.hostname) and not any(c.isspace() for c in url)
    except ValueError:return False
sha=lambda b:hashlib.sha256(b).hexdigest()
FRAME_COUNTS={}
FRAME_BASE='be2e6084d430f1e6f9de0f66289b1d3c2570e255'

def eligible(base=None):
    def read_at(path):
        if base is None:return house.read(ROOT/path)
        raw=subprocess.check_output(['git','show',f'{base}:{path}'],cwd=ROOT)
        return list(csv.DictReader(io.StringIO(raw.decode('utf-8'),newline='')))
    if base is None:
        shards=[p.relative_to(ROOT).as_posix() for p in (ROOT/'data').glob('evidence_*.csv')]
    else:
        listing=subprocess.check_output(['git','ls-tree','-r','--name-only',base,'data'],cwd=ROOT,text=True)
        shards=[p for p in listing.splitlines() if re.fullmatch(r'data/evidence_.*\.csv',p)]
    sites=read_at('data/sites_OH.csv')
    si={r['site_id'] for r in sites if r['state']=='OH' and re.sub(r' County$','',r['county']) in house.PIC18}
    oi={r['org_id'] for r in sites if r['site_id'] in si}
    old={r['evidence_id'] for r in house.read(HERE/'before.csv')}
    return [r for path in shards for r in read_at(path) if r['source_class']=='own_site' and r['evidence_id'] not in old and ((r['record_table']=='sites' and r['record_id'] in si) or (r['record_table']=='organizations' and r['record_id'] in oi))]

def frame():
    rows=eligible(FRAME_BASE)
    assert len(rows)==len({r['evidence_id'] for r in rows})
    FRAME_COUNTS.update(eligible_evidence_rows=len(rows),not_a_url_evidence_rows=sum(not valid_url(r['source_ref']) for r in rows))
    selected={};out=[]
    for r in sorted(rows,key=lambda r:r['evidence_id']):
        url=r['source_ref']
        if not valid_url(url):continue
        if url not in selected and len(selected)<1500:selected[url]=len(selected)+1
        if url in selected:out.append(dict(evidence_id=r['evidence_id'],url=url,quote=house.quote(r),url_order=selected[url]))
    assert all(valid_url(r['url']) for r in out)
    return out
