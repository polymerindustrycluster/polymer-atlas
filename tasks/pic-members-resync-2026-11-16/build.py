"""Replay the public roster snapshot; includes the authorized Custom Rubber membership flag."""
import csv
import html
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from shard_io import append_sorted
DATE = '2026-11-16'
URL = 'https://polymerindustrycluster.org/'
TEAM = 'TeamNEO Proud to be part of the Northeast Ohio Region - JobsOhio Network Partner'

def read(path):
    with open(path, newline='') as f:
        return list(csv.DictReader(f))

def roster():
    raw = (HERE / 'public-list.html').read_text()
    # The two membership sections terminate before the page footer.
    start = raw.index('Investing Partners')
    corner = raw.index('Cornerstone Partners', start)
    entries = []
    for m in re.finditer(r'<p class="logo-title">(.*?)</p>', raw, re.S):
        assert m.start() > start
        entries.append((html.unescape(m[1]).strip(), 'Investing Partners' if m.start() < corner else 'Cornerstone Partners'))
    assert len(entries) == len(set(n for n, _ in entries))
    return entries

def expected():
    old = read(HERE / 'members.before.csv')
    by_name = {r['display_name']: r for r in old}
    out = []
    for name, tier in roster():
        key = 'TeamNEO' if name == TEAM else name
        if key in by_name:
            row = dict(by_name[key])
            row.update(display_name=name, member_tier=tier, snapshot_date=DATE)
        else:
            assert name == 'Custom Rubber Corp', name
            row = dict(member_row_id='MBR-000061', display_name=name, member_tier=tier,
                       record_class='organization', org_id='ORG-000113', member_since='',
                       membership_source_url=URL, snapshot_date=DATE,
                       notes='Public roster links customrubbercorp.com; exact domain match to held Custom Rubber Corporation ORG-000113. Dedupe stop at step 1.')
        out.append(row)
    assert {r['member_row_id'] for r in old} <= {r['member_row_id'] for r in out}, 'hold missing listings; schema has no lapse field'
    return sorted(out, key=lambda r:r['member_row_id'])

def main():
    path = ROOT / 'data/members.csv'
    target = expected()
    current = read(path)
    assert {r['member_row_id'] for r in current} <= {r['member_row_id'] for r in target}, 'unexpected member IDs'
    org_path = ROOT / 'data/organizations_OH.csv'
    orgs = read(org_path)
    for row in orgs:
        if row['org_id'] == 'ORG-000113':
            row['pic_member'] = 'true'
            row['membership_source_url'] = 'https://polymerindustrycluster.org/'
    with org_path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=orgs[0], lineterminator='\n')
        w.writeheader()
        w.writerows(orgs)
    if current == target:
        return
    old_ids = {r['member_row_id'] for r in current}
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=current[0], lineterminator='\n')
        w.writeheader()
        w.writerows(r for r in target if r['member_row_id'] in old_ids)
    append_sorted(path, [r for r in target if r['member_row_id'] not in old_ids], 'member_row_id')

if __name__ == '__main__':
    main()
