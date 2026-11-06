"""Exact registry-key joins; federal years are signals only, never closure evidence."""
import csv
import json
from pathlib import Path
import urllib.request

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
API = 'https://data.epa.gov/dmapservice/query'

def read(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def write(path, rows, fields):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)

def query_years(ids):
    q = ('query { tri__tri_reporting_form (limit: 10000, groupBy: ["tri_facility_id"], '
         'where: {tri_facility_id: {in: ' + json.dumps(ids) + '}}) '
         '{ tri_facility_id fn__max(parameters: ["reporting_year"], alias: "latest_year") } }')
    req = urllib.request.Request(API, data=json.dumps({'query': q}).encode(),
                                 headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=180) as f:
        data = json.load(f)
    assert data.get('status') == 'COMPLETED', data
    rows = data['data']['tri__tri_reporting_form']
    assert len(rows) < 10000
    assert len({r['tri_facility_id'] for r in rows}) == len(rows)
    assert all(r['tri_facility_id'] in ids for r in rows)
    return rows

def fetch():
    ids = sorted({r['registry_id'] for r in read(HERE / 'registry_links_snapshot.csv') if r['registry'] == 'TRI_TRIFID'})
    rows = []
    for start in range(0, len(ids), 100):
        batch = ids[start:start+100]
        cache = HERE / 'tri_batches' / f'{start:04}.json'
        cache.parent.mkdir(exist_ok=True)
        if cache.exists():
            result = json.loads(cache.read_text())
        else:
            try:
                found = {r['tri_facility_id']: r['latest_year'] for r in query_years(batch)}
                result = [dict(trifid=i, latest_year=found.get(i, ''), coverage='found' if i in found else 'no_return') for i in batch]
            except Exception as exc:
                result = [dict(trifid=i, latest_year='', coverage=type(exc).__name__) for i in batch]
            cache.write_text(json.dumps(result, indent=2)+'\n')
        assert {r['trifid'] for r in result} == set(batch)
        rows.extend(result)
        print(start+len(batch), '/', len(ids), flush=True)
    assert len(rows) == len(ids) == len({r['trifid'] for r in rows})
    write(HERE / 'tri_years.csv', rows, ['trifid','latest_year','coverage'])

if __name__ == '__main__':
    fetch()
