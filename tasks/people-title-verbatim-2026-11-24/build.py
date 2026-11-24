"""Replay the reviewed decisions against the pinned pre-repair tree."""
import csv
import io
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = '65d0f53b'
PEOPLE = 'data/people.csv'
sys.path.insert(0, str(ROOT / 'scripts'))
from atlas import squash


def read_file(path):
    data = subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT)
    return list(csv.DictReader(io.StringIO(data.decode('utf-8-sig'), newline='')))


def host(url):
    return (urlsplit(url).hostname or '').removeprefix('www.')


def on_domain(source, domain):
    return domain and (host(source) == domain or host(source).endswith('.' + domain))


# Candidate detector reproduced from read-class-candidates-2026-11-24/find.py.
def rank(s):
    t = squash(s)
    if re.search(r'\b(emerit\w+|postdoctoral|postdoc)\b',t): return 'outside rank gate'
    for pat,role in [
        (r'deputy group leader','deputy'), (r'research (assistant |associate )?professor','research_professor'),
        (r'(assistant|asst) professor','assistant_professor'), (r'(associate|assoc) professor','associate_professor'),
        (r'senior lecturer','senior_lecturer'), (r'senior research engineer','senior_research_engineer'),
        (r'(group leader|section head)','group_leader'),(r'(governor s chair|endowed laboratory chair)','named_chair'),
        (r'(research staff|researcher)','research_scientist')]:
        if re.search(r'\b(?:'+pat+r')\b',t): return role
    for role in ['distinguished_scientist','senior_scientist','staff_scientist','research_scientist','research_engineer','associate_scientist','assistant_scientist','division_director','professor']:
        if re.search(r'\b'+role.replace('_',' ')+r'\b',t): return role
    return ''

def title(role,published,quotes):
    """Readable own-institution title quote disagrees in rank or verbatim wording."""
    if not role or not published: return N,'missing recorded role or published title'
    clean = False
    for q in quotes:
        mapped = rank(q)
        if not mapped: continue
        director = role=='center_director_professor' and 'director' in squash(q) and 'professor' in squash(q)
        if mapped=='deputy' and role!='group_leader': continue
        if mapped != role and not director: return F,'institutional title quote maps to a different rank'
        if not (' '+squash(published)+' ') in (' '+squash(q)+' '): return F,'recorded published title absent from institutional title excerpt'
        clean = True
    return (C,'rank and title agree in held excerpt') if clean else (N,'missing or unmapped institutional title excerpt')


F, C, N = 'FLAGGED', 'CLEAN', 'NOT_INSPECTED'


def frame():
    people = read_file(PEOPLE)
    org = {r['org_id']: r for r in read_file('data/ecosystem.csv')}
    missing = {p['institution_org_id'] for p in people} - org.keys()
    if missing:
        for f in sorted((ROOT/'data').glob('organizations_[A-Z]*.csv')):
            org.update((r['org_id'], r) for r in read_file('data/' + f.name) if r['org_id'] in missing)
    quotes = defaultdict(list)
    for e in read_file('data/evidence_people.csv'):
        if (e['record_table'], e['claim_type'], e['source_class']) != ('people','existence','own_site'):
            continue
        m = re.search(r'raw words in order(?:\s*\([^)]*\))?:\s*([^\n]+)', e['notes'], re.I)
        if m:
            q = re.split(r'\s+Packet note:', m[1], flags=re.I)[0].strip()
            quotes[e['record_id']].append((e['evidence_id'], q, e['source_ref']))
    flagged = {}
    for p in people:
        i = p['person_id']
        domain = host(org.get(p['institution_org_id'], {}).get('website',''))
        candidates = [e for e in quotes[i] if any(on_domain(e[2], d) for d in (domain, host(p['public_profile_url'])))]
        status, reason = title(p['role'], p['role_as_published'], [e[1] for e in candidates])
        if status == F:
            flagged[i] = (p, domain, candidates, reason)
    return people, flagged


def decisions():
    with (HERE/'decisions.csv').open(newline='') as f:
        return list(csv.DictReader(f))


if __name__ == '__main__':
    people, flagged = frame()
    changes = {d['person_id']: d for d in decisions() if d['decision'] == 'CHANGE'}
    output = io.StringIO(newline='')
    writer = csv.DictWriter(output, fieldnames=people[0], lineterminator='\n')
    writer.writeheader()
    for p in people:
        if d := changes.get(p['person_id']):
            p.update(role=d['role'], role_as_published=d['role_as_published'])
        writer.writerow(p)
    result = output.getvalue().encode()
    target = ROOT / PEOPLE
    if target.read_bytes() != result:
        base = subprocess.check_output(['git','show',f'{BASE}:{PEOPLE}'], cwd=ROOT)
        if target.read_bytes() != base:
            sys.exit('People table differs from base. Reconcile before applying.')
        target.write_bytes(result)


def institution_domains():
    """Institutional roots independently attested by an organization or its program."""
    roots = defaultdict(set)
    for o in read_file('data/ecosystem.csv'):
        if o['website']:
            roots[o['org_id']].add(host(o['website']))
        for u in [o['website'], *re.findall(r'https?://[^\s;]+', o['sources'])]:
            h = host(u)
            if h.endswith('.edu'):
                roots[o['org_id']].add('.'.join(h.split('.')[-2:]))
    for r in read_file('data/programs.csv'):
        h = host(r['url'])
        if h.endswith('.edu'):
            roots[r['institution_org_id']].add('.'.join(h.split('.')[-2:]))
    return roots
