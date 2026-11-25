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
    assert not rd.plant_detected(read(with_(street_address=finding('street_address', 'UNCONFIRMED', settling_fact='the street on the own site')), T), 'street_address'), 'UNCONFIRMED never detects'
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
    expect_raises(ValueError, lambda: rd.dependency_check(row('sites', dict(street_address='1 A St', city='', state='OH')), smoke.DEPENDS), '(withheld or blank)')
    expect_raises(ValueError, lambda: rd.dependency_check(row('organizations', dict(hq_county='Summit', hq_city='')), smoke.DEPENDS), 'hq_city')
    rd.dependency_check(row('organizations', dict(hq_county='', hq_city='')), smoke.DEPENDS)  # no core claim, no dependency
    expect_raises(ValueError, lambda: rd.dependency_check(row('sites', dict(street_address='1 A St', city=rd.WITHHELD, state='OH')), smoke.DEPENDS), '(withheld or blank)')
    org = dict(table='organizations', values_json=json.dumps(dict(naics_primary='326199', naics_primary_source_type='directory_assigned', naics_primary_source_name='', naics_confidence='high', legal_name='X')),
               context_json=json.dumps(dict(children=[dict(table='registry_links', values=dict(registry='FRS', registry_id='1'), context={}), dict(table='site_capabilities', values=dict(term='t'), context={})])))
    assert rd.not_inspected_targets(org, None) == ['naics_confidence', 'naics_primary', 'naics_primary_source_type'], 'blank NAICS source name: filed values not inspected'
    assert rd.not_inspected_targets(org, dict(fields=[], children=[dict(table='registry_links', match=dict(registry='FRS', registry_id='1'))])) == ['c1.registry', 'c1.registry_id', 'naics_confidence', 'naics_primary', 'naics_primary_source_type']
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


SRC['S3'] = 'Visit us at 12 Elm Street, Akron, Ohio 44301.'
SRC['S4'] = 'Moved to 112 Elm Street, Akron.'
sid = lambda f, sid_: dict(f, source_id=sid_)


@case('C: a plant passes only when the swap is named: UNCONFIRMED never, an unreplayed or restating CONTRADICTED never, a replaying different value does')
def _():
    det = lambda f: rd.plant_detected(read(with_(street_address=f), T), 'street_address')
    for fact in ('the street printed on the plant contact page', 'We need more information', 'withheld'):
        assert not det(finding('street_address', 'UNCONFIRMED', settling_fact=fact)), fact  # planted value is HELD's street
    assert not det(finding('street_address', 'CONTRADICTED', 'moved to 7 Pine Road', '7 Pine Road')), 'a quote that does not replay on the cached bytes'
    assert not det(sid(finding('street_address', 'CONTRADICTED', 'Visit us at 12 Elm Street, Akron', '12 Elm Street'), 'S3')), 'a contradiction restating the planted value'
    assert not det(sid(finding('street_address', 'CONTRADICTED', 'Visit us at 12 Elm Street, Akron', '12 Elm Street, Akron'), 'S3')), 'restating it with the city added'
    assert det(finding('street_address', 'CONTRADICTED', 'located at 99 Oak Avenue, Akron', '99 Oak Avenue')), 'a replaying quote that states a different value detects'


def plant_row(street):
    return dict(table='sites', columns_under_audit='street_address;site_name', values_json=json.dumps(dict(street_address=street, site_name='Acme')), context_json=json.dumps(dict(children=[])))


