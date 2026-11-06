Deep adversarial completion refute L2 Ohio C/U continuation2, branchagent/codex/oh-street-address-cu-2. Readonly; VERDICT APPROVE/REFUTE with demonstrated facts,nomerge/statusactions.
Controller07:55ESTwithdrawsstopnewrounds. Original819CUblankactiveOhioframe frozenon192,prior40werefirst40eligibleSCATTEREDrows,notfirst40broadindices. Controllerexplicitlycorrects153040+ to153000+ORIGINALindex;chooses100NEWindices0–100EXCLUDINGpriorheld70/SITE000140/EVD153070unused.40prior+100new+679future=819.100siteIDsunique,slots153000–153100except70fixed,NOgapreuse. Pinnedfreshmain5574d48f4060f3b03633399f707047db0314e28b.
Sourcepriority0existingaddressEVD,0currentsite-keyedFRSlinks;23knownZIPs/77unknown;23FRSIDsfromnotesover22sites,78noroute. Exact/strongITA/inspection/echoeligible0;37moderate/weakpacketmatchesexplicitlyEXCLUDED. NotesIDsareLEADSONLY;admissionneedsfreshofficialFRSRegistryId+EXACTheldlegal/tradename(punctuation/corporatesuffixonly)+notesstreet+recordedcityZIP5countyOH. No newalias/link/matcherstrength/owner/status/scopeinference. Sourceceilingregistry/address/supports_C,unchangedtiersC6U1.
Research23requests at12secspacing,22OK1UNAVAILABLE.9initialcandidates/evidence_proposed9.csv BEFOREaudit. Fixed9censusfirst6match3HTTP22=>strictgateFAIL;unavailable-only3retryat12sec=>7match2HTTP22=>strictgateFAIL. SameofficialendpointalternatequeryordercalibrationONLYknowns:firstPASS,secondHTTP22FAIL(three-known gatenotmet);NEVERusedoncandidates;deadfetchercodeomitted,failedlogandoneknownrawkept. NOaddressdisagreements/ITAtranscriptionerrors,NOabsenceinference.
Two proposedfillsWITHDRAWN BEFOREANYcanonicalwrite: SITE000025/EVD153012 andSITE000156/EVD153081;HOLDforfreshsourceunavailable,NOTfalseaddress/closed. IDspermanentlyretiredandabsentglobally. NOreplacement/resample and ORIGINAL9rowskeptinaudit.csv+bothattempt histories,7freshmatches/2uncheckableexplicit. Admittedsubset7/7freshmatches0errors in audit_admitted.csv;notclaiming9freshPASS. Rerunaudit.pyALWAYSsamplesoriginal9proposalpopulation,requiresallcurrentlyadmitted7registrysourcesfresh;reportsheldunavailable separately. Retry.py historicalall9gateFAILED,notreportedPASS.
Final100=7VERIFIED93STILL_UNCERTAIN. Sevenexistingstreet/source-onlyedits+7append-onlyregistry/address/supports_CEVD153015153018153020153029153078153088153100. No county/county_source/ZIP/tier/status/ring/registry/derivedfields,entities/merges/inclusioncalls. ActiveOhio348/1883→355/1883,pendingotherstreetPRsexcluded. Mainkeys/legacyEVDallpreservedexact7+7;retiredIDsabsent;structuredstreet/city/stateoverlapscan0hits.
93holdpartition79noroute(78noFRSlead+1unavailable),2audit-unavailablewithdrawals,1competingFRSstreet/city,7othercity/notes,2county,2identity/nonphysicalbinding. All100verdictssettlingfactsretained;679futureunworked,noexhaustivewebresearchclaim.
KnownchecksBEFOREmatcher:3LIVEFRSliteraladdresses+cityZIPcountyPOBoxnegatives;3freshknownliteraloperatoridentities+3unrelatedoperatornegatives,plus exacttrade-namecontrols/differentpolymernamesnegative. Check7fixed100selection/819slots/original9auditbinding+admitted7gate/realconflicts/boundary/byte-idempotence/streetZIPtierstatus+lateforeignID+RETIREDidinforeignshard rejectBEFOREwrites. Validator0/native-rowloss/diffPASS. Codeimportsprovenfirst134FRShelper;no sharedscriptsedited.
Potentialfailures: notes-onlyIDphantom/operatoraliasorwrongsite; corporate-suffixmatcherfalsepositive; unknownZIPsilentlyfilled; city/countymailinglocality; POBox/suite/ordinalloss; auditwithdrawalfavorscount/sampleorconcealsfailure; retiredIDreuse/globalcollision; legacyrowloss/replayfielddrift; 100NEWvsprior40doublecount; ownrawAPI recordwrongRegistryId. Challengeexactsource/data,notjustconsensus.
Run task/check.py; task/audit.py(networkfixed9); task/fetch.py --known; scripts/validate.py; scripts/check_row_loss.py --base5574d48f4060f3b03633399f707047db0314e28b --headHEAD. Fulltaskpath tasks/oh-street-address-cu-2-2026-11-06. FreshJSONraw/audit_raw,allfailurehistories/retirements/sourcecensus/identitybindings/819frame/README/journalkept. Do not conflate sameFRSfreshrecheckwithindependentsecondsource/currentoperation.

FILE fetch.py
"""Paced FRS fetches using the already-proven first-pass helper, no canonical writes."""
import csv,importlib.util,json,time,sys
from pathlib import Path
TASK=Path(__file__).resolve().parent;ROOT=TASK.parents[1]
spec=importlib.util.spec_from_file_location('held_oh_address',ROOT/'tasks/oh-street-address-2026-11-06/build.py');frs=importlib.util.module_from_spec(spec);spec.loader.exec_module(frs);frs.TASK=TASK
read,write=frs.read,frs.write
def known():
 cases=[('110000745766','160 Parker Ct','Chardon','44024'),('110000391415','350 N Buckeye St','Bellevue','44811'),('110000383941','555 W Linfoot St','Wauseon','43567')]
 out=[]
 for rid,street,city,zip_ in cases:
  f=frs.facility(frs.fetch(rid,'known_raw'),rid)
  assert frs.streetkey(f['LocationAddress'])==frs.streetkey(street),(rid,f)
  assert frs.norm(f['CityName'])==frs.norm(city) and f['ZipCode'][:5]==zip_,f
  s=dict(city=city,zip=zip_,county=f['CountyName'])
  assert not frs.conflict(s,f)
  for field,value in [('city','WRONG CITY'),('zip','00000'),('county','WRONG COUNTY')]:assert frs.conflict(dict(s,**{field:value}),f)
  assert frs.conflict(s,dict(f,LocationAddress='PO BOX 99'))
  out.append(dict(registry_id=rid,expected_street=street,city=city,zip=zip_,result='PASS'));write(TASK/'known_answers.csv',out)
  print('KNOWN',rid,'PASS',flush=True);time.sleep(12)
 print('PASS3live known answers plus city/ZIP/county/PO-box mutations',flush=True)
