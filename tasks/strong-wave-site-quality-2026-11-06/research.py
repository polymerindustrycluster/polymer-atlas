"""Use the shared corpus transport; every route receipt is retained outside git."""
import concurrent.futures,csv,json,sys
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from site_corpus import Corpus,on_page
CACHE=Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/cache/l11-strong-quality')
def read(p):return list(csv.DictReader(open(p)))
def main():
 corpus=Corpus(CACHE)
 known=[r for r in read(H/'creation_frame.csv') if r['verification_tier']=='B'][:3]
 checks=[]
 for r in known:
  rec=corpus.fetch(r['prior_own_url']);t=(CACHE/rec['text_file']).read_text() if rec['status']=='ok' else ''
  checks.append(dict(site_id=r['site_id'],url=r['prior_own_url'],quote=r['prior_own_quote'],status=rec['status'],positive=on_page(r['prior_own_quote'],t),negative=on_page(r['prior_own_quote']+' fabricated atlas zebra 7731',t)))
 (H/'known_answers.json').write_text(json.dumps(checks,indent=2)+'\n')
 assert all(r['positive'] and not r['negative'] for r in checks),checks
 rows=read(H/'input.csv');urls=sorted({r['prior_own_url'] or r['org_website'] for r in rows if (r['prior_own_url'] or r['org_website']).startswith(('http://','https://'))})
 results=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
  for u,rec in zip(urls,pool.map(corpus.fetch,urls)):
   results.append(rec);(H/'discovery.json').write_text(json.dumps(results,indent=2)+'\n')
   print(rec['status'],u,flush=True)
if __name__=='__main__':main()
