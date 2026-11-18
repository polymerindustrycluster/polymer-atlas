#!/usr/bin/env python3
"""Recompute every published count, compare yield with an independent count of the input, re-verify
every witness quote against its stored raw page, scan committed files for lead names and URLs, and
prove the checks fail on injected defects. Names, URLs and quotes live only in controller storage."""
import copy, csv, glob, hashlib, re, subprocess, sys
from pathlib import Path
from urllib.parse import urlsplit
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build import ROOT, read, counts, used_ids
S = Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist')
PRIV = S / 'pic18-discovery-2' / 'private'
words = lambda t: re.findall(r'[a-z0-9]+', t.lower())
# generic words and common place names that may appear in prose; everything else from a lead name is a leak term
STOP = set('inc llc ltd lp co corp corporation company the of and international products industries industrial chemical chemicals plastic plastics technologies technology systems group manufacturing services supply american north laboratories energy finishing coatings polymer controls packaging imaging transportation specialty specialties quality universal worldwide solutions rubber holdings ohio cleveland akron vinyl metal search general dealer'.split())
# Held-record facts each verdict relies on: (table, id, column, substring that must be present)
TARGET_FACTS = {'1': ('sites', 'SITE-000445', 'street_address', '215 Sinter'), '28': ('sites', 'SITE-000116', 'street_address', '1400 E. 222nd'),
                '39': ('sites', 'SITE-000357', 'street_address', 'FIGGIE'), '41': ('sites', 'SITE-000228', 'street_address', '951 Jaycox'),
                '43': ('organizations', 'ORG-001597', 'hq_city', 'Niles'), '59': ('sites', 'SITE-001777', 'notes', '2926 Chester'),
                '18': ('sites', 'SITE-000928', 'notes', '509 Water'), '80': ('organizations', 'ORG-000140', 'hq_city', 'Cleveland')}

def load_data():
    return {t: {r[k]: r for p in glob.glob(str(ROOT / 'data' / f'{t}_*.csv')) for r in read(Path(p))}
            for t, k in (('organizations', 'org_id'), ('sites', 'site_id'))}

def leak_terms(frame, vfull, wfull):
    """Private name list: lead names (phrase and distinctive tokens), own-site names, URL hosts."""
    names = [r['name'] for r in frame] + [r['own_site_name'] for r in vfull if r['own_site_name']]
    terms = set()
    for n in names:
        ws = [x for x in words(n) if x not in STOP]
        if len(ws) >= 2: terms.add(' '.join(ws))
        terms |= {x for x in ws if len(x) >= 5}
    urls = [w['url'] for w in wfull] + re.findall(r'https?://[^\s)]+', ' '.join(r['url_provenance'] for r in vfull))
    hosts = {urlsplit(u).netloc.lower().removeprefix('www.') for u in urls} - {''}
    return terms, hosts

def leaks(texts, terms, hosts):
    out = []
    for name, t in texts.items():
        norm = ' ' + ' '.join(words(t)) + ' '
        out += [f'{name}: lead term {x!r}' for x in terms if f' {x} ' in norm]
        out += [f'{name}: lead URL host {h!r}' for h in hosts if h in t.lower()]
    return out

