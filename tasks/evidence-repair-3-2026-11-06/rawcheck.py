"""Fresh raw-page checks of manually adjudicated replacements (house L1 matcher)."""
import concurrent.futures,csv,hashlib
from pathlib import Path
from fetch import read,fetch,on_page,ROOT,live_posture
H=Path(__file__).resolve().parent
if __name__=='__main__':
 selected=read(H/'selected.csv');urls=sorted({r['source_url'] for r in selected})
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:fs=dict(zip(urls,pool.map(lambda u:fetch(u,refresh=True),urls)))
 rows=[]
 for r in selected:
  f=fs[r['source_url']];ok=f['status']=='ok' and live_posture(f,r['source_url'])=='ok' and on_page(r['quote'],ROOT/f['page'])
  b=(ROOT/f['page']).read_bytes() if f.get('page') else b'';digest=hashlib.sha256(b).hexdigest();frozen=ROOT/'build/l11-repair3-cache/frozen'/(digest+'.txt');frozen.parent.mkdir(exist_ok=True);frozen.write_bytes(b)
  rows.append(dict(**r,page_sha256=digest,raw='yes' if ok else 'no',page=str(frozen.relative_to(ROOT)),sha256=f.get('sha256',''),fetched_at=f['fetched_at']))
 with open(H/'rawcheck.csv','w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
 print('raw',sum(r['raw']=='yes' for r in rows),'/',len(rows),'URLs',len(urls))
 assert all(r['raw']=='yes' for r in rows),'unverified source holds; do not apply'
