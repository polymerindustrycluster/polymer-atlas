"""Freshly re-fetch every admitted URL; require manual context review if its raw body changes."""
import hashlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from research import P,read,fetch,found
raw=read(P/'rawcheck.csv');witnesses={r['site_id']:r for r in read(P/'witnesses.csv')}
sources={r['source_id']:r for r in read(P/'sources.csv')};ids=list(dict.fromkeys(r['source_id'] for r in raw))
for sid in ids:
 r=next(r for r in raw if r['source_id']==sid);p=Path(r['cache_file']);p.with_suffix('.before.txt').write_bytes(p.read_bytes())
results=list(ThreadPoolExecutor(max_workers=4).map(fetch,[sources[sid] for sid in ids]))
changed=[]
for result in results:
 assert result['fetch']=='loaded',('fresh source unavailable',result['source_id'])
 text=Path(result['cache_file']).read_text()
 for r in raw:
  if r['source_id']!=result['source_id']:continue
  assert found(text,r['quote']) and found(text,witnesses[r['site_id']]['location_anchor']),('fresh words/location missing',r['site_id'])
  if result['raw_sha256']!=r['raw_sha256']:changed.append(result['source_id'])
assert not changed,('fresh body changed: reread context before updating receipt',sorted(set(changed)))
print('PASS fresh raw:',len(ids),'URLs /',len(raw),'site quotes; all bodies unchanged; no summary/snippet witnesses.')
