import json,hashlib
from research import BASE,CACHE
pairs=json.loads((BASE/'input.json').read_text());receipts=[json.loads(p.read_text()) for p in sorted(CACHE.glob('*.json'))]
def evidence(pair,url,quote,source_class,source_date='',date_basis='',claim='',endpoints=None):
 rc=next(x for x in receipts if x['pair_id']==pair and x['url']==url)
 return dict(source_url=url,source_class=source_class,quote=quote,source_date=source_date,date_basis=date_basis,observed_date='2026-11-06',claim=claim,endpoint_ids=endpoints or [],raw_sha256=rc['raw_sha256'])
D01='https://ir.cooperstandard.com/2018-07-03-Cooper-Standard-Agrees-to-Acquire-Lauren-Manufacturing-and-Lauren-Plastics-to-Accelerate-Growth-in-Key-Industrial-Markets'
D02='https://dam.assets.ohio.gov/image/upload/epa.ohio.gov/Portals/27/sip/Nonattain/D1-nonEGU_point_source_inv.pdf'
D03='https://roppe.com/wp-content/uploads/2018/10/Roppe-Press-Release_New-Facility_2018-10-23.pdf'
EPD='https://roppe.com/wp-content/uploads/2024/12/SCS-EPD-RFCI_LVT-Gluedown.pdf'
D04='https://fs2.magicalir.net/tdnet/2026/5108/20260227571355.pdf'
ADMIN='https://www.bridgestoneamericas.com/content/bscorpcomm-sites/americas/en/contact-us/locations/administrative-offices.html'
D05='https://dam.assets.ohio.gov/image/upload/epa.ohio.gov/PUBLIC/DSW/INDUS.pdf'
result=[]
for p in pairs:
 key=p['pair_id'];ids=[p['a_id'],p['b_id']]
 r=dict(pair_id=key,record_table=p['record_table'],a_id=ids[0],b_id=ids[1],verdict='STILL_UNCERTAIN',decision='LINK_FLAG',duplicate_of='',legal_names=[x.get('legal_name') or x.get('site_name') for x in p['records']],observed_date='2026-11-06',evidence=[],settling_fact='',recommendation='',reason='')
 if key=='D01':
  r['evidence']=[evidence(key,D01,"announced its agreement to acquire Lauren Manufacturing and Lauren Plastics, subject to regulatory approvals and related parties' consent.",'own_site','2018-07-03','release date; agreement, not closing','Cooper Standard announced acquisition agreement; does not establish same legal entity or exact plant identity.',ids)]
  r['reason']='Dated release concerns acquisition agreement and four facilities, including two in New Philadelphia. It does not identify 2228 Reiser or establish same legal operator for both site records. Known own site and two certificate URLs failed/returned not found. Existing banked duplicate note is not primary proof; closed status cannot be read as physical closure.'
  r['settling_fact']='Dated primary certificate/filing explicitly tying both site representations to the same legal operator and the same 2228 Reiser Avenue SE establishment, plus a permitted duplicate-tombstone correction procedure.'
  r['recommendation']='Keep both IDs; flag prior closed tombstone as an unproven duplicate designation, not evidence of physical plant closure. No merge, rekey, status correction or parent-org identity inference from this packet.'
 elif key=='D02':
  r['evidence']=[evidence(key,D02,'Iten Industries Inc. (Plant 3) || 1303 West 38th Street, Ashtabula, OH 44004','government_filing','','Source header: 2008 Base Year Emissions Inventory; period year only, no full date asserted.','Historic Iten plant identity/address; no TDM LLC legal relationship established.',['ORG-000386'])]
  r['reason']='Historical Ohio inventory names Iten at 1303 West 38th. Own Iten page inspected. TDM/TRI route and possible own-domain discovery route failed. Banked 2022–2024 TDM Form 5500 sponsor note remains context; it was not independently source-verified here. Same address across periods does not establish same legal entity or concurrent operator.'
  r['settling_fact']='Source-system verified TDM LLC sponsor/entity record and a dated primary acquisition, legal-name-change or operating-company instrument explicitly resolving TDM versus Iten at 1303 West 38th, with effective dates.'
  r['recommendation']='Retain organizations and facility links unchanged; flag possible historical operator/asset succession as hypothesis only. Do not merge from address or sponsor-note overlap.'
 elif key=='D03':
  r.update(verdict='VERIFIED',decision='DISTINCT')
  r['evidence']=[evidence(key,D03,'Roppe Holding Company (RHC), the parent company to commercial flooring leaders Roppe and Flexco','own_site','2018-10-23','release date','Holding-company versus operating-business distinction.',ids),evidence(key,EPD,'Roppe Corporation is a wholly owned division of Roppe Holding Company','own_site','2024-05-09','EPD SCS-EPD-10146 validity start; valid through 2029-05-08','Exact Corporation name separately identified from holding company.',ids)]
  r['reason']='Dated own-issued release and own-hosted dated EPD identify parent/operating business separately. A wholly owned division description is not a same-legal-entity finding. Existing held parent pointer is context only.'
  r['recommendation']='No merge. Retain parent/operator separation. Parent may use these sources to corroborate existing relationship under its own schema/relationship gate; do not infer member identity or transfer facility TRI links.'
 elif key=='D04':
  r.update(verdict='VERIFIED',decision='DISTINCT')
  r['evidence']=[evidence(key,D04,'Bridgestone Americas, Inc. || Management of Americas operations || Firestone Polymers, LLC || Manufacture and sale of synthetic rubber','own_site','2025-12-31','FY2025 business report period end (Jan 1 through Dec 31 2025), published 2026; translated report p37–38','Separate named companies in corporate group report.',ids),evidence(key,ADMIN,'Firestone Polymers Corporate Headquarters A subsidiary of Bridgestone Americas, Inc.','own_site','','Live own administrative-offices page is undated; retrieval is not publication date.','Explicit subsidiary context corroborates dated group company distinction.',ids)]
  r['reason']='Dated group report lists Bridgestone Americas Inc and Firestone Polymers LLC as separate companies; own admin page explicitly describes subsidiary relationship. Shared held TRI ID cannot collapse parent and operator. TRI ownership/link allocation at 381 W Wilbeth was not source-system resolved.'
  r['recommendation']='No organization merge. Retain all registry links for integrator review; require current source-system TRI record showing facility operator versus parent before any link rekey/removal.'
 else:
  r['evidence']=[evidence(key,D05,'EXTERIOR PORTFOLIO LLC-NORTH PLANT || 1550 UNIVERSAL RD || 9/11/2025 || EXTERIOR PORTFOLIO LLC - SOUTH PLANT || 1441 UNIVERSAL RD || 9/4/2025','government_filing','2025-09-11','North permit issue 2025-09-11; South permit issue 2025-09-04; one public regulator list.','Two separately named and addressed establishments; not a same-legal-entity finding for held organization abstractions.',ids)]
  r['reason']='Ohio regulator lists north plant 1550 Universal and south plant 1441 Universal separately, with Royal applicant names. Shared held TRI assignment is a lead only: both TRI source-system fetches failed. One held organization models north plant, another spans broader Royal business; legal-entity equivalence remains unsettled.'
  r['settling_fact']='Source-system TRI records for 43207VNYLM1441U and 43207CRNPR1550U plus dated exact operator legal identities and a determination of whether both held organization records represent that same legal entity, rather than distinct facilities or group scope.'
  r['recommendation']='No merge/rekey/removal. Preserve both plants and organization records; flag shared TRI assignment for explicit source-system operator/parent adjudication. Separate establishments alone do not prove distinct organizations.'
 r['primary_fetch_count_by_org']={oid:sum(oid in x['org_ids'] for x in receipts) for oid in {x['org_id'] for x in p['organizations']}}
 result.append(r)
(BASE/'verdicts.json').write_text(json.dumps(result,indent=2)+'\n')
(BASE/'receipts.json').write_text(json.dumps({'observed_date':'2026-11-06','baseline':'542629e','input_sha256':hashlib.sha256((BASE/'input.json').read_bytes()).hexdigest(),'fetches':receipts},indent=2)+'\n')
print('5 pairs; 2 VERIFIED/DISTINCT, 3 STILL_UNCERTAIN/LINK_FLAG; no duplicate or merge proposals;',len(receipts),'fetches')
