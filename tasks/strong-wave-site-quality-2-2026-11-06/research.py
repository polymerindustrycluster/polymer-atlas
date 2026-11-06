"""Known-answer test first, then fetch each candidate's recorded own-site pages through the shared Corpus transport."""
import concurrent.futures,json,sys
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from site_corpus import Corpus,on_page
from prep import read
CACHE=Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/cache/strong-quality-2')
def known(corpus):
 # Round 1's three known-B own-site answers (merged in #237): the fetcher must reproduce each quote and reject a fabricated one.
 checks=[]
 for k in json.loads((ROOT/'tasks/strong-wave-site-quality-2026-11-06/known_answers.json').read_text()):
  rec=corpus.fetch(k['url']);t=(CACHE/rec['text_file']).read_text() if rec['status']=='ok' else ''
  checks.append(dict(site_id=k['site_id'],url=k['url'],quote=k['quote'],status=rec['status'],positive=bool(on_page(k['quote'],t)),negative=bool(on_page(k['quote']+' fabricated atlas zebra 7731',t))))
 (H/'known_answers.json').write_text(json.dumps(checks,indent=2)+'\n')
 assert len(checks)==3 and all(c['positive'] and not c['negative'] for c in checks),checks
def main():
 corpus=Corpus(CACHE);known(corpus)
 fed={r['site_id']:r for r in read(H/'federal_review.csv')}
 urls=[]
 for r in read(H/'input.csv'):
  if fed[r['site_id']]['admissible']!='yes':continue
  for u in (r['prior_own_url'],r['org_website']):
   if u.startswith(('http://','https://')) and u not in urls:urls.append(u)
 out=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
  for u,rec in zip(urls,pool.map(corpus.fetch,urls)):
   out.append(rec);(H/'discovery.json').write_text(json.dumps(out,indent=2)+'\n');print(rec['status'],u,flush=True)
if __name__=='__main__':main()
