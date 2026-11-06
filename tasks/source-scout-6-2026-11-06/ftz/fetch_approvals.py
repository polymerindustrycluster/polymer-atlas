"""ITA OFIS FTZ Production Database: approvals whose parts fall under HTSUS headings 3901-3926 and 4001-4017.
The public page calls ?handler=LoadPartsByHTSUS (JSON) with an antiforgery cookie+header. One request/second.
Usage: python3 -I fetch_approvals.py OUTDIR   (OUTDIR is under the persist dir, never in the repo)"""
import http.cookiejar,json,re,sys,time,urllib.request
from pathlib import Path
BASE='https://ofis.trade.gov/ManufacturingDB/DetailHTSUS'
HEADINGS=[f'39{i:02d}' for i in range(1,27)]+[f'40{i:02d}' for i in range(1,18)]
def main(out):
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 jar=http.cookiejar.CookieJar();op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar));op.addheaders=[('User-Agent','polymer-atlas-source-scout-6')]
 for h in HEADINGS:
  dest=out/f'approvals_{h}.json'
  if dest.exists():continue
  page=op.open(f'{BASE}?htsus={h}&partType=Product',timeout=90).read().decode()
  tok=re.search(r'name="__RequestVerificationToken" type="hidden" value="([^"]+)"',page).group(1)
  req=urllib.request.Request(f'{BASE}?htsus={h}&partType=Product&handler=LoadPartsByHTSUS',json.dumps({'htsus':h,'parttype':'Product'}).encode(),
   {'RequestVerificationToken':tok,'Content-Type':'application/json','Referer':f'{BASE}?htsus={h}&partType=Product'})
  body=op.open(req,timeout=120).read();json.loads(body)['data'];dest.write_bytes(body);print(h,len(body));time.sleep(1)
if __name__=='__main__':main(sys.argv[1])
