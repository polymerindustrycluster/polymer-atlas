"""Resume bounded company-route fetches; keep raw pages outside the public tree."""
import concurrent.futures,csv,hashlib,json,subprocess
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin,urlsplit
P=Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/pic18-discovery-leads')
DOMAINS='''glipoolproducts.com malcopro.com cosmaxusa.com turfcaresupply.com royalchemical.com cosmocorp.com horizonsinc.com mcgean.com polarproducts.com sunlessinc.com hilltopenergy.com pioneerworld.com olonricerca.com midwestind.com akronporcelain.com ashtachemicals.com engineeredprofiles.com us-technologymedia.com wraptite.com coventya.com oakwoodlabs.com lukemanufacturing.com mvpplastics.com gebauer.com propackaging.com enpress.com bleachtech.com napc.com vinylprofiles.com hartindustrial.com mdairfoils.com technoform.com towerindustries.com zenexint.com americanmarble.com aqstripping.com quesindustries.com cantonfloors.com extrudex.com meridienne.com apcoat.com imperialmetalsolutions.com itpsinc.com columbiachemical.com kbbioenergy.com murrubber.com srpindustries.com laureninternational.com classiclaminations.com futurecontrols.com murrubber.com technoform.com armeton.com graphicartssystems.com johnsonbrosgreenwich.com rotosolutions.com source3media.com helicalline.com dependable.us generalcolor.com woodbineproducts.com olmstedtransportation.com tallmadgefinishing.com evereadyproducts.com gmrtechnology.com huntimaging.com intellipak.com deterslaw.com genesisplastictechnologies.com srcworldwide.com superiorflux.com bluegrasschemical.com bluegrasschemical.com chagrinvalleysoapandsalve.com commandplastic.com globeplastic.com harborindustrial.com universalcoatings.com autodealerdesigns.com clevelandspecialty.com'''.split()
class Text(HTMLParser):
 def __init__(self):super().__init__();self.parts=[];self.links=[];self.skip=0
 def handle_starttag(self,t,a):
  if t in ('script','style'):self.skip+=1
  if t=='a':self.links.extend(v for k,v in a if k=='href')
 def handle_endtag(self,t):
  if t in ('script','style'):self.skip=max(0,self.skip-1)
 def handle_data(self,s):
  if not self.skip:self.parts.append(s)
def work(pair):
 r,domain=pair;n=int(r['rank']);dest=P/f'{n:02}';dest.mkdir(exist_ok=True);receipt=dest/'receipt.json'
 if receipt.exists():return
 urls=['https://'+domain+'/'];out=[]
 for i,url in enumerate(urls):
  if i>=3:break
  raw=dest/f'{i}.html';run=subprocess.run(['curl','-L','-sS','--max-time','25','--max-filesize','3000000','-A','Mozilla/5.0','-w','%{http_code}\n%{url_effective}',url,'-o',str(raw)],capture_output=True,text=True)
  info=dict(url=url,curl_exit=run.returncode,response=run.stdout)
  if raw.exists():
   b=raw.read_bytes();info.update(sha256=hashlib.sha256(b).hexdigest(),bytes=len(b));t=Text();t.feed(b.decode('utf-8',errors='replace'));(dest/f'{i}.txt').write_text(' '.join(' '.join(t.parts).split()))
   if i==0 and run.returncode==0:
    for link in t.links:
     u=urljoin(url,link)
     if urlsplit(u).netloc==urlsplit(url).netloc and any(x in link.lower() for x in ('contact','about','location')) and u not in urls and len(urls)<3:urls.append(u)
  out.append(info)
 receipt.write_text(json.dumps(dict(rank=n,name=r['name'],domain=domain,pages=out),indent=2))
 print(n,r['name'],len(out),flush=True)
if __name__=='__main__':
 rows=list(csv.DictReader((P/'frame.csv').open()));assert len(rows)==len(DOMAINS)==80
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:list(pool.map(work,zip(rows,DOMAINS)))
