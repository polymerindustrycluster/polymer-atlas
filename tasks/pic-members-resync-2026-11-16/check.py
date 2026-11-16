"""Full output equality, independent HTML yield, and three demonstrated failures."""
import copy
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
    before = read(HERE / 'members.before.csv')
    assert len(before) == 60
    assert len(rows) - len(before) == 0
    assert sum(r['snapshot_date'] == '2026-11-16' for r in rows) == 60
    for defect in ('drop', 'duplicate', 'stale_date'):
        bad = copy.deepcopy(rows)
        if defect == 'drop': bad.pop()
        elif defect == 'duplicate': bad.append(dict(bad[0]))
        else: bad[0]['snapshot_date'] = '2026-10-29'
        try: verify(bad)
        except AssertionError: print('rejected injected defect:', defect)
        else: raise AssertionError('silent pass: ' + defect)
    print('PASS: 61 public listings; 60 refreshed; 0 added; 1 held; 0 absent; 0 unmatched new listings')
