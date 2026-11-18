"""Live fetches (links from stored pages only, rule 14); raw bytes + journal under persist."""
import hashlib,json,re,sys,html,urllib.request,datetime
from pathlib import Path
P=Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/pic18-size-ownsite-2026-11-18')
# (org, url, stored page it was linked from)
LIVE=[('ORG-001592','https://www.alphatoolandmold.com/employment/','alphatoolandmold.com/ (stored home nav)'),
('ORG-001514','https://juzousa.com/About-Us/The-Juzo-Family','juzousa.com/About-Us/Juzo-History nav'),
('ORG-001514','https://juzousa.com/About-Us/Juzo-International','juzousa.com/About-Us/Juzo-History nav'),
('ORG-000156','https://www.swagelok.com/en/about/global','swagelok.com/en/about nav'),
('ORG-000156','https://www.swagelok.com/en/about/legacy','swagelok.com/en/about nav')]
def text(b):
 t=re.sub(r'<(script|style)[^>]*>.*?</\1>',' ',b.decode('utf8','replace'),flags=re.S)
 return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]+>',' ',t)))
for org,url,via in LIVE:
 d=P/org;d.mkdir(parents=True,exist_ok=True)
 try:
  rq=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; atlas-research)'})
  with urllib.request.urlopen(rq,timeout=30) as r:code,b=r.status,r.read()
 except Exception as e:code,b=str(e)[:60],b''
 h=hashlib.sha256(b).hexdigest()
 (d/(h[:16]+'.html')).write_bytes(b)
 rec=dict(org=org,url=url,linked_from=via,status=code,sha256=h,at=datetime.datetime.utcnow().isoformat()+'Z')
 with open(P/'journal.jsonl','a') as f:f.write(json.dumps(rec)+'\n')
 print(rec)
 for m in re.finditer(r'.{0,140}(?:employ|associates|team members|staff|workforce).{0,140}',text(b),re.I):
  if re.search(r'\d',m.group(0)):print('   ',m.group(0))
