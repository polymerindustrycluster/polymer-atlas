"""Work frozen class-a source searches; never re-fetch a known prior URL as new."""
from inventory import D,norm
from research import fetch
import json,re
from urllib.parse import urlsplit
from concurrent.futures import ThreadPoolExecutor
rows=json.loads((D/'initial_classifications.json').read_text());prior=json.loads((D/'prior_routes.json').read_text());known={u for v in prior.values() for u in v};jobs=[];discovery={}
for p in sorted(D.glob('search-*.json')):
 x=json.loads(p.read_text())
 for oid,q in zip(x['org_ids'],x['queries']):
  domain=q['q'].split('site:',1)[1].split()[0];candidates=[];old=[]
  for u in x['urls']:
   host=(urlsplit(u).hostname or '').lower().removeprefix('www.')
   if not(host==domain or host.endswith('.'+domain)):continue
   u=u.rstrip('.,;')
   if norm(u) in known:old.append(u);continue
   if u not in candidates:candidates.append(u)
  def score(u):
   s=u.lower();return 10*bool(re.search(r'\.pdf|/getmedia/',s))+4*bool(re.search('material|manufactur|compounding|extrus|3d-printing-services|plastisol|vinyl|faq|technical|about|service|plastics',s))-15*bool(re.search('career|job|ethics|cookie|policy|contact|supply-chain|saiyo|brand-use|rfd.*approval',s))
  selected=sorted(candidates,key=lambda u:(-score(u),len(u)))[:2]
  discovery[oid]={'search_file':p.name,'query':q['q'],'new_candidates':candidates,'excluded_tried_urls':old,'selected_urls':selected}
  jobs.extend((oid,u) for u in selected)
(D/'discovery.json').write_text(json.dumps(discovery,indent=2))
assert len(discovery)==61
assert all(norm(u) not in known for oid,u in jobs)
print('NEW FETCH JOBS',len(jobs),flush=True)
def one(j):
 oid,u=j;r,t=fetch(oid,u);print(oid,r['http_status'],len(t),u,flush=True)
with ThreadPoolExecutor(max_workers=8) as ex:list(ex.map(one,jobs))
