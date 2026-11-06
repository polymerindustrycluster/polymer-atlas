"""Reuse the merged L6 curl/Jina fetcher and house token matcher for nominated operator pages."""
import csv,hashlib,importlib.util,subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('l6_house_research',P.parent/'corroborated-ca-tx-quality-2026-11-06/research.py')
house=importlib.util.module_from_spec(spec);spec.loader.exec_module(house)
found=house.found
def read(p):
 with p.open(newline='') as f:return list(csv.DictReader(f))
def fetch(r):
 key='L7-quality-'+r['source_id'];cache=Path('/tmp/L6-'+key+'.txt')
 if r['format']=='pdf':
  pdf=cache.with_suffix('.pdf');x=subprocess.run(['curl','--fail','-sS','-L','--max-time','30','-A','Mozilla/5.0',r['url'],'-o',str(pdf)],capture_output=True)
  if x.returncode==0:x=subprocess.run(['pdftotext','-layout',str(pdf),str(cache)],capture_output=True)
  result={'fetch':'loaded' if x.returncode==0 else 'unfetchable','route':r['url']}
  if result['fetch']!='loaded':
   route='https://r.jina.ai/'+r['url'];x=subprocess.run(['curl','--fail','-sS','-L','--max-time','30','-A','Mozilla/5.0',route],capture_output=True)
   if x.returncode==0 and len(x.stdout)>300:cache.write_bytes(x.stdout);result={'fetch':'loaded','route':route}
 else:result=house.fetch((key,r['url']))
 if result['fetch']=='loaded' and len(cache.read_text().strip())<120:result['fetch']='unreadable'
 return {**r,**result,'cache_file':str(cache),'raw_sha256':hashlib.sha256(cache.read_bytes()).hexdigest() if result['fetch']=='loaded' else ''}
if __name__=='__main__':
 rows=read(P/'sources.csv');assert len(rows)==len({r['source_id'] for r in rows})==len({r['url'] for r in rows})
 for oid in {r['org_id'] for r in rows}:assert sum(r['org_id']==oid for r in rows)<=6,('fetch cap',oid)
 old=read(P/'fetches.csv') if (P/'fetches.csv').exists() else [];done={r['source_id'] for r in old}
 results=old+list(ThreadPoolExecutor(max_workers=4).map(fetch,[r for r in rows if r['source_id'] not in done]))
 fields=list(dict.fromkeys(k for r in results for k in r))
 with (P/'fetches.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(results)
 print('Fetch outcomes:',len(results),'/',len(rows),{k:sum(r['fetch']==k for r in results) for k in ['loaded','unfetchable','unreadable']})
