#!/usr/bin/env python3
"""Check for the site-name repair PR. Against the merge base it asserts:
- the site_name cells this PR changes, the corrected site_name claims, the PACKET rows and the batch's evidence rows are the same
  set of site IDs, each ID once (a missing, extra or duplicated entry anywhere fails);
- on a renamed site, notes is the base notes plus exactly one appended sentence naming the old site_name (build.former_note); on any
  other site notes is unchanged; no other site column changes;
- each new site_name equals PACKET, and each evidence row's claim names it and its quote holds that name (without the locality
  suffix) and the held street;
- each site named in the README is in CLAIMS_CHECKED, and the README's row counts equal the file's;
- each capture replays at its offset in the store.
Anything it could not inspect is printed NOT_INSPECTED with its count and the exit status is 2, never 0 (--no-store skips the
capture replay and its plant, so it exits 2 at best). Exit 1 is a failure.
Plants, each rejected or the check fails: a change with no claim, a claim with no change, a wrong new name, a missing or duplicated
packet entry, a missing evidence row, a lost note, an omitted former name, a new name absent from the quote, a README count that is
wrong, a README site with no claims row, a shifted offset, and the exit-status rule itself.
Usage: check.py [--base REF] [--store DIR] [--no-store]"""
import copy, csv, glob, hashlib, io, re, subprocess, sys
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; D = Path(__file__).parent
sys.path.insert(0, str(ROOT / 'scripts')); sys.path.insert(0, str(D))
import check_evidence_binding as g  # noqa: E402
from build import LABEL, former_note  # noqa: E402

STORE = Path(sys.argv[sys.argv.index('--store') + 1] if '--store' in sys.argv else '/Volumes/johnpswan/work/GAC/polymer-atlas/atlas-store')


def rows(text): return list(csv.DictReader(io.StringIO(text, newline='')))


