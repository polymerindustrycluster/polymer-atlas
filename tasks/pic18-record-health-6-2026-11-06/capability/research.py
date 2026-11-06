"""Fresh raw source collection with route deduplication; no evidence inference."""
import csv,json,re,subprocess,hashlib,sys,unicodedata
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from html.parser import HTMLParser
class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.skip=0; self.parts=[]
    def handle_starttag(self,tag,attrs):
        if tag in {"script","style"}: self.skip+=1
    def handle_endtag(self,tag):
        if tag in {"script","style"}: self.skip-=1
    def handle_data(self,data):
        if not self.skip: self.parts.append(data)
D=Path(__file__).resolve().parent
W=lambda s:re.findall(r'[a-z0-9]+',unicodedata.normalize('NFKD',s or '').encode('ascii','ignore').decode().lower())
def has(t,p):
 t,p=W(t),W(p);return bool(p) and any(t[i:i+len(p)]==p for i in range(len(t)-len(p)+1))
def fetch(oid,url,kind='curl_browserUA'):
 folder=D/'raw'/oid;folder.mkdir(parents=True,exist_ok=True);k=hashlib.sha256(url.encode()).hexdigest()[:12];body=folder/(k+'.body');out=folder/(k+'.txt')
 p=subprocess.run(['curl','-L','--max-time','24','--connect-timeout','8','-sS','-A','Mozilla/5.0','-w','%{http_code}\t%{url_effective}',url,'-o',str(body)],capture_output=True,text=True)
 z=p.stdout.split('\t',1);code=z[0];final=z[-1];b=body.read_bytes() if body.exists() else b'';err=p.stderr.strip();parser='HTML Text'
 if b.startswith(b'%PDF'):
  q=subprocess.run(['pdftotext','-layout',str(body),str(out)],capture_output=True,text=True);t=out.read_text(errors='replace') if out.exists() else '';err+=' '+q.stderr.strip();parser='pdftotext -layout'
 else:
  h=Text();h.feed(b.decode(errors='replace'));t=' '.join(' '.join(h.parts).split())
 t=re.sub(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}','[contact redacted]',t);t=re.sub(r'(?:\+?1[\s.-]*)?\(?[2-9]\d{2}\)?[\s.-]*\d{3}[\s.-]*\d{4}','[phone redacted]',t);out.write_text(t)
 if body.exists():body.unlink()
 r=dict(org_id=oid,kind=kind,attempted_url=url,final_url=final,http_status=code,availability='available' if code.startswith('2') and len(t)>100 and not any(s in t.lower() for s in ['access denied','just a moment','verify you are human']) else 'failed_or_sparse',raw_path=str(out.relative_to(D)),observed_date='2026-11-06',notes=parser+'; '+err)
 log=folder/'routes.json';rr=json.loads(log.read_text()) if log.exists() else [];rr.append(r);log.write_text(json.dumps(rr,indent=2));return r,t
if __name__=='__main__':
 r,t=fetch(sys.argv[1],sys.argv[2]);print(r);print(' '.join(t.split())[:600])
