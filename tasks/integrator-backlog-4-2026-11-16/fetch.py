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