def main():
 assert len(read(TASK/'known_answers.csv'))==3,'known gate incomplete'
 ids=sorted({r['registry_id'] for r in read(TASK/'registry_links_input.csv')+read(TASK/'frs_notes_leads.csv')});out=[]
 for rid in ids:
  try:
   if (TASK/'raw'/f'{rid}.json').exists():data=json.loads((TASK/'raw'/f'{rid}.json').read_text())
   else:data=frs.fetch(rid)
   f=frs.facility(data,rid);result='OK';error=''
  except Exception as ex:result='UNAVAILABLE';error=str(ex)
  out.append(dict(registry_id=rid,result=result,error=error));write(TASK/'fetch_log.csv',out)
  print(rid,result,error,flush=True);time.sleep(12)
 assert len(out)==len(ids)
 print('Fetch yield',len(out),'expected registry IDs',len(ids),'OK',sum(r['result']=='OK' for r in out),flush=True)
if __name__=='__main__':
 if '--known' in sys.argv:known()
 else:main()

FILE build.py
"""C/U federal street pass; all source, scope and namespace checks precede canonical writes."""
import csv,json,re,sys
from pathlib import Path
from fetch import TASK,ROOT,frs,read,write
sys.path.insert(0,str(ROOT/'scripts'))
from shard_io import append_sorted
DATE='2026-11-06'
def namekey(value):
 return ' '.join(t for t in re.findall('[A-Z0-9]+',value.upper()) if t not in {'THE','INC','INCORPORATED','LLC','CORP','CORPORATION','CO','COMPANY','LTD','LIMITED'})
def identity(s,f):
 names=[s['held_legal_name']]+s['held_trade_names'].split(';')
 return any(namekey(n)==namekey(f.get('FacilityName') or '') for n in names if n.strip())

ITA_URL='https://www.osha.gov/sites/default/largefiles/ITA_300A_Summary_Data_2025_through_08-31-2026.csv'
ITA_SHA='69c0d987d453471293b092640b392eaef44b21cb55446a1c9b69ad8b54bf703a'
def note_streets(s):
 out=re.findall(r'(?i)(?:Address[^:]{0,120}:|at)\s*(\d+\s+[^,;()]+),\s*'+re.escape(s['city']),s['notes'])
 m=re.search(r'(?i)\bstreet(?:\s*\([^)]*\))?:\s*(.+)',s['notes'])
 if m:out.append(re.split(r'\.\s+(?=PASS|BAND|CERT|Ring|INTEGRATION|Parcel|Re-pointed|NAICS|Source|(?i:county UNVERIFIED)|\[)',m[1])[0].rstrip('. '))
 return out
def plan():
 frame=read(TASK/'frame.csv');selected=[s for s in frame if s['selected']=='yes'];links=read(TASK/'registry_links_input.csv')+read(TASK/'frs_notes_leads.csv');ids={s['site_id'] for s in selected}
 assert len(frame)==len({s['site_id'] for s in frame})==819
 assert len(selected)==len(ids)==100 and len({s['reserved_evidence_id'] for s in frame})==819
 assert [s['reserved_evidence_id'] for s in frame]==[f'EVD-{153000+i:06d}' for i in range(819)]
 assert ids=={s['site_id'] for i,s in enumerate(frame) if i<=100 and i!=70},'selected cohort changed'
 assert {r['site_id'] for r in links}<=ids
 byid={s['site_id']:s for s in selected}
 assert all(r['registry_id'] in re.findall(r'\b110\d{9}\b',byid[r['site_id']]['notes']) and r['org_id']==byid[r['site_id']]['org_id'] for r in read(TASK/'frs_notes_leads.csv')),'notes lead ID/operator not frozen in site notes'
 fetches={r['registry_id']:r for r in read(TASK/'fetch_log.csv')}
 assert fetches.keys()=={r['registry_id'] for r in links},'FRS request yield incomplete'
 ita={r['establishment_id']:r for r in read(ROOT/'tasks/osha-ita-2026-11-01/establishments.csv')}
 matches=[m for m in read(ROOT/'tasks/osha-ita-2026-11-01/site_matches.csv') if m['site_id'] in ids and m['match_strength'] in ('exact','strong')]
 existing=[e for e in read(ROOT/'data/evidence_sites_OH.csv') if e['record_id'] in ids and e['claim_type']=='address' and e['created_by']!='atlas-L2-oh-address-cu-2']
 assert not existing,'new held address evidence needs priority/adjudication before this frozen pass'
 ev=[];verdicts=[];transcription=[]
 for s in selected:
  sid=s['site_id'];why=[];candidates=[];unavailable=[]
  for link in [r for r in links if r['site_id']==sid]:
   rid=link['registry_id'];row=fetches[rid]
   if link['org_id']!=s['org_id']:why.append('registry link operator differs from Atlas operator')
   if row['result']!='OK':unavailable.append(rid+': '+row['error']);continue
   f=frs.facility(json.loads((TASK/'raw'/f'{rid}.json').read_text()),rid)
   if not identity(s,f):why.append('fresh FRS facility name lacks exact held legal/trade-name identity; operator adjudication needed')
   if link.get('lead_basis') and not note_streets(s):why.append('notes-only identifier lacks street binding to this site')
   conflict=frs.conflict(s,f)
   if conflict:why.append('FRS '+rid+': '+conflict)
   if re.search(r'(?i)\bP\.?\s*O\.?\s*BOX\b|mailing',f.get('SupplementalLocation') or ''):why.append('supplemental mailing/PO-box ambiguity')
   candidates.append(dict(street=f['LocationAddress'],source_class='registry',ref=frs.FRSU+rid+'&output=JSON',date=DATE,
                          effect='supports_C',notes=f"EPA FRS registry {rid}; fetched {DATE}; raw copy tasks/oh-street-address-cu-2-2026-11-06/raw/{rid}.json",source_id=rid))
  for m in [m for m in matches if m['site_id']==sid]:
   r=ita[m['establishment_id']]
   assert m['street']==r['street'] and m['city']==r['city'] and m['zip5']==r['zip5'],'inherited ITA transcription drift'
   transcription.append(dict(site_id=sid,establishment_id=r['establishment_id'],street=r['street'],city=r['city'],zip=r['zip5'],result='PASS'))
   if m['org_id']!=s['org_id']:why.append('ITA matched operator differs from current Atlas operator');continue
   if frs.norm(r['city'])!=frs.norm(s['city']) or not re.fullmatch(r'\d{5}(?:-\d{4})?',s['zip']) or r['zip5']!=s['zip'][:5]:
    why.append('ITA city/ZIP conflict or missing');continue
   if not re.match(r'^\d+\s+\S+',r['street']) or re.search(r'(?i)\bP\.?\s*O\.?\s*BOX\b',r['street']):
    why.append('ITA physical street ambiguous');continue
   candidates.append(dict(street=r['street'],source_class='government_filing',ref=ITA_URL,date='2026-11-01',effect='supports_A',
     notes=f"OSHA ITA CY2025 establishment_ID {r['establishment_id']}; date_submitted {r['date_submitted']}; owner-supplied filtered extract SHA-256 {ITA_SHA}; inherited bulk exception controller2026-11-06",source_id=r['establishment_id']))
  if len({frs.streetkey(c['street']) for c in candidates})>1:why.append('federal sources disagree on street')
  street=candidates[0]['street'] if candidates else ''
  # shortcut: written ordinals/dotted diagonals remain distinct; adjudicate held aliases before widening matching.
  if candidates and any(frs.streetkey(n)!=frs.streetkey(street) for n in note_streets(s)):why.append('notes street conflicts; dated address adjudication needed')
  if sid in {r['site_id'] for r in read(TASK/'retired_ids.csv')}:why.append('cited FRS audit source unavailable after bounded retry; successful fresh recheck required')
  if not candidates:why.append('need admissible physical street witness; no qualifying federal route or source unavailable')
  v=dict(site_id=sid,verdict='STILL_UNCERTAIN' if why else 'VERIFIED',street_address=street,evidence_id='' if why else s['reserved_evidence_id'],reason='; '.join(why),availability='; '.join(unavailable))
  verdicts.append(v)
  if not why:
   c=candidates[0];ev.append(dict(evidence_id=s['reserved_evidence_id'],record_table='sites',record_id=sid,claim_type='address',
     claim_detail=f"street_address {street}, {s['city']}, OH {s['zip']}",
     source_class=c['source_class'],source_ref=c['ref'],observed_date=c['date'],tier_effect=c['effect'],created_by='atlas-L2-oh-address-cu-2',
     notes=c['notes']+'. County, county_source, ZIP, record tier and status unchanged.'))
 assert len(verdicts)==len({v['site_id'] for v in verdicts})==100
 return selected,links,verdicts,ev,transcription
