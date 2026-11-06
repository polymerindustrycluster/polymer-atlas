"""Idempotently union the reviewed L10 values and append one immutable evidence row per value."""
import csv, json, sys
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from shard_io import append_sorted
from regions import PIC18

def read(path):
    with path.open(newline='') as f: return list(csv.DictReader(f))

def main():
    data = ROOT / 'data'
    shards = {p: read(p) for p in sorted(data.glob('organizations_*.csv')) if p.stem != 'organizations_all'}
    orgs = {r['org_id']: (p, r) for p, rows in shards.items() for r in rows}
    assert len(orgs) == sum(map(len, shards.values()))
    vocab = json.loads((ROOT / 'docs/schema/vocab.json').read_text())['vocabularies']
    allowed = {'markets_served': set(vocab['MARKETS']['values']), 'certifications': set(vocab['CERTS']['values'])}
    inputs = read(HERE / 'inputs.csv')
    assert len({(r['org_id'], r['field'], r['value']) for r in inputs}) == len(inputs)
    pic18 = {r['org_id'] for r in read(data / 'sites_OH.csv') if r['county'] in PIC18}
    evidence = {r['evidence_id']: r for p in data.glob('evidence_*.csv') for r in read(p)}
    append, touched = defaultdict(list), set()
    def counts():
        active = [r for _, r in orgs.values() if r['status'] == 'active']
        return {'active_organizations': len(active), **{f: sum(bool(r[f]) for r in active) for f in allowed}}
    before = counts()
    for i, v in enumerate(inputs):
        if v['verdict'] == 'STILL_UNCERTAIN': continue
        assert v['verdict'] == 'VERIFIED'
        field = v['field']; assert field in allowed and v['value'] in allowed[field]
        path, row = orgs[v['org_id']]
        assert row['status'] == 'active' and row['org_id'] in pic18
        host = lambda u: urlparse(u if '://' in u else 'https://' + u).hostname.removeprefix('www.')
        assert host(v['source_url']) == host(row['website']), v
        values = row[field].split(';') if row[field] else []
        if v['value'] not in values:
            row[field] = ';'.join(sorted(values + [v['value']])); touched.add(path)
        eid = f'EVD-{240000+i:06d}'; assert int(eid[4:]) <= 259999
        ev = dict(evidence_id=eid, record_table='organizations', record_id=v['org_id'], claim_type='activity',
                  claim_detail=f'{field} {v["value"]}: "{v["quote"]}"', source_class='own_site',
                  source_ref=v['source_url'], observed_date='2026-11-06', tier_effect='supports_A',
                  created_by='codex atlas-L10-markets-certs', notes=v['note'] or 'Own-site corporate claim; raw quote checked 2026-11-06; record tier unchanged.')
        if eid in evidence: assert evidence[eid] == ev, ('ID collision or changed observation', eid)
        else: append[data / path.name.replace('organizations_', 'evidence_organizations_')].append(ev)
    for path in touched:
        with path.open('w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(shards[path][0]), lineterminator='\n'); w.writeheader(); w.writerows(shards[path])
    for path, rows in append.items(): append_sorted(path, rows, 'evidence_id')
    print(json.dumps({'before': before, 'after': counts(), 'packet_value_rows': len(inputs),
                      'packet_organizations': len({r['org_id'] for r in inputs if r['verdict'] == 'VERIFIED'}),
                      'tiers': dict(Counter(orgs[oid][1]['verification_tier'] for oid in {r['org_id'] for r in inputs if r['verdict'] == 'VERIFIED'})),
                      'new_evidence_rows': sum(map(len, append.values()))}, indent=2))

if __name__ == '__main__': main()
