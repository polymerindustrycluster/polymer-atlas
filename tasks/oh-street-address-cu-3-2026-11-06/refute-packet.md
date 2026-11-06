CURRENT CONSERVATION SUBSET PR231:6VERIFIED94holds/C5U1,415→421/1883. ClarkSITE000197/EVD153109WITHDRAWN/permanentretired,streetblank. Codex6REFUTEaccepted:siteexplicitlynotstagedsourcesconflict;referencedORG0001908615vs8888EastAveunadjudicated.8837federalagreementdoesnotsettleflag. Other6street/source/EVDvaluesIDENTICALcfa528e. Original7sourceauditkept7primarytranscriptions+7RESTmatches,accepted6allcovered,noresample. Actualsite/CURRENTreferencedparentwarningnowproductiongate;actualClark/referenced-onlywarning/NAICSnegative+originaldefectreenable+late-retiredIDmutationsfailBEFOREwrites. Check6/validator0/nativeguard/keypreservation6+6PASS. MainPINc909f6bb855f2044f963a1165c3a8703d33031b0.
ControllerconservationSUPERSEDEScontinue-all-CU:finishCURRENTfixes,NOnewframe/batch/followup,NOnewreviewround. ThisamendsexistingGrok2reviewonly;CodexoriginalREFUTEisNOTrelabeledAPPROVE. Initial7deepcensusverifiedall7field/sourcevalues;oneClarkwarningwithdrawn. Currentcode/sourcefactsbelow;fetch_bulk.pyunchangedfromoriginalreviewedcfa528e.
Original819indices101–217excludingprior140:100new,140prior,579future. FinaluniqueCU240worked=37V203holds. Slots153000+originalindexfixed;153109retired. Registryaddresssupports_C,NOTtierupgrade. ECHOZIPofficialhttps://echo.epa.gov/files/echodownloads/echo_exporter.zip;downloadNov6T13:12:33Z,SHA db39...sameNov1,DATEISNOTaddresseffective. Permitflagsnotstatus/blankIDsnotabsence. HouseT2helper5bd0c22/read-onlynoindexwrites. Known3+locality/ID/namecontrolsPASS;1586localqueries50observations/28site-IDbindings26IDs. Fulloriginal7auditactualZIPbytes/SHA+ALL3233462CSVrows/exact7projections,0errors. Separate7RESTsecondwitnesses=3priorsame-taskfresh+4new/explicitattribution. No identity/status/county/scope/ring inference. Noentitycreates/deletes/merges. Only6street/sourceedits+6append-onlyEVD,nooffscopewrites.
Remaining6sourcevaluesarestrictsubsetofindependentlycheckedoriginal7.94holdsnotexhaustivelyresearched. No new scope, no old ID reuse, no additional review request. Read README finalcorrection/retired_ids.csv/actualcode;run check.py,validate.py,nativerowloss. Seeoriginalcfa528epacketforunchangedlookup/auditcontext.

FILE build.py
"""C/U federal street pass; all source, scope and namespace checks precede canonical writes."""
import csv,json,re,sys
from pathlib import Path
from fetch import TASK,ROOT,frs,read,write
sys.path.insert(0,str(ROOT/'scripts'))
from shard_io import append_sorted
DATE='2026-11-06'
from fetch_bulk import facility as bulk_facility,namekey
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
def address_warning(s,org_note=None):
 text=s['notes']
 if re.search(r'(?i)\bsee (?:the )?(?:org|organization|parent) note',text):text+=' '+(org_note if org_note is not None else s.get('held_org_notes',''))
 return bool(re.search(r'(?i)(?:street|address)[^.\\n]{0,120}(?:not staged|withheld|discrepancy|unresolved|sources conflict)|(?:unresolved|conflicting) (?:street|address)',text))