def run(apply=False):
 selected,links,verdicts,ev,transcription=plan();sites=read(ROOT/'data/sites_OH.csv');byid={s['site_id']:s for s in sites};frozen={s['site_id']:s for s in selected};eb={e['record_id']:e for e in ev}
 live_links={(r['org_id'],r['registry_id'],r['site_id']) for r in read(ROOT/'data/registry_links.csv') if r['registry']=='FRS'}
 assert all((r['org_id'],r['registry_id'],r['site_id']) in live_links for r in read(TASK/'registry_links_input.csv')),'main link no longer held'
 existing={};planned_ids={e['evidence_id'] for e in ev};retired={r['evidence_id'] for r in read(TASK/'retired_ids.csv')}
 for p in (ROOT/'data').glob('evidence_*.csv'):
  for e in read(p):
   assert e['evidence_id'] not in retired,'retired audit-withdrawal ID exists in canonical data'
   if e['evidence_id'] in planned_ids:existing.setdefault(e['evidence_id'],[]).append((p.name,e))
 new=[]
 for v in verdicts:
  if v['verdict']!='VERIFIED':continue
  s=byid[v['site_id']];old=frozen[s['site_id']];e=eb[s['site_id']]
  for k in ('org_id','city','state','zip','county','county_source','verification_tier','operating_status','notes'):assert s[k]==old[k],(s['site_id'],k,'main changed')
  assert s['verification_tier'] in ('C','U') and s['operating_status']=='active' and not old['street_address']
  assert s['street_address'] in ('',v['street_address']),'pre-existing street conflict'
  have=existing.get(e['evidence_id'],[]);assert not have or have==[('evidence_sites_OH.csv',e)],'global evidence ID collision'
  if not have:new.append(e)
 if apply:
  (TASK/'backups').mkdir(exist_ok=True)
  for name in ('sites_OH.csv','evidence_sites_OH.csv'):
   p=ROOT/'data'/name;b=TASK/'backups'/name
   if not b.exists():b.write_bytes(p.read_bytes())
  for v in verdicts:
   if v['verdict']!='VERIFIED':continue
   s=byid[v['site_id']];e=eb[s['site_id']];s['street_address']=v['street_address']
   if e['source_ref'] not in s['sources']:s['sources']+='; '+e['source_ref']
  if new:append_sorted(ROOT/'data/evidence_sites_OH.csv',new,'evidence_id')
  write(ROOT/'data/sites_OH.csv',sites)
 write(TASK/'verdicts.csv',verdicts);write(TASK/'holds.csv',[v for v in verdicts if v['verdict']!='VERIFIED'])
 if ev:write(TASK/'evidence.csv',ev)
 if transcription:write(TASK/'ita_transcription.csv',transcription)
 active=[s for s in sites if s['operating_status']=='active'];actual=sum(bool(s['street_address']) for s in active)
 before=actual-len(ev) if all(byid[e['record_id']]['street_address'] for e in ev) else actual
 summary=dict(cu_active_blank_cohort=819,prior_worked=40,worked=100,unworked_cohort=679,
              fills=len(ev),holds=100-len(ev),active_ohio_sites=len(active),before_streets=before,after_streets=before+len(ev))
 (TASK/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary)
if __name__=='__main__':run('--apply' in sys.argv)

