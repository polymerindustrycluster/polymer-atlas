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
