Deep adversarial completion refute requested: L3 merged-site quality, frozen main d1e618b. Exactly3 mergedCsites(141Watson+198PolyMonroe/PlastipakPineville), OPEN164/202/204excluded.1C→B Pineville,2holds,0creates. Fiveappend-onlyB EVD304012–016:4government_filing(existence,address,code,parent) from bankedITA192504 +1own_site scope EXACTcompanyissuedjobquote. OwnWorkdaytenantlinkedbyownPlastipakcareerspage; JSONREQ24583 namesPinevilleLA,plasticcontainermanufacture,issuer1000PlastipakPackagingIncUS,date2026-09-23. DirectJSONandcareersraw200/hashbound;HTMLshell/Jinafailure notused. Ownclaimquote-only07:20,nofederalfacts;noBparentinference/sameissuer. Statusunknownretained(noactive/livenessassertion),oldCrowsappend-only. All5mandatoryBrequiredactualgate. HoldsWatsonblankNAICS/FergusonvsheldSTLouis;PolyownZIP71203vsheld71210,unchanged. Full1promotioncensusrequired. Exact2datafiles3sitecells+5EVD,alloldrowspreserved/globalIDguard/allCSVreplay/validator0PASS. Known3+fakenegatives,receipt5+negative5,jobquote+negative/issuer/date/city/delegation PASS;missing5claimsgatefaults and4beforewrite mutations(scope/city/hash/foreignEVD) rejected. Fetchcaps2/2/4,rawcache/tmp(noPIIinrepo). Strict326unchangedMO43/LA9. Please REFUTE sourceissuer/ownissuedclassification(cityactivitysameJSON)/jointfederalBclaimstrength/bankvintage/status/tierweakestclaim/localityholds/framecompleteness/preservation/idempotence; END APPROVEorREFUTE with findings+coverage+limits. UsePRrefsowncheckout,donotswitchworker. Raw selected.json paths/tmp sharedhost; publicJSON source can be independentlycurl fetched.


FILE README.md
# L3 merged-site quality

