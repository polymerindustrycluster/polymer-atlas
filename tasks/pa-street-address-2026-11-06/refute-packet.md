Adversarial completion review — PA continuation, L2. Return VERDICT: APPROVE or REFUTE with demonstrated findings; tools read-only. Scope7 existing activePA street fills from raw own operator pages, append7 supports_A evidence; tiers A5/B2 unchanged. No county/county_source/ZIP/status/tier/registry changes. Frozen24blank activePA sites →7VERIFIED/17STILL_UNCERTAIN. Coverage750/774→757/774 (96.90→97.80%). Known-answer parser cases3 pass; wrongcity/PO-box and phone-prefix injections rejected. check.py7fills, only street/sources, idempotence and injected conflicting street refusal pass. Fresh own-page audit census7/7 zero errors. validate.py0errors. IDs155000–159999 controller allocation, 7 sparse IDs within155004–155021. No federal exact/strong matches for these24blanks; website-only. ExecutoolZIP13485 vsfresh16505 held; OilCreek notesZIP conflict alsoheld, no ZIP changes. Root/contact pages bounded; quote only exact address block (no personaldata). Potential defects: phoneprefix pollution, wrongsitefooter/city, parsing onepage's multipleaddress blocks, notes conflict missed, county contradiction, exactquotes not present, idempotence/rebase overwrite.
Read all code and source rows below; full artifacts are on branchagent/codex/pa-street-address. Controller clerk route supersedes council-only gate; two-family verdicts required before ready. Checks: python3 tasks/pa-street-address-2026-11-06/check.py; python3 scripts/validate.py; build.py --audit forfreshownpagecensus. Do not mutate current checkout.