def check(verdicts, wpub, data, prior, frame, readme, vfull, wfull, texts):
    errs = []
    expect = {r['rank'] for r in frame} - {r['rank'] for r in prior if r['verdict'] == 'DUPLICATE_OF'}
    got = [v['rank'] for v in verdicts]
    if len(got) != len(set(got)) or set(got) != expect or len(expect) != 72: errs.append(f'yield: {len(got)} verdict rows vs {len(expect)} held leads')
    if {(r['rank'], r['verdict'], r['target_record']) for r in vfull} != {(r['rank'], r['verdict'], r['target_record']) for r in verdicts}: errs.append('committed verdicts drift from private table')
    c = counts(verdicts)
    if f"{c['leads_adjudicated']} held leads adjudicated" not in readme or any(f'{k} {n}' not in readme.replace(':', '') for k, n in c['by_verdict'].items()):
        errs.append(f'README counts do not match recomputed {c}')
    if c['applied'] or c['data_rows_added']: errs.append('this pass must apply zero rows')
    wmap, pub = {w['witness_id']: w for w in wfull}, {w['witness_id']: w for w in wpub}
    if set(pub) != set(wmap) or any(pub[k]['sha256'] != wmap[k]['sha256'] or pub[k]['rank'] != wmap[k]['rank'] for k in pub): errs.append('committed witnesses drift from private table')
    for v in verdicts:
        for wid in filter(None, v['witness_ids'].split(';')):
            w = wmap.get(wid)
            if not w: errs.append(f'rank {v["rank"]}: unknown witness {wid}'); continue
            html = S / w['raw_file']
            if not html.exists() or hashlib.sha256(html.read_bytes()).hexdigest() != w['sha256']: errs.append(f'{wid}: raw page missing or hash drift'); continue
            tw, qw = words(html.with_suffix('.txt').read_text()), words(w['quote'])
            if not any(tw[i:i + len(qw)] == qw for i in range(len(tw))): errs.append(f'{wid}: quote not on stored page')
        if not v['url_provenance']: errs.append(f'rank {v["rank"]}: no url_provenance')
        if v['witness_ids'] and v['url_provenance'] == 'none': errs.append(f'rank {v["rank"]}: witness on a URL with no provenance')
        if v['verdict'] == 'REJECT' and not v['witness_ids']: errs.append(f'rank {v["rank"]}: REJECT without a quoted deciding fact')
        for tid in filter(None, v['target_record'].split(';')):
            if tid not in data['organizations'] and tid not in data['sites']: errs.append(f'rank {v["rank"]}: target {tid} not in data/')
        if v['verdict'] == 'DUPLICATE_OF' and not v['target_record']: errs.append(f'rank {v["rank"]}: DUPLICATE_OF without a target')
    for rank, (tbl, rid, col, sub) in TARGET_FACTS.items():
        row = data[tbl].get(rid)
        if not row or sub not in row[col]: errs.append(f'rank {rank}: held {rid}.{col} no longer contains {sub!r}')
    if used_ids(): errs.append(f'IDs in reserved blocks already used: {used_ids()}')
    terms, hosts = leak_terms(frame, vfull, wfull)
    if len(terms) < 40 or not hosts: errs.append(f'leak scan has too few private terms ({len(terms)} terms, {len(hosts)} hosts)')
    errs += leaks(texts, terms, hosts)
    return errs

def main():
    verdicts, wpub = read(HERE / 'verdicts.csv'), read(HERE / 'witnesses.csv')
    vfull, wfull = read(PRIV / 'verdicts_full.csv'), read(PRIV / 'witnesses_full.csv')
    data, prior = load_data(), read(PRIV / 'prior_pr356_verdicts.csv')
    frame, readme = read(S / 'pic18-discovery-leads' / 'frame.csv'), (HERE / 'README.md').read_text()
    texts = {p.name: p.read_text() for p in HERE.iterdir() if p.is_file() and p.suffix in {'.md', '.csv', '.py', '.json', '.txt'}}
    assert len(frame) == 80 and len(prior) == 80
    errs = check(verdicts, wpub, data, prior, frame, readme, vfull, wfull, texts)
    print('real check:', 'FAIL ' + str(errs) if errs else 'ok', f'({len(verdicts)} verdicts, {len(wpub)} witnesses, {len(texts)} files scanned for leaks)')
    base = subprocess.run(['git', 'merge-base', 'origin/main', 'HEAD'], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    diff = subprocess.run(['git', 'diff', '--name-only', base, '--', 'data'], cwd=ROOT, capture_output=True, text=True).stdout.split()
    if diff: errs.append(f'data/ files changed: {diff}')
    terms, hosts = leak_terms(frame, vfull, wfull)
    name, host = sorted(terms)[0], sorted(hosts)[0]
    def inj(label, mut):
        v, w, p, t = copy.deepcopy(verdicts), copy.deepcopy(wfull), copy.deepcopy(prior), dict(texts)
        mut(v, w, p, t)
        caught = bool(check(v, wpub, data, p, frame, readme, vfull, w, t)); print(f'injected {label}:', 'caught' if caught else 'MISSED'); return caught
    def quote(v, w, p, t): w[0]['quote'] += ' xyzzy'
    def target(v, w, p, t): next(x for x in v if x['target_record'])['target_record'] = 'ORG-999999'
    def drop(v, w, p, t): v.pop()
    def flip(v, w, p, t): next(x for x in v if x['verdict'] == 'STILL_UNCERTAIN')['verdict'] = 'REJECT'
    def sha(v, w, p, t): w[1]['sha256'] = '0' * 64
    def guess(v, w, p, t): next(x for x in v if x['witness_ids'])['url_provenance'] = 'none'
    def leak_name(v, w, p, t): t['README.md'] += f'\n{name}\n'
    def leak_url(v, w, p, t): t['verdicts.csv'] += f'\nsee https://www.{host}/\n'
    ok = all([inj('altered quote', quote), inj('nonexistent target', target), inj('dropped verdict row', drop), inj('flipped verdict (count drift)', flip),
              inj('hash drift', sha), inj('witness on guessed URL', guess), inj('lead name in committed README', leak_name), inj('lead URL host in committed CSV', leak_url)])
    sys.exit(0 if ok and not errs else 1)

if __name__ == '__main__':
    main()
