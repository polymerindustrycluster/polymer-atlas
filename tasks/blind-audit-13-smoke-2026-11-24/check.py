#!/usr/bin/env python3
"""Selftest on a synthetic fixture: no real frame, no network, no model call. Each planted case must fail for the right reason.

    python3 tasks/blind-audit-13-smoke-2026-11-24/check.py
"""
import csv, hashlib, json, sys, tempfile
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reading as rd  # noqa: E402
import smoke  # noqa: E402

PASSED = []


import os  # noqa: E402
FAILED = []


def case(name):
    def deco(fn):
        try:
            fn()
            PASSED.append(name)
        except Exception as e:  # noqa: BLE001
            if not os.environ.get('CHECK_CONTINUE'):
                raise
            FAILED.append(f'{name}: {type(e).__name__} {str(e)[:100]}')
    return deco


def expect_raises(exc, fn, why):
    try:
        fn()
    except exc as e:
        assert why in str(e), f'raised for the wrong reason: {e}'
        return
    raise AssertionError(f'expected a refusal ({why}); none raised')


PAGE = 'Acme Plastics, Inc. is located at 99 Oak Avenue, Akron, Ohio. We mold thermoplastic parts.'
SRC = {'S1': PAGE}


def finding(target, verdict, quote='', source_value='', **kw):
    return dict(target=target, verdict=verdict, source_id='S1', quote=quote, source_value=source_value, settling_fact=kw.pop('settling_fact', ''), **kw)


def read(findings, targets, held=None):
    return rd.read_findings(dict(findings=findings), SRC, targets, held if held is not None else HELD)


T = ['legal_name', 'street_address', 'processes', 'polymer_relevance']
OK = [finding(t, 'VERIFIED') for t in T]


def with_(**by_target):
    return [by_target.get(f['target'], f) for f in OK]


HELD = {'legal_name': 'Acme Plastics LLC', 'street_address': '12 Elm Street', 'processes': 'injection_molding', 'polymer_relevance': ''}


def outcome(findings, targets=T, held=None):
    return rd.record_outcome(rd.combine(read(findings, targets, held or HELD), None))


@case('a contradicted core field with a replayed quote reaches k')
def _():
    o = outcome(with_(street_address=finding('street_address', 'CONTRADICTED', 'located at 99 Oak Avenue, Akron', '99 Oak Avenue')))
    assert o['k'] and o['contradicted_core'] == ['street_address']


@case('a contradiction whose quote is not on the page does not reach k')
def _():
    o = outcome(with_(street_address=finding('street_address', 'CONTRADICTED', 'moved to 7 Pine Road', '7 Pine Road')))
    assert not o['k'] and o['unconfirmed']['street_address'] == 'quote_not_replayed'


@case('an unconfirmed core claim does not reach k and is tallied')
def _():
    o = outcome(with_(polymer_relevance=finding('polymer_relevance', 'UNCONFIRMED', settling_fact='the plant page naming its processes')))
    assert not o['k'] and o['unconfirmed'] == {'polymer_relevance': 'unsettled'}


@case('a contradicted descriptive field does not reach k and is tallied by field')
def _():
    o = outcome(with_(processes=finding('processes', 'CONTRADICTED', 'We mold thermoplastic parts', 'thermoplastic parts')))
    assert not o['k'] and o['contradicted_desc'] == ['processes']


@case('a legal-form-only name difference is not a contradiction; a division or different entity is')
def _():
    held = {'legal_name': 'Acme Plastics LLC'}
    o = outcome(with_(legal_name=finding('legal_name', 'CONTRADICTED', 'Acme Plastics, Inc. is located', 'Acme Plastics, Inc.')), held=held)
    assert not o['k'] and o['notes'] == ['legal_name'], o
    for other in ('Acme Plastics Division of Zeta Holdings', 'Acme Plastic Systems', 'The Acme Group'):
        assert not rd.name_equivalent('Acme Plastics LLC', other), other
    assert rd.name_equivalent('The Acme Plastics Co.', 'ACME PLASTICS, INC')
    assert rd.name_equivalent('Acme L.L.C.', 'Acme LLC'), 'dotted legal-form initials are punctuation'
    SRC['S2'] = 'Acme Plastics Division of Zeta Holdings makes parts.'
    f2 = dict(finding('legal_name', 'CONTRADICTED', 'Acme Plastics Division of Zeta Holdings', 'Acme Plastics Division of Zeta Holdings'), source_id='S2')
    o = outcome(with_(legal_name=f2), held=held)
    assert o['k'], 'a different entity name must be contradicted'


