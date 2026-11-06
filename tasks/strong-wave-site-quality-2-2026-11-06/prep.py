"""Round 2: freeze eligible-frame rows 41-80 against current main; consult bulk ECHO index and T1 corpus first."""
import csv,json,re,subprocess,sys
from pathlib import Path
from urllib.parse import urlsplit
H=Path(__file__).resolve().parent;ROOT=H.parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from site_corpus import Corpus
from bulk_sources import frs_by_registry_id,DEFAULT_CACHE
FRAME=ROOT/'tasks/strong-wave-site-quality-2026-11-06/eligible_frame.csv'  # round 1's frozen 161-site frame, merged in #237
def read(p):
 with open(p,newline='') as f:return list(csv.DictReader(f))
def write(p,rows,fields):
 with open(p,'w',newline='') as f:
  w=csv.DictWriter(f,fields,extrasaction='ignore',lineterminator='\n');w.writeheader();w.writerows(rows)
def host(u):return (urlsplit(u).hostname or '').lower().removeprefix('www.')
def main():
 assert not (H/'baseline.json').exists(),'frame already frozen'
 base=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
 eligible=read(FRAME);assert len(eligible)==161 and len({r['site_id'] for r in eligible})==161
 inputs=eligible[40:80];assert [r['site_id'] for r in inputs][0]=='SITE-011166' and inputs[-1]['site_id']=='SITE-011459'
 cur={r['site_id']:r for p in (ROOT/'data').glob('sites_*.csv') for r in read(p)}
 for r in inputs:  # preimage: every framed site is unchanged on current main
  c=cur[r['site_id']];assert all(c[k]==r[k] for k in c),('frame row changed on main',r['site_id'])
  assert r['verification_tier']=='C' and r['operating_status']=='active'
 write(H/'input.csv',inputs,list(inputs[0]))
 manifest=json.loads((DEFAULT_CACHE/'manifest.json').read_text())['frs'];echo=[]
 for r in inputs:
  for rid in re.findall(r'(?:^|;)ECHO:(\d+)',r['sources_with_ids']):
   for f in frs_by_registry_id(rid):
    echo.append(dict(site_id=r['site_id'],registry_id=rid,**{k:f.get(k,'') for k in ['FAC_NAME','FAC_STREET','FAC_CITY','FAC_STATE','FAC_ZIP','FAC_COUNTY','FAC_NAICS_CODES']},source_ref=manifest['url'],observed_date=manifest['date'][:10],snapshot_sha256=manifest['sha256']))
 write(H/'echo_lookup.csv',echo,list(echo[0]) if echo else ['site_id','registry_id'])
 (H/'echo_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 corpus=Corpus();index=read(corpus.cache/'index.csv');domains={host(r['org_website']) for r in inputs if host(r['org_website'])};cached=[]
 for rec in index:
  if rec.get('extraction_version')!='3' or host(rec['url']) not in domains or '/robots.txt' in rec['url']:continue
  cur_rec=corpus.cached(rec['url'])
  if cur_rec and not any(x['url']==cur_rec['url'] for x in cached):cached.append(cur_rec)
 write(H/'corpus_lookup.csv',cached,list(cached[0]) if cached else ['url','status'])
 (H/'baseline.json').write_text(json.dumps(dict(base=base,frame_rows='41-80',input_sites=40,echo_rows=len(echo),corpus_pages=len(cached)),indent=2)+'\n')
 print(json.dumps(dict(inputs=len(inputs),echo_rows=len(echo),corpus_pages=len(cached))))
if __name__=='__main__':main()