FILE fetch.py
"""Raw-check PA operator pages; only complete physical street/city/state/ZIP blocks become candidates."""
import concurrent.futures,csv,hashlib,json,re,subprocess
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin,urlparse
TASK=Path(__file__).resolve().parent;ROOT=TASK.parents[1]
def read(p):return list(csv.DictReader(open(p)))
def write(p,rows):
 with open(p,'w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
class Page(HTMLParser):
 def __init__(self):super().__init__();self.parts=[];self.links=[];self.skip=0
 def handle_starttag(self,t,a):
  if t in ('script','style'):self.skip+=1
  if t=='a':self.links.extend(v for k,v in a if k=='href' and re.search('contact|location',v,re.I))
 def handle_endtag(self,t):
  if t in ('script','style'):self.skip=max(0,self.skip-1)
 def handle_data(self,s):
  if not self.skip and s.strip():self.parts.append(s.strip())
def fetch(u):
 r=subprocess.run(['curl','--fail','-L','--max-time','25','-A','Mozilla/5.0',u],capture_output=True)
 if r.returncode:raise ValueError('transport '+str(r.returncode))
 p=Page();p.feed(r.stdout.decode(errors='replace'));return ' '.join(p.parts),p.links,hashlib.sha256(r.stdout).hexdigest()
def extract(text,city):
 suffix=r'(?:Street|St\.?|Road|Rd\.?|Drive|Dr\.?|Avenue|Ave\.?|Boulevard|Blvd\.?|Lane|Ln\.?|Parkway|Pkwy\.?|Place|Pl\.?|Way|Court|Ct\.?|Route\s+\d+)'
 pattern=r'\b(\d{1,6}\s+(?:(?!\d+\b)[A-Za-z0-9.#/-]+\s+){0,8}?'+suffix+r')[, •|]*\s*'+re.escape(city)+r'\s*[, •|]*\s*(?:PA|Pennsylvania)\s*[, •|]*\s*(\d{5}(?:-\d{4})?)\b'
 text=' '.join(text.split())
 return [(m[1].strip(),m[2],m[0]) for m in re.finditer(pattern,text,re.I)]
def known():
 cases=[('2935 W 17th St, Erie, PA 16505','Erie','2935 W 17th St','16505'),('7 Headley Pl, Fallsington PA 19054','Fallsington','7 Headley Pl','19054'),('21 Lebanon Parkway, Lebanon, PA 17042','Lebanon','21 Lebanon Parkway','17042')]
 for text,city,street,zip_ in cases:
  assert extract(text,city)==[(street,zip_,text)]
  assert not extract(text,'WRONG CITY') and not extract('PO Box 123, '+city+', PA '+zip_,city)
 assert extract('Phone 2166 1 Lark Ave., Leola, PA 17540','Leola')==[('1 Lark Ave.','17540','1 Lark Ave., Leola, PA 17540')]
 assert extract('2970 Molding Division Main Office 1040 Maple Avenue Lake City, PA 16423','Lake City')==[('1040 Maple Avenue','16423','1040 Maple Avenue Lake City, PA 16423')]
 print('PASS: 3 known address blocks; injected wrong-city and PO-box cases rejected')
def main():
 known();sites=read(TASK/'baseline_blank.csv');orgs={r['org_id']:r for p in (ROOT/'data').glob('organizations_*.csv') for r in read(p)}
 def work(s):
  base=orgs[s['org_id']]['website']
  if not base and s['site_id'] in ('SITE-002834','SITE-002838'):base=re.search(r'https?://[^; ]+',s['sources'])[0]
  base=base if '://' in base or not base else 'https://'+base
  # Sources already on the site can supply an own-domain URL when corporate website is blank.
  todo=[base] if base else [];seen=[];out=[]
  for _ in range(4):
   if not todo:break
   u=todo.pop(0)
   if u in seen:continue
   seen.append(u)
   try:
    text,links,sha=fetch(u)
    for street,zip_,quote in extract(text,s['city']):
     out.append(dict(site_id=s['site_id'],street_address=street,source_zip=zip_,quote=quote,url=u,sha256=sha,checked_urls=';'.join(seen)))
    todo.extend(v for v in (urljoin(u,x) for x in links) if urlparse(v).hostname==urlparse(base).hostname and v not in seen and v not in todo)
   except Exception:pass
  return out or [dict(site_id=s['site_id'],street_address='',source_zip='',quote='',url=base,sha256='',checked_urls=';'.join(seen))]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:out=[r for group in pool.map(work,sites) for r in group]
 write(TASK/'rawchecks.csv',out);print('rawcheck rows',len(out),'sites with address',len({r['site_id'] for r in out if r['street_address']}))
if __name__=='__main__':main()

FILE build.py
"""Apply raw operator-page streets to the frozen 24-site PA blank cohort; no other geography changes."""
import csv,json,re,sys
from pathlib import Path
TASK=Path(__file__).resolve().parent;ROOT=TASK.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from shard_io import append_sorted
from fetch import extract,read,write,fetch,known

def key(s):
 aliases={'STREET':'ST','WEST':'W','EAST':'E','NORTH':'N','SOUTH':'S','ROAD':'RD','DRIVE':'DR','AVENUE':'AVE','PARKWAY':'PKWY','PLACE':'PL'}
 return ' '.join(aliases.get(t,t) for t in re.findall('[A-Z0-9]+',s.upper()))

def run(apply=False):
 baseline=read(TASK/'baseline_blank.csv');checks=read(TASK/'rawchecks.csv');sites=read(ROOT/'data/sites_PA.csv');byid={r['site_id']:r for r in sites}
 ev=[];verdicts=[]
 for i,s in enumerate(sorted(baseline,key=lambda r:r['site_id'])):
  rows=[r for r in checks if r['site_id']==s['site_id'] and r['street_address']];why=[]
  if not rows:why.append('need own-operator physical street page for this city; none raw-checked within cap')
  if len({key(r['street_address']) for r in rows})>1:why.append('raw source address blocks disagree')
  if any(s['zip'] and s['zip'][:5]!=r['source_zip'][:5] for r in rows):why.append('existing ZIP conflicts with own-page ZIP; geography correction is outside this pass')
  if any(not re.match(r'^\d+\s+[A-Za-z]',r['street_address']) or not re.search('[A-Za-z]',r['street_address']) for r in rows):why.append('ambiguous physical street')
  # Notes are leads only, but a differing complete address blocks application.
  noted=extract(s['notes'],s['city'])
  if rows and any(key(x[0])!=key(rows[0]['street_address']) for x in noted):why.append('notes address differs from raw page; adjudication required')
  row=dict(site_id=s['site_id'],verdict='STILL_UNCERTAIN' if why else 'VERIFIED',street_address=rows[0]['street_address'] if rows else '',reason='; '.join(why),evidence_id='')
  if not why:
   r=rows[0];eid=f'EVD-{155000+i:06d}';row['evidence_id']=eid
   ev.append(dict(evidence_id=eid,record_table='sites',record_id=s['site_id'],claim_type='address',claim_detail=f"street_address {r['street_address']}, {s['city']}, PA; own-page ZIP {r['source_zip']}",
      source_class='own_site',source_ref=r['url'],observed_date='2026-11-06',tier_effect='supports_A',created_by='atlas-L2-pa-address',
      notes=f"Raw checked 2026-11-06; SHA-256 {r['sha256']}; quote: {r['quote']}. County, county_source, ZIP and record tier unchanged."))
  verdicts.append(row)
 assert len(verdicts)==len({r['site_id'] for r in verdicts})==24
 write(TASK/'verdicts.csv',verdicts);write(TASK/'holds.csv',[r for r in verdicts if r['verdict']!='VERIFIED']);write(TASK/'evidence.csv',ev)
 if apply:
  (TASK/'backups').mkdir(exist_ok=True)
  for name in ('sites_PA.csv','evidence_sites_PA.csv'):
   p=ROOT/'data'/name;b=TASK/'backups'/name
   if not b.exists():b.write_bytes(p.read_bytes())
  existing={r['evidence_id']:r for r in read(ROOT/'data/evidence_sites_PA.csv')};new=[];eb={r['record_id']:r for r in ev}
  for v in verdicts:
   if v['verdict']!='VERIFIED':continue
   s=byid[v['site_id']];old=next(r for r in baseline if r['site_id']==s['site_id'])
   for field in ('org_id','city','zip','county','county_source','verification_tier','operating_status'):assert s[field]==old[field],(s['site_id'],field)
   assert s['street_address'] in ('',v['street_address']),'new street conflict'
   s['street_address']=v['street_address'];e=eb[s['site_id']]
   if e['source_ref'] not in s['sources']:s['sources']+='; '+e['source_ref']
   if e['evidence_id'] in existing:assert existing[e['evidence_id']]==e,'evidence collision'
   else:new.append(e)
  if new:append_sorted(ROOT/'data/evidence_sites_PA.csv',new,'evidence_id')
  write(ROOT/'data/sites_PA.csv',sites)
 summary=dict(active_sites=774,before_filled=750,fills=len(ev),after_filled=750+len(ev),holds=24-len(ev));(TASK/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary)

def audit():
 ev=read(TASK/'evidence.csv');out=[]
 for e in ev:
  error=''
  try:
   text,_,sha=fetch(e['source_ref']);quote=e['notes'].split('; quote: ')[1].removesuffix('. County, county_source, ZIP and record tier unchanged.')
   assert ' '.join(quote.split()) in ' '.join(text.split()),'quote missing'
  except Exception as ex:error=str(ex)
  out.append(dict(site_id=e['record_id'],source_ref=e['source_ref'],result='PASS' if not error else 'FAIL',error=error))
 write(TASK/'audit.csv',out);assert len(out)==len(ev) and not any(r['error'] for r in out),out
 print(f'Own-page fresh-refetch census: {len(out)}/{len(ev)}, zero errors')

if __name__=='__main__':
 if '--known' in sys.argv:known()
 elif '--audit' in sys.argv:audit()
 else:run('--apply' in sys.argv)

FILE check.py
"""Named L2 mutation-boundary and idempotence check; no canonical writes."""
import contextlib
import hashlib
import io
import shutil
import tempfile
from pathlib import Path
import build

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    root=build.ROOT
    with tempfile.TemporaryDirectory() as tmp:
        build.ROOT=Path(tmp);(build.ROOT/'data').mkdir()
        for name in ('sites_PA.csv','evidence_sites_PA.csv'):
            shutil.copyfile(root/'data'/name,build.ROOT/'data'/name)
        frozen={r['site_id']:r for r in build.read(build.TASK/'baseline_blank.csv')}
        base=build.read(build.ROOT/'data/sites_PA.csv')
        base=[frozen.get(r['site_id'],r) for r in base]
        build.write(build.ROOT/'data/sites_PA.csv',base)
        ev=build.read(build.ROOT/'data/evidence_sites_PA.csv')
        build.write(build.ROOT/'data/evidence_sites_PA.csv',[r for r in ev if r['created_by']!='atlas-L2-pa-address'])
        before=build.read(build.ROOT/'data/sites_PA.csv')
        with contextlib.redirect_stdout(io.StringIO()): build.run(apply=True)
        after=build.read(build.ROOT/'data/sites_PA.csv')
        changed=0
        assert len(before)==len(after)
        for a,b in zip(before,after):
            fields={k for k in a if a[k]!=b[k]}
            assert fields <= {'street_address','sources'},(a['site_id'],fields)
            if fields:
                changed+=1
                assert not a['street_address'] and b['street_address'] and a['operating_status']=='active'
        paths=list((build.ROOT/'data').glob('*.csv'));hashes=[digest(p) for p in paths]
        with contextlib.redirect_stdout(io.StringIO()):build.run(apply=True)
        assert hashes==[digest(p) for p in paths],'not idempotent'
        # Inject a new street conflict: reapplication must refuse instead of overwriting.
        target=next(r for a,r in zip(before,after) if not a['street_address'] and r['street_address'])
        target['street_address']='999 WRONG ROAD';build.write(build.ROOT/'data/sites_PA.csv',after)
        try:
            with contextlib.redirect_stdout(io.StringIO()):build.run(apply=True)
        except AssertionError:pass
        else:raise AssertionError('injected street conflict was silently overwritten')
        print(f'PASS: {changed} fills; only street/sources change; second build byte-identical; injected street conflict refused')
    build.ROOT=root

if __name__=='__main__':main()

FILE README.md
# Pennsylvania street addresses — L2 continuation, 2026-11-06

Second branch/PR: agent/codex/pa-street-address. Controller allocated EVD-155000–159999 on 2026-11-06; Ohio retains EVD-150000–154999. Preparation only until the Ohio PR is open.

Baseline main bd57a08: 774 active Pennsylvania site rows, 750 streets (96.90%), 24 blanks. No blank active PA site has a site-keyed registry link. All held ITA matches for these 24 sites are moderate/weak, and all held ECHO matches are weak; none is admissible under the lane's exact/strong federal requirement. One existing address evidence row is city-grain only. Operator pages are the remaining admissible route.

Acceptance: existing active PA site rows only; street + sources and append-only address evidence; no county/county_source/ZIP/status/tier changes. Conflicting city, existing ZIP or notes street → HOLD. Raw website quotes only. All accepted fills will be re-fetched as a census (maximum 24 rows, so a 30-row sample is impossible). Validator zero errors; builder idempotence and mutation-boundary check; two-family deep refute before second PR. First user Atlas integrator, review date 2026-11-06; non-use finding date 2026-11-13.


Final pass (base c71c041, PR128 merged while Ohio stayed on its own branch): **7 active Pennsylvania site street fills**, seven own_site address evidence rows (supports_A), sparse IDs EVD-155004–155021. Record tiers unchanged: A5/B2. Active PA street coverage **750/774 (96.90%) → 757/774 (97.80%)**. No site/org creates, registry links, inclusion-log calls or other column edits beyond street_address/sources.

The parser initially admitted preceding phone fragments as part of two address candidates (e.g. `2166 1 Lark Ave`). Before any application it was tightened to reject bare numeric tokens inside a street body, and two injected phone-fragment cases were added to the known-answer check. The resulting candidates are exact raw-page substrings. Quotes remain address blocks only; no personal contacts or whole pages are retained.

Checks:
- `python3 tasks/pa-street-address-2026-11-06/build.py --known`: 3 known address blocks passed (Erie, Fallsington, Lebanon); injected wrong city/PO-box and two phone-fragment cases rejected/correctly parsed. These are parser known-answer fixtures drawn from held addresses, not claims those sites have been freshly verified.
- `python3 tasks/pa-street-address-2026-11-06/check.py`: PASS 7 fills; only street/sources change, second build byte-identical; injected pre-existing conflicting street refused.
- `python3 tasks/pa-street-address-2026-11-06/build.py --audit`: **7/7 accepted fill rows freshly re-fetched, zero missing quotes/errors**. This is the complete accepted-fill census, exceeding a proportional sample because only 7 fills exist.
- `python3 scripts/validate.py`: OK — validation passed, **0 errors**. No scripts/ files changed; the Ohio pass ran the full 221-test unittest suite (one existing skip), and this pass uses its own builder check.

Holds (unit: active PA blank site rows; verdicts in holds.csv):

| Site | Operator site | Settling fact |
|---|---|---|
| SITE-002807 | Adept Corp. - York | need own-operator physical street page for this city; none raw-checked within cap |
| SITE-002817 | Covington Plastic Molding Inc. - York | need own-operator physical street page for this city; none raw-checked within cap |
| SITE-002822 | Executool Precision Tooling Inc. - Erie | existing ZIP conflicts with own-page ZIP; geography correction is outside this pass |
| SITE-002824 | Gemini Plastics Inc. - Fallsington | need own-operator physical street page for this city; none raw-checked within cap |
| SITE-002829 | M&Q Packaging LLC - Schuylkill Haven | need own-operator physical street page for this city; none raw-checked within cap |
| SITE-002831 | Millet Plastics Inc. - Lebanon | need own-operator physical street page for this city; none raw-checked within cap |
| SITE-002838 | Oil Creek Plastics Inc. - Titusville | need own-operator physical street page for this city; none raw-checked within cap |
| SITE-002845 | Retal PA LLC - Donora | need own-operator physical street page for this city; none raw-checked within cap |
| SITE-002848 | Viking Plastics Inc - Corry | need own-operator physical street page for this city; none raw-checked within cap |
| SITE-002852 | Graham Packaging Company - Lancaster | need own-operator physical street page for this city; none raw-checked within cap |
| SITE-002854 | Quality Plastics LLC - Erie | need own-operator physical street page for this city; none raw-checked within cap |
| SITE-003584 | Valex Group Headquarters | need own-operator physical street page for this city; none raw-checked within cap |
| SITE-003723 | Zurn PEX Erie plant | need own-operator physical street page for this city; none raw-checked within cap |
| SITE-004115 | Acmos, Inc. — Wexford office | need own-operator physical street page for this city; none raw-checked within cap |
| SITE-004272 | Technical Process & Engineering - Lehighton HQ plant | need own-operator physical street page for this city; none raw-checked within cap |
| SITE-004558 | Norac Additives - Ambler (HQ and development lab) | need own-operator physical street page for this city; none raw-checked within cap |
| SITE-004560 | Sudarshan — Fairless Hills | need own-operator physical street page for this city; none raw-checked within cap |

SITE-002822 Executool is held because recorded ZIP13485 conflicts with own-page ZIP16505; 13485 also appears in the notes as an ISO certificate number, but correcting ZIP is outside this address-only lane. SITE-002838 Oil Creek carries ZIP45619 while its notes state16354 (and house45619); its current website fetch failed, so the notes are a correction lead only, never a street witness. No ZIP is changed. Other holds need an own-page physical address at the recorded city; unavailable or unparsable pages never prove absence.

Controller's 05:55 clerk route explicitly supersedes the brief's council-only publication order: draft PR first, then designated Codex/Grok clerks. Both technical verdicts pending. Pre-pass backups remain local and ignored.

FILE baseline_blank.csv
site_id,org_id,site_name,site_type,city,state,zip,county,ring_primary,naics_primary,naics_primary_source_type,naics_confidence,processes,processes_other_note,materials,materials_other_note,markets_served,employee_band_site,operating_status,sources,verification_tier,last_verified,created_by,notes,street_address,latitude,longitude,geocode_precision,county_source,site_group_id,country
SITE-002807,ORG-002732,Adept Corp. - York,manufacturing_plant,York,PA,,York,1,,,,assembly_secondary_ops;extrusion_profile;mold_tool_making,,abs;acrylic_pmma;polyethylene_pe;polypropylene_pp;pvc,,construction_building_products,,active,https://www.adeptcorp.com/about-us/; Phase B WP2 verdict [ADEPT CORP.] (staging working/phase-b/wp2_pa_company_verdicts.csv),A,2026-10-29,pass-13 integrator (spaghetti subagent),"Created 2026-10-29 in integration pass 13 from the Phase B WP2 verdict for seed [ADEPT CORP.] (staging working/phase-b/wp2_pa_company_verdicts.csv). Basis: Own site About: rigid plastic extrusion (PVC/PP/ASA/ABS) plus stampings and machinery from 62,000 sq ft York PA facility expanded 2007 Street address not stated in the verdict evidence. Settling fact: the plant street address from a primary source.",,,,,,,US
SITE-002817,ORG-002741,Covington Plastic Molding Inc. - York,manufacturing_plant,York,PA,,York,1,,,,,,,,,,active,https://www.covingtonplasticmolding.com/about.html; Phase B WP2 verdict [COVINGTON PLASTIC MOLDING INC.] (staging working/phase-b/wp2_pa_company_verdicts.csv),A,2026-10-29,pass-13 integrator (spaghetti subagent),"Created 2026-10-29 in integration pass 13 from the Phase B WP2 verdict for seed [COVINGTON PLASTIC MOLDING INC.] (staging working/phase-b/wp2_pa_company_verdicts.csv). Basis: Own About page: in-house injection molding facility at 10 S Bolton St, New Oxford PA, plus high-production facility added in York PA in 2019 Street address not stated in the verdict evidence. Settling fact: the plant street address from a primary source.",,,,,,,US
SITE-002822,ORG-002745,Executool Precision Tooling Inc. - Erie,manufacturing_plant,Erie,PA,13485,Erie,1,,,,injection_molding;mold_tool_making;tooling_repair_maintenance,,,,automotive_unspecified;electronics_electrical;medical_healthcare_general,,active,https://www.executool.net/; Phase B WP2 verdict [EXECUTOOL PRECISION TOOLING INC.] (staging working/phase-b/wp2_pa_company_verdicts.csv),A,2026-10-29,pass-13 integrator (spaghetti subagent),"Created 2026-10-29 in integration pass 13 from the Phase B WP2 verdict for seed [EXECUTOOL PRECISION TOOLING INC.] (staging working/phase-b/wp2_pa_company_verdicts.csv). Basis: Own site: Executool Precision Tooling, 2727 W 16th St, Erie PA - injection mold tooling and molding (medical, ISO 13485) Street address not stated in the verdict evidence. Settling fact: the plant street address from a primary source.",,42.097807450197,-80.139337463563,address_interpolated,,,US
SITE-002824,ORG-002747,Gemini Plastics Inc. - Fallsington,manufacturing_plant,Fallsington,PA,,Bucks,1,,,,injection_molding;tooling_repair_maintenance,,,,consumer_goods_housewares;electronics_electrical;general_industrial,,active,http://www.geminiplastics.net; Phase B WP2 verdict [GEMINI PLASTICS INC.] (staging working/phase-b/wp2_pa_company_verdicts.csv),A,2026-10-29,pass-13 integrator (spaghetti subagent),"Created 2026-10-29 in integration pass 13 from the Phase B WP2 verdict for seed [GEMINI PLASTICS INC.] (staging working/phase-b/wp2_pa_company_verdicts.csv). Basis: Own site: Gemini Plastics Inc, 7 Headley Pl, Fallsington PA - family-owned custom injection molder of thermoplastics since 1969 (40,000 sq ft, 23 molding machines per vendor case study) Street address not stated in the verdict evidence. Settling fact: the plant street address from a primary source.",,40.190748854236,-74.814763786164,address_interpolated,,,US
SITE-002825,ORG-002748,Georgeko Industries Inc. - Erie,manufacturing_plant,Erie,PA,,Erie,1,,,,assembly_secondary_ops;injection_molding;insert_overmolding;printing_decorating_plastics,,,,automotive_unspecified;construction_building_products;consumer_goods_housewares;medical_healthcare_general,,active,https://www.georgeko.com/GeorgeKo-Production-Manufacturing.htm; Phase B WP2 verdict [GEORGEKO INDUSTRIES INC.] (staging working/phase-b/wp2_pa_company_verdicts.csv),A,2026-10-29,pass-13 integrator (spaghetti subagent),"Created 2026-10-29 in integration pass 13 from the Phase B WP2 verdict for seed [GEORGEKO INDUSTRIES INC.] (staging working/phase-b/wp2_pa_company_verdicts.csv). Basis: Own site opened in full and current: plastics manufacturing facility with 11 injection molding machines 50-943 tons, insert/overmolding, 30,000 sq ft building, Erie PA (4861 W 23rd St) Street address not stated in the verdict evidence. Settling fact: the plant street address from a primary source.",,42.071907316445,-80.185992639104,address_interpolated,,,US
SITE-002829,ORG-002752,M&Q Packaging LLC - Schuylkill Haven,manufacturing_plant,Schuylkill Haven,PA,17972,Schuylkill,1,,,,,,nylon_pa,,aerospace_defense;food_processing_foodservice;medical_healthcare_general,,active,https://mqplastics.com/; Phase B WP2 verdict [M&Q PACKAGING LLC] (staging working/phase-b/wp2_pa_company_verdicts.csv),A,2026-10-29,pass-13 integrator (spaghetti subagent),"Created 2026-10-29 in integration pass 13 from the Phase B WP2 verdict for seed [M&Q PACKAGING LLC] (staging working/phase-b/wp2_pa_company_verdicts.csv). Basis: Own site opened in full: manufacturer of high-temperature nylon packaging films; own contact page gives a manufacturing address on Earl Street, Schuylkill Haven, PA 17972 and own news page states film is manufactured in its Schuylkill Haven PA facility. Street address not stated in the verdict evidence. Settling fact: the plant street address from a primary source.",,,,,,,US
SITE-002831,ORG-002754,Millet Plastics Inc. - Lebanon,manufacturing_plant,Lebanon,PA,17042,Lebanon,1,,,,blow_molding_extrusion,,,,packaging_consumer;packaging_food_beverage;packaging_industrial,,active,https://milletplastics-group.com/; Phase B WP2 verdict [MILLET PLASTICS INC.] (staging working/phase-b/wp2_pa_company_verdicts.csv),A,2026-10-29,pass-13 integrator (spaghetti subagent),"Created 2026-10-29 in integration pass 13 from the Phase B WP2 verdict for seed [MILLET PLASTICS INC.] (staging working/phase-b/wp2_pa_company_verdicts.csv). Basis: Group own site opened in full lists a production site: Millet Plastics, 21 Lebanon Parkway, Lebanon, PA 17042, USA, for technical parts and packaging, technologies extrusion blow molding and decoration. Street address not stated in the verdict evidence. Settling fact: the plant street address from a primary source. CERT-SITE (own site, observed 2026-11-01): iso_9001.",,,,,,,US
SITE-002833,ORG-002756,Munot Plastics Inc. - Erie,manufacturing_plant,Erie,PA,16505,Erie,1,,,,mold_tool_making;thermoforming_unspecified,,abs;pet_petg;polyethylene_pe;polypropylene_pp;polystyrene_ps_hips;pvc;recycled_content_pcr_pir,,medical_healthcare_general;packaging_consumer;packaging_food_beverage,,active,https://www.munotplastics.com/; Phase B WP2 verdict [MUNOT PLASTICS INC.] (staging working/phase-b/wp2_pa_company_verdicts.csv),A,2026-10-29,pass-13 integrator (spaghetti subagent),"Created 2026-10-29 in integration pass 13 from the Phase B WP2 verdict for seed [MUNOT PLASTICS INC.] (staging working/phase-b/wp2_pa_company_verdicts.csv). Basis: Own site opened in full: custom thermoformed packaging (blisters, clamshells, trays) since 1963; footer: Munot Plastics Inc, 2935 W 17th St, Erie, PA 16505. Street address not stated in the verdict evidence. Settling fact: the plant street address from a primary source.",,42.095499658728,-80.143707305577,address_interpolated,,,US
SITE-002834,ORG-002757,National Polymers - Charleroi,manufacturing_plant,Charleroi,PA,,Washington,1,,,,,,,,,,active,https://nationalpolymers.com/about; Phase B WP2 verdict [National Polymers] (staging working/phase-b/wp2_pa_company_verdicts.csv),A,2026-10-29,pass-13 integrator (spaghetti subagent),"Created 2026-10-29 in integration pass 13 from the Phase B WP2 verdict for seed [National Polymers] (staging working/phase-b/wp2_pa_company_verdicts.csv). Basis: Own about page opened in full: National Polymers Inc. (NPI) is a private-label manufacturer of concrete restoration, protective flooring and roofing products, located in the Speers Industrial Park in Charleroi, PA. Street address not stated in the verdict evidence. Settling fact: the plant street address from a primary source.",,,,,,,US
SITE-002838,ORG-002761,Oil Creek Plastics Inc. - Titusville,manufacturing_plant,Titusville,PA,45619,Crawford,1,,,,,,,,,,active,https://oilcreekplastics.com/; Phase B WP2 verdict [OIL CREEK PLASTICS INC.] (staging working/phase-b/wp2_pa_company_verdicts.csv),B,2026-10-29,pass-13 integrator (spaghetti subagent),"Created 2026-10-29 in integration pass 13 from the Phase B WP2 verdict for seed [OIL CREEK PLASTICS INC.] (staging working/phase-b/wp2_pa_company_verdicts.csv). Basis: Own-domain terms page (effective 2024-12-16) gives Oil Creek Plastics, 45619 State Rte 27, Titusville, PA 16354; NSF certified listing shows PE pipe products from the Titusville PA facility. Street address not stated in the verdict evidence. Settling fact: the plant street address from a primary source.",,,,,,,US
SITE-002840,ORG-002763,Polymar - Leola,manufacturing_plant,Leola,PA,17540,Lancaster,1,,,,injection_molding,,abs;acetal_pom;nylon_pa;pet_petg;polycarbonate_pc;polypropylene_pp,,aerospace_defense;automotive_unspecified;construction_building_products;electronics_electrical;medical_healthcare_general,,active,https://polymar-asm.com/; Phase B WP2 verdict [POLYMAR] (staging working/phase-b/wp2_pa_company_verdicts.csv),B,2026-10-29,pass-13 integrator (spaghetti subagent),"Created 2026-10-29 in integration pass 13 from the Phase B WP2 verdict for seed [POLYMAR] (staging working/phase-b/wp2_pa_company_verdicts.csv). Basis: Own site content: expert plastic injection molding, 1 Lark Ave., Leola, PA 17540; own services page describes custom plastic injection molding services in Leola, PA. Street address not stated in the verdict evidence. Settling fact: the plant street address from a primary source.",,40.087380102212,-76.155600548139,address_interpolated,,,US
SITE-002845,ORG-002768,Retal PA LLC - Donora,manufacturing_plant,Donora,PA,,Washington,1,,,,injection_molding,,pet_petg,,packaging_food_beverage,,active,https://retalgroup.com/; Phase B WP2 verdict [RETAL PA LLC] (staging working/phase-b/wp2_pa_company_verdicts.csv),B,2026-10-29,pass-13 integrator (spaghetti subagent),"Created 2026-10-29 in integration pass 13 from the Phase B WP2 verdict for seed [RETAL PA LLC] (staging working/phase-b/wp2_pa_company_verdicts.csv). Basis: Parent RETAL Group own site: RETAL PA is well-established in Donora, PA, creating and manufacturing PET preforms; group reporting cites 1.247 billion preforms produced at RETAL PA in 2022. Street address not stated in the verdict evidence. Settling fact: the plant street address from a primary source.",,,,,,,US
SITE-002848,ORG-002771,Viking Plastics Inc - Corry,manufacturing_plant,Corry,PA,16407,Erie,1,,,,injection_molding,,,,,,active,https://vikingplastics.com/; Phase B WP2 verdict [Viking Plastics Inc] (staging working/phase-b/wp2_pa_company_verdicts.csv),B,2026-10-29,pass-13 integrator (spaghetti subagent),"Created 2026-10-29 in integration pass 13 from the Phase B WP2 verdict for seed [Viking Plastics Inc] (staging working/phase-b/wp2_pa_company_verdicts.csv). Basis: Own site: injection molding and value-added assembly provider with locations in Corry, PA, Louisville, KY and Jeffersonville, IN; HQ 1 Viking St, Corry, PA 16407; own news page on the Hoffmann Family of Companies purchase describes the company as headquartered in Corry, Pennsylvania. Street address not stated in the verdict evidence. Settling fact: the plant street address from a primary source. CERT-SITE (own site, observed 2026-11-01): iatf_16949; iso_14001.",,41.922871643892,-79.630041888753,address_interpolated,,,US
SITE-002852,ORG-001403,Graham Packaging Company - Lancaster,manufacturing_plant,Lancaster,PA,,Lancaster,1,,,,,,,,,,active,Phase B WP2 verdict [GRAHAM PACKAGING CO. LP] (staging working/phase-b/wp2_pa_company_verdicts.csv),C,2026-10-29,pass-13 integrator (spaghetti subagent),Created 2026-10-29 in integration pass 13 from the Phase B WP2 verdict for seed [GRAHAM PACKAGING CO. LP] (staging working/phase-b/wp2_pa_company_verdicts.csv). Basis:  Street address not stated in the verdict evidence. Settling fact: the plant street address from a primary source.,,,,,,,US
SITE-002853,ORG-000974,"Multi-Plastics, Inc. - Hazleton",manufacturing_plant,Hazleton,PA,,Luzerne,1,,,,extrusion_sheet;polymerization,,,,,,active,https://multi-plastics.com/; Phase B WP2 verdict [MULTI-PLASTICS EXTRUSIONS INC.] (staging working/phase-b/wp2_pa_company_verdicts.csv),A,2026-10-29,pass-13 integrator (spaghetti subagent),"Created 2026-10-29 in integration pass 13 from the Phase B WP2 verdict for seed [MULTI-PLASTICS EXTRUSIONS INC.] (staging working/phase-b/wp2_pa_company_verdicts.csv). Basis: Own site opened in full: polymerization and film extrusion at its Hazleton, PA facility; corroborated by a PA DEP permit document naming Multi Plastics Extrusions Inc / Hazleton. Street address not stated in the verdict evidence. Settling fact: the plant street address from a primary source.",,,,,,,US
SITE-002854,ORG-001877,Quality Plastics LLC - Erie,manufacturing_plant,Erie,PA,,Erie,1,,,,,,,,,,active,Phase B WP2 verdict [Quality Plastics] (staging working/phase-b/wp2_pa_company_verdicts.csv),C,2026-10-29,pass-13 integrator (spaghetti subagent),Created 2026-10-29 in integration pass 13 from the Phase B WP2 verdict for seed [Quality Plastics] (staging working/phase-b/wp2_pa_company_verdicts.csv). Basis:  Street address not stated in the verdict evidence. Settling fact: the plant street address from a primary source. Evidence-thin attach: the source row carries no evidence_url/tier (fetches_used=0); linkage rests on the WP2 packet disposition plus the exact name/city match. Tier C recorded.,,,,,,,US
SITE-002859,ORG-002304,Engineered Plastics LLC - Lake City,manufacturing_plant,Lake City,PA,,Erie,,,,,,,,,,,active,"verification wave 12 verdict W12-PA-0370 (staging working/verification-wave-12/wave12_verdicts_merged.csv, 2026-10-29)",A,2026-10-29,pass-13 integrator (spaghetti subagent),"Created 2026-10-29 in integration pass 13 under the prep's WP2_REVIEW presumption (row_dispositions WP2::ENGINEERED PLASTICS|LAKE CITY): the Phase B evidence describes the Lake City molding facility, distinct from the wave-12 creation's Erie site, so it lands as a second site. Street address not stated in the verdict evidence. Settling fact: the plant street address from a primary source. Basis: Own site opened in full: custom thermoplastic injection molder with three locations in NW Pennsylvania; company text states injection molding takes place in its Lake City facility (ISO 9001, 27 presses 55-850 tons), assembly in Erie, plus post-industrial recycling",,,,,,,US
SITE-003584,ORG-003143,Valex Group Headquarters,hq_only,Pittsburgh,PA,15238,Allegheny,3,,,,,,natural_rubber_nr;synthetic rubbers;latex;carbon black (distributed),,,,active,"ThomasNet distributor listing; Rubber Division, ACS corporate member roster",C,2026-10-30,pass-18 integrator 2 (spaghetti subagent),Created 2026-10-30 in integration pass 18 from verification wave 2 site design NEW:A01-31-S1 (org NEW:A01-31). ,,,,,,,US
SITE-003723,ORG-003283,Zurn PEX Erie plant,manufacturing_plant,Erie,PA,,Erie,1,,,,extrusion_unspecified;crosslinking,,PEX (crosslinked polyethylene),,,,active,"ASPE Pipeline (Zurn Elkay press release): PEX pipe manufacturing facilities in Erie, Pennsylvania and Commerce, Texas",B,2026-10-30,pass-18 integrator 2 (spaghetti subagent),Created 2026-10-30 in integration pass 18 from verification wave 2 site design NEW:A06-10-S2 (org NEW:A06-10). Street address not established within cap; city-level site only,,,,,,,US
SITE-004115,ORG-003691,"Acmos, Inc. — Wexford office",hq_only,Wexford,PA,15090,Allegheny,3,,,,release agents / cleaners / lubricants for molding,,polyurethane_pu;elastomers_rubber;composites_unspecified;thermoplastics,,,,active,Parent site acmos.com; ThomasNet,C,2026-10-30,pass-18 integrator 2 (spaghetti subagent),Created 2026-10-30 in integration pass 18 from verification wave 2 site design NEW:A20-37-S1 (org NEW:A20-37). Street address not established; US production historically via contract manufacturing per Manufacturing In Focus.,,,,,,,US
SITE-004272,ORG-003825,Technical Process & Engineering - Lehighton HQ plant,hq_and_plant,Lehighton,PA,18235,Carbon,3,,,,extruder and downstream equipment manufacturing,,extruders; mixers; compounding equipment,,,,active,Thomasnet category listing; Crunchbase profile,B,2026-10-30,pass-18 integrator 2 (spaghetti subagent),Created 2026-10-30 in integration pass 18 from verification wave 2 site design NEW:A26-44-S1 (org NEW:A26-44). Street address not captured,,,,,,,US
SITE-004299,ORG-003849,Audia Elastomers - Washington HQ,hq_only,Washington,PA,,Washington,2,,,,elastomer development; compounding (group campus),,thermoplastic_elastomers_tpe_tpu;TPEE,,,,active,https://audiaelastomers.com/news_posts/audia-elastomers-unveils-audiaflex-family-of-sustainable-thermoplastic-elastomers-tpes,B,2026-10-30,pass-18 integrator 2 (spaghetti subagent),Created 2026-10-30 in integration pass 18 from verification wave 2 site design NEW:A28-09-S1 (org NEW:A28-09). Street address not captured in legs - gap,,,,,,,US
SITE-004558,ORG-004016,Norac Additives - Ambler (HQ and development lab),hq_only,Ambler,PA,,Montgomery,2,325199,researcher_inferred,medium,research and development,,plastic additives,,,unknown,active,https://www.peter-greven.de/en/news-details/relocation-of-norac-additives-headquarters-and-development-lab,B,2026-10-30,pass-20 integrator (spaghetti subagent),Created 2026-10-30 in integration pass 20 from candidate-queue wave Q01-Q02 site design NEW:D-97-S2 (org NEW:D-97). City grain only.,,,,,,,US
SITE-004560,ORG-004018,Sudarshan — Fairless Hills,manufacturing_plant,Fairless Hills,PA,,Bucks,2,325130,researcher_inferred,medium,pigment manufacturing (former Heubach plant),,organic and inorganic pigments,,,unknown,active,Sudarshan Annual Report FY2025-26 (sudarshan.com),B,2026-10-30,pass-20 integrator (spaghetti subagent),Operator: Sudarshan North America Inc.. Created 2026-10-30 in integration pass 20 from candidate-queue wave Q01-Q02 site design NEW:E-103-S1 (org NEW:E-103). City-grain site by design; do not invent a street address.,,,,,,,US

FILE verdicts.csv
site_id,verdict,street_address,reason,evidence_id
SITE-002807,STILL_UNCERTAIN,,need own-operator physical street page for this city; none raw-checked within cap,
SITE-002817,STILL_UNCERTAIN,,need own-operator physical street page for this city; none raw-checked within cap,
SITE-002822,STILL_UNCERTAIN,2727 West 16th St.,existing ZIP conflicts with own-page ZIP; geography correction is outside this pass,
SITE-002824,STILL_UNCERTAIN,,need own-operator physical street page for this city; none raw-checked within cap,
SITE-002825,VERIFIED,4861 West 23rd Street,,EVD-155004
SITE-002829,STILL_UNCERTAIN,,need own-operator physical street page for this city; none raw-checked within cap,
SITE-002831,STILL_UNCERTAIN,,need own-operator physical street page for this city; none raw-checked within cap,
SITE-002833,VERIFIED,2935 West 17th Street,,EVD-155007
SITE-002834,VERIFIED,9 Guttman Avenue,,EVD-155008
SITE-002838,STILL_UNCERTAIN,,need own-operator physical street page for this city; none raw-checked within cap,
SITE-002840,VERIFIED,1 Lark Ave.,,EVD-155010
SITE-002845,STILL_UNCERTAIN,,need own-operator physical street page for this city; none raw-checked within cap,
SITE-002848,STILL_UNCERTAIN,,need own-operator physical street page for this city; none raw-checked within cap,
SITE-002852,STILL_UNCERTAIN,,need own-operator physical street page for this city; none raw-checked within cap,
SITE-002853,VERIFIED,600 Dietrich Ave,,EVD-155014
SITE-002854,STILL_UNCERTAIN,,need own-operator physical street page for this city; none raw-checked within cap,
SITE-002859,VERIFIED,1040 Maple Avenue,,EVD-155016
SITE-003584,STILL_UNCERTAIN,,need own-operator physical street page for this city; none raw-checked within cap,
SITE-003723,STILL_UNCERTAIN,,need own-operator physical street page for this city; none raw-checked within cap,
SITE-004115,STILL_UNCERTAIN,,need own-operator physical street page for this city; none raw-checked within cap,
SITE-004272,STILL_UNCERTAIN,,need own-operator physical street page for this city; none raw-checked within cap,
SITE-004299,VERIFIED,480 Johnson Road,,EVD-155021
SITE-004558,STILL_UNCERTAIN,,need own-operator physical street page for this city; none raw-checked within cap,
SITE-004560,STILL_UNCERTAIN,,need own-operator physical street page for this city; none raw-checked within cap,

FILE evidence.csv
evidence_id,record_table,record_id,claim_type,claim_detail,source_class,source_ref,observed_date,tier_effect,created_by,notes
EVD-155004,sites,SITE-002825,address,"street_address 4861 West 23rd Street, Erie, PA; own-page ZIP 16506",own_site,https://www.georgeko.com/Contact-GeorgeKo.htm,2026-11-06,supports_A,atlas-L2-pa-address,"Raw checked 2026-11-06; SHA-256 74a642a21640dcc3f436707cf5d0f44759540dd408e4c4ece5e146ec8e7cc730; quote: 4861 West 23rd Street Erie, PA 16506. County, county_source, ZIP and record tier unchanged."
EVD-155007,sites,SITE-002833,address,"street_address 2935 West 17th Street, Erie, PA; own-page ZIP 16505",own_site,https://www.munotplastics.com/,2026-11-06,supports_A,atlas-L2-pa-address,"Raw checked 2026-11-06; SHA-256 c0bd6d70303261b406c9295ee70a1a9786abd570ff3ac862d4052c66d8823d06; quote: 2935 West 17th Street Erie, PA 16505. County, county_source, ZIP and record tier unchanged."
EVD-155008,sites,SITE-002834,address,"street_address 9 Guttman Avenue, Charleroi, PA; own-page ZIP 15022",own_site,https://nationalpolymers.com/about,2026-11-06,supports_A,atlas-L2-pa-address,"Raw checked 2026-11-06; SHA-256 35a77973e7231a8b155e3daa4c711ada8514680b3d009396aba4c1cdc9a5f79c; quote: 9 Guttman Avenue Charleroi, PA 15022. County, county_source, ZIP and record tier unchanged."
EVD-155010,sites,SITE-002840,address,"street_address 1 Lark Ave., Leola, PA; own-page ZIP 17540",own_site,https://polymar-asm.com/,2026-11-06,supports_A,atlas-L2-pa-address,"Raw checked 2026-11-06; SHA-256 1561f7475bf9cabb58d72621f89d2bfd6ba769ea58812089ed9965b6e76750d9; quote: 1 Lark Ave., Leola, PA 17540. County, county_source, ZIP and record tier unchanged."
EVD-155014,sites,SITE-002853,address,"street_address 600 Dietrich Ave, Hazleton, PA; own-page ZIP 18201",own_site,https://multi-plastics.com/,2026-11-06,supports_A,atlas-L2-pa-address,"Raw checked 2026-11-06; SHA-256 dc555a30df1f5c1fad90ace8d43a5d9251e23a581bab29c2086535de044ac9f8; quote: 600 Dietrich Ave, Hazleton, PA 18201. County, county_source, ZIP and record tier unchanged."
EVD-155016,sites,SITE-002859,address,"street_address 1040 Maple Avenue, Lake City, PA; own-page ZIP 16423",own_site,https://engineeredplastics.com/,2026-11-06,supports_A,atlas-L2-pa-address,"Raw checked 2026-11-06; SHA-256 bfc9224d396bdcf27425d2f139e739ab91fed23c9acfa1e0006ba06d9cbd9d5a; quote: 1040 Maple Avenue Lake City, PA 16423. County, county_source, ZIP and record tier unchanged."
EVD-155021,sites,SITE-004299,address,"street_address 480 Johnson Road, Washington, PA; own-page ZIP 15301",own_site,https://www.audiaelastomers.com/pages/contact,2026-11-06,supports_A,atlas-L2-pa-address,"Raw checked 2026-11-06; SHA-256 9c42f44b5ce37d63a272a2e39240d580b49e9548b2848e0bdcf7d1d613810ca8; quote: 480 Johnson Road Washington, PA 15301. County, county_source, ZIP and record tier unchanged."

FILE rawchecks.csv
site_id,street_address,source_zip,quote,url,sha256,checked_urls
SITE-002807,,,,https://www.adeptcorp.com/about-us/,,https://www.adeptcorp.com/about-us/;https://www.adeptcorp.com/contact-us/
SITE-002817,,,,https://covingtonplasticmolding.com/,,https://covingtonplasticmolding.com/;https://covingtonplasticmolding.com/#contact-form
SITE-002822,2727 West 16th St.,16505,"2727 West 16th St. Erie, PA 16505",https://www.executool.net/,d9ba24d43df717bab42b39c90b5b3d2588bed15d26d8aa8e305a69cdeadb480f,https://www.executool.net/
SITE-002822,2727 West 16th St.,16505,"2727 West 16th St. Erie, PA 16505",https://www.executool.net/,d9ba24d43df717bab42b39c90b5b3d2588bed15d26d8aa8e305a69cdeadb480f,https://www.executool.net/
SITE-002822,2727 West 16th St.,16505,"2727 West 16th St. Erie, PA 16505",https://www.executool.net/contact-us/,0ff7d14116fee3aa5bfb4221ba6b85139a30946a7deb6cc2d8f989111aba2a9b,https://www.executool.net/;https://www.executool.net/contact-us/
SITE-002822,2727 West 16th St.,16505,"2727 West 16th St. Erie, PA 16505",https://www.executool.net/contact-us/,0ff7d14116fee3aa5bfb4221ba6b85139a30946a7deb6cc2d8f989111aba2a9b,https://www.executool.net/;https://www.executool.net/contact-us/
SITE-002824,,,,http://www.geminiplastics.net,,http://www.geminiplastics.net
SITE-002825,4861 West 23rd Street,16506,"4861 West 23rd Street Erie, PA 16506",https://www.georgeko.com/Contact-GeorgeKo.htm,74a642a21640dcc3f436707cf5d0f44759540dd408e4c4ece5e146ec8e7cc730,https://www.georgeko.com/GeorgeKo-Production-Manufacturing.htm;https://www.georgeko.com/Contact-GeorgeKo.htm
SITE-002829,,,,https://mqplastics.com/,,https://mqplastics.com/;https://mqplastics.com/contact-us/
SITE-002831,,,,https://milletplastics-group.com/,,https://milletplastics-group.com/
SITE-002833,2935 West 17th Street,16505,"2935 West 17th Street Erie, PA 16505",https://www.munotplastics.com/,c0bd6d70303261b406c9295ee70a1a9786abd570ff3ac862d4052c66d8823d06,https://www.munotplastics.com/
SITE-002833,2935 W 17th St,16505,"2935 W 17th St Erie, PA 16505",https://www.munotplastics.com/contact-us/,403432a6cc81d0eb8d1f78411fc0ca612a4e272781a1228cd107823c857c6e49,https://www.munotplastics.com/;https://www.munotplastics.com/contact-us/
SITE-002833,2935 West 17th Street,16505,"2935 West 17th Street Erie, PA 16505",https://www.munotplastics.com/contact-us/,403432a6cc81d0eb8d1f78411fc0ca612a4e272781a1228cd107823c857c6e49,https://www.munotplastics.com/;https://www.munotplastics.com/contact-us/
SITE-002838,,,,,,
SITE-002840,1 Lark Ave.,17540,"1 Lark Ave., Leola, PA 17540",https://polymar-asm.com/,1561f7475bf9cabb58d72621f89d2bfd6ba769ea58812089ed9965b6e76750d9,https://polymar-asm.com/
SITE-002840,1 Lark Ave.,17540,"1 Lark Ave., Leola, PA 17540",https://polymar-asm.com/contact-us/,56371af6dba436342a0748d4e28d3ac0da06a0dd6c3225fc56579402b57437b9,https://polymar-asm.com/;https://polymar-asm.com/contact-us/
SITE-002840,1 Lark Ave.,17540,"1 Lark Ave., Leola, PA 17540",https://polymar-asm.com/contact-us/,56371af6dba436342a0748d4e28d3ac0da06a0dd6c3225fc56579402b57437b9,https://polymar-asm.com/;https://polymar-asm.com/contact-us/
SITE-002845,,,,https://retalgroup.com/,,https://retalgroup.com/
SITE-002848,,,,https://vikingplastics.com/,,https://vikingplastics.com/
SITE-002852,,,,https://www.grahampackaging.com/,,https://www.grahampackaging.com/;https://www.grahampackaging.com/solutions/co-location-manufacturing/;https://www.grahampackaging.com/contact/
SITE-002853,600 Dietrich Ave,18201,"600 Dietrich Ave, Hazleton, PA 18201",https://multi-plastics.com/,dc555a30df1f5c1fad90ace8d43a5d9251e23a581bab29c2086535de044ac9f8,https://multi-plastics.com/
SITE-002853,600 Dietrich Ave.,18201,"600 Dietrich Ave. Hazleton, PA 18201",https://multi-plastics.com/contact-us,493c33a4c2bddcc34c6e50e72a86cd0e2587a39ef6ad8baad3fee3ed8ff9ea50,https://multi-plastics.com/;https://multi-plastics.com/contact-us
SITE-002853,600 Dietrich Ave,18201,"600 Dietrich Ave, Hazleton, PA 18201",https://multi-plastics.com/contact-us,493c33a4c2bddcc34c6e50e72a86cd0e2587a39ef6ad8baad3fee3ed8ff9ea50,https://multi-plastics.com/;https://multi-plastics.com/contact-us
SITE-002853,600 Dietrich Ave.,18201,"600 Dietrich Ave. Hazleton, PA 18201",https://multi-plastics.com/contact-us/,493c33a4c2bddcc34c6e50e72a86cd0e2587a39ef6ad8baad3fee3ed8ff9ea50,https://multi-plastics.com/;https://multi-plastics.com/contact-us;https://multi-plastics.com/contact-us/
SITE-002853,600 Dietrich Ave,18201,"600 Dietrich Ave, Hazleton, PA 18201",https://multi-plastics.com/contact-us/,493c33a4c2bddcc34c6e50e72a86cd0e2587a39ef6ad8baad3fee3ed8ff9ea50,https://multi-plastics.com/;https://multi-plastics.com/contact-us;https://multi-plastics.com/contact-us/
SITE-002854,,,,https://qualityplasticsllc.com,,https://qualityplasticsllc.com
SITE-002859,1040 Maple Avenue,16423,"1040 Maple Avenue Lake City, PA 16423",https://engineeredplastics.com/,bfc9224d396bdcf27425d2f139e739ab91fed23c9acfa1e0006ba06d9cbd9d5a,https://engineeredplastics.com/
SITE-002859,1040 Maple Avenue,16423,"1040 Maple Avenue Lake City PA, 16423",https://engineeredplastics.com/contact,43d87ceeac65618d0cd375779e77f0397d144a449f2ca36bd32e3192dab45760,https://engineeredplastics.com/;https://engineeredplastics.com/contact
SITE-002859,1040 Maple Avenue,16423,"1040 Maple Avenue Lake City, PA 16423",https://engineeredplastics.com/contact,43d87ceeac65618d0cd375779e77f0397d144a449f2ca36bd32e3192dab45760,https://engineeredplastics.com/;https://engineeredplastics.com/contact
SITE-003584,,,,https://valexgroup.com,,https://valexgroup.com;https://valexgroup.com/contact/;https://valexgroup.com/contact
SITE-003723,,,,https://www.zurn.com/,,https://www.zurn.com/
SITE-004115,,,,https://acmos.com,,https://acmos.com
SITE-004272,,,,,,
SITE-004299,480 Johnson Road,15301,"480 Johnson Road Washington, PA 15301",https://www.audiaelastomers.com/pages/contact,9c42f44b5ce37d63a272a2e39240d580b49e9548b2848e0bdcf7d1d613810ca8,https://www.audiaelastomers.com;https://www.audiaelastomers.com/pages/contact
SITE-004558,,,,https://www.noracadditives.com,,https://www.noracadditives.com;https://www.noracadditives.com/contact
SITE-004560,,,,https://www.sudarshan.com,,https://www.sudarshan.com;https://www.sudarshan.com/contact-us/
SITE-002834,9 Guttman Avenue,15022,"9 Guttman Avenue Charleroi, PA 15022",https://nationalpolymers.com/about,35a77973e7231a8b155e3daa4c711ada8514680b3d009396aba4c1cdc9a5f79c,https://nationalpolymers.com/about

FILE audit.csv
site_id,source_ref,result,error
SITE-002825,https://www.georgeko.com/Contact-GeorgeKo.htm,PASS,
SITE-002833,https://www.munotplastics.com/,PASS,
SITE-002834,https://nationalpolymers.com/about,PASS,
SITE-002840,https://polymar-asm.com/,PASS,
SITE-002853,https://multi-plastics.com/,PASS,
SITE-002859,https://engineeredplastics.com/,PASS,
SITE-004299,https://www.audiaelastomers.com/pages/contact,PASS,