FILE check.py
"""Federal-pass boundary/replay and fail-before-write mutations, in an isolated data tree."""
import contextlib,hashlib,io,shutil,tempfile
from pathlib import Path
import build
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 root=build.ROOT;selected,links,verdicts,ev,transcription=build.plan()
 identity_known=build.read(build.TASK/'known_identity.csv')
 assert len(identity_known)==3 and all(r['result']=='PASS' and r['negative_wrong_operator']=='rejected' for r in identity_known)
 frame=build.read(build.TASK/'frame.csv')
 assert [r['reserved_evidence_id'] for r in frame]==[f'EVD-{153000+i:06d}' for i in range(819)]
 assert [r['site_id'] for r in selected]==[r['site_id'] for i,r in enumerate(frame) if i<=100 and i!=70]
 for name,raw in [('Lincoln Electric','LINCOLN ELECTRIC CO'),('ABC, LLC','ABC INC'),('The Parker Corporation','PARKER INC')]:
  assert build.identity(dict(held_legal_name=name,held_trade_names=''),dict(FacilityName=raw))
 assert build.identity(dict(held_legal_name='Held Parent',held_trade_names='Old Registrant;Other Name'),dict(FacilityName='OLD REGISTRANT INC'))
 assert not build.identity(dict(held_legal_name='Held Parent',held_trade_names=''),dict(FacilityName='Different Operator'))
 assert not build.identity(dict(held_legal_name='ABC Polymers',held_trade_names=''),dict(FacilityName='ABC Plastics'))
 audit=build.read(build.TASK/'audit.csv')
 import random
 proposed=build.read(build.TASK/'evidence_proposed9.csv')
 sample=random.Random(20261106).sample(sorted(proposed,key=lambda e:e['record_id']),min(30,len(proposed)))
 assert {r['site_id'] for r in audit}=={e['record_id'] for e in sample} and len(audit)==len(sample)
 assert all(r['fresh_source_match']=='yes' and not r['error'] for r in audit if r['source_class']=='registry' and r['site_id'] in {e['record_id'] for e in ev})

 assert build.note_streets(dict(city='South Euclid',notes='Street (per Grok): 4321 Glenridge Road. county UNVERIFIED — Grok county_check=TRUE'))==['4321 Glenridge Road']
 assert len(ev)==7,'frozen source-adjudication yield changed'
 for sid in ('SITE-000011','SITE-000053','SITE-000108','SITE-000135','SITE-000165','SITE-000170','SITE-000177'):
  assert next(v for v in verdicts if v['site_id']==sid)['verdict']=='STILL_UNCERTAIN',sid
 expected=len(ev)
 with tempfile.TemporaryDirectory() as tmp:
  build.ROOT=Path(tmp);(build.ROOT/'data').mkdir()
  for p in (root/'data').glob('evidence_*.csv'):shutil.copyfile(p,build.ROOT/'data'/p.name)
  for name in ('sites_OH.csv','registry_links.csv'):shutil.copyfile(root/'data'/name,build.ROOT/'data'/name)
  for name in ('establishments.csv','site_matches.csv'):
   p=build.ROOT/'tasks/osha-ita-2026-11-01'/name;p.parent.mkdir(parents=True,exist_ok=True)
   shutil.copyfile(root/'tasks/osha-ita-2026-11-01'/name,p)
  frozen={s['site_id']:s for s in selected};before=build.read(build.ROOT/'data/sites_OH.csv')
  for s in before:
   if s['site_id'] in frozen:
    for k in s:s[k]=frozen[s['site_id']][k]
  build.write(build.ROOT/'data/sites_OH.csv',before)
  p=build.ROOT/'data/evidence_sites_OH.csv';old_evidence=[r for r in build.read(p) if r['created_by']!='atlas-L2-oh-address-cu-2'];build.write(p,old_evidence)
  with contextlib.redirect_stdout(io.StringIO()):build.run(apply=True)
  after=build.read(build.ROOT/'data/sites_OH.csv');changed=[]
  assert len(before)==len(after)
  for a,b in zip(before,after):
   fields={k for k in a if a[k]!=b[k]};assert fields<={'street_address','sources'},(a['site_id'],fields)
   if fields:
    changed.append(b);assert not a['street_address'] and b['street_address'] and a['verification_tier'] in ('C','U') and a['operating_status']=='active'
  assert len(changed)==expected
  paths=list((build.ROOT/'data').glob('*.csv'));hashes={p.name:digest(p) for p in paths}
  with contextlib.redirect_stdout(io.StringIO()):build.run(apply=True)
  assert hashes=={p.name:digest(p) for p in paths},'not byte-idempotent'
  target=changed[0]
  for field,value in [('street_address','999 WRONG ROAD'),('zip','00000'),('verification_tier','A'),('operating_status','closed')]:
   original=target[field];target[field]=value;build.write(build.ROOT/'data/sites_OH.csv',after)
   hashes={p.name:digest(p) for p in paths}
   try:
    with contextlib.redirect_stdout(io.StringIO()):build.run(apply=True)
   except AssertionError:pass
   else:raise AssertionError('injected '+field+' drift silently accepted')
   assert hashes=={p.name:digest(p) for p in paths},'canonical write before drift refusal'
   target[field]=original;build.write(build.ROOT/'data/sites_OH.csv',after)
  foreign=build.ROOT/'data/evidence_sites_ZZ.csv'
  retired_row=dict(ev[-1],evidence_id=build.read(build.TASK/'retired_ids.csv')[0]['evidence_id'])
  for foreign_row in (ev[-1],retired_row):
   build.write(foreign,[foreign_row])
   paths=list((build.ROOT/'data').glob('*.csv'));hashes={p.name:digest(p) for p in paths}
   try:
    with contextlib.redirect_stdout(io.StringIO()):build.run(apply=True)
   except AssertionError:pass
   else:raise AssertionError('foreign-shard or retired evidence collision accepted')
   assert hashes=={p.name:digest(p) for p in paths},'canonical write before ID collision refusal'

 build.ROOT=root
 print(f'PASS {expected} fills; only street/sources; byte-idempotent; street/ZIP/tier/status/foreign-ID mutations reject before writes')
if __name__=='__main__':main()

FILE audit.py
"""Paced seeded fresh FRS audit, plus inherited-ITA transcription when applicable."""
import csv,json,random,re,time
from fetch import TASK,ROOT,frs,read,write
from build import identity
evidence=read(TASK/'evidence_proposed9.csv');admitted={e['record_id'] for e in read(TASK/'evidence.csv')};sites={s['site_id']:s for s in read(TASK/'frame.csv')}
links=read(TASK/'registry_links_input.csv')+read(TASK/'frs_notes_leads.csv');sample=random.Random(20261106).sample(sorted(evidence,key=lambda e:e['record_id']),min(30,len(evidence)))
ita=read(ROOT/'tasks/osha-ita-2026-11-01/site_matches.csv')
out=[]
for e in sample:
 sid=e['record_id'];s=sites[sid];transcription='not_ITA';error='';detail='';corroborated=False
 street=e['claim_detail'].removeprefix('street_address ').split(', '+s['city']+', OH ',1)[0]
 if e['source_class']=='government_filing':
  transcription='PASS' if any(m['site_id']==sid and m['match_strength'] in ('exact','strong') and frs.streetkey(m['street'])==frs.streetkey(street) and frs.norm(m['city'])==frs.norm(s['city']) and m['zip5']==s['zip'][:5] for m in ita) else 'FAIL'
  if transcription=='FAIL':error='ITA transcription mismatch'
 rid=re.search(r'registry_id=(\d+)',e['source_ref'])[1] if e['source_class']=='registry' else next(r['registry_id'] for r in links if r['site_id']==sid)
 try:
  f=frs.facility(frs.fetch(rid,'audit_raw'),rid);mismatch=frs.conflict(s,f)
  if not identity(s,f):raise ValueError('fresh FRS operator identity differs')
  if mismatch:raise ValueError('FRS not corroborating: '+mismatch)
  if frs.streetkey(f['LocationAddress'])!=frs.streetkey(street):error='fresh FRS street disagrees: '+f['LocationAddress']
  else:corroborated=True;detail='fresh identifier,street,city,ZIP,county,state agree'
 except Exception as ex:detail=str(ex)
 out.append(dict(site_id=sid,source_class=e['source_class'],registry_id=rid,transcription=transcription,fresh_source_match='yes' if corroborated else 'no',detail=detail,error=error))
 write(TASK/'audit.csv',out);print(sid,corroborated,error,detail,flush=True);time.sleep(12)
summary=dict(original_candidates=len(evidence),accepted_fills=len(admitted),sampled=len(out),ita_sampled=sum(r['transcription']!='not_ITA' for r in out),transcription_errors=sum(r['transcription']=='FAIL' for r in out),
             fresh_source_matches=sum(r['fresh_source_match']=='yes' for r in out),not_freshly_checkable=sum(r['fresh_source_match']=='no' and not r['error'] for r in out),address_errors=sum(bool(r['error']) for r in out))
