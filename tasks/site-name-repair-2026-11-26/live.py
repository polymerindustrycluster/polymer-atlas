#!/usr/bin/env python3
"""Live capture screen: fetch each site's own pages with the binding gate's own fetcher (fetch_url: HTTPS, status 200 only, no
redirect, UA evidence-check/1), and keep a hit only where the main text the gate reads carries the printed name and the street
together. A page that fetches differently twice is dropped (the gate fetches again at merge). One row per site, to --out.
Usage: live.py --sites ID,ID --out FILE [--extra-paths]"""
import argparse, csv, glob, hashlib, re, sys, time
from pathlib import Path
from urllib.parse import urlsplit
sys.path.insert(0, str(Path(__file__).parent)); sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import candidates as c  # noqa: E402
from atlas import squash  # noqa: E402
import check_evidence_binding as g  # noqa: E402

PATHS = ['/', '/contact', '/contact/', '/contact-us', '/contact-us/', '/about', '/about-us', '/about-us/', '/locations', '/location']


def span(ct, m, run):
    a = ct.rfind(run, 0, m.start()) if run else -1
    if a < 0: return None
    tail = re.match(r"[^A-Za-z0-9]{0,6}(?:[A-Za-z .'-]+?)[,. ]+(?:OH|Ohio)[,. ]*\d{5}(?:-\d{4})?", ct[m.end():m.end() + 80])
    b = m.end() + (tail.end() if tail else 0)
    q = ct[a:b]
    while q and q.split(' ', 1)[0].lower().strip('.:') in c.STOP and ' ' in q:  # leading nav or label word
        a += len(q.split(' ', 1)[0]) + 1; q = ct[a:b]
    return q, a


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--sites', required=True); ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    sites = {r['site_id']: r for p in glob.glob(str(c.ROOT / 'data/sites_*.csv')) for r in c.read(p)}
    orgs = {r['org_id']: r for p in glob.glob(str(c.ROOT / 'data/organizations_*.csv')) for r in c.read(p)}
    pages = c.load_pages(c.CORPORA); rows = []; last = {}
    for sid in a.sites.split(','):
        s = sites[sid]; o = orgs[s['org_id']]; own = c.own_pages(o, pages.get(s['org_id'], []))
        rx, names, own_names, city = c.street_regex(s['street_address']), c.held_names(s, o), c.held_names(s, o, True), squash(s['city'])
        urls = list(dict.fromkeys([p['asked'] for p in own] + [p['url'] for p in own] + [f"{urlsplit(p['asked']).scheme}://{urlsplit(p['asked']).netloc}{x}" for p in own[:1] for x in PATHS]))
        best, tried = None, []
        for u in urls:
            if not u.startswith('https://'): continue
            host = urlsplit(u).netloc; time.sleep(max(0, 1.0 - (time.time() - last.get(host, 0)))); last[host] = time.time()
            try: data = g.fetch_url(u)
            except Exception as e: tried.append(f'{u[-40:]}:{str(e)[:30]}'); continue
            ct = g.capture_text(data)
            for m in (rx.finditer(ct) if rx else ()):
                if city not in squash(ct[max(0, m.start() - 150):m.end() + 150]): continue
                j = c.judge(ct[max(0, m.start() - c.BEFORE):m.start()], ct[m.end():m.end() + c.AFTER], names, own_names, city)
                sp = span(ct, m, j['printed'])
                if not sp or g.web_street_reason(s['street_address'], sp[0]): continue
                row = dict(site_id=sid, held=s['site_name'], printed=j['printed'], kind=j['kind'], url=u, sha256=hashlib.sha256(data).hexdigest(), quote=sp[0], offset=sp[1])
                if best is None or (len(best['printed']) == 0, c.RANK_KIND.get(best['kind'], 3)) > (len(row['printed']) == 0, c.RANK_KIND.get(row['kind'], 3)): best = row
        if best:
            time.sleep(1.0)
            try: best['stable'] = hashlib.sha256(g.fetch_url(best['url'])).hexdigest() == best['sha256']
            except Exception: best['stable'] = False
            rows.append(best); print(sid, best['kind'] or '-', best['stable'], '|', best['quote'][:110], '|', best['url'], flush=True)
        else: print(sid, 'NO LIVE HIT', '; '.join(tried[:4]), flush=True)
    if rows:
        with open(a.out, 'w', newline='') as f:
            w = csv.DictWriter(f, list(rows[0])); w.writeheader(); w.writerows(rows)


if __name__ == '__main__': main()