@case('C: a record is plant-eligible only if its cached pages state the true value and the ideal answer would detect the swap; the draw gets the same verdict')
def _():
    srcs = {'S1': dict(excerpt=PAGE)}
    assert rd.plant_reason(plant_row('7 Pine Road'), 'street_address', '99 Oak Avenue', srcs) == ''
    assert rd.plant_reason(plant_row('7 Pine Road'), 'street_address', '5 Maple Court', srcs) == 'no_source_states_true_value', 'no true-value source: not eligible'
    assert rd.plant_reason(plant_row('99 Oak Ave'), 'street_address', '99 Oak Avenue', srcs) == 'planted_value_not_distinguishable_from_true_value', 'St for Street is no swap'
    assert rd.plant_reason(plant_row(rd.WITHHELD), 'street_address', '99 Oak Avenue', srcs) == 'planted_cell_withheld'
    assert rd.plant_reason(plant_row('7 Pine Road'), 'county', 'Summit', srcs) == 'field_not_on_checklist'
    assert not rd.distinct('street_address', '12 Elm St', '12 Elm Street') and rd.distinct('street_address', '12 Elm St', '99 Oak Ave')
    assert not rd.distinct('county', 'Summit', 'Summit County') and not rd.distinct('legal_name', 'Acme LLC', 'Acme Inc')
    keys = [('sites', f'SITE-{i:04}') for i in range(200)]
    rows = [dict(site_id=k[1], org_id='O', site_name=f'Plant {i}', street_address=f'{i} Main St', city='Akron', county='Summit', employee_band_site='10-49') for i, k in enumerate(keys)]
    R = SimpleNamespace(at='0' * 40, rows=lambda t: rows if t == 'sites' else [])
    fams = {k: set() for k in keys}
    odd = lambda cands: {(c['table'], c['record_id'], c['field']): '' if int(c['record_id'][-4:]) % 2 == 0 else 'no_source_states_true_value' for c in cands}
    report = {}
    plants = smoke.make_plants(R, b'plant-secret-' * 4, keys, set(), fams, odd, report)
    assert len(plants) == 9 and all(int(p['record_id'][-4:]) % 2 == 0 for p in plants), 'plants come only from eligible records'
    assert all(report[p]['eligible_records'] < report[p]['pool_records'] and report[p]['checked'] for p in smoke.PROVIDERS), report
    expect_raises(ValueError, lambda: smoke.make_plants(R, b'plant-secret-' * 4, keys, set(), fams, lambda cands: {(c['table'], c['record_id'], c['field']): 'no_source_states_true_value' for c in cands}), 'plant pool exhausted')


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


