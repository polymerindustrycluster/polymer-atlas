"""Named offline check: score boundaries, federal coverage, unique queue and dated-status gate."""
import json
from build import score
from federal_signals import HERE, ROOT, read

assert score('NXDOMAIN',[],False,[])==30
assert score('PARKED_SUSPECT',[2023],True,[2020])==50
assert score('BOT_WALL_SUSPECT',[],False,[])==0
assert score('OK',[2024],False,[2024])==0
assert score('OK',[2023,2025],False,[2010,2024])==0
links=read(HERE/'registry_links_snapshot.csv')
tri=read(HERE/'tri_years.csv')
assert len(tri)==len({r['trifid'] for r in tri})
assert {r['trifid'] for r in tri}=={r['registry_id'] for r in links if r['registry']=='TRI_TRIFID'}
actual={r['trifid']:r['latest_year'] for r in tri}
for r in json.loads((HERE/'known_answers.json').read_text()):
    assert int(actual[r['trifid']])==r['expected_year']
rows=read(HERE/'signals.csv')
def unique(records):
    assert len(records)==len({r['org_id'] for r in records})
unique(rows)
try:
    unique(rows+[rows[0]])
except AssertionError:
    pass
else:
    raise AssertionError('injected duplicate escaped uniqueness gate')
expected=[r for p in sorted((ROOT/'data').glob('organizations_*.csv')) for r in read(p)] + read(ROOT/'data/ecosystem.csv')
assert {r['org_id'] for r in rows} == {r['org_id'] for r in expected if r['status'] in ('active','unknown')}

assert rows==sorted(rows,key=lambda r:(-int(r['score']),r['org_id']))
assert [int(r['rank']) for r in rows]==list(range(1,len(rows)+1))
assert [int(r['score']) for r in rows]==sorted([int(r['score']) for r in rows],reverse=True)
print(f'PASS: {len(tri)} distinct TRI keys accounted; 3 independent known answers; {len(rows)} unique ranked rows; score boundaries')

sponsor_rows=read(ROOT/'tasks/form5500-spine-2026-11-01/sponsors.csv')
sponsors={r['ein']:r for r in sponsor_rows}
assert len(sponsors)==len(sponsor_rows)
for key,year in [('631127539','2024'),('881282156','2025'),('341352998','2023')]:
    assert sponsors[key]['latest_filed_plan_year_any']==year
print('PASS: 3 Form 5500 known-key years (2024 / 2025 / 2023)')
import subprocess
# This packet applies zero mutations; any data edit requires a new dated-evidence application contract.
from git_gate import assert_data_unchanged
assert_data_unchanged(ROOT)
print('PASS: zero data/status changes; dated-status evidence gate has no applied cases')

assert len(tri)==2150 and all(r['coverage']=='found' and r['latest_year']=='2024' for r in tri)
federal=read(HERE/'federal_link_signals.csv')
assert len(federal)==2473
assert sum(r['registry']=='EIN' and r['coverage']=='found' for r in federal)==320
assert all(r['coverage']=='found' for r in federal)
import hashlib
assert hashlib.sha256((HERE/'registry_links_snapshot.csv').read_bytes()).hexdigest()=='b830d047d4bedc576b7628cf0bbdebf685a6288cb2ed4d2ddbf1700d9e741953'
for r in rows:
    sy=[int(item.rsplit(':',1)[1]) for item in r['ein_years'].split(';') if item and item.rsplit(':',1)[1].isdigit()]
    ty=[int(item.rsplit(':',1)[1]) for item in r['trifid_years'].split(';') if item and item.rsplit(':',1)[1].isdigit()]
    assert int(r['score'])==score(r['signal_class'],sy,r['form5500_final_or_short']=='1',ty)
print('PASS: frozen-run all-key coverage/year claims; pinned snapshot; every queue score recomputed')

from collections import Counter, defaultdict
from build import normalize_website
by_org=defaultdict(list)
expected_links=[]
for link in links:
    if link['registry'] not in ('EIN','TRI_TRIFID'): continue
    by_org[link['org_id']].append(link)
    key=link['registry_id']
    if link['registry']=='EIN':
        year=sponsors.get(key,{}).get('latest_filed_plan_year_any','')
        coverage='found' if year else 'NOT_IN_SPINE'
    else:
        item=next(r for r in tri if r['trifid']==key)
        year=item['latest_year'];coverage=item['coverage']
    expected_links.append(dict(org_id=link['org_id'],site_id=link['site_id'],registry=link['registry'],registry_id=key,latest_year=year,coverage=coverage))
assert Counter(tuple(sorted(r.items())) for r in federal)==Counter(tuple(sorted(r.items())) for r in expected_links)
orgs={r['org_id']:r for r in expected}
sweep={oid:r for r in read(HERE/'sweep/signals.csv') for oid in r['org_id'].split(';')}
tri_index={r['trifid']:r for r in tri}
for r in rows:
    oid=r['org_id']; f=[];t=[]
    for link in by_org[oid]:
        key=link['registry_id']
        if link['registry']=='EIN':
            item=sponsors.get(key,{})
            f.append((key,item.get('latest_filed_plan_year_any',''),item.get('latest_py_all_final_or_short','')))
        else:
            item=tri_index[key];t.append((key,item['latest_year'],item['coverage']))
    assert r['ein_years']==';'.join(k+':'+(y or 'NOT_IN_SPINE') for k,y,_ in f)
    assert r['trifid_years']==';'.join(k+':'+(y or cov) for k,y,cov in t)
    assert r['form5500_final_or_short']==str(int(any(v=='1' for _,_,v in f)))
    fy=[int(y) for _,y,_ in f if y];ty=[int(y) for _,y,_ in t if y]
    assert r['form5500_latest_year']==(str(max(fy)) if fy else '')
    assert r['tri_latest_year']==(str(max(ty)) if ty else '')
    assert r['tri_unresolved']==str(sum(not y for _,y,_ in t))
    assert r['current_website']==orgs[oid]['website'] and r['legal_name']==orgs[oid]['legal_name']
    domain,_=normalize_website(orgs[oid]['website']); obs=sweep.get(oid,{})
    changed=bool(obs and domain!=obs['domain'])
    assert r['domain']==(domain or '') and r['sweep_domain']==obs.get('domain','')
    assert r['signal_class']==('WEBSITE_CHANGED_SINCE_SWEEP' if changed else obs.get('signal_class','NOT_SWEPT'))
    assert r['final_url']==('' if changed else obs.get('final_url',''))
old={r['domain']:r for r in read(ROOT/'tasks/liveness-sweep-2026-11-01/signals.csv')}
new={r['domain']:r for r in read(HERE/'sweep/signals.csv')}
assert len(old)==len(read(ROOT/'tasks/liveness-sweep-2026-11-01/signals.csv'))
assert len(new)==len(read(HERE/'sweep/signals.csv'))
comparison=read(HERE/'comparison.csv')
assert len(comparison)==len({r['domain'] for r in comparison})==len(old.keys()|new.keys())
for r in comparison:
    assert r['previous']==old.get(r['domain'],{}).get('signal_class','NOT_IN_FRAME')
    assert r['current']==new.get(r['domain'],{}).get('signal_class','NOT_IN_FRAME')
assert {r['domain'] for r in comparison}==old.keys()|new.keys()
from research import CASES
assert [r['org_id'] for r in rows[:10]]==[r['org_id'] for r in read(HERE/'verdicts.csv')]==[r[0] for r in CASES]
print('PASS: full federal-link multiset; source field joins; every comparison transition; current websites; research top-ten alignment; no untracked data')