The frozen census contains three merged L3 tier-C establishments: Watson Coatings (SITE-012001, merged #141), Poly Processing Monroe (SITE-012503), and Plastipak Pineville (SITE-012511), the latter two from merged #198. The pinned main is d1e618b. PRs #164, #202 and #204 were open and are excluded.

One establishment is promoted C→B: Plastipak Pineville. Two remain STILL_UNCERTAIN. No organizations or sites are created. Only three site cells change: verification_tier, sources, and notes. last_verified is assigned2026-11-06, its existing value. Address, code, process, ring, status, county, qualifiers, registry links and relationships remain unchanged.

Five appended evidence rows, EVD-304012–304016, cover the promoted site's five mandatory claims at B. Allocation is304000+6*frozen input index, inside the controller's unused304000+ block. Slots304000–304011 remain unused permanent gaps. All existing evidence is preserved.

## Plastipak Pineville: joint primary-source support

The company's careers page links its Workday tenant. The tenant's public company-issued job JSON for REQ24583 names Plastipak-Pineville, LA; the hiring organization1000 Plastipak Packaging Inc. (US); and plastic-container manufacture using extrusion and blow-molding equipment. The source date is2026-09-23; retrieval/review was2026-11-06. The direct JSON request returned200. The HTML job URL returned a JavaScript shell and the Jina route failed; these availability signals did not supply evidence. The own careers page also returned200.

selected.json records the exact source URL, public job URL, issuer/location/activity strings, dates, raw paths and SHA256 digests. The complete raw responses remain in/tmp, outside the public repository. The job is an own-issued document, rather than a platform-assigned category; the company's own careers link establishes the issuer. The named employer is the held operator, so no parent/group relationship is inferred. B-PARENT does not require a new relationship for this issuer.

The own_site scope claim_detail contains only the exact job sentence. It includes no government identifiers, registrant aliases, NAICS or federal claims, under the controller's07:20 rule.

Four government_filing observations at B cover existence, address, code and operator linkage from ITA192504: Plastipak-Pineville;4101 Pardue Rd, Pineville LA71360; NAICS326160; and filed company_name Plastipak Packaging Inc. These values match the held site and operator. The source remains the controller-authorized banked CY2025 filing, packet observed2026-11-01, submitted2026-01-16. No fresh federal download is asserted.

This follows the campaign and L11 mi-il-site-quality convention: the independent company-issued city/activity witness corroborates the federal plant identity and location, with all five mandatory claims explicitly supported at B. Government facts remain government claims. The fifth claim, scope, is the own-issued quote. Operating_status remains unknown; no current-operation/status claim is made. Existing C activity/liveness observations remain append-only and are not mandatory for unknown status. There is no A promotion.

## Holds

Watson: its own homepage/about page supports coatings manufacture at325 Paul Avenue, Ferguson MO63135. The held city is ST LOUIS and the site's NAICS is blank. Promotion needs site-code provenance at B and postal-locality reconciliation. Banked FRS325510 is an old registry context; the employer Form5500 padded group325500 does not settle the current site code. No locality, code, status or tier correction is applied. See watson-source-gaps.md.

Poly Processing: its own contact page names2201 Old Sterlington Rd, Monroe LA71203; the held filing/site ZIP is71210. Its own blog confirms manufacturing in Monroe, but does not reconcile the ZIP. Hold pending physical ZIP reconciliation; no ZIP, status or tier change. Both pages returned200 and their quotes are raw-verified in rawcheck.json.

## Checks

Before use, the existing STRONG/evidence-repair parser and matcher passed three known Watson quotes and three fabricated-suffix negatives. Two Poly quotes and negatives also pass. Plastipak's source quote, issuer, city, date and careers delegation are checked against its raw JSON/HTML. This uses standard JSON parsing and the existing matcher, with no new network fetcher.

Primary routes: Watson2, Poly2, Plastipak4 (job HTML, Jina fallback, direct company-issued JSON, careers bridge), within the approximate six-route cap. Search-index job text was discovery only until direct JSON verification. A bridge hash initially used newline-normalized text rather than raw bytes; the preflight rejected it before any canonical write. It was corrected to hash the same raw bytes used by the builder.

Run:
- python3 tasks/l3-merged-site-quality-2026-11-06/build.py --apply
- python3 tasks/l3-merged-site-quality-2026-11-06/check.py --negative-controls
- python3 scripts/validate.py

Results: PASS3/3 independently reconstructed merged-C inputs, one promotion/two holds, all five B claims, every old canonical row/evidence preserved, exact two data files/three site cells/five evidence rows. The actual require_five gate rejects each missing mandatory claim. Four mutations (fabricated scope, wrong city, raw hash, cross-shard EVD collision) reject before any write; temporary canonical CSV hashes remain unchanged. Raw receipts pass five quote/five fake-suffix checks, plus the selected job quote and its negative. All canonical CSVs are byte-identical after builder replay. Validator:0 errors.

Full promotion census is full-promotion-census.csv (one establishment, so inspect all rather than sample20). No shared scripts changed; full scripts pytest was not run. Raw cache paths in selected.json/rawcheck.json are available on this shared host; re-fetch public URLs with curl/browser UA if needed. Full page bodies are not committed because they may contain personal contacts. The missing Mac entity catalogue was reported INCOMPLETE, never absence.

Strict NAICS326 counts are unchanged: MO43/368 and LA9/117 QCEW2023 private establishments. Tier C already entered the strict numerator; this quality promotion changes no establishment count or NAICS value. These are count ratios, not matched coverage; see qcew.json.

The first user is the controller/research integrator, review date2026-11-06. Acceptance preceded application; merged #198 frame expansion was recorded before promotion. Earlier research checkpoints in research-journal.md are superseded. The priority MN wrong-parent correction b420831 was completed before this application. Two-family deep completion refutes remain pending; the controller alone merges and changes tracker status.


FILE LANE_BRIEF.md
# L3 merged-site quality pass

Controller assigns quality pass2026-11-06: merged L3 tierCcreates only(PR141 and any merged164/198/202/204). Frozen pinnedmain542629e atstart has exactly1eligibleCsite,SITE012001WatsonCoatingsMO; other fourPRsOPENexcluded. Firstusercontroller/researchintegrator intendedreview2026-11-06. No unmergedrecordpromotion,workermerge/status/QUEUEwrite.

Acceptance beforeapply: eachfrozeneligible siteexactonceverdict; C→B onlyafterrawverbatimownpage namesplantcity+polymeractivity andall5site must-haveclaims(existence,address,scope,code,parent)haveBsupport; active status additionallyneedsactivity/livenessatB. B-PARENT documentedrelationship+plantcity/activity andB-PARENT-WEBnotes,controller07:20pagewordsonlyownclaims. Federalfacts remainfederalobservations. MissingNAICS/source/activitybinding hold,notboilerplatepromotion. No closure/identity/repoint/scope/ring/selfruling; unresolvedfactsnamed. Approx6primaryroutes/orgcap,failedroutesnotabsence.

Reuse L11mi-il-site-quality pattern/house evidence-repairrawmatcher andshard_io.append_sorted; no new fetcher/sharedscripts. Known3rawanswers+fabricatednegativesbeforetrust,fullpromotedcensus,hashboundrawreceipts. Everynewfactevidencedappendonly,oldEVDunchanged. IDsEVD304000–305999 unused withincontroller300000–309999 grant,slot6evidenceperinput for5mandatory+optionalactiveclaim; nogapsreused. NoORG/SITEcreates.

Namedcheckcompleteframe/sourceBclaimcoverage/oldrowpreservation/exactfieldboundary/globalreservedID/no-writefaults/replay/validate0errors; T3strict326unchangedunlessindependentlyauthorizedcodechange(nochangeplanned). TwofamilydeeprefutesbeforeDone,controllermergeonly.

Revision before application: controller merged #198 at2026-11-06T12:59:04Z. The frame expands from Watson alone to exactly3 merged C sites on pinned d1e618b:012001,012503,012511. PR164/202/204 remain OPEN and excluded. Original one-site checkpoint is superseded for census only; all acceptance/source/ID/merge-only restrictions stand. Raw Plastipak company-issued API is an own-issued document, with issuer delegation proven by the company's careers link; it does not require a new parent relationship. Promotion may affect only tier/sources/last_verified/notes, plus append-only five-claim evidence. No address/status/code correction authorized. Raw cache remains outside public repo.


FILE build.py
#!/usr/bin/env python3
"""Joint primary-source quality adjudication of the three frozen merged L3 C sites."""
import argparse,csv,hashlib,importlib.util,json,sys
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from shard_io import append_sorted
from atlas import name_key,street_key
spec=importlib.util.spec_from_file_location('raw',ROOT/'tasks/strong-waves-mo-sc-la-2026-11-06/prepare.py');raw=importlib.util.module_from_spec(spec);spec.loader.exec_module(raw)
BY='atlas-L3-merged-site-quality';DATE='2026-11-06'
def read(p):
 with open(p,newline='') as f:return list(csv.DictReader(f))
def write(p,rows):
 with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def witness(r):
 p=Path(r['raw_path']);bridge=Path(r['bridge_raw_path'])
 assert hashlib.sha256(p.read_bytes()).hexdigest()==r['raw_sha256'],'job raw hash changed'
 assert hashlib.sha256(bridge.read_bytes()).hexdigest()==r['bridge_sha256'],'issuer bridge changed'
 assert 'https://plastipak.wd1.myworkdayjobs.com/Plastipak' in bridge.read_text(),'issuer tenant link absent'
 d=json.loads(p.read_text());j=d['jobPostingInfo'];t=raw.Text();t.feed(j['jobDescription']);text=' '.join(t.parts)
 assert r['raw'] and j['jobReqId']=='REQ24583' and j['location']==r['city_quote']=='Plastipak - Pineville, LA'
 assert j['startDate']==r['source_date']=='2026-09-23' and d['hiringOrganization']['name']==r['issuer_quote']=='1000 Plastipak Packaging Inc. (US)'
 assert raw.contains(text,r['quote']),'scope quote absent'
 assert r['source_url']=='https://plastipak.wd1.myworkdayjobs.com/wday/cxs/plastipak/Plastipak/job/Process-Technician--Day-Shift_REQ24583'
 return text

def require_five(rows):
 assert {r['claim_type'] for r in rows if r['tier_effect']=='supports_B'}=={'existence','address','code','parent','scope'},'missing B must-have claim'
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');ap.add_argument('--data-dir',type=Path,default=ROOT/'data');a=ap.parse_args();data=a.data_dir
 frame=read(H/'input.csv');selected=json.loads((H/'selected.json').read_text());holds=read(H/'holds.csv')
 assert len(frame)==3 and {r['site_id'] for r in frame}=={'SITE-012001','SITE-012503','SITE-012511'}
 assert len(selected)==1 and selected[0]['site_id']=='SITE-012511'
 assert {r['site_id'] for r in holds}=={'SITE-012001','SITE-012503'} and all(r['verdict']=='STILL_UNCERTAIN' and r['reason'] for r in holds)
 sites=[(p,r) for p in data.glob('sites_*.csv') for r in read(p)];assert len(sites)==len({r['site_id'] for _,r in sites}),'duplicate site ID'
 by={r['site_id']:(p,r) for p,r in sites};ev=[(p,r) for p in data.glob('evidence_*.csv') for r in read(p)];assert len(ev)==len({r['evidence_id'] for _,r in ev}),'duplicate evidence ID'
 have={r['evidence_id']:(p,r) for p,r in ev};orgs={r['org_id']:r for p in data.glob('organizations_*.csv') for r in read(p)}
 ita={r['establishment_id']:r for r in read(ROOT/'tasks/osha-ita-2026-11-01/establishments.csv')};updates={};planned=[];verdicts=[]
 for slot,i in enumerate(frame):
  p,now=by[i['site_id']]
  if i['site_id']!='SITE-012511':assert now==i,('held record changed',i['site_id']);verdicts.append(next(r for r in holds if r['site_id']==i['site_id']));continue
  r=selected[0];witness(r);assert i['verification_tier']=='C' and i['operating_status']=='unknown'
  f=ita[r['establishment_id']];org=orgs[i['org_id']];assert i['org_id']=='ORG-001033' and org['status']=='active' and not org['successor_org_id']
  assert name_key(f['company_name']) in {name_key(x) for x in [org['legal_name']]+org['trade_names'].split(';')}
  assert street_key(f['street']) and street_key(f['street'])==street_key(i['street_address']) and (f['city'],f['state'],f['zip5'],f['naics_code'])==(i['city'],i['state'],i['zip'],i['naics_primary'])
  assert f['reliability']=='ok' and f['naics_code']=='326160' and f['establishment_id']=='192504'
  new=dict(i);new.update(verification_tier='B',last_verified=DATE,sources=i['sources']+'; '+r['source_url'],notes=i['notes']+' | '+DATE+' quality: joint federal and company-issued Pineville plastic-container manufacturing witness; five must-have claims B. Operating_status unknown retained; job dated2026-09-23. Workday tenant linked by own careers page.')
  assert now in [i,new],('conflicting site edit',i['site_id']);updates[p]={i['site_id']:new}
  claims={'existence':f"ITA192504: {f['establishment_name']}; filed company_name {f['company_name']}",'address':f"{f['street']}, {f['city']}, {f['state']} {f['zip5']}, US; county unchanged/unset",'code':f"naics_primary {f['naics_code']}; government_filing, medium confidence",'parent':f"org_id {i['org_id']} ({org['legal_name']}); filed company_name {f['company_name']}"}
  for n,(claim,detail) in enumerate(list(claims.items())+[('scope',r['quote'])]):
   own=claim=='scope';e=dict(evidence_id=f'EVD-{304000+slot*6+n:06d}',record_table='sites',record_id=i['site_id'],claim_type=claim,claim_detail=detail,source_class='own_site' if own else 'government_filing',source_ref=r['source_url'] if own else i['sources'],observed_date=r['source_date'] if own else '2026-11-01',tier_effect='supports_B',created_by=BY,notes=(r['note'] if own else f"CY2025 banked ITA192504 submitted {f['date_submitted']}, joint company-issued Pineville scope corroboration; government facts stay government claims.")+f' Retrieved/reviewed{DATE}; current operating status unknown.')
   path=data/'evidence_sites_LA.csv'
   if e['evidence_id'] in have:assert have[e['evidence_id']]==(path,e),('conflicting evidence ID',e['evidence_id'])
   planned.append((path,e))
  verdicts.append(dict(site_id=i['site_id'],verdict='VERIFIED',reason='Five must-have claims atB after federal and company-issued Pineville plastic-container manufacturing corroboration; statusunknown retained.'))
 require_five([r for _,r in planned])
 if a.apply:
  for p,changes in updates.items():write(p,[changes.get(r['site_id'],r) for r in read(p)])
  for p in {p for p,_ in planned}:
   pending=[r for q,r in planned if p==q and r['evidence_id'] not in have]
   if pending:append_sorted(p,pending,'evidence_id')
 write(H/'verdicts.csv',verdicts)
 print(json.dumps({'merged_C_frame':3,'promoted':1,'holds':2,'new_evidence':5,'pending_evidence':sum(r['evidence_id'] not in have for _,r in planned)}))
if __name__=='__main__':main()


FILE check.py
#!/usr/bin/env python3
"""Merged-frame/weakest-claim/source boundary and fail-before-write quality checks."""
import argparse,copy,csv,hashlib,io,json,shutil,subprocess,sys,tempfile
from pathlib import Path
from build import H,ROOT,read,witness,raw,BY,require_five
ap=argparse.ArgumentParser();ap.add_argument('--negative-controls',action='store_true');a=ap.parse_args()
base=json.loads((H/'baseline.json').read_text())['commit'];frame=read(H/'input.csv');vs=read(H/'verdicts.csv');sel=json.loads((H/'selected.json').read_text());assert len(frame)==len(vs)==3 and {r['site_id'] for r in frame}=={r['site_id'] for r in vs}
frozen=[]
for path in subprocess.check_output(['git','ls-tree','-r','--name-only',base,'data/'],cwd=ROOT,text=True).splitlines():
 if path.startswith('data/sites_') and path.endswith('.csv'):
  frozen.extend(r for r in csv.DictReader(io.StringIO(subprocess.check_output(['git','show',base+':'+path],cwd=ROOT,text=True))) if r['verification_tier']=='C' and r['created_by'] in {'atlas-L3-strong-mo-sc-la','atlas-L3-corroborated-mo-sc','atlas-L3-corroborated-la','atlas-L3-corroborated-mn','atlas-L3-corroborated-nj'})
assert {r['site_id']:r for r in frozen}=={r['site_id']:r for r in frame},'under-returned merged frame'
assert sum(r['verdict']=='VERIFIED' for r in vs)==1 and sum(r['verdict']=='STILL_UNCERTAIN' for r in vs)==2
text=witness(sel[0]);bad=copy.deepcopy(sel[0]);bad['quote']+=' fabricatedplantproof7731'
try:witness(bad)
except AssertionError:pass
else:raise AssertionError('fabricated scope accepted')
sites={r['site_id']:r for p in (ROOT/'data').glob('sites_*.csv') for r in read(p)}
for r in frame:
 now=sites[r['site_id']];diff={k for k in r if r[k]!=now[k]}
 if r['site_id']=='SITE-012511':assert diff=={'verification_tier','sources','notes'} and now['verification_tier']=='B' and now['operating_status']=='unknown'
 else:assert not diff,('held site changed',r['site_id'])
paths=subprocess.check_output(['git','diff','--name-only',base,'--','data/'],cwd=ROOT,text=True).splitlines();assert set(paths)=={'data/sites_LA.csv','data/evidence_sites_LA.csv'},paths
new=[]
for path in paths:
 old=list(csv.DictReader(io.StringIO(subprocess.check_output(['git','show',base+':'+path],cwd=ROOT,text=True))));now=read(ROOT/path);key=list(old[0])[0];by={r[key]:r for r in now};assert len(by)==len(now)
 for r in old:
  assert r[key] in by
  if r[key]!='SITE-012511':assert by[r[key]]==r,('old row edited',path,r[key])
 if key=='site_id':assert len(old)==len(now)
 else:have={r[key] for r in old};new=[r for r in now if r[key] not in have]
assert len(new)==5 and {r['evidence_id'] for r in new}=={f'EVD-{n:06d}' for n in range(304012,304017)}
assert {r['claim_type'] for r in new}=={'existence','address','code','parent','scope'} and all(r['tier_effect']=='supports_B' and r['record_id']=='SITE-012511' and r['created_by']==BY for r in new)
for r in new:
 if r['source_class']=='own_site':assert r['claim_type']=='scope' and r['claim_detail']==sel[0]['quote'] and r['observed_date']=='2026-09-23' and r['source_ref']==sel[0]['source_url']
 else:assert r['source_class']=='government_filing' and r['observed_date']=='2026-11-01' and r['source_ref'].endswith('#establishment_ID=192504')
# Complete weakest-claim regression: dropping any of the five observations cannot support B.
for claim in ['existence','address','code','parent','scope']:
 bad=[r for r in new if r['claim_type']!=claim]
 try:require_five(bad)
 except AssertionError:pass
 else:raise AssertionError(('missing B claim accepted',claim))
for r in json.loads((H/'rawcheck.json').read_text()):
 if 'raw_text_path' in r:p=Path(r['raw_text_path']);t=p.read_text()
 else:
  name='home' if r['source_url'].endswith('.com/') else 'about';p=Path('/tmp/l3-quality-watson-'+name+'.html');parser=raw.Text();parser.feed(p.read_text());t=' '.join(parser.parts)
 assert hashlib.sha256(p.read_bytes()).hexdigest()==r['raw_sha256'] and raw.contains(t,r['quote']) and not raw.contains(t,r['quote']+' fabricatedplantproof7731')
if a.negative_controls:
 with tempfile.TemporaryDirectory() as d:
  root=Path(d);data=root/'data';shutil.copytree(ROOT/'data',data);packet=root/'tasks'/H.name;packet.parent.mkdir();shutil.copytree(H,packet)
  (root/'scripts').symlink_to(ROOT/'scripts',target_is_directory=True)
  for name in ['osha-ita-2026-11-01','strong-waves-mo-sc-la-2026-11-06','evidence-repair-2-2026-11-04']:(packet.parent/name).symlink_to(ROOT/'tasks'/name,target_is_directory=True)
  def fail(needle):
   hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.csv')};run=subprocess.run([sys.executable,str(packet/'build.py'),'--data-dir',str(data),'--apply'],capture_output=True,text=True)
   assert run.returncode and needle in run.stderr,run.stderr;assert hashes=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.glob('*.csv')}
  wrong=data/'evidence_sites_AL.csv';orig=wrong.read_bytes();rows=read(wrong)
  with wrong.open('a',newline='') as f:csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n').writerow({**rows[0],'evidence_id':'EVD-304012'})
  fail('duplicate evidence ID');wrong.write_bytes(orig)
  p=packet/'selected.json';bad=copy.deepcopy(sel);bad[0]['quote']+=' fabricatedplantproof7731';p.write_text(json.dumps(bad));fail('scope quote absent')
  bad=copy.deepcopy(sel);bad[0]['city_quote']='Plastipak - Wrong City';p.write_text(json.dumps(bad));fail('AssertionError')
  bad=copy.deepcopy(sel);bad[0]['raw_sha256']='0'*64;p.write_text(json.dumps(bad));fail('job raw hash changed')
