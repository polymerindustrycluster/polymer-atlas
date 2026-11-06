"""Bounded public route probes; store status/hashes only, not raw page/contact contents."""
import csv,hashlib,subprocess,tempfile,concurrent.futures
from pathlib import Path
HERE=Path(__file__).parent
ROUTES=[
 ('apr','terms','https://plasticsrecycling.org/wp-content/uploads/2024/08/APR-Terms-of-Use-8-16-2024.pdf'),
 ('vinyl-institute','terms','https://www.vinylinfo.org/terms-and-conditions/'),
 ('acma','directory_page','https://acmanet.org/membership/why-membership-matters/membership-directory/'),
 ('acma','public_list_api','https://acmanet.org/wp-json/mg/v1/content/directory?type=&state='),
 ('acma','terms','https://acmanet.org/tcs/'),
 ('epa-cdr','access','https://www.epa.gov/chemical-data-reporting/access-chemical-data-reporting-data'),
 ('epa-cdr','license','https://edg.epa.gov/data/EPA_Data_License.html'),
 ('sam-gov','terms','https://sam.gov/about/terms-of-use'),
 ('sam-gov','anonymous_public_extract','https://api.sam.gov/data-services/v1/extracts?fileType=ENTITY&sensitivity=PUBLIC'),
]
def main():
 with tempfile.TemporaryDirectory() as d:
  def probe(pair):
   i,(source,route,url)=pair;p=Path(d)/str(i)
   c=subprocess.run(['curl','-LsS','--max-time','45','-A',('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36' if source=='vinyl-institute' else 'Mozilla/5.0'),url,'-o',str(p),'-w','%{http_code}'],capture_output=True,text=True)
   b=p.read_bytes() if p.exists() else b''
   return dict(source=source,route=route,url=url,observed_date='2026-11-06',http_status=c.stdout,fetch_rc=c.returncode,bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
  with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:out=list(pool.map(probe,enumerate(ROUTES)))
  with (HERE/'routes.csv').open('w') as f:
   w=csv.DictWriter(f,fieldnames=list(out[0]),lineterminator='\n');w.writeheader();w.writerows(out)
 for r in out:print(r['source'],r['route'],r['http_status'],r['bytes'])
if __name__=='__main__':main()
