#!/usr/bin/env python3
"""Census the packet and blind-shuffle its 10 creates against banked ITA rows."""
import csv,hashlib,json,random,subprocess,sys,tempfile,shutil
from pathlib import Path
from collections import Counter
H=Path(__file__).resolve().parent;R=H.parents[1];sys.path.insert(0,str(R/'scripts'))
from atlas import load_tables,dedupe,name_key
from build_qcew_denominators import atlas_numerators
from build import read, clean_street, ring_for_naics
vs=read(H/'verdicts.csv');cs=read(H/'input.csv');alloc=read(H/'allocations.csv')
assert len(vs)==len(cs)==len({r['cluster_id'] for r in vs})==125
assert {r['cluster_id'] for r in cs}=={r['cluster_id'] for r in vs}
assert len(alloc)==10 and len({r['site_id'] for r in alloc})==10
T=load_tables(R/'data');ita={r['establishment_id']:r for r in read(R/'tasks/osha-ita-2026-11-01/establishments.csv')}
sites={r['site_id']:r for r in T['sites'].rows};orgs={r['org_id']:r for r in T['organizations'].rows}
# Known-answer calibration includes the two registrant-name failures that motivated B-ALIAS.
for name,oid in [('Dart Container Corp','ORG-002441'),('New Wincup Holdings, Inc.','ORG-000984'),('Plastipak Packaging','ORG-001033')]:
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
assert len(dups)==0
for v in dups:
 assert sites[v['duplicate_of']]['org_id']==v['held_org_id']
for fn in ['sites_WI.csv','evidence_sites_WI.csv']:
 old=list(csv.DictReader(subprocess.check_output(['git','show','9d69978:data/'+fn],text=True).splitlines()))
 key=list(old[0])[0];new={r[key]:r for r in read(R/'data'/fn)}
 assert all(new.get(r[key])==r for r in old)
owned=[r for r in T['evidence'].rows if 204000<=int(r['evidence_id'][4:])<=204076]
assert len(owned)==70 and all(r['source_class']=='government_filing' for r in owned)
ff=next(r for r in read(H/'allocations.csv') if r['cluster_id']=='LF-WI-00632')
assert sum(r['state']=='WI' and r['street_address']=='8430 Murphy Dr' for r in T['sites'].rows)==1
for r in owned:
 if r['record_id']==ff['site_id']:
  assert '568224' in r['notes'] and '568232' in r['notes']
for code,expected in [('326199','1'),('325510','2'),('325520','2'),('325991','2'),('325212','2')]:assert ring_for_naics(code)==expected
for code in ['325211','325998','325999']:
 try:ring_for_naics(code);raise AssertionError('unresolved ring admitted')
 except ValueError:pass
assert next(v for v in vs if v['cluster_id']=='LF-WI-00381')['verdict']=='STILL_UNCERTAIN'
assert 'SITE-016408' not in sites
assert not({f'EVD-{i:06d}' for i in range(204056,204063)} & {r['evidence_id'] for r in T['evidence'].rows})
with tempfile.TemporaryDirectory(dir=H.parent) as packet_dir,tempfile.TemporaryDirectory() as data_dir:
 packet=Path(packet_dir);shutil.copytree(H,packet,dirs_exist_ok=True);verdicts=read(packet/'verdicts.csv')
 for v in verdicts:
  if v['cluster_id']=='LF-WI-00381':v.update(verdict='VERIFIED',held_org_id='ORG-000662')
 with (packet/'verdicts.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(verdicts[0]),lineterminator='\n');w.writeheader();w.writerows(verdicts)
 data=Path(data_dir)/'data';shutil.copytree(R/'data',data);before_bad={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.csv')}
 bad=subprocess.run([sys.executable,str(packet/'build.py'),'--data-dir',str(data),'--apply'],capture_output=True)
 assert bad.returncode!=0 and b'HOLD: unresolved independent operator/domain conflict' in bad.stderr
 assert before_bad=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.csv')}
# Byte idempotence, and a mutation: an occupied lane ID must fail without modifying any file.
files=[R/'data'/f for f in ['sites_WI.csv','evidence_sites_WI.csv','organizations_WI.csv','evidence_organizations_WI.csv']]
before=[hashlib.sha256(p.read_bytes()).hexdigest() for p in files]
subprocess.run([sys.executable,str(H/'build.py'),'--apply'],check=True,capture_output=True)
assert before==[hashlib.sha256(p.read_bytes()).hexdigest() for p in files]
with tempfile.TemporaryDirectory() as d:
 data=Path(d)/'data';shutil.copytree(R/'data',data)
 p=data/'sites_WI.csv';p.write_text(p.read_text().replace('SITE-016400,','SITE-016400,WRONG-',1))
 before_bad={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.csv')}
 r=subprocess.run([sys.executable,str(H/'build.py'),'--data-dir',str(data),'--apply'],capture_output=True)
 assert r.returncode!=0 and b'conflicting ID' in r.stderr
 assert before_bad=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.csv')}
for dest,key,value in [('sites_FL.csv','site_id','SITE-016400'),('evidence_organizations_FL.csv','evidence_id','EVD-204000')]:
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
now=atlas_numerators(str(R))[('WI','326')][1]
base=list(csv.DictReader(subprocess.check_output(['git','show','9d69978:data/sites_WI.csv'],text=True).splitlines()))
old=sum(r.get('country','US') in ('','US') and r['naics_primary'].startswith('326') and r['operating_status'] in ('active','unknown') and r['verification_tier'] in ('A','B','C') for r in base)
q=next(r for r in read(R/'docs/denominators/qcew_state_polymer_2023_2024.csv') if r['area_fips']=='55000' and r['year']=='2023' and r['industry_code']=='326')
den=float(q['annual_avg_estabs'])
assert now==old+sum(sites[r["site_id"]]["naics_primary"].startswith("326") for r in alloc)
result=dict(worked_WI_clusters=125,sites_C=10,blind_recheck_passes=10,known_answer_passes=3,idempotence='PASS',conflicting_ID_mutation='PASS (fails before writes)',NAICS326_strict_sites_before=old,NAICS326_strict_sites_after=now,QCEW2023_private_establishments=den,strict_share_before=old/den,strict_share_after=now/den)
(H/'check_results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
