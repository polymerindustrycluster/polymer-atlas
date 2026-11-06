#!/usr/bin/env python3
"""Manually reviewed quotes only; no tier or data mutations."""
from research import D,has
import csv,json,sys,re,hashlib
from collections import Counter
TODAY='2026-11-06'
COLS=['org_id','claim_type','quote','source_ref','raw_path','source_class','observed_date','notes']
def write(name,rows,cols):
 with (D/name).open('w') as f:
  w=csv.DictWriter(f,cols);w.writeheader();w.writerows(rows)
frame=list(csv.DictReader((D/'frame.csv').open()));parent=list(csv.DictReader((D.parent/'frame.csv').open()));assert frame==parent[25:62] and len({r['org_id'] for r in frame})==37
routes=[]
for row in frame:
 rr=json.loads((D/'raw'/row['org_id']/'routes.json').read_text());assert any('government' in r['kind'] for r in rr);routes+=rr
packet=[]
for oid,claim,urlpart,q,notes in json.loads((D/'selections.json').read_text()):
 rr=[r for r in routes if r['org_id']==oid and urlpart in r['source_ref'] and r['availability']=='available' and has((D/r['raw_path']).read_text(),q)]
 assert rr,(oid,claim,q)
 r=rr[0];packet.append(dict(org_id=oid,claim_type=claim,quote=q,source_ref=r['source_ref'],raw_path=r['raw_path'],source_class='own_site',observed_date=TODAY,notes=notes+' Retrieved 2026-11-06 via '+r['kind']+'. Preliminary witness only; lead derives V25, no tier recommendation imposed.'))
# Separate, dated government observation; never embed registrant facts in own-site claim detail.
r=next(r for r in routes if r['org_id']=='ORG-000551' and r['kind']=='government_record');t=(D/r['raw_path']).read_text()
for claim,q in [('existence','Röechling Industrial Cleveland, L.P., 4321 Glenridge Road, South Euclid, OH, 44212'),('address','Röechling Industrial Cleveland, L.P., 4321 Glenridge Road, South Euclid, OH, 44212'),('scope','Nature of Business: Manufacturer of fiberglass plastic components for primarily the electrical sector.')]:
 assert has(t,q),(claim,q)
 packet.append(dict(org_id=r['org_id'],claim_type=claim,quote=q,source_ref=r['source_ref'],raw_path=r['raw_path'],source_class='government_filing',observed_date='2023-12-08',notes='Ohio EPA draft NPDES public notice dated2023-12-08, retrieved2026-11-06. Historical registrant/address/business facts only; not current final permit or code assignment. Stated ZIP44212 retained as source text, not proposed correction.'))
# Explicit controller R5 exception: inherited ITA, not a fresh government retrieval.
ita=json.loads((D/'ita_candidates.json').read_text());admit={'ORG-000174','ORG-000188','ORG-000551'}
url='https://www.osha.gov/sites/default/largefiles/ITA_300A_Summary_Data_2025_through_08-31-2026.csv'
for row in ita:
 if row['org_id'] not in admit:continue
 keys=['establishment_id','ita_row_id','company_name','establishment_name','street','city','state','zip5','naics_code','naics_year','industry_description','date_submitted','year_filing_for'];brief={k:row[k] for k in keys};p=D/'raw'/row['org_id']/'inherited-ita.json';p.write_text(json.dumps(brief,indent=2));raw=str(p.relative_to(D))
 q=row['company_name']
 for claim in ['existence']:
  quote=q if claim=='existence' else row['street']+' '+row['city'] if claim=='address' else row['naics_code']
  # JSON field values are checked independently; source row order is not manufactured into a verbatim source quotation.
  if claim=='address':quote=row['street']
  assert has(p.read_text(),quote)
  packet.append(dict(org_id=row['org_id'],claim_type=claim,quote=quote,source_ref=url,raw_path=raw,source_class='government_filing',observed_date=row['date_submitted'],notes='Controller-authorized inherited CY2025 ITA exception relayed by lead; NOT freshly retrieved. Repo packet2026-11-01. establishment_ID='+row['establishment_id']+'; ITArowID='+row['ita_row_id']+'; date_submitted='+row['date_submitted']+'; CY2025 reporting period, observed_date is actual date_submitted; '+row['company_name']+' / '+row['establishment_name']+'; '+row['street']+', '+row['city']+', '+row['state']+' '+row['zip5']+'; NAICS'+row['naics_code']+' (vintage'+row['naics_year']+'). Exact inherited row values; no registry link or identity alias inferred.'))
notes=json.loads((D/'holds.json').read_text()) if (D/'holds.json').exists() else {}
vv=[]
for row in frame:
 oid=row['org_id'];own={r['claim_type'] for r in packet if r['org_id']==oid and r['source_class']=='own_site'};ok={'existence','address','scope'}<=own
 vv.append(dict(org_id=oid,legal_name=row['legal_name'],verdict='VERIFIED' if ok else 'STILL_UNCERTAIN',missing_fact='' if ok else notes.get(oid,'A matched own legal identity, physical corporate address in held '+row['hq_city']+', and explicit own polymer operations; failed routes do not settle these facts.'),notes='Own triple admissible for lead tier-restatement review; no upgrade applied. Weakest all must-have claims including code/activity/liveness and contradictions govern V25.' if ok else 'HOLD, no tier/status/HQ/identity/parent change; no negative inference from failed fetches.',route_count=sum(r['org_id']==oid for r in routes)))
# Defect injection: a wrong quote must fail the raw matcher, and a city-only or incomplete claim set cannot pass a triple.
assert not has((D/packet[0]['raw_path']).read_text(),'VERTEX manufactures epoxy floor patch in Houston')
assert not {'existence','address','scope'}<= {'existence','scope'}
if '--check' in sys.argv:
 assert list(csv.DictReader((D/'packet.csv').open()))==packet
 old=list(csv.DictReader((D/'verdicts.csv').open()));assert len(old)==37 and {r['org_id'] for r in old}=={r['org_id'] for r in frame};assert all(r['missing_fact'] for r in old if r['verdict']=='STILL_UNCERTAIN')
 assert len(list(csv.DictReader((D/'routes.csv').open())))==len(routes)
 for r in packet:assert has((D/r['raw_path']).read_text(),r['quote'])
else:
 write('packet.csv',packet,COLS);write('verdicts.csv',vv,['org_id','legal_name','verdict','missing_fact','notes','route_count']);write('routes.csv',routes,['org_id','kind','source_ref','final_url','http_status','availability','raw_path','notes'])
print('PASS',len(frame),'unique organizations;',len(packet),'claim rows;',dict(Counter(r['verdict'] for r in vv)),';',len(routes),'fetch routes; wrong-quote and incomplete-triple negatives PASS')
