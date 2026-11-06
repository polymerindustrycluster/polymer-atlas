"""Bounded curl + house Jina fallback; cache outside the public tree."""
import concurrent.futures, hashlib, html, json, re, subprocess
from html.parser import HTMLParser
from pathlib import Path
# Persisted copy of the sanitized cache (survives /tmp cleanup and worktree archive); /tmp is the original location.
CACHE = Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/people-titles-3-2026-11-06/pages')
if not CACHE.exists(): CACHE = Path('/tmp/atlas-l12-titles3-pages')
CACHE.mkdir(exist_ok=True)
class Text(HTMLParser):
    def __init__(self): super().__init__(); self.parts=[]; self.skip=0
    def handle_starttag(self,t,a):
        if t in ('script','style'): self.skip+=1
        if t in ('p','br','div','h1','h2','h3','h4','li','tr'): self.parts.append('\n')
    def handle_endtag(self,t):
        if t in ('script','style'): self.skip=max(0,self.skip-1)
        if t in ('p','div','h1','h2','h3','li','tr'): self.parts.append('\n')
    def handle_data(self,d):
        if not self.skip:self.parts.append(d)
def words(s):return re.findall(r'[a-z0-9]+',s.lower())
def found(p,q):
    p,q=words(p),words(q)
    return bool(q) and any(p[i:i+len(q)]==q for i in range(len(p)-len(q)+1))
def get(u, *, refresh=False):
    f=CACHE/(hashlib.sha256(u.encode()).hexdigest()+'.json')
    if f.exists() and not refresh:return json.loads(f.read_text())
    errors=[]
    for route in (u,'https://r.jina.ai/'+u):
        r=subprocess.run(['curl','-L','--fail','--max-time','25','-sS','-A','Mozilla/5.0',route],capture_output=True,text=True,errors="replace")
        if r.returncode: errors.append(str(r.returncode));continue
        raw=r.stdout
        if '<html' in raw.lower() or '<!doctype' in raw.lower():
            p=Text();p.feed(raw);raw=''.join(p.parts)
        raw=html.unescape(raw)
        raw=re.sub(r'[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}', '[contact omitted]',raw)
        raw=re.sub(r'(?<![0-9])(?:\+1[ .-]?)?\(?[0-9]{3}\)?[ .-][0-9]{3}[ .-][0-9]{4}(?![0-9])', '[contact omitted]', raw)
        raw='\n'.join(re.sub(r'\s+',' ',l).strip() for l in raw.splitlines() if l.strip())
        if len(raw)<150 or any(x in raw.lower()[:2000] for x in ('access denied','just a moment','verify you are human','403 forbidden','404 not found')):errors.append('blocked/empty');continue
        out={'url':u,'route':route,'text':raw,'status':'ok'};break
    else:out={'url':u,'text':'','status':'unfetchable '+','.join(errors)}
    f.write_text(json.dumps(out));return out
