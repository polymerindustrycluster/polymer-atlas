"""Resumable Census batch fetch; raw responses are committed witnesses."""
import csv,json,subprocess,time
from pathlib import Path
P=Path(__file__).resolve().parent
R=P.parents[1]
def get(url,path):
 if not path.exists(): subprocess.run(['curl','--fail','--retry','2','--max-time','600','-sS',url,'-o',str(path)],check=True)
if __name__=='__main__':
 rows=[]
 for p in sorted((R/'data').glob('sites_*.csv')):
  if p.name=='sites_INTL.csv': continue
  rows.extend(dict(r,shard=p.name) for r in csv.DictReader(p.open()) if r['street_address'].strip())
 if not (P/'baseline.csv').exists():
  with (P/'baseline.csv').open('w',newline='') as f:
   w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 for name,url in [('benchmarks.json','https://geocoding.geo.census.gov/geocoder/benchmarks?format=json'),('vintages.json','https://geocoding.geo.census.gov/geocoder/vintages?benchmark=4&format=json'),('counties.txt','https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt')]: get(url,P/name)
 for n,start in enumerate(range(0,len(rows),1000)):
  inp=P/f'input_{n}.csv';out=P/f'response_{n}.csv'
  with inp.open('w',newline='') as f: csv.writer(f).writerows([r[k] for k in ('site_id','street_address','city','state','zip')] for r in rows[start:start+1000])
  if out.exists(): continue
  with (P/'fetch.log').open('a') as f: f.write(f'{time.ctime()} start {n}\n')
  subprocess.run(['curl','--fail','--retry','2','--max-time','600','-sS','https://geocoding.geo.census.gov/geocoder/geographies/addressbatch','-F',f'addressFile=@{inp}','-F','benchmark=Public_AR_Current','-F','vintage=Current_Current','-o',str(out)+'.tmp'],check=True)
  Path(str(out)+'.tmp').replace(out)
  with (P/'fetch.log').open('a') as f: f.write(f'{time.ctime()} complete {n}\n')