print('PASS3mergedCsites/1C→B2holds/5Bclaims/oldrows/evidenceappendonly/rawissuer-city-scope/5missingclaims/4no-writefaults(ifrequested); strict326 unchanged')


FILE selected.json
[
  {
    "site_id": "SITE-012511",
    "establishment_id": "192504",
    "source_url": "https://plastipak.wd1.myworkdayjobs.com/wday/cxs/plastipak/Plastipak/job/Process-Technician--Day-Shift_REQ24583",
    "public_job_url": "https://plastipak.wd1.myworkdayjobs.com/Plastipak/job/Plastipak---Pineville-LA/Process-Technician--Day-Shift_REQ24583",
    "quote": "As a Process Technician, you operate equipment to manufacture plastic containers for leading consumer brands.",
    "city_quote": "Plastipak - Pineville, LA",
    "issuer_quote": "1000 Plastipak Packaging Inc. (US)",
    "source_date": "2026-09-23",
    "retrieved_date": "2026-11-06",
    "raw_path": "/tmp/l3-quality-plastipak-job.json",
    "raw_sha256": "9f65ba63b4b99455542c6323972294651151cb07014b95003ad59852e9cc7516",
    "own_issued_bridge_url": "https://www.plastipak.com/careers/",
    "bridge_raw_path": "/tmp/l3-quality-plastipak-careers.html",
    "bridge_sha256": "1f4aee6b0598281249614b723c6c3c4a400af48eef76bb6bd132b846f2c4b065",
    "raw": true,
    "note": "Company-issued job via Workday tenant linked by own careers page; JSON names Pineville LA,plastic container manufacturing and hiring issuer. Source date2026-09-23; no current-status change. Own claim_detail only quoted job words."
  }
]


