#!/usr/bin/env python3
"""Fresh capture of one page per site with the binding gate's own fetcher, twice (bytes must be identical), then the quote and its
offset in capture_text(). Writes the bytes to the shared store (provenance/site-name-repair-2026-11-26/captures/<sha256>.html) and
a JSON line per site. Usage: capture.py --out FILE SITE_ID=URL ..."""
import argparse, hashlib, json, os, re, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent)); sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import candidates as c  # noqa: E402
from atlas import squash  # noqa: E402
import check_evidence_binding as g  # noqa: E402

STORE = Path('/Volumes/johnpswan/work/GAC/polymer-atlas/atlas-store/provenance/site-name-repair-2026-11-26/captures')


def span(ct, m, run):
    toks = run.split()
    hits = list(re.finditer(r'[^A-Za-z0-9]+'.join(map(re.escape, toks)), ct[:m.start()])) if toks else []
    if not hits: return None
    a = hits[-1].start()
    tail = re.match(r"[^A-Za-z0-9]{0,6}(?:[A-Za-z .'-]+?)[,. ]+(?:OH|Ohio)[,. ]*\d{5}(?:-\d{4})?", ct[m.end():m.end() + 80])
    q = ct[a:m.end() + (tail.end() if tail else 0)]
    while ' ' in q and q.split(' ', 1)[0].lower().strip('.:') in c.STOP | {'submit'}:  # a leading nav or button word
        a += len(q.split(' ', 1)[0]) + 1; q = ct[a:a + len(q) - len(q.split(' ', 1)[0]) - 1]
    return q, a


def main():
    import glob
    ap = argparse.ArgumentParser(); ap.add_argument('--out', type=Path, required=True); ap.add_argument('pairs', nargs='+')
    a = ap.parse_args()
    sites = {r['site_id']: r for p in glob.glob(str(c.ROOT / 'data/sites_*.csv')) for r in c.read(p)}
    orgs = {r['org_id']: r for p in glob.glob(str(c.ROOT / 'data/organizations_*.csv')) for r in c.read(p)}
    STORE.mkdir(parents=True, exist_ok=True); out = []
    for pair in a.pairs:
        sid, url = pair.split('=', 1); s = sites[sid]; o = orgs[s['org_id']]
        d1 = g.fetch_url(url); time.sleep(1.5); d2 = g.fetch_url(url)
        sha = hashlib.sha256(d1).hexdigest()
        if d1 != d2: print(sid, 'UNSTABLE bytes, skipped'); continue
        ct = g.capture_text(d1); rx, city = c.street_regex(s['street_address']), squash(s['city'])
        names, own_names = c.held_names(s, o), c.held_names(s, o, True); found = []
        for m in rx.finditer(ct):
            if city not in squash(ct[max(0, m.start() - 150):m.end() + 150]): continue
            j = c.judge(ct[max(0, m.start() - c.BEFORE):m.start()], ct[m.end():m.end() + c.AFTER], names, own_names, city)
            sp = span(ct, m, j['printed'])
            if sp and not g.web_street_reason(s['street_address'], sp[0]) and ct[sp[1]:sp[1] + len(sp[0])] == sp[0]: found.append((j, sp))
        if not found: print(sid, 'no quote in main text'); continue
        j, (q, off) = found[0]
        (STORE / f'{sha}.html').write_bytes(d1)
        out.append(dict(site_id=sid, org_id=s['org_id'], held=s['site_name'], printed=j['printed'], url=url, capture_sha256=sha, quote=q, offset=off, capture_date=time.strftime('%Y-%m-%d'), n_hits=len(found)))
        print(sid, '|', q, '|', url, '| hits', len(found), flush=True)
    a.out.write_text('\n'.join(json.dumps(r) for r in out) + '\n')


if __name__ == '__main__': main()