def run_fixture(items, fams=None, packets_extra=None, receipt_extra=None, skip_packet=(), rc=None, packet_due=0, children=()):
    work = Path(tempfile.mkdtemp(prefix='a13-check-'))
    draw_dir, cache, out = work / 'draw', work / 'cache', work / 'run'
    draw_dir.mkdir(), cache.mkdir()
    (cache / 'page.txt').write_text(PAGE)
    (cache / 'manifest.json').write_text(json.dumps({'https://acme.example/': dict(status='ok', final_url='https://acme.example/', fetched_at='t', text_file='page.txt')}))
    sample, pk = [], []
    for pos, (kind, name, prov) in enumerate(items, 1):
        bid = f'A13-{pos:04}'
        row = dict(blind_id=bid, record_label=name, table='sites', record_id=name, columns_under_audit='site_name;street_address', values_json=json.dumps(dict(site_name='Acme Plastics', street_address='12 Elm Street')),
                   context_json=json.dumps(dict(children=list(children))), cited_sources='https://acme.example/', evidence_json='[]')
        if name not in skip_packet:
            pk.append(json.dumps(dict(row=row, masked=[], plant='street_address' if kind == 'plant' else '', urls=['https://acme.example/'], not_inspected=[], **({} if packet_due is None else dict(due=packet_due)))))
        sample.append(dict(pos=pos, blind_id=bid, kind=kind, table='sites', record_id=name, provider=prov, check_coin='0', plant_field='street_address' if kind == 'plant' else '', donor_record_id=''))
    with open(draw_dir / 'sample.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, list(sample[0]))
        w.writeheader(), w.writerows(sample)
    (draw_dir / 'packets.jsonl').write_text('\n'.join(pk) + '\n')
    (draw_dir / 'families.json').write_text(json.dumps(fams or {}))
    (draw_dir / 'receipts.json').write_text(json.dumps(rc or dict(receipts={}, due={}, counts={}, not_inspected_classes={})))
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
    R = FakeR(sites=[site], organizations=[org], ecosystem=[], registry_links=[dict(org_id='ORG-1', site_id='', registry='FRS', registry_id='1')], code_assignments=[dict(org_id='ORG-1', code_system='NAICS', code_value='326199', source_type='government_filing')],
              evidence=[ev('E1', 'https://data.sba.gov/x (SBA PPP LoanNumber 1)'), ev('E2', 'DOL EFAST2 Form 5500-SF, sponsor X')])
    receipts, ni_classes, counts, ni = replays.coverage(R, [('sites', 'SITE-1'), ('organizations', 'ORG-1')], Path('/nonexistent-store'))[:4]
    assert counts['band:ppp'] == {'not_inspected': 1} and counts['registry:FRS'] == {'not_inspected': 1} and counts['naics:government_filing'] == {'not_inspected': 1}
    assert counts['naics:code_assignment'] == {'not_inspected': 1} and counts['band:form5500'] == {'LEAD_ONLY': 1}
    assert [r['status'] for r in receipts['sites|SITE-1']] == ['LEAD_ONLY'] and 'band:ppp' in ni_classes
    assert ni['sites|SITE-1']['fields'] == ['employee_band_site'] and sorted(c['table'] for c in ni['organizations|ORG-1']['children']) == ['code_assignments', 'registry_links']
    assert 'employee_band_site' in rd.not_inspected_targets(dict(table='sites', values_json=json.dumps(dict(employee_band_site='10-49')), context_json='{}'), ni['sites|SITE-1'])


def run_to_score(items, fake, children=(), args=None):
    """A real run_stage over fake model calls; returns the output directory holding results.json, ledger.jsonl and reads/."""
    draw_dir, cache, out = run_fixture(items, children=children)
    patched(fake, lambda: rd.run_stage(draw_dir, cache, out, args or ARGS(stop_at=99)))
    return out


def score(out):
    import contextlib, io
    with contextlib.redirect_stdout(io.StringIO()):
        rd.score_stage(out)
    return json.loads((out / 'score.json').read_text())


@case('B: every call is persisted (raw text, parsed answer, findings, round, provider; 0600, create-exclusive), the lock line names the file, and a second run into the same directory is refused')
def _():
    import stat
    items = [('plant', 'plant-b', 'astra'), ('real', 'bad-b', 'astra')]
    out = run_to_score(items, lambda provider, prompt, procs, timeout=0: good(name_of(prompt), provider, street_bad=True))
    files = sorted((out / 'reads').iterdir())
    assert len(files) == 3, [f.name for f in files]  # plant primary + real primary + real second
    ledger = [json.loads(l) for l in open(out / 'ledger.jsonl')]
    calls = [l for l in ledger if l.get('role') in ('primary', 'second')]
    assert len(calls) == 3 and all(stat.S_IMODE(f.stat().st_mode) == 0o600 for f in files)
    for l in calls:
        doc = json.loads((out / 'reads' / l['file']).read_text())
        assert doc['raw_text'] and doc['parsed']['findings'] and doc['findings'] and doc['provider'] == l['provider'] and doc['round'] == l['round'] and rd.sha256((out / 'reads' / l['file']).read_bytes()) == l['file_sha256']
    lock = next(l for l in ledger if l.get('role') == 'lock')
    assert lock['file'] and (out / 'reads' / lock['file']).exists()
    draw_dir, cache, _ = run_fixture(items)
    expect_raises(SystemExit, lambda: patched(lambda provider, prompt, procs, timeout=0: good(name_of(prompt), provider), lambda: rd.run_stage(draw_dir, cache, out, ARGS())), 'one run per output directory')


@case('B: score reads only the persisted files: a deleted file, an altered file, a flipped plant verdict and a different record outcome each refuse (exit 1), never skip')
def _():
    import shutil
    items = [('plant', 'plant-s', 'astra'), ('real', 'bad-s', 'astra'), ('real', 'clean-s', 'astra')]
    fake = lambda provider, prompt, procs, timeout=0: good(name_of(prompt), provider, street_bad=name_of(prompt) != 'clean-s')
    out = run_to_score(items, fake)
    s = score(out)
    assert s['reader_files_verified'] == 3 and s['plants']['by_provider']['astra'] == dict(planted=1, detected=1) and s['k'] == 1
    def broken(mutate, why):
        d = Path(tempfile.mkdtemp(prefix='a13-score-')) / 'run'
        shutil.copytree(out, d)
        mutate(d)
        expect_raises(SystemExit, lambda: rd.score_stage(d), why)
    broken(lambda d: next((d / 'reads').glob('*A13-0002-primary*')).unlink(), 'is missing')
    broken(lambda d: next((d / 'reads').glob('*A13-0002-primary*')).write_text('{}'), 'does not match its ledger hash')
    def flip(d):
        doc = json.loads((d / 'results.json').read_text())
        next(r for r in doc['results'] if r['kind'] == 'plant')['detected'] = False
        (d / 'results.json').write_text(json.dumps(doc))
    broken(flip, 'plant')
    def other_outcome(d):
        doc = json.loads((d / 'results.json').read_text())
        next(r for r in doc['results'] if r['record_id'] == 'bad-s').update(k=False, contradicted_core=[])
        (d / 'results.json').write_text(json.dumps(doc))
    broken(other_outcome, 'disagrees with its reader files')


@case('A1: a street that differs only by suffix or an added city is not a contradiction; names and statuses get no reverse test; a failed source supports no VERIFIED')
def _():
    f = lambda held, q, sv, src='S3': outcome(with_(street_address=sid(finding('street_address', 'CONTRADICTED', q, sv), src)), held=dict(HELD, street_address=held))
    assert not f('12 Elm St', 'at 12 Elm Street, Akron', '12 Elm Street')['k'], 'St vs Street'
    assert not f('12 Elm Street', 'Visit us at 12 Elm Street, Akron', '12 Elm Street, Akron')['k'], 'the source adds the city'
    assert f('12 Elm Street', 'Moved to 112 Elm Street', '112 Elm Street', 'S4')['k'], 'a different street number still contradicts'
    SRC['S5'] = 'Acme Plastics Division of Zeta Holdings makes parts.'
    o = outcome(with_(legal_name=sid(finding('legal_name', 'CONTRADICTED', 'Acme Plastics Division of Zeta Holdings', 'Acme Plastics Division of Zeta Holdings'), 'S5')), held={'legal_name': 'Acme Plastics'})
    assert o['k'], 'the held name is contained in the source name: still a different entity'
    SRC['S6'] = 'Status: not active since 2024.'
    o = rd.record_outcome(rd.combine(rd.read_findings(dict(findings=[sid(finding('status', 'CONTRADICTED', 'not active since 2024', 'not active'), 'S6')]), SRC, ['status'], dict(status='active')), None))
    assert o['k'], 'a status is not widened by reverse containment'
    got = rd.read_findings(dict(findings=[finding('street_address', 'VERIFIED')]), {'S1': ''}, ['street_address'], HELD)
    assert got['street_address']['status'] == 'UNCONFIRMED' and got['street_address']['reason'] == 'verified_without_source', 'an empty (failed) source cannot verify'


@case('C: fetch re-checks every sealed plant on the bytes it just fetched and refuses if one is no longer detectable')
def _():
    import replays
    draw_dir, cache, out = run_fixture([('plant', 'plant-f', 'astra'), ('real', 'r-f', 'astra')])
    row = json.loads((draw_dir / 'packets.jsonl').read_text().splitlines()[0])['row']
    (draw_dir / 'packets.jsonl').unlink()
    R = SimpleNamespace(at='x')
    pr = lambda R_, entries, approved, ids: ([(e, dict(row, values_json=json.dumps(dict(site_name='Acme Plastics', street_address='12 Elm Street'))), []) for e in entries], {})
    manifest = {'https://acme.example/': dict(status='ok', final_url='https://acme.example/', fetched_at='t', text_file='page.txt')}
    real_fetch, real_cov = rd.fetch_urls, replays.coverage
    rd.fetch_urls = lambda cache_dir, urls: manifest
    replays.coverage = lambda R_, keys, store: ({}, {}, {}, {}, {})
    try:
        expect_raises(SystemExit, lambda: rd.fetch_stage(draw_dir, cache, lambda at: R, pr, true_of=lambda *a: '5 Maple Court'), 'no longer detectable')
        assert rd.fetch_stage(draw_dir, cache, lambda at: R, pr, true_of=lambda *a: '99 Oak Avenue') == 0, 'a plant whose true value the page states still passes'
    finally:
        rd.fetch_urls, replays.coverage = real_fetch, real_cov


@case('A2: a packet must be its sealed row: another record ID, another table or a moved plant field is refused before any call')
def _():
    def tamper(mut):
        draw_dir, cache, out = run_fixture([('plant', 'plant-t', 'astra'), ('real', 'r-t', 'astra')])
        lines = [json.loads(l) for l in (draw_dir / 'packets.jsonl').read_text().splitlines()]
        mut(lines)
        (draw_dir / 'packets.jsonl').write_text('\n'.join(json.dumps(l) for l in lines) + '\n')
        called = []
        expect_raises(SystemExit, lambda: patched(lambda provider, prompt, procs, timeout=0: called.append(1) or good(name_of(prompt), provider), lambda: rd.run_stage(draw_dir, cache, out, ARGS())), 'not its sealed row')
        assert not called, 'no model call before the refusal'
    tamper(lambda ls: ls[1]['row'].update(record_id='r-other', record_label='r-other'))
    tamper(lambda ls: ls[0].update(plant='county'))
    tamper(lambda ls: ls[1]['row'].update(table='organizations'))


@case('A3: a failed call stops every later call at once, and a projected overrun halts before the call')
def _():
    import threading, time
    draw_dir, cache, out = run_fixture([('real', 'a-1', 'astra'), ('real', 'b-1', 'astra')])
    b_failed, calls = threading.Event(), []
    def fake(provider, prompt, procs, timeout=0):
        name = name_of(prompt)
        calls.append((name, provider))
        if name == 'b-1':
            b_failed.set()
            return dict(good('x', provider), error='no output', text='', usage=None, metered=False)
        b_failed.wait(5)
        time.sleep(0.5)
        return good(name, provider, street_bad=True)
    patched(fake, lambda: rd.run_stage(draw_dir, cache, out, ARGS(window=2, stop_at=99)))
    assert sorted(calls) == [('a-1', 'astra'), ('b-1', 'astra')], f'A started a second read after B failed: {calls}'
    draw_dir, cache, out = run_fixture([('real', 'big-p', 'astra')])
    calls.clear()
    patched(lambda provider, prompt, procs, timeout=0: calls.append(1) or good(name_of(prompt), provider), lambda: rd.run_stage(draw_dir, cache, out, ARGS(caps_m=dict(astra=0.0005))))
    doc = json.loads((out / 'results.json').read_text())
    assert not calls and doc['status'] == 'HALTED_TOKEN_BUDGET' and 'before the next call' not in ' '.join(doc['halt']) and 'stage budget' in ' '.join(doc['halt']), (calls, doc['halt'])
    import importlib.util
    spec = importlib.util.spec_from_file_location('sizes', HERE.parent / 'blind-audit-13-protocol-2026-11-24' / 'sizes.py')
    sizes = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sizes)
    assert [round(v, 3) for v in sizes.spend(sizes.SMOKE, 3)] == [rd.CAPS_M[p] for p in ('astra', 'hydrogen', 'sonnet')], 'stage caps are the sizes.py budgets, not twice them'


