"""Integrate selected own-site address blocks; validate every planned write before touching canonical data."""
import csv,hashlib,json,re,sys
from pathlib import Path
from urllib.parse import urlparse
TASK=Path(__file__).resolve().parent;ROOT=TASK.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from shard_io import append_sorted
from fetch import read,write,extract,fetch
DATE='2026-11-06'
def key(v):
 aliases={'STREET':'ST','ROAD':'RD','AVENUE':'AVE','DRIVE':'DR','COURT':'CT','PARKWAY':'PKWY','BOULEVARD':'BLVD','PLACE':'PL','PARK':'PK','RTE':'ROUTE','WEST':'W','EAST':'E','NORTH':'N','SOUTH':'S'}
 return ' '.join(aliases.get(t,t) for t in re.findall('[A-Z0-9]+',v.upper()))
def note_streets(s):
 out=[x[0] for x in extract(s['notes'],s['city'])]
 m=re.search(r'(?i)\bstreet(?:\s*\([^)]*\))?:\s*(.+)',s['notes'])
 if m:
  value=re.split(r'\.\s+(?=PASS|BAND|CERT|Ring|INTEGRATION|Parcel|Re-pointed|NAICS|Source|Address confirmed|Co-located|Converted|Filing basis|(?i:county UNVERIFIED)|\[)',m[1])[0]
  value=re.split(r',\s*'+re.escape(s['city'])+r'\b',value,maxsplit=1,flags=re.I)[0]
  value=re.split(r'\s+\((?=(?i:address per|company contact|GS1 manufacturer|per (?:the operator|wave-\d+ verdict)))',value,maxsplit=1)[0]
  out.append(value.rstrip('. '))
 out+=re.findall(r'(?i)(?:Address[^:]{0,120}:|at)\s*(\d+\s+[^,;()]+),\s*'+re.escape(s['city']),s['notes'])
 return out
def plan():
 frame=read(TASK/'frame.csv');selected=[r for r in frame if r['selected']=='yes'];checks=read(TASK/'rawchecks.csv')
 assert len(frame)==448 and len({s['site_id'] for s in frame})==448
 assert len(selected)==88 and len({s['reserved_evidence_id'] for s in frame})==448
 assert {r['site_id'] for r in checks}=={s['site_id'] for s in selected},'source yield mismatch'
 canonical=read(ROOT/'data/sites_OH.csv')
 verdicts=[];ev=[]
 for s in selected:
  rows=[r for r in checks if r['site_id']==s['site_id'] and r['street_address']];why=[]
  if not s['city'].strip():why.append('recorded city missing; establish locality before filling street')
  if not rows:why.append('need own-page physical street block at recorded city; no admissible block fetched')
  peers=[t for t in canonical if t['site_id']!=s['site_id'] and t['org_id']==s['org_id'] and t['operating_status']=='active' and key(t['city'])==key(s['city']) and (not s['zip'] or not t['zip'] or s['zip'][:5]==t['zip'][:5])]
  if rows and peers and not note_streets(s):why.append('generic corporate address lacks site-specific binding among same-operator city/ZIP records')
  if any(r['posture'] for r in rows):why.append('mailing-only or ambiguous address context')
  host=lambda u:(urlparse(u if '://' in u else 'https://'+u).hostname or '').removeprefix('www.')
  for r in rows:
   assert host(r['url'])==host(s['website']),'witness leaves held operator host'
   assert re.fullmatch('[0-9a-f]{64}',r['sha256']),'missing page digest'
   assert any(key(a)==key(r['street_address']) and z==r['source_zip'] for a,z,q in extract(r['quote'],s['city'])),'quote/field binding failure'
  if len({key(r['street_address']) for r in rows})>1:why.append('own-page street blocks disagree')
  if len({r['source_zip'][:5] for r in rows})>1:why.append('own-page ZIPs disagree')
  if any(s['zip'] and s['zip'][:5]!=r['source_zip'][:5] for r in rows):why.append('own-page ZIP conflicts with current site ZIP')
  if rows and re.search(r'(?i)\bZIP discrepancy:',s['notes']):why.append('existing notes name an unresolved ZIP discrepancy; reconcile primary locality first')
  if rows and any(key(n)!=key(rows[0]['street_address']) for n in note_streets(s)):why.append('notes address conflicts; dated adjudication needed')
  if any(key(r['street_address']).startswith(('PO BOX','P O BOX')) or not re.match(r'^\d+\s+[A-Za-z]',r['street_address']) for r in rows):why.append('non-physical or ambiguous street')
  v=dict(site_id=s['site_id'],verdict='STILL_UNCERTAIN' if why else 'VERIFIED',street_address=rows[0]['street_address'] if rows else '',evidence_id='' if why else s['reserved_evidence_id'],reason='; '.join(why))
  verdicts.append(v)
  if not why:
   r=rows[0];ev.append(dict(evidence_id=s['reserved_evidence_id'],record_table='sites',record_id=s['site_id'],claim_type='address',
       claim_detail=f"street_address {r['street_address']}, {s['city']}, OH; own-page ZIP {r['source_zip']}",
       source_class='own_site',source_ref=r['url'],observed_date=DATE,tier_effect='supports_A',created_by='atlas-L2-oh-address-7',
       notes=f"Raw checked {DATE}; SHA-256 {r['sha256']}; quote: {r['quote']}. County, county_source, ZIP and record tier unchanged."))
 assert len(verdicts)==len({v['site_id'] for v in verdicts})==88
 return selected,verdicts,ev
