#!/usr/bin/env python3
"""Selftest on a synthetic fixture: no real frame, no network, no model call. Each planted case must fail for the right reason.

    python3 tasks/blind-audit-13-smoke-2026-11-24/check.py
"""
import csv, json, sys, tempfile
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reading as rd  # noqa: E402
import smoke  # noqa: E402

PASSED = []


def case(name):
    def deco(fn):
        fn()
        PASSED.append(name)
    return deco


def expect_raises(exc, fn, why):
    try:
        fn()
    except exc as e:
        assert why in str(e), f'raised for the wrong reason: {e}'
        return
    raise AssertionError(f'expected a refusal ({why}); none raised')


PAGE = 'Acme Plastics, Inc. is located at 12 Elm Street, Akron, Ohio. We mold thermoplastic parts.'
SRC = {'S1': PAGE}


def finding(target, verdict, quote='', source_value='', **kw):
    return dict(target=target, verdict=verdict, source_id='S1', quote=quote, source_value=source_value, settling_fact=kw.pop('settling_fact', ''), **kw)


def read(findings, targets, held=None):
    return rd.read_findings(dict(findings=findings), SRC, targets, held or {})


T = ['legal_name', 'street_address', 'processes', 'polymer_relevance']
OK = [finding(t, 'VERIFIED') for t in T]


def with_(**by_target):
    return [by_target.get(f['target'], f) for f in OK]


def outcome(findings, targets=T, held=None):
    return rd.record_outcome(rd.combine(read(findings, targets, held), None))


@case('a contradicted core field with a replayed quote reaches k')
def _():
    o = outcome(with_(street_address=finding('street_address', 'CONTRADICTED', 'located at 12 Elm Street, Akron', '12 Elm Street')))
    assert o['k'] and o['contradicted_core'] == ['street_address']


@case('a contradiction whose quote is not on the page does not reach k')
def _():
    o = outcome(with_(street_address=finding('street_address', 'CONTRADICTED', 'moved to 99 Oak Avenue', '99 Oak Avenue')))
    assert not o['k'] and o['unconfirmed']['street_address'] == 'quote_not_replayed'


@case('an unconfirmed core claim does not reach k and is tallied')
def _():
    o = outcome(with_(polymer_relevance=finding('polymer_relevance', 'UNCONFIRMED', settling_fact='the plant page naming its processes')))
    assert not o['k'] and o['unconfirmed'] == {'polymer_relevance': 'unsettled'}


@case('a contradicted descriptive field does not reach k and is tallied by field')
def _():
    o = outcome(with_(processes=finding('processes', 'CONTRADICTED', 'We mold thermoplastic parts', 'injection molding only')))
    assert not o['k'] and o['contradicted_desc'] == ['processes']


@case('a legal-form-only name difference is not a contradiction; a division or different entity is')
def _():
    held = {'legal_name': 'Acme Plastics LLC'}
    o = outcome(with_(legal_name=finding('legal_name', 'CONTRADICTED', 'Acme Plastics, Inc. is located', 'Acme Plastics, Inc.')), held=held)
    assert not o['k'] and o['notes'] == ['legal_name'], o
    for other in ('Acme Plastics Division of Zeta Holdings', 'Acme Plastic Systems', 'The Acme Group'):
        assert not rd.name_equivalent('Acme Plastics LLC', other), other
    assert rd.name_equivalent('The Acme Plastics Co.', 'ACME PLASTICS, INC')
    o = outcome(with_(legal_name=finding('legal_name', 'CONTRADICTED', 'Acme Plastics, Inc.', 'Acme Plastics Division of Zeta Holdings')), held=held)
    assert o['k'], 'a different entity name must be contradicted'


@case('a missing assessment is unconfirmed, never verified')
def _():
    o = outcome(OK[:-1])
    assert o['unconfirmed'] == {'polymer_relevance': 'missing_assessment'} and not o['k']


@case('a replayed contradiction from the second read stands; a vote cannot erase it; the builder-exception reader cannot clear an unconfirmed claim')
def _():
    prim = read(OK, T)
    sec = read(with_(street_address=finding('street_address', 'CONTRADICTED', 'located at 12 Elm Street', '12 Elm Street')), T)
    assert rd.record_outcome(rd.combine(prim, sec))['k'], 'check-only discovery must count'
    assert rd.record_outcome(rd.combine(sec, prim))['k'], 'a later AGREE must not erase the flag'
    unc = read(with_(processes=finding('processes', 'UNCONFIRMED', settling_fact='x')), T)
    assert rd.combine(unc, prim, True)['processes']['status'] == 'VERIFIED', 'an independent verified second read clears an unconfirmed claim'
    assert rd.combine(unc, prim, False)['processes']['status'] == 'UNCONFIRMED', 'the builder family cannot clear a flag'


