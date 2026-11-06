"""Resolve only literal held operator/address/code matches; record competing filed codes."""
import csv,json,re,sys
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from atlas import name_key,street_key
from prep import read,write

def main():
 ita={r['establishment_id']:r for r in read(ROOT/'tasks/osha-ita-2026-11-01/establishments.csv')};osha={r['est_key']:r for r in read(ROOT/'tasks/osha-spine-2026-11-01/establishments.csv')};out=[]
 for s in read(H/'input.csv'):
  aliases={name_key(s['org_legal_name']),*(name_key(t) for t in s['org_trade_names'].split(';') if t)};candidates=[]
  for kind,fid in re.findall(r'(ITA|OSHA):([^;]+)',s['sources_with_ids']):
   f=(ita if kind=='ITA' else osha)[fid]
   if kind=='ITA': r=dict(kind=kind,key=fid,name=f['company_name'],street=f['street'],city=f['city'],state=f['state'],zip=f['zip5'],code=f['naics_code'],date=f['date_submitted'][:10],url='https://www.osha.gov/sites/default/largefiles/ITA_300A_Summary_Data_2025_through_08-31-2026.csv#establishment_ID='+fid)
   else:r=dict(kind=kind,key=fid,name=f['name'],street=f['street'],city=f['city'],state=f['state'],zip=f['zip'],code=f['naics_latest'],date=f['latest_inspection'][:10],url='https://www.osha.gov/ords/imis/establishment.inspection_detail?id='+f['latest_activity_nr'])
   r['physical_street']=re.sub(r'^PO\s+Box\s+\d+\s+', '',r['street'],flags=re.I)
   candidates.append(r)
  exact=[f for f in candidates if name_key(f['name']) in aliases and f['state']==s['state'] and f['zip']==s['zip'] and street_key(f['physical_street'])==street_key(s['street_address']) and f['code']==s['naics_primary']]
  same_street=[f for f in candidates if street_key(f['physical_street'])==street_key(s['street_address']) and f['state']==s['state']]
  conflicts=[f for f in same_street if f['code'] and f['code']!=s['naics_primary']]
  chosen=next((f for f in exact if f['kind']=='ITA'),exact[0] if exact else None)
  # A newer conflicting code is held; selecting an older matching inspection would hide it.
  newer=[f for f in conflicts if chosen and f['date']>=chosen['date']]
  reason=('newer competing filed NAICS: '+json.dumps(newer)) if newer else ('literal held operator/street/state/ZIP/primary-code match' if chosen else 'settle operator/address/primary-code binding against held fields; '+json.dumps(candidates))
  out.append(dict(site_id=s['site_id'],admissible='yes' if chosen and not newer else 'no',chosen=json.dumps(chosen) if chosen and not newer else '',reason=reason,candidates=json.dumps(candidates)))
 write(H/'federal_review.csv',out,list(out[0]));print(sum(r['admissible']=='yes' for r in out),'/',len(out),'literal federal sets admitted')
if __name__=='__main__':main()