def note_plan():
 flags=read(TASK/'note_flags.csv');assert len(flags)==len({r['site_id'] for r in flags})==6
 frame={r['site_id']:r for r in read(TASK/'frame.csv')};ev=[]
 for r in flags:
  assert r['other_site_id'] in frame and r['site_id']!=r['other_site_id']
  if not r['evidence_id']:continue
  s=frame[r['site_id']]
  quote=r['source_notes'].split('; quote: ')[1].removesuffix('. County, county_source, ZIP and record tier unchanged.')
  assert any(key(a)==key(r['street_address']) and z==r['source_zip'] for a,z,q in extract(quote,s['city']))
  assert (urlparse(r['source_ref']).hostname or '').removeprefix('www.')==(urlparse(s['website']).hostname or '').removeprefix('www.')
  ev.append(dict(evidence_id=r['evidence_id'],record_table='sites',record_id=r['site_id'],claim_type='address',claim_detail=f"Address overlap lead with {r['other_site_id']}: both publish {r['street_address']}, {s['city']}; no merge or co-location adjudication",source_class='own_site',source_ref=r['source_ref'],observed_date=DATE,tier_effect='supports_A',created_by='atlas-L2-oh-address-7',notes=r['source_notes']))
 assert {e['evidence_id'] for e in ev}=={'EVD-152448','EVD-152449'}
 return flags,ev
def run(apply=False):
 selected,verdicts,ev=plan();sites=read(ROOT/'data/sites_OH.csv');byid={s['site_id']:s for s in sites};frozen={s['site_id']:s for s in selected};eb={e['record_id']:e for e in ev}
 flags,note_ev=note_plan();flag_byid={r['site_id']:r for r in flags};all_ev=ev+note_ev
 frame={r['site_id']:r for r in read(TASK/'frame.csv')}
 for r in flags:
  s=byid[r['site_id']];old=frame[r['site_id']]
  for field in ('org_id','city','state','county','county_source','zip','verification_tier','operating_status'):assert s[field]==old[field],(s['site_id'],field,'flag target changed')
  assert s['notes'] in (r['notes_before'],r['notes_before']+r['note_append']),'pre-existing notes conflict'
  assert s['street_address'] in ('',r['street_address']),'flag address changed'
  if r['site_id'] in eb:eb[r['site_id']]['claim_detail']+=f"; possible duplicate/co-location lead with {r['other_site_id']}; no adjudication"
 # Whole-namespace preflight, including foreign shards. No canonical write happens before every invariant passes.
 existing={}
 for p in (ROOT/'data').glob('evidence_*.csv'):
  for r in read(p):
   if r['evidence_id'] in {e['evidence_id'] for e in all_ev}:existing.setdefault(r['evidence_id'],[]).append((p.name,r))
 new=[]
 for v in verdicts:
  if v['verdict']!='VERIFIED':continue
  s=byid[v['site_id']];old=frozen[s['site_id']];e=eb[s['site_id']]
  for field in ('org_id','city','state','county','county_source','zip','verification_tier','operating_status'):assert s[field]==old[field],(s['site_id'],field,'main changed')
  assert s['notes'] in (old['notes'],old['notes']+flag_byid.get(s['site_id'],{}).get('note_append','')),'main notes changed'
  assert s['operating_status']=='active' and not old['street_address']
  assert s['street_address'] in ('',v['street_address']),'pre-existing street conflict'
  have=existing.get(e['evidence_id'],[])
  assert not have or have==[('evidence_sites_OH.csv',e)],'global evidence ID collision'
  if not have:new.append(e)
 for e in note_ev:
  have=existing.get(e['evidence_id'],[])
  assert not have or have==[('evidence_sites_OH.csv',e)],'global notes evidence ID collision'
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
  for r in flags:byid[r['site_id']]['notes']=r['notes_before']+r['note_append']
  if new:append_sorted(ROOT/'data/evidence_sites_OH.csv',new,'evidence_id')
  write(ROOT/'data/sites_OH.csv',sites)
 write(TASK/'verdicts.csv',verdicts);write(TASK/'holds.csv',[r for r in verdicts if r['verdict']!='VERIFIED'])
 if all_ev:write(TASK/'evidence.csv',all_ev)
 active=[r for r in sites if r['operating_status']=='active']
 actual=sum(bool(s['street_address']) for s in active)
 before=actual-len(ev) if all(byid[e['record_id']]['street_address'] for e in ev) else actual
 summary=dict(eligible_sites=448,prior_batch_sites=360,worked=88,unworked=0,fills=len(ev),holds=88-len(ev),note_flags=len(flags),evidence_rows=len(all_ev),active_ohio_sites=len(active),before_streets=before,after_streets=before+len(ev))
 (TASK/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary)
if __name__=='__main__':run('--apply' in sys.argv)
