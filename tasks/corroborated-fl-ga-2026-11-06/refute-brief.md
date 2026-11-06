Attempt to REFUTE this Florida Atlas batch. End APPROVE or REFUTE, identifying concrete errors. Review only supplied packet; do not claim filesystem checks. Ground truth checks passed: validate.py 0 errors, exact census103, creates20 sites tier C, no org creates, alias1, evidence141, 20 source-first blind checks, idempotence and corrupt-ID failure before writes. Controller expressly permits inherited ITA at 2026-11-01 packet vintage without fresh download, notes retain dates. Federal-only C scope via existing CAMPAIGN convention is authorized; no B/A claims or own-page quotes. Assess parent links, addresses, code provenance, duplicate/campus risk, evidence completeness, baseline claims, idempotence. 83 holds mean uncompleted research, not absence. Supplied code and source-first check data below. No need to criticize not fetching internet: this source exception is explicit.

FILE README.md
# Florida CORROBORATED screening (L7), 2026-11-06

Acceptance: FL first, <=150 clusters; exact one-verdict census; no new parent when ownership unresolved; provisional federal-only C sites only under resolved held parents; ordered lane IDs; evidence append-only; idempotent fail-closed builder; validate 0 errors; source-first blind re-check of 20 creates; strict NAICS 326 numerator before/after. First user: campaign integrator reviewing this PR on 2026-11-06; non-use finding date 2026-11-13 (controller review).

103 FL CORROBORATED candidate establishment clusters screened: 20 VERIFIED new sites under 19 held parents; 83 STILL_UNCERTAIN holds; 0 REJECT, 0 DUPLICATE_OF, 0 new organizations. All 20 sites are tier C. 141 evidence rows appended (140 site, 1 organization); one held organization gets a federal registrant alias (MAPEI, B-ALIAS). No ring/scope vocabulary rulings. No inclusion_log entries: unresolved cases remain holds.

Sources: banked OSHA ITA CY2025 establishment rows, source URL https://www.osha.gov/sites/default/largefiles/ITA_300A_Summary_Data_2025_through_08-31-2026.csv. Controller thr_9i2c6byhcz explicitly granted use without fresh download at packet vintage 2026-11-01; notes preserve establishment_ID, date_submitted and review date. This supersedes brief section 4 only for the enumerated inherited federal packets. ECHO and Form5500 are discovery/corroboration only here. No own-page quotations or tier B claims. Source scope is provisional federal NAICS per CAMPAIGN's C convention, not independently established current product mix. No current operating-status claim beyond the federal vintage is warranted; active is provisional as documented on each new row.

Dedupe: `create_dedupe.json` records atlas.py CLI domain (when held), normalized-name, address, trade_names/notes searches. `dedupe.json` screens all 103 original clusters and variants. Generic Lakeland resolved from ITA company_name to Graham Packaging. Dart and WinCup known-answer hits prove the B-ALIAS examples remain held, not new parents. MAPEI registrant alias is explicitly marked. No missing county is guessed from city; counties remain blank. No blank HQ inferred for new parents because none are created. The 83 holds were screened for identity/site evidence, not exhaustively investigated or fetched six times. They remain uncompleted research, not negative findings.

Named checks (2026-11-06):
- `python3 scripts/validate.py`: PASS, zero errors.
- `python3 tasks/corroborated-fl-ga-2026-11-06/check.py`: PASS. 103/103 exact verdict census, 3 known answers, 20/20 shuffled source-first blind re-checks against the banked ITA records; exact rerun produces byte-identical data. Deliberate occupied-ID corruption fails before any write.
- `python3 tasks/corroborated-fl-ga-2026-11-06/build.py --apply`: idempotent, second run pending rows 0.
- No scripts/ edits, so scripts pytest gate does not apply.

Florida NAICS 326 strict sites (active/unknown, A/B/C, US) / QCEW 2023 private establishments: 37/798 = 4.6366% before, 53/798 = 6.6416% after. 16 of 20 creates carry 326; four carry 3255. This is a count ratio, not matched QCEW coverage. Baseline bd57a08. GA unchanged by this PR; continuation requires separate branch and PR.

Pre-pass backup: branch base bd57a08. Builder touches sites_FL, evidence_sites_FL, organizations_FL (alias only), evidence_organizations_FL. IDs SITE-016000–016019; EVD-200000–200140. No ORG IDs minted. No registry_links or derived qualifiers touched. Rebase by restoring current main data then re-running build.py (never hand-merge CSVs).

Cross-thread: L6 confirmed ECHO+F5500-only holds, ITA plant labels and missing ownership-status-2 rawcheck path; no shared scripts edited. L2 owns paced FRS REST; L7 made no FRS requests. DATA-ESTATE Documents/RAG layers unavailable on Mac (platform gaps), so no claim of exhaustive estate search; repository extracts suffice for this scoped pass.

