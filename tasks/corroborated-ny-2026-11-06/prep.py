import csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
from atlas import load_tables,dedupe
T=load_tables(ROOT/'data')
def read(p):return list(csv.DictReader(open(p)))
H=Path(__file__).parent
cs=[c for c in read(ROOT/'tasks/lead-fusion-2026-11-01/clusters.csv') if c['state']=='NY' and c['class']=='CORROBORATED']
with open(H/'input.csv','w') as f:
 w=csv.DictWriter(f,fieldnames=list(cs[0]),lineterminator='\n');w.writeheader();w.writerows(cs)
report={}
for c in cs:
 hits={}
 for n in [c['best_name']]+c['name_variants'].split(' | '):
  d=dedupe(T,name=n,street=c['street'],city=c['city'],state=c['state'],zip_=c['zip5'])
  for st in d['steps']:
   for h in st['hits']:hits[h['id']]=h
 report[c['cluster_id']]=list(hits.values())
 print(c['cluster_id'],c['best_name'],c['city'],' | '.join(h['id']+' '+h['name'] for h in hits.values())[:230])
(H/'dedupe.json').write_text(json.dumps(report,indent=2))
