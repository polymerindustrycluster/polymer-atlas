"""Re-probe the route URLs and re-check the terms quotes RAW (words in order, house normaliser = lowercase alphanumeric tokens).
Writes routes.csv (status/size/hash metadata) and terms_checks.csv. Non-200 is a recorded route observation, never an empty dataset.
Usage: python3 -I fetch_routes.py [--write]"""
import csv,hashlib,re,subprocess,sys,html,datetime
from pathlib import Path
HERE=Path(__file__).resolve().parent
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
WB='https://web.archive.org/web/2026/'
ROUTES=[ # (source, role, url, how)  how: get = fetch body, head = HEAD only (large file)
 ('fda','terms+landing','https://www.fda.gov/medical-devices/device-registration-and-listing/establishment-registration-and-medical-device-listing-files-download','get'),
 ('fda','bulk','https://www.accessdata.fda.gov/premarket/ftparea/registration_listing.zip','head'),
 ('fda','bulk','https://www.accessdata.fda.gov/premarket/ftparea/Listing_PCD.zip','head'),
 ('fda','bulk','https://www.accessdata.fda.gov/premarket/ftparea/foiclass.zip','head'),
 ('fied','bulk','https://data.openei.org/files/6158/foundational_industry_data_2017.csv','head'),
 ('fied','landing','https://data.openei.org/submissions/6158','get'),
 ('nei','landing','https://www.epa.gov/air-emissions-inventories/2020-national-emissions-inventory-nei-data','get'),
 ('nei','landing-2023','https://www.epa.gov/air-emissions-inventories/2023-national-emissions-inventory-nei-data','get'),
 ('nei','bulk','https://gaftp.epa.gov/air/nei/nei_facility_summaries/2020_nei_facility_summary.zip','head'),
 ('nei','bulk','https://gaftp.epa.gov/air/nei/2020/data_summaries/2020nei_facility_process_byregions.zip','head'),
 ('ftz','legacy-T/IM','http://ita-web.ita.doc.gov/ia/FTZManufac.nsf','get'),
 ('ftz','ofis-landing','https://ofis.trade.gov/','get'),
 ('ftz','ofis-production-db','https://ofis.trade.gov/ManufacturingDB','get'),
 ('dol','host-direct','https://www.dol.gov/sites/dolgov/files/ETA/oflc/pdfs/LCA_Disclosure_Data_FY2025_Q4.xlsx','head'),
 ('dol','host-landing','https://www.dol.gov/agencies/eta/foreign-labor/performance','get'),
 ('dol','wayback-landing',WB+'https://www.dol.gov/agencies/eta/foreign-labor/performance','get'),
 ('usaspending','api','https://api.usaspending.gov/api/v2/references/naics/?filter=3252','get'),
]
TERMS=[ # (source, url, quote)
 ('fda','https://www.fda.gov/about-fda/about-website/website-policies','They are in the public domain and may be republished, reprinted and otherwise used freely by anyone without the need to obtain permission from FDA'),
 ('fied','https://data.openei.org/submissions/6158','Content is available under Creative Commons Attribution 4.0 unless otherwise noted'),
 ('nei','https://edg.epa.gov/data/EPA_Data_License.html','all data produced by the U.S EPA is by default in the public domain'),
 ('ftz','https://catalog.data.gov/search?q=foreign-trade','http://www.usa.gov/publicdomain/label/1.0/'),
 ('dol',WB+'https://www.dol.gov/general/aboutdol/copyright','Materials created by the federal government are generally part of the public domain and may be used, reproduced and distributed without permission'),
 ('usaspending','https://raw.githubusercontent.com/fedspendingtransparency/usaspending-api/master/LICENSE','CC0 1.0 Universal'),
]
def curl(url,head=False):
 cmd=['curl','-sL','-m','90','-A',UA,'-o','-' if not head else '/dev/null','-w','\n%{http_code}|%{size_download}|%header{content-length}|%{content_type}']
 if head:cmd.insert(1,'-I')
 p=subprocess.run(cmd+[url],capture_output=True);body,_,tail=p.stdout.rpartition(b'\n');f=tail.decode('latin-1').split('|')+['','','']
 return int(f[0] or 0),(f[2].strip() if f[2].strip() not in('','-1') else f[1]),f[3],body
def words(s):return re.findall(r'[a-z0-9]+',html.unescape(re.sub(r'<script.*?</script>|<style.*?</style>|<[^>]+>',' ',s,flags=re.S)).lower())
def in_order(quote,text):
 q=words(quote);t=words(text);n=len(q)
 return any(t[i:i+n]==q for i in range(len(t)-n+1))
def main():
 routes=[];today=datetime.date.today().isoformat()
 for s,role,u,how in ROUTES:
  code,size,ctype,body=curl(u,head=(how=='head'))
  routes.append(dict(source=s,role=role,url=u,method='HEAD' if how=='head' else 'GET',http_status=code,bytes=size,content_type=ctype.split(';')[0],sha256=hashlib.sha256(body).hexdigest() if how=='get' and body else '',observed=today));print(s,role,code,size,flush=True)
 terms=[]
 for s,u,q in TERMS:
  code,_,_,body=curl(u);terms.append(dict(source=s,url=u,http_status=code,quote=q,raw_words_in_order='PASS' if in_order(q,body.decode('utf-8','replace')) else 'FAIL',observed=today));print(s,'terms',code,terms[-1]['raw_words_in_order'],flush=True)
 if '--write' in sys.argv:
  for name,rows in (('routes.csv',routes),('terms_checks.csv',terms)):
   with open(HERE/name,'w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
if __name__=='__main__':main()
