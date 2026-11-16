"""Resumable primary fetch receipts; full raw witnesses stay in controller storage."""
import urllib.request, subprocess, json, hashlib, re, html
from pathlib import Path
CACHE=Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/integrator-backlog-4');CACHE.mkdir(parents=True,exist_ok=True)
URLS={
'cooperiso':'https://www.cooperstandard.com/sites/default/files/ISO%2014001%20Certificate%202023-2026%20NP%20CSISG.pdf',
'kingspanhome':'https://roofing.kingspan.com/',
'altraset':'https://altraset.mar-bal.com/about/',
'kingspan':'https://applications.deq.ok.gov/permitspublic/storedpermits/8998.pdf',
'silgan':'https://silgandispensing.com/news/two-silgan-dispensing-manufacturing-sites-receive-iscc-plus-certification/',
'nov':'https://assets.nov.com/NCP4N68N/at/6349njt78mq7q638cjkkqjh/STAR_Anhydride_Line_Pipe_High_Pressure_-_Standard_Design_Data_Sheet.pdf',
'ppg':'https://www.sec.gov/Archives/edgar/data/79879/000007987926000046/ppg-20251231.htm',
'shw':'https://www.sec.gov/Archives/edgar/data/89800/000008980026000008/shw-20251231.htm',
'paint':'https://www.pittsburghpaintsco.com/',
'hexpol':'https://www.hexpol.com/rubber/plant-locations/hexpol-silicone-compounding/',
'cooper':'https://www.cooperstandard-isg.com/',
'ppg21':'https://www.sec.gov/Archives/edgar/data/79879/000007987926000046/ppg2025ex21-subsidiariesof.htm',
'shw21':'https://www.sec.gov/Archives/edgar/data/89800/000008980026000008/shw-12312025xex211.htm'
}
if __name__=='__main__':
 for key,url in URLS.items():
  p=CACHE/(key+'.raw')
  if not p.exists():
   try:
    data=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Atlas research contact research@polymerindustrycluster.org'}),timeout=35).read();p.write_bytes(data)
   except Exception as e: print(key,str(e),flush=True);continue
  if p.read_bytes().startswith(b'%PDF'):
   subprocess.run(['pdftotext','-layout',str(p),str(CACHE/(key+'.txt'))],check=True)
  else:
   s=p.read_text(errors='replace');s=re.sub(r'<(script|style)\b.*?</\1>',' ',s,flags=re.S|re.I);s=re.sub('<[^>]+>',' ',s);s=html.unescape(s)
   (CACHE/(key+'.txt')).write_text(re.sub(r'\s+',' ',s))
  print(key,len(p.read_bytes()),hashlib.sha256(p.read_bytes()).hexdigest(),flush=True)
 # Persist complete source context with individual contact fields redacted.
 receipts=[]
 for key,url in URLS.items():
  raw=CACHE/(key+'.raw');txt=CACHE/(key+'.txt')
  if not raw.exists() or not txt.exists():continue
  text=txt.read_text()
  text=re.sub(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', '[EMAIL REDACTED]',text)
  text=re.sub(r'(?<!\d)(?:\+?1[ -]?)?\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}(?!\d)','[PHONE REDACTED]',text)
  witness=CACHE/(key+'.witness.txt');witness.write_text(text)
  receipts.append(dict(key=key,url=url,raw_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),witness_file=witness.name,witness_sha256=hashlib.sha256(witness.read_bytes()).hexdigest(),retrieved='2026-11-16',route='urllib.request direct origin, User-Agent: Atlas research contact research@polymerindustrycluster.org; PDF via pdftotext -layout; HTML via fetch.py strip/decode; contact fields redacted'))
 Path(__file__).with_name('fetch-receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
