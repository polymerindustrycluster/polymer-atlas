Attempt to REFUTE completion of GA CORROBORATED continuation L7. End VERDICT: APPROVE or REFUTE with concrete findings. Inspect code, sources, parent/address identity, duplicate/campus risk and evidence. Controller grants inherited ITA at2026-11-01 vintage without fresh download. Federal-only C is existing CAMPAIGN convention; no A/B claims, own-page quotes or new organizations.147 screened=20creates+127 uncompleted research holds,140 site evidence. Validate0, census,20 source-first checks,idempotence,mutation pass. Claimed blind check uses shuffled source-first rows and separately tests company_name against held legal/trade_names (builder does not). Supplied files follow.

FILE README.md
# Georgia CORROBORATED continuation (L7), 2026-11-06

Acceptance: after FL draft PR132, separate branch/PR; max150 clusters, exact verdict census, held-parent-only federal C creates, append-only evidence, ordered IDs, fail-closed/idempotent builder, validate0,20 shuffled source-first re-checks, strict NAICS326/QCEW before/after. First user: campaign integrator reviewing this PR on2026-11-06; non-use finding date2026-11-13.

147 GA CORROBORATED candidate establishment clusters screened:20 VERIFIED site creates under 15 held parents;127 STILL_UNCERTAIN research holds;0 new organizations,0 REJECT,0 DUPLICATE_OF. All20 sites tier C;140 site evidence rows. No changes to held organizations or their tiers. Federal company names are already represented by legal/trade names (including New Wincup Holdings→ORG-000984); no new alias needed. No inclusion_log entries: unresolved cases held.

Sources: banked OSHA ITA CY2025 employer establishment filings, https://www.osha.gov/sites/default/largefiles/ITA_300A_Summary_Data_2025_through_08-31-2026.csv . Controller expressly authorized inherited ITA/OSHA/ECHO packets at2026-11-01 vintage without new downloads; this supersedes the brief raw-fetch rule only for those named federal extracts. All20 creates use ITA; every citation has establishment_ID and date_submitted. No own-page quotes, A/B claims or new registry links. Existing CAMPAIGN federal-only C convention governs provisional scope. Active is provisional at CY2025 filing vintage; no2026 live operating check is claimed. No closure findings. No county guessed from city (left blank).

Dedupe: atlas.py CLI logs before application in create_dedupe.json; domain where held, company/registrant legal and trade names, addresses and notes. prep.py additionally screens all147 cluster names/variants. Known-answer calibration passes Dart, New Wincup Holdings and Plastipak. Generic Valdosta→GAF from ITA company_name, supported by held GAF trade name. Adjacent CKS5515/5545 Tulane addresses remain holds; no two-campus assumption. Held Shaw/Printpack/Goodyear ambiguous campus aliases stay held, no ID allocation for them. The127 holds are screened, uncompleted research; no claim of exhaustive six-fetch investigations.

`python3 scripts/validate.py`: PASS zero errors.
`python3 tasks/corroborated-ga-2026-11-06/check.py`: PASS147/147 census,3 known answers,20/20 shuffled source-first blind checks, byte-idempotence and occupied-ID mutation fails before writes.
`python3 tasks/corroborated-ga-2026-11-06/build.py --apply`: second run pending rows0.
No scripts/ edits; scripts pytest not applicable.

Georgia strict NAICS326 sites (active/unknown,A/B/C,US)/QCEW2023 private establishments:62/491=12.6273% before,74/491=15.0713% after.12 creates carry326;8 carry3255/3259. Count ratio, not matched coverage. Other states untouched. Pre-pass backup is branch base c71c0413f0054bc99bf341a8c75dff36609d24d7. IDs SITE-016100–016119;EVD-201000–201139. ORG IDs unused. Rebase by restoring main data and rerunning builder, never hand-merge CSVs.

Cross-thread: no shared scripts edits; L6 confirms banked official URL and CORROBORATED source gaps. L7 made no FRS REST requests. Controller05:55 clerk policy supersedes original council-only/refutes-before-draft sequence; two-family approval remains mandatory. DATA-ESTATE Documents/RAG layers unavailable on Mac; no estate-absence claim. No private/licensed sources or personal contacts.

## Refutes
Pending Codex and Grok approval; draft only.