@case('a missing assessment is unconfirmed, never verified')
def _():
    o = outcome(OK[:-1])
    assert o['unconfirmed'] == {'polymer_relevance': 'missing_assessment'} and not o['k']


@case('a replayed contradiction from the second read stands; a vote cannot erase it; the builder-exception reader cannot clear an unconfirmed claim')
def _():
    prim = read(OK, T)
    sec = read(with_(street_address=finding('street_address', 'CONTRADICTED', 'located at 99 Oak Avenue', '99 Oak Avenue')), T)
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


@case('a core field needs its locality beside it (a withheld one blocks); a NAICS value with no source name is NOT_INSPECTED, not a block')
def _():
    row = lambda t, v: dict(table=t, values_json=json.dumps(v))
    rd.dependency_check(row('sites', dict(street_address='1 A St', city='Akron', state='OH')), smoke.DEPENDS)
    rd.dependency_check(row('sites', dict(street_address='1 A St', city='', state='OH')), smoke.DEPENDS)  # blank in the data: not a masking defect
    expect_raises(ValueError, lambda: rd.dependency_check(row('sites', dict(street_address='1 A St', city=rd.WITHHELD, state='OH')), smoke.DEPENDS), '(withheld)')
    org = dict(table='organizations', values_json=json.dumps(dict(naics_primary='326199', naics_primary_source_type='directory_assigned', naics_primary_source_name='', naics_confidence='high', legal_name='X')),
               context_json=json.dumps(dict(children=[dict(table='registry_links', values=dict(registry='FRS', registry_id='1'), context={}), dict(table='site_capabilities', values=dict(term='t'), context={})])))
    assert rd.not_inspected_targets(org, None) == ['naics_confidence', 'naics_primary', 'naics_primary_source_type'], 'blank NAICS source name: filed values not inspected'
    assert rd.not_inspected_targets(org, dict(fields=[], children=['registry_links'])) == ['c1.registry', 'c1.registry_id', 'naics_confidence', 'naics_primary', 'naics_primary_source_type']
    assert 'naics_primary' not in rd.targets_of(dict(org, columns_under_audit='naics_primary;legal_name'), ['naics_primary']), 'not-inspected targets leave the checklist'


@case('a contradiction must bind a different source value: a corroborating address, or a value equal to the held one, is not a contradiction')
def _():
    o = outcome(with_(street_address=finding('street_address', 'CONTRADICTED', 'located at 99 Oak Avenue, Akron', '99 Oak Avenue')), held=dict(HELD, street_address='99 Oak Avenue'))
    assert not o['k'] and o['unconfirmed']['street_address'] == 'source_value_equals_held'
    o = outcome(with_(street_address=finding('street_address', 'CONTRADICTED', 'located at 99 Oak Avenue, Akron', '')))
    assert not o['k'] and o['unconfirmed']['street_address'] == 'source_value_not_in_quote'
    o = outcome(with_(street_address=finding('street_address', 'CONTRADICTED', 'We mold thermoplastic parts', '99 Oak Avenue')))
    assert not o['k'], 'the incompatible value must be inside the replayed quote'
    o = outcome(with_(street_address=finding('street_address', 'CONTRADICTED', 'located at 99 Oak Avenue, Akron', '99 Oak Avenue')))
    assert o['k'] and o['deciding']['street_address']['quote'] == 'located at 99 Oak Avenue, Akron', 'the deciding quote is kept'


