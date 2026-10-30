"""Offline conservative Census response interpretation; no writes to data/."""
import csv,json,re,pathlib,collections,hashlib,unicodedata
OUT=pathlib.Path(__file__).parent
SUFFIX={'STREET':'ST','ROAD':'RD','AVENUE':'AVE','BOULEVARD':'BLVD','DRIVE':'DR','LANE':'LN','COURT':'CT','HIGHWAY':'HWY','PARKWAY':'PKWY','PLACE':'PL','CIRCLE':'CIR','TERRACE':'TER','EXPRESSWAY':'EXPY','TRAIL':'TRL','NORTH':'N','SOUTH':'S','EAST':'E','WEST':'W','NORTHEAST':'NE','NORTHWEST':'NW','SOUTHEAST':'SE','SOUTHWEST':'SW','ONE':'1'}
def norm(x): return ' '.join(SUFFIX.get(t,t) for t in re.sub(r'[^A-Z0-9 ]',' ',x.upper()).split())
def compare(r,matched):
 a=[s.strip() for s in matched.split(',')]
 if len(a)!=4:return 'unparseable_matched_address'
 failures=[]
 for name,original,new in [('street',r['street_address'],a[0]),('city',r['city'],a[1]),('state',r['state'],a[2])]:
  if original and norm(original)!=norm(new):failures.append(name+'_mismatch')
 if r['zip'] and r['zip'][:5]!=a[3][:5]: failures.append('zip_mismatch')
 return ';'.join(failures)
def county_norm(x):
 x=unicodedata.normalize('NFKD',x).encode('ascii','ignore').decode().upper().replace('INDEPENDENT CITY','CITY')
 x=re.sub(r'[.()]','',x)
 return re.sub(r' (COUNTY|PARISH|BOROUGH|MUNICIPIO|CENSUS AREA)$','',x.strip())
def main():
 pop=list(csv.DictReader(open(OUT/'population.csv')));req=list(csv.reader(open(OUT/'request.csv')));raw=list(csv.reader(open(OUT/'response.csv')))
 assert len(raw)==len(req) and {r[0] for r in raw}=={r[0] for r in req} and len({r[0] for r in raw})==len(raw)
 results={r[0]:r for r in raw}
 county={(r['STATEFP'],r['COUNTYFP']):r['COUNTYNAME'] for r in csv.DictReader(open(OUT/'county-codes-2020.txt'),delimiter='|')}
 packet=[]
 for r in pop:
  p={k:r[k] for k in ('site_id','cohort','creation_pass','row_sha256')};p.update(lat='',lng='',precision_class='',geocode_source='',retrieved_at='',disposition=r['input_status'],provider_match='',provider_match_type='',matched_address='',address_check='',tiger_line_id='',side='',geocoder_state_fips='',geocoder_county_fips='',geocoder_county_name='',recorded_county=r['county'],county_comparison='NOT_ASSESSED',settling_fact='')
  if r['input_status']!='REQUESTED':
   p['settling_fact']='Existing paired coordinates and source must be reviewed, not replaced' if r['input_status']=='HELD_EXISTING_COORDINATES' else 'A complete physical business street address with structure number'
  else:
   a=results[r['site_id']];p.update(geocode_source='https://geocoding.geo.census.gov/geocoder/geographies/addressbatch',retrieved_at='2026-10-30',provider_match=a[2],provider_match_type=a[3] if len(a)>3 else '')
   if a[2]!='Match':p.update(disposition='HELD_'+re.sub('[^A-Z]+','_',a[2].upper()).strip('_'),settling_fact='A unique address-exact public geocoder result at the recorded physical business address')
   else:
    assert len(a)>=8
    p.update(matched_address=a[4],address_check=compare(r,a[4]),tiger_line_id=a[6],side=a[7])
    if len(a)>=10:
     p.update(geocoder_state_fips=a[8],geocoder_county_fips=a[9],geocoder_county_name=county.get((a[8],a[9]),''))
     if not r['county']: p['county_comparison']='RECORDED_COUNTY_BLANK'
     elif not p['geocoder_county_name']:p['county_comparison']='UNMAPPED_FIPS_REVIEW'
     elif county_norm(r['county'])!=county_norm(p['geocoder_county_name']):p['county_comparison']='CONFLICT_REVIEW_ONLY'
     else:p['county_comparison']='AGREES_REFERENCE_ONLY'
    if a[3]!='Exact':p.update(disposition='HELD_NONEXACT_MATCH',settling_fact='An exact unique address match or manual address-specific resolution')
    elif p['address_check']:p.update(disposition='HELD_ADDRESS_COMPARISON',settling_fact='Resolve '+p['address_check']+' against the recorded physical address; do not silently correct it')
    else:
     lng,lat=a[5].split(',');assert -180<float(lng)<180 and -90<float(lat)<90
     p.update(disposition='REFERENCE_MATCH',lat=lat,lng=lng,precision_class='address_interpolated',address_check='PASS_STRICT_NORMALIZED')
  packet.append(p)
 with open(OUT/'coordinates-packet.csv','w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(packet[0]));w.writeheader();w.writerows(packet)
 summary={'population':len(packet),'dispositions':dict(collections.Counter(r['disposition'] for r in packet)),'county_comparison':dict(collections.Counter(r['county_comparison'] for r in packet)),'provider_match':dict(collections.Counter(r[2] for r in raw)),'provider_match_type':dict(collections.Counter(r[3] for r in raw if len(r)>3)),'cohort_dispositions':{c:dict(collections.Counter(r['disposition'] for r in packet if r['cohort']==c)) for c in sorted({r['cohort'] for r in packet})},'raw_response_sha256':hashlib.sha256((OUT/'response.csv').read_bytes()).hexdigest(),'county_code_source':'https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt','county_code_source_retrieved':'2026-10-30'}
 (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
