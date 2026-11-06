"""Follow-up read for SITE-011453 (Grok finding on #238): was the hold really an availability block? Records facts only; mints nothing."""
import hashlib,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from site_corpus import Text,on_page,UA
from prep import read
import county_check
def get(url,ua=None):
 cmd=['curl','-sS','-L','-m','40','-o','-','-w','\n%{http_code}']+(['-A',ua] if ua else [])+[url];out=subprocess.run(cmd,capture_output=True).stdout
 body,code=out.rsplit(b'\n',1);return int(code),body
QUOTES={'https://modernpolymers.com/contact/':['Modern Polymers, Inc. 901 W Academy St. Cherryville, NC 28021','Whether you need custom molded EPS or EPP foam solutions for automotive, aerospace, or packaging applications'],'https://modernpolymers.com/facilities/':['Located in Cherryville NC EPS Division: 68,000 Sq. Ft.']}
if __name__=='__main__':
 rec=dict(read_utc=datetime.now(timezone.utc).isoformat(timespec='seconds'),robots_txt_https=get('https://modernpolymers.com/robots.txt',UA)[0],pages=[])
 rec['robots_disallow_lines']=[l for l in get('https://modernpolymers.com/robots.txt',UA)[1].decode().splitlines() if l.lower().startswith(('disallow','user-agent'))]
 for url,quotes in QUOTES.items():
  house,_=get(url,UA);code,body=get(url);p=Text();p.feed(body.decode('utf-8','replace'));text=' '.join(p.parts)
  assert code==200 and all(on_page(q,text) for q in quotes),(url,code)
  rec['pages'].append(dict(url=url,http_default_curl_agent=code,http_house_agent=house,raw_sha256=hashlib.sha256(body).hexdigest(),text_sha256=hashlib.sha256(text.encode()).hexdigest(),quotes_in_order=quotes))
 site=next(r for r in read(H/'input.csv') if r['site_id']=='SITE-011453');c=county_check.one(site)
 rec['census_address_check']={k:c.get(k) for k in ('status','county','geoid','matched_address','raw_sha256')}  # not shipped as evidence
 (H/'modern_polymers_followup.json').write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps(rec,indent=2))
