"""Named SEC identity census, immutable-row and replay checks (no network)."""
import collections
import csv
import hashlib
import io
import json
import subprocess
import tempfile
from pathlib import Path
from build import HERE, ROOT, apply, packet, read


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args], text=True)


def main():
    baseline = json.loads((HERE / 'baseline.json').read_text())
    base = baseline['main']
    paths = git('ls-tree', '-r', '--name-only', base, 'data').splitlines()
    original_orgs = [r for p in paths if p.startswith('data/organizations_') and p.endswith('.csv')
                     for r in csv.DictReader(io.StringIO(git('show', f'{base}:{p}')))]
    original_links = list(csv.DictReader(io.StringIO(git('show', f'{base}:data/registry_links.csv'))))
    old_own = {r['org_id'] for r in original_links if r['registry'] == 'SEC_CIK'}
    eligible = {r['org_id'] for r in original_orgs if (r['stock_ticker'] or 'public_parent' in r['tier1_qualifier']
                or 'public_parent:' in r['tier1_qualifier_basis']) and r['org_id'] not in old_own}
    frame = json.loads((HERE / 'frame.json').read_text())
    assert eligible == {r['org_id'] for r in frame} and len(eligible) == 103, 'independent baseline coverage'
    links, verdicts = packet(ROOT / 'data')
    assert read(HERE / 'new_links.csv') == links and read(HERE / 'verdicts.csv') == verdicts, 'packet drift'
    assert collections.Counter(r['verdict'] for r in verdicts) == {'VERIFIED': 64, 'STILL_UNCERTAIN': 39}
    assert all(r['settling_fact'] for r in verdicts if r['verdict'] == 'STILL_UNCERTAIN')
    by_org = {r['org_id']: r for r in verdicts}
    for row in links:
        assert len(row['registry_id']) == 10 and row['registry_id'].isdigit()
        assert by_org[row['org_id']]['source_url'] in row['match_basis']
    for cik, name, ticker in [('0000320193', 'Apple Inc.', 'AAPL'),
                             ('0000051143', 'INTERNATIONAL BUSINESS MACHINES CORP', 'IBM'),
                             ('0000089800', 'SHERWIN WILLIAMS CO', 'SHW'), ('0001122976', 'AVIENT CORP', 'AVNT')]:
        source = json.loads((HERE / 'sources' / f'CIK{cik}.json').read_text())
        assert source['http_status'] == 200 and str(source['cik']).zfill(10) == cik
        assert source['name'] == name and ticker in source['tickers'], 'known answer failed'
    live = read(ROOT / 'data/registry_links.csv')
    key = lambda r: tuple(r.values())
    assert not (collections.Counter(map(key, original_links)) - collections.Counter(map(key, live))), 'old registry row changed/lost'
    ours = {r['org_id'] for r in links}
    assert [r for r in live if r['org_id'] in ours and r['registry'] == 'SEC_CIK'] == links, 'applied link census'
    with tempfile.TemporaryDirectory() as tmp:
        data = Path(tmp)
        p = data / 'registry_links.csv'
        p.write_bytes((ROOT / 'data/registry_links.csv').read_bytes())
        before = hashlib.sha256(p.read_bytes()).hexdigest()
        assert apply(data, links) == 0 and hashlib.sha256(p.read_bytes()).hexdigest() == before, 'non-idempotent builder'
    # Check all three Git states, including a committed forbidden edit masked by a working-tree restoration.
    merge_base = git('merge-base', 'HEAD', 'origin/main').strip()
    for args in ([merge_base, 'HEAD'], ['--cached', 'HEAD'], []):
        changed = git('diff', '--name-only', *args, '--', 'data/').splitlines()
        assert all(p == 'data/registry_links.csv' for p in changed), ('forbidden canonical delta', args, changed)
    assert not git('ls-files', '--others', '--exclude-standard', 'data/').strip(), 'untracked canonical file'
    print('PASS sec-identity-census: 103 unique organizations; 64 own CIK links; 39 explicit holds; four known answers; old rows preserved; replay byte-identical; registry-only data boundary')


if __name__ == '__main__':
    main()