def plan():
 frame=read(TASK/'frame.csv');selected=[s for s in frame if s['selected']=='yes'];links=read(TASK/'bulk_bindings.csv');ids={s['site_id'] for s in selected}
 assert len(frame)==len({s['site_id'] for s in frame})==819
 assert len(selected)==len(ids)==100 and len({s['reserved_evidence_id'] for s in frame})==819
 assert [s['reserved_evidence_id'] for s in frame]==[f'EVD-{153000+i:06d}' for i in range(819)]
 assert ids=={s['site_id'] for s in read(TASK/'selection.csv')},'selected cohort changed'
 assert {r['site_id'] for r in links}<=ids
 byid={s['site_id']:s for s in selected}
 assert all(r['registry_id'] in re.findall(r'\b110\d{9}\b',byid[r['site_id']]['notes']) and r['org_id']==byid[r['site_id']]['org_id'] for r in read(TASK/'frs_notes_leads.csv')),'notes lead ID/operator not frozen in site notes'
 source=json.loads((TASK/'bulk_manifest.json').read_text())['source'];assert source['url']=='https://echo.epa.gov/files/echodownloads/echo_exporter.zip'
 fetches={r['registry_id']:r for r in read(TASK/'bulk_log.csv')}
 assert fetches.keys()=={r['registry_id'] for r in links},'bulk identifier yield incomplete'
 ita={r['establishment_id']:r for r in read(ROOT/'tasks/osha-ita-2026-11-01/establishments.csv')}
 matches=[m for m in read(ROOT/'tasks/osha-ita-2026-11-01/site_matches.csv') if m['site_id'] in ids and m['match_strength'] in ('exact','strong')]
 existing=[e for e in read(ROOT/'data/evidence_sites_OH.csv') if e['record_id'] in ids and e['claim_type']=='address' and e['created_by']!='atlas-L2-oh-address-cu-2']
 assert not existing,'new held address evidence needs priority/adjudication before this frozen pass'
 ev=[];verdicts=[];transcription=[];canonical=read(ROOT/'data/sites_OH.csv')
 parents={r['org_id']:r for p in (ROOT/'data').glob('organizations_*.csv') for r in read(p)};parents.update({r['org_id']:r for r in read(ROOT/'data/ecosystem.csv')})
 for s in selected:
  sid=s['site_id'];why=[];candidates=[];unavailable=[]
  if address_warning(s,parents[s['org_id']]['notes']):why.append('explicit unresolved street/address warning including referenced org note; documented reconciliation required')
  peers=[r for r in canonical if r['site_id']!=sid and r['org_id']==s['org_id'] and r['operating_status']=='active' and frs.norm(r['city'])==frs.norm(s['city']) and (not r['zip'] or not s['zip'] or r['zip'][:5]==s['zip'][:5])]
  for link in [r for r in links if r['site_id']==sid]:
   rid=link['registry_id'];row=fetches[rid]
   if link['org_id']!=s['org_id']:why.append('registry link operator differs from Atlas operator')
   if row['result']!='OK':why.append('bulk identifier ambiguous');unavailable.append(rid+': '+row['result']);continue
   f=bulk_facility(json.loads((TASK/'bulk_raw'/f'{rid}.json').read_text()),rid)
   if not identity(s,f):why.append('bulk facility name lacks exact held legal/trade-name identity; operator adjudication needed')
   if peers and not note_streets(s):why.append('bulk address lacks site-specific binding among same-operator city/ZIP peers')
   conflict=frs.conflict(s,f)
   if conflict:why.append('FRS '+rid+': '+conflict)
   if re.search(r'(?i)\bP\.?\s*O\.?\s*BOX\b|mailing',f.get('SupplementalLocation') or ''):why.append('supplemental mailing/PO-box ambiguity')
   candidates.append(dict(street=f['LocationAddress'],source_class='registry',ref=source['url'],date=source['date'][:10],
                          effect='supports_C',notes=f"EPA ECHO REGISTRY_ID {rid}; bulk download {source['date']}; archive SHA-256 {source['sha256']}; raw projection tasks/oh-street-address-cu-3-2026-11-06/bulk_raw/{rid}.json; retrieval date not address-effective date",source_id=rid))
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
  # Previously fetched REST records remain contradiction checks, never relabeled as bulk observations.
  historical=read(TASK/'registry_links_input.csv')+read(TASK/'frs_notes_leads.csv')+read(TASK/'frs_packet_leads.csv')
  for old in [r for r in historical if r['site_id']==sid]:
   path=TASK/'raw'/(old['registry_id']+'.json')
   if not path.exists():continue
   fresh=frs.facility(json.loads(path.read_text()),old['registry_id'])
   if not identity(s,fresh) or frs.conflict(s,fresh):why.append('earlier fresh REST identity/locality conflicts; source reconciliation needed')
   if candidates and any(frs.streetkey(c['street'])!=frs.streetkey(fresh['LocationAddress']) for c in candidates):why.append('bulk and earlier fresh REST streets disagree')
  if len({frs.streetkey(c['street']) for c in candidates})>1:why.append('federal sources disagree on street')
  street=candidates[0]['street'] if candidates else ''
  # shortcut: written ordinals/dotted diagonals remain distinct; adjudicate held aliases before widening matching.
  if candidates and any(frs.streetkey(n)!=frs.streetkey(street) for n in note_streets(s)):why.append('notes street conflicts; dated address adjudication needed')
  if sid in {r['site_id'] for r in read(TASK/'retired_ids.csv')}:why.append('retired proposal requires documented address/source reconciliation')
  if not candidates:why.append('need admissible physical street witness; no qualifying federal route or source unavailable')
  why=list(dict.fromkeys(why))
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
 selected,links,verdicts,ev,transcription=plan();assert len(ev)==6,'frozen adjudication yield changed before writes'
 sites=read(ROOT/'data/sites_OH.csv');byid={s['site_id']:s for s in sites};frozen={s['site_id']:s for s in selected};eb={e['record_id']:e for e in ev}
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
 summary=dict(cu_active_blank_cohort=819,prior_worked=140,worked=100,unworked_cohort=579,
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
 assert {r['site_id'] for r in selected}=={r['site_id'] for r in build.read(build.TASK/'selection.csv')}
 for name,raw in [('Lincoln Electric','LINCOLN ELECTRIC CO'),('ABC, LLC','ABC INC'),('The Parker Corporation','PARKER INC')]:
  assert build.identity(dict(held_legal_name=name,held_trade_names=''),dict(FacilityName=raw))
 assert build.identity(dict(held_legal_name='Held Parent',held_trade_names='Old Registrant;Other Name'),dict(FacilityName='OLD REGISTRANT INC'))
 assert not build.identity(dict(held_legal_name='Held Parent',held_trade_names=''),dict(FacilityName='Different Operator'))
 assert not build.identity(dict(held_legal_name='ABC Polymers',held_trade_names=''),dict(FacilityName='ABC Plastics'))
 audit=build.read(build.TASK/'audit.csv')
 import random
 proposed=build.read(build.TASK/'evidence_proposed.csv')
 sample=random.Random(20261106).sample(sorted(proposed,key=lambda e:e['record_id']),min(30,len(proposed)))
 assert {r['site_id'] for r in audit}=={e['record_id'] for e in sample} and len(audit)==len(sample)
 assert all(r['bulk_transcription']=='PASS' and not r['error'] for r in audit if r['site_id'] in {e['record_id'] for e in ev})

 assert build.note_streets(dict(city='South Euclid',notes='Street (per Grok): 4321 Glenridge Road. county UNVERIFIED — Grok county_check=TRUE'))==['4321 Glenridge Road']
 assert len(ev)==6,'frozen bulk-source yield changed; inspect before revising'
 assert len(build.read(build.TASK/'bulk_known.csv'))==3
 import json,re,subprocess,csv
 original=list(csv.DictReader(subprocess.check_output(['git','show','a9af228:tasks/oh-street-address-cu-2026-11-06/frame.csv'],text=True).splitlines()))
 assert [(r['site_id'],r['reserved_evidence_id']) for r in frame]==[(r['site_id'],r['reserved_evidence_id']) for r in original]
 prior=build.read(build.TASK/'prior_worked.csv')
 assert len(prior)==len({r['site_id'] for r in prior})==140 and not {r['site_id'] for r in prior}&{r['site_id'] for r in selected}
 manifest=json.loads((build.TASK/'bulk_manifest.json').read_text())['source']
 for e in ev:
  assert e['source_class']=='registry' and e['tier_effect']=='supports_C' and e['source_ref']==manifest['url'] and e['observed_date']==manifest['date'][:10]
  assert 'retrieval date not address-effective date' in e['notes'] and re.search(r'REGISTRY_ID \d{12};',e['notes'])
 for sid in ('SITE-000184','SITE-000185','SITE-000205','SITE-000234','SITE-000256','SITE-000282','SITE-000297','SITE-000309','SITE-000333','SITE-000355','SITE-000360','SITE-000387','SITE-000393','SITE-000414','SITE-000427'):
  assert next(v for v in verdicts if v['site_id']==sid)['verdict']=='STILL_UNCERTAIN',sid
 clark=next(r for r in selected if r['site_id']=='SITE-000197')
 assert build.address_warning(clark),'actual Clark deferred-address warning missed'
 assert next(v for v in verdicts if v['site_id']=='SITE-000197')['verdict']=='STILL_UNCERTAIN'
 assert build.address_warning(dict(notes='See org note for address.',held_org_notes='ADDRESS DISCREPANCY: alternatives; resolve at verification.'))
 assert not build.address_warning(dict(notes='NAICS codes conflict; Street: 123 Main Road.',held_org_notes=''))
 expected=len(ev)
 with tempfile.TemporaryDirectory() as tmp:
  build.ROOT=Path(tmp);(build.ROOT/'data').mkdir()
  for p in (root/'data').glob('evidence_*.csv'):shutil.copyfile(p,build.ROOT/'data'/p.name)
  for p in (root/'data').glob('organizations_*.csv'):shutil.copyfile(p,build.ROOT/'data'/p.name)
  shutil.copyfile(root/'data/ecosystem.csv',build.ROOT/'data/ecosystem.csv')
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
  saved_warning=build.address_warning;saved_read=build.read
  build.address_warning=lambda *args:False
  build.read=lambda p:[] if Path(p).name=='retired_ids.csv' else saved_read(p)
  try:
   with contextlib.redirect_stdout(io.StringIO()):build.run(apply=True)
  except AssertionError:pass
  else:raise AssertionError('original Clark admission defect bypassed frozen subset')
  finally:build.address_warning=saved_warning;build.read=saved_read
  assert hashes=={p.name:digest(p) for p in paths},'writes happened before Clark defect rejection'
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
  retired_row=dict(ev[-1],evidence_id='EVD-153109')
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

FILE audit_bulk.py
"""Seeded source transcription directly against the official ZIP; optional fresh REST is a separate witness."""
import hashlib,json,random,re,time,zipfile
from fetch import TASK,frs,read,write
from fetch_bulk import CACHE,FIELDS,helper,facility
from build import identity
source=json.loads((TASK/'bulk_manifest.json').read_text())['source']
evidence=read(TASK/'evidence_proposed.csv');admitted={e['record_id'] for e in read(TASK/'evidence.csv')}
sample=random.Random(20261106).sample(sorted(evidence,key=lambda e:e['record_id']),min(30,len(evidence)))
sites={r['site_id']:r for r in read(TASK/'frame.csv')}
ids={re.search(r'REGISTRY_ID (\d+);',e['notes'])[1] for e in sample};found={rid:[] for rid in ids}
archive=CACHE/source['file'];assert archive.stat().st_size==source['size'] and helper.sha256(archive)==source['sha256']
count=0
with zipfile.ZipFile(archive) as z:
 members=[n for n in z.namelist() if n.lower().endswith('.csv')];assert len(members)==1
 for row in helper.csv_rows(z,members[0]):
  count+=1
  if row.get('REGISTRY_ID') in ids:found[row['REGISTRY_ID']].append({k:row.get(k) or '' for k in FIELDS})
assert count==source['row_count']==source['independent_count'],'archive row yield differs from manifest'
out=[]
rest_proof={r['site_id']:r for r in read(TASK/'audit_rest.csv')}
for e in sample:
 sid=e['record_id'];s=sites[sid];rid=re.search(r'REGISTRY_ID (\d+);',e['notes'])[1];error='';fresh='not_checked';detail=''
 raw=found[rid];assert len(raw)==1,'missing/duplicate archive ID'
 banked=json.loads((TASK/'bulk_raw'/(rid+'.json')).read_text())
 assert raw==banked,'banked projection differs from exact official CSV row'
 f=facility(raw,rid);street=e['claim_detail'].removeprefix('street_address ').split(', '+s['city']+', OH ',1)[0]
 assert identity(s,f) and not frs.conflict(s,f) and street==f['LocationAddress'],'bulk transcription/binding differs'
 # These three prior fresh audits remain separate REST observations; no archive row is labeled freshly updated.
 prior=rest_proof.get(sid)
 path=TASK/'audit_raw'/(rid+'.json')
 try:
  if prior and prior['fresh_source_match']=='yes' and path.exists():
   other=frs.facility(json.loads(path.read_text()),rid);detail='prior same-task fresh REST audit, retained independently'
  else:
   try:other=frs.facility(frs.fetch(rid,'bulk_audit_rest_raw'),rid)
   finally:time.sleep(12)
   detail='fresh optional REST re-fetch'
  fields=('LocationAddress','CityName','ZipCode','CountyName','StateAbbr')
  if not identity(s,other):error='REST identity differs from held operator'
  for field in fields:
   left=other.get(field) or '';right=f.get(field) or ''
   if not left:continue
   normalize=frs.streetkey if field=='LocationAddress' else (lambda x:x[:5]) if field=='ZipCode' else frs.norm
   if normalize(left)!=normalize(right):error='fresh REST disagrees on '+field
  fresh='yes' if not error and not frs.conflict(s,other) else 'incomplete' if not error else 'disagrees'
 except Exception as ex:fresh='unavailable';detail=str(ex)
 out.append(dict(site_id=sid,registry_id=rid,bulk_transcription='PASS',bulk_row_sha256=hashlib.sha256(json.dumps(raw[0],sort_keys=True).encode()).hexdigest(),fresh_rest_match=fresh,rest_detail=detail,error=error))
 write(TASK/'audit.csv',out);print(sid,'bulk PASS','REST',fresh,error,flush=True)
summary=dict(original_candidates=len(evidence),sampled=len(out),accepted_fills=len(admitted),archive_rows_reconciled=count,bulk_transcription_errors=0,fresh_rest_matches=sum(r['fresh_rest_match']=='yes' for r in out),rest_unavailable=sum(r['fresh_rest_match']=='unavailable' for r in out),rest_incomplete=sum(r['fresh_rest_match']=='incomplete' for r in out),address_disagreements=sum(bool(r['error']) for r in out),source_download_date=source['date'],source_is_address_effective_date=False)
(TASK/'audit_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary)
assert len(out)==min(30,len(evidence)) and all(not r['error'] for r in out if r['site_id'] in admitted)

FILE evidence.csv
evidence_id,record_table,record_id,claim_type,claim_detail,source_class,source_ref,observed_date,tier_effect,created_by,notes
EVD-153108,sites,SITE-000195,address,"street_address 15730 S MADISON RD, Middlefield, OH 44062",registry,https://echo.epa.gov/files/echodownloads/echo_exporter.zip,2026-11-06,supports_C,atlas-L2-oh-address-cu-2,"EPA ECHO REGISTRY_ID 110004707924; bulk download 2026-11-06T13:12:33.594168+00:00; archive SHA-256 db39e0733204652f1016f0f2b9b66f3e5cc53caeca328214351233b2b3aba90a; raw projection tasks/oh-street-address-cu-3-2026-11-06/bulk_raw/110004707924.json; retrieval date not address-effective date. County, county_source, ZIP, record tier and status unchanged."
EVD-153112,sites,SITE-000208,address,"street_address 2751 WEST AVE., Ashtabula, OH 44004",registry,https://echo.epa.gov/files/echodownloads/echo_exporter.zip,2026-11-06,supports_C,atlas-L2-oh-address-cu-2,"EPA ECHO REGISTRY_ID 110000385093; bulk download 2026-11-06T13:12:33.594168+00:00; archive SHA-256 db39e0733204652f1016f0f2b9b66f3e5cc53caeca328214351233b2b3aba90a; raw projection tasks/oh-street-address-cu-3-2026-11-06/bulk_raw/110000385093.json; retrieval date not address-effective date. County, county_source, ZIP, record tier and status unchanged."
EVD-153126,sites,SITE-000246,address,"street_address 8006 KATHERINE BLVD, Brecksville, OH 44141",registry,https://echo.epa.gov/files/echodownloads/echo_exporter.zip,2026-11-06,supports_C,atlas-L2-oh-address-cu-2,"EPA ECHO REGISTRY_ID 110070122366; bulk download 2026-11-06T13:12:33.594168+00:00; archive SHA-256 db39e0733204652f1016f0f2b9b66f3e5cc53caeca328214351233b2b3aba90a; raw projection tasks/oh-street-address-cu-3-2026-11-06/bulk_raw/110070122366.json; retrieval date not address-effective date. County, county_source, ZIP, record tier and status unchanged."
EVD-153179,sites,SITE-000357,address,"street_address 310 FIGGIE RD, Painesville, OH 44077",registry,https://echo.epa.gov/files/echodownloads/echo_exporter.zip,2026-11-06,supports_C,atlas-L2-oh-address-cu-2,"EPA ECHO REGISTRY_ID 110032654660; bulk download 2026-11-06T13:12:33.594168+00:00; archive SHA-256 db39e0733204652f1016f0f2b9b66f3e5cc53caeca328214351233b2b3aba90a; raw projection tasks/oh-street-address-cu-3-2026-11-06/bulk_raw/110032654660.json; retrieval date not address-effective date. County, county_source, ZIP, record tier and status unchanged."
EVD-153184,sites,SITE-000365,address,"street_address 260 SPRINGSIDE DR, Akron, OH 44333",registry,https://echo.epa.gov/files/echodownloads/echo_exporter.zip,2026-11-06,supports_C,atlas-L2-oh-address-cu-2,"EPA ECHO REGISTRY_ID 110004620544; bulk download 2026-11-06T13:12:33.594168+00:00; archive SHA-256 db39e0733204652f1016f0f2b9b66f3e5cc53caeca328214351233b2b3aba90a; raw projection tasks/oh-street-address-cu-3-2026-11-06/bulk_raw/110004620544.json; retrieval date not address-effective date. County, county_source, ZIP, record tier and status unchanged."
EVD-153191,sites,SITE-000379,address,"street_address 220 CAMPUS DR, Aurora, OH 44202",registry,https://echo.epa.gov/files/echodownloads/echo_exporter.zip,2026-11-06,supports_C,atlas-L2-oh-address-cu-2,"EPA ECHO REGISTRY_ID 110037437850; bulk download 2026-11-06T13:12:33.594168+00:00; archive SHA-256 db39e0733204652f1016f0f2b9b66f3e5cc53caeca328214351233b2b3aba90a; raw projection tasks/oh-street-address-cu-3-2026-11-06/bulk_raw/110037437850.json; retrieval date not address-effective date. County, county_source, ZIP, record tier and status unchanged."

FILE verdicts.csv
site_id,verdict,street_address,evidence_id,reason,availability
SITE-000184,STILL_UNCERTAIN,340 MARTINEL DR,,bulk facility name lacks exact held legal/trade-name identity; operator adjudication needed; bulk and earlier fresh REST streets disagree; earlier fresh REST identity/locality conflicts; source reconciliation needed; federal sources disagree on street,
SITE-000185,STILL_UNCERTAIN,340 MARTINEL DR,,bulk facility name lacks exact held legal/trade-name identity; operator adjudication needed; earlier fresh REST identity/locality conflicts; source reconciliation needed; bulk and earlier fresh REST streets disagree; federal sources disagree on street; notes street conflicts; dated address adjudication needed,
SITE-000187,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000188,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000190,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000191,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000193,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000195,VERIFIED,15730 S MADISON RD,EVD-153108,,
SITE-000197,STILL_UNCERTAIN,8837 EAST AVE,,explicit unresolved street/address warning including referenced org note; documented reconciliation required; retired proposal requires documented address/source reconciliation,
SITE-000200,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000205,STILL_UNCERTAIN,4150 MILLENIUM BLVD SE,,FRS 110020691429: ZIP conflict/missing; earlier fresh REST identity/locality conflicts; source reconciliation needed; bulk and earlier fresh REST streets disagree; notes street conflicts; dated address adjudication needed,
SITE-000208,VERIFIED,2751 WEST AVE.,EVD-153112,,
SITE-000209,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000210,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000211,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000214,STILL_UNCERTAIN,8940 TYLER BOULEVARD,,FRS 110042190232: city conflict; earlier fresh REST identity/locality conflicts; source reconciliation needed,
SITE-000226,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000229,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000234,STILL_UNCERTAIN,367 STANTON AVE,,notes street conflicts; dated address adjudication needed,
SITE-000237,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000243,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000246,VERIFIED,8006 KATHERINE BLVD,EVD-153126,,
SITE-000249,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000255,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000256,STILL_UNCERTAIN,858 MAHONING AVE,,notes street conflicts; dated address adjudication needed,
SITE-000259,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000265,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000266,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000267,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000268,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000269,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000275,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000280,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000282,STILL_UNCERTAIN,4413 HAMANN PKWY,,notes street conflicts; dated address adjudication needed,
SITE-000283,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000284,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000291,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000292,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000293,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000295,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000297,STILL_UNCERTAIN,1244 E HIGHLAND RD,,notes street conflicts; dated address adjudication needed,
SITE-000301,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000304,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000307,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000308,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000309,STILL_UNCERTAIN,,,ITA city/ZIP conflict or missing; need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000311,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000313,STILL_UNCERTAIN,,,ITA city/ZIP conflict or missing; need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000315,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000316,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000320,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000321,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000322,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000324,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000326,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000330,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000333,STILL_UNCERTAIN,6200 HILLCREST DRIVE,,bulk facility name lacks exact held legal/trade-name identity; operator adjudication needed; FRS 110000840788: ZIP conflict/missing; ITA city/ZIP conflict or missing; earlier fresh REST identity/locality conflicts; source reconciliation needed,
SITE-000339,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000340,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000344,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000345,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000349,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000351,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000352,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000353,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000354,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000355,STILL_UNCERTAIN,1016 9TH STREET SOUTH WEST,,FRS 110004596447: ZIP conflict/missing; federal sources disagree on street; notes street conflicts; dated address adjudication needed,
SITE-000357,VERIFIED,310 FIGGIE RD,EVD-153179,,
SITE-000358,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000359,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000360,STILL_UNCERTAIN,1687 COMMERCE DRIVE,,federal sources disagree on street; notes street conflicts; dated address adjudication needed,
SITE-000364,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000365,VERIFIED,260 SPRINGSIDE DR,EVD-153184,,
SITE-000370,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000373,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000375,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000379,VERIFIED,220 CAMPUS DR,EVD-153191,,
SITE-000382,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000385,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000387,STILL_UNCERTAIN,510 W BROAD ST,,federal sources disagree on street; notes street conflicts; dated address adjudication needed,
SITE-000388,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000389,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000393,STILL_UNCERTAIN,1020 LAMBERT STREET,,bulk facility name lacks exact held legal/trade-name identity; operator adjudication needed; FRS 110000388492: ZIP conflict/missing; ITA city/ZIP conflict or missing; earlier fresh REST identity/locality conflicts; source reconciliation needed,
SITE-000395,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000400,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000401,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000405,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000406,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000407,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000410,STILL_UNCERTAIN,,,ITA city/ZIP conflict or missing; need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000414,STILL_UNCERTAIN,3500 N RIDGE RD W,,FRS 110071041484: county conflict/missing; FRS 110070380166: county conflict/missing; earlier fresh REST identity/locality conflicts; source reconciliation needed; bulk and earlier fresh REST streets disagree; federal sources disagree on street,
SITE-000415,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000417,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000424,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000425,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000427,STILL_UNCERTAIN,,,ITA city/ZIP conflict or missing; need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000428,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000430,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000431,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,
SITE-000435,STILL_UNCERTAIN,,,need admissible physical street witness; no qualifying federal route or source unavailable,

FILE audit.csv
site_id,registry_id,bulk_transcription,bulk_row_sha256,fresh_rest_match,rest_detail,error
SITE-000365,110004620544,PASS,77171dd4ff7f5879977496440fb603653a5cfea89e475358b87a965f30a80894,yes,fresh optional REST re-fetch,
SITE-000195,110004707924,PASS,9c32e0e38febdd773a8a8d235f7a011c4b280ec89cd6d19b10607cf8f97ff83f,yes,"prior same-task fresh REST audit, retained independently",
SITE-000379,110037437850,PASS,fadb7085218bae04e594bf5760734f7ed8dd33f3039a6dbe8e4940a4aff4e915,yes,fresh optional REST re-fetch,
SITE-000197,110004619226,PASS,65a578cbb1be309b1ed4db3e159e8f4a1a011afed3f53d6dc0ab03dd9c163c56,yes,"prior same-task fresh REST audit, retained independently",
SITE-000357,110032654660,PASS,817cf8972a9bbb5e620948de20e1c600849b8dcc76ad532ac936d928e102a6c0,yes,fresh optional REST re-fetch,
SITE-000208,110000385093,PASS,1c550bed53c6a4e4476a23016201337978e4c04ff43f7866c069b9147aaba02e,yes,"prior same-task fresh REST audit, retained independently",
SITE-000246,110070122366,PASS,4af166415016a09e168fa061f081cdc5e866ac104220961dcfbd6b27576181eb,yes,fresh optional REST re-fetch,

FILE retired_ids.csv
site_id,evidence_id,reason
SITE-000197,EVD-153109,explicit unresolved site/org address discrepancy 8615 vs8888EastAve;8837federalagreementdoesnotadjudicateflag

FILE bulk_manifest.json
{
  "source": {
    "url": "https://echo.epa.gov/files/echodownloads/echo_exporter.zip",
    "date": "2026-11-06T13:12:33.594168+00:00",
    "size": 446459497,
    "sha256": "db39e0733204652f1016f0f2b9b66f3e5cc53caeca328214351233b2b3aba90a",
    "file": "db39e0733204652f1016f0f2b9b66f3e5cc53caeca328214351233b2b3aba90a.zip",
    "row_count": 3233462,
    "indexed_rows": 3233462,
    "historical_members": 0,
    "independent_count": 3233462,
    "published_count": null
  },
  "helper_commit": "5bd0c22f3aedbcc8269de8ae4d2c3783487ca7cd",
  "source_caveats": [
    "retrieval date not address-effective date",
    "same archive SHA as held Nov1 spine",
    "permit activity not establishment operating status",
    "18887 source rows have blank registry IDs",
    "ECHO covers regulated facilities, not all FRS"
  ]
}

FILE audit_summary.json
{
  "original_candidates": 7,
  "sampled": 7,
  "accepted_fills": 6,
  "archive_rows_reconciled": 3233462,
  "bulk_transcription_errors": 0,
  "fresh_rest_matches": 7,
  "rest_unavailable": 0,
  "rest_incomplete": 0,
  "address_disagreements": 0,
  "source_download_date": "2026-11-06T13:12:33.594168+00:00",
  "source_is_address_effective_date": false,
  "accepted_bulk_transcriptions": 6,
  "withdrawn_for_explicit_unresolved_warning": 1,
  "replacement_sample": false
}
