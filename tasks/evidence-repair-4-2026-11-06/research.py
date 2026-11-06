"""Re-fetch frozen weak-source URLs using L1's calibrated public-page fetcher."""
import concurrent.futures,csv,json
from pathlib import Path
from fetch import fetch,read,ROOT,CACHE,on_page,live_posture
H=Path(__file__).resolve().parent
if __name__=='__main__':
 rows=read(H/'input.csv');urls=sorted({r['url'] for r in rows})
 assert len(rows)==269 and len(urls)==155
 with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
  result=list(pool.map(lambda u:fetch(u,refresh=True),urls))
 for r in result:r['posture']=live_posture(r,r['url'])
 (H/'fetches.json').write_text(json.dumps(result,indent=2)+'\n')
 print('Fetched',len(result),'of',len(urls),{s:sum(r['posture']==s for r in result) for s in {r['posture'] for r in result}},flush=True)