@case('A4: a record due a filing receipt that was not issued is refused; a packet with no receipt count is refused; matching counts run')
def _():
    r1 = dict(id='R1', status='MATCHES', text='ITA row binds; band equal', cls='band:osha_ita', field='employee_band_site')
    rc = lambda issued, due: dict(receipts={'sites|r-4': issued} if issued else {}, due={'sites|r-4': due} if due else {}, counts={'band:osha_ita': {'MATCHES': 1}}, not_inspected_classes={})
    fake = lambda provider, prompt, procs, timeout=0: good(name_of(prompt), provider)
    draw_dir, cache, out = run_fixture([('real', 'r-4', 'astra')], rc=rc([], 1), packet_due=1)
    expect_raises(SystemExit, lambda: patched(fake, lambda: rd.run_stage(draw_dir, cache, out, ARGS())), 'expects 1 filing receipts')
    draw_dir, cache, out = run_fixture([('real', 'r-4', 'astra')], rc=rc([r1], 1), packet_due=None)
    expect_raises(SystemExit, lambda: patched(fake, lambda: rd.run_stage(draw_dir, cache, out, ARGS())), 'expects None filing receipts')
    draw_dir, cache, out = run_fixture([('real', 'r-4', 'astra')], rc=rc([r1], 1), packet_due=1)
    patched(fake, lambda: rd.run_stage(draw_dir, cache, out, ARGS()))
    assert json.loads((out / 'results.json').read_text())['status'] == 'COMPLETE'


