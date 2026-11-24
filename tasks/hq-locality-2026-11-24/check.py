"""Verify the full before/after shard contents and every corrected claim."""
import csv
import hashlib
import io
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from check_evidence_binding import claim_sha256, capture_text

BASE = sys.argv[1] if len(sys.argv)>1 else 'a80ad5fc'
def read(name, base=False):
    f = ROOT / 'data' / (name+'.csv')
    data = subprocess.check_output(['git','show',f'{BASE}:data/{f.name}'],cwd=ROOT) if base else f.read_bytes()
    return list(csv.DictReader(io.StringIO(data.decode(), newline='')))

def packet(name):
    with (HERE/name).open(newline='') as f:
        return list(csv.DictReader(f))

expected = {'ORG-000149': ('MN','EVD-483118',dict(hq_city='Minneapolis',hq_state='MN',hq_county='',hq_in_scope='national_us')),
            'ORG-001776': ('OH','EVD-483119',dict(hq_city='Canton'))}
proofs = packet('BINDING_PROOF.csv')
assert len(proofs) == 2 and {p['evidence_id'] for p in proofs} == {v[1] for v in expected.values()}
claims = []
for table, key in [('organizations','org_id'),('evidence_organizations','record_id')]:
    old = {s:read(table+'_'+s,True) for s in ('OH','MN')}
    new = {s:read(table+'_'+s) for s in old}
    for i,(shard,eid,fields) in expected.items():
        rows = [r for r in old['OH'] if r[key]==i]
        assert rows
        if table=='organizations':
            record, = rows
            for k,v in fields.items():
                assert record[k]!=v
                claims.append(('organizations',i,k,'corrected',eid))
                record[k]=v
        if shard!='OH':
            old['OH'] = [r for r in old['OH'] if r[key]!=i]
            old[shard].extend(rows)
        if table=='evidence_organizations':
            ev, = [r for r in new[shard] if r['evidence_id']==eid]
            proof, = [p for p in proofs if p['evidence_id']==eid]
            assert (ev[key],ev['address_role'],ev['claim_type'],ev['source_class'])==(i,'physical','address','own_site')
            assert proof['capture'] == ev['source_ref'] or proof['capture'].endswith('id_/'+ev['source_ref'])
            assert proof['claim_sha256']==claim_sha256(ev) and proof['verdict']=='VERIFIED'
            old[shard].append(ev)
    if table=='organizations':
        old['MN'].sort(key=lambda r:r['org_id'])
    assert new==old, table
assert sorted(tuple(c.values()) for c in packet('CLAIMS_CHECKED.csv'))==sorted(claims)
archives=read('archive_links')
assert archives[:-2]==read('archive_links',True)
assert [r['evidence_id'] for r in archives[-2:]]==[p['evidence_id'] for p in proofs]
if len(sys.argv)>2:
    manifest=(HERE/'INPUTS.sha256').read_text().splitlines()
    assert len(manifest)==2
    for proof, line in zip(proofs,manifest,strict=True):
        sha, path=line.split('  ')
        b=(Path(sys.argv[2])/path).read_bytes()
        assert hashlib.sha256(b).hexdigest()==sha==proof['capture_sha256']
        shard=expected[proof['record_id']][0]
        ev,=[r for r in read('evidence_organizations_'+shard) if r['evidence_id']==proof['evidence_id']]
        quote=ev['claim_detail'].split('quote: ')[1]
        assert capture_text(b)[int(proof['quote_offset']):].startswith(quote)
    print('Both shared-store hashes and quote offsets passed')
print('Two corrected organization HQ records, five changed cells, two witnesses, two archive links. All four shards replay.')
