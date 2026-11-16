"""Full output equality, independent HTML yield, and three demonstrated failures."""
import copy
import csv
import io
import subprocess
from html.parser import HTMLParser
from build import HERE, ROOT, read, roster, expected

class Count(HTMLParser):
    def __init__(self):
        super().__init__()
        self.n = 0
    def handle_starttag(self, tag, attrs):
        if tag == 'p' and dict(attrs).get('class') == 'logo-title':
            self.n += 1

def verify(rows):
    assert len({r['member_row_id'] for r in rows}) == len(rows), 'duplicate member ID'
    assert rows == expected(), 'output differs from complete public roster replay'

if __name__ == '__main__':
    p = Count()
    p.feed((HERE / 'public-list.html').read_text())
    assert p.n == len(roster()) == 61
    rows = read(ROOT / 'data/members.csv')
    verify(rows)
    orgs = read(ROOT / 'data/organizations_OH.csv')
    base = list(csv.DictReader(io.StringIO(subprocess.check_output(['git', 'show', 'cb6d3d4:data/organizations_OH.csv'], cwd=ROOT, text=True))))
    for row in base:
        if row['org_id'] == 'ORG-000113':
            row['pic_member'] = 'true'
            row['membership_source_url'] = 'https://polymerindustrycluster.org/'
    assert orgs == base, 'organization changes exceed authorized cells'
    before = read(HERE / 'members.before.csv')
    assert len(before) == 60
    assert len(rows) - len(before) == 1
    assert sum(r['snapshot_date'] == '2026-11-16' for r in rows) == 61
    for defect in ('drop', 'duplicate', 'stale_date'):
        bad = copy.deepcopy(rows)
        if defect == 'drop': bad.pop()
        elif defect == 'duplicate': bad.append(dict(bad[0]))
        else: bad[0]['snapshot_date'] = '2026-10-29'
        try: verify(bad)
        except AssertionError: print('rejected injected defect:', defect)
        else: raise AssertionError('silent pass: ' + defect)
    print('PASS: 61 public listings; 60 refreshed; 1 added; 0 held; 0 absent; 0 unmatched new listings')
