"""Fetch each seeded operator homepage using existing corpus transport and cache receipts."""
import csv,sys,json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from build import HERE,P,ROOT,read
sys.path.insert(0,str(ROOT/'scripts'));from site_corpus import Corpus
C=Corpus(P/'own_site')
def one(r):
 if not r['website']:return dict(site_id=r['site_id'],status='NO_URL')
 result=C.fetch(r['website']);result['site_id']=r['site_id'];return result
if __name__=='__main__':
 results=list(ThreadPoolExecutor(max_workers=8).map(one,read(HERE/'sample_frame.csv')))
 (P/'sample_fetch.json').write_text(json.dumps(results,indent=2))
 print([(r['site_id'],r['status']) for r in results])
