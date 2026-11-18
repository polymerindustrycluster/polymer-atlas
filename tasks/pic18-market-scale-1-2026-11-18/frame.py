"""Market-scale frame, recomputed from git at FRAME_REF with the canary's pool definition (briefs draw_frames.py / pic18_unknown.py logic, verbatim):
PIC-18 organization with an active A-C Ohio site, market unknown at both grains (site union, then the organization cell), MKT3 `not_adjudicated`,
and at least one stored corpus text page of 1 KB or more (not a GIF). The canary's 10 frame organizations are removed."""
import csv
import io
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from regions import PIC18

FRAME_REF = 'e1df30e4'  # main after the canary merged (#385)
CORPUS = Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/pic18-corpus-2026-11-16')
CANARY = 'ORG-000043 ORG-000087 ORG-000157 ORG-000469 ORG-000508 ORG-001380 ORG-001422 ORG-001504 ORG-001892 ORG-002136'.split()
EXPECTED = 191


def show(path, ref=FRAME_REF):
    return subprocess.run(['git', '-C', str(ROOT), 'show', f'{ref}:{path}'], capture_output=True, text=True, check=True).stdout


def rows(prefix, ref=FRAME_REF):
    names = subprocess.run(['git', '-C', str(ROOT), 'ls-tree', '--name-only', ref, 'data/'], capture_output=True, text=True, check=True).stdout.split()
    return [r for f in names if f.split('/')[-1].startswith(prefix) for r in csv.DictReader(io.StringIO(show(f, ref)))]


def toks(v):
    return {t.strip() for t in (v or '').split(';') if t.strip() and t.strip() != 'unknown'}


def readable(oid):
    d = CORPUS / oid
    return d.is_dir() and any(p.stat().st_size >= 1000 and p.read_bytes()[:6] not in (b'GIF89a', b'GIF87a') for p in d.glob('*.txt'))


def market_pool(ref=FRAME_REF):
    orgs = {o['org_id']: o for o in rows('organizations_', ref)}
    eco = {o['org_id']: o for o in rows('ecosystem.csv', ref)}
    sites = {}
    for s in rows('sites_', ref):
        if s['state'] == 'OH' and s['county'] in PIC18 and s['operating_status'] == 'active' and s['verification_tier'] and s['verification_tier'] in 'ABC':
            sites.setdefault(s['org_id'], []).append(s)
    unknown = [oid for oid, ss in sites.items() if not (set().union(*(toks(s['markets_served']) for s in ss)) or toks((orgs.get(oid) or eco.get(oid) or {}).get('markets_served')))]
    mkt3 = {r['org_id'] for r in csv.DictReader(io.StringIO(show('tasks/pic18-markets-3-2026-11-16/holds.csv', ref))) if r.get('hold_class') == 'not_adjudicated'}
    return sorted(o for o in unknown if o in mkt3 and readable(o))


def frame(ref=FRAME_REF):
    pool = market_pool(ref)
    out = [o for o in pool if o not in CANARY]
    return out


if __name__ == '__main__':
    f = frame()
    assert len(f) == EXPECTED, ('frame count changed', len(f))
    print(len(market_pool()), len(f), f[0], f[95], f[96], f[-1])
