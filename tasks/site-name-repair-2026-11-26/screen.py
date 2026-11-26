#!/usr/bin/env python3
"""Gate-aware screen of the candidates: which retained own page prints the street in the main text the binding gate reads
(`capture_text`: footers, headers and navigation are excluded), and what run is printed before it. Offline: stored page bytes only.
Usage: screen.py [--sites ID,ID,...]   one line per site; sites with no main-text street hit are listed apart."""
import argparse, csv, glob, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent)); sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import candidates as c  # noqa: E402
from atlas import squash  # noqa: E402
import check_evidence_binding as g  # noqa: E402

RANK = {'D': 0, 'A': 1, 'E': 2, '': 3}


def quote_for(text, m, run):
    """Verbatim span of the capture's main text: the printed run, the street, and the place line up to the ZIP when it follows."""
    a = text.rfind(run, 0, m.start()) if run else m.start()
    tail = re.match(r"[^A-Za-z0-9]{0,6}(?:[A-Za-z .'-]+?)[,. ]+(?:OH|Ohio)[,. ]*\d{5}(?:-\d{4})?", text[m.end():m.end() + 80])
    b = m.end() + (tail.end() if tail else 0)
    return text[a:b], a


def screen(ids=None):
    sites = {r['site_id']: r for p in glob.glob(str(c.ROOT / 'data/sites_*.csv')) for r in c.read(p)}
    orgs = {r['org_id']: r for p in glob.glob(str(c.ROOT / 'data/organizations_*.csv')) for r in c.read(p)}
    roots = {p.name: p for p in c.CORPORA}
    pages = c.load_pages(c.CORPORA)
    out, none = [], []
    for sid in ids:
        s = sites[sid]; o = orgs[s['org_id']]
        rx, names, own_names, city = c.street_regex(s['street_address']), c.held_names(s, o), c.held_names(s, o, True), squash(s['city'])
        best = None
        for p in c.own_pages(o, pages.get(s['org_id'], [])):
            if not p['raw_file']: continue  # reader-route pages carry text only
            try: ct = g.capture_text((roots[p['corpus']] / p['raw_file']).read_bytes())
            except Exception: continue
            for m in (rx.finditer(ct) if rx else ()):
                if city not in squash(ct[max(0, m.start() - 150):m.end() + 150]): continue
                before = ct[max(0, m.start() - c.BEFORE):m.start()]
                j = c.judge(before, ct[m.end():m.end() + c.AFTER], names, own_names, city)
                q, off = quote_for(ct, m, j['printed'])
                row = dict(site_id=sid, held=s['site_name'], printed=j['printed'], kind=j['kind'], url=p['url'], asked=p['asked'], quote=q, offset=off,
                           street_ok=g.web_street_reason(s['street_address'], q) == '', capture_sha=p['sha256'])
                if best is None or (RANK[row['kind']], not row['street_ok']) < (RANK[best['kind']], not best['street_ok']): best = row
        (out if best else none).append(best or dict(site_id=sid, held=s['site_name']))
    return out, none


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--sites'); ap.add_argument('--out', type=Path)
    a = ap.parse_args()
    d = Path(__file__).parent
    ids = a.sites.split(',') if a.sites else sorted({r['site_id'] for r in c.read(d / 'CANDIDATES.csv')} | {r['site_id'] for r in c.read(d / 'PILOT.csv') if r['verdict'] != 'REJECT'} | set(c.KNOWN))
    out, none = screen(ids)
    print(len(ids), 'sites;', len(out), 'with a main-text street hit;', len(none), 'without')
    for r in out: print(f"{r['site_id']}|{r['kind'] or '-'}|{'ok' if r['street_ok'] else 'street?'}|held: {r['held']}|run: {r['printed']}|{r['url']}")
    print('NO MAIN-TEXT HIT:', ' '.join(r['site_id'] for r in none))
    if a.out:
        with open(a.out, 'w', newline='') as f:
            w = csv.DictWriter(f, list(out[0])); w.writeheader(); w.writerows(out)


if __name__ == '__main__': main()