@case('A5: only the filed child is not inspected: an unrelated registry link or SIC code of the same table is still judged')
def _():
    import replays
    org = dict(org_id='ORG-1', legal_name='Acme', employee_band_ohio='', naics_primary='', naics_primary_source_type='')
    R = FakeR(sites=[], organizations=[org], ecosystem=[], registry_links=[dict(org_id='ORG-1', site_id='', registry='FRS', registry_id='1')],
              code_assignments=[dict(org_id='ORG-1', code_system='NAICS', code_value='326199', source_type='government_filing'), dict(org_id='ORG-1', code_system='SIC', code_value='3081', source_type='government_filing')], evidence=[])
    ni = replays.coverage(R, [('organizations', 'ORG-1')], Path('/nonexistent-store'))[3]['organizations|ORG-1']
    child = lambda table, **v: dict(table=table, values=v, context={})
    row = dict(table='organizations', values_json=json.dumps(dict(legal_name='Acme')), context_json=json.dumps(dict(children=[
        child('registry_links', registry='FRS', registry_id='1'), child('registry_links', registry='TRI', registry_id='9'),
        child('code_assignments', code_system='NAICS', code_value='326199', source_type='government_filing'), child('code_assignments', code_system='SIC', code_value='3081', source_type='government_filing')])))
    got = rd.not_inspected_targets(row, ni)
    assert got == ['c1.registry', 'c1.registry_id', 'c3.code_system', 'c3.code_value', 'c3.source_type'], got


