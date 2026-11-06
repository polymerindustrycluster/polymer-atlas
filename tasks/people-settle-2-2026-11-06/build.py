"""Append the frozen second-pass people packet; replay never changes a held row."""
import csv, json, re, sys, unicodedata
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from shard_io import append_sorted

DATE = '2026-11-06'
DOMAIN_OVERRIDES = {'ORG-001314': {'uc.edu'}, 'ORG-001284': {'osu.edu', 'ohio-state.edu'}}

def read(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def norm(name):
    s = ''.join(c for c in unicodedata.normalize('NFKD', name).casefold() if not unicodedata.combining(c))
    return ' '.join(re.findall(r'[^\W_]+', s))

def identity(name):
    tokens = norm(name).split()
    assert tokens, 'empty normalized person name'
    return tokens[0], tokens[-1]

def require_specialties(row):
    vocab = json.loads((ROOT / 'docs/schema/vocab.json').read_text())['vocabularies']
    allowed = set().union(*(set(vocab[k]['values']) for k in ('PROCESSES', 'MATERIALS', 'RESEARCH_SUPPLEMENT')))
    assert row['research_specialties'] and set(row['research_specialties'].split(';')) <= allowed, (row['full_name'], 'unsupported specialty; owner hold')

def on_domain(url, domains):
    host = urlparse(url).hostname or ''
    return any(host == d or host.endswith('.' + d) for d in domains)

def records():
    data = ROOT / 'data'
    institutions = {r['org_id']: r for f in [data / 'ecosystem.csv', *sorted(data.glob('organizations_*.csv'))] for r in read(f)}
    people = read(data / 'people.csv')
    columns = list(people[0])
    packet = read(HERE / 'reviewed.csv')
    extra = read(HERE / 'evidence_append.csv')
    assert len({r['candidate_id'] for r in packet}) == len(packet)
    raw = {(r['url'], r['quote']): r for r in read(HERE / 'rawcheck.csv')}
    additions, evidence = [], []
    for r in packet:
        require_specialties(r)
        pid = r['allocated_person_id']
        assert 2100 <= int(pid[7:]) <= 2499
        home = institutions[r['institution_org_id']]
        web = urlparse(home.get('website', '')).hostname or ''
        domains = DOMAIN_OVERRIDES.get(r['institution_org_id'], {'.'.join(web.split('.')[-2:])} if web else set())
        assert domains, ('missing institution domain', pid)
        for gate in ('a', 'b', 'parent'):
            u, q = r[f'gate_{gate}_url'], r[f'gate_{gate}_quote']
            assert u.startswith('https://') and '@' not in u and on_domain(u, domains), (pid, gate, u)
            assert q and len(q.split()) <= 25, (pid, gate, 'quote ceiling')
            ck = raw[(u, q)]
            assert ck['record_name'] == r['full_name'], (pid, 'source entry belongs to another person')
            assert ck['found'] == ck['entry_checked'] == 'yes'
            assert re.fullmatch('[0-9a-f]{64}', ck['sanitized_text_sha256'])
            if gate == 'a':
                assert ck['surname_near'] == 'yes'
            if gate == 'b':
                assert ck['current_person_scope'] == 'yes'
            eid = r[f'evidence_{gate}_id']
            assert 282000 <= int(eid[4:]) <= 284999
            claim = {'a': 'existence', 'b': 'scope', 'parent': 'parent'}[gate]
            detail = {'a': f"name {r['full_name']}; role {r['role']}; title {r['role_as_published']}",
                      'b': f"Current own-institution polymer research; research_specialties {r['research_specialties']}",
                      'parent': f"institution_org_id {r['institution_org_id']}; public_profile_url {r['public_profile_url']}"}[gate]
            evidence.append(dict(evidence_id=eid, record_table='people', record_id=pid, claim_type=claim,
                claim_detail=detail, source_class='own_site', source_ref=u, observed_date=DATE,
                tier_effect='supports_A', created_by='codex atlas-L12-people-settle-2', notes='Raw words in order: ' + q))
        names = [r['full_name']] + [n for n in r['dedupe_aliases'].split(';') if n]
        dup = [x['person_id'] for x in people + additions if x['person_id'] != pid and
               any(norm(x['full_name']) == norm(n) or identity(x['full_name']) == identity(n) for n in names)]
        assert not dup, (pid, 'HOLD identity duplicate for owner', dup)
        record = {k: r.get(k, '') for k in columns}
        record.update(person_id=pid, verification_tier='C', last_verified=DATE,
            sources=';'.join(dict.fromkeys([r['public_profile_url']] + [r[f'gate_{g}_url'] for g in ('a', 'b', 'parent')] +
                [e['source_ref'] for e in extra if e['record_id'] == pid])))
        additions.append(record)
    for e in extra:
        target = next(r for r in packet if r['allocated_person_id'] == e['record_id'])
        web = urlparse(institutions[target['institution_org_id']].get('website', '')).hostname or ''
        domains = DOMAIN_OVERRIDES.get(target['institution_org_id'], {'.'.join(web.split('.')[-2:])} if web else set())
        q = e['notes'].removeprefix('Raw words in order: ')
        assert on_domain(e['source_ref'], domains) and len(q.split()) <= 25
        assert raw[(e['source_ref'], q)]['found'] == 'yes'
        assert e['record_table'] == 'people' and e['source_class'] == 'own_site' and e['observed_date'] == DATE
        assert 282000 <= int(e['evidence_id'][4:]) <= 284999
    evidence += extra
    assert len({r['person_id'] for r in additions}) == len(additions)
    assert len({r['evidence_id'] for r in evidence}) == len(evidence)
    return additions, evidence

def main():
    new_people, new_evidence = records()
    targets = [(ROOT / 'data/people.csv', new_people, 'person_id'),
               (ROOT / 'data/evidence_people.csv', new_evidence, 'evidence_id')]
    prepared = []
    for path, rows, key in targets:
        existing = {r[key]: r for r in read(path)}
        for r in rows:
            if r[key] in existing:
                assert existing[r[key]] == r, (r[key], 'collision or replay differs')
        prepared.append((path, [r for r in rows if r[key] not in existing], key))
    all_evidence = {r['evidence_id']: f.name for f in (ROOT / 'data').glob('evidence_*.csv') for r in read(f)}
    for r in new_evidence:
        assert all_evidence.get(r['evidence_id'], 'evidence_people.csv') == 'evidence_people.csv', 'cross-shard evidence collision'
    for path, rows, key in prepared:
        if rows:
            append_sorted(path, rows, key)
    print(f'{len(new_people)} packet people; {len(prepared[0][1])} created this replay; {len(new_evidence)} evidence observations')

if __name__ == '__main__':
    main()
