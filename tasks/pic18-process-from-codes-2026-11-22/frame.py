"""Shared frame + material readers for the process-in-hand packet (Part A). Read-only; no data/ writes."""
import csv, glob, collections, re, sys, random
from pathlib import Path
T = Path(__file__).resolve().parent
ROOT = T.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from regions import PIC18  # noqa: E402
# (corpus path unused in Part B)
CORPUS = Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/pic18-corpus-2026-11-16')
SEED = 20261122

def rd(pat):
    return [r for f in sorted(glob.glob(str(ROOT / pat))) for r in csv.DictReader(open(f, newline='', encoding='utf-8'))]

def toks(v):
    return {t.strip() for t in (v or '').split(';') if t.strip() and t.strip() != 'unknown'}

def load():
    orgs = {o['org_id']: o for o in rd('data/organizations_*.csv')}
    eco = {o['org_id']: o for o in rd('data/ecosystem.csv')}
    sites_all = rd('data/sites_*.csv')
    active_by_org = collections.Counter(s['org_id'] for s in sites_all if s['operating_status'] == 'active')
    g = collections.defaultdict(list)
    for s in sites_all:
        if s['state'] == 'OH' and s['county'] in PIC18 and s['operating_status'] == 'active' and s['verification_tier'] in ('A', 'B', 'C'):
            g[s['org_id']].append(s)
    unk = [o for o, ss in g.items()
           if not (set().union(*(toks(s['processes']) for s in ss)) or toks((orgs.get(o) or eco.get(o) or {}).get('processes')))]
    frame = sorted((s for o in unk for s in g[o]), key=lambda s: s['site_id'])
    return dict(orgs=orgs, eco=eco, g=g, unk=sorted(unk), frame=frame, active_by_org=active_by_org)

def sample(frame, n=25):
    return random.Random(SEED).sample(frame, n)

def vocab():
    import json
    v = json.load(open(ROOT / 'docs/schema/vocab.json'))
    return v

def pages(org_id):
    """Stored 2026-11-16 corpus pages with a text file for one organization (both passes)."""
    out = []
    for r in csv.DictReader(open(CORPUS / 'manifest.csv', newline='')):
        if r['org_id'] == org_id and r['text_file']:
            out.append(r)
    return out

def norm(s):
    return ' '.join(s.split())
