Adversarial refute L2 optional C/U Ohio street pass. NEWindependent branch agent/codex/oh-street-address-cu, noAB156/171code/data included. Return VERDICT:APPROVE/REFUTE with demonstrated findings, no mutations/merge.
Scope frozen819activeC/UOhio blanks;108hadheldsite-keyedFRS+nonblankZIP. First40byimmutableSiteID selected BEFOREfetch,41registryIDs(one site2).40outcomes=24VERIFIED/16STILL_UNCERTAIN;779broadunworked/68othereligibleunworked.24street/source-only edits+24append-onlyregistry/address/supports_C evidence; recordtiersC22/U2unchanged; sparseEVD153120–153334 within819positionreservation153000–153818. Noentitycreate/delete/merges,geography/tier/status/ring/registry/derivedchanges. Currentmaincoverage286/1883→310/1883(15.19→16.46%), excludespendingAB15619 and17138.
Sourcepriority:0existingaddresswitnesses forselected40; freshsite-keyedFRS41fetches40OK1HTTP22unavailable at12secspacing; allsuccessfulJSONretained. ExactRegistryID,city,ZIP5,county,state,physicalstreet andAtlasoperatorlinkguard.6exact/strongbankedITArows transcribed0drift andusedforconflictchecks; NONEadmittedasevidence,all24EVDregistryC. InheritedITAexceptionexplicitcontrollergrant(publicCY2025file,observed2026-11-01,filingdate/ID/SHA); nofreshbulkdownloadclaim. Failedfetchesavailabilityonly,neverabsence/status. Notesareleadsveto only. Countyannotations strippedfromstreetkey; writtenordinals/dotteddiagonals deliberatelyremainheld. Full40verdicts/inputsexplicit; nocherry-pickpositive.
Namedgroundtruth:3literalLIVEFRSknownanswers+wrongcity/ZIP/county/POboxmutationsPASS BEFORE41fetches. check.py24fills; onlystreet/sources; byte-idempotent; street/ZIP/tier/status andforeign-shardEVDinjectionsrejectBEFOREwrites. Auditinputall24accepted; initialstrictgateFAILED22matches+2HTTP22unavailable (savedattempt1); retryONLY2at12secspacingrecoveredboth. Final24/24freshcitedFRSrecords agreeonID/street/city/ZIP/county/state,0errors/0uncheckable. Thisrepeatssamecitedsource, NOTanindependentsecondsource/tierupgrade. audit.csv fresh_source_match terminology corrected accordingly. Originalpreliminarycontroller"completed"overstatementcorrectedbeforecanonicalwrites; exacthistoryREADME/BOARD.
validate.py0errors; fresh-mainkeycomparisonallsite/evidencekeysretained,alllegacyevidenceunchanged,24edits24appends;diffcheckPASS. No scripts/changes. Rawcoords retainedaspartprimaryJSON butneverusedorwritten. ThispassonepertiedID+audit,retrypacedwithinbudget; no web ownpage/mailclassifierhere: FRSLocationAddressphysical-and-POboxguard only.
Potentialfailureclasses: incorrectkeyedFRS/operatorlink, locality/physical/mailingambiguity, notes-onlyaddressorwrongcounty, sourceparsermissingrecords, freshness/unavailablecountturnedPASS, IDcollision/rebaseoverwrite, literalstreetnormalizationfalseagreement, sourceclassceilingorunintendedtierpromotion, undetectedlegacyrowloss. Challengeactualevidence.
Commands: python3 tasks/oh-street-address-cu-2026-11-06/check.py; python3 scripts/validate.py. audit.pyfreshpaced24census (~5min), runbackground. retry_audit.pyONLYunavailable andstrictfullgatereassertion,historypreserved. fetch.py --known3pacedpositiveanswers (~36sec). Full819frame+41links+41fetchlog+40rawJSONin taskfolder; belowcode+40compactinputs+40verdicts+24EVD+allsuccessfulFRSidentity/addressfields+audit.

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
 ids=sorted({r['registry_id'] for r in read(TASK/'registry_links_input.csv')});out=[]
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
ITA_URL='https://www.osha.gov/sites/default/largefiles/ITA_300A_Summary_Data_2025_through_08-31-2026.csv'
ITA_SHA='69c0d987d453471293b092640b392eaef44b21cb55446a1c9b69ad8b54bf703a'
def note_streets(s):
 out=re.findall(r'(?i)(?:Address[^:]{0,120}:|at)\s*(\d+\s+[^,;()]+),\s*'+re.escape(s['city']),s['notes'])
 m=re.search(r'(?i)\bstreet(?:\s*\([^)]*\))?:\s*(.+)',s['notes'])
 if m:out.append(re.split(r'\.\s+(?=PASS|BAND|CERT|Ring|INTEGRATION|Parcel|Re-pointed|NAICS|Source|(?i:county UNVERIFIED)|\[)',m[1])[0].rstrip('. '))
 return out
def plan():
 frame=read(TASK/'frame.csv');selected=[s for s in frame if s['selected']=='yes'];links=read(TASK/'registry_links_input.csv');ids={s['site_id'] for s in selected}
 assert len(frame)==len({s['site_id'] for s in frame})==819
 assert len(selected)==len(ids)==40 and len({s['reserved_evidence_id'] for s in frame})==819
 assert {r['site_id'] for r in links}==ids
 fetches={r['registry_id']:r for r in read(TASK/'fetch_log.csv')}
 assert fetches.keys()=={r['registry_id'] for r in links},'FRS request yield incomplete'
 ita={r['establishment_id']:r for r in read(ROOT/'tasks/osha-ita-2026-11-01/establishments.csv')}
 matches=[m for m in read(ROOT/'tasks/osha-ita-2026-11-01/site_matches.csv') if m['site_id'] in ids and m['match_strength'] in ('exact','strong')]
 existing=[e for e in read(ROOT/'data/evidence_sites_OH.csv') if e['record_id'] in ids and e['claim_type']=='address' and e['created_by']!='atlas-L2-oh-address-cu']
 assert not existing,'new held address evidence needs priority/adjudication before this frozen pass'
 ev=[];verdicts=[];transcription=[]
 for s in selected:
  sid=s['site_id'];why=[];candidates=[];unavailable=[]
  for link in [r for r in links if r['site_id']==sid]:
   rid=link['registry_id'];row=fetches[rid]
   if link['org_id']!=s['org_id']:why.append('registry link operator differs from Atlas operator')
   if row['result']!='OK':unavailable.append(rid+': '+row['error']);continue
   f=frs.facility(json.loads((TASK/'raw'/f'{rid}.json').read_text()),rid)
   conflict=frs.conflict(s,f)
   if conflict:why.append('FRS '+rid+': '+conflict)
   if re.search(r'(?i)\bP\.?\s*O\.?\s*BOX\b|mailing',f.get('SupplementalLocation') or ''):why.append('supplemental mailing/PO-box ambiguity')
   candidates.append(dict(street=f['LocationAddress'],source_class='registry',ref=frs.FRSU+rid+'&output=JSON',date=DATE,
                          effect='supports_C',notes=f"EPA FRS registry {rid}; fetched {DATE}; raw copy tasks/oh-street-address-cu-2026-11-06/raw/{rid}.json",source_id=rid))
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
  if not candidates:why.append('need admissible site-keyed physical street witness; FRS unavailable and no qualifying inherited ITA')
  v=dict(site_id=sid,verdict='STILL_UNCERTAIN' if why else 'VERIFIED',street_address=street,evidence_id='' if why else s['reserved_evidence_id'],reason='; '.join(why),availability='; '.join(unavailable))
  verdicts.append(v)
  if not why:
   c=candidates[0];ev.append(dict(evidence_id=s['reserved_evidence_id'],record_table='sites',record_id=sid,claim_type='address',
     claim_detail=f"street_address {street}, {s['city']}, OH {s['zip']}",
     source_class=c['source_class'],source_ref=c['ref'],observed_date=c['date'],tier_effect=c['effect'],created_by='atlas-L2-oh-address-cu',
     notes=c['notes']+'. County, county_source, ZIP, record tier and status unchanged.'))
 assert len(verdicts)==len({v['site_id'] for v in verdicts})==40
 return selected,links,verdicts,ev,transcription
