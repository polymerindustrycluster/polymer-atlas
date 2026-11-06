import csv, hashlib, io, json, re, sys, time
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET
sys.path.insert(0, str(Path.cwd() / 'scripts'))
import build_changelog as m
base = m.git(m.ROOT, 'rev-parse', 'origin/main').strip()
start = time.monotonic()
entries = m.build(m.ROOT, base)
elapsed = round(time.monotonic() - start, 2)
prs = {e['pr']: e for e in entries if e['pr']}
assert len([r for r in prs['140']['created'] if r['table'] == 'equipment']) == 34
assert len([r for r in prs['143']['created'] if r['table'] == 'sites']) == 18
assert [(r['id'], old, new) for r, old, new in prs['133']['tier']] == [('ORG-000132', 'C', 'A')]
evidence = {}
for path in m.git(m.ROOT, 'ls-tree', '-r', '--name-only', base, 'data/').splitlines():
    if not re.fullmatch(r'data/evidence(?:_.*)?\.csv', path):
        continue
    for row in csv.DictReader(io.StringIO(m.git(m.ROOT, 'show', base + ':' + path))):
        assert row['evidence_id'] not in evidence
        evidence[row['evidence_id']] = row['record_table']
balance = sum(sum(e['evidence'].values()) + sum(r['table'] == 'evidence' for r in e['restored'])
              - sum(r['table'] == 'evidence' for r in e['removed']) for e in entries)
assert balance == len(evidence), (balance, len(evidence))
out = m.ROOT / 'build/changelog'
digest = lambda: {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir()}
hashes = digest()
root = ET.parse(out / 'feed.xml').getroot()
atom = {'a': m.ATOM}
nodes = root.findall('a:entry', atom)
assert len(nodes) == len(entries)
assert len({n.find('a:id', atom).text for n in nodes}) == len(entries)
for parent in [root, *nodes]:
    for tag in ['id', 'title', 'updated']:
        assert parent.find('a:' + tag, atom) is not None
    if parent is not root:
        assert parent.find('a:content', atom).attrib['type'] == 'text'
public = (out / 'CHANGELOG.md').read_text() + (out / 'feed.xml').read_text()
assert not re.search(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', public)
assert not re.search(r'(?<!\d)\d{3}[-. ]\d{3}[-. ]\d{4}(?!\d)', public)
assert 'CRM' not in public and 'mailto:' not in public
print('Actual main generation, 3 known answers, evidence balance, Atom structure and contact exclusion PASS', flush=True)
m.build(m.ROOT, base)
assert digest() == hashes
report = {'main_snapshot': base, 'data_history_entries': len(entries),
          'merged_pr_entries': sum(e['pr'] is not None for e in entries),
          'direct_commit_entries': sum(e['pr'] is None for e in entries),
          'first_generation_seconds': elapsed, 'known_answers': '3/3',
          'evidence_row_balance': balance, 'evidence_rows_at_main': len(evidence),
          'deterministic_replay': True, 'atom_entries': len(nodes),
          'output_sha256': hashes, 'output_files_committed': False,
          'check': 'PASS'}
Path('tasks/change-feed-2026-11-06/real-check.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2), flush=True)