FILE holds.csv
site_id,verdict,reason
SITE-012001,STILL_UNCERTAIN,"Need site NAICS/provenance at B and plant-locality reconciliation before C→B: held site NAICS is blank; banked FRS325510 and employer-padded Form5500group325500 do not settle a current site code. Own pages state325PaulAvenueFergusonMO63135/coating manufacture, while held postal city isSTLOUIS. No code/city/status/tier correction applied."
SITE-012503,STILL_UNCERTAIN,Need physical ZIP reconciliation: own contact page names2201OldSterlingtonRd MonroeLA71203; heldbankedITA/siteZIP71210. Ownblog confirmsMonroemanufacturing but doesnotsettlethe conflictingpostalcode. NoZIP/tier/statuschange.


FILE rawcheck.json
[
  {
    "source_url": "https://watsoncoatings.com/",
    "quote": "Your Trusted Coating Manufacturer.",
    "raw": true,
    "http_status": 200,
    "raw_sha256": "c65a16569be7f083a8d2df4a98d8e665bab937fa860e897a59d41354f82e07d7",
    "retrieved_date": "2026-11-06",
    "fabricated_suffix_rejected": true
  },
  {
    "source_url": "https://watsoncoatings.com/",
    "quote": "325 Paul Avenue Ferguson, MO 63135",
    "raw": true,
    "http_status": 200,
    "raw_sha256": "c65a16569be7f083a8d2df4a98d8e665bab937fa860e897a59d41354f82e07d7",
    "retrieved_date": "2026-11-06",
    "fabricated_suffix_rejected": true
  },
  {
    "source_url": "https://watsoncoatings.com/about-us/",
    "quote": "water-reducible alkyd, acrylic, polyester, and phenolic enamel coatings",
    "raw": true,
    "http_status": 200,
    "raw_sha256": "6caeb419c19c02a4cbf591ef2516ab76a5e8afb983bf0f434cf9ae054e024f33",
    "retrieved_date": "2026-11-06",
    "fabricated_suffix_rejected": true
  },
  {
    "source_url": "https://www.polyprocessing.com/contact-us/",
    "quote": "Monroe, LA 71203",
    "raw": true,
    "http_status": 200,
    "raw_text_path": "/tmp/l3-quality-poly-contact.txt",
    "raw_sha256": "2b07d4d59e9f2bae1e424460ffa23b7ba6ec95c3e43408aad55b1bd3d13fb6ec",
    "retrieved_date": "2026-11-06",
    "fabricated_suffix_rejected": true
  },
  {
    "source_url": "https://blog.polyprocessing.com/blog/poly-processing-tank-shipping-procedure",
    "quote": "Poly Processing has three strategically located manufacturing plants, headquartered in Monroe, Louisiana",
    "raw": true,
    "http_status": 200,
    "raw_text_path": "/tmp/l3-quality-poly-shipping.txt",
    "raw_sha256": "d8d26627dee00754ceb1394867d27f507d03afaccdb3dac0d5216c09fae44546",
    "retrieved_date": "2026-11-06",
    "fabricated_suffix_rejected": true
  }
]


FILE full-promotion-census.csv
site_id,org_id,street_address,city,state,zip,naics_primary,operating_status,tier_before,tier_after,establishment_id,own_source,own_quote,city_quote,issuer_quote,source_date,retrieved_date
SITE-012511,ORG-001033,4101 Pardue Rd,Pineville,LA,71360,326160,unknown,C,B,192504,https://plastipak.wd1.myworkdayjobs.com/wday/cxs/plastipak/Plastipak/job/Process-Technician--Day-Shift_REQ24583,"As a Process Technician, you operate equipment to manufacture plastic containers for leading consumer brands.","Plastipak - Pineville, LA",1000 Plastipak Packaging Inc. (US),2026-09-23,2026-11-06


FILE qcew.json
{
  "MO": {
    "strict326_before": 43,
    "strict326_after": 43,
    "qcew2023": 368
  },
  "LA": {
    "strict326_before": 9,
    "strict326_after": 9,
    "qcew2023": 117
  }
}