def run(apply=False):
 selected,links,verdicts,ev,transcription=plan();sites=read(ROOT/'data/sites_OH.csv');byid={s['site_id']:s for s in sites};frozen={s['site_id']:s for s in selected};eb={e['record_id']:e for e in ev}
 live_links={(r['org_id'],r['registry_id'],r['site_id']) for r in read(ROOT/'data/registry_links.csv') if r['registry']=='FRS'}
 assert all((r['org_id'],r['registry_id'],r['site_id']) in live_links for r in links),'main link no longer held'
 existing={};planned_ids={e['evidence_id'] for e in ev}
 for p in (ROOT/'data').glob('evidence_*.csv'):
  for e in read(p):
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
 summary=dict(cu_active_blank_cohort=819,frs_known_zip_eligible=108,worked=40,unworked_cohort=779,unworked_frs_known_zip=68,
              fills=len(ev),holds=40-len(ev),active_ohio_sites=len(active),before_streets=before,after_streets=before+len(ev))
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
 assert len(ev)==24,'frozen source-adjudication yield changed; inspect before revising'
 audit=build.read(build.TASK/'audit.csv')
 assert len(audit)==24 and {r['site_id'] for r in audit}=={e['record_id'] for e in ev},'audit yield/binding mismatch'
 assert all(r['fresh_source_match']=='yes' and not r['error'] for r in audit),'fresh source gate incomplete'
 assert build.note_streets(dict(city='South Euclid',notes='Street (per Grok): 4321 Glenridge Road. county UNVERIFIED — Grok county_check=TRUE'))==['4321 Glenridge Road']
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
  p=build.ROOT/'data/evidence_sites_OH.csv';old_evidence=[r for r in build.read(p) if r['created_by']!='atlas-L2-oh-address-cu'];build.write(p,old_evidence)
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
  foreign=build.ROOT/'data/evidence_sites_ZZ.csv';build.write(foreign,[ev[0]])
  paths=list((build.ROOT/'data').glob('*.csv'));hashes={p.name:digest(p) for p in paths}
  try:
   with contextlib.redirect_stdout(io.StringIO()):build.run(apply=True)
  except AssertionError:pass
  else:raise AssertionError('foreign-shard evidence collision accepted')
  assert hashes=={p.name:digest(p) for p in paths},'canonical write before ID collision refusal'
 build.ROOT=root
 print(f'PASS {expected} fills; only street/sources; byte-idempotent; street/ZIP/tier/status/foreign-ID mutations reject before writes')
if __name__=='__main__':main()

FILE audit.py
"""Paced seeded fresh FRS audit, plus inherited-ITA transcription when applicable."""
import csv,json,random,re,time
from fetch import TASK,ROOT,frs,read,write
evidence=read(TASK/'evidence.csv');sites={s['site_id']:s for s in read(TASK/'frame.csv')}
links=read(TASK/'registry_links_input.csv');sample=random.Random(20261106).sample(sorted(evidence,key=lambda e:e['record_id']),min(30,len(evidence)))
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
  if mismatch:raise ValueError('FRS not corroborating: '+mismatch)
  if frs.streetkey(f['LocationAddress'])!=frs.streetkey(street):error='fresh FRS street disagrees: '+f['LocationAddress']
  else:corroborated=True;detail='fresh identifier,street,city,ZIP,county,state agree'
 except Exception as ex:detail=str(ex)
 out.append(dict(site_id=sid,source_class=e['source_class'],registry_id=rid,transcription=transcription,fresh_source_match='yes' if corroborated else 'no',detail=detail,error=error))
 write(TASK/'audit.csv',out);print(sid,corroborated,error,detail,flush=True);time.sleep(12)
summary=dict(accepted_fills=len(evidence),sampled=len(out),ita_sampled=sum(r['transcription']!='not_ITA' for r in out),transcription_errors=sum(r['transcription']=='FAIL' for r in out),
             fresh_source_matches=sum(r['fresh_source_match']=='yes' for r in out),not_freshly_checkable=sum(r['fresh_source_match']=='no' and not r['error'] for r in out),address_errors=sum(bool(r['error']) for r in out))
