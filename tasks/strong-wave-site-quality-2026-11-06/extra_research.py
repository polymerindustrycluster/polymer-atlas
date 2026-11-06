"""Fetch only explicitly reviewed discovery URLs, using T1's existing transport."""
import concurrent.futures,json,sys
from pathlib import Path
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H.parents[1]/'scripts'))
from site_corpus import Corpus
from research import CACHE
if __name__=='__main__':
 urls=json.loads(Path(sys.argv[1]).read_text());assert len(urls)==len(set(urls));rs=[];c=Corpus(CACHE)
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
  for u,r in zip(urls,pool.map(c.fetch,urls)):
   rs.append(r);(H/'extra_discovery.json').write_text(json.dumps(rs,indent=2)+'\n');print(r['status'],u,flush=True)