def git_show(ref, path): return subprocess.run(['git', 'show', f'{ref}:{path}'], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def exit_code(bad, not_inspected):
    """1 on any failure; else 2 when anything was not inspected; 0 only when everything was."""
    return 1 if bad else 2 if not_inspected else 0


def words(s): return ' '.join(g.squash(s).split())


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


def quote_problem(row, claim_detail):
    """The evidence row's claim and quote against PACKET and the held street (data only; no capture needed)."""
    q = claim_detail.partition('quote:')[2].strip()
    if not claim_detail.startswith(f"site_name '{row['new_site_name']}' as printed at the recorded address; quote:"): return 'evidence claim does not name the new site_name'
    if q != row['quote']: return 'evidence quote differs from PACKET'
    if g.web_street_reason(row['street'], q): return 'held street not in the quote'
    core = re.split(r'\s[—–-]\s', row['new_site_name'])[0]  # the name without its locality suffix
    if f' {words(core)} ' not in f' {words(q)} ': return 'new site_name not in the quote'
    return ''


def capture_problem(row, capture):
    if hashlib.sha256(capture).hexdigest() != row['capture_sha256']: return 'capture hash differs'
    q, a = row['quote'], int(row['quote_offset'])
    return '' if g.capture_text(capture)[a:a + len(q)] == q else 'quote not at offset in the capture main text'


def readme_problems(readme, claims):
    ids = {r['record_id'] for r in claims}; n = len(claims)
    c = sum(r['verdict'] == 'corrected' for r in claims); h = sum(r['verdict'] == 'held' for r in claims)
    bad = [f'README names {i} with no CLAIMS_CHECKED row' for i in sorted(set(re.findall(r'SITE-\d{6}', readme)) - ids)]
    if f'{n} rows: {c} corrected, {h} held' not in readme: bad.append(f'README does not state "{n} rows: {c} corrected, {h} held"')
    return bad


def verify(base_sites, cur_sites, claims, packet, evidence, readme):
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
    ev = {r['record_id']: r for r in evidence}; street = {r['site_id']: r['street_address'] for r in cur_sites}
    bad += [f"{r['record_id']}: claims evidence_id differs from the batch evidence row" for r in claims if r['verdict'] == 'corrected' and r['record_id'] in ev and ev[r['record_id']]['evidence_id'] != r['evidence_id']]
    bad += [f"{r['record_id']}: held row names an evidence id" for r in claims if r['verdict'] == 'held' and r['evidence_id']]
    for s, r in pk.items():
        if s in ev and s in street and (why := quote_problem(dict(r, street=street[s]), ev[s]['claim_detail'])): bad.append(f'{s}: {why}')
    return bad + readme_problems(readme, claims)


def main():
    base = (sys.argv[sys.argv.index('--base') + 1] if '--base' in sys.argv else subprocess.run(['git', 'merge-base', 'HEAD', 'origin/main'], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip())
    shards = sorted((ROOT / 'data').glob('sites_*.csv'))
    base_sites = [r for p in shards for r in rows(git_show(base, f'data/{p.name}'))]
    cur_sites = [r for p in shards for r in rows(p.read_text(encoding='utf-8'))]
    claims = rows((D / 'CLAIMS_CHECKED.csv').read_text()); packet = rows((D / 'PACKET.csv').read_text()); readme = (D / 'README.md').read_text()
    evidence = [r for p in sorted(glob.glob(str(ROOT / 'data/evidence_*.csv'))) for r in rows(Path(p).read_text(encoding='utf-8')) if r['created_by'] == LABEL]
    bad = verify(base_sites, cur_sites, claims, packet, evidence, readme)
    bad += [f"{r['evidence_id']}: batch evidence row is not a sites row" for r in evidence if r['record_table'] != 'sites']
    sites = {r['site_id']: r for r in cur_sites}; ev = {r['record_id']: r for r in evidence}
    store = lambda r: STORE / 'provenance' / LABEL / 'captures' / f"{r['capture_sha256']}.html"  # noqa: E731
    replayed, not_inspected = 0, []
    for pk in packet:
        if pk['site_id'] not in ev: continue  # already reported by verify
        if not store(pk).exists():
            if '--no-store' in sys.argv: not_inspected.append(f"capture replay of {pk['site_id']}"); continue
            bad.append(f"{pk['site_id']}: capture not in the store at {store(pk)} (use --no-store to skip the replay and exit 2)"); continue
        replayed += 1
        if why := capture_problem(pk, store(pk).read_bytes()): bad.append(f"{pk['site_id']}: {why}")
    # plants: each must be rejected, or the check proves nothing
    changed = changes(base_sites, cur_sites)[0]; one = sorted(changed)[0]; old = changed[one][0]
    base_notes = next(b['notes'] for b in base_sites if b['site_id'] == one)
    def mutate(**kw):
        a = dict(base_sites=base_sites, cur_sites=copy.deepcopy(cur_sites), claims=copy.deepcopy(claims), packet=copy.deepcopy(packet), evidence=copy.deepcopy(evidence), readme=readme); a.update(kw); return a
    drop = lambda lst, i, key: [r for r in lst if r[key] != i]  # noqa: E731
    on_one = lambda lst, key, **f: [dict(r, **f) if r[key] == one else r for r in lst]  # noqa: E731
    new1 = next(r['new_site_name'] for r in packet if r['site_id'] == one)
    plants = {'unclaimed change': mutate(claims=drop(claims, one, 'record_id')),
              'claim without change': mutate(cur_sites=on_one(cur_sites, 'site_id', site_name=old, notes=base_notes)),
              'wrong new name': mutate(packet=on_one(packet, 'site_id', new_site_name='Wrong Name')),
              'missing packet entry': mutate(packet=drop(packet, one, 'site_id')),
              'duplicated packet entry': mutate(packet=packet + [r for r in packet if r['site_id'] == one]),
              'missing evidence row': mutate(evidence=drop(evidence, one, 'record_id')),
              'lost note': mutate(cur_sites=[dict(r, notes=r['notes'][20:]) if r['site_id'] == one else r for r in cur_sites]),
              'omitted former name': mutate(cur_sites=[dict(r, notes=r['notes'].replace(former_note(old), '').rstrip()) if r['site_id'] == one else r for r in cur_sites]),
              'new name absent from the quote': mutate(cur_sites=on_one(cur_sites, 'site_id', site_name='Foo Corp'), packet=on_one(packet, 'site_id', new_site_name='Foo Corp'),
                                                       evidence=[dict(r, claim_detail=r['claim_detail'].replace(f"'{new1}'", "'Foo Corp'", 1)) if r['record_id'] == one else r for r in evidence]),
              'README count wrong': mutate(readme=re.sub(r'\d+ rows: \d+ corrected, \d+ held', '1 rows: 1 corrected, 0 held', readme)),
              'README site with no claims row': mutate(readme=readme + ' SITE-999999')}
    caught = {k: verify(**a) for k, a in plants.items()}
    f1 = store(next(r for r in packet if r['site_id'] == one))
    if f1.exists():
        pk1 = next(r for r in packet if r['site_id'] == one)
        caught['shifted offset'] = [capture_problem(dict(pk1, quote_offset=str(int(pk1['quote_offset']) + 1)), f1.read_bytes())]
    else: not_inspected.append('shifted-offset plant')
    rule_ok = exit_code([], ['x']) == 2 and exit_code(['f'], ['x']) == 1 and exit_code([], []) == 0  # the exit-status rule itself
    bad += [f'planted defect not caught: {k}' for k, v in caught.items() if not any(v)]
    if not rule_ok: bad.append('exit-status rule broken: a NOT_INSPECTED run could exit 0')
    print(f'{len(changed)} site_name cells changed, {sum(r["verdict"] == "corrected" for r in claims)} corrected rows, {replayed} captures replayed, {len(caught)} plants caught')
    if not_inspected: print(f'NOT_INSPECTED: {len(not_inspected)}: ' + '; '.join(not_inspected))
    for b in bad: print('FAIL', b)
    sys.exit(exit_code(bad, not_inspected))


if __name__ == '__main__': main()
