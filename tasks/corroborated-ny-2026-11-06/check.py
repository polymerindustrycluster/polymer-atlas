#!/usr/bin/env python3
"""Census the packet and blind-shuffle its 7 creates against banked ITA rows."""
import csv,hashlib,json,random,subprocess,sys,tempfile,shutil
from pathlib import Path
from collections import Counter
H=Path(__file__).resolve().parent;R=H.parents[1];sys.path.insert(0,str(R/'scripts'))
from atlas import load_tables,dedupe,name_key
from build_qcew_denominators import atlas_numerators
from build import read, clean_street
vs=read(H/'verdicts.csv');cs=read(H/'input.csv');alloc=read(H/'allocations.csv')
assert len(vs)==len(cs)==len({r['cluster_id'] for r in vs})==81
assert {r['cluster_id'] for r in cs}=={r['cluster_id'] for r in vs}
assert len(alloc)==7 and len({r['site_id'] for r in alloc})==7
T=load_tables(R/'data');ita={r['establishment_id']:r for r in read(R/'tasks/osha-ita-2026-11-01/establishments.csv')}
sites={r['site_id']:r for r in T['sites'].rows};orgs={r['org_id']:r for r in T['organizations'].rows}
# Known-answer calibration includes the two registrant-name failures that motivated B-ALIAS.
for name,oid in [('Dart Container Corp','ORG-002441'),('New Wincup Holdings, Inc.','ORG-000984'),('Plastipak Packaging','ORG-001033'),('Protective Industries Inc','ORG-002737')]:
 assert any(h['id']==oid for st in dedupe(T,name=name)['steps'] for h in st['hits']),(name,oid)
# Re-check source-first in a seeded blind order, without using verdict reasons as evidence.
rows=[];random.Random(7731).shuffle(alloc)
for a in alloc:
 f=ita[a['establishment_id']];s=sites[a['site_id']];o=orgs[s['org_id']]
 assert (s['street_address'],s['city'],s['zip'],s['naics_primary'])==(clean_street(f),f['city'],f['zip5'],f['naics_code'])
 assert f['reliability']=='ok' and f['size_code_vs_avg_employees']=='consistent'
 assert s['verification_tier']=='C' and f['year_filing_for']=='2025'
 names={name_key(o['legal_name']),*(name_key(t.removesuffix(' (federal registrant name)').strip()) for t in o['trade_names'].split(';'))}
 # Mapei Wildwood is witnessed by its explicitly preserved registrant alias.
 assert name_key(f['company_name']) in names,(s['site_id'],f['company_name'],o['legal_name'])
 rows.append(dict(site_id=s['site_id'],establishment_id=f['establishment_id'],operator=o['legal_name'],result='PASS: held operator + physical address + filed NAICS; federal-only C'))
with (H/'blind_recheck.csv').open('w') as out:
 w=csv.DictWriter(out,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
dups=[r for r in vs if r['verdict']=='DUPLICATE_OF']
assert len(dups)==1 and dups[0]['duplicate_of']=='SITE-003050'
assert sites[dups[0]['duplicate_of']]['org_id']==dups[0]['held_org_id']
# Every pre-pass row survives; only the three declared alias cells may differ.
for fn in ['sites_NY.csv','evidence_sites_NY.csv','organizations_PA.csv','evidence_organizations_PA.csv','organizations_OH.csv','evidence_organizations_OH.csv']:
 old=list(csv.DictReader(subprocess.check_output(['git','show','9489b60:data/'+fn],text=True).splitlines()))
 key=list(old[0])[0];new={r[key]:r for r in read(R/'data'/fn)}
 for r in old:
  assert r[key] in new
  changed={k for k in r if r[k]!=new[r[key]][k]}
  assert not changed or (fn.startswith('organizations_') and r[key] in {'ORG-002737','ORG-001148','ORG-000004'} and changed=={'trade_names'})
# Byte idempotence, and a mutation: an occupied lane ID must fail without modifying any file.
files=[R/'data'/f for f in ['sites_NY.csv','evidence_sites_NY.csv','organizations_PA.csv','evidence_organizations_PA.csv','organizations_OH.csv','evidence_organizations_OH.csv']]
before=[hashlib.sha256(p.read_bytes()).hexdigest() for p in files]
subprocess.run([sys.executable,str(H/'build.py'),'--apply'],check=True,capture_output=True)
assert before==[hashlib.sha256(p.read_bytes()).hexdigest() for p in files]
with tempfile.TemporaryDirectory() as d:
 data=Path(d)/'data';shutil.copytree(R/'data',data)
 p=data/'sites_NY.csv';p.write_text(p.read_text().replace('SITE-016200,','SITE-016200,WRONG-',1))
 before_bad={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.csv')}
 r=subprocess.run([sys.executable,str(H/'build.py'),'--data-dir',str(data),'--apply'],capture_output=True)
 assert r.returncode!=0 and b'conflicting ID' in r.stderr
 assert before_bad=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.csv')}
for dest,key,value in [('sites_FL.csv','site_id','SITE-016200'),('evidence_organizations_FL.csv','evidence_id','EVD-202000')]:
 with tempfile.TemporaryDirectory() as d:
  data=Path(d)/'data';shutil.copytree(R/'data',data)
  p=data/dest;rows=read(p);bad=dict(rows[0]);bad[key]=value
  with p.open('a') as f:
   w=csv.DictWriter(f,fieldnames=list(bad),lineterminator='\n');w.writerow(bad)
  before_bad={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.csv')}
  r=subprocess.run([sys.executable,str(H/'build.py'),'--data-dir',str(data),'--apply'],capture_output=True)
  assert r.returncode!=0 and b'conflicting ID' in r.stderr
  assert before_bad=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.csv')}
# State strict numerator definition is reused from the official denominator builder.
now=atlas_numerators(str(R))[('NY','326')][1]
base=list(csv.DictReader(subprocess.check_output(['git','show','9489b60:data/sites_NY.csv'],text=True).splitlines()))
old=sum(r.get('country','US') in ('','US') and r['naics_primary'].startswith('326') and r['operating_status'] in ('active','unknown') and r['verification_tier'] in ('A','B','C') for r in base)
q=next(r for r in read(R/'docs/denominators/qcew_state_polymer_2023_2024.csv') if r['area_fips']=='36000' and r['year']=='2023' and r['industry_code']=='326')
den=float(q['annual_avg_estabs'])
assert now==old+sum(sites[r["site_id"]]["naics_primary"].startswith("326") for r in alloc)
result=dict(worked_NY_clusters=81,sites_C=7,blind_recheck_passes=7,known_answer_passes=4,idempotence='PASS',conflicting_ID_mutation='PASS (fails before writes)',NAICS326_strict_sites_before=old,NAICS326_strict_sites_after=now,QCEW2023_private_establishments=den,strict_share_before=old/den,strict_share_after=now/den)
(H/'check_results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
