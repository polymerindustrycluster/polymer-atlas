#!/usr/bin/env python3
"""Check for the site-name repair PR. Against the merge base it asserts:
- the site_name cells this PR changes, the corrected site_name claims, the PACKET rows and the batch's evidence rows are the same
  set of site IDs, each ID once (a missing, extra or duplicated entry anywhere fails);
- on a renamed site, notes is the base notes plus exactly one appended sentence naming the old site_name (build.former_note); on any
  other site notes is unchanged; no other site column changes;
- each new site_name equals PACKET, each evidence row carries the PACKET quote and the held street, and (store mounted) each capture
  replays at its offset.
Plants, each rejected or the check fails: a change with no claim, a claim with no change, a wrong new name, a missing packet entry, a
duplicated packet entry, a lost note, an omitted former name, a shifted offset.
Usage: check.py [--base REF] [--no-store]"""
import copy, csv, glob, hashlib, io, subprocess, sys
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; D = Path(__file__).parent
sys.path.insert(0, str(ROOT / 'scripts')); sys.path.insert(0, str(D))
import check_evidence_binding as g  # noqa: E402
from build import LABEL, former_note  # noqa: E402

STORE = Path('/Volumes/johnpswan/work/GAC/polymer-atlas/atlas-store')


def rows(text): return list(csv.DictReader(io.StringIO(text, newline='')))