@case('a verified answer must cite a source that exists; a receipt is a source')
def _():
    f = read([dict(finding('processes', 'VERIFIED'), source_id='S9')] + OK[:1], ['processes', 'legal_name'])
    assert f['processes']['reason'] == 'verified_without_source'
    f = rd.read_findings(dict(findings=[dict(target='employee_band_site', verdict='CONTRADICTED', source_id='R1', quote='band 100-249 differs', source_value='100-249')]),
                         {'R1': 'Filing row: employees 120 -> band 100-249 differs from the held band.'}, ['employee_band_site'], dict(employee_band_site='50-99'))
    assert f['employee_band_site']['status'] == 'CONTRADICTED', 'a contradiction quoting a replay receipt must be able to count'


@case('plant credit needs a specific settling fact, not a blindness or availability excuse')
def _():
    ex = lambda fact: read(with_(street_address=finding('street_address', 'UNCONFIRMED', settling_fact=fact)), T)
    assert not rd.plant_detected(ex('withheld'), 'street_address')
    assert not rd.plant_detected(ex('the value is withheld for blindness'), 'street_address')
    assert rd.plant_detected(ex('the street printed on the plant contact page'), 'street_address')


@case('plants prefer core and locality fields and come only from eligible records outside the sample')
def _():
    secret = b'plant-secret-' * 4
    keys = [('sites', f'SITE-{i:04}') for i in range(200)]
    rows = [dict(site_id=k[1], org_id='O', site_name=f'Plant {i}', street_address=f'{i} Main St', city='Akron', county='Summit', employee_band_site='10-49') for i, k in enumerate(keys)]
    R = SimpleNamespace(at='0' * 40, rows=lambda t: rows if t == 'sites' else [])
    plants = smoke.make_plants(R, secret, keys, set(), {k: set() for k in keys})
    assert len(plants) == 9 and all(p['field'] in smoke.PLANT_PREFERRED for p in plants), [p['field'] for p in plants]


class FakeR:
    """Just enough of the pinned reader for provenance and coverage cases."""
    at = '0' * 40
    def __init__(self, **tables):
        self.t = tables
    def rows(self, t):
        return self.t.get(t, [])
    def git(self, *a):
        return '2026-11-24' if a[:2] == ('show', '-s') else ''


@case('provenance reaches every scoped child (host_org_id equipment, archive links); mixed uncertain provenance resolves explicitly')
def _():
    R = FakeR(organizations=[dict(org_id='ORG-1', created_by='claude-code a')], ecosystem=[], sites=[],
              evidence=[dict(evidence_id='EVD-1', record_table='organizations', record_id='ORG-1', created_by='claude-code a')],
              equipment=[dict(host_org_id='ORG-1', site_id='', program_id='', created_by='codex build-x')],
              archive_links=[dict(evidence_id='EVD-1', created_by='gemini arc')])
    R.git = lambda *a: ''
    labels = smoke.builder_labels(R, [('organizations', 'ORG-1')])
    assert labels[('organizations', 'ORG-1')] == {'claude-code a', 'codex build-x', 'gemini arc'}, labels
    assert smoke.route({'uncertain', 'openai'}) == 'hydrogen' and smoke.route({'uncertain'}) == 'astra'


