#!/usr/bin/env python3
"""Check for the site-name repair PR. Asserts, against the merge base: the site_name cells this PR changes are exactly the CLAIMS_CHECKED
rows marked corrected; each equals PACKET's new name; no other site cell changes except `notes` (old name kept); each corrected row has
one own-site evidence row with the quote, the held street in the quote, and (store mounted) the capture replayed at its offset.
Plants: a changed cell with no claims row, a claims row with no change, a wrong new name and a shifted offset must each be rejected.
Usage: check.py [--base REF] [--no-store]"""
import csv, hashlib, io, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; D = Path(__file__).parent
sys.path.insert(0, str(ROOT / 'scripts'))
import check_evidence_binding as g  # noqa: E402

STORE = Path('/Volumes/johnpswan/work/GAC/polymer-atlas/atlas-store')


def rows(text): return list(csv.DictReader(io.StringIO(text, newline='')))


def git_show(ref, path): return subprocess.run(['git', 'show', f'{ref}:{path}'], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def changes(base_rows, cur_rows):
    """site_id -> (old name, new name) for changed site_name cells, plus problems for any other changed cell except notes."""
    base = {r['site_id']: r for r in base_rows}; out, bad = {}, []
    if set(base) != {r['site_id'] for r in cur_rows}: bad.append('site rows added or removed')
    for r in cur_rows:
        b = base.get(r['site_id'])
        for k in r:
            if b and r[k] != b[k]:
                if k == 'site_name': out[r['site_id']] = (b[k], r[k])
                elif k != 'notes': bad.append(f"{r['site_id']}: column {k} changed")
    return out, bad


def compare(changed, corrected, packet):
    bad = [f'{s}: site_name changed with no corrected claims row' for s in changed if s not in corrected]
    bad += [f'{s}: corrected claims row but site_name is unchanged' for s in corrected if s not in changed]
    bad += [f'{s}: new site_name differs from PACKET' for s, (_, new) in changed.items() if s in packet and packet[s]['new_site_name'] != new]
    return bad


def replay(row, ev_detail, capture):
    q = ev_detail.partition('quote:')[2].strip()
    if q != row['quote']: return 'evidence quote differs from PACKET'
    if g.web_street_reason(row['street'], q): return 'held street not in the quote'
    if hashlib.sha256(capture).hexdigest() != row['capture_sha256']: return 'capture hash differs'
    a = int(row['quote_offset'])
    return '' if g.capture_text(capture)[a:a + len(q)] == q else 'quote not at offset in the capture main text'


def main():
    base = (sys.argv[sys.argv.index('--base') + 1] if '--base' in sys.argv else subprocess.run(['git', 'merge-base', 'HEAD', 'origin/main'], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip())
    changed, bad = {}, []
    for p in sorted((ROOT / 'data').glob('sites_*.csv')):
        c, b = changes(rows(git_show(base, f'data/{p.name}')), rows(p.read_text(encoding='utf-8'))); changed.update(c); bad += b
    claims = rows((D / 'CLAIMS_CHECKED.csv').read_text())
    corrected = {r['record_id'] for r in claims if r['verdict'] == 'corrected'}
    packet = {r['site_id']: r for r in rows((D / 'PACKET.csv').read_text())}
    bad += compare(changed, corrected, packet)
    bad += [f"{r['record_id']}: held row names an evidence id" for r in claims if r['verdict'] == 'held' and r['evidence_id']]
    sites = {r['site_id']: r for p in (ROOT / 'data').glob('sites_*.csv') for r in rows(p.read_text(encoding='utf-8'))}
    ev = {r['record_id']: r for r in rows((ROOT / 'data/evidence_sites_OH.csv').read_text(encoding='utf-8')) if r['created_by'] == D.name}
    replayed = skipped = 0
    for sid, pk in packet.items():
        if sid not in ev: bad.append(f'{sid}: no evidence row'); continue
        pk = dict(pk, street=sites[sid]['street_address'])
        f = STORE / 'provenance' / D.name / 'captures' / f"{pk['capture_sha256']}.html"
        if not f.exists():
            if '--no-store' in sys.argv: skipped += 1; continue
            bad.append(f'{sid}: capture not in the store at {f} (use --no-store to skip replay)'); continue
        why = replay(pk, ev[sid]['claim_detail'], f.read_bytes()); replayed += 1
        if why: bad.append(f'{sid}: {why}')
    # plants: each must be rejected, or the check proves nothing
    one = next(iter(changed)); pk1 = packet[one]
    plants = {'unclaimed change': compare(dict(changed, **{'SITE-999999': ('a', 'b')}), corrected, packet),
              'claim without change': compare({k: v for k, v in changed.items() if k != one}, corrected, packet),
              'wrong new name': compare(dict(changed, **{one: (changed[one][0], 'Wrong Name')}), corrected, packet)}
    f1 = STORE / 'provenance' / D.name / 'captures' / f"{pk1['capture_sha256']}.html"
    if f1.exists():
        plants['shifted offset'] = [replay(dict(pk1, street=sites[one]['street_address'], quote_offset=str(int(pk1['quote_offset']) + 1)), ev[one]['claim_detail'], f1.read_bytes())]
    missed = [k for k, v in plants.items() if not any(v)]
    bad += [f'planted defect not caught: {k}' for k in missed]
    print(f'{len(changed)} site_name cells changed, {len(corrected)} corrected rows, {replayed} captures replayed, {skipped} skipped, {len(plants)} plants caught')
    for b in bad: print('FAIL', b)
    sys.exit(1 if bad else 0)


if __name__ == '__main__': main()