(TASK/'audit_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary)
assert len(out)==min(30,len(evidence)) and summary['address_errors']==0 and summary['transcription_errors']==0
# Registry fill rows require their own cited FRS source to re-fetch, not the inherited-bulk exception.
assert all(r['fresh_source_match']=='yes' for r in out if r['source_class']=='registry'),'registry audit source unavailable'

FILE retry_audit.py
"""Retry only unavailable registry audit rows; retain the original failures and reassert the full gate."""
import json,time
from fetch import TASK,frs,read,write
rows=read(TASK/'audit.csv');sites={s['site_id']:s for s in read(TASK/'frame.csv')};ev={e['record_id']:e for e in read(TASK/'evidence.csv')};log=[]
for r in rows:
 if r['fresh_source_match']=='yes':continue
 old=r['detail'];s=sites[r['site_id']];e=ev[r['site_id']];street=e['claim_detail'].removeprefix('street_address ').split(', '+s['city']+', OH ',1)[0]
 try:
  f=frs.facility(frs.fetch(r['registry_id'],'audit_raw'),r['registry_id'])
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

IMPORTEDHELPER exactfunctions frommain tasks/oh-street-address-2026-11-06/build.py
def norm(v):
    return ' '.join(re.findall(r'[A-Z0-9]+', v.upper()))
def streetkey(v):
    aliases = {'STREET':'ST','ROAD':'RD','DRIVE':'DR','AVENUE':'AVE','COURT':'CT','PARKWAY':'PKWY',
               'EAST':'E','WEST':'W','NORTH':'N','SOUTH':'S','HIGHWAY':'HWY','BOULEVARD':'BLVD'}
    return ' '.join(aliases.get(t,t) for t in norm(v).split())
def fetch(rid, folder='raw'):
    p = TASK / folder / (rid + '.json'); p.parent.mkdir(exist_ok=True)
    r = subprocess.run(['curl','--fail','-L','--max-time','45','-A','Mozilla/5.0',FRSU+rid+'&output=JSON'], capture_output=True)
    if r.returncode:
        raise ValueError('FRS fetch failed: '+str(r.returncode))
    data = json.loads(r.stdout)
    p.write_bytes(r.stdout)
    return data
def facility(data, rid):
    records = data['Results']['FRSFacility']
    assert len(records) == 1 and records[0]['RegistryId'] == rid, 'missing/ambiguous registry identifier'
    return records[0]
def conflict(s, f):
    if norm(f.get('CityName') or '') != norm(s['city']): return 'city conflict'
    if not re.fullmatch(r'\d{5}(?:-\d{4})?', s['zip']) or f['ZipCode'][:5] != s['zip'][:5]: return 'ZIP conflict/missing'
    if f['StateAbbr'] != 'OH': return 'state conflict'
    if norm(f.get('CountyName') or '') != norm(s['county'].removesuffix(' County')): return 'county conflict/missing'
    street = f.get('LocationAddress') or ''
    if not re.match(r'^\d+\s+\S+',street) or re.search(r'\bP\.?\s*O\.?\s*BOX\b|POST OFFICE|RURAL ROUTE',street,re.I): return 'non-physical/ambiguous street'
    return ''
INPUT siteID|operatorOrgID|siteName|city|ZIP|county|recordTier|reservedEVID|notedstreetleads
SITE-000140|ORG-000140|Cleveland Specialty Products — Cleveland|Cleveland|44102|Cuyahoga|C|EVD-153070|['12690 ELMWOOD AVENUE']
SITE-000223|ORG-000210|Addipel — Elyria|Elyria|44035|Lorain|C|EVD-153117|['170 Keep Court']
SITE-000233|ORG-000219|Akro-Plastics — Kent|Kent|44240|Portage|C|EVD-153120|['900 West Main Street']
SITE-000238|ORG-000224|Alliance Equipment Company, Inc. — Alliance|Alliance|44601|Stark|C|EVD-153123|['1000 North Union Avenue']
SITE-000244|ORG-000230|American Wire & Cable — Olmsted Falls|Olmsted Falls|44138|Cuyahoga|C|EVD-153125|['7951 Bronson Road']
SITE-000248|ORG-000234|Architectural Fiberglass — Cleveland|Cleveland|44127|Cuyahoga|C|EVD-153127|['8300 Bessemer Ave']
SITE-000251|ORG-000237|AUTOMATED PACKAGING SYSTEMS, INC. - GARFIELD|Garfield Heights|44124|Cuyahoga|U|EVD-153129|['13555 MCCRACKEN ROAD']
SITE-000252|ORG-000237|Automated Packaging Systems-Sealed Air-Bedford — Bedford Heights|Bedford Heights|44146|Cuyahoga|C|EVD-153130|['25900 Solon Road']
SITE-000273|ORG-000257|BVPV Styrenics — Painesville|Painesville|44077|Lake|C|EVD-153139|['786 Hardy Road']
SITE-000288|ORG-000728|Charter Next Generation - Massillon|Massillon|44646|Stark|C|EVD-153145|['8333 Navarre Road SE']
SITE-000303|ORG-000745|Composites One LLC — Ashtabula|Ashtabula|44004-8974|Ashtabula|C|EVD-153152|['4750 Kister Court']
SITE-000305|ORG-000286|Container Compliance — Cleveland|Cleveland|44102|Cuyahoga|U|EVD-153154|['5151 Denison Avenue']
SITE-000367|ORG-000344|Fomo Products — Norton|Norton|44203|Summit|C|EVD-153185|['2775 BARBER ROAD']
SITE-000376|ORG-000352|General Color & Chemical — Minerva|Minerva|44657|Stark|C|EVD-153189|['350 Bridge St']
SITE-000378|ORG-000354|Gmr Technology — Ashtabula|Ashtabula|44004|Ashtabula|C|EVD-153190|['2131 Aetna Road']
SITE-000402|ORG-000377|Industrial Technologies, Inc. — Akron|Akron|44312|Summit|C|EVD-153201|['1643 Massillon Rd']
SITE-000412|ORG-000386|Iten Industries Inc. (Plant 1)|Ashtabula|44005|Ashtabula|C|EVD-153206|['4001 Benefit Ave']
SITE-000432|ORG-000403|Karman Rubber Company — Akron|Akron|44320|Summit|C|EVD-153216|['2331 Copley Road']
SITE-000439|ORG-000410|Killian Latex, Inc. — Akron|Akron|44312|Summit|C|EVD-153221|['2064 Killian Road']
SITE-000462|ORG-000431|Masco (Mercury Plastics)|Middlefield|44062|Geauga|C|EVD-153232|['15760 Madison Road']
SITE-000479|ORG-000448|Mold Surface Textures LLC — Kent|Kent|44240|Portage|C|EVD-153242|['4485 Crystal Parkway Suite 300']
SITE-000494|ORG-000462|Next Dimension Components — Jefferson|Jefferson|44047|Ashtabula|C|EVD-153247|['223 S. Spruce Street']
SITE-000517|ORG-000483|PENTAIR WATER PURIFICATION|Chardon|44024|Geauga|C|EVD-153255|['200 INDUSTRIAL PARKWAY']
SITE-000521|ORG-000486|PET Processors LLC — Painesville|Painesville|44077|Lake|C|EVD-153258|['1350 Bacon Road']
SITE-000547|ORG-000513|Polystar Containment — Stow|Stow|44224|Summit|C|EVD-153269|['1676 Commerce Drive']
SITE-000556|ORG-000521|Premier Oem — Cuyahoga Falls|Cuyahoga Falls|44221|Summit|C|EVD-153273|["3479 State Road. TRI PARENT NOTE 2026-10-30 (pass 16, Stage G; tri-linkage conflicts): TRI's standard parent name for this facility reads 'POLARIS INDUSTRIES INC' and differs from the Atlas parent attribution — TRI parent standardization is stale-by-design (it lags acquisitions and rebrands) and the Atlas link stands on facility evidence (TRIFID 4422WPRMRM3479S). No parent change is made on TRI's say-so"]
SITE-000563|ORG-000527|Progressive Foam Technologies — Beach City|Beach City|44608|Tuscarawas|C|EVD-153277|["6753 Chestnut Ridge Rd.. County correction 2026-10-29 pass 5 (geocode adjudication): Stark → Tuscarawas — mailing-city artifact; address-exact Census geocode + TIGERweb point-in-polygon. Census single-address geocode of 6753 Chestnut Ridge Rd matched '6753 CHESTNUT RIDGE RD NW, BEACH CITY, OH, 44608' and the independent TIGERweb State_County point-in-polygon at that point returns Tuscarawas County. The… Source: https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/State_County/MapServer/1/query?geometry=-81.581486095356%2C40.639665422428&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatial…"]
SITE-000570|ORG-000534|Quality Synthetic Rubber — Twinsburg|Twinsburg|44087|Summit|C|EVD-153282|['1700 Highland Road']
SITE-000580|ORG-000544|Foundation Wellness — Wadsworth|Wadsworth|44281|Medina|C|EVD-153289|['961 Seville Road']
SITE-000589|ORG-000551|Roechling Industrial Cleveland, L.P.|South Euclid|44121|Cuyahoga|C|EVD-153291|['4321 Glenridge Road']
SITE-000590|ORG-000552|Rogers Industrial Products — Akron|Akron|44311|Summit|C|EVD-153292|['532 South Main Street']
SITE-000606|ORG-000567|Seco Machine — North Canton|North Canton|44720|Summit|C|EVD-153298|['5335 MAYFAIR RD']
SITE-000628|ORG-000589|The Step 2 Company — Streetsboro|Streetsboro|44241|Portage|C|EVD-153310|['10010 AURORA HUDSON RD']
SITE-000634|ORG-000595|System Seals — Brecksville|Brecksville|44141|Cuyahoga|U|EVD-153314|['6600 W SNOWVILLE RD']
SITE-000637|ORG-000598|Team Wendy — Cleveland|Cleveland|44110|Cuyahoga|C|EVD-153315|['17000 SAINT CLAIR AVE BLDG 1']
SITE-000650|ORG-000610|Tower Industries LTD — Massillon|Massillon|44647|Stark|C|EVD-153322|['2101 Ninth Street S.W']
SITE-000653|ORG-000612|Trelleborg Seals & Profiles Americas|Aurora|44202|Portage|C|EVD-153323|['285 Lena Drive']
SITE-000657|ORG-000616|Tribotech Composites — Valley View|Valley View|44125|Cuyahoga|C|EVD-153326|['7800 EXCHANGE ST']
SITE-000664|ORG-000623|Uniwall Mfg — Louisville|Louisville|44641|Stark|C|EVD-153329|['1875 AIRPARK DRIVE']
SITE-000670|ORG-000629|Walton Plastics — Walton Hills|Walton Hills|44146|Cuyahoga|C|EVD-153334|['20493 Hannan Pkwy']
RAW SOURCEFIELDS RegistryId/FacilityName/LocationAddress/SupplementalLocation/CityName/ZipCode/CountyName/StateAbbr
{"RegistryId":"110000385100","FacilityName":"ITEN INDUSTRIES, INC. - PLANT 1 (0204010112)","LocationAddress":"4001 BENEFIT AVE.","SupplementalLocation":null,"CityName":"ASHTABULA","ZipCode":"440052150","CountyName":"ASHTABULA","StateAbbr":"OH"}
{"RegistryId":"110000385333","FacilityName":"PENTAIR WATER PURIFICATION","LocationAddress":"200 INDUSTRIAL PARKWAY","SupplementalLocation":null,"CityName":"CHARDON","ZipCode":"44024","CountyName":"GEAUGA","StateAbbr":"OH"}
{"RegistryId":"110000385930","FacilityName":"PET PROCESSORS, L.L.C. (0243000165)","LocationAddress":"1350 BACON ROAD","SupplementalLocation":null,"CityName":"PAINESVILLE","ZipCode":"44077-4781","CountyName":"LAKE","StateAbbr":"OH"}
{"RegistryId":"110000385958","FacilityName":"NOVA CHEMICALS INC","LocationAddress":"786 HARDY ROAD","SupplementalLocation":null,"CityName":"PAINESVILLE","ZipCode":"44077","CountyName":"LAKE","StateAbbr":"OH"}
{"RegistryId":"110000387340","FacilityName":"R\u00c3\u0096CHLING INDUSTRIAL CLEVELAND (1318544510)","LocationAddress":"4321 GLENRIDGE ROAD","SupplementalLocation":null,"CityName":"SOUTH EUCLID","ZipCode":"44121-2891","CountyName":"CUYAHOGA","StateAbbr":"OH"}
{"RegistryId":"110000388429","FacilityName":"FOMO PRODUCTS, INC.","LocationAddress":"2775 BARBER ROAD","SupplementalLocation":null,"CityName":"NORTON","ZipCode":"44203","CountyName":"SUMMIT","StateAbbr":"OH"}
{"RegistryId":"110000390229","FacilityName":"ALLIANCE EQUIPMENT COMPANY, INC. (1576011516)","LocationAddress":"1000 N. UNION AVE.","SupplementalLocation":null,"CityName":"ALLIANCE","ZipCode":"44601-1392","CountyName":"STARK","StateAbbr":"OH"}
{"RegistryId":"110000815164","FacilityName":"AUTOMATED PACKAGING SYSTEMS, INC. - GARFIELD","LocationAddress":"13555 MCCRACKEN ROAD","SupplementalLocation":null,"CityName":"GARFIELD HEIGHTS","ZipCode":"44125-1939","CountyName":"CUYAHOGA","StateAbbr":"OH"}
{"RegistryId":"110001624537","FacilityName":"TOWER INDUSTRIES, LTD.","LocationAddress":"2101 9TH ST SW","SupplementalLocation":null,"CityName":"MASSILLON","ZipCode":"44647-7651","CountyName":"STARK","StateAbbr":"OH"}
{"RegistryId":"110001624582","FacilityName":"UNIWALL MFG. CO. (1576111601)","LocationAddress":"1875 AIRPARK DRIVE","SupplementalLocation":null,"CityName":"LOUISVILLE","ZipCode":"44641","CountyName":"STARK","StateAbbr":"OH"}
{"RegistryId":"110002110448","FacilityName":"QUALITY SYNTHETIC RUBBER INC","LocationAddress":"1700 HIGHLAND RD.","SupplementalLocation":null,"CityName":"TWINSBURG","ZipCode":"44087-2247","CountyName":"SUMMIT","StateAbbr":"OH"}
{"RegistryId":"110002111063","FacilityName":"AMERICAN WIRE & CABLE CO.","LocationAddress":"7951 BRONSON RD.","SupplementalLocation":null,"CityName":"OLMSTED FALLS","ZipCode":"44138","CountyName":"CUYAHOGA","StateAbbr":"OH"}
{"RegistryId":"110002111376","FacilityName":"THE STEP 2 COMPANY, LLC","LocationAddress":"10010 AURORA HUDSON RD.","SupplementalLocation":null,"CityName":"STREETSBORO","ZipCode":"44241-1619","CountyName":"PORTAGE","StateAbbr":"OH"}
{"RegistryId":"110002111660","FacilityName":"KARMAN RUBBER CO","LocationAddress":"2331 COPLEY RD","SupplementalLocation":null,"CityName":"AKRON","ZipCode":"44320","CountyName":"SUMMIT","StateAbbr":"OH"}
{"RegistryId":"110002452603","FacilityName":"CONTAINER COMPLIANCE CORP","LocationAddress":"5151 DENISON AVE","SupplementalLocation":null,"CityName":"CLEVELAND","ZipCode":"44102-5827","CountyName":"CUYAHOGA","StateAbbr":"OH"}
{"RegistryId":"110004597240","FacilityName":"MERCURY PLASTICS, LLC","LocationAddress":"15760 MADISON RD","SupplementalLocation":null,"CityName":"MIDDLEFIELD","ZipCode":"44062","CountyName":"GEAUGA","StateAbbr":"OH"}
{"RegistryId":"110004731112","FacilityName":"ROGERS INDUSTRIAL PRODUCTS, INC.","LocationAddress":"532 S MAIN ST","SupplementalLocation":null,"CityName":"AKRON","ZipCode":"44311","CountyName":"SUMMIT","StateAbbr":"OH"}
{"RegistryId":"110006264586","FacilityName":"PROGRESSIVE FOAM TECHNOLOGIES, INC. (0679000272)","LocationAddress":"6753 CHESTNUT RIDGE RD","SupplementalLocation":null,"CityName":"BEACH CITY","ZipCode":"44608","CountyName":"TUSCARAWAS","StateAbbr":"OH"}
{"RegistryId":"110006429917","FacilityName":"MOLD SURFACE TEXTURES INC","LocationAddress":"4485 CRYSTAL PKWY","SupplementalLocation":"SUITE 200","CityName":"KENT","ZipCode":"44240","CountyName":"PORTAGE","StateAbbr":"OH"}
{"RegistryId":"110006519026","FacilityName":"ARCHITECTURAL FIBERGLASS INC. (1318008262)","LocationAddress":"8300 BESSEMER AVE","SupplementalLocation":null,"CityName":"CLEVELAND","ZipCode":"44127-1839","CountyName":"CUYAHOGA","StateAbbr":"OH"}
{"RegistryId":"110009430767","FacilityName":"AUTOMATED PACKAGING SYSTEMS","LocationAddress":"25900 SOLON RD","SupplementalLocation":null,"CityName":"BEDFORD HEIGHTS","ZipCode":"44146","CountyName":"CUYAHOGA","StateAbbr":"OH"}
{"RegistryId":"110009634495","FacilityName":"POLYSTAR INC","LocationAddress":"1676 COMMERCE DRIVE","SupplementalLocation":null,"CityName":"STOW","ZipCode":"44224-1731","CountyName":"SUMMIT","StateAbbr":"OH"}
{"RegistryId":"110009821336","FacilityName":"KILLIAN LATEX, INC.","LocationAddress":"2064 KILLIAN RD","SupplementalLocation":null,"CityName":"AKRON","ZipCode":"44312-4897","CountyName":"SUMMIT","StateAbbr":"OH"}
{"RegistryId":"110012175243","FacilityName":"REMINGTON PRODUCTS COMPANY","LocationAddress":"961 SEVILLE RD","SupplementalLocation":null,"CityName":"WADSWORTH","ZipCode":"442810506","CountyName":"MEDINA","StateAbbr":"OH"}
{"RegistryId":"110015666992","FacilityName":"AKRO-PLASTICS","LocationAddress":"900 W MAIN ST","SupplementalLocation":null,"CityName":"KENT","ZipCode":"442402218","CountyName":"PORTAGE","StateAbbr":"OH"}
{"RegistryId":"110025332913","FacilityName":"GENERAL COLOR & CHEMICAL CO INC","LocationAddress":"350 BRIDGE ST","SupplementalLocation":null,"CityName":"MINERVA","ZipCode":"44657","CountyName":"CARROLL","StateAbbr":"OH"}
{"RegistryId":"110031249682","FacilityName":"GMR TECHNOLOGY INC (0204010490)","LocationAddress":"2131 AETNA RD.","SupplementalLocation":null,"CityName":"ASHTABULA","ZipCode":"44004","CountyName":"ASHTABULA","StateAbbr":"OH"}
{"RegistryId":"110031434213","FacilityName":"COMPOSITES ONE LLC","LocationAddress":"4750 KISTER CT","SupplementalLocation":null,"CityName":"ASHTABULA","ZipCode":"44004","CountyName":"ASHTABULA","StateAbbr":"OH"}
{"RegistryId":"110037143631","FacilityName":"TEAM WENDY LLC","LocationAddress":"17000 SAINT CLAIR AVE BLDG 1","SupplementalLocation":null,"CityName":"CLEVELAND","ZipCode":"44110","CountyName":"CUYAHOGA","StateAbbr":"OH"}
{"RegistryId":"110043989020","FacilityName":"TEAM WENDY LLC","LocationAddress":"17000 SAINT CLAIR AVE BLDG 1","SupplementalLocation":null,"CityName":"CLEVELAND","ZipCode":"44110","CountyName":"CUYAHOGA","StateAbbr":"OH"}
{"RegistryId":"110046273938","FacilityName":"NEXT DIMENSION COMPONENTS","LocationAddress":"223 SOUTH SPRUCE STREET","SupplementalLocation":null,"CityName":"JEFFERSON","ZipCode":"44047","CountyName":"ASHTABULA","StateAbbr":"OH"}
{"RegistryId":"110046559434","FacilityName":"TRIBOTECH COMPOSITES, INC.","LocationAddress":"7800 EXCHANGE ST","SupplementalLocation":null,"CityName":"VALLEY VIEW","ZipCode":"44125","CountyName":"CUYAHOGA","StateAbbr":"OH"}
{"RegistryId":"110054879789","FacilityName":"CLEVELAND SPECIALTY PRODUCTS","LocationAddress":"2130 WEST 110TH ST","SupplementalLocation":null,"CityName":"CLEVELAND","ZipCode":"44102","CountyName":"CUYAHOGA","StateAbbr":"OH"}
{"RegistryId":"110070070026","FacilityName":"PREMIER OEM","LocationAddress":"3479 STATE RD","SupplementalLocation":null,"CityName":"CUYAHOGA FALLS","ZipCode":"44223","CountyName":"SUMMIT COUNTY","StateAbbr":"OH"}
{"RegistryId":"110070207909","FacilityName":"WALTON PLASTICS INC","LocationAddress":"20493 HANNAN PKWY","SupplementalLocation":null,"CityName":"WALTON HILLS","ZipCode":"44146","CountyName":"CUYAHOGA","StateAbbr":"OH"}
{"RegistryId":"110070791866","FacilityName":"TRELLEBORG SEALS & PROFILES AMERICAS","LocationAddress":"285 LENA DR","SupplementalLocation":null,"CityName":"AURORA","ZipCode":"44202","CountyName":"PORTAGE COUNTY","StateAbbr":"OH"}
{"RegistryId":"110071018510","FacilityName":"SECO MACHINE","LocationAddress":"5335 MAYFAIR RD","SupplementalLocation":null,"CityName":"NORTH CANTON","ZipCode":"44720","CountyName":"SUMMIT COUNTY","StateAbbr":"OH"}
{"RegistryId":"110071344621","FacilityName":"INDUSTRIAL TECHNOLOGIES INC.","LocationAddress":"1643 MASSILLON ROAD","SupplementalLocation":null,"CityName":"SPRINGFIELD, TOWNSHIP OF","ZipCode":"44312","CountyName":null,"StateAbbr":"OH"}
{"RegistryId":"110071381043","FacilityName":"SYSTEM SEALS INC","LocationAddress":"6600 W SNOWVILLE RD","SupplementalLocation":null,"CityName":"BRECKSVILLE","ZipCode":"44141","CountyName":"CUYAHOGA","StateAbbr":"OH"}
{"RegistryId":"110071956474","FacilityName":"CHARTER NEXT GENERATION - MASSILLON","LocationAddress":"8333 NAVARRE RD SE","SupplementalLocation":null,"CityName":"MASSILLON","ZipCode":"44646","CountyName":"STARK COUNTY","StateAbbr":"OH"}
FILE evidence.csv
evidence_id,record_table,record_id,claim_type,claim_detail,source_class,source_ref,observed_date,tier_effect,created_by,notes
EVD-153120,sites,SITE-000233,address,"street_address 900 W MAIN ST, Kent, OH 44240",registry,https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id=110015666992&output=JSON,2026-11-06,supports_C,atlas-L2-oh-address-cu,"EPA FRS registry 110015666992; fetched 2026-11-06; raw copy tasks/oh-street-address-cu-2026-11-06/raw/110015666992.json. County, county_source, ZIP, record tier and status unchanged."
EVD-153123,sites,SITE-000238,address,"street_address 1000 N. UNION AVE., Alliance, OH 44601",registry,https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id=110000390229&output=JSON,2026-11-06,supports_C,atlas-L2-oh-address-cu,"EPA FRS registry 110000390229; fetched 2026-11-06; raw copy tasks/oh-street-address-cu-2026-11-06/raw/110000390229.json. County, county_source, ZIP, record tier and status unchanged."
EVD-153125,sites,SITE-000244,address,"street_address 7951 BRONSON RD., Olmsted Falls, OH 44138",registry,https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id=110002111063&output=JSON,2026-11-06,supports_C,atlas-L2-oh-address-cu,"EPA FRS registry 110002111063; fetched 2026-11-06; raw copy tasks/oh-street-address-cu-2026-11-06/raw/110002111063.json. County, county_source, ZIP, record tier and status unchanged."
EVD-153127,sites,SITE-000248,address,"street_address 8300 BESSEMER AVE, Cleveland, OH 44127",registry,https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id=110006519026&output=JSON,2026-11-06,supports_C,atlas-L2-oh-address-cu,"EPA FRS registry 110006519026; fetched 2026-11-06; raw copy tasks/oh-street-address-cu-2026-11-06/raw/110006519026.json. County, county_source, ZIP, record tier and status unchanged."
EVD-153152,sites,SITE-000303,address,"street_address 4750 KISTER CT, Ashtabula, OH 44004-8974",registry,https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id=110031434213&output=JSON,2026-11-06,supports_C,atlas-L2-oh-address-cu,"EPA FRS registry 110031434213; fetched 2026-11-06; raw copy tasks/oh-street-address-cu-2026-11-06/raw/110031434213.json. County, county_source, ZIP, record tier and status unchanged."
EVD-153154,sites,SITE-000305,address,"street_address 5151 DENISON AVE, Cleveland, OH 44102",registry,https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id=110002452603&output=JSON,2026-11-06,supports_C,atlas-L2-oh-address-cu,"EPA FRS registry 110002452603; fetched 2026-11-06; raw copy tasks/oh-street-address-cu-2026-11-06/raw/110002452603.json. County, county_source, ZIP, record tier and status unchanged."
EVD-153185,sites,SITE-000367,address,"street_address 2775 BARBER ROAD, Norton, OH 44203",registry,https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id=110000388429&output=JSON,2026-11-06,supports_C,atlas-L2-oh-address-cu,"EPA FRS registry 110000388429; fetched 2026-11-06; raw copy tasks/oh-street-address-cu-2026-11-06/raw/110000388429.json. County, county_source, ZIP, record tier and status unchanged."
EVD-153190,sites,SITE-000378,address,"street_address 2131 AETNA RD., Ashtabula, OH 44004",registry,https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id=110031249682&output=JSON,2026-11-06,supports_C,atlas-L2-oh-address-cu,"EPA FRS registry 110031249682; fetched 2026-11-06; raw copy tasks/oh-street-address-cu-2026-11-06/raw/110031249682.json. County, county_source, ZIP, record tier and status unchanged."
EVD-153216,sites,SITE-000432,address,"street_address 2331 COPLEY RD, Akron, OH 44320",registry,https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id=110002111660&output=JSON,2026-11-06,supports_C,atlas-L2-oh-address-cu,"EPA FRS registry 110002111660; fetched 2026-11-06; raw copy tasks/oh-street-address-cu-2026-11-06/raw/110002111660.json. County, county_source, ZIP, record tier and status unchanged."
EVD-153221,sites,SITE-000439,address,"street_address 2064 KILLIAN RD, Akron, OH 44312",registry,https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id=110009821336&output=JSON,2026-11-06,supports_C,atlas-L2-oh-address-cu,"EPA FRS registry 110009821336; fetched 2026-11-06; raw copy tasks/oh-street-address-cu-2026-11-06/raw/110009821336.json. County, county_source, ZIP, record tier and status unchanged."
EVD-153232,sites,SITE-000462,address,"street_address 15760 MADISON RD, Middlefield, OH 44062",registry,https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id=110004597240&output=JSON,2026-11-06,supports_C,atlas-L2-oh-address-cu,"EPA FRS registry 110004597240; fetched 2026-11-06; raw copy tasks/oh-street-address-cu-2026-11-06/raw/110004597240.json. County, county_source, ZIP, record tier and status unchanged."
EVD-153247,sites,SITE-000494,address,"street_address 223 SOUTH SPRUCE STREET, Jefferson, OH 44047",registry,https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id=110046273938&output=JSON,2026-11-06,supports_C,atlas-L2-oh-address-cu,"EPA FRS registry 110046273938; fetched 2026-11-06; raw copy tasks/oh-street-address-cu-2026-11-06/raw/110046273938.json. County, county_source, ZIP, record tier and status unchanged."
EVD-153255,sites,SITE-000517,address,"street_address 200 INDUSTRIAL PARKWAY, Chardon, OH 44024",registry,https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id=110000385333&output=JSON,2026-11-06,supports_C,atlas-L2-oh-address-cu,"EPA FRS registry 110000385333; fetched 2026-11-06; raw copy tasks/oh-street-address-cu-2026-11-06/raw/110000385333.json. County, county_source, ZIP, record tier and status unchanged."
EVD-153258,sites,SITE-000521,address,"street_address 1350 BACON ROAD, Painesville, OH 44077",registry,https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id=110000385930&output=JSON,2026-11-06,supports_C,atlas-L2-oh-address-cu,"EPA FRS registry 110000385930; fetched 2026-11-06; raw copy tasks/oh-street-address-cu-2026-11-06/raw/110000385930.json. County, county_source, ZIP, record tier and status unchanged."
EVD-153269,sites,SITE-000547,address,"street_address 1676 COMMERCE DRIVE, Stow, OH 44224",registry,https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id=110009634495&output=JSON,2026-11-06,supports_C,atlas-L2-oh-address-cu,"EPA FRS registry 110009634495; fetched 2026-11-06; raw copy tasks/oh-street-address-cu-2026-11-06/raw/110009634495.json. County, county_source, ZIP, record tier and status unchanged."
EVD-153282,sites,SITE-000570,address,"street_address 1700 HIGHLAND RD., Twinsburg, OH 44087",registry,https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id=110002110448&output=JSON,2026-11-06,supports_C,atlas-L2-oh-address-cu,"EPA FRS registry 110002110448; fetched 2026-11-06; raw copy tasks/oh-street-address-cu-2026-11-06/raw/110002110448.json. County, county_source, ZIP, record tier and status unchanged."
EVD-153289,sites,SITE-000580,address,"street_address 961 SEVILLE RD, Wadsworth, OH 44281",registry,https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id=110012175243&output=JSON,2026-11-06,supports_C,atlas-L2-oh-address-cu,"EPA FRS registry 110012175243; fetched 2026-11-06; raw copy tasks/oh-street-address-cu-2026-11-06/raw/110012175243.json. County, county_source, ZIP, record tier and status unchanged."
EVD-153292,sites,SITE-000590,address,"street_address 532 S MAIN ST, Akron, OH 44311",registry,https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id=110004731112&output=JSON,2026-11-06,supports_C,atlas-L2-oh-address-cu,"EPA FRS registry 110004731112; fetched 2026-11-06; raw copy tasks/oh-street-address-cu-2026-11-06/raw/110004731112.json. County, county_source, ZIP, record tier and status unchanged."
EVD-153310,sites,SITE-000628,address,"street_address 10010 AURORA HUDSON RD., Streetsboro, OH 44241",registry,https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id=110002111376&output=JSON,2026-11-06,supports_C,atlas-L2-oh-address-cu,"EPA FRS registry 110002111376; fetched 2026-11-06; raw copy tasks/oh-street-address-cu-2026-11-06/raw/110002111376.json. County, county_source, ZIP, record tier and status unchanged."
EVD-153314,sites,SITE-000634,address,"street_address 6600 W SNOWVILLE RD, Brecksville, OH 44141",registry,https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id=110071381043&output=JSON,2026-11-06,supports_C,atlas-L2-oh-address-cu,"EPA FRS registry 110071381043; fetched 2026-11-06; raw copy tasks/oh-street-address-cu-2026-11-06/raw/110071381043.json. County, county_source, ZIP, record tier and status unchanged."
EVD-153315,sites,SITE-000637,address,"street_address 17000 SAINT CLAIR AVE BLDG 1, Cleveland, OH 44110",registry,https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id=110043989020&output=JSON,2026-11-06,supports_C,atlas-L2-oh-address-cu,"EPA FRS registry 110043989020; fetched 2026-11-06; raw copy tasks/oh-street-address-cu-2026-11-06/raw/110043989020.json. County, county_source, ZIP, record tier and status unchanged."
EVD-153326,sites,SITE-000657,address,"street_address 7800 EXCHANGE ST, Valley View, OH 44125",registry,https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id=110046559434&output=JSON,2026-11-06,supports_C,atlas-L2-oh-address-cu,"EPA FRS registry 110046559434; fetched 2026-11-06; raw copy tasks/oh-street-address-cu-2026-11-06/raw/110046559434.json. County, county_source, ZIP, record tier and status unchanged."
EVD-153329,sites,SITE-000664,address,"street_address 1875 AIRPARK DRIVE, Louisville, OH 44641",registry,https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id=110001624582&output=JSON,2026-11-06,supports_C,atlas-L2-oh-address-cu,"EPA FRS registry 110001624582; fetched 2026-11-06; raw copy tasks/oh-street-address-cu-2026-11-06/raw/110001624582.json. County, county_source, ZIP, record tier and status unchanged."
EVD-153334,sites,SITE-000670,address,"street_address 20493 HANNAN PKWY, Walton Hills, OH 44146",registry,https://frs-public.epa.gov/ords/frs_public2/frs_rest_services.get_facilities?registry_id=110070207909&output=JSON,2026-11-06,supports_C,atlas-L2-oh-address-cu,"EPA FRS registry 110070207909; fetched 2026-11-06; raw copy tasks/oh-street-address-cu-2026-11-06/raw/110070207909.json. County, county_source, ZIP, record tier and status unchanged."

FILE verdicts.csv
site_id,verdict,street_address,evidence_id,reason,availability
SITE-000140,STILL_UNCERTAIN,2130 WEST 110TH ST,,notes street conflicts; dated address adjudication needed,
SITE-000223,STILL_UNCERTAIN,,,need admissible site-keyed physical street witness; FRS unavailable and no qualifying inherited ITA,110071956419: FRS fetch failed: 22
SITE-000233,VERIFIED,900 W MAIN ST,EVD-153120,,
SITE-000238,VERIFIED,1000 N. UNION AVE.,EVD-153123,,
SITE-000244,VERIFIED,7951 BRONSON RD.,EVD-153125,,
SITE-000248,VERIFIED,8300 BESSEMER AVE,EVD-153127,,
SITE-000251,STILL_UNCERTAIN,13555 MCCRACKEN ROAD,,FRS 110000815164: ZIP conflict/missing,
SITE-000252,STILL_UNCERTAIN,25900 SOLON RD,,ITA city/ZIP conflict or missing,
SITE-000273,STILL_UNCERTAIN,786 HARDY ROAD,,ITA city/ZIP conflict or missing,
SITE-000288,STILL_UNCERTAIN,8333 NAVARRE RD SE,,FRS 110071956474: county conflict/missing,
SITE-000303,VERIFIED,4750 KISTER CT,EVD-153152,,
SITE-000305,VERIFIED,5151 DENISON AVE,EVD-153154,,
SITE-000367,VERIFIED,2775 BARBER ROAD,EVD-153185,,
SITE-000376,STILL_UNCERTAIN,350 BRIDGE ST,,FRS 110025332913: county conflict/missing,
SITE-000378,VERIFIED,2131 AETNA RD.,EVD-153190,,
SITE-000402,STILL_UNCERTAIN,1643 MASSILLON ROAD,,FRS 110071344621: city conflict,
SITE-000412,STILL_UNCERTAIN,4001 BENEFIT AVE.,,ITA city/ZIP conflict or missing,
SITE-000432,VERIFIED,2331 COPLEY RD,EVD-153216,,
SITE-000439,VERIFIED,2064 KILLIAN RD,EVD-153221,,
SITE-000462,VERIFIED,15760 MADISON RD,EVD-153232,,
SITE-000479,STILL_UNCERTAIN,4485 CRYSTAL PKWY,,notes street conflicts; dated address adjudication needed,
SITE-000494,VERIFIED,223 SOUTH SPRUCE STREET,EVD-153247,,
SITE-000517,VERIFIED,200 INDUSTRIAL PARKWAY,EVD-153255,,
SITE-000521,VERIFIED,1350 BACON ROAD,EVD-153258,,
SITE-000547,VERIFIED,1676 COMMERCE DRIVE,EVD-153269,,
SITE-000556,STILL_UNCERTAIN,3479 STATE RD,,FRS 110070070026: ZIP conflict/missing; ITA city/ZIP conflict or missing; notes street conflicts; dated address adjudication needed,
SITE-000563,STILL_UNCERTAIN,6753 CHESTNUT RIDGE RD,,notes street conflicts; dated address adjudication needed,
SITE-000570,VERIFIED,1700 HIGHLAND RD.,EVD-153282,,
SITE-000580,VERIFIED,961 SEVILLE RD,EVD-153289,,
SITE-000589,STILL_UNCERTAIN,4321 GLENRIDGE ROAD,,ITA city/ZIP conflict or missing,
SITE-000590,VERIFIED,532 S MAIN ST,EVD-153292,,
SITE-000606,STILL_UNCERTAIN,5335 MAYFAIR RD,,FRS 110071018510: county conflict/missing,
SITE-000628,VERIFIED,10010 AURORA HUDSON RD.,EVD-153310,,
SITE-000634,VERIFIED,6600 W SNOWVILLE RD,EVD-153314,,
SITE-000637,VERIFIED,17000 SAINT CLAIR AVE BLDG 1,EVD-153315,,
SITE-000650,STILL_UNCERTAIN,2101 9TH ST SW,,notes street conflicts; dated address adjudication needed,
SITE-000653,STILL_UNCERTAIN,285 LENA DR,,FRS 110070791866: county conflict/missing,
SITE-000657,VERIFIED,7800 EXCHANGE ST,EVD-153326,,
SITE-000664,VERIFIED,1875 AIRPARK DRIVE,EVD-153329,,
SITE-000670,VERIFIED,20493 HANNAN PKWY,EVD-153334,,

FILE audit.csv
site_id,source_class,registry_id,transcription,detail,error,fresh_source_match
SITE-000637,registry,110043989020,not_ITA,"fresh identifier,street,city,ZIP,county,state agree",,yes
SITE-000238,registry,110000390229,not_ITA,"fresh identifier,street,city,ZIP,county,state agree",,yes
SITE-000244,registry,110002111063,not_ITA,"fresh identifier,street,city,ZIP,county,state agree",,yes
SITE-000303,registry,110031434213,not_ITA,"fresh identifier,street,city,ZIP,county,state agree on bounded retry",,yes
SITE-000378,registry,110031249682,not_ITA,"fresh identifier,street,city,ZIP,county,state agree on bounded retry",,yes
SITE-000233,registry,110015666992,not_ITA,"fresh identifier,street,city,ZIP,county,state agree",,yes
SITE-000462,registry,110004597240,not_ITA,"fresh identifier,street,city,ZIP,county,state agree",,yes
SITE-000517,registry,110000385333,not_ITA,"fresh identifier,street,city,ZIP,county,state agree",,yes
SITE-000432,registry,110002111660,not_ITA,"fresh identifier,street,city,ZIP,county,state agree",,yes
SITE-000547,registry,110009634495,not_ITA,"fresh identifier,street,city,ZIP,county,state agree",,yes
SITE-000590,registry,110004731112,not_ITA,"fresh identifier,street,city,ZIP,county,state agree",,yes
SITE-000628,registry,110002111376,not_ITA,"fresh identifier,street,city,ZIP,county,state agree",,yes
SITE-000521,registry,110000385930,not_ITA,"fresh identifier,street,city,ZIP,county,state agree",,yes
SITE-000580,registry,110012175243,not_ITA,"fresh identifier,street,city,ZIP,county,state agree",,yes
SITE-000664,registry,110001624582,not_ITA,"fresh identifier,street,city,ZIP,county,state agree",,yes
SITE-000248,registry,110006519026,not_ITA,"fresh identifier,street,city,ZIP,county,state agree",,yes
SITE-000670,registry,110070207909,not_ITA,"fresh identifier,street,city,ZIP,county,state agree",,yes
SITE-000439,registry,110009821336,not_ITA,"fresh identifier,street,city,ZIP,county,state agree",,yes
SITE-000367,registry,110000388429,not_ITA,"fresh identifier,street,city,ZIP,county,state agree",,yes
SITE-000657,registry,110046559434,not_ITA,"fresh identifier,street,city,ZIP,county,state agree",,yes
SITE-000305,registry,110002452603,not_ITA,"fresh identifier,street,city,ZIP,county,state agree",,yes
SITE-000570,registry,110002110448,not_ITA,"fresh identifier,street,city,ZIP,county,state agree",,yes
SITE-000494,registry,110046273938,not_ITA,"fresh identifier,street,city,ZIP,county,state agree",,yes
SITE-000634,registry,110071381043,not_ITA,"fresh identifier,street,city,ZIP,county,state agree",,yes

FILE audit_summary.json
{
  "accepted_fills": 24,
  "sampled": 24,
  "ita_sampled": 0,
  "transcription_errors": 0,
  "address_errors": 0,
  "fresh_source_matches": 24,
  "not_freshly_checkable": 0
}

FILE summary.json
{
  "cu_active_blank_cohort": 819,
  "frs_known_zip_eligible": 108,
  "worked": 40,
  "unworked_cohort": 779,
  "unworked_frs_known_zip": 68,
  "fills": 24,
  "holds": 16,
  "active_ohio_sites": 1883,
  "before_streets": 286,
  "after_streets": 310
}