(TASK/'audit_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary)
assert len(out)==min(30,len(evidence)) and summary['address_errors']==0 and summary['transcription_errors']==0
# Registry fill rows require their own cited FRS source to re-fetch, not the inherited-bulk exception.
assert all(r['fresh_source_match']=='yes' for r in out if r['source_class']=='registry' and r['site_id'] in admitted),'registry audit source unavailable'

FILE retry_audit.py
"""Retry only unavailable registry audit rows; retain the original failures and reassert the full gate."""
import json,time
from fetch import TASK,frs,read,write
from build import identity
rows=read(TASK/'audit.csv');sites={s['site_id']:s for s in read(TASK/'frame.csv')};ev={e['record_id']:e for e in read(TASK/'evidence.csv')};log=[]
for r in rows:
 if r['fresh_source_match']=='yes':continue
 old=r['detail'];s=sites[r['site_id']];e=ev[r['site_id']];street=e['claim_detail'].removeprefix('street_address ').split(', '+s['city']+', OH ',1)[0]
 try:
  f=frs.facility(frs.fetch(r['registry_id'],'audit_raw'),r['registry_id'])
  assert identity(s,f),'fresh operator identity differs'
  assert not frs.conflict(s,f),frs.conflict(s,f)
  assert frs.streetkey(f['LocationAddress'])==frs.streetkey(street),'fresh street disagrees'
  r.update(fresh_source_match='yes',detail='fresh identifier,street,city,ZIP,county,state agree on bounded retry',error='')
 except AssertionError as ex:r.update(detail=str(ex),error=str(ex))
 except Exception as ex:r.update(detail=str(ex),error='')
 log.append(dict(site_id=r['site_id'],registry_id=r['registry_id'],prior=old,after=r['detail'],result=r['fresh_source_match']))
 write(TASK/'audit.csv',rows);write(TASK/'audit_retry_log.csv',log);print(log[-1],flush=True);time.sleep(12)
summary=dict(accepted_fills=len(ev),sampled=len(rows),ita_sampled=sum(r['transcription']!='not_ITA' for r in rows),transcription_errors=sum(r['transcription']=='FAIL' for r in rows),fresh_source_matches=sum(r['fresh_source_match']=='yes' for r in rows),not_freshly_checkable=sum(r['fresh_source_match']=='no' and not r['error'] for r in rows),address_errors=sum(bool(r['error']) for r in rows))
(TASK/'audit_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary)
assert summary['address_errors']==0 and summary['transcription_errors']==0 and summary['fresh_source_matches']==len(rows)==min(30,len(ev))

INPUT100;fullnotesinframe.csv
site_id,org_id,city,zip,county,verification_tier,reserved_evidence_id
SITE-000011,ORG-000012,Akron,44308,Summit,C,EVD-153000
SITE-000012,ORG-000013,Akron,,Summit,C,EVD-153001
SITE-000013,ORG-000014,Akron,,Summit,C,EVD-153002
SITE-000015,ORG-000016,Akron,,Summit,U,EVD-153003
SITE-000016,ORG-000017,Akron,,Summit,U,EVD-153004
SITE-000018,ORG-000019,Akron,,Summit,U,EVD-153005
SITE-000019,ORG-000020,Akron,,Summit,U,EVD-153006
SITE-000020,ORG-000021,Akron,,Summit,U,EVD-153007
SITE-000021,ORG-000022,Akron,,Summit,U,EVD-153008
SITE-000022,ORG-000023,Akron,,Summit,U,EVD-153009
SITE-000023,ORG-000024,Akron,,Summit,U,EVD-153010
SITE-000024,ORG-000025,Akron,,Summit,C,EVD-153011
SITE-000025,ORG-000026,Akron,44305,Summit,C,EVD-153012
SITE-000026,ORG-000027,Akron,44221,Summit,C,EVD-153013
SITE-000027,ORG-000028,Akron,,Summit,C,EVD-153014
SITE-000028,ORG-000029,Akron,44305,Summit,C,EVD-153015
SITE-000029,ORG-000029,Barberton,,Summit,C,EVD-153016
SITE-000030,ORG-000030,Akron,,Summit,C,EVD-153017
SITE-000031,ORG-000031,Akron,44314,Summit,C,EVD-153018
SITE-000032,ORG-000032,Akron,,Summit,C,EVD-153019
SITE-000034,ORG-000034,Akron,44305,Summit,C,EVD-153020
SITE-000036,ORG-000036,Akron,,Summit,C,EVD-153021
SITE-000040,ORG-000040,Akron,,Summit,C,EVD-153022
SITE-000041,ORG-000041,Akron,,Summit,C,EVD-153023
SITE-000042,ORG-000042,Akron,44321,Summit,C,EVD-153024
SITE-000049,ORG-000049,Akron,,Summit,U,EVD-153025
SITE-000053,ORG-000053,Akron,44333,Summit,U,EVD-153026
SITE-000054,ORG-000054,Cuyahoga Falls,44310,Summit,C,EVD-153027
SITE-000055,ORG-000055,Cuyahoga Falls,,Summit,C,EVD-153028
SITE-000057,ORG-000057,Cuyahoga Falls,44221,Summit,U,EVD-153029
SITE-000059,ORG-000059,Stow,,Summit,C,EVD-153030
SITE-000062,ORG-000062,Tallmadge,,Summit,C,EVD-153031
SITE-000063,ORG-000063,Tallmadge,,Summit,C,EVD-153032
SITE-000064,ORG-000064,Tallmadge,,Summit,C,EVD-153033
SITE-000065,ORG-000065,Hudson,,Summit,C,EVD-153034
SITE-000066,ORG-000066,Hudson,,Summit,C,EVD-153035
SITE-000067,ORG-000067,Hudson,,Summit,C,EVD-153036
SITE-000068,ORG-000068,Macedonia,,Summit,C,EVD-153037
SITE-000069,ORG-000069,Macedonia,,Summit,C,EVD-153038
SITE-000073,ORG-000073,Twinsburg,,Summit,C,EVD-153039
SITE-000080,ORG-000080,Barberton,44203,Summit,C,EVD-153040
SITE-000084,ORG-000084,Barberton,,Summit,U,EVD-153041
SITE-000089,ORG-000089,Akron,,Summit,U,EVD-153042
SITE-000090,ORG-000090,Akron,,Summit,C,EVD-153043
SITE-000091,ORG-000091,Akron,,Summit,U,EVD-153044
SITE-000093,ORG-000093,Akron,,Summit,C,EVD-153045
SITE-000094,ORG-000094,Akron,,Summit,U,EVD-153046
SITE-000095,ORG-000095,Akron,,Summit,U,EVD-153047
SITE-000096,ORG-000096,Akron,,Summit,U,EVD-153048
SITE-000097,ORG-000097,Akron,,Summit,U,EVD-153049
SITE-000098,ORG-000098,Akron,,Summit,U,EVD-153050
SITE-000099,ORG-000099,Akron,,Summit,U,EVD-153051
SITE-000100,ORG-000100,Hudson,,Summit,U,EVD-153052
SITE-000102,ORG-000102,Hudson,,Summit,U,EVD-153053
SITE-000103,ORG-000103,Copley,,Summit,U,EVD-153054
SITE-000104,ORG-000105,Strongsville,,Cuyahoga,C,EVD-153055
SITE-000108,ORG-000108,Cleveland,44115,Cuyahoga,C,EVD-153056
SITE-000118,ORG-000119,Strongsville,,Cuyahoga,C,EVD-153057
SITE-000119,ORG-000120,Bedford,,Cuyahoga,C,EVD-153058
SITE-000121,ORG-000122,Solon,,Cuyahoga,U,EVD-153059
SITE-000122,ORG-000123,Woodmere,,Cuyahoga,U,EVD-153060
SITE-000127,ORG-000128,North Randall,,Cuyahoga,U,EVD-153061
SITE-000128,ORG-000129,Cleveland,,Cuyahoga,C,EVD-153062
SITE-000130,ORG-000131,Solon,,Cuyahoga,C,EVD-153063
SITE-000131,ORG-000132,Cleveland,44146,Cuyahoga,C,EVD-153064
SITE-000132,ORG-000132,Brecksville,,Cuyahoga,C,EVD-153065
SITE-000135,ORG-000135,Independence,44131,Cuyahoga,U,EVD-153066
SITE-000137,ORG-000137,Middleburg Heights,,Cuyahoga,U,EVD-153067
SITE-000138,ORG-000138,Solon,,Cuyahoga,C,EVD-153068
SITE-000139,ORG-000139,Warrensville Heights,,Cuyahoga,U,EVD-153069
SITE-000142,ORG-000142,Westlake,,Cuyahoga,C,EVD-153071
SITE-000144,ORG-000144,Solon,,Cuyahoga,U,EVD-153072
SITE-000146,ORG-000146,Cleveland,,Cuyahoga,U,EVD-153073
SITE-000147,ORG-000147,Westlake,,Cuyahoga,C,EVD-153074
SITE-000148,ORG-000148,Strongsville,,Cuyahoga,C,EVD-153075
SITE-000149,ORG-000149,Euclid,,Cuyahoga,U,EVD-153076
SITE-000152,ORG-000152,Oakwood Village,,Cuyahoga,C,EVD-153077
SITE-000153,ORG-000153,North Olmsted,44070,Cuyahoga,C,EVD-153078
SITE-000154,ORG-000154,Euclid,44117,Cuyahoga,C,EVD-153079
SITE-000155,ORG-000155,Beachwood,44100,Cuyahoga,C,EVD-153080
SITE-000156,ORG-000156,Solon,44139,Cuyahoga,C,EVD-153081
SITE-000157,ORG-000157,Brooklyn Heights,,Cuyahoga,C,EVD-153082
SITE-000159,ORG-000159,Cleveland,,Cuyahoga,U,EVD-153083
SITE-000160,ORG-000160,Cleveland,,Cuyahoga,U,EVD-153084
SITE-000161,ORG-000161,Cleveland,,Cuyahoga,U,EVD-153085
SITE-000162,ORG-000162,Cleveland,,Cuyahoga,U,EVD-153086
SITE-000163,ORG-000163,Cleveland,,Cuyahoga,U,EVD-153087
SITE-000164,ORG-000164,Cleveland,44195,Cuyahoga,C,EVD-153088
SITE-000165,ORG-000165,Cleveland,44130,Cuyahoga,U,EVD-153089
SITE-000166,ORG-000166,Cleveland,,Cuyahoga,U,EVD-153090
SITE-000167,ORG-000006,Beachwood,,Cuyahoga,C,EVD-153091
SITE-000169,ORG-000007,Mayfield Heights,,Cuyahoga,C,EVD-153092
SITE-000170,ORG-000035,Solon,44139,Cuyahoga,C,EVD-153093
SITE-000172,ORG-000103,Solon,,Cuyahoga,C,EVD-153094
SITE-000173,ORG-000073,Cleveland,,Cuyahoga,U,EVD-153095
SITE-000176,ORG-000169,Twinsburg,,Summit,C,EVD-153096
SITE-000177,ORG-000170,Barberton,44203,Summit,U,EVD-153097
SITE-000178,ORG-000171,Akron,,Summit,U,EVD-153098
SITE-000181,ORG-000174,Mogadore,,Summit,C,EVD-153099
SITE-000182,ORG-000175,Cuyahoga Falls,44221,Summit,C,EVD-153100

FILE evidence.csv
evidence_id,record_table,record_id,claim_type,claim_detail,source_class,source_ref,observed_date,tier_effect,created_by,notes
EVD-153015,sites,SITE-000028,address,"street_address 2887 GILCHRIST ROAD, Akron, OH 44305",registry,https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id=110004720384&output=JSON,2026-11-06,supports_C,atlas-L2-oh-address-cu-2,"EPA FRS registry 110004720384; fetched 2026-11-06; raw copy tasks/oh-street-address-cu-2-2026-11-06/raw/110004720384.json. County, county_source, ZIP, record tier and status unchanged."
EVD-153018,sites,SITE-000031,address,"street_address 2719 CORY AVENUE, Akron, OH 44314",registry,https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id=110001625180&output=JSON,2026-11-06,supports_C,atlas-L2-oh-address-cu-2,"EPA FRS registry 110001625180; fetched 2026-11-06; raw copy tasks/oh-street-address-cu-2-2026-11-06/raw/110001625180.json. County, county_source, ZIP, record tier and status unchanged."
EVD-153020,sites,SITE-000034,address,"street_address 571 KENNEDY RD, Akron, OH 44305",registry,https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id=110004711660&output=JSON,2026-11-06,supports_C,atlas-L2-oh-address-cu-2,"EPA FRS registry 110004711660; fetched 2026-11-06; raw copy tasks/oh-street-address-cu-2-2026-11-06/raw/110004711660.json. County, county_source, ZIP, record tier and status unchanged."
EVD-153029,sites,SITE-000057,address,"street_address 2020 FRONT ST STE 301, Cuyahoga Falls, OH 44221",registry,https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id=110010739772&output=JSON,2026-11-06,supports_C,atlas-L2-oh-address-cu-2,"EPA FRS registry 110010739772; fetched 2026-11-06; raw copy tasks/oh-street-address-cu-2-2026-11-06/raw/110010739772.json. County, county_source, ZIP, record tier and status unchanged."
EVD-153078,sites,SITE-000153,address,"street_address 25300 AL MOEN DR, North Olmsted, OH 44070",registry,https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id=110004733646&output=JSON,2026-11-06,supports_C,atlas-L2-oh-address-cu-2,"EPA FRS registry 110004733646; fetched 2026-11-06; raw copy tasks/oh-street-address-cu-2-2026-11-06/raw/110004733646.json. County, county_source, ZIP, record tier and status unchanged."
EVD-153088,sites,SITE-000164,address,"street_address 9500 EUCLID AVENUE, Cleveland, OH 44195",registry,https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id=110063155482&output=JSON,2026-11-06,supports_C,atlas-L2-oh-address-cu-2,"EPA FRS registry 110063155482; fetched 2026-11-06; raw copy tasks/oh-street-address-cu-2-2026-11-06/raw/110063155482.json. County, county_source, ZIP, record tier and status unchanged."
EVD-153100,sites,SITE-000182,address,"street_address 1365 ORLEN AVE, Cuyahoga Falls, OH 44221",registry,https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id=110006269313&output=JSON,2026-11-06,supports_C,atlas-L2-oh-address-cu-2,"EPA FRS registry 110006269313; fetched 2026-11-06; raw copy tasks/oh-street-address-cu-2-2026-11-06/raw/110006269313.json. County, county_source, ZIP, record tier and status unchanged."

FILE evidence_proposed9.csv
evidence_id,record_table,record_id,claim_type,claim_detail,source_class,source_ref,observed_date,tier_effect,created_by,notes
EVD-153012,sites,SITE-000025,address,"street_address 1070 EVANS AVE, Akron, OH 44305",registry,https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id=110004599596&output=JSON,2026-11-06,supports_C,atlas-L2-oh-address-cu-2,"EPA FRS registry 110004599596; fetched 2026-11-06; raw copy tasks/oh-street-address-cu-2-2026-11-06/raw/110004599596.json. County, county_source, ZIP, record tier and status unchanged."
EVD-153015,sites,SITE-000028,address,"street_address 2887 GILCHRIST ROAD, Akron, OH 44305",registry,https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id=110004720384&output=JSON,2026-11-06,supports_C,atlas-L2-oh-address-cu-2,"EPA FRS registry 110004720384; fetched 2026-11-06; raw copy tasks/oh-street-address-cu-2-2026-11-06/raw/110004720384.json. County, county_source, ZIP, record tier and status unchanged."
EVD-153018,sites,SITE-000031,address,"street_address 2719 CORY AVENUE, Akron, OH 44314",registry,https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id=110001625180&output=JSON,2026-11-06,supports_C,atlas-L2-oh-address-cu-2,"EPA FRS registry 110001625180; fetched 2026-11-06; raw copy tasks/oh-street-address-cu-2-2026-11-06/raw/110001625180.json. County, county_source, ZIP, record tier and status unchanged."
EVD-153020,sites,SITE-000034,address,"street_address 571 KENNEDY RD, Akron, OH 44305",registry,https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id=110004711660&output=JSON,2026-11-06,supports_C,atlas-L2-oh-address-cu-2,"EPA FRS registry 110004711660; fetched 2026-11-06; raw copy tasks/oh-street-address-cu-2-2026-11-06/raw/110004711660.json. County, county_source, ZIP, record tier and status unchanged."
EVD-153029,sites,SITE-000057,address,"street_address 2020 FRONT ST STE 301, Cuyahoga Falls, OH 44221",registry,https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id=110010739772&output=JSON,2026-11-06,supports_C,atlas-L2-oh-address-cu-2,"EPA FRS registry 110010739772; fetched 2026-11-06; raw copy tasks/oh-street-address-cu-2-2026-11-06/raw/110010739772.json. County, county_source, ZIP, record tier and status unchanged."
EVD-153078,sites,SITE-000153,address,"street_address 25300 AL MOEN DR, North Olmsted, OH 44070",registry,https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id=110004733646&output=JSON,2026-11-06,supports_C,atlas-L2-oh-address-cu-2,"EPA FRS registry 110004733646; fetched 2026-11-06; raw copy tasks/oh-street-address-cu-2-2026-11-06/raw/110004733646.json. County, county_source, ZIP, record tier and status unchanged."
EVD-153081,sites,SITE-000156,address,"street_address 31400 AURORA RD, Solon, OH 44139",registry,https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id=110004726761&output=JSON,2026-11-06,supports_C,atlas-L2-oh-address-cu-2,"EPA FRS registry 110004726761; fetched 2026-11-06; raw copy tasks/oh-street-address-cu-2-2026-11-06/raw/110004726761.json. County, county_source, ZIP, record tier and status unchanged."
EVD-153088,sites,SITE-000164,address,"street_address 9500 EUCLID AVENUE, Cleveland, OH 44195",registry,https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id=110063155482&output=JSON,2026-11-06,supports_C,atlas-L2-oh-address-cu-2,"EPA FRS registry 110063155482; fetched 2026-11-06; raw copy tasks/oh-street-address-cu-2-2026-11-06/raw/110063155482.json. County, county_source, ZIP, record tier and status unchanged."
EVD-153100,sites,SITE-000182,address,"street_address 1365 ORLEN AVE, Cuyahoga Falls, OH 44221",registry,https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id=110006269313&output=JSON,2026-11-06,supports_C,atlas-L2-oh-address-cu-2,"EPA FRS registry 110006269313; fetched 2026-11-06; raw copy tasks/oh-street-address-cu-2-2026-11-06/raw/110006269313.json. County, county_source, ZIP, record tier and status unchanged."

FILE verdicts.csv
site_id,verdict,street_address,evidence_id,reason,availability
SITE-000011,STILL_UNCERTAIN,62 N SUMMIT ST,,FRS 110072052997: city conflict; federal sources disagree on street,
SITE-000012,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000013,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000015,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000016,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000018,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000019,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000020,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000021,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000022,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000023,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000024,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000025,STILL_UNCERTAIN,1070 EVANS AVE,,cited FRS audit source unavailable after bounded retry; successful fresh recheck required,
SITE-000026,STILL_UNCERTAIN,1251 MAIN ST,,FRS 110004667101: city conflict,
SITE-000027,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000028,VERIFIED,2887 GILCHRIST ROAD,EVD-153015,,
SITE-000029,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000030,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000031,VERIFIED,2719 CORY AVENUE,EVD-153018,,
SITE-000032,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000034,VERIFIED,571 KENNEDY RD,EVD-153020,,
SITE-000036,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000040,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000041,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000042,STILL_UNCERTAIN,3835 COPLEY RD,,FRS 110004660304: city conflict,
SITE-000049,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000053,STILL_UNCERTAIN,4040 EMBASSY PKWY,,FRS 110070835503: county conflict/missing,
SITE-000054,STILL_UNCERTAIN,1353 INDUSTRIAL PKWY,,FRS 110009620133: city conflict,
SITE-000055,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000057,VERIFIED,2020 FRONT ST STE 301,EVD-153029,,
SITE-000059,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000062,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000063,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000064,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000065,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000066,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000067,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000068,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000069,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000073,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000080,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000084,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000089,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000090,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000091,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000093,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000094,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000095,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000096,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000097,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000098,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000099,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000100,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000102,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000103,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000104,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000108,STILL_UNCERTAIN,1825-1849 PROSPECT AVE,,fresh FRS facility name lacks exact held legal/trade-name identity; operator adjudication needed; notes-only identifier lacks street binding to this site; FRS 110006336937: non-physical/ambiguous street,
SITE-000118,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000119,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000121,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000122,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000127,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000128,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000130,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000131,STILL_UNCERTAIN,26300 FARGO AVENUE,,FRS 110001630272: city conflict,
SITE-000132,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000135,STILL_UNCERTAIN,7050 KRICK ROAD,,FRS 110070045046: city conflict; notes street conflicts; dated address adjudication needed,
SITE-000137,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000138,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000139,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000142,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000144,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000146,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000147,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000148,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000149,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000152,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000153,VERIFIED,25300 AL MOEN DR,EVD-153078,,
SITE-000154,STILL_UNCERTAIN,22801 SAINT CLAIR AVE,,FRS 110001620121: city conflict,
SITE-000155,STILL_UNCERTAIN,111 SUPERIOR AVE,,FRS 110010738826: city conflict,
SITE-000156,STILL_UNCERTAIN,31400 AURORA RD,,cited FRS audit source unavailable after bounded retry; successful fresh recheck required,
SITE-000157,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000159,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000160,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000161,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000162,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000163,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000164,VERIFIED,9500 EUCLID AVENUE,EVD-153088,,
SITE-000165,STILL_UNCERTAIN,11000 W PLEASANT VALLEY RD,,FRS 110069082913: county conflict/missing,
SITE-000166,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000167,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000169,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000170,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,110070931164: FRS fetch failed: 22
SITE-000172,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000173,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000176,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000177,STILL_UNCERTAIN,255 WOOSTER RD N,,fresh FRS facility name lacks exact held legal/trade-name identity; operator adjudication needed,
SITE-000178,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000181,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000182,VERIFIED,1365 ORLEN AVE,EVD-153100,,

FILE audit.csv
site_id,source_class,registry_id,transcription,fresh_source_match,detail,error
SITE-000025,registry,110004599596,not_ITA,no,FRS fetch failed: 22,
SITE-000028,registry,110004720384,not_ITA,yes,"fresh identifier,street,city,ZIP,county,state agree",
SITE-000164,registry,110063155482,not_ITA,yes,"fresh identifier,street,city,ZIP,county,state agree",
SITE-000156,registry,110004726761,not_ITA,no,FRS fetch failed: 22,
SITE-000182,registry,110006269313,not_ITA,yes,"fresh identifier,street,city,ZIP,county,state agree",
SITE-000031,registry,110001625180,not_ITA,yes,"fresh identifier,street,city,ZIP,county,state agree on bounded retry",
SITE-000153,registry,110004733646,not_ITA,yes,"fresh identifier,street,city,ZIP,county,state agree",
SITE-000034,registry,110004711660,not_ITA,yes,"fresh identifier,street,city,ZIP,county,state agree",
SITE-000057,registry,110010739772,not_ITA,yes,"fresh identifier,street,city,ZIP,county,state agree",

FILE audit_transport_attempt1.csv
site_id,source_class,registry_id,transcription,fresh_source_match,detail,error
SITE-000025,registry,110004599596,not_ITA,no,FRS fetch failed: 22,
SITE-000028,registry,110004720384,not_ITA,yes,"fresh identifier,street,city,ZIP,county,state agree",
SITE-000164,registry,110063155482,not_ITA,yes,"fresh identifier,street,city,ZIP,county,state agree",
SITE-000156,registry,110004726761,not_ITA,no,FRS fetch failed: 22,
SITE-000182,registry,110006269313,not_ITA,yes,"fresh identifier,street,city,ZIP,county,state agree",
SITE-000031,registry,110001625180,not_ITA,no,FRS fetch failed: 22,
SITE-000153,registry,110004733646,not_ITA,yes,"fresh identifier,street,city,ZIP,county,state agree",
SITE-000034,registry,110004711660,not_ITA,yes,"fresh identifier,street,city,ZIP,county,state agree",
SITE-000057,registry,110010739772,not_ITA,yes,"fresh identifier,street,city,ZIP,county,state agree",

FILE audit_retry_log.csv
site_id,registry_id,prior,after,result
SITE-000025,110004599596,FRS fetch failed: 22,FRS fetch failed: 22,no
SITE-000156,110004726761,FRS fetch failed: 22,FRS fetch failed: 22,no
SITE-000031,110001625180,FRS fetch failed: 22,"fresh identifier,street,city,ZIP,county,state agree on bounded retry",yes

FILE retired_ids.csv
site_id,evidence_id,reason
SITE-000025,EVD-153012,cited FRS audit source remains unavailable after bounded retry; successful fresh recheck required before physical street fill
SITE-000156,EVD-153081,cited FRS audit source remains unavailable after bounded retry; successful fresh recheck required before physical street fill

FILE identity_bindings.csv
site_id,registry_id,held_legal_name,held_trade_names,fresh_facility_name,fresh_street,fresh_city,fresh_zip,fresh_county,fresh_state,notes_street,result,admitted
SITE-000025,110004599596,"Enterprise Rubber, Inc.",,ENTERPRISE RUBBER INC,1070 EVANS AVE,AKRON,44305,SUMMIT,OH,1070 EVANS AVE,literal held-name identity plus street/locality match,no: audit unavailable
SITE-000028,110004720384,"Akron Rubber Development Laboratory, Inc.",ARDL,AKRON RUBBER DEVELOPMENT LABORATORY INC,2887 GILCHRIST ROAD,AKRON,44305-4415,SUMMIT,OH,2887 GILCHRIST ROAD,literal held-name identity plus street/locality match,yes
SITE-000031,110001625180,Akron Porcelain & Plastics Co.,,AKRON PORCELAIN & PLASTICS CO.,2719 CORY AVENUE,AKRON,44314,SUMMIT,OH,2719 CORY AVENUE,literal held-name identity plus street/locality match,yes
SITE-000034,110004711660,Akron Polymer Products,,AKRON POLYMER PRODUCTS,571 KENNEDY RD,AKRON,44305,SUMMIT,OH,571 KENNEDY RD,literal held-name identity plus street/locality match,yes
SITE-000057,110010739772,Smithers-Oasis Co.,,SMITHERS OASIS CO,2020 FRONT ST STE 301,CUYAHOGA FALLS,44221,SUMMIT,OH,2020 FRONT ST STE 301,literal held-name identity plus street/locality match,yes
SITE-000153,110004733646,Moen Incorporated,,MOEN INCORPORATED,25300 AL MOEN DR,NORTH OLMSTED,44070,CUYAHOGA,OH,25300 AL MOEN DR,literal held-name identity plus street/locality match,yes
SITE-000156,110004726761,Swagelok,,SWAGELOK CO,31400 AURORA RD,SOLON,44139,CUYAHOGA,OH,31400 AURORA RD,literal held-name identity plus street/locality match,no: audit unavailable
SITE-000164,110063155482,Cleveland Clinic,,CLEVELAND CLINIC,9500 EUCLID AVENUE,CLEVELAND,44195,CUYAHOGA,OH,9500 EUCLID AVENUE,literal held-name identity plus street/locality match,yes
SITE-000182,110006269313,Harwood Rubber Products,Coreline Rollers,HARWOOD RUBBER PRODUCTS INC,1365 ORLEN AVE,CUYAHOGA FALLS,44221,SUMMIT,OH,1365 ORLEN AVE,literal held-name identity plus street/locality match,yes

AUDITSUMMARY
{
  "original_candidates": 9,
  "sampled": 9,
  "original_transcription_errors": 0,
  "original_address_disagreements": 0,
  "fresh_source_matches": 7,
  "not_freshly_checkable": 2,
  "held_for_unavailable_audit": 2,
  "accepted_fills": 7,
  "accepted_fresh_matches": 7,
  "accepted_errors": 0,
  "ita_sampled": 0,
  "replacement_sample": false
}
