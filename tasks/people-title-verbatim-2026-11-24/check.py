"""Replay every decision and compare the full people table cell by cell."""
import csv
import re
import tempfile
from pathlib import Path
from collections import Counter
from build import HERE, ROOT, PEOPLE, frame, decisions, institution_domains, on_domain, read_file


def quoted(title, excerpt):
    assert title and title in excerpt, 'title is not a verbatim substring of the bound quote'


def mapped(title, lab):
    t = title.lower()
    if lab:
        if any(word in t for word in ('deputy', 'corporate fellow', 'senior r&d staff')):
            raise ValueError('No single explicit lab rank')
        for phrase, role in [('assistant scientist', 'assistant_scientist'), ('section head', 'group_leader'),
                             ('group leader', 'group_leader'), ('researcher', 'research_scientist')]:
            if phrase in t:
                return role
        for role in ('staff_scientist','research_engineer','senior_scientist','research_scientist'):
            if role.replace('_',' ') in t:
                return role
    elif 'professor' in t:
        if 'director' in t and any(word in t for word in ('center', 'institute')):
            return 'center_director_professor'
        if re.search(r'research (assistant |associate )?professor', t):
            return 'research_professor'
        if re.search(r'(associate|assoc\.?) professor', t):
            return 'associate_professor'
        if 'assistant professor' in t:
            return 'assistant_professor'
        return 'professor'
    raise ValueError(f'No explicit mapping for {title!r}')


def rank_in_context(title, excerpt, lab):
    """Require the quoted title to contain the entire rank at the matched position."""
    quoted(title, excerpt)
    rank_words = re.compile(
        r"\b(?:(?:assistant|associate|assoc\.?|asst\.?|research|full|distinguished|clinical|adjunct|"
        r"senior|deputy|supervisory|staff)\s+)*(?:professor|scientist|research engineer|group leader|section head)\b",
        re.I)
    ranks = list(rank_words.finditer(excerpt))
    for m in re.finditer(re.escape(title), excerpt):
        overlaps = [r for r in ranks if r.start() < m.end() and m.start() < r.end()]
        if overlaps and all(m.start() <= r.start() and r.end() <= m.end() for r in overlaps):
            return mapped(title, lab)
    raise ValueError('Proposed phrase drops or lacks an institutional rank')


def check_claims(path, expected):
    with path.open(newline='') as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == ['table','record_id','field','verdict','evidence_id']
        claims = list(reader)
    assert sorted(tuple(c.values()) for c in claims) == sorted(expected), 'claim list mismatch'
    return claims


def main():
    before, flagged = frame()
    assert len(flagged) == 293
    domains = institution_domains()
    labs = {r['org_id'] for r in read_file('data/ecosystem.csv') if r['ecosystem_subtype']=='government_lab_agency'}
    packet = decisions()
    by_id = {d['person_id']: d for d in packet}
    assert len(by_id) == len(packet) and by_id.keys() == flagged.keys()
    with (ROOT/PEOPLE).open(newline='') as f:
        after = list(csv.DictReader(f))
    assert len(after) == len(before)
    actual, expected_claims = set(), set()
    for old, new in zip(before, after, strict=True):
        i = old['person_id']
        assert old.keys() == new.keys() and new['person_id'] == i
        changed = {key for key in old if new[key] != old[key]}
        actual.update((i, k) for k in changed)
        assert changed <= {'role_as_published', 'role'}
        if i not in by_id:
            assert not changed
            continue
        d = by_id[i]
        assert bool(changed) == (d['decision'] == 'CHANGE')
        match, = [e for e in flagged[i][2] if e[0] == d['evidence_id']]
        if d['decision'] != 'HOLD':
            assert d['decision'] in ('CHANGE','KEEP')
            q = re.split(r'; (?:replaces an identifier|page sha256|stored page)',match[1])[0]
            quoted(new['role_as_published'], q)
            assert any(on_domain(match[2], root) for root in domains[old['institution_org_id']])
            assert new['role_as_published'] == d['role_as_published']
            assert new['role'] == d['role'] == rank_in_context(new['role_as_published'], q, old['institution_org_id'] in labs), i
        else:
            assert d['reason'] and not changed
        for k in ('role_as_published','role'):
            verdict = 'corrected' if k in changed else 'held' if d['decision']=='HOLD' else 'verified'
            expected_claims.add(('people',i,k,verdict,d['evidence_id']))
    path = HERE/'CLAIMS_CHECKED.csv'
    claims = check_claims(path, expected_claims)
    with tempfile.TemporaryDirectory() as folder:
        planted = Path(folder)/path.name
        planted.write_bytes(path.read_bytes() + path.read_bytes().splitlines(keepends=True)[1])
        try:
            check_claims(planted, expected_claims)
        except AssertionError as exc:
            print('Duplicate claim on disk rejected:', exc)
        else:
            raise AssertionError('Duplicate claim passed')
    assert actual == {(c['record_id'], c['field']) for c in claims if c['verdict']=='corrected'}
    i = 'PERSON-000732'
    excerpt = next(e[1] for e in flagged[i][2] if e[0]==by_id[i]['evidence_id'])
    assert rank_in_context('Associate Professor', excerpt, False)=='associate_professor'
    try:
        rank_in_context('Professor', excerpt, False)
    except ValueError as exc:
        print('Dropped Associate rejected:', exc)
    else:
        raise AssertionError('Shortened rank passed')
    plant = next(d for d in packet if d['decision']=='CHANGE')
    quote = next(e[1] for e in flagged[plant['person_id']][2] if e[0]==plant['evidence_id'])
    try:
        quoted(plant['role_as_published'] + ' (faculty appointment)', quote)
    except AssertionError as exc:
        print('Paraphrase plant rejected:', exc)
    else:
        raise AssertionError('Paraphrase plant passed')
    print(len(flagged),'flagged people;',Counter(d['decision'] for d in packet),len(actual),'changed cells')


if __name__ == '__main__':
    main()
