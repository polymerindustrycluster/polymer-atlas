#!/usr/bin/env python3
"""Deterministic ID-free derivative of frozen blind observations; stdlib only."""
import csv, datetime, hashlib, json, re
from pathlib import Path
from collections import Counter, defaultdict
ROOT=Path(__file__).resolve().parent
DATE='2026-10-30'
HEAD=['evidence_id','record_table','record_id','claim_type','claim_detail','source_class','source_ref','observed_date','tier_effect','created_by','notes']
CERT={
'https://www.arlon.com/assets/docs/Arlon_ISO_9001_2015_Certificate_65804_Effective_02052024.pdf',
'https://durableproductsinc.com/wp-content/uploads/2025/11/IATF16949-10000432-DP-LLC.pdf',
'https://www.armacell.com/sites/default/files/2025/01/17/0152984_ENG_Armacell%20LLC.pdf',
'https://www.renolit.com/fileadmin/renolit/corporate/Certificates/American_RENOLIT_Corporation_La_Porte/Certificate_US019775________Item_1-9C3INIF.pdf',
'https://bakelite.com/wp-content/uploads/2024/12/ISO-9001-Certificate_06-09-2027EN-Louisville-KY.pdf',
'https://ac-catalysts.com/DOCS/NEWS/0223117_LLC_14001.pdf',
'https://www.resinlab.com/wp-content/uploads/2018/06/ResinLab-ISO-Certification.pdf',
'https://assets.danfoss.com/approvals/latest/582477/ID488137032413-0501.pdf',
'https://assets.danfoss.com/approvals/latest/517571/ID531143369300-0101.pdf',
'https://www.syensqo.com/sites/g/files/alwlxe161/files/2026-02/Syensqo%20Specialty%20Polymers_Global_ISO%209001_EXP%2008-Jan-2028.pdf'}
HOLDS={
('SITE-005513','alternate_company_address'):'Different establishment; cannot evidence sampled plant identity/address.',
('SITE-005510','polymer_product'):'Company-wide product construction does not establish sampled plant material/process.',
('SITE-005843','relocation_plan'):'Conditional relocation is not a dated closure/liveness outcome; retain in blind review.',
('SITE-005843','current_company_manufacturing_location;current_company_name'):'Different city/establishment; do not attach as sampled-site address or liveness.',
('SITE-005618','organization_scope'):'Group scope cannot establish sampled establishment activity.',
('SITE-005618','other_address'):'Other establishment address, not sampled establishment.',
('SITE-005305','product_context'):'Group-wide products do not establish sampled establishment manufacture.',
('SITE-005582','products'):'Group product family not a plant-specific manufacturing witness.',
('ORG-004378','processes'):'Researcher classification proposal, not source-stated vocabulary.'}
ADDRESS={'city','state','zip','county','site','city_state_zip','alternate_zip','zip_corroboration','hq_city','hq_state','hq_zip','current_company_manufacturing_location','manufacturing_locations','manufacturing_location'}
IDENTITY={'legal_name','name','published_name','site_name','website','organization_name','legal_name_as_filed','name_as_filed','current_location_name','current_company_name','site_identity','brands','current_operator_brand'}
PARENT={'operator','operator_name','operator_group','parent_name','ultimate_parent_name','parent_brand_relationship','parent_relationship','parent_history','ownership_event','group_identity','identity_event','operator_history'}
LIVE={'status','operating_status','operating_observation','current_activity','current_site_listing','current_presence','operating_presence','activity_status','manufacturing_recruitment'}
def classify(field):
 if field in ADDRESS or 'address' in field:return 'address'
 if field in IDENTITY:return 'existence'
 if field in PARENT:return 'parent'
 if 'naics' in field or field=='sic':return 'code'
 if field in LIVE:return 'liveness'
 if field.startswith('polymer_scope') or field=='polymer_relevance':return 'scope'
 if any(w in field for w in ['activity','process','material','product']) or field in {'facility_history','facility_start_year','employee_band_site','historic_process','historical_scope'}:return 'activity'
 raise ValueError('Unmapped field '+field)
def parts(o):
 f=o['field'];v=str(o['value']); fs=f.split(';');vs=v.split(';')
 if len(fs)>1 and len(fs)==len(vs):return list(zip(fs,vs))
 if f in {'operator_address','operator_address_county','operator_county','name_address','name_hq','historical_name_address','identity_ownership'}:
  if f=='identity_ownership':return [('legal_name',vs[0]),('parent_relationship',';'.join(vs[1:]))]
  first='operator_name' if f.startswith('operator') else 'name'
  return [(first,vs[0]),('county' if f=='operator_county' else 'address',';'.join(vs[1:]))]
 return [(a,v) for a in fs]
