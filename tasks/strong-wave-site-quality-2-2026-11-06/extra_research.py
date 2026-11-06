"""Fetch only explicitly reviewed discovery URLs (extra_urls.json) through the same cache/transport."""
import concurrent.futures,json,sys
from pathlib import Path
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H.parents[1]/'scripts'))
from site_corpus import Corpus
from research import CACHE
if __name__=='__main__':
 name=sys.argv[1] if len(sys.argv)>1 else 'extra';urls=json.loads((H/f'{name}_urls.json').read_text());assert len(urls)==len(set(urls));rs=[];c=Corpus(CACHE)
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
  for u,r in zip(urls,pool.map(c.fetch,urls)):
   rs.append(r);(H/f'{name}_discovery.json').write_text(json.dumps(rs,indent=2)+'\n');print(r['status'],u,flush=True)