@case('the stop fires at the 3rd record with a contradicted core field, counting records once')
def _():
    b = rd.Board(3)
    yes, no = dict(k=True), dict(k=False)
    for pos, o in enumerate([no, yes, no, yes], 1):
        assert b.add(pos, 'real', o)
    assert b.k == 2 and b.stopped_at is None
    assert not b.add(5, 'real', yes) and b.stopped_at == 5
    assert not b.add(6, 'real', yes) and len(b.real) == 5, 'items after the stop are not scored'


@case('a missed plant invalidates the stage; a detected one does not')
def _():
    b = rd.Board(3)
    assert b.add(1, 'plant', detected=True, provider='astra') and b.invalid is None
    assert not b.add(2, 'plant', detected=False, provider='hydrogen') and 'missed' in b.invalid
    primary = read(OK, T)
    assert not rd.plant_detected(primary, 'street_address'), 'a VERIFIED planted field is a miss'
    assert not rd.plant_detected(primary, 'not_in_packet')
    assert rd.plant_detected(read(with_(street_address=finding('street_address', 'UNCONFIRMED', settling_fact='the street on the own site')), T), 'street_address')
    assert not rd.plant_detected(read(OK[:1], T), 'street_address'), 'a missing assessment is a miss'


@case('a duplicate record ID is refused')
def _():
    expect_raises(AssertionError, lambda: smoke.assert_unique([('sites', 'SITE-1'), ('organizations', 'ORG-1'), ('sites', 'SITE-1')]), 'duplicate record ID refused')


class Gate:
    @staticmethod
    def family_of_text(t):
        return {'claude': 'anthropic', 'codex': 'openai', 'gemini': 'google'}.get(next((w for w in t.lower().replace('-', ' ').split() if w in ('claude', 'codex', 'gemini')), ''), '')
    @staticmethod
    def label_folder(l):
        return ''
    @staticmethod
    def builder_family(r):
        return ''


@case('an unknown builder family blocks; routing follows independence; an uncertain map entry resolves without a family guess')
def _():
    fams, unres = smoke.families_of({'claude-code lane-a', 'pass-13 integrator (spaghetti subagent)'}, Gate, lambda f: b'', [])
    assert fams == {'anthropic'} and unres == {'pass-13 integrator (spaghetti subagent)'}
    assert smoke.block_reason({'x'}, fams, unres) == 'unknown_builder_family'
    assert smoke.block_reason(set(), set(), set()) == 'unknown_builder_family', 'no label at all is unknown'
    fams, unres = smoke.families_of({'pass-13 integrator (spaghetti subagent)'}, Gate, lambda f: b'', [('pass-', 'uncertain')])
    assert not unres and fams == {'uncertain'} and smoke.route(fams) == 'astra'
    assert smoke.route({'openai'}) == 'hydrogen' and smoke.route({'openai', 'google'}) == '' and smoke.route({'anthropic'}) == 'astra'
    assert smoke.block_reason({'x'}, {'openai', 'google'}, set()) == 'no_eligible_primary_reader'


@case('a packet whose NAICS source name was removed fails the dependency gate')
def _():
    row = lambda v: dict(table='organizations', values_json=json.dumps(v))
    full = dict(naics_primary='326199', naics_primary_source_type='government_filing', naics_primary_source_name='OSHA ITA')
    rd.dependency_check(row(full), smoke.DEPENDS)
    expect_raises(ValueError, lambda: rd.dependency_check(row(dict(full, naics_primary_source_name='')), smoke.DEPENDS), 'naics_primary_source_name')
    expect_raises(ValueError, lambda: rd.dependency_check(row(dict(full, naics_primary_source_name=rd.WITHHELD)), smoke.DEPENDS), '(withheld)')
    rd.dependency_check(row(dict(full, naics_primary='', naics_primary_source_name='')), smoke.DEPENDS)  # a blank value is not a claim


