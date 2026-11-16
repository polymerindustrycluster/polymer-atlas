"""Apply only blank coordinate fields from exact Census matches."""
import csv,json,sys,math
from pathlib import Path
from collections import Counter
P=Path(__file__).resolve().parent
R=P.parents[1]
sys.path.insert(0,str(R/'scripts'))
from regions import PIC18

def read(p): return list(csv.DictReader(p.open(newline='')))
def write(p,rows,fields):
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
def responses():
 rows=[r for p in sorted(P.glob('response_*.csv')) for r in csv.reader(p.open(newline=''))]
 assert all(len(r)>=3 for r in rows)
 ids=[r[0] for r in rows];assert len(ids)==len(set(ids)), 'duplicate response IDs'
 return {r[0]:r for r in rows}
def changes(b,r):
 if r[2:4]!=['Match','Exact']: return {}
 assert len(r)==12, ('unexpected geography response',r)
 lon,lat=r[5].split(',');assert -180<=float(lon)<=180 and -90<=float(lat)<=90
 return {k:v for k,v in [('latitude',lat),('longitude',lon),('geocode_precision','address_interpolated')] if not b[k].strip()}
def distance(a,b):
 lat1,lon1,lat2,lon2=map(math.radians,[float(a['latitude']),float(a['longitude']),float(b[5].split(',')[1]),float(b[5].split(',')[0])])
 h=math.sin((lat2-lat1)/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2
 return 6371000*2*math.asin(min(1,math.sqrt(h)))
def products(base,res,counties):
 assert len(base)==len({b['site_id'] for b in base})
 assert set(res)=={b['site_id'] for b in base}, 'response coverage'
 props=[];holds=[];mismatches=[]
 for b in base:
  r=res[b['site_id']];c=changes(b,r)
  for k,v in c.items(): props.append(dict(site_id=b['site_id'],field=k,before=b[k],after=v,disposition='applied'))
  if r[2:4]!=['Match','Exact']:
   holds.append(dict(site_id=b['site_id'],result='/'.join(r[2:4]),disposition='held',settling_fact='A unique Exact Census address match or a verified coordinate supplement'))
  else:
   county=counties[(r[8],r[9])].split(',')[0]
   norm=lambda s:s.removesuffix(' County').strip().casefold()
   if norm(county)!=norm(b['county']):
    mismatches.append(dict(site_id=b['site_id'],state=b['state'],recorded_county=b['county'],census_county=county,census_county_fips=r[8]+r[9],pic18=str(b['state']=='OH' and (b['county'] in PIC18 or county.removesuffix(' County') in PIC18)),disposition='held',settling_fact='Site-specific physical-address or parcel adjudication'))
 return props,holds,mismatches
if __name__=='__main__':
 base=read(P/'baseline.csv');res=responses();counties={(r['STATEFP'],r['COUNTYFP']):r['COUNTYNAME'] for r in csv.DictReader((P/'counties.txt').open(),delimiter='|')}
 props,holds,mismatches=products(base,res,counties)
 for name,rows,fields in [('proposals.csv',props,['site_id','field','before','after','disposition']),('holds.csv',holds,['site_id','result','disposition','settling_fact']),('county_mismatches.csv',mismatches,['site_id','state','recorded_county','census_county','census_county_fips','pic18','disposition','settling_fact'])]: write(P/name,rows,fields)
 lookup={b['site_id']:b for b in base}
 for shard in sorted({b['shard'] for b in base}):
  p=R/'data'/shard;rows=read(p);dirty=False
  for r in rows:
   if r['site_id'] not in lookup:continue
   for k,v in changes(lookup[r['site_id']],res[r['site_id']]).items():
    assert r[k] in ('',v), 'concurrent value conflict'
    if r[k]!=v:r[k]=v;dirty=True
  if dirty:write(p,rows,list(rows[0]))
 stats=dict(frame=len(base),results=dict(Counter('/'.join(r[2:4]) for r in res.values())),fields=dict(Counter(p['field'] for p in props)),changed_sites=len({p['site_id'] for p in props}),tiers=dict(Counter(lookup[s]['verification_tier'] for s in {p['site_id'] for p in props})),county_mismatches=len(mismatches),pic18_mismatches=sum(r['pic18']=='True' for r in mismatches),holds=len(holds))
 (P/'summary.json').write_text(json.dumps(stats,indent=2)+'\n');print(stats)
