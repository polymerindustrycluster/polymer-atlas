"""Named gate for lane CAP2A: independent counts, exact replay of every added cell/row, column boundary, witnesses, 6 injected defects, idempotence."""
import copy, hashlib, json, re
import build as b

# Guard (added after the Gemini review of 20ff680): an applied site whose organization's stored pages show another-state address or a
# non-US operation must be reviewed here, with the page that binds the applied terms to this establishment.
OTHER = re.compile(r'\b(?:AL|AZ|AR|CA|CO|CT|DE|FL|GA|IL|IN|IA|KS|KY|LA|MD|MA|MI|MN|MS|MO|NC|NE|NV|NH|NJ|NM|NY|OK|OR|PA|SC|TN|TX|UT|VA|WA|WV|WI|DC)\s*,?\s+\d{5}\b|\b(?:Mexico|China|Canada|India|Germany|Poland|Europe|Georgia|Texas|Tennessee|Carolina|Michigan|Indiana|Pennsylvania|Kentucky|Florida|California|Illinois|Wisconsin|Netherlands|Brazil)\b')
MULTI_OK = {
    'SITE-000458': 'malishplastics.com /news: "Malish Plastics has announced its plans to move the company\'s headquarters and manufacturing operations" to the 160,000 sq ft Mentor facility; the Mexico, Poland, NY and China entries are the Malish Corporation directory (residual risk noted in README)',
    'SITE-000591': 'royalplastics.com /about lists "RPI – Mentor, OH USA Custom Injection Molder and Contract Manufacturer" apart from RPI-China; the witness is that line',
    'SITE-000909': 'flextechnologies.com /about-us: "Midvale, Ohio Corporate Headquarters & Extrusion"; only the extrusion terms remain, compounding (Baltic) and molding (Mt. Eaton, Lafayette TN) were withdrawn',
}
def multi_location_unreviewed(decisions, multi_ok):
    orgs = {s['site_id']: s['org_id'] for s in b.read(b.T / 'slice.csv')}
    pages = [r for r in b.read(b.CORPUS / 'manifest.csv') if r['text_file']]
    bad = []
    for sid in sorted({d['site_id'] for d in decisions}):
        hit = any(OTHER.search(' '.join((b.CORPUS / p['text_file']).read_text(errors='replace').split())) for p in pages if p['org_id'] == orgs[sid])
        if hit and sid not in multi_ok: bad.append(sid)
    return bad

def check(decisions, multi_ok=MULTI_OK):
    sites, caps, ev, verdicts = b.outputs(decisions)
    assert not multi_location_unreviewed(decisions, multi_ok), ('multi-location organization not reviewed', multi_location_unreviewed(decisions, multi_ok))
    retired = set((b.T / 'retired_ids.txt').read_text().split())
    assert not retired & ({r['capability_id'] for r in caps} | {r['evidence_id'] for r in ev}), 'a retired id is in use'
    # independent input counts: PR #351 left 220 sites unadjudicated; this lane's slice is the first 110 by site_id
    pr351 = sorted((b.T / 'pr351_unadjudicated_sites.txt').read_text().split())
    assert len(pr351) == 220 and b.slice_ids() == pr351[:110], 'slice is not the first half of the 220 unadjudicated sites'
    assert not set(b.slice_ids()) - {s['site_id'] for s in b.frame_now()}, 'slice site left the frame (filled elsewhere): re-baseline'
    assert {v['site_id'] for v in verdicts} == set(b.slice_ids()), 'a slice site has no verdict row'
    orig = {s['site_id']: s for s in b.base('data/sites_OH.csv')}
    cur = {s['site_id']: s for s in b.read(b.ROOT / 'data/sites_OH.csv')}
    assert cur.keys() == orig.keys()
    for sid, s in cur.items():
        if sid in sites:  # only processes/materials may differ, and only by appended terms
            assert {k: v for k, v in s.items() if k not in ('processes', 'materials')} == {k: v for k, v in orig[sid].items() if k not in ('processes', 'materials')}, ('column boundary', sid)
            for col in ('processes', 'materials'):
                o = [v for v in orig[sid][col].split(';') if v]; n = [v for v in s[col].split(';') if v]
                assert n[:len(o)] == o and n == [v for v in sites[sid][col].split(';') if v], ('cell', sid, col)
        else: assert s == orig[sid], ('untouched site changed', sid)
    for filename, rows, key, lo, hi in [('site_capabilities.csv', caps, 'capability_id', 1200, 1499), ('evidence_sites_OH.csv', ev, 'evidence_id', 387000, 387999)]:
        old = {r[key]: r for r in b.base('data/' + filename)}; now = {r[key]: r for r in b.read(b.ROOT / 'data' / filename)}
        assert all(now[k] == v for k, v in old.items()), 'existing row changed or lost'
        assert {k: v for k, v in now.items() if k not in old} == {r[key]: r for r in rows}, 'appended rows differ from expected'
        assert all(lo <= int(r[key].split('-')[1]) <= hi for r in rows), 'id outside block'
    tier = {s['site_id']: s['verification_tier'] for s in sites.values()}
    assert all(not (e['tier_effect'] == 'supports_C' and tier[e['record_id']] in ('A', 'B')) for e in ev), 'C-strength evidence on a tier A/B site (V-25)'
    assert all(r['provenance'] == 'company_disclosed' for r in caps)
    assert b.read(b.T / 'verdicts.csv') == verdicts, 'verdicts.csv differs'
    sm = b.summary(decisions, sites, caps, ev, verdicts)
    assert json.loads((b.T / 'summary.json').read_text()) == sm, 'summary differs'
    return sm

if __name__ == '__main__':
    decisions = b.read(b.T / 'decisions.csv'); print(check(decisions))
    tiers = {s['site_id']: s['verification_tier'] for s in b.base('data/sites_OH.csv')}
    tierab_menu = next(i for i, d in enumerate(decisions) if d['basis'] == 'menu' and tiers[d['site_id']] in ('A', 'B'))
    muts = [('false quote', lambda ds: ds[0].update(quote='INJECTED UNSUPPORTED QUOTE')), ('invalid term', lambda ds: ds[0].update(term='injected_invalid_term')),
            ('false locality witness', lambda ds: ds[0].update(grain_quote='INJECTED WRONG PLANT, TX 77001')),
            ('tier A/B menu term promoted to a tag', lambda ds: ds[tierab_menu].update(basis='narrative')), ('dropped decision (site loses its verdict)', lambda ds: ds.pop(0) and None)]
    muts = [m + ({},) for m in muts] + [('multi-location site not reviewed', lambda ds: None, {'multi_ok': {}})]
    for name, f, kw in muts:
        bad = copy.deepcopy(decisions); f(bad)
        try: check(bad, **kw)
        except (AssertionError, KeyError, ValueError, StopIteration): print('detected injected defect:', name)
        else: raise AssertionError('mutation survived: ' + name)
    paths = [b.ROOT / 'data' / n for n in ('sites_OH.csv', 'site_capabilities.csv', 'evidence_sites_OH.csv')] + [b.T / 'verdicts.csv', b.T / 'summary.json']
    before = [hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]; b.main()
    assert before == [hashlib.sha256(p.read_bytes()).hexdigest() for p in paths], 'non-idempotent'
    print('PASS: CAP2A replay / counts / 6 injected defects / idempotence')