@case('a call that resolves to another model, or returns no usage record, is refused')
def _():
    def agy(model, usage=True):
        res = dict(status='SUCCESS', response='{}', **({'usage': {'input_tokens': 10, 'output_tokens': 1}} if usage else {}))
        return 0, '\n'.join(json.dumps(e) for e in ({'event': 'init', 'init': {'model': model}}, {'event': 'result', 'result': res})), ''
    real = rd.run_process
    try:
        rd.run_process = lambda *a, **k: agy('Gemini 4 Neon (High)')
        assert 'refused' in rd.call_model('hydrogen', 'x', set())['error']
        rd.run_process = lambda *a, **k: agy('Gemini 4 Hydrogen (High)', usage=False)
        assert 'unmetered' in rd.call_model('hydrogen', 'x', set())['error']
        rd.run_process = lambda *a, **k: agy('Gemini 4 Hydrogen (High)')
        ok = rd.call_model('hydrogen', 'x', set())
        assert not ok['error'] and ok['metered'] and rd.input_tokens(ok['usage']) == 10
        council = lambda model, usage: (0, json.dumps(dict(providers=[dict(status='success', model=model, resolved_model=None, output='{}', usage=usage)])), '')
        rd.run_process = lambda *a, **k: council('gpt-6.2-sol/medium', dict(input_tokens=5))
        assert 'refused' in rd.call_model('astra', 'x', set())['error']
        rd.run_process = lambda *a, **k: council('gpt-6.2-astra/max', None)
        assert 'unmetered' in rd.call_model('astra', 'x', set())['error']
    finally:
        rd.run_process = real


@case('draw: keyed orderings, 3 plants per provider outside the real sample and independent of the builder, check coins near 15%')
def _():
    secret = b'selftest-secret-' * 4
    keys = [('sites', f'SITE-{i:05}') for i in range(400)]
    assert [smoke.keyed(secret, 'smoke', '|'.join(k)) for k in keys[:5]] != [smoke.keyed(secret, 'order', '|'.join(k)) for k in keys[:5]], 'purposes must be independent'
    fams = {k: ({'openai'} if i % 3 == 0 else {'google'} if i % 3 == 1 else {'anthropic'}) for i, k in enumerate(keys)}
    rows = [dict(site_id=k[1], org_id='ORG-1', site_name=f'Plant {i}', street_address=f'{i} Main St', city='Akron') for i, k in enumerate(keys)]
    R = SimpleNamespace(at='0' * 40, rows=lambda t: rows if t == 'sites' else [])
    real = set(sorted(keys, key=lambda k: smoke.keyed(secret, 'smoke', '|'.join(k)))[:40])
    plants = smoke.make_plants(R, secret, keys, real, fams)
    assert Counter(p['provider'] for p in plants) == dict.fromkeys(smoke.PROVIDERS, 3)
    for p in plants:
        k = (p['table'], p['record_id'])
        assert k not in real and smoke.FAMILY_OF_PROVIDER[p['provider']] not in fams[k], 'plant overlaps the sample or sits with its builder family'
    assert len({(p['table'], p['record_id']) for p in plants}) == 9
    coins = [smoke.keyed(secret, 'coin', f'sites|{i}')[:8] for i in range(3000)]
    share = sum(int.from_bytes(c, 'big') / 2**64 < smoke.CHECK_P for c in coins) / len(coins)
    assert abs(share - 0.15) < 0.03, share