def main():
 identities={r['record_id']:r['table'] for r in json.loads((ROOT/'identity_only.json').read_text())}
 groups={}; changes=[]; excluded=[]; hashes={}; urls=set(); n=0; used=set()
 for path in sorted((ROOT/'blind').glob('*.json')):
  raw=path.read_bytes();hashes[path.name]=hashlib.sha256(raw).hexdigest()
  for r in json.loads(raw)['records']:
   rid=r['record_id']
   for i,o in enumerate(r['observations']):
    n+=1; ref=f'{path.name}:{rid}:observations[{i}]';url=o['source_url'];urls.add(url);f=o['field'];v=str(o['value'])
    why=HOLDS.get((rid,f))
    if o.get('claim_type') in {'researcher_inferred','research_observation'} or f in {'ring','ring_recommendation','contact_page_result'}:why='Researcher inference or fetch observation, not independently witnessed fact.'
    if 'candidate' in f:why='Potential relationship lacks settled factual linkage.'
    if f in {'certification','site_certification_claim','employee_band_site'} or (f=='status' and ('certif' in v.lower() or 'qualification' in v.lower())):why='Certification/qualification/legal standing is not itself operating activity; no suitable primary-activity claim asserted.'
    if f=='employee_band_site':why='Headcount is a Nice-field observation, not a witnessed primary activity; retained in frozen observations.'
    if why:excluded.append({'observation':ref,'field':f,'source_url':url,'reason':why});continue
    sc=o['source_class']; orig=sc
    if url in CERT:sc='registry'
    elif sc=='government':sc='government_filing'
    elif sc in {'primary_manufacturer_document_hosted_by_third_party','company_document_third_party_host'}:sc='own_site'
    elif sc=='commercial_reseller':sc='directory'
    assert sc in {'own_site','government_filing','registry','directory','press','platform_category','harvest_roster'},sc
    sd=o.get('source_date',''); od=sd if re.fullmatch(r'\d{4}-\d{2}-\d{2}',sd) else DATE
    # Explicitly dated inspection plus case-close date: inspection date is force date, not closure date.
    if sd.startswith('2023-07-27; case closed'):od='2023-07-27'
    datetime.date.fromisoformat(od)
    emitted=[]
    for field,value in parts(o):
     if field=='naics_primary_source_type':continue # provenance travels with code observation, not a second code fact
     ct=classify(field)
     if rid in {'SITE-005406','ORG-004202'} and ct=='scope':ct='activity'
     effect='supports_B' # deliberately conservative claim strength; never a full-record tier
     if sc in {'registry','directory'} and ct=='address':effect='supports_C'
     if orig=='commercial_reseller' or sc=='platform_category':effect='supports_C'
     if sc=='platform_category' and ct=='scope':raise ValueError('Platform scope cannot support')
     key=(rid,ct,url,od,sc,effect)
     if key not in groups:groups[key]={'details':[],'notes':[],'refs':[]}
     g=groups[key]; detail=field+' = '+value
     if detail not in g['details']:g['details'].append(detail)
     note='Witness: '+o['source_name']+'. Retrieved '+o.get('accessed_date',DATE)+'.'
     if sd:note+=' Frozen source date: '+sd+'.'
     if sd and od==DATE and sd not in {'undated',DATE}:note+=' Source-date precision incomplete; retrieval date does not redate historical facts.'
     if o.get('summary'):note+=' '+o['summary']
     if o.get('source_note'):note+=' '+o['source_note']
     if url in CERT:note+=' Third-party certificate authorship; registry ceiling; identifier/validity retained in cited certificate, no independent live registry lookup in this derivative.'
     if orig=='commercial_reseller':note+=' Reseller statement only, conservative directory/C; not primary operator evidence.'
     if note not in g['notes']:g['notes'].append(note)
     if ref not in g['refs']:g['refs'].append(ref)
     emitted.append({'field':field,'claim_type':ct,'source_class':sc,'observed_date':od,'tier_effect':effect});used.add(ref)
    changes.append({'observation':ref,'original_field':f,'original_claim_type':o.get('claim_type'),'original_source_class':orig,'original_source_date':sd,'normalized':emitted})
 rows=[]
 for (rid,ct,url,od,sc,eff),g in sorted(groups.items()):
  rows.append(dict(zip(HEAD,['',identities[rid],rid,ct,'; '.join(g['details']),sc,url,od,eff,'F1 audit 8 independent-observation draft',' '.join(g['notes'])+' Observation provenance: '+', '.join(g['refs'])+'. Draft only; claim-local observation, not full-record verification or proposed automatic tier/status change.'])))
 assert n==321 and len(urls)==137,(n,len(urls))
 assert len(used)+len(excluded)==n
 for row in rows:
  assert row['source_ref'] in urls and row['evidence_id']==''
  assert row['claim_type'] in {'existence','activity','scope','address','parent','liveness','code'}
  assert not(row['source_class'] in {'registry','directory'} and row['claim_type']=='address' and row['tier_effect']!='supports_C')
 with (ROOT/'evidence_drafts.csv').open('w',newline='') as out:
  w=csv.DictWriter(out,fieldnames=HEAD);w.writeheader();w.writerows(rows)
 log={'method_version':1,'input_sha256':hashes,'input_observations':n,'input_unique_urls':len(urls),'included_observations':len(used),'excluded_observations_count':len(excluded),'draft_rows':len(rows),'draft_unique_urls':len({r['source_ref'] for r in rows}),'draft_records':len({r['record_id'] for r in rows}),'counts_by_claim':dict(sorted(Counter(r['claim_type'] for r in rows).items())),'counts_by_class':dict(sorted(Counter(r['source_class'] for r in rows).items())),'counts_by_effect':dict(sorted(Counter(r['tier_effect'] for r in rows).items())),'normalizations':changes,'excluded_observations':excluded}
 (ROOT/'evidence_normalization_log.json').write_text(json.dumps(log,indent=2)+'\n')
 print(json.dumps({k:v for k,v in log.items() if k not in {'normalizations','excluded_observations','input_sha256'}},indent=2))
if __name__=='__main__':main()
