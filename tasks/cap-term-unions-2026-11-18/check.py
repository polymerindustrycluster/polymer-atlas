"""check.py: recomputes the union delta against the pinned base and fails on injected defects. Run from anywhere: python3 tasks/cap-term-unions-2026-11-18/check.py"""
import copy, csv, hashlib, importlib.util, io, itertools, json, subprocess, sys, tempfile
from pathlib import Path
from unittest.mock import patch
T = Path(__file__).resolve().parent
ROOT = T.parents[1]
spec = importlib.util.spec_from_file_location('build', T / 'build.py'); build = importlib.util.module_from_spec(spec); spec.loader.exec_module(build)
BASE = (T / 'base.txt').read_text().strip()
VOCAB = json.loads((ROOT / 'docs/schema/vocab.json').read_text())['vocabularies']
BLOCK = range(396500, 396550)
REQUOTED = {'SITE-001986'}  # CAP2B held this term without a quote
# held by controller decisions (2026-11-18) and never written: 001109 no single sentence says CNC-machines-plastic; 000707 is a tool shop (molds for these processes);
# 000562 compression_molding is the plastics term, the rubber molder gets rubber_molding_compression (SCHEMA 3.1/3.6)
HOLD = {('SITE-001109', 'plastics_machining_cnc'), ('SITE-000707', 'compression_molding'), ('SITE-000707', 'thermoforming_unspecified'), ('SITE-000562', 'compression_molding')}
REMAP = {('SITE-000562', 'rubber_molding_compression'): 'compression_molding'}
def rd(text): return list(csv.DictReader(io.StringIO(text, newline='')))
def base_file(p): return rd(subprocess.check_output(['git', 'show', f'{BASE}:{p}'], cwd=ROOT, text=True))
def verify(base_sites, sites, base_ev, ev, decisions):
    """Raises AssertionError on any violation; returns the counts."""
    b = {s['site_id']: s for s in base_sites}; n = {s['site_id']: s for s in sites}
    assert [s['site_id'] for s in base_sites] == [s['site_id'] for s in sites], 'site rows added, dropped or reordered'
    listed = {d['site_id'] for d in decisions}
    changed = {k for k in n if n[k] != b[k]}
    assert changed == listed, f'changed sites differ from the listed sites: {sorted(changed ^ listed)}'
    for k in changed:
        assert [c for c in n[k] if n[k][c] != b[k][c]] and all(n[k][c] == b[k][c] for c in n[k] if c not in ('processes', 'materials')), f'{k}: column outside processes/materials changed'
    for k, t in HOLD: assert t not in n[k]['processes'].split(';') + n[k]['materials'].split(';'), f'{k}: held term {t} was written'
    assert len(sites) == len(base_sites), 'sites row count differs from the base'
    for k in changed:
        for field, vocab in (('processes', 'PROCESSES'), ('materials', 'MATERIALS')):
            old = [v for v in b[k][field].split(';') if v]; new = [v for v in n[k][field].split(';') if v]
            want = [d['term'] for d in decisions if d['site_id'] == k and d['field'] == field]
            assert new[:len(old)] == old, f'{k} {field}: an existing value was removed or reordered'
            assert sorted(new[len(old):]) == sorted(want), f'{k} {field}: appended terms {new[len(old):]} differ from decisions {want}'
            assert old or not want, f'{k} {field}: union rule applies to non-blank cells only'
            for t in new[len(old):]: assert t in VOCAB[vocab]['values'], f'{k} {field}: {t} is not a section 3.1/3.2 term'
    bids = {r['evidence_id']: r for r in base_ev}
    assert all(ev_r == bids[ev_r['evidence_id']] for ev_r in ev if ev_r['evidence_id'] in bids) and set(bids) <= {r['evidence_id'] for r in ev}, 'base evidence row changed or dropped'
    added = [r for r in ev if r['evidence_id'] not in bids]
    assert len(ev) == len(base_ev) + len(decisions), f'evidence rows {len(ev)} != base {len(base_ev)} + {len(decisions)}'
    assert all(int(r['evidence_id'][4:]) in BLOCK for r in added), 'evidence ID outside EVD-396500..396549'
    for d in decisions:
        build.cap2a.validate_decision(d)
        rows = [r for r in added if r['record_id'] == d['site_id'] and r['claim_detail'].startswith(f"{d['field']}={d['term']};")]
        assert len(rows) == 1, f"{d['site_id']} {d['term']}: {len(rows)} new evidence rows (need 1)"
        r = rows[0]; tier = n[d['site_id']]['verification_tier']
        assert d['quote'] in r['claim_detail'] and r['claim_type'] == 'scope' and r['record_table'] == 'sites' and r['source_class'] == 'own_site'
        assert r['tier_effect'] == ('supports_C' if d['basis'] == 'menu' else 'supports_A'), f"{d['site_id']} {d['term']}: tier_effect does not match basis"
        assert r['tier_effect'] == 'supports_A' or tier == 'C', 'V-25: C-strength evidence on a tier A/B site'
    assert len(added) == len(decisions), 'evidence rows without a decision'
    tiers = sorted(n[k]['verification_tier'] for k in changed); strengths = sorted(r['tier_effect'] for r in added)
    return dict(sites_changed=len(changed), terms_appended=len(decisions), evidence_rows_added=len(added), tiers=''.join(tiers), strengths=','.join(strengths))
