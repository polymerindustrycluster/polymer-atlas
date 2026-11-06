"""Acquire required public source text; reviewed hash/quote/binding must match before cache write."""
import concurrent.futures,hashlib
from pathlib import Path
from fetch import ROOT,read,fetch,live_posture,on_page
H=Path(__file__).resolve().parent
def acquire(r):
 f=fetch(r['source_url'],refresh=True)
 assert live_posture(f,r['source_url'])=='ok',('exact public page unavailable',r['key'])
 text=' '.join((ROOT/f['page']).read_text().split())
 assert hashlib.sha256(text.encode()).hexdigest()==r['page_sha256'],('source changed; review required, never bypass hash',r['key'])
 assert on_page(r['quote'],ROOT/f['page']) and on_page(r['binding_quote'],ROOT/f['page']),('quote/binding absent',r['key'])
 p=ROOT/r['page'];p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
 return r['key']
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:done=list(pool.map(acquire,read(H/'rawcheck.csv')))
 print('PASS public acquisition',len(done),done)