FILE build.py
#!/usr/bin/env python3
"""Apply the curated Georgia federal-only C packet; reruns compare then skip exact rows."""
import argparse,csv,json,sys
from collections import Counter,defaultdict
from pathlib import Path
H=Path(__file__).resolve().parent; ROOT=H.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from shard_io import append_sorted
from atlas import street_key
DATE='2026-11-06'; BY='codex atlas-L7-corr-fl-ga'
SOURCE='https://www.osha.gov/sites/default/largefiles/ITA_300A_Summary_Data_2025_through_08-31-2026.csv'
def read(p):
 with open(p,newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');ap.add_argument('--data-dir',type=Path,default=ROOT/'data');a=ap.parse_args();data=a.data_dir
 cs={r['cluster_id']:r for r in read(H/'input.csv')};vs=read(H/'verdicts.csv')
 assert len(vs)==len(cs)==147 and len({v['cluster_id'] for v in vs})==147
 assert set(cs)=={v['cluster_id'] for v in vs}
 assert set(v['verdict'] for v in vs)<={'VERIFIED','REJECT','STILL_UNCERTAIN','DUPLICATE_OF'}
 ita={r['establishment_id']:r for r in read(ROOT/'tasks/osha-ita-2026-11-01/establishments.csv')}
 orgs={r['org_id']:r for p in data.glob('organizations_*.csv') for r in read(p)}
 oldsites=[r for p in data.glob('sites_*.csv') for r in read(p)]
 out=defaultdict(list);eid=201000;alloc=[]
 for idx,v in enumerate(v for v in vs if v['verdict']=='VERIFIED'):
  c=cs[v['cluster_id']];oid=v['held_org_id'];org=orgs[oid];assert org['status']=='active' and not org['successor_org_id']
  fed=[ita[s[4:]] for s in c['sources_with_ids'].split(';') if s.startswith('ITA:')]
  assert fed and all(r['state']=='GA' for r in fed)
  f=fed[0];assert f['schema_2_2_signal']=='P' and f['naics_code'][:3] in ('326','325')
  assert all(r['naics_code']==f['naics_code'] and street_key(r['street'])==street_key(f['street']) for r in fed)
  assert f['street'] and f['city'] and f['zip5']
  sid=f'SITE-{16100+idx:06d}';assert 16100+idx<=17999
  # A blank held street at the same parent/locality is an unresolved duplicate, not a free address.
  for s in oldsites:
   if s['site_id']==sid:continue
   assert not (s['state']=='GA' and street_key(s['street_address'])==street_key(f['street'])),(c['cluster_id'],s['site_id'])
   assert not (s['org_id']==oid and s['state']=='GA' and s['city'].casefold()==f['city'].casefold() and not s['street_address']),(c['cluster_id'],s['site_id'])
  ring='1' if f['naics_code'].startswith('326') else '2'
  ref=SOURCE+'#establishment_ID='+f['establishment_id']
  notes=f"CY2025 ITA establishment_ID {f['establishment_id']}; date_submitted {f['date_submitted']}; packet observed 2026-11-01, reviewed {DATE}. {v['reason']}"
  out['sites_GA.csv'].append(dict(site_id=sid,org_id=oid,site_name=org['legal_name']+' - '+f['city'],site_type='manufacturing_plant',street_address=f['street'],city=f['city'],state='GA',zip=f['zip5'],country='US',ring_primary=ring,naics_primary=f['naics_code'],naics_primary_source_type='government_filing',naics_confidence='medium',operating_status='active',sources=ref,verification_tier='C',last_verified=DATE,created_by=BY,notes=f"{c['cluster_id']}; Federal-only provisional C, operating evidence is CY2025 filing, not a 2026 observation. {notes}"))
  claims={
   'existence':f"ITA establishment {f['establishment_id']}: {f['establishment_name']}",
   'address':f"{f['street']}, {f['city']}, GA {f['zip5']}, US; county left unset",
   'scope':f"Provisional ring_primary {ring}, manufacturing_plant; employer-reported NAICS {f['naics_code']} (SCHEMA 2.2 Primary); federal-only C per CAMPAIGN convention",
   'code':f"naics_primary {f['naics_code']}; government_filing, medium confidence",
   'parent':f"org_id {oid} ({org['legal_name']}); filed company_name {f['company_name']}; establishment_name {f['establishment_name']}",
   'activity':f"Manufacturing filing for CY{f['year_filing_for']}; active provisional at that vintage",
   'liveness':f"CY{f['year_filing_for']} filing submitted {f['date_submitted']}; does not assert live operating check in 2026"}
  for claim,detail in claims.items():
   assert eid<=219999
   out['evidence_sites_GA.csv'].append(dict(evidence_id=f'EVD-{eid:06d}',record_table='sites',record_id=sid,claim_type=claim,claim_detail=detail,source_class='government_filing',source_ref=ref,observed_date='2026-11-01',tier_effect='supports_C',created_by=BY,notes=notes));eid+=1
  alloc.append(dict(cluster_id=c['cluster_id'],site_id=sid,org_id=oid,establishment_id=f['establishment_id']))
 # Preflight every file before any write; conflicting IDs fail closed.
 pending={}
 for name,rows in out.items():
  p=data/name;old=read(p);key='site_id' if name.startswith('sites_') else 'evidence_id';by={r[key]:r for r in old};header=list(old[0])
  for r in rows:
   if r[key] in by: assert by[r[key]]=={k:r.get(k,'') for k in header},('conflicting ID',r[key])
  pending[name]=[r for r in rows if r[key] not in by]
 if a.apply:
  for name,rows in pending.items():
   if rows:append_sorted(data/name,rows,'site_id' if name.startswith('sites_') else 'evidence_id')
 with open(H/'allocations.csv','w') as f:
  w=csv.DictWriter(f,fieldnames=list(alloc[0]),lineterminator='\n');w.writeheader();w.writerows(alloc)
 print(json.dumps({'worked_GA_clusters':len(vs),'verdicts':dict(Counter(v['verdict'] for v in vs)),'sites_C':len(alloc),'organizations_created':0,'evidence_rows':eid-201000,'pending_rows':{k:len(v) for k,v in pending.items()}}))
if __name__=='__main__':main()

FILE check.py
#!/usr/bin/env python3
"""Census the packet and blind-shuffle its 20 creates against banked ITA rows."""
import csv,hashlib,json,random,subprocess,sys,tempfile,shutil
from pathlib import Path
from collections import Counter
H=Path(__file__).resolve().parent;R=H.parents[1];sys.path.insert(0,str(R/'scripts'))
from atlas import load_tables,dedupe,name_key
from build_qcew_denominators import atlas_numerators
from build import read
vs=read(H/'verdicts.csv');cs=read(H/'input.csv');alloc=read(H/'allocations.csv')
assert len(vs)==len(cs)==len({r['cluster_id'] for r in vs})==147
assert {r['cluster_id'] for r in cs}=={r['cluster_id'] for r in vs}
assert len(alloc)==20 and len({r['site_id'] for r in alloc})==20
T=load_tables(R/'data');ita={r['establishment_id']:r for r in read(R/'tasks/osha-ita-2026-11-01/establishments.csv')}
sites={r['site_id']:r for r in T['sites'].rows};orgs={r['org_id']:r for r in T['organizations'].rows}
# Known-answer calibration includes the two registrant-name failures that motivated B-ALIAS.
for name,oid in [('Dart Container Corp','ORG-002441'),('New Wincup Holdings, Inc.','ORG-000984'),('Plastipak Packaging','ORG-001033')]:
 assert any(h['id']==oid for st in dedupe(T,name=name)['steps'] for h in st['hits']),(name,oid)
# Re-check source-first in a seeded blind order, without using verdict reasons as evidence.
rows=[];random.Random(7731).shuffle(alloc)
for a in alloc:
 f=ita[a['establishment_id']];s=sites[a['site_id']];o=orgs[s['org_id']]
 assert (s['street_address'],s['city'],s['zip'],s['naics_primary'])==(f['street'],f['city'],f['zip5'],f['naics_code'])
 assert s['verification_tier']=='C' and f['year_filing_for']=='2025'
 names={name_key(o['legal_name']),*(name_key(t.removesuffix(' (federal registrant name)').strip()) for t in o['trade_names'].split(';'))}
 # Mapei Wildwood is witnessed by its explicitly preserved registrant alias.
 assert name_key(f['company_name']) in names,(s['site_id'],f['company_name'],o['legal_name'])
 rows.append(dict(site_id=s['site_id'],establishment_id=f['establishment_id'],operator=o['legal_name'],result='PASS: held operator + physical address + filed NAICS; federal-only C'))
with (H/'blind_recheck.csv').open('w') as out:
 w=csv.DictWriter(out,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
# Byte idempotence, and a mutation: an occupied lane ID must fail without modifying any file.
files=[R/'data'/f for f in ['sites_GA.csv','evidence_sites_GA.csv','organizations_GA.csv','evidence_organizations_GA.csv']]
before=[hashlib.sha256(p.read_bytes()).hexdigest() for p in files]
subprocess.run([sys.executable,str(H/'build.py'),'--apply'],check=True,capture_output=True)
assert before==[hashlib.sha256(p.read_bytes()).hexdigest() for p in files]
with tempfile.TemporaryDirectory() as d:
 data=Path(d)/'data';shutil.copytree(R/'data',data)
 p=data/'sites_GA.csv';p.write_text(p.read_text().replace('SITE-016100,','SITE-016100,WRONG-',1))
 before_bad={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.csv')}
 r=subprocess.run([sys.executable,str(H/'build.py'),'--data-dir',str(data),'--apply'],capture_output=True)
 assert r.returncode!=0 and b'conflicting ID' in r.stderr
 assert before_bad=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.csv')}
# State strict numerator definition is reused from the official denominator builder.
now=atlas_numerators(str(R))[('GA','326')][1]
base=list(csv.DictReader(subprocess.check_output(['git','show','c71c0413f0054bc99bf341a8c75dff36609d24d7:data/sites_GA.csv'],text=True).splitlines()))
old=sum(r['naics_primary'].startswith('326') and r['operating_status'] in ('active','unknown') and r['verification_tier'] in ('A','B','C') for r in base)
q=next(r for r in read(R/'docs/denominators/qcew_state_polymer_2023_2024.csv') if r['area_fips']=='13000' and r['year']=='2023' and r['industry_code']=='326')
den=float(q['annual_avg_estabs'])
result=dict(worked_GA_clusters=147,sites_C=20,blind_recheck_passes=20,known_answer_passes=3,idempotence='PASS',conflicting_ID_mutation='PASS (fails before writes)',NAICS326_strict_sites_before=old,NAICS326_strict_sites_after=now,QCEW2023_private_establishments=den,strict_share_before=old/den,strict_share_after=now/den)
(H/'check_results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

FILE allocations.csv
cluster_id,site_id,org_id,establishment_id
LF-GA-00204,SITE-016100,ORG-002537,1492622
LF-GA-00199,SITE-016101,ORG-000984,1533149
LF-GA-00170,SITE-016102,ORG-002537,1476799
LF-GA-00303,SITE-016103,ORG-000003,1514964
LF-GA-00030,SITE-016104,ORG-000132,208892
LF-GA-00389,SITE-016105,ORG-004251,1071562
LF-GA-00259,SITE-016106,ORG-002281,1427307
LF-GA-00128,SITE-016107,ORG-001128,1082159
LF-GA-00332,SITE-016108,ORG-004300,519695
LF-GA-00362,SITE-016109,ORG-004300,1417323
LF-GA-00715,SITE-016110,ORG-004392,1466199
LF-GA-00812,SITE-016111,ORG-000132,345917
LF-GA-00757,SITE-016112,ORG-004995,1527500
LF-GA-00559,SITE-016113,ORG-000651,1000465
LF-GA-00719,SITE-016114,ORG-000690,1469237
LF-GA-00796,SITE-016115,ORG-000132,208942
LF-GA-00846,SITE-016116,ORG-001408,803419
LF-GA-00764,SITE-016117,ORG-004995,1527520
LF-GA-00657,SITE-016118,ORG-001124,1431239
LF-GA-00637,SITE-016119,ORG-007510,1336218

FILE blind_recheck.csv
site_id,establishment_id,operator,result
SITE-016110,1466199,"Habasit America, Inc.",PASS: held operator + physical address + filed NAICS; federal-only C
SITE-016116,803419,Altium Packaging,PASS: held operator + physical address + filed NAICS; federal-only C
SITE-016102,1476799,Pactiv Corporation,PASS: held operator + physical address + filed NAICS; federal-only C
SITE-016109,1417323,MAPEI Corporation,PASS: held operator + physical address + filed NAICS; federal-only C
SITE-016101,1533149,WinCup,PASS: held operator + physical address + filed NAICS; federal-only C
SITE-016103,1514964,The Goodyear Tire & Rubber Company,PASS: held operator + physical address + filed NAICS; federal-only C
SITE-016114,1469237,Axium Packaging Inc,PASS: held operator + physical address + filed NAICS; federal-only C
SITE-016104,208892,The Sherwin-Williams Company,PASS: held operator + physical address + filed NAICS; federal-only C
SITE-016113,1000465,"Advanced Drainage Systems, Inc.",PASS: held operator + physical address + filed NAICS; federal-only C
SITE-016100,1492622,Pactiv Corporation,PASS: held operator + physical address + filed NAICS; federal-only C
SITE-016117,1527520,CKS Packaging,PASS: held operator + physical address + filed NAICS; federal-only C
SITE-016105,1071562,GAF Materials Corporation,PASS: held operator + physical address + filed NAICS; federal-only C
SITE-016111,345917,The Sherwin-Williams Company,PASS: held operator + physical address + filed NAICS; federal-only C
SITE-016108,519695,MAPEI Corporation,PASS: held operator + physical address + filed NAICS; federal-only C
SITE-016112,1527500,CKS Packaging,PASS: held operator + physical address + filed NAICS; federal-only C
SITE-016107,1082159,"Storopack, Inc.",PASS: held operator + physical address + filed NAICS; federal-only C
SITE-016106,1427307,Penn Color Inc.,PASS: held operator + physical address + filed NAICS; federal-only C
SITE-016118,1431239,Standridge Color Corporation,PASS: held operator + physical address + filed NAICS; federal-only C
SITE-016115,208942,The Sherwin-Williams Company,PASS: held operator + physical address + filed NAICS; federal-only C
SITE-016119,1336218,"Crown USA, Inc.",PASS: held operator + physical address + filed NAICS; federal-only C

FILE check_results.json
{
  "worked_GA_clusters": 147,
  "sites_C": 20,
  "blind_recheck_passes": 20,
  "known_answer_passes": 3,
  "idempotence": "PASS",
  "conflicting_ID_mutation": "PASS (fails before writes)",
  "NAICS326_strict_sites_before": 62,
  "NAICS326_strict_sites_after": 74,
  "QCEW2023_private_establishments": 491.0,
  "strict_share_before": 0.12627291242362526,
  "strict_share_after": 0.15071283095723015
}
{"establishment_id": "803419", "ita_row_id": "2970038", "ein": "061056158", "ein_quality": "zero_padded", "company_name": "Altium Packaging", "establishment_name": "Altium Packaging - Fulton", "street": "6220 Duquesne Dr SW", "city": "Atlanta", "state": "GA", "zip5": "30336", "zip_as_filed": "30336", "naics_code": "326160", "naics_year": "2012", "industry_description": "Bottles, plastics, manufacturing", "family4": "3261", "scope_class": "core_P", "schema_2_2_ring": "Ring 1", "schema_2_2_signal": "P", "establishment_type": "1", "size_code": "22", "annual_average_employees": "128", "band_from_avg_employees": "100-249", "size_code_vs_avg_employees": "consistent", "hours_per_employee_screen": "ok", "reliability": "ok", "date_submitted": "2026-01-27", "amended_filing": "N", "year_filing_for": "2025", "ita_estabs_at_address": "1"}
{"establishment_id": "1527500", "ita_row_id": "3221890", "ein": "581645660", "ein_quality": "ok", "company_name": "CKS Packaging, Inc.", "establishment_name": "CKS Fisk", "street": "300 Fisk Drive", "city": "Atlanta", "state": "GA", "zip5": "30336", "zip_as_filed": "30336", "naics_code": "326160", "naics_year": "2022", "industry_description": "Manufacturing", "family4": "3261", "scope_class": "core_P", "schema_2_2_ring": "Ring 1", "schema_2_2_signal": "P", "establishment_type": "1", "size_code": "22", "annual_average_employees": "239", "band_from_avg_employees": "100-249", "size_code_vs_avg_employees": "consistent", "hours_per_employee_screen": "ok", "reliability": "ok", "date_submitted": "2026-03-01", "amended_filing": "N", "year_filing_for": "2025", "ita_estabs_at_address": "1"}
{"establishment_id": "1527520", "ita_row_id": "3221910", "ein": "581645660", "ein_quality": "ok", "company_name": "CKS Packaging, Inc.", "establishment_name": "CKS Purdue", "street": "6195 Purdue Drive", "city": "Atlanta", "state": "GA", "zip5": "30336", "zip_as_filed": "30336", "naics_code": "326160", "naics_year": "2022", "industry_description": "Manufacturing", "family4": "3261", "scope_class": "core_P", "schema_2_2_ring": "Ring 1", "schema_2_2_signal": "P", "establishment_type": "1", "size_code": "21", "annual_average_employees": "96", "band_from_avg_employees": "50-99", "size_code_vs_avg_employees": "consistent", "hours_per_employee_screen": "ok", "reliability": "ok", "date_submitted": "2026-03-01", "amended_filing": "N", "year_filing_for": "2025", "ita_estabs_at_address": "1"}
{"establishment_id": "1082159", "ita_row_id": "2916206", "ein": "042637050", "ein_quality": "zero_padded", "company_name": "Storopack, Inc.", "establishment_name": "Storopack, Inc. - Atlanta", "street": "6140 Duquesne Drive", "city": "Atlanta", "state": "GA", "zip5": "30336", "zip_as_filed": "30336", "naics_code": "326140", "naics_year": "2022", "industry_description": "Polystyrene foam packaging manufacturing", "family4": "3261", "scope_class": "core_P", "schema_2_2_ring": "Ring 1", "schema_2_2_signal": "P", "establishment_type": "1", "size_code": "1", "annual_average_employees": "13", "band_from_avg_employees": "10-49", "size_code_vs_avg_employees": "consistent", "hours_per_employee_screen": "ok", "reliability": "ok", "date_submitted": "2026-01-14", "amended_filing": "N", "year_filing_for": "2025", "ita_estabs_at_address": "1"}
{"establishment_id": "1417323", "ita_row_id": "2902463", "ein": "", "ein_quality": "blank", "company_name": "Mapei Corporation", "establishment_name": "Mapei-Calhoun", "street": "201 Enterprise Drive", "city": "Calhoun", "state": "GA", "zip5": "30701", "zip_as_filed": "30701", "naics_code": "325520", "naics_year": "2022", "industry_description": "Pastes, adhesive, manufacturing", "family4": "3255", "scope_class": "core_P", "schema_2_2_ring": "Ring 2", "schema_2_2_signal": "P", "establishment_type": "1", "size_code": "21", "annual_average_employees": "31", "band_from_avg_employees": "10-49", "size_code_vs_avg_employees": "consistent", "hours_per_employee_screen": "ok", "reliability": "ok", "date_submitted": "2026-01-08", "amended_filing": "N", "year_filing_for": "2025", "ita_estabs_at_address": "1"}
{"establishment_id": "1476799", "ita_row_id": "3086531", "ein": "362552989", "ein_quality": "ok", "company_name": "Pactiv LLC", "establishment_name": "Foodservice CONYERS", "street": "1501 Rockdale Industrial Blvd", "city": "Conyers", "state": "GA", "zip5": "30012", "zip_as_filed": "30012", "naics_code": "326199", "naics_year": "2022", "industry_description": "All Other Plastics Product Manufacturing", "family4": "3261", "scope_class": "core_P", "schema_2_2_ring": "Ring 1", "schema_2_2_signal": "P", "establishment_type": "1", "size_code": "22", "annual_average_employees": "184", "band_from_avg_employees": "100-249", "size_code_vs_avg_employees": "consistent", "hours_per_employee_screen": "ok", "reliability": "ok", "date_submitted": "2026-02-17", "amended_filing": "N", "year_filing_for": "2025", "ita_estabs_at_address": "1"}
{"establishment_id": "1492622", "ita_row_id": "3112229", "ein": "362552989", "ein_quality": "ok", "company_name": "Pactiv, LLC", "establishment_name": "Foodservice COVINGTON", "street": "8170 Alcovy Road NE", "city": "Covington", "state": "GA", "zip5": "30014", "zip_as_filed": "30014", "naics_code": "326140", "naics_year": "2022", "industry_description": "Polystyrene Foam Product Manufacturing", "family4": "3261", "scope_class": "core_P", "schema_2_2_ring": "Ring 1", "schema_2_2_signal": "P", "establishment_type": "1", "size_code": "3", "annual_average_employees": "447", "band_from_avg_employees": "250-499", "size_code_vs_avg_employees": "consistent", "hours_per_employee_screen": "ok", "reliability": "ok", "date_submitted": "2026-02-19", "amended_filing": "N", "year_filing_for": "2025", "ita_estabs_at_address": "1"}
{"establishment_id": "345917", "ita_row_id": "3062077", "ein": "340526850", "ein_quality": "ok", "company_name": "The Sherwin-Williams Company", "establishment_name": "USA GA Covington Plant", "street": "13129 Harland Drive, Covington, GA 30014", "city": "Covington", "state": "GA", "zip5": "30014", "zip_as_filed": "30014", "naics_code": "325510", "naics_year": "2012", "industry_description": "Paint and Coating Manufacturing", "family4": "3255", "scope_class": "core_P", "schema_2_2_ring": "Ring 2", "schema_2_2_signal": "P", "establishment_type": "1", "size_code": "22", "annual_average_employees": "150", "band_from_avg_employees": "100-249", "size_code_vs_avg_employees": "consistent", "hours_per_employee_screen": "ok", "reliability": "ok", "date_submitted": "2026-02-12", "amended_filing": "N", "year_filing_for": "2025", "ita_estabs_at_address": "1"}
{"establishment_id": "519695", "ita_row_id": "2902458", "ein": "", "ein_quality": "blank", "company_name": "Mapei", "establishment_name": "Mapei Corporation", "street": "2308 Dalton Industrial Court", "city": "Dalton", "state": "GA", "zip5": "30721", "zip_as_filed": "30721", "naics_code": "325520", "naics_year": "2012", "industry_description": "Adhesives (except asphalt, dental, gypsum base) manufacturing", "family4": "3255", "scope_class": "core_P", "schema_2_2_ring": "Ring 2", "schema_2_2_signal": "P", "establishment_type": "1", "size_code": "2", "annual_average_employees": "25", "band_from_avg_employees": "10-49", "size_code_vs_avg_employees": "consistent", "hours_per_employee_screen": "ok", "reliability": "ok", "date_submitted": "2026-01-08", "amended_filing": "N", "year_filing_for": "2025", "ita_estabs_at_address": "1"}
{"establishment_id": "1431239", "ita_row_id": "2924735", "ein": "581271080", "ein_quality": "ok", "company_name": "Standridge Color Corporation", "establishment_name": "Standridge Color Jasper", "street": "111 Stewart Parkway", "city": "Greensboro", "state": "GA", "zip5": "30642", "zip_as_filed": "30642", "naics_code": "325991", "naics_year": "2022", "industry_description": "Plastics resins, custom compounding of purchased", "family4": "3259", "scope_class": "core_P", "schema_2_2_ring": "Ring 2", "schema_2_2_signal": "P", "establishment_type": "1", "size_code": "21", "annual_average_employees": "48", "band_from_avg_employees": "10-49", "size_code_vs_avg_employees": "consistent", "hours_per_employee_screen": "ok", "reliability": "ok", "date_submitted": "2026-01-16", "amended_filing": "N", "year_filing_for": "2025", "ita_estabs_at_address": "1"}
{"establishment_id": "1469237", "ita_row_id": "3058661", "ein": "371646363", "ein_quality": "ok", "company_name": "Axium Packaging, LLC", "establishment_name": "Axium Packaging : Lawrenceville", "street": "1775 Macleod Dr.", "city": "Lawrenceville", "state": "GA", "zip5": "30043", "zip_as_filed": "30043", "naics_code": "326160", "naics_year": "2022", "industry_description": "Plastic Bottle Manufacturing", "family4": "3261", "scope_class": "core_P", "schema_2_2_ring": "Ring 1", "schema_2_2_signal": "P", "establishment_type": "1", "size_code": "22", "annual_average_employees": "167", "band_from_avg_employees": "100-249", "size_code_vs_avg_employees": "consistent", "hours_per_employee_screen": "ok", "reliability": "ok", "date_submitted": "2026-02-12", "amended_filing": "N", "year_filing_for": "2025", "ita_estabs_at_address": "1"}
{"establishment_id": "208892", "ita_row_id": "3062078", "ein": "340526850", "ein_quality": "ok", "company_name": "The Sherwin-Williams Company", "establishment_name": "USA GA Lawrenceville Plant", "street": "725 Raco Drive, Lawrenceville, GA 30045", "city": "Lawrenceville", "state": "GA", "zip5": "30045", "zip_as_filed": "30045", "naics_code": "325510", "naics_year": "2012", "industry_description": "Paint and Coating Manufacturing", "family4": "3255", "scope_class": "core_P", "schema_2_2_ring": "Ring 2", "schema_2_2_signal": "P", "establishment_type": "1", "size_code": "21", "annual_average_employees": "58", "band_from_avg_employees": "50-99", "size_code_vs_avg_employees": "consistent", "hours_per_employee_screen": "ok", "reliability": "ok", "date_submitted": "2026-02-12", "amended_filing": "N", "year_filing_for": "2025", "ita_estabs_at_address": "1"}
{"establishment_id": "208942", "ita_row_id": "3062079", "ein": "340526850", "ein_quality": "ok", "company_name": "The Sherwin-Williams Company", "establishment_name": "USA GA Morrow Plant", "street": "6795 Jonesboro Rd, Morrow, GA 30260", "city": "Morrow", "state": "GA", "zip5": "30260", "zip_as_filed": "30260", "naics_code": "325510", "naics_year": "2012", "industry_description": "Paint and Coating Manufacturing", "family4": "3255", "scope_class": "core_P", "schema_2_2_ring": "Ring 2", "schema_2_2_signal": "P", "establishment_type": "1", "size_code": "22", "annual_average_employees": "153", "band_from_avg_employees": "100-249", "size_code_vs_avg_employees": "consistent", "hours_per_employee_screen": "ok", "reliability": "ok", "date_submitted": "2026-02-12", "amended_filing": "N", "year_filing_for": "2025", "ita_estabs_at_address": "1"}
{"establishment_id": "1000465", "ita_row_id": "3110696", "ein": "510105665", "ein_quality": "ok", "company_name": "Advanced Drainage Systems", "establishment_name": "Perry", "street": "1005 Valley Drive", "city": "Perry", "state": "GA", "zip5": "31069", "zip_as_filed": "31069", "naics_code": "326122", "naics_year": "2012", "industry_description": "Plastic Pipe Manufacturing", "family4": "3261", "scope_class": "core_P", "schema_2_2_ring": "Ring 1", "schema_2_2_signal": "P", "establishment_type": "1", "size_code": "22", "annual_average_employees": "143", "band_from_avg_employees": "100-249", "size_code_vs_avg_employees": "consistent", "hours_per_employee_screen": "ok", "reliability": "ok", "date_submitted": "2026-02-19", "amended_filing": "N", "year_filing_for": "2025", "ita_estabs_at_address": "1"}
{"establishment_id": "1427307", "ita_row_id": "2940384", "ein": "", "ein_quality": "blank", "company_name": "Penn Color", "establishment_name": "Penn Color Ringgold", "street": "540 Hackett Mill Road", "city": "Ringgold", "state": "GA", "zip5": "30736", "zip_as_filed": "30736", "naics_code": "325510", "naics_year": "2022", "industry_description": "Industrial product finishes and coatings (i.e., paint) manufacturing", "family4": "3255", "scope_class": "core_P", "schema_2_2_ring": "Ring 2", "schema_2_2_signal": "P", "establishment_type": "1", "size_code": "21", "annual_average_employees": "37", "band_from_avg_employees": "10-49", "size_code_vs_avg_employees": "consistent", "hours_per_employee_screen": "ok", "reliability": "ok", "date_submitted": "2026-01-21", "amended_filing": "N", "year_filing_for": "2025", "ita_estabs_at_address": "1"}
{"establishment_id": "1514964", "ita_row_id": "3184348", "ein": "", "ein_quality": "blank", "company_name": "The Goodyear Tire and Rubber Company", "establishment_name": "The Goodyear Tire and Rubber Company", "street": "100 Business Center Drive", "city": "Stockbridge", "state": "GA", "zip5": "30281", "zip_as_filed": "30281", "naics_code": "326212", "naics_year": "2022", "industry_description": "Retreading tires", "family4": "3262", "scope_class": "core_P", "schema_2_2_ring": "Ring 1", "schema_2_2_signal": "P", "establishment_type": "1", "size_code": "21", "annual_average_employees": "54", "band_from_avg_employees": "50-99", "size_code_vs_avg_employees": "consistent", "hours_per_employee_screen": "ok", "reliability": "ok", "date_submitted": "2026-02-26", "amended_filing": "N", "year_filing_for": "2025", "ita_estabs_at_address": "1"}
{"establishment_id": "1533149", "ita_row_id": "3235747", "ein": "205897540", "ein_quality": "ok", "company_name": "New Wincup Holdings, Inc.", "establishment_name": "WinCup Stone Mountain", "street": "4640 Lewis Rd", "city": "Stone Mountain", "state": "GA", "zip5": "30083", "zip_as_filed": "30083", "naics_code": "326140", "naics_year": "2022", "industry_description": "Manufacture of foodservice packaging products including foam and paper cups, food containers, plastic lids, drinking straws", "family4": "3261", "scope_class": "core_P", "schema_2_2_ring": "Ring 1", "schema_2_2_signal": "P", "establishment_type": "1", "size_code": "22", "annual_average_employees": "180", "band_from_avg_employees": "100-249", "size_code_vs_avg_employees": "consistent", "hours_per_employee_screen": "ok", "reliability": "ok", "date_submitted": "2026-03-02", "amended_filing": "N", "year_filing_for": "2025", "ita_estabs_at_address": "1"}
{"establishment_id": "1466199", "ita_row_id": "3046444", "ein": "233059540", "ein_quality": "ok", "company_name": "Habasit America", "establishment_name": "Habasit America Suwanee", "street": "805 Satellite Blvd NW", "city": "Suwanee", "state": "GA", "zip5": "30024", "zip_as_filed": "30024", "naics_code": "326220", "naics_year": "2022", "industry_description": "Plastics and rubber belts and hoses (without fittings) manufacturing", "family4": "3262", "scope_class": "core_P", "schema_2_2_ring": "Ring 1", "schema_2_2_signal": "P", "establishment_type": "1", "size_code": "3", "annual_average_employees": "435", "band_from_avg_employees": "250-499", "size_code_vs_avg_employees": "consistent", "hours_per_employee_screen": "ok", "reliability": "ok", "date_submitted": "2026-02-27", "amended_filing": "N", "year_filing_for": "2025", "ita_estabs_at_address": "1"}
{"establishment_id": "1336218", "ita_row_id": "3124890", "ein": "582218656", "ein_quality": "ok", "company_name": "Crown USA, Inc.", "establishment_name": "Crown USA, Inc. Thomaston", "street": "600 Poplar Drive", "city": "Thomaston", "state": "GA", "zip5": "30286", "zip_as_filed": "30286", "naics_code": "325510", "naics_year": "2022", "industry_description": "Plastisol coating compounds manufacturing", "family4": "3255", "scope_class": "core_P", "schema_2_2_ring": "Ring 2", "schema_2_2_signal": "P", "establishment_type": "1", "size_code": "21", "annual_average_employees": "36", "band_from_avg_employees": "10-49", "size_code_vs_avg_employees": "consistent", "hours_per_employee_screen": "ok", "reliability": "ok", "date_submitted": "2026-02-23", "amended_filing": "N", "year_filing_for": "2025", "ita_estabs_at_address": "1"}
{"establishment_id": "1071562", "ita_row_id": "2947364", "ein": "223626208", "ein_quality": "ok", "company_name": "GAF", "establishment_name": "Valdosta", "street": "2100 Steeda Way", "city": "Valdosta", "state": "GA", "zip5": "31601", "zip_as_filed": "31601", "naics_code": "326130", "naics_year": "2022", "industry_description": "Sheet, laminated plastics (except flexible packaging), manufacturing", "family4": "3261", "scope_class": "core_P", "schema_2_2_ring": "Ring 1", "schema_2_2_signal": "P", "establishment_type": "1", "size_code": "21", "annual_average_employees": "25", "band_from_avg_employees": "10-49", "size_code_vs_avg_employees": "consistent", "hours_per_employee_screen": "ok", "reliability": "ok", "date_submitted": "2026-01-22", "amended_filing": "N", "year_filing_for": "2025", "ita_estabs_at_address": "1"}
