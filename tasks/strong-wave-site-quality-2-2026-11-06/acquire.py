"""Public raw re-acquisition of each selected page into a fresh cache; refuse quote/binding/hash drift rather than bypass a missing witness."""
import concurrent.futures,hashlib,sys,tempfile
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from site_corpus import Corpus,on_page,same_page
from prep import read

def one(r):
 with tempfile.TemporaryDirectory(prefix='atlas-public-witness-') as tmp:
  c=Corpus(Path(tmp));m=c.fetch(r['source_url'])
  assert m['status']=='ok' and same_page(m['final_url'],r['source_url']),('source unavailable/wrong page',r['site_id'],m['status'])
  text=' '.join((Path(tmp)/m['text_file']).read_text().split())
  for k in ['quote','activity_quote','city_quote','binding_quote','context_quote']:
   if r[k]:assert on_page(r[k],text),('raw quote absent',r['site_id'],k)
  assert hashlib.sha256(text.encode()).hexdigest()==r['page_sha256'],('reviewed page changed',r['site_id'])
  p=Path(r['page']);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)  # absolute path under the persist dir
  return dict(site_id=r['site_id'],status='PASS',fetched_at=m['fetched_at'],route=m['route'])

def attempt(r):
 try:return one(r)
 except AssertionError as e:return dict(site_id=r['site_id'],status='FAIL',reason=str(e))

if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  results=list(pool.map(attempt,read(H/'selected.csv')))
 for result in results:print(result,flush=True)
 sys.exit(any(r['status']!='PASS' for r in results))