def run_fixture(items, fams=None, packets_extra=None, receipt_extra=None, skip_packet=()):
    work = Path(tempfile.mkdtemp(prefix='a13-check-'))
    draw_dir, cache, out = work / 'draw', work / 'cache', work / 'run'
    draw_dir.mkdir(), cache.mkdir()
    (cache / 'page.txt').write_text(PAGE)
    (cache / 'manifest.json').write_text(json.dumps({'https://acme.example/': dict(status='ok', final_url='https://acme.example/', fetched_at='t', text_file='page.txt')}))
    sample, pk = [], []
    for pos, (kind, name, prov) in enumerate(items, 1):
        bid = f'A13-{pos:04}'
        row = dict(blind_id=bid, record_label=name, table='sites', columns_under_audit='site_name;street_address', values_json=json.dumps(dict(site_name='Acme Plastics', street_address='12 Elm Street')),
                   context_json=json.dumps(dict(children=[])), cited_sources='https://acme.example/', evidence_json='[]')
        if name not in skip_packet:
            pk.append(json.dumps(dict(row=row, masked=[], plant='street_address' if kind == 'plant' else '', urls=['https://acme.example/'], not_inspected=[])))
        sample.append(dict(pos=pos, blind_id=bid, kind=kind, table='sites', record_id=name, provider=prov, check_coin='0', plant_field='street_address' if kind == 'plant' else '', donor_record_id=''))
    with open(draw_dir / 'sample.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, list(sample[0]))
        w.writeheader(), w.writerows(sample)
    (draw_dir / 'packets.jsonl').write_text('\n'.join(pk) + '\n')
    (draw_dir / 'families.json').write_text(json.dumps(fams or {}))
    (draw_dir / 'receipts.json').write_text(json.dumps(dict(receipts={}, counts={}, not_inspected_classes={})))
    (draw_dir / 'draw_receipt.json').write_text(json.dumps(dict(at='x', inputs=dict(records_sha256='x', **(receipt_extra or {})), n_real=sum(1 for i in items if i[0] == 'real'), plants={},
                                                                sample_sha256=hashlib.sha256((draw_dir / 'sample.csv').read_bytes()).hexdigest())))
    return draw_dir, cache, out


def good(name, provider, street_bad=False, prompts=None):
    street = 'located at 99 Oak Avenue, Akron' if street_bad else ''
    f = [finding('site_name', 'VERIFIED'), finding('street_address', 'CONTRADICTED', street, '99 Oak Avenue') if street else finding('street_address', 'VERIFIED'), finding('polymer_relevance', 'VERIFIED')]
    return dict(provider=provider, text=json.dumps(dict(findings=f)), model=rd.MODELS[provider], usage=dict(input_tokens=1000, cache_read_tokens=0), metered=True, error='', elapsed=0.0, prompt_bytes=1)


def name_of(prompt):
    return json.loads(prompt.split('=== RECORD ===')[1].split('=== SOURCES')[0])['record']


def patched(fake, fn):
    real = rd.call_model
    rd.call_model = fake
    try:
        return fn()
    finally:
        rd.call_model = real


ARGS = lambda **kw: SimpleNamespace(**dict(dict(stop_at=3, window=1, max_tokens_m=0), **kw))


@case('run: sealed-order scoring, the stop cancels the rest, blind second reads, uncertain always re-read, plants interleaved')
def _():
    items = [('real', 'clean-1', 'astra'), ('plant', 'plant-a', 'astra'), ('real', 'bad-1', 'astra'), ('real', 'unc-1', 'hydrogen'), ('real', 'bad-2', 'astra'),
             ('plant', 'plant-h', 'hydrogen'), ('real', 'bad-3', 'astra'), ('real', 'late-1', 'astra'), ('real', 'late-2', 'astra')]
    draw_dir, cache, out = run_fixture(items, {'sites|clean-1': ['uncertain'], 'sites|unc-1': ['openai']})
    prompts, called = {}, Counter()

    def fake(provider, prompt, procs, timeout=0):
        name = name_of(prompt)
        prompts.setdefault(name, []).append((provider, prompt))
        called[name] += 1
        if name == 'unc-1':
            f = [finding('site_name', 'UNCONFIRMED', settling_fact='the plant page naming this site'), finding('street_address', 'VERIFIED'), finding('polymer_relevance', 'VERIFIED')]
            return dict(good(name, provider), text=json.dumps(dict(findings=f)))
        return good(name, provider, street_bad=name.startswith(('bad', 'plant')))
    rc = patched(fake, lambda: rd.run_stage(draw_dir, cache, out, ARGS()))
    doc = json.loads((out / 'results.json').read_text())
    assert doc['status'] == 'STOPPED_AT_K' and doc['k'] == 3 and doc['stopped_at'] == 7 and rc == 0, doc['status']
    assert called['late-1'] == called['late-2'] == 0, 'calls after the stop must be cancelled'
    assert [r['pos'] for r in doc['incomplete_calls']] == [8, 9], doc['incomplete_calls']
    assert [p['detected'] for p in [r for r in doc['results'] if r['kind'] == 'plant']] == [True, True]
    clean = next(r for r in doc['results'] if r['record_id'] == 'clean-1')
    assert clean['second_provider'] == 'hydrogen' and clean['coin'] == '0', 'an uncertain record always gets a Hydrogen second read'
    assert len(prompts['bad-1']) == 2 and prompts['bad-1'][0][1] == prompts['bad-1'][1][1], 'the second read sees the same prompt: no flag, no first verdict'
    unc = next(r for r in doc['results'] if r['record_id'] == 'unc-1')
    assert unc['second_provider'] == 'sonnet' and unc['exception'] is False
    bad = next(r for r in doc['results'] if r['record_id'] == 'bad-1')
    assert bad['deciding']['street_address']['quote'] == 'located at 99 Oak Avenue, Akron'
    ledger = [json.loads(l) for l in open(out / 'ledger.jsonl')]
    assert any(l['role'] == 'lock' for l in ledger) and all(l.get('metered') for l in ledger if l['role'] in ('primary', 'second'))


@case('run: the sealed sample is what runs: an altered sample, a lost packet and a tuned frame run are refused, never COMPLETE')
def _():
    items = [('plant', 'plant-x', 'astra'), ('real', 'r-1', 'astra')]
    draw_dir, cache, out = run_fixture(items, skip_packet=('plant-x',))
    expect_exit = lambda fn, why: expect_raises(SystemExit, fn, why)
    expect_exit(lambda: rd.run_stage(draw_dir, cache, out, ARGS()), 'no packet')
    draw_dir, cache, out = run_fixture(items)
    (draw_dir / 'sample.csv').write_text((draw_dir / 'sample.csv').read_text().replace('r-1', 'r-2'))
    expect_exit(lambda: rd.run_stage(draw_dir, cache, out, ARGS()), 'differs from the draw receipt')
    draw_dir, cache, out = run_fixture(items, receipt_extra=dict(preflight_receipt_sha256='x'))
    expect_exit(lambda: rd.run_stage(draw_dir, cache, out, ARGS()), 'not 40 real records')
    rec = json.loads((draw_dir / 'draw_receipt.json').read_text())
    rec.update(n_real=40, plants=dict.fromkeys(rd.CAPS_M, 3))
    (draw_dir / 'draw_receipt.json').write_text(json.dumps(rec))
    expect_exit(lambda: rd.run_stage(draw_dir, cache, out, ARGS(stop_at=5)), 'stop count is 3')


@case('run: dispatch is bounded to the unscored window; a failed or unmetered call halts without a retry; a missing second read is a halt, not a crash')
def _():
    import threading, time
    items = [('real', f'r-{i}', 'astra') for i in range(1, 7)]
    draw_dir, cache, out = run_fixture(items)
    release, called = threading.Event(), []

    def slow(provider, prompt, procs, timeout=0):
        name = name_of(prompt)
        called.append(name)
        if name == 'r-1':
            release.wait(5)
        return good(name, provider)
    t = threading.Thread(target=lambda: patched(slow, lambda: rd.run_stage(draw_dir, cache, out, ARGS(window=2, stop_at=99))))
    t.start()
    time.sleep(1.0)
    started = set(called)
    release.set()
    t.join(30)
    assert started == {'r-1', 'r-2'}, f'only the window may start while r-1 is open: {started}'
    draw_dir, cache, out = run_fixture(items[:2])
    bad = lambda provider, prompt, procs, timeout=0: dict(good('x', provider), error='no output', text='', usage=None, metered=False)
    calls = Counter()
    def failing(provider, prompt, procs, timeout=0):
        calls[name_of(prompt)] += 1
        return bad(provider, prompt, procs)
    patched(failing, lambda: rd.run_stage(draw_dir, cache, out, ARGS()))
    doc = json.loads((out / 'results.json').read_text())
    assert doc['status'] == 'SUSPENDED_NO_OUTPUT' and calls['r-1'] == 1 and not doc['results'], 'a failed call must halt, not retry past the halt'
    draw_dir, cache, out = run_fixture([('real', 'unc-2', 'astra')])
    def second_fails(provider, prompt, procs, timeout=0):
        if provider == 'astra':
            return dict(good('x', provider), text=json.dumps(dict(findings=[finding('site_name', 'UNCONFIRMED', settling_fact='the plant page naming this site'), finding('street_address', 'VERIFIED'), finding('polymer_relevance', 'VERIFIED')])))
        return bad(provider, prompt, procs)
    patched(second_fails, lambda: rd.run_stage(draw_dir, cache, out, ARGS()))
    assert json.loads((out / 'results.json').read_text())['status'] == 'SUSPENDED_NO_OUTPUT', 'SECOND_MISSING must halt cleanly and write results'


@case('run: a requested source is shared: the second reader gets the same bounded source set as the primary, and stage budgets halt for repricing')
def _():
    import site_corpus
    draw_dir, cache, out = run_fixture([('real', 'req-1', 'astra')])
    seen = []
    class FakeCorpus:
        def __init__(self, d): self.d = Path(d)
        def fetch(self, u):
            (self.d / 'req.txt').write_text('Requested page text about Acme.')
            return dict(status='ok', http_status=200, final_url=u, fetched_at='t', sha256='0', text_file='req.txt')
    def fake(provider, prompt, procs, timeout=0):
        seen.append((provider, prompt))
        first = finding('site_name', 'REQUEST', request_url='https://acme.example/contact') if len(seen) == 1 else finding('site_name', 'UNCONFIRMED', settling_fact='the plant page naming this site') if len(seen) == 2 else finding('site_name', 'VERIFIED')
        f = [first, finding('street_address', 'VERIFIED'), finding('polymer_relevance', 'VERIFIED')]
        return dict(good('x', provider), text=json.dumps(dict(findings=f)))
    real_corpus, site_corpus.Corpus = site_corpus.Corpus, FakeCorpus
    try:
        patched(fake, lambda: rd.run_stage(draw_dir, cache, out, ARGS()))
    finally:
        site_corpus.Corpus = real_corpus
    assert len(seen) == 3 and seen[1][1] == seen[2][1] and 'https://acme.example/contact' in seen[2][1], 'primary round 2 and the second read must see one source set'
    draw_dir, cache, out = run_fixture([('real', 'big-1', 'astra'), ('real', 'big-2', 'astra')])
    big = lambda provider, prompt, procs, timeout=0: dict(good(name_of(prompt), provider), usage=dict(input_tokens=5_000_000))
    patched(big, lambda: rd.run_stage(draw_dir, cache, out, ARGS(caps_m=dict(astra=1.0))))
    assert json.loads((out / 'results.json').read_text())['status'] == 'HALTED_TOKEN_BUDGET'


@case('a call is refused unless the resolved model is exactly the registry model and the input count is a real number')
def _():
    def agy(model, usage):
        res = dict(status='SUCCESS', response='{}', **({'usage': usage} if usage is not None else {}))
        return 0, '\n'.join(json.dumps(e) for e in ({'event': 'init', 'init': {'model': model}}, {'event': 'result', 'result': res})), ''
    council = lambda model, resolved, usage: (0, json.dumps(dict(providers=[dict(status='success', model=model, resolved_model=resolved, output='{}', usage=usage)])), '')
    real = rd.run_process
    try:
        for model in ('Gemini 4 Neon (High)', 'Gemini 4 Argon (High)', 'Gemini 4 Carbon (High)', 'Gemini 4 Hydrogen (High) Preview'):
            rd.run_process = lambda *a, m=model, **k: agy(m, dict(input_tokens=10))
            assert 'refused' in rd.call_model('hydrogen', 'x', set())['error'], model
        rd.run_process = lambda *a, **k: agy('Gemini 4 Hydrogen (High)', dict(input_tokens=None))
        assert 'unmetered' in rd.call_model('hydrogen', 'x', set())['error']
        rd.run_process = lambda *a, **k: agy('Gemini 4 Hydrogen (High)', None)
        assert 'unmetered' in rd.call_model('hydrogen', 'x', set())['error']
        rd.run_process = lambda *a, **k: agy('Gemini 4 Hydrogen (High)', dict(input_tokens=10))
        ok = rd.call_model('hydrogen', 'x', set())
        assert not ok['error'] and rd.input_tokens(ok['usage']) == 10
        rd.run_process = lambda *a, **k: council('gpt-6.2-sol/medium', None, dict(input_tokens=5))
        assert 'refused' in rd.call_model('astra', 'x', set())['error']
        rd.run_process = lambda *a, **k: council('gpt-6.2-astra/max', None, None)
        assert 'unmetered' in rd.call_model('astra', 'x', set())['error']
        rd.run_process = lambda *a, **k: council('sonnet/medium', 'claude-opus-5-5', dict(input_tokens=5))
        assert 'refused' in rd.call_model('sonnet', 'x', set())['error']
        rd.run_process = lambda *a, **k: council('sonnet/medium', 'claude-sonnet-5-5', dict(input_tokens=2, modelUsage={'claude-sonnet-5-5': dict(inputTokens=2, cacheReadInputTokens=600, cacheCreationInputTokens=1200)}))
        ok = rd.call_model('sonnet', 'x', set())
        assert not ok['error'] and rd.input_tokens(ok['usage']) == 1802, 'claude input counts cache reads and writes'
    finally:
        rd.run_process = real


@case('filing replay: the cited row binds first; an older different band under a newer supporting filing matches; a newer different band contradicts; no single cited row is unresolved')
def _():
    import replays
    site = dict(site_id='SITE-1', org_id='ORG-1', site_name='Acme Plastics - Akron', street_address='12 Elm Street', city='Akron', zip='44301', employee_band_site='50-99')
    orgs = {'ORG-1': dict(org_id='ORG-1', legal_name='Acme Plastics, Inc.', trade_names='', parent_org_id='', ultimate_parent_name='', successor_org_id='')}
    row = lambda year, n: dict(establishment_name='Acme Plastics', street_address='12 Elm St', city='Akron', zip_code='44301', annual_average_employees=str(n), year_filing_for=str(year),
                               company_name='', ein='', establishment_id='5')
    ev = lambda year: dict(source_ref=f'OSHA ITA Form 300A CY{year}, establishment_id 5', claim_detail='')
    br = lambda year, hits: replays.band_receipt(site, orgs, ev(year), True, {'5': [(r, 'f') for r in hits]}, {}, {}, {}, None, '2016-11-24')
    assert br(2020, [row(2020, 20), row(2025, 79)])['status'] == 'MATCHES', 'newer filing supports the held band'
    assert br(2020, [row(2020, 79), row(2025, 300)])['status'] == 'CONTRADICTS', 'a newer different band supersedes'
    assert br(2020, [row(2025, 79)])['reason'] == 'cited_row_not_identified'
    assert br(2020, [row(2020, 79), row(2020, 20)])['reason'] == 'cited_row_not_identified'
    assert br(2025, [])['status'] == 'UNRESOLVED'


@case('coverage end to end: no-replayer classes are counted as not inspected (no receipt, no block); bands with a replayer keep their receipts')
def _():
    import replays
    site = dict(site_id='SITE-1', org_id='ORG-1', site_name='Acme', street_address='12 Elm Street', city='Akron', zip='44301', employee_band_site='10-49', naics_primary='', naics_primary_source_type='')
    org = dict(org_id='ORG-1', legal_name='Acme', employee_band_ohio='', naics_primary='326199', naics_primary_source_type='government_filing')
    ev = lambda eid, ref, cls='government_filing': dict(evidence_id=eid, record_table='sites', record_id='SITE-1', claim_type='size_band', source_class=cls, source_ref=ref, claim_detail='')
    R = FakeR(sites=[site], organizations=[org], ecosystem=[], registry_links=[dict(org_id='ORG-1', site_id='', registry='FRS', registry_id='1')], code_assignments=[dict(org_id='ORG-1', code_system='NAICS', source_type='government_filing')],
              evidence=[ev('E1', 'https://data.sba.gov/x (SBA PPP LoanNumber 1)'), ev('E2', 'DOL EFAST2 Form 5500-SF, sponsor X')])
    receipts, ni_classes, counts, ni = replays.coverage(R, [('sites', 'SITE-1'), ('organizations', 'ORG-1')], Path('/nonexistent-store'))
    assert counts['band:ppp'] == {'not_inspected': 1} and counts['registry:FRS'] == {'not_inspected': 1} and counts['naics:government_filing'] == {'not_inspected': 1}
    assert counts['naics:code_assignment'] == {'not_inspected': 1} and counts['band:form5500'] == {'LEAD_ONLY': 1}
    assert [r['status'] for r in receipts['sites|SITE-1']] == ['LEAD_ONLY'] and 'band:ppp' in ni_classes
    assert ni['sites|SITE-1']['fields'] == ['employee_band_site'] and ni['organizations|ORG-1']['children'] == ['code_assignments', 'registry_links']
    assert 'employee_band_site' in rd.not_inspected_targets(dict(table='sites', values_json=json.dumps(dict(employee_band_site='10-49')), context_json='{}'), ni['sites|SITE-1'])


@case('score: every field has its denominator and error rate (zero included), NOT_INSPECTED is tallied by field, cost charges failed calls')
def _():
    work = Path(tempfile.mkdtemp(prefix='a13-check-'))
    res = dict(status='STOPPED_AT_K', k=3, stop_at=3, stopped_at=9, invalid=None, incomplete_calls=[], input_tokens_spent={}, replay_coverage={'band:osha_ita': {'MATCHES': 2}}, not_inspected_classes={'band:ppp': 3},
               results=[dict(pos=i, kind='real', provider='astra', contradicted_core=['street_address'] if i < 4 else [], contradicted_desc=[], unconfirmed={'processes': 'unsettled'} if i % 2 else {},
                             audited=['site_name', 'processes'], not_inspected=['employee_band_site'], exception=False, second_provider=None, k=i < 4, disputed=[]) for i in range(1, 10)]
              + [dict(pos=10, kind='plant', provider='astra', detected=True)])
    (work / 'results.json').write_text(json.dumps(res))
    rows = [dict(role='primary', provider='astra', kind='real', metered=True, error='', usage=dict(input_tokens=100, cache_read_tokens=50)),
            dict(role='primary', provider='astra', kind='real', metered=False, error='unmetered call', usage=dict(input_tokens=40))]
    (work / 'ledger.jsonl').write_text('\n'.join(json.dumps(r) for r in rows) + '\n')
    import contextlib, io
    with contextlib.redirect_stdout(io.StringIO()):
        rd.score_stage(work)
    s = json.loads((work / 'score.json').read_text())
    assert s['by_field']['site_name'] == dict(audited_values=9, contradicted=0, error_rate=0.0, unconfirmed=0, unconfirmed_share=0.0, not_inspected=0), 'a zero-error field is still reported'
    assert s['by_field']['processes']['unconfirmed'] == 5 and s['not_inspected_by_field'] == {'employee_band_site': 9} and s['replay_coverage']
    c = s['cost_by_provider']['astra']
    assert c['requests'] == 2 and c['failed'] == 1 and c['tokens_on_failed'] == 40 and c['input_tokens'] == 190 and c['completed_real'] == 1, c
    assert 'record_id' not in json.dumps(s), 'the publication output carries aggregates only'


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
    for f in FAILED:
        print('  FAIL', f)
    sys.exit(1 if FAILED else 0)
