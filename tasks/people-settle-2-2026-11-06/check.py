"""Check the entire candidate frame, prospective evidence, conservation and replay."""
import csv, hashlib, io, json, re, subprocess, sys
from pathlib import Path
import build
from build import HERE, ROOT, read, norm, identity, require_specialties
from fetch import get, found, words

PRIVATE = Path('/Users/johnswanson/.bb/thread-storage/thr_mcdghpxw8c/people-settle-2-private')
VERDICTS = {'VERIFIED', 'REJECT', 'STILL_UNCERTAIN', 'DUPLICATE_OF'}

def require_claims(evidence, pid):
    assert {'existence', 'scope', 'parent'} <= {e['claim_type'] for e in evidence if e['record_id'] == pid}, (pid, 'missing required claim')

def main():
    packet = read(HERE / 'reviewed.csv')
    assert len(packet) == 12 and len({r['candidate_id'] for r in packet}) == 12
    frame = json.loads((PRIVATE / 'frame.json').read_text())
    assert len(frame) == len({r['id'] for r in frame}) == 342
    expected = {r['id'] for r in frame}
    dispositions = []
    parts = [('helper', 'helper171.json', 171), ('uc58', 'uc58.json', 58), ('osu60', 'osu60.json', 60),
             ('root15', 'root15_followup.json', 15), ('root8', 'root8_followup.json', 8), ('root30', 'root30.json', 30)]
    for lane, source, count in parts:
        rows = json.loads((PRIVATE / lane / 'dispositions.json').read_text())
        ids = [int(r.get('candidate_id', r.get('id'))) for r in rows]
        want = [int(r['id']) for r in json.loads((PRIVATE / source).read_text())]
        assert len(rows) == count and set(ids) == set(want) and len(set(ids)) == count, (lane, 'input/output yield')
        assert all(r['verdict'] in VERDICTS for r in rows)
        for r in rows:
            assert any(r.get(k) for k in ('fact', 'verdict_note', 'settling_fact', 'deciding_fact')), (lane, 'missing deciding/settling fact')
            r = dict(r, candidate_id=int(r.get('candidate_id', r.get('id'))), source_list=lane)
            dispositions.append(r)
    ids = [r['candidate_id'] for r in dispositions]
    assert len(ids) == len(set(ids)) == 342 and set(ids) == expected, 'overlap, omission or extra candidate'
    counts = {v: sum(r['verdict'] == v for r in dispositions) for v in VERDICTS}
    assert counts == {'VERIFIED': 12, 'REJECT': 25, 'STILL_UNCERTAIN': 302, 'DUPLICATE_OF': 3}, counts
    assert {r['candidate_id'] for r in dispositions if r['verdict'] == 'VERIFIED'} == {int(r['candidate_id']) for r in packet}
    held = read(ROOT / 'data/people.csv')
    held_by_id = {r['person_id']: r for r in held}
    pending = read(PRIVATE / 'pending_first_pass_people.csv')
    assert len(pending) == 12
    for r in dispositions:
        if r['verdict'] == 'DUPLICATE_OF':
            assert r['duplicate_of'] in held_by_id, ('duplicate endpoint not held', r['candidate_id'])
    for r in packet:
        require_specialties(r)
        d = get(r['gate_a_url'])
        t, q = words(d['text']), words(r['gate_a_quote'])
        surname = words(r['full_name'])[-1]
        assert any(t[i:i+len(q)] == q and surname in t[max(0, i-40):i+len(q)+40] for i in range(len(t)-len(q)+1)), (r['full_name'], 'rank/surname distance')
        assert found(d['text'], r['role_as_published']), (r['full_name'], 'published title')
        names = [r['full_name']] + [s for s in r['dedupe_aliases'].split(';') if s]
        for h in held + pending:
            if h['person_id'] != r['allocated_person_id']:
                assert not any(norm(h['full_name']) == norm(n) or identity(h['full_name']) == identity(n) for n in names), ('identity HOLD', r['full_name'], h['person_id'])
    calibration = json.loads((PRIVATE / 'calibration.json').read_text())
    assert calibration['recorded_before_new_builder'] and len(calibration['actual_primary_cases']) == 4
    for c in calibration['actual_primary_cases']:
        assert found(get(c['url'])['text'], c['quote']), c['label']
    for text, quote in [('depolymerization', 'polymer'), ('polymeric', 'polymer'), ('Professorship', 'Professor'),
                        ('Professor Kumar studies polymers. Wang studies metals.', 'Wang studies polymers')]:
        assert not found(text, quote), 'boundary/wrong-person matcher defect'
    assert not found(get(calibration['actual_primary_cases'][0]['url'])['text'], 'Yoonjee Park Associate Professor')
    bad = dict(packet[0], research_specialties='Polymeric sorbents')
    try:
        require_specialties(bad)
    except AssertionError:
        pass
    else:
        raise AssertionError('unsupported specialty mutation was accepted')
    for ck in read(HERE / 'rawcheck.csv'):
        d = get(ck['url'])
        assert d['status'].startswith('ok') and not d['text'].lstrip().startswith('%PDF'), ('uninspectable raw source', ck['url'])
        assert hashlib.sha256(d['text'].encode()).hexdigest() == ck['sanitized_text_sha256'], ('source changed; recheck required', ck['url'])
        assert found(d['text'], ck['quote']) and len(ck['quote'].split()) <= 25
    people, evidence = build.records()
    assert len(people) == 12 and len(evidence) == 37
    for r in people:
        assert r['verification_tier'] == 'C'
        require_claims(evidence, r['person_id'])
    damaged = [e for e in evidence if not (e['record_id'] == people[0]['person_id'] and e['claim_type'] == 'parent')]
    try:
        require_claims(damaged, people[0]['person_id'])
    except AssertionError:
        pass
    else:
        raise AssertionError('missing-parent mutation was accepted')
    base = (HERE / 'base_commit.txt').read_text().strip()
    for name, rows, key in [('people.csv', people, 'person_id'), ('evidence_people.csv', evidence, 'evidence_id')]:
        old = list(csv.DictReader(io.StringIO(subprocess.check_output(['git', 'show', f'{base}:data/{name}'], cwd=ROOT, text=True))))
        now = read(ROOT / 'data' / name)
        by = {r[key]: r for r in now}
        assert len(by) == len(now)
        assert all(by.get(r[key]) == r for r in old), (name, 'pre-pass row removed or edited')
        assert len(now) == len(old) + len(rows), (name, 'unexpected row delta')
        assert all(by.get(r[key]) == r for r in rows), (name, 'packet differs')
    for r in read(HERE / 'withdrawn_proposals.csv'):
        assert r['person_id'] not in held_by_id, 'retired proposal resurrected'
        all_eids = {x['evidence_id'] for f in (ROOT / 'data').glob('evidence_*.csv') for x in read(f)}
        assert not set(r['evidence_ids'].split(';')) & all_eids
    for f in HERE.rglob('*.csv'):
        text = f.read_text()
        assert b'\r' not in f.read_bytes() and not re.search(r'[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}|mailto:|tel:', text), f
    paths = [ROOT / 'data/people.csv', ROOT / 'data/evidence_people.csv']
    hashes = [hashlib.sha256(f.read_bytes()).hexdigest() for f in paths]
    subprocess.run([sys.executable, str(HERE / 'build.py')], cwd=ROOT, check=True)
    assert hashes == [hashlib.sha256(f.read_bytes()).hexdigest() for f in paths], 'replay changed bytes'
    print('PASS342unique candidate people=12V/25R/302U/3D;12newC/37append-onlyEVD;41rawquote keys;vocabulary+missing-parent defects rejected;pre-pass preservation;byte-identical replay')

if __name__ == '__main__':
    main()