@case('A8: the second reader may use the one REQUEST round when the primary did not')
def _():
    import site_corpus
    draw_dir, cache, out = run_fixture([('real', 'req-8', 'astra')])
    seen = []
    class FakeCorpus:
        def __init__(self, d): self.d = Path(d)
        def fetch(self, u):
            (self.d / 'req8.txt').write_text('Requested page text about Acme.')
            return dict(status='ok', http_status=200, final_url=u, fetched_at='t', sha256='0', text_file='req8.txt')
    def fake(provider, prompt, procs, timeout=0):
        seen.append((provider, prompt))
        first = finding('site_name', 'UNCONFIRMED', settling_fact='the plant page naming this site') if len(seen) == 1 else \
            finding('site_name', 'REQUEST', request_url='https://acme.example/about') if len(seen) == 2 else finding('site_name', 'VERIFIED')
        return dict(good('x', provider), text=json.dumps(dict(findings=[first, finding('street_address', 'VERIFIED'), finding('polymer_relevance', 'VERIFIED')])))
    real_corpus, site_corpus.Corpus = site_corpus.Corpus, FakeCorpus
    try:
        patched(fake, lambda: rd.run_stage(draw_dir, cache, out, ARGS()))
    finally:
        site_corpus.Corpus = real_corpus
    assert len(seen) == 3 and seen[1][0] == seen[2][0] == 'hydrogen' and 'https://acme.example/about' in seen[2][1] and 'https://acme.example/about' not in seen[1][1], [p for p, _ in seen]


@case('A9: a core-impacting child contradiction is counted under the child field it names and reaches k; its denominator is that field')
def _():
    child = dict(table='registry_links', values=dict(registry='FRS', registry_id='1'), context={})
    SRC['S7'] = 'Registry entry 1 belongs to Zeta Holdings.'
    final = {'c1.registry_id': dict(status='CONTRADICTED', core_effect='name', source_id='S7', source_value='Zeta Holdings', quote='belongs to Zeta Holdings', by='primary')}
    o = rd.record_outcome(final)
    assert o['k'] and o['contradicted_core'] == ['child:name'] and o.get('contradicted_core_fields') == ['registry_id'], o

    def fake(provider, prompt, procs, timeout=0):
        f = [finding('site_name', 'VERIFIED'), finding('street_address', 'VERIFIED'), finding('polymer_relevance', 'VERIFIED'), finding('c1.registry', 'VERIFIED'),
             dict(finding('c1.registry_id', 'CONTRADICTED', 'located at 99 Oak Avenue, Akron', '99 Oak Avenue'), core_effect='name')]
        return dict(good('x', provider), text=json.dumps(dict(findings=f)))
    sc = score(run_to_score([('real', 'child-9', 'astra')], fake, children=[child]))
    assert sc['k'] == 1 and sc['by_field']['registry_id'] == dict(audited_values=1, contradicted=1, error_rate=1.0, unconfirmed=0, unconfirmed_share=0.0, not_inspected=0), sc['by_field']


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