def main():
    decisions = build.read(T / 'decisions.csv')
    # independent count of the input: CAP2A's own verdicts list the held-tag terms; CAP2B's holds list SITE-001986
    held = [(v['site_id'], v['term']) for v in build.read(ROOT / 'tasks/pic18-capabilities-corpus-2a-2026-11-16/verdicts.csv') if v['disposition'].startswith('tag held (cell not blank')]
    assert len(held) == 10 and len({s for s, _ in held}) == 7, held
    assert any(h['site_id'] == 'SITE-001986' and 'composites_unspecified' in h.values() for h in build.read(ROOT / 'tasks/pic18-capabilities-corpus-2b-2026-11-16/holds.csv')), 'CAP2B hold missing'
    got = {(d['site_id'], d['term']) for d in decisions}
    got = {(d['site_id'], d['term']) for d in decisions}
    assert {(k, REMAP.get((k, t), t)) for k, t in got} - {('SITE-001986', 'composites_unspecified')} == set(held) - (HOLD - {(k[0], v) for k, v in REMAP.items()}) and len(decisions) == 8, 'decisions differ from the CAP2A held terms (minus the holds, plus the remap) + the CAP2B term'
    c2a = {(d['site_id'], d['term']): d for d in build.read(ROOT / 'tasks/pic18-capabilities-corpus-2a-2026-11-16/decisions.csv') if d['field'] == 'processes'}
    for d in decisions:
        if d['site_id'] not in REQUOTED: assert all(c2a[(d['site_id'], REMAP.get((d['site_id'], d['term']), d['term']))][k] == d[k] for k in ('quote', 'sha256', 'url', 'basis', 'grain_quote')), 'decision differs from CAP2A row'
    base_sites, base_ev = base_file('data/sites_OH.csv'), base_file('data/evidence_sites_OH.csv')
    sites, ev = build.read(build.SITES), build.read(build.EVID)
    counts = verify(base_sites, sites, base_ev, ev, decisions); print('PASS', counts)
    assert counts == dict(sites_changed=6, terms_appended=8, evidence_rows_added=8, tiers='ABBCCC', strengths=','.join(['supports_A'] * 6 + ['supports_C'] * 2)), counts  # README: tiers A 1/B 2/C 3; strength A 6/C 2
    # idempotence: a rebuild leaves both data files byte-identical
    before = [hashlib.sha256(p.read_bytes()).hexdigest() for p in (build.SITES, build.EVID)]; build.main()
    assert before == [hashlib.sha256(p.read_bytes()).hexdigest() for p in (build.SITES, build.EVID)], 'rebuild changed data'
    # injected defects: each must fail verify()
    def inject(name, mut):
        s, e, d = copy.deepcopy(sites), copy.deepcopy(ev), copy.deepcopy(decisions); mut(s, e, d)
        try: verify(base_sites, s, base_ev, e, d)
        except AssertionError as x: print('  caught', name, '->', str(x)[:90]); return
        raise SystemExit(f'FAIL: injected defect not caught: {name}')
    site = lambda s, k: next(r for r in s if r['site_id'] == k)
    inject('existing value removed', lambda s, e, d: site(s, 'SITE-000458').update(processes='extrusion_profile;extrusion_pipe_tube'))
    def offvocab(s, e, d):
        site(s, 'SITE-000243').update(processes='tooling_mold_die;injection_moulding'); d[0]['term'] = 'injection_moulding'; e[-10]['claim_detail'] = e[-10]['claim_detail'].replace('injection_molding', 'injection_moulding')
    inject('term not in 3.1/3.2', offvocab)
    inject('term without evidence', lambda s, e, d: e.pop(next(i for i, r in enumerate(e) if r['created_by'] == build.WHO)))
    inject('write to a non-listed site', lambda s, e, d: site(s, 'SITE-000001').update(processes=site(s, 'SITE-000001')['processes'] + ';injection_molding'))
    inject('false quote', lambda s, e, d: d[0].update(quote='Since 1990 we have been molding diamonds'))
    inject('C-strength evidence on tier A', lambda s, e, d: next(r for r in e if r['record_id'] == 'SITE-001125' and r['created_by'] == build.WHO).update(tier_effect='supports_C'))
    inject('held term written (rubber molder gets the plastics compression_molding)', lambda s, e, d: site(s, 'SITE-000562').update(processes=site(s, 'SITE-000562')['processes'].replace('rubber_molding_compression', 'compression_molding')))
    inject('evidence row count off (an extra row)', lambda s, e, d: e.append(dict(e[-1], evidence_id='EVD-396549')))
    inject('sites row dropped', lambda s, e, d: s.pop())
    # cut-short write (the codex-24 reproduction for PR #382, applied here): a write dying after 100 rows must leave both targets intact with no temp file, and a retry must reproduce the committed bytes
    want = [build.SITES.read_bytes(), build.EVID.read_bytes()]
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp); fs, fe = d / 'sites_OH.csv', d / 'evidence_sites_OH.csv'
        for f, p in ((fs, 'data/sites_OH.csv'), (fe, 'data/evidence_sites_OH.csv')): f.write_bytes(subprocess.check_output(['git', 'show', f'{BASE}:{p}'], cwd=ROOT))
        real = build.write_atomic
        def cut(path, header, rows):
            def dying(): yield from itertools.islice(rows, 100); raise OSError('injected interrupted write')
            return real(path, header, dying())
        with patch.object(build, 'SITES', fs), patch.object(build, 'EVID', fe):
            before = [fs.read_bytes(), fe.read_bytes()]
            try:
                with patch.object(build, 'write_atomic', cut): build.main()
                raise SystemExit('FAIL: cut-short write did not raise')
            except OSError: pass
            assert [fs.read_bytes(), fe.read_bytes()] == before and not list(d.glob('*.tmp')), 'cut-short write damaged a target or left a temp file'
            build.main(); assert [fs.read_bytes(), fe.read_bytes()] == want, 'retry did not reproduce the committed data'
            fs.write_text(''.join(fs.read_text().splitlines(True)[:101]))  # a target already truncated by another writer: refuse
            try: build.main(); raise SystemExit('FAIL: builder accepted a truncated sites file')
            except AssertionError: pass
    print('  caught cut-short write (targets intact, no temp file, retry reproduces the committed bytes, truncated target refused)')
    print('check.py: PASS (9 injected defects caught, plus the cut-short-write reproduction)')
if __name__ == '__main__': main()
