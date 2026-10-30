#!/usr/bin/env python3
"""Read-only packet guards; optional argument = official RY2024 US CSV."""
import csv, hashlib, json, pathlib, re, subprocess, sys
D=pathlib.Path(__file__).resolve().parent
R=D.parents[2]
def read(p):
    with p.open(newline='') as f:return list(csv.DictReader(f))
fp=json.loads((D/'fingerprints.json').read_text());pin=fp['pin']
for p,h in fp['canonical_file_sha256'].items():
    assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
    assert subprocess.check_output(['git','show',f'{pin}:{p}'],cwd=R)==(R/p).read_bytes(),p
q=(R/'tasks/QUEUE.md').read_text();base=subprocess.check_output(['git','show',f'{pin}:tasks/QUEUE.md'],cwd=R,text=True)
assert q==base.replace('`open` **F3 —','`claimed:codex-f3 2026-10-30` **F3 —')
orgs={r['org_id'] for p in (R/'data').glob('organizations_*.csv') for r in read(p)}
sites=[r for p in (R/'data').glob('sites_*.csv') for r in read(p)]
org_universe=orgs | {r['org_id'] for r in read(R/'data/ecosystem.csv')}
assert all(r['org_id'] in org_universe for r in sites),'canonical full-union FK failure'
v=read(D/'verdicts.csv');s=read(D/'site_design.csv');e=read(D/'evidence_rows.csv');g=read(D/'registry_checks.csv')
keys={r['packet_key'] for r in v};assert len(v)==len(keys)==5
assert {r['packet_key'] for r in s}==keys=={r['packet_key'] for r in g}
assert sum(r['verdict']=='VERIFIED' for r in v)==3
for r in v:
    assert r['verdict'] in {'VERIFIED','STILL_UNCERTAIN','REJECT'}
    assert r['deciding_fact'] if r['verdict'] in {'VERIFIED','REJECT'} else r['settling_fact']
for r in s:
    assert not r['site_id']
    assert not r['org_id'] or r['org_id'] in orgs
    assert r['candidate_held_org_id'] in orgs
for r in e:
    assert r['packet_key'] in keys and not r['evidence_id'] and not r['record_id']
    assert r['record_table']=='sites'
    assert r['claim_type'] in {'existence','address','scope','code','parent','activity','liveness'}
    assert r['tier_effect'] in {'supports_A','supports_B','supports_C','contradicts'}
    assert re.fullmatch(r'\d{4}-\d{2}-\d{2}',r['observed_date'])
    assert r['source_ref'].startswith('https://')
    if r['source_class'] in {'registry','directory','press'}:assert r['tier_effect']!='supports_A'
    if r['source_class'] in {'registry','directory'} and r['claim_type']=='address':assert r['tier_effect'] in {'supports_C','contradicts'}
for r in v:
    if r['verdict']=='VERIFIED':
        assert {x['claim_type'] for x in e if x['packet_key']==r['packet_key']}=={'existence','address','scope','code','parent','activity','liveness'}
    else:
        x=next(x for x in s if x['packet_key']==r['packet_key']);assert not x['org_id'] and x['verification_tier']=='U'
for r in g:assert not r['site_id'] and not r['registry_link_id']
assert all(not x['normalized_street_state_hits'] for x in fp['dedupe'])
if len(sys.argv)>1:
    raw=pathlib.Path(sys.argv[1]);rows=read(raw)
    assert hashlib.sha256(raw.read_bytes()).hexdigest()==g[0]['extract_sha256']
    for r in g:
        hits=[x for x in rows if x['2. TRIFD']==r['TRI_TRIFID']]
        assert len(hits)==int(r['chemical_report_row_count'])
        for x in hits:
            for a,b in [('FRS_ID','3. FRS ID'),('street_address','5. STREET ADDRESS'),('county','7. COUNTY'),('state','8. ST')]:assert r[a]==x[b]
print(f'PASS: {len(v)} verdicts, {len(s)} designs, {len(e)} unallocated evidence observations; {len(sites)} canonical site FKs resolve across {len(org_universe)} organization/ecosystem-union IDs; all data bytes unchanged.')
