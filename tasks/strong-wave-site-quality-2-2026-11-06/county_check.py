"""Read official Census county geography for matched business addresses; never use coordinates for tiers."""
import concurrent.futures,csv,hashlib,json,subprocess,sys
from pathlib import Path
from urllib.parse import urlencode
H=Path(__file__).resolve().parent;ROOT=H.parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from atlas import street_key
from prep import read
R1=ROOT/'tasks/strong-wave-site-quality-2026-11-06'
CACHE=Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/strong-wave-site-quality-2/county');CACHE.mkdir(parents=True,exist_ok=True)
def one(s):
 q=urlencode(dict(street=s['street_address'],city=s['city'],state=s['state'],zip=s['zip'],benchmark='Public_AR_Current',vintage='Current_Current',layers='Counties',format='json'))
 u='https://geocoding.geo.census.gov/geocoder/geographies/address?'+q;p=CACHE/(s['site_id']+'.json')
 cp=subprocess.run(['curl','-fsS','-A','Mozilla/5.0 (Atlas county verification)','--max-time','35',u,'-o',str(p)],capture_output=True,text=True)
 if cp.returncode:return dict(site_id=s['site_id'],status='UNAVAILABLE',source_url=u,reason=cp.stderr[:200])
 body=json.loads(p.read_text());ms=body['result']['addressMatches'];good=[]
 for m in ms:
  geo=m.get('geographies',{}).get('Counties',[])
  if len(geo)==1 and geo[0]['NAME'].removesuffix(' County').lower()==s['county'].lower():good.append((m,geo[0]))
 if len(good)!=1:return dict(site_id=s['site_id'],status='HOLD',source_url=u,reason='County/address match absent or ambiguous')
 m,g=good[0];matched_street=m['matchedAddress'].split(',',1)[0]  # Census fromAddress is a street-range endpoint, not the matched house number.
 if street_key(matched_street)!=street_key(s['street_address']):return dict(site_id=s['site_id'],status='HOLD',source_url=u,reason='Matched physical street differs: '+m['matchedAddress'])
 return dict(site_id=s['site_id'],status='PASS',source_url=u,county=g['NAME'],geoid=g['GEOID'],matched_address=m['matchedAddress'],raw_file=str(p),raw_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),observed_date='2026-11-06',reason='Address-exact county geography, no coordinates used')
if __name__=='__main__':
 # Known answers: round 1's three county/address cases (merged in #237) must reproduce before any new candidate is admitted.
 r1={r['site_id']:r for r in read(R1/'input.csv')};r1rec={r['site_id']:r for r in json.loads((R1/'county_receipts.json').read_text())}
 known=[one(r1[s]) for s in ['SITE-011028','SITE-011011','SITE-011151']]
 assert all(k['status']=='PASS' and k['county']==r1rec[k['site_id']]['county'] and k['geoid']==r1rec[k['site_id']]['geoid'] and k['matched_address']==r1rec[k['site_id']]['matched_address'] for k in known),'Known county lookup failed; do not trust candidate matching'
 (H/'county_calibration.json').write_text(json.dumps(known,indent=2)+'\n');print('known county/address answers reproduce round 1',flush=True)
 inputs={r['site_id']:r for r in read(H/'input.csv')}
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rs=list(pool.map(one,[inputs[r['site_id']] for r in read(H/'selected.csv')]))
 (H/'county_receipts.json').write_text(json.dumps(rs,indent=2)+'\n');print([(r['site_id'],r['status'],r.get('county') or r['reason']) for r in rs],flush=True)
