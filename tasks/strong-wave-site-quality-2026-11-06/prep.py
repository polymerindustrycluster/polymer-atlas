"""Freeze actual merged creates and consult existing source indexes before live requests."""
import csv,hashlib,json,re,sqlite3,subprocess,sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit
H=Path(__file__).resolve().parent;ROOT=H.parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from site_corpus import Corpus
from bulk_sources import frs_by_registry_id,DEFAULT_CACHE
STATES='MN NY NJ NC TN KY VA MA'.split()
EXPECTED=dict(zip(STATES,[40,25,23,25,23,25,16,43]))
def read(p):
 with open(p,newline='') as f:return list(csv.DictReader(f))
def write(p,rows,fields):
 with open(p,'w',newline='') as f:
  w=csv.DictWriter(f,fields,extrasaction='ignore',lineterminator='\n');w.writeheader();w.writerows(rows)
def host(u):return (urlsplit(u).hostname or '').lower().removeprefix('www.')
def main():
 assert not (H/'baseline.json').exists(),'frame already frozen'
 base=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
 orgs={r['org_id']:r for p in (ROOT/'data').glob('organizations_*.csv') for r in read(p)}
 allrows=[];inputs=[];packets={};counts={}
 for st in STATES:
  task=ROOT/f'tasks/{st.lower()}-strong-wave-2026-11-04'
  vs={r['cluster_id']:r for p in task.glob('lanes/L*/verdicts.csv') for r in read(p)}
  cs={r['cluster_id']:r for p in task.glob('lanes/L*/input.csv') for r in read(p)}
  rows=[r for r in read(ROOT/f'data/sites_{st}.csv') if r['created_by']==f'claude-code {st.lower()}-strong-wave-2026-11-04']
  assert len(rows)==EXPECTED[st],(st,len(rows),EXPECTED[st])
  counts[st]=dict(Counter(r['verification_tier'] for r in rows))
  for s in rows:
   cid=re.search(r'cluster (LF-[A-Z]{2}-\d+)',s['notes'])[1]
   assert vs[cid]['verdict'].strip() in ('VERIFIED_NEW_ORG','VERIFIED_NEW_SITE','VERIFIED_HELD_ORG','VERIFIED_EXISTING_ORG'),vs[cid]['verdict']
   o=orgs[s['org_id']];v=vs[cid];c=cs[cid]
   r=dict(s,cluster_id=cid,task=str(task.relative_to(ROOT)),org_legal_name=o['legal_name'],org_website=o['website'],org_trade_names=o['trade_names'],parent_org_id=o['parent_org_id'],ultimate_parent_name=o['ultimate_parent_name'],org_notes=o['notes'],sources_with_ids=c['sources_with_ids'],prior_own_url=v['own_url'],prior_own_quote=v['own_quote'])
   allrows.append(r)
   if s['verification_tier']=='C':inputs.append(r)
 assert len(allrows)==220 and len(inputs)==161 and len({r['site_id'] for r in allrows})==220
 assert len({r['cluster_id'] for r in allrows})==220
 write(H/'creation_frame.csv',allrows,list(allrows[0]));write(H/'input.csv',inputs,list(inputs[0]))
 manifest=json.loads((DEFAULT_CACHE/'manifest.json').read_text())['frs']
 echo=[]
 for r in inputs:
  ids=re.findall(r'(?:^|;)ECHO:(\d+)',r['sources_with_ids'])
  for rid in ids:
   found=frs_by_registry_id(rid)
   for f in found:
    echo.append(dict(site_id=r['site_id'],registry_id=rid,**{k:f.get(k,'') for k in ['FAC_NAME','FAC_STREET','FAC_CITY','FAC_STATE','FAC_ZIP','FAC_COUNTY','FAC_NAICS_CODES']},source_ref=manifest['url'],observed_date=manifest['date'][:10],snapshot_sha256=manifest['sha256']))
 write(H/'echo_lookup.csv',echo,list(echo[0]) if echo else ['site_id','registry_id'])
 (H/'echo_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 corpus=Corpus();index=read(corpus.cache/'index.csv');domains={host(r['org_website']) for r in inputs if host(r['org_website'])};cached=[]
 for rec in index:
  if rec.get('extraction_version')!='3' or host(rec['url']) not in domains or '/robots.txt' in rec['url']:continue
  current=corpus.cached(rec['url'])
  if current and not any(x['url']==current['url'] for x in cached):cached.append(current)
 write(H/'corpus_lookup.csv',cached,list(cached[0]) if cached else ['url','status'])
 (H/'baseline.json').write_text(json.dumps(dict(base=base,frame_commit=base,counts=counts,frame_sites=220,input_sites=161,echo_rows=len(echo),corpus_pages=len(cached)),indent=2)+'\n')
 print(json.dumps(dict(counts=counts,inputs=len(inputs),echo_rows=len(echo),corpus_pages=len(cached))))
if __name__=='__main__':main()