## Refutes
Pending Codex + Grok deep refutes. Not completion-approved until both approve.

83 holds omitted for size; generic settling fact is primary operator/site-scope witness, with explicit campus holds Dart, Carpenter, TSE.

FILE build.py
#!/usr/bin/env python3
"""Apply the curated Florida federal-only C packet; reruns compare then skip exact rows."""
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
 assert len(vs)==len(cs)==103 and len({v['cluster_id'] for v in vs})==103
 assert set(cs)=={v['cluster_id'] for v in vs}
 assert set(v['verdict'] for v in vs)<={'VERIFIED','REJECT','STILL_UNCERTAIN','DUPLICATE_OF'}
 ita={r['establishment_id']:r for r in read(ROOT/'tasks/osha-ita-2026-11-01/establishments.csv')}
 orgs={r['org_id']:r for p in data.glob('organizations_*.csv') for r in read(p)}
 oldsites=[r for p in data.glob('sites_*.csv') for r in read(p)]
 out=defaultdict(list);eid=200000;alloc=[]
 for idx,v in enumerate(v for v in vs if v['verdict']=='VERIFIED'):
  c=cs[v['cluster_id']];oid=v['held_org_id'];org=orgs[oid];assert org['status']=='active' and not org['successor_org_id']
  fed=[ita[s[4:]] for s in c['sources_with_ids'].split(';') if s.startswith('ITA:')]
  assert fed and all(r['state']=='FL' for r in fed)
  f=fed[0];assert f['schema_2_2_signal']=='P' and f['naics_code'][:3] in ('326','325')
  assert all(r['naics_code']==f['naics_code'] and street_key(r['street'])==street_key(f['street']) for r in fed)
  assert f['street'] and f['city'] and f['zip5']
  sid=f'SITE-{16000+idx:06d}';assert 16000+idx<=17999
  # A blank held street at the same parent/locality is an unresolved duplicate, not a free address.
  for s in oldsites:
   if s['site_id']==sid:continue
   assert not (s['state']=='FL' and street_key(s['street_address'])==street_key(f['street'])),(c['cluster_id'],s['site_id'])
   assert not (s['org_id']==oid and s['state']=='FL' and s['city'].casefold()==f['city'].casefold() and not s['street_address']),(c['cluster_id'],s['site_id'])
  ring='1' if f['naics_code'].startswith('326') else '2'
  ref=SOURCE+'#establishment_ID='+f['establishment_id']
  notes=f"CY2025 ITA establishment_ID {f['establishment_id']}; date_submitted {f['date_submitted']}; packet observed 2026-11-01, reviewed {DATE}. {v['reason']}"
  out['sites_FL.csv'].append(dict(site_id=sid,org_id=oid,site_name=org['legal_name']+' - '+f['city'],site_type='manufacturing_plant',street_address=f['street'],city=f['city'],state='FL',zip=f['zip5'],country='US',ring_primary=ring,naics_primary=f['naics_code'],naics_primary_source_type='government_filing',naics_confidence='medium',operating_status='active',sources=ref,verification_tier='C',last_verified=DATE,created_by=BY,notes=f"{c['cluster_id']}; Federal-only provisional C, operating evidence is CY2025 filing, not a 2026 observation. {notes}"))
  claims={
   'existence':f"ITA establishment {f['establishment_id']}: {f['establishment_name']}",
   'address':f"{f['street']}, {f['city']}, FL {f['zip5']}, US; county left unset",
   'scope':f"Provisional ring_primary {ring}, manufacturing_plant; employer-reported NAICS {f['naics_code']} (SCHEMA 2.2 Primary); federal-only C per CAMPAIGN convention",
   'code':f"naics_primary {f['naics_code']}; government_filing, medium confidence",
   'parent':f"org_id {oid} ({org['legal_name']}); filed company_name {f['company_name']}; establishment_name {f['establishment_name']}",
   'activity':f"Manufacturing filing for CY{f['year_filing_for']}; active provisional at that vintage",
   'liveness':f"CY{f['year_filing_for']} filing submitted {f['date_submitted']}; does not assert live operating check in 2026"}
  for claim,detail in claims.items():
   assert eid<=219999
   out['evidence_sites_FL.csv'].append(dict(evidence_id=f'EVD-{eid:06d}',record_table='sites',record_id=sid,claim_type=claim,claim_detail=detail,source_class='government_filing',source_ref=ref,observed_date='2026-11-01',tier_effect='supports_C',created_by=BY,notes=notes));eid+=1
  alloc.append(dict(cluster_id=c['cluster_id'],site_id=sid,org_id=oid,establishment_id=f['establishment_id']))
 aliases={'ORG-004300':['Mapei - Wildwood']}
 for oid,names in aliases.items():
  shard=next(p.name for p in data.glob('organizations_*.csv') if any(r['org_id']==oid for r in read(p)))
  for name in sorted(set(names)):
   out['evidence_'+shard].append(dict(evidence_id=f'EVD-{eid:06d}',record_table='organizations',record_id=oid,claim_type='existence',claim_detail=f'trade_names registrant alias: {name}; B-ALIAS 2026-11-04',source_class='government_filing',source_ref=SOURCE,observed_date='2026-11-01',tier_effect='supports_C',created_by=BY,notes='ITA establishment_ID 1558286; date_submitted 2026-03-11; banked CY2025 packet; reviewed 2026-11-06'));eid+=1
 # Preflight every file before any write; conflicting IDs fail closed.
 pending={}
 for name,rows in out.items():
  p=data/name;old=read(p);key='site_id' if name.startswith('sites_') else 'evidence_id';by={r[key]:r for r in old};header=list(old[0])
  for r in rows:
   if r[key] in by: assert by[r[key]]=={k:r.get(k,'') for k in header},('conflicting ID',r[key])
  pending[name]=[r for r in rows if r[key] not in by]
 if a.apply:
  for oid,names in aliases.items():
   p=next(p for p in data.glob('organizations_*.csv') if any(r['org_id']==oid for r in read(p)))
   rows=read(p)
   for r in rows:
    if r['org_id']==oid:
     tokens=r['trade_names'].split('; ') if r['trade_names'] else []
     for n in sorted(set(names)):
      val=n+' (federal registrant name)'
      if val not in tokens:tokens.append(val)
     r['trade_names']='; '.join(tokens)
   with p.open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
  for name,rows in pending.items():
   if rows:append_sorted(data/name,rows,'site_id' if name.startswith('sites_') else 'evidence_id')
 with open(H/'allocations.csv','w') as f:
  w=csv.DictWriter(f,fieldnames=list(alloc[0]),lineterminator='\n');w.writeheader();w.writerows(alloc)
 print(json.dumps({'worked_FL_clusters':len(vs),'verdicts':dict(Counter(v['verdict'] for v in vs)),'sites_C':len(alloc),'organizations_created':0,'evidence_rows':eid-200000,'pending_rows':{k:len(v) for k,v in pending.items()}}))
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
assert len(vs)==len(cs)==len({r['cluster_id'] for r in vs})==103
assert {r['cluster_id'] for r in cs}=={r['cluster_id'] for r in vs}
assert len(alloc)==20 and len({r['site_id'] for r in alloc})==20
T=load_tables(R/'data');ita={r['establishment_id']:r for r in read(R/'tasks/osha-ita-2026-11-01/establishments.csv')}
sites={r['site_id']:r for r in T['sites'].rows};orgs={r['org_id']:r for r in T['organizations'].rows}
# Known-answer calibration includes the two registrant-name failures that motivated B-ALIAS.
for name,oid in [('Dart Container Corp','ORG-002441'),('WinCup','ORG-000984'),('Plastipak Packaging','ORG-001033')]:
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
files=[R/'data'/f for f in ['sites_FL.csv','evidence_sites_FL.csv','organizations_FL.csv','evidence_organizations_FL.csv']]
before=[hashlib.sha256(p.read_bytes()).hexdigest() for p in files]
subprocess.run([sys.executable,str(H/'build.py'),'--apply'],check=True,capture_output=True)
assert before==[hashlib.sha256(p.read_bytes()).hexdigest() for p in files]
with tempfile.TemporaryDirectory() as d:
 data=Path(d)/'data';shutil.copytree(R/'data',data)
 p=data/'sites_FL.csv';p.write_text(p.read_text().replace('SITE-016000,','SITE-016000,WRONG-',1))
 before_bad={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.csv')}
 r=subprocess.run([sys.executable,str(H/'build.py'),'--data-dir',str(data),'--apply'],capture_output=True)
 assert r.returncode!=0 and b'conflicting ID' in r.stderr
 assert before_bad=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.csv')}
# State strict numerator definition is reused from the official denominator builder.
now=atlas_numerators(str(R))[('FL','326')][1]
base=list(csv.DictReader(subprocess.check_output(['git','show','bd57a08:data/sites_FL.csv'],text=True).splitlines()))
old=sum(r['naics_primary'].startswith('326') and r['operating_status'] in ('active','unknown') and r['verification_tier'] in ('A','B','C') for r in base)
q=next(r for r in read(R/'docs/denominators/qcew_state_polymer_2023_2024.csv') if r['area_fips']=='12000' and r['year']=='2023' and r['industry_code']=='326')
den=float(q['annual_avg_estabs'])
result=dict(worked_FL_clusters=103,sites_C=20,blind_recheck_passes=20,known_answer_passes=3,idempotence='PASS',conflicting_ID_mutation='PASS (fails before writes)',NAICS326_strict_sites_before=old,NAICS326_strict_sites_after=now,QCEW2023_private_establishments=den,strict_share_before=old/den,strict_share_after=now/den)
(H/'check_results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

FILE allocations.csv
cluster_id,site_id,org_id,establishment_id
LF-FL-00292,SITE-016000,ORG-002521,818294
LF-FL-00028,SITE-016001,ORG-000132,204465
LF-FL-00217,SITE-016002,ORG-002643,1468400
LF-FL-00134,SITE-016003,ORG-001033,98122
LF-FL-00421,SITE-016004,ORG-004300,1558286
LF-FL-00236,SITE-016005,ORG-004311,1494484
LF-FL-00344,SITE-016006,ORG-000853,324275
LF-FL-00261,SITE-016007,ORG-001408,803548
LF-FL-00116,SITE-016008,ORG-001403,174687
LF-FL-00441,SITE-016009,ORG-000566,1519390
LF-FL-00014,SITE-016010,ORG-002349,1248403
LF-FL-00286,SITE-016011,ORG-004965,1454532
LF-FL-00379,SITE-016012,ORG-004516,1301745
LF-FL-00009,SITE-016013,ORG-002723,995961
LF-FL-00337,SITE-016014,ORG-007606,1440553
LF-FL-00209,SITE-016015,ORG-001128,1082299
LF-FL-00154,SITE-016016,ORG-001128,1082384
LF-FL-00582,SITE-016017,ORG-000259,1088099
LF-FL-00744,SITE-016018,ORG-004995,1527514
LF-FL-00835,SITE-016019,ORG-000905,958828

FILE blind_recheck.csv
site_id,establishment_id,operator,result
SITE-016010,1248403,Cork Industries Inc.,PASS: held operator + physical address + filed NAICS; federal-only C
SITE-016016,1082384,"Storopack, Inc.",PASS: held operator + physical address + filed NAICS; federal-only C
SITE-016002,1468400,Jeld-Wen,PASS: held operator + physical address + filed NAICS; federal-only C
SITE-016009,1519390,Sealed Air Corporation,PASS: held operator + physical address + filed NAICS; federal-only C
SITE-016001,204465,The Sherwin-Williams Company,PASS: held operator + physical address + filed NAICS; federal-only C
SITE-016003,98122,"Plastipak Packaging, Inc.",PASS: held operator + physical address + filed NAICS; federal-only C
SITE-016014,1440553,American Vinyl Company,PASS: held operator + physical address + filed NAICS; federal-only C
SITE-016004,1558286,MAPEI Corporation,PASS: held operator + physical address + filed NAICS; federal-only C
SITE-016013,995961,Amrize Building Envelope LLC,PASS: held operator + physical address + filed NAICS; federal-only C
SITE-016000,818294,Hilex Poly Co. LLC,PASS: held operator + physical address + filed NAICS; federal-only C
SITE-016017,1088099,CANTEX Inc.,PASS: held operator + physical address + filed NAICS; federal-only C
SITE-016005,1494484,Jacuzzi Brands LLC,PASS: held operator + physical address + filed NAICS; federal-only C
SITE-016011,1454532,"LATICRETE International, Inc.",PASS: held operator + physical address + filed NAICS; federal-only C
SITE-016008,174687,Graham Packaging Company,PASS: held operator + physical address + filed NAICS; federal-only C
SITE-016012,1301745,The Toro Company,PASS: held operator + physical address + filed NAICS; federal-only C
SITE-016007,803548,Altium Packaging,PASS: held operator + physical address + filed NAICS; federal-only C
SITE-016006,324275,"FXI, Inc.",PASS: held operator + physical address + filed NAICS; federal-only C
SITE-016018,1527514,CKS Packaging,PASS: held operator + physical address + filed NAICS; federal-only C
SITE-016015,1082299,"Storopack, Inc.",PASS: held operator + physical address + filed NAICS; federal-only C
SITE-016019,958828,"ISCO Industries, Inc.",PASS: held operator + physical address + filed NAICS; federal-only C
{"establishment_id": "1088099", "ita_row_id": "3016632", "ein": "133645159", "ein_quality": "ok", "company_name": "CANTEX INC.", "establishment_name": "Cantex", "street": "202 Progress Rd.", "city": "Auburndale", "state": "FL", "zip5": "33823", "zip_as_filed": "33823", "naics_code": "326122", "naics_year": "2022", "industry_description": "PVC pipe manufacturing", "family4": "3261", "scope_class": "core_P", "schema_2_2_ring": "Ring 1", "schema_2_2_signal": "P", "establishment_type": "1", "size_code": "22", "annual_average_employees": "191", "band_from_avg_employees": "100-249", "size_code_vs_avg_employees": "consistent", "hours_per_employee_screen": "ok", "reliability": "ok", "date_submitted": "2026-02-03", "amended_filing": "N", "year_filing_for": "2025", "ita_estabs_at_address": "2"}
{"establishment_id": "1440553", "ita_row_id": "2958838", "ein": "043624519", "ein_quality": "zero_padded", "company_name": "American Vinyl Company", "establishment_name": "Aurora Material Solutions - FLUS01PR", "street": "600 W 83rd St", "city": "Hialeah", "state": "FL", "zip5": "33014", "zip_as_filed": "33014", "naics_code": "326121", "naics_year": "2022", "industry_description": "Rod, nonrigid plastics, manufacturing", "family4": "3261", "scope_class": "core_P", "schema_2_2_ring": "Ring 1", "schema_2_2_signal": "P", "establishment_type": "1", "size_code": "21", "annual_average_employees": "36", "band_from_avg_employees": "10-49", "size_code_vs_avg_employees": "consistent", "hours_per_employee_screen": "ok", "reliability": "ok", "date_submitted": "2026-01-26", "amended_filing": "N", "year_filing_for": "2025", "ita_estabs_at_address": "1"}
{"establishment_id": "1248403", "ita_row_id": "3119483", "ein": "232135974", "ein_quality": "ok", "company_name": "Cork Industries, Inc.", "establishment_name": "Cork Industries, Inc.- Jacksonville, FL", "street": "5555 W Beaver Street", "city": "Jacksonville", "state": "FL", "zip5": "32254", "zip_as_filed": "32254", "naics_code": "325510", "naics_year": "2022", "industry_description": "Industrial product finishes and coatings (i.e., paint) manufacturing", "family4": "3255", "scope_class": "core_P", "schema_2_2_ring": "Ring 2", "schema_2_2_signal": "P", "establishment_type": "1", "size_code": "21", "annual_average_employees": "21", "band_from_avg_employees": "10-49", "size_code_vs_avg_employees": "consistent", "hours_per_employee_screen": "ok", "reliability": "ok", "date_submitted": "2026-02-20", "amended_filing": "N", "year_filing_for": "2025", "ita_estabs_at_address": "1"}
{"establishment_id": "818294", "ita_row_id": "3233744", "ein": "562379442", "ein_quality": "ok", "company_name": "Hilex Poly", "establishment_name": "Hilex Poly A NOVOLEX Company - Jacksonville", "street": "500 N Ellis Rd, Suite A", "city": "Jacksonville", "state": "FL", "zip5": "32254", "zip_as_filed": "32254", "naics_code": "326111", "naics_year": "2012", "industry_description": "Grocery bags, plastics film, single wall or multiwall, manufacturing", "family4": "3261", "scope_class": "core_P", "schema_2_2_ring": "Ring 1", "schema_2_2_signal": "P", "establishment_type": "1", "size_code": "22", "annual_average_employees": "145", "band_from_avg_employees": "100-249", "size_code_vs_avg_employees": "consistent", "hours_per_employee_screen": "ok", "reliability": "ok", "date_submitted": "2026-03-02", "amended_filing": "N", "year_filing_for": "2025", "ita_estabs_at_address": "1"}
{"establishment_id": "995961", "ita_row_id": "2980678", "ein": "205404918", "ein_quality": "ok", "company_name": "Amrize Building Envelope LLC", "establishment_name": "Jacksonville", "street": "6831 Stuart Ave", "city": "Jacksonville", "state": "FL", "zip5": "32254", "zip_as_filed": "32254", "naics_code": "326150", "naics_year": "2012", "industry_description": "Urethane foam products manufacturing", "family4": "3261", "scope_class": "core_P", "schema_2_2_ring": "Ring 1", "schema_2_2_signal": "P", "establishment_type": "1", "size_code": "21", "annual_average_employees": "44", "band_from_avg_employees": "10-49", "size_code_vs_avg_employees": "consistent", "hours_per_employee_screen": "ok", "reliability": "ok", "date_submitted": "2026-01-28", "amended_filing": "N", "year_filing_for": "2025", "ita_estabs_at_address": "1"}
{"establishment_id": "1494484", "ita_row_id": "3117748", "ein": "", "ein_quality": "blank", "company_name": "Jacuzzi Brands LLC", "establishment_name": "Duel Named Insureds Roto Ops, LLC; LMI IP, LLC", "street": "2452 Lake Emma Road", "city": "Lake Mary", "state": "FL", "zip5": "32746", "zip_as_filed": "32746", "naics_code": "326191", "naics_year": "2022", "industry_description": "Plumbing fixtures (e.g., shower stalls, toilets, urinals), plastics or fiberglass, manufacturing", "family4": "3261", "scope_class": "core_P", "schema_2_2_ring": "Ring 1", "schema_2_2_signal": "P", "establishment_type": "1", "size_code": "21", "annual_average_employees": "99", "band_from_avg_employees": "50-99", "size_code_vs_avg_employees": "consistent", "hours_per_employee_screen": "ok", "reliability": "ok", "date_submitted": "2026-02-20", "amended_filing": "N", "year_filing_for": "2025", "ita_estabs_at_address": "1"}
{"establishment_id": "174687", "ita_row_id": "3285083", "ein": "232378668", "ein_quality": "ok", "company_name": "Graham Packaging Company", "establishment_name": "Lakeland", "street": "1070 County Line Rd", "city": "Lakeland", "state": "FL", "zip5": "33815", "zip_as_filed": "33815", "naics_code": "326160", "naics_year": "2012", "industry_description": "Bottles, plastics, manufacturing", "family4": "3261", "scope_class": "core_P", "schema_2_2_ring": "Ring 1", "schema_2_2_signal": "P", "establishment_type": "1", "size_code": "21", "annual_average_employees": "42", "band_from_avg_employees": "10-49", "size_code_vs_avg_employees": "consistent", "hours_per_employee_screen": "ok", "reliability": "ok", "date_submitted": "2026-03-24", "amended_filing": "N", "year_filing_for": "2025", "ita_estabs_at_address": "1"}
{"establishment_id": "1519390", "ita_row_id": "3196869", "ein": "", "ein_quality": "blank", "company_name": "Sealed Air", "establishment_name": "Sealed Air", "street": "5135 Drane Field Road", "city": "Lakeland", "state": "FL", "zip5": "33811", "zip_as_filed": "33811", "naics_code": "326112", "naics_year": "2022", "industry_description": "Packaging film, plastics, single-web or multiweb, manufacturing", "family4": "3261", "scope_class": "core_P", "schema_2_2_ring": "Ring 1", "schema_2_2_signal": "P", "establishment_type": "1", "size_code": "1", "annual_average_employees": "17", "band_from_avg_employees": "10-49", "size_code_vs_avg_employees": "consistent", "hours_per_employee_screen": "ok", "reliability": "ok", "date_submitted": "2026-02-27", "amended_filing": "N", "year_filing_for": "2025", "ita_estabs_at_address": "1"}
{"establishment_id": "1082299", "ita_row_id": "2916708", "ein": "042637050", "ein_quality": "zero_padded", "company_name": "Storopack, Inc.", "establishment_name": "Storopack, Inc. - Medley", "street": "11825 NW 100th Road Suite 4", "city": "Medley", "state": "FL", "zip5": "33178", "zip_as_filed": "33178", "naics_code": "326140", "naics_year": "2022", "industry_description": "Polystyrene foam packaging manufacturing", "family4": "3261", "scope_class": "core_P", "schema_2_2_ring": "Ring 1", "schema_2_2_signal": "P", "establishment_type": "1", "size_code": "1", "annual_average_employees": "13", "band_from_avg_employees": "10-49", "size_code_vs_avg_employees": "consistent", "hours_per_employee_screen": "ok", "reliability": "ok", "date_submitted": "2026-01-14", "amended_filing": "N", "year_filing_for": "2025", "ita_estabs_at_address": "1"}
{"establishment_id": "324275", "ita_row_id": "3003005", "ein": "270283137", "ein_quality": "ok", "company_name": "FXI, Inc.", "establishment_name": "FXI, Inc. - Miami", "street": "11000 NW 32nd Avenue", "city": "Miami", "state": "FL", "zip5": "33167", "zip_as_filed": "33167", "naics_code": "326150", "naics_year": "2012", "industry_description": "Urethane foam products manufacturing", "family4": "3261", "scope_class": "core_P", "schema_2_2_ring": "Ring 1", "schema_2_2_signal": "P", "establishment_type": "1", "size_code": "21", "annual_average_employees": "65", "band_from_avg_employees": "50-99", "size_code_vs_avg_employees": "consistent", "hours_per_employee_screen": "ok", "reliability": "ok", "date_submitted": "2026-02-01", "amended_filing": "N", "year_filing_for": "2025", "ita_estabs_at_address": "1"}
{"establishment_id": "958828", "ita_row_id": "2999243", "ein": "", "ein_quality": "blank", "company_name": "ISCO Industries, Inc", "establishment_name": "ISCO Industries, Inc - Mulberry", "street": "460 Fife Road", "city": "Mulberry", "state": "FL", "zip5": "33850", "zip_as_filed": "33850", "naics_code": "326191", "naics_year": "2012", "industry_description": "Chemical toilets, plastics, manufacturing", "family4": "3261", "scope_class": "core_P", "schema_2_2_ring": "Ring 1", "schema_2_2_signal": "P", "establishment_type": "1", "size_code": "1", "annual_average_employees": "24", "band_from_avg_employees": "10-49", "size_code_vs_avg_employees": "inconsistent", "hours_per_employee_screen": "ok", "reliability": "review", "date_submitted": "2026-01-30", "amended_filing": "N", "year_filing_for": "2025", "ita_estabs_at_address": "1"}
{"establishment_id": "1527514", "ita_row_id": "3221904", "ein": "581645660", "ein_quality": "ok", "company_name": "CKS Packaging, Inc.", "establishment_name": "CKS Michigan", "street": "333 W. Michigan St", "city": "Orlando", "state": "FL", "zip5": "32806", "zip_as_filed": "32806", "naics_code": "326160", "naics_year": "2022", "industry_description": "Manufacturing", "family4": "3261", "scope_class": "core_P", "schema_2_2_ring": "Ring 1", "schema_2_2_signal": "P", "establishment_type": "1", "size_code": "22", "annual_average_employees": "125", "band_from_avg_employees": "100-249", "size_code_vs_avg_employees": "consistent", "hours_per_employee_screen": "ok", "reliability": "ok", "date_submitted": "2026-03-01", "amended_filing": "N", "year_filing_for": "2025", "ita_estabs_at_address": "1"}
{"establishment_id": "204465", "ita_row_id": "3062076", "ein": "340526850", "ein_quality": "ok", "company_name": "The Sherwin-Williams Company", "establishment_name": "USA FL Orlando Plant", "street": "2150 W Sandlake Rd, Orlando, FL 32809", "city": "Orlando", "state": "FL", "zip5": "32809", "zip_as_filed": "32809", "naics_code": "325510", "naics_year": "2012", "industry_description": "Paint and Coating Manufacturing", "family4": "3255", "scope_class": "core_P", "schema_2_2_ring": "Ring 2", "schema_2_2_signal": "P", "establishment_type": "1", "size_code": "22", "annual_average_employees": "163", "band_from_avg_employees": "100-249", "size_code_vs_avg_employees": "consistent", "hours_per_employee_screen": "ok", "reliability": "ok", "date_submitted": "2026-02-12", "amended_filing": "N", "year_filing_for": "2025", "ita_estabs_at_address": "1"}
{"establishment_id": "98122", "ita_row_id": "2924596", "ein": "382418126", "ein_quality": "ok", "company_name": "Plastipak Packaging, Inc.", "establishment_name": "Plastipak- Plant City", "street": "4211 Amberjack Blvd.", "city": "Plant City", "state": "FL", "zip5": "33566", "zip_as_filed": "33566", "naics_code": "326160", "naics_year": "2012", "industry_description": "Bottles, plastics, manufacturing", "family4": "3261", "scope_class": "core_P", "schema_2_2_ring": "Ring 1", "schema_2_2_signal": "P", "establishment_type": "1", "size_code": "22", "annual_average_employees": "147", "band_from_avg_employees": "100-249", "size_code_vs_avg_employees": "consistent", "hours_per_employee_screen": "ok", "reliability": "ok", "date_submitted": "2026-01-16", "amended_filing": "N", "year_filing_for": "2025", "ita_estabs_at_address": "1"}
{"establishment_id": "1301745", "ita_row_id": "2985991", "ein": "410580470", "ein_quality": "ok", "company_name": "The Toro Company", "establishment_name": "SANFORD", "street": "3000 MELLONVILLE AVE, BLDG 422", "city": "SANFORD", "state": "FL", "zip5": "32773", "zip_as_filed": "32773", "naics_code": "326122", "naics_year": "2022", "industry_description": "Fittings, rigid plastics pipe, manufacturing", "family4": "3261", "scope_class": "core_P", "schema_2_2_ring": "Ring 1", "schema_2_2_signal": "P", "establishment_type": "1", "size_code": "21", "annual_average_employees": "42", "band_from_avg_employees": "10-49", "size_code_vs_avg_employees": "consistent", "hours_per_employee_screen": "ok", "reliability": "ok", "date_submitted": "2026-01-29", "amended_filing": "N", "year_filing_for": "2025", "ita_estabs_at_address": "1"}
{"establishment_id": "1082384", "ita_row_id": "2916819", "ein": "042637050", "ein_quality": "zero_padded", "company_name": "Storopack, Inc.", "establishment_name": "Storopack, Inc. - Tampa", "street": "4724 Transport Drive", "city": "Tampa", "state": "FL", "zip5": "33605", "zip_as_filed": "33605", "naics_code": "326140", "naics_year": "2022", "industry_description": "Polystyrene foam packaging manufacturing", "family4": "3261", "scope_class": "core_P", "schema_2_2_ring": "Ring 1", "schema_2_2_signal": "P", "establishment_type": "1", "size_code": "1", "annual_average_employees": "7", "band_from_avg_employees": "1-9", "size_code_vs_avg_employees": "consistent", "hours_per_employee_screen": "ok", "reliability": "ok", "date_submitted": "2026-01-14", "amended_filing": "N", "year_filing_for": "2025", "ita_estabs_at_address": "1"}
{"establishment_id": "1468400", "ita_row_id": "3055785", "ein": "930496342", "ein_quality": "ok", "company_name": "Jeld-Wen, Inc", "establishment_name": "North America Venice", "street": "355 Center Court", "city": "Venice", "state": "FL", "zip5": "34285", "zip_as_filed": "34285", "naics_code": "326199", "naics_year": "2022", "industry_description": "All Other Plastics Product Manufacturing", "family4": "3261", "scope_class": "core_P", "schema_2_2_ring": "Ring 1", "schema_2_2_signal": "P", "establishment_type": "1", "size_code": "22", "annual_average_employees": "176", "band_from_avg_employees": "100-249", "size_code_vs_avg_employees": "consistent", "hours_per_employee_screen": "ok", "reliability": "ok", "date_submitted": "2026-02-11", "amended_filing": "N", "year_filing_for": "2025", "ita_estabs_at_address": "1"}
{"establishment_id": "1454532", "ita_row_id": "3009430", "ein": "060774147", "ein_quality": "zero_padded", "company_name": "LATICRETE International, Inc.", "establishment_name": "LATICRETE International Inc - West Palm Beach", "street": "6769 White Drive", "city": "West Palm Beach", "state": "FL", "zip5": "33407", "zip_as_filed": "33407", "naics_code": "325520", "naics_year": "2022", "industry_description": "Manufacture of building materials", "family4": "3255", "scope_class": "core_P", "schema_2_2_ring": "Ring 2", "schema_2_2_signal": "P", "establishment_type": "1", "size_code": "21", "annual_average_employees": "24", "band_from_avg_employees": "10-49", "size_code_vs_avg_employees": "consistent", "hours_per_employee_screen": "ok", "reliability": "ok", "date_submitted": "2026-02-02", "amended_filing": "N", "year_filing_for": "2025", "ita_estabs_at_address": "1"}
{"establishment_id": "1558286", "ita_row_id": "3277616", "ein": "331817133", "ein_quality": "ok", "company_name": "Mapei - Wildwood", "establishment_name": "Mapei - Wildwood", "street": "4405 Northeast 82nd Ave.", "city": "Wildwood", "state": "FL", "zip5": "34785", "zip_as_filed": "34785", "naics_code": "325520", "naics_year": "2022", "industry_description": "Tile adhesives manufacturing", "family4": "3255", "scope_class": "core_P", "schema_2_2_ring": "Ring 2", "schema_2_2_signal": "P", "establishment_type": "1", "size_code": "21", "annual_average_employees": "69", "band_from_avg_employees": "50-99", "size_code_vs_avg_employees": "consistent", "hours_per_employee_screen": "ok", "reliability": "ok", "date_submitted": "2026-03-11", "amended_filing": "N", "year_filing_for": "2025", "ita_estabs_at_address": "1"}
{"establishment_id": "803548", "ita_row_id": "2972169", "ein": "061056158", "ein_quality": "zero_padded", "company_name": "Altium Packaging", "establishment_name": "Altium Packaging - Zephyrhills", "street": "4330 20th St.", "city": "Zephyrhills", "state": "FL", "zip5": "33540", "zip_as_filed": "33540", "naics_code": "326160", "naics_year": "2012", "industry_description": "Bottles, plastics, manufacturing", "family4": "3261", "scope_class": "core_P", "schema_2_2_ring": "Ring 1", "schema_2_2_signal": "P", "establishment_type": "1", "size_code": "21", "annual_average_employees": "31", "band_from_avg_employees": "10-49", "size_code_vs_avg_employees": "consistent", "hours_per_employee_screen": "ok", "reliability": "ok", "date_submitted": "2026-01-27", "amended_filing": "N", "year_filing_for": "2025", "ita_estabs_at_address": "1"}
