#!/usr/bin/env python3
"""Recompute every published count, compare yield with an independent count of the input, re-verify
every witness quote against its stored raw page, and prove the checks fail on injected defects."""
import copy, csv, glob, hashlib, json, re, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build import ROOT, read, counts, used_ids
S = Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist')
words = lambda t: re.findall(r'[a-z0-9]+', t.lower())
# Held-record facts each verdict relies on: (table, id, column, substring that must be present)
TARGET_FACTS = {'1': ('sites', 'SITE-000445', 'street_address', '215 Sinter'), '28': ('sites', 'SITE-000116', 'street_address', '1400 E. 222nd'),
                '39': ('sites', 'SITE-000357', 'street_address', 'FIGGIE'), '41': ('sites', 'SITE-000228', 'street_address', '951 Jaycox'),
                '43': ('organizations', 'ORG-001597', 'website', 'itps-inc.com'), '59': ('sites', 'SITE-001777', 'notes', '2926 Chester'),
                '18': ('sites', 'SITE-000928', 'notes', '509 Water'), '80': ('organizations', 'ORG-000140', 'legal_name', 'Cleveland Specialty Products')}

def load_data():
    return {t: {r[k]: r for p in glob.glob(str(ROOT / 'data' / f'{t}_*.csv')) for r in read(Path(p))}
            for t, k in (('organizations', 'org_id'), ('sites', 'site_id'))}

def check(verdicts, witnesses, data, prior, frame, readme):
    errs = []
    # yield: independent count of the input = frame ranks minus the first lane's DUPLICATE_OF ranks
    expect = {r['rank'] for r in frame} - {r['rank'] for r in prior if r['verdict'] == 'DUPLICATE_OF'}
    got = [v['rank'] for v in verdicts]
    if len(got) != len(set(got)) or set(got) != expect or len(expect) != 72: errs.append(f'yield: {len(got)} verdict rows vs {len(expect)} held leads')
    c = counts(verdicts)
    if f"{c['leads_adjudicated']} held leads adjudicated" not in readme or any(f'{k} {n}' not in readme.replace(':', '') for k, n in c['by_verdict'].items()):
        errs.append(f'README counts do not match recomputed {c}')
    if c['applied'] or c['data_rows_added']: errs.append('this pass must apply zero rows')
    wmap = {w['witness_id']: w for w in witnesses}
    for v in verdicts:
        for wid in filter(None, v['witness_ids'].split(';')):
            w = wmap.get(wid)
            if not w: errs.append(f'rank {v["rank"]}: unknown witness {wid}'); continue
            html = S / w['raw_file']
            if not html.exists() or hashlib.sha256(html.read_bytes()).hexdigest() != w['sha256']: errs.append(f'{wid}: raw page missing or hash drift'); continue
            tw, qw = words(html.with_suffix('.txt').read_text()), words(w['quote'])
            if not any(tw[i:i + len(qw)] == qw for i in range(len(tw))): errs.append(f'{wid}: quote not on stored page')
        if not v['url_provenance']: errs.append(f'rank {v["rank"]}: no url_provenance')
        if v['witness_ids'] and v['url_provenance'].startswith('none'): errs.append(f'rank {v["rank"]}: witness on a URL with no provenance')
        if v['verdict'] == 'REJECT' and not v['witness_ids']: errs.append(f'rank {v["rank"]}: REJECT without a quoted deciding fact')
        for tid in filter(None, v['target_record'].split(';')):
            if tid not in data['organizations'] and tid not in data['sites']: errs.append(f'rank {v["rank"]}: target {tid} not in data/')
        if v['verdict'] == 'DUPLICATE_OF' and not v['target_record']: errs.append(f'rank {v["rank"]}: DUPLICATE_OF without a target')
    for rank, (tbl, rid, col, sub) in TARGET_FACTS.items():
        row = data[tbl].get(rid)
        if not row or sub not in row[col]: errs.append(f'rank {rank}: held {rid}.{col} no longer contains {sub!r}')
    if used_ids(): errs.append(f'IDs in reserved blocks already used: {used_ids()}')
    return errs

def main():
    verdicts, witnesses = read(HERE / 'verdicts.csv'), read(HERE / 'witnesses.csv')
    data, prior = load_data(), read(HERE / 'prior_pr356_verdicts.csv')
    frame, readme = read(S / 'pic18-discovery-leads' / 'frame.csv'), (HERE / 'README.md').read_text()
    assert len(frame) == 80 and len(prior) == 80
    errs = check(verdicts, witnesses, data, prior, frame, readme)
    print('real check:', 'FAIL ' + str(errs) if errs else 'ok', f'({len(verdicts)} verdicts, {len(witnesses)} witnesses)')
    base = subprocess.run(['git', 'merge-base', 'origin/main', 'HEAD'], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    diff = subprocess.run(['git', 'diff', '--name-only', base, '--', 'data'], cwd=ROOT, capture_output=True, text=True).stdout.split()
    if diff: errs.append(f'data/ files changed: {diff}')
    # injected defects: each must be caught
    def inj(name, mut):
        v, w, p = copy.deepcopy(verdicts), copy.deepcopy(witnesses), copy.deepcopy(prior)
        mut(v, w, p)
        caught = bool(check(v, w, data, p, frame, readme)); print(f'injected {name}:', 'caught' if caught else 'MISSED'); return caught
    def quote(v, w, p): w[0]['quote'] += ' xyzzy'
    def target(v, w, p): next(x for x in v if x['target_record'])['target_record'] = 'ORG-999999'
    def drop(v, w, p): v.pop()
    def flip(v, w, p): next(x for x in v if x['verdict'] == 'STILL_UNCERTAIN')['verdict'] = 'REJECT'
    def guess(v, w, p): next(x for x in v if x['witness_ids'])['url_provenance'] = 'none: guessed'
    def sha(v, w, p): w[1]['sha256'] = '0' * 64
    ok = all([inj('altered quote', quote), inj('nonexistent target', target), inj('dropped verdict row', drop), inj('flipped verdict (count drift)', flip), inj('hash drift', sha), inj('witness on guessed URL', guess)])
    sys.exit(0 if ok and not errs else 1)

if __name__ == '__main__':
    main()
