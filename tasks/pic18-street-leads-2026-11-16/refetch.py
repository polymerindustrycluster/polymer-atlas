import concurrent.futures,subprocess,hashlib,json,re
from scout import S,TASK,read,write
from pathlib import Path
from html.parser import HTMLParser
class Text(HTMLParser):
 def __init__(self):super().__init__();self.parts=[]
 def handle_data(self,s):self.parts.append(s)
def words(t):return re.findall(r'[a-z0-9]+',t.lower())
def check(row):
 if row['source_class']!='own_site' or row['disposition']!='applied':return row
 p=S/'pic18-street-leads';p.mkdir(exist_ok=True)
 r=subprocess.run(['curl','-sL','--compressed','--max-time','40','-A','Mozilla/5.0',row['source_ref']],capture_output=True)
 sha=hashlib.sha256(r.stdout).hexdigest();raw=p/(sha+'.html');raw.write_bytes(r.stdout)
 t=Text();t.feed(r.stdout.decode(errors='replace'));w=words(' '.join(t.parts));q=words(row['quote']);ok=any(w[i:i+len(q)]==q for i in range(len(w)-len(q)+1))
 row['fresh_sha256']=sha;row['fresh_file']=str(raw)
 if not ok:row.update(disposition='held',verdict='STILL_UNCERTAIN',settling_fact='Need a readable fresh own-site physical-address block reproducing the stored quote; fetch failure is availability only.')
 return row
if __name__=='__main__':
 rows=read(TASK/'proposals.csv')
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:out=list(pool.map(check,rows))
 for r in out:r.setdefault('fresh_sha256','');r.setdefault('fresh_file','')
 write(TASK/'proposals.csv',out);print('fresh verified',sum(r['disposition']=='applied' for r in out))