@case('run: sealed-order scoring, the stop cancels the rest, blind second reads, uncertain always re-read, plants interleaved')
def _():
    work = Path(tempfile.mkdtemp(prefix='a13-check-'))
    draw_dir, cache, out = work / 'draw', work / 'cache', work / 'run'
    draw_dir.mkdir(), cache.mkdir()
    (cache / 'page.txt').write_text(PAGE)
    (cache / 'manifest.json').write_text(json.dumps({'https://acme.example/': dict(status='ok', final_url='https://acme.example/', fetched_at='t', text_file='page.txt')}))
    items = [('real', 'clean-1', 'astra'), ('plant', 'plant-a', 'astra'), ('real', 'bad-1', 'astra'), ('real', 'unc-1', 'hydrogen'), ('real', 'bad-2', 'astra'),
             ('plant', 'plant-h', 'hydrogen'), ('real', 'bad-3', 'astra'), ('real', 'late-1', 'astra'), ('real', 'late-2', 'astra')]
    sample, packets, fams = [], [], {}
    for pos, (kind, name, prov) in enumerate(items, 1):
        bid = f'A13-{pos:04}'
        row = dict(blind_id=bid, record_label=name, table='sites', columns_under_audit='site_name;street_address', values_json=json.dumps(dict(site_name='Acme Plastics', street_address='12 Elm Street')),
                   context_json=json.dumps(dict(children=[])), cited_sources='https://acme.example/', evidence_json='[]')
        packets.append(json.dumps(dict(row=row, masked=[], plant='street_address' if kind == 'plant' else '', urls=['https://acme.example/'])))
        sample.append(dict(pos=pos, blind_id=bid, kind=kind, table='sites', record_id=name, provider=prov, check_coin='0', plant_field='street_address' if kind == 'plant' else '', donor_record_id=''))
        fams[f'sites|{name}'] = ['uncertain'] if name == 'clean-1' else ['openai'] if name == 'unc-1' else []
    with open(draw_dir / 'sample.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, list(sample[0]))
        w.writeheader(), w.writerows(sample)
    (draw_dir / 'packets.jsonl').write_text('\n'.join(packets) + '\n')
    (draw_dir / 'families.json').write_text(json.dumps(fams))
    (draw_dir / 'receipts.json').write_text(json.dumps(dict(receipts={}, no_replayer={}, counts={})))
    prompts, called = {}, Counter()

    def fake(provider, prompt, procs, timeout=0):
        name = json.loads(prompt.split('=== RECORD ===')[1].split('=== SOURCES')[0])['record']
        prompts.setdefault(name, []).append((provider, prompt))
        called[name] += 1
        street = 'located at 12 Elm Street, Akron' if name.startswith('bad') or name.startswith('plant') else ''
        f = [finding('site_name', 'VERIFIED'), finding('street_address', 'CONTRADICTED', street, 'x') if street else finding('street_address', 'VERIFIED')]
        if name == 'unc-1':
            f[0] = finding('site_name', 'UNCONFIRMED', settling_fact='the plant page')
        f = [dict(x, source_id='S1') for x in f] + [dict(finding('polymer_relevance', 'VERIFIED'))]
        return dict(provider=provider, text=json.dumps(dict(findings=f)), model=rd.MODELS[provider], usage=dict(input_tokens=1000, cache_read_tokens=0), metered=True, error='', elapsed=0.0, prompt_bytes=len(prompt))
    real_call = rd.call_model
    rd.call_model = fake
    try:
        rc = rd.run_stage(draw_dir, cache, out, SimpleNamespace(stop_at=3, window=1, max_tokens_m=0))
    finally:
        rd.call_model = real_call
    doc = json.loads((out / 'results.json').read_text())
    assert doc['status'] == 'STOPPED_AT_K' and doc['k'] == 3 and doc['stopped_at'] == 7 and rc == 0, doc['status']
    assert called['late-1'] == called['late-2'] == 0, 'calls after the stop must be cancelled'
    assert [r['pos'] for r in doc['incomplete_calls']] == [8, 9], doc['incomplete_calls']
    plants = [r for r in doc['results'] if r['kind'] == 'plant']
    assert [p['detected'] for p in plants] == [True, True], plants
    clean = next(r for r in doc['results'] if r['record_id'] == 'clean-1')
    assert clean['second_provider'] == 'hydrogen' and clean['coin'] == '0', 'an uncertain record always gets a Hydrogen second read'
    p, s = prompts['bad-1']
    assert len(prompts['bad-1']) == 2 and p[1] == s[1], 'the second read must see the same prompt: no flag, no first verdict'
    assert 'CONTRADICTED' not in s[1].split('=== RECORD ===')[0].split('Reply with one JSON')[0]
    unc = next(r for r in doc['results'] if r['record_id'] == 'unc-1')
    assert unc['second_provider'] == 'sonnet' and unc['exception'] is False, 'Hydrogen primary on an OpenAI-built record: Sonnet is the independent second family'
    ledger = [json.loads(l) for l in open(out / 'ledger.jsonl')]
    assert any(l['role'] == 'lock' for l in ledger), 'first verdicts are locked before the second family reads'
    assert all(l.get('metered') for l in ledger if l['role'] in ('primary', 'second'))


@case('run: a missed plant suspends the stage')
def _():
    work = Path(tempfile.mkdtemp(prefix='a13-check-'))
    draw_dir, cache, out = work / 'draw', work / 'cache', work / 'run'
    draw_dir.mkdir(), cache.mkdir()
    (cache / 'manifest.json').write_text('{}')
    row = dict(blind_id='A13-0001', record_label='plant-x', table='sites', columns_under_audit='street_address', values_json=json.dumps(dict(street_address='1 A St')),
               context_json=json.dumps(dict(children=[])), cited_sources='', evidence_json='[]')
    (draw_dir / 'packets.jsonl').write_text(json.dumps(dict(row=row, masked=[], plant='street_address', urls=[])) + '\n')
    (draw_dir / 'sample.csv').write_text('pos,blind_id,kind,table,record_id,provider,check_coin,plant_field,donor_record_id\n1,A13-0001,plant,sites,plant-x,astra,0,street_address,\n')
    (draw_dir / 'families.json').write_text('{}')
    (draw_dir / 'receipts.json').write_text(json.dumps(dict(receipts={}, no_replayer={}, counts={})))
    ok = lambda provider, prompt, procs, timeout=0: dict(provider=provider, text=json.dumps(dict(findings=[finding('street_address', 'VERIFIED'), finding('polymer_relevance', 'VERIFIED')])), model=rd.MODELS[provider],
                                                       usage=dict(input_tokens=5), metered=True, error='', elapsed=0.0, prompt_bytes=1)
    real_call, rd.call_model = rd.call_model, ok
    try:
        rd.run_stage(draw_dir, cache, out, SimpleNamespace(stop_at=3, window=1, max_tokens_m=0))
    finally:
        rd.call_model = real_call
    doc = json.loads((out / 'results.json').read_text())
    assert doc['status'] == 'SUSPENDED_PLANT_MISSED' and 'missed' in doc['invalid']


@case('score: aggregates only, with denominators; replay: no-replayer classes block and 5500 is lead-only')
def _():
    work = Path(tempfile.mkdtemp(prefix='a13-check-'))
    res = dict(status='STOPPED_AT_K', k=3, stop_at=3, stopped_at=9, invalid=None, incomplete_calls=[], input_tokens_spent={},
               results=[dict(pos=i, kind='real', provider='astra', contradicted_core=['street_address'] if i < 4 else [], contradicted_desc=[], unconfirmed={'processes': 'unsettled'} if i % 2 else {},
                             audited=['site_name', 'processes'], exception=False, second_provider=None, k=i < 4) for i in range(1, 10)])
    (work / 'results.json').write_text(json.dumps(res))
    (work / 'ledger.jsonl').write_text(json.dumps(dict(role='primary', provider='astra', metered=True, usage=dict(input_tokens=100, cache_read_tokens=50))) + '\n')
    import contextlib, io
    with contextlib.redirect_stdout(io.StringIO()):
        rd.score_stage(work)
    s = json.loads((work / 'score.json').read_text())
    assert s['k'] == 3 and s['unconfirmed_by_field']['processes'] == dict(unconfirmed=5, audited_values=9, share=0.556)
    assert s['cost_per_call_by_provider']['astra']['mean_input_tokens'] == 150
    assert 'record_id' not in json.dumps(s), 'the publication output carries aggregates only'
    import replays
    rec = lambda **kw: dict(dict(record_table='sites', record_id='SITE-1', claim_type='size_band', source_class='government_filing', source_ref='', claim_detail=''), **kw)
    assert replays.band_kind(rec(source_ref='DOL EFAST2 Form 5500-SF, sponsor X')) == 'form5500'
    assert replays.band_kind(rec(source_ref='https://data.sba.gov/x (SBA PPP LoanNumber 1)')) == 'ppp'
    assert replays.band_kind(rec(source_ref='OSHA ITA Form 300A CY2025, establishment_id 12')) == 'osha_ita'


@case('replay receipts: a matched control passes; a wrong operator, a wrong street and a 2015 vintage do not bind; a newer different band contradicts')
def _():
    import replays
    site = dict(site_id='SITE-1', org_id='ORG-1', site_name='Acme Plastics - Akron', street_address='12 Elm Street', city='Akron', zip='44301')
    orgs = {'ORG-1': dict(org_id='ORG-1', legal_name='Acme Plastics, Inc.', trade_names='', parent_org_id='', ultimate_parent_name='', successor_org_id='')}
    base = dict(establishment_name='Acme Plastics', street_address='12 Elm St', city='Akron', zip_code='44301', annual_average_employees='79', year_filing_for='2025',
                company_name='', ein='', establishment_id='5')
    got = lambda **kw: replays.receipt(site, orgs, dict(base, **kw), 'osha_ita', 'x/y.csv', '2016-11-24', '50-99')
    assert (got()['status'], got()['reason']) == ('MATCHES', 'band_equal')
    assert got(establishment_name='Zeta Tire')['reason'] == 'filing_does_not_bind_operator_and_street'
    assert got(street_address='99 Oak Ave')['reason'] == 'filing_does_not_bind_operator_and_street'
    assert got(year_filing_for='2015')['reason'] == 'stale_over_10_years'
    assert got(annual_average_employees='300')['status'] == 'CONTRADICTS'


if __name__ == '__main__':
    print(f'check.py PASS: {len(PASSED)} planted cases')
    for n in PASSED:
        print('  -', n)