def git_show(ref, path): return subprocess.run(['git', 'show', f'{ref}:{path}'], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def changes(base_rows, cur_rows):
    """site_id -> (old, new) for changed site_name cells, and problems for any other change (notes: only the expected append)."""
    base = {r['site_id']: r for r in base_rows}; out, bad = {}, []
    if len(base) != len(base_rows) or len({r['site_id'] for r in cur_rows}) != len(cur_rows): bad.append('duplicate site ids')
    if set(base) != {r['site_id'] for r in cur_rows}: bad.append('site rows added or removed')
    for r in cur_rows:
        b = base.get(r['site_id'])
        if not b: continue
        for k in r:
            if k not in ('site_name', 'notes') and r[k] != b[k]: bad.append(f"{r['site_id']}: column {k} changed")
        if r['site_name'] != b['site_name']: out[r['site_id']] = (b['site_name'], r['site_name'])
        want = (b['notes'] + ' ' if b['notes'] else '') + former_note(b['site_name']) if r['site_name'] != b['site_name'] else b['notes']
        if r['notes'] != want: bad.append(f"{r['site_id']}: notes are not the base notes" + (" plus the one old-name sentence" if r['site_name'] != b['site_name'] else " (unchanged on a site that is not renamed)"))
    return out, bad


def verify(base_sites, cur_sites, claims, packet, evidence):
    """Every problem found, from the data alone (no store, no network)."""
    changed, bad = changes(base_sites, cur_sites)
    corrected = [r['record_id'] for r in claims if r['verdict'] == 'corrected' and r['table'] == 'sites' and r['field'] == 'site_name']
    pk = {r['site_id']: r for r in packet}
    for name, ids in (('corrected claims', corrected), ('PACKET', [r['site_id'] for r in packet]), ('batch evidence', [r['record_id'] for r in evidence])):
        bad += [f'{name}: {i} listed {n} times' for i, n in Counter(ids).items() if n > 1]
        bad += [f'{name}: {i} has no changed site_name' for i in sorted(set(ids) - set(changed))]
        bad += [f'{name}: {i} (changed site_name) is missing' for i in sorted(set(changed) - set(ids))]
    bad += [f'{s}: new site_name differs from PACKET' for s, (_, new) in changed.items() if s in pk and pk[s]['new_site_name'] != new]
    bad += [f'{s}: old site_name differs from PACKET' for s, (old, _) in changed.items() if s in pk and pk[s]['old_site_name'] != old]
    ev = {r['record_id']: r for r in evidence}
    bad += [f"{r['record_id']}: claims evidence_id differs from the batch evidence row" for r in claims if r['verdict'] == 'corrected' and r['record_id'] in ev and ev[r['record_id']]['evidence_id'] != r['evidence_id']]
    bad += [f"{r['record_id']}: held row names an evidence id" for r in claims if r['verdict'] == 'held' and r['evidence_id']]
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
    shards = sorted((ROOT / 'data').glob('sites_*.csv'))
    base_sites = [r for p in shards for r in rows(git_show(base, f'data/{p.name}'))]
    cur_sites = [r for p in shards for r in rows(p.read_text(encoding='utf-8'))]
    claims = rows((D / 'CLAIMS_CHECKED.csv').read_text()); packet = rows((D / 'PACKET.csv').read_text())
    evidence = [r for p in sorted(glob.glob(str(ROOT / 'data/evidence_*.csv'))) for r in rows(Path(p).read_text(encoding='utf-8')) if r['created_by'] == LABEL]
    bad = verify(base_sites, cur_sites, claims, packet, evidence)
    bad += [f"{r['evidence_id']}: batch evidence row is not a sites row" for r in evidence if r['record_table'] != 'sites']
    sites = {r['site_id']: r for r in cur_sites}; ev = {r['record_id']: r for r in evidence}
    replayed = skipped = 0
    for pk in packet:
        sid = pk['site_id']
        if sid not in ev: continue  # already reported by verify
        pk = dict(pk, street=sites[sid]['street_address'])
        f = STORE / 'provenance' / LABEL / 'captures' / f"{pk['capture_sha256']}.html"
        if not f.exists():
            if '--no-store' in sys.argv: skipped += 1; continue
            bad.append(f'{sid}: capture not in the store at {f} (use --no-store to skip replay)'); continue
        why = replay(pk, ev[sid]['claim_detail'], f.read_bytes()); replayed += 1
        if why: bad.append(f'{sid}: {why}')
    # plants: each must be rejected, or the check proves nothing
    changed = changes(base_sites, cur_sites)[0]; one = sorted(changed)[0]
    def mutate(**kw):
        a = dict(base_sites=base_sites, cur_sites=copy.deepcopy(cur_sites), claims=copy.deepcopy(claims), packet=copy.deepcopy(packet), evidence=copy.deepcopy(evidence)); a.update(kw); return a
    drop = lambda lst, i, key: [r for r in lst if r[key] != i]  # noqa: E731
    site = lambda s, f: [dict(r, **f(r)) if r['site_id'] == one else r for r in s]  # noqa: E731
    plants = {'unclaimed change': mutate(claims=drop(claims, one, 'record_id')),
              'claim without change': mutate(cur_sites=[dict(r, site_name=changed[one][0], notes=base_sites[[b['site_id'] for b in base_sites].index(one)]['notes']) if r['site_id'] == one else r for r in cur_sites]),
              'wrong new name': mutate(packet=[dict(r, new_site_name='Wrong Name') if r['site_id'] == one else r for r in packet]),
              'missing packet entry': mutate(packet=drop(packet, one, 'site_id')),
              'duplicated packet entry': mutate(packet=packet + [r for r in packet if r['site_id'] == one]),
              'missing evidence row': mutate(evidence=drop(evidence, one, 'record_id')),
              'lost note': mutate(cur_sites=site(cur_sites, lambda r: dict(notes=r['notes'][20:]))),
              'omitted former name': mutate(cur_sites=site(cur_sites, lambda r: dict(notes=r['notes'].replace(former_note(changed[one][0]), '').rstrip())))}
    caught = {k: verify(**a) for k, a in plants.items()}
    f1 = STORE / 'provenance' / LABEL / 'captures' / f"{next(r for r in packet if r['site_id'] == one)['capture_sha256']}.html"
    if f1.exists():
        pk1 = dict(next(r for r in packet if r['site_id'] == one), street=sites[one]['street_address'])
        caught['shifted offset'] = [replay(dict(pk1, quote_offset=str(int(pk1['quote_offset']) + 1)), ev[one]['claim_detail'], f1.read_bytes())]
    bad += [f'planted defect not caught: {k}' for k, v in caught.items() if not any(v)]
    print(f'{len(changed)} site_name cells changed, {len(set(r["record_id"] for r in claims if r["verdict"] == "corrected"))} corrected rows, {replayed} captures replayed, {skipped} skipped, {len(caught)} plants caught')
    for b in bad: print('FAIL', b)
    sys.exit(1 if bad else 0)


if __name__ == '__main__': main()
