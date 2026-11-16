#!/usr/bin/env python3
"""Apply only parent columns; append evidence and derive missing parent edges."""
import csv
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CORPUS = Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/pic18-corpus-2026-11-16')
sys.path.insert(0, str(ROOT / 'scripts'))
from shard_io import append_sorted

def read(p):
    with Path(p).open(newline='') as f:
        return list(csv.DictReader(f))

def words(s):
    return re.findall(r'[a-z0-9]+', unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower())

def validate_packet(packet):
    assert len({p['org_id'] for p in packet}) == len(packet)
    manifest = read(CORPUS / 'manifest.csv')
    for p in packet:
        assert p['field'] in ('parent_org_id', 'ultimate_parent_name')
        r = manifest[p['manifest_index']]
        assert (r['org_id'], r['url'], r['text_file']) == (p['org_id'], p['url'], p['text_file'])
        for k in ('text', 'raw'):
            if p[k+'_file']:
                assert hashlib.sha256((CORPUS / p[k+'_file']).read_bytes()).hexdigest() == p[k+'_sha256']
        t, q = words((CORPUS / p['text_file']).read_text()), words(p['quote'])
        assert q and any(t[i:i+len(q)] == q for i in range(len(t)-len(q)+1)), p['org_id']

def main():
    data = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'data'
    packet = json.loads((HERE / 'proposals.json').read_text())
    validate_packet(packet)
    groups = {f: read(f) for f in data.glob('organizations_*.csv')}
    orgs = {r['org_id']: (f,r) for f, rows in groups.items() for r in rows}
    rels = read(data / 'relationships.csv')
    edges = {(r['from_org_id'],r['relationship_type'],r['to_org_id']) for r in rels}
    new_rel, evgroups, touched = [], {}, set()
    for i,p in enumerate(packet):
        f,o = orgs[p['org_id']]
        other = 'ultimate_parent_name' if p['field']=='parent_org_id' else 'parent_org_id'
        assert not o[other] and o[p['field']] in ('',p['value']), p
        if p['field']=='parent_org_id':
            assert p['value'] in orgs and p['value'] != p['org_id']
        o[p['field']] = p['value']; touched.add(f)
        ef = data / ('evidence_'+f.name)
        ev = dict(evidence_id=f'EVD-{384000+i:06d}', record_table='organizations',record_id=p['org_id'],claim_type='parent',
                  claim_detail=f'{p["field"]}={p["value"]}: "{p["quote"]}"',source_class='own_site',source_ref=p['url'],observed_date='2026-11-16',
                  tier_effect='supports_U' if o['verification_tier']=='U' else 'supports_A',created_by='atlas-w16-parents',notes='Shared retained own-site corpus; parent-only observation, no tier or status restatement.')
        existing={r['evidence_id']:r for r in read(ef)}
        if ev['evidence_id'] in existing: assert existing[ev['evidence_id']]==ev
        else: evgroups.setdefault(ef,[]).append(ev)
    # Generate from the canonical columns after application, following §4.14 / V-27.
    for p in packet:
        o=orgs[p['org_id']][1]
        edge=(o['parent_org_id'],'parent_of',o['org_id'])
        if o['parent_org_id'] and edge not in edges:
            new_rel.append(dict(relationship_id=f'REL-{480+len(new_rel):06d}',from_org_id=edge[0],relationship_type=edge[1],to_org_id=edge[2],effective_from='',effective_to='',
                                basis=f'Generated from {o["org_id"]}.parent_org_id; pic18-parent-links 2026-11-16.',source_ref=f'organizations: {o["org_id"]}.parent_org_id; tasks/pic18-parent-links-2026-11-16/proposals.json',created_by='atlas-w16-parents',notes='No effective date inferred.'))
    for f in touched:
        with f.open('w',newline='') as out:
            w=csv.DictWriter(out,fieldnames=list(groups[f][0]),lineterminator='\n');w.writeheader();w.writerows(groups[f])
    for f,rows in evgroups.items(): append_sorted(f,rows,'evidence_id')
    if new_rel: append_sorted(data/'relationships.csv',new_rel,'relationship_id')
    print(f'{len(packet)} organization parent fills; {sum(map(len,evgroups.values()))} evidence rows appended; {len(new_rel)} generated edges appended')
if __name__=='__main__': main()
