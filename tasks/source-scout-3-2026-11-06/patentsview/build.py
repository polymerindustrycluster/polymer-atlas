"""Aggregate the public bulk join; exact matches are candidates, never automatic merges."""
import csv,sys,json,random
from pathlib import Path
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
import atlas
from regions import PIC18
from build_cbp_size_classes import PIC_COUNTIES
HERE=Path(__file__).parent

def write(name,rows):
 with (HERE/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)

def main():
 tables=atlas.load_tables(ROOT/'data');names=defaultdict(set);held={}
 for table in ['organizations','ecosystem']:
  for r in tables[table].rows:
   held[r['org_id']]=r
   for n in [r['legal_name']]+r.get('trade_names','').split(';'): 
    if n:names[atlas.name_key(n)].add(r['org_id'])
 groups={};patents=set();pic=defaultdict(set)
 counties={f[2:] for f in PIC_COUNTIES}
 with open(sys.argv[1]) as f:
  for r in csv.DictReader(f):
   patents.add(r['patent_id']);g=groups.setdefault(r['assignee_id'],dict(names=set(),patents=set(),countries=set(),states=set(),sample=None,pic=False))
   g['names'].add(r['name']);g['patents'].add(r['patent_id']);g['countries'].add(r['country']);g['states'].add(r['state']);g['sample']=min(g['sample'] or r,r,key=lambda x:x['patent_id'])
   if r['country']=='US' and r['state']=='OH' and r['county_fips'] in counties:g['pic']=True
 out=[]
 for aid,g in sorted(groups.items()):
  ids=set().union(*(names[atlas.name_key(n)] for n in g['names']))
  out.append(dict(assignee_id=aid,name=';'.join(sorted(g['names'])),countries=';'.join(sorted(g['countries'])),states=';'.join(sorted(g['states'])),patent_count=len(g['patents']),atlas_ids=';'.join(sorted(ids)),pic18_assignee_location=int(g['pic'])))
  if g['pic']:
   for oid in ids:pic[oid].update(g['patents'])
 assert len(out)==len({r['assignee_id'] for r in out})
 write('assignees.csv',out)
 # Unit is held organizations with an OH PIC18 county HQ or site, rather than inventor locality.
 footprint={r['org_id'] for r in tables['sites'].rows if r['state']=='OH' and r['county'] in PIC18}
 footprint|={r['org_id'] for r in tables['organizations'].rows if r['hq_state']=='OH' and r['hq_county'] in PIC18}
 picheld=[dict(org_id=oid,atlas_name=held[oid]['legal_name'],patent_count=len(pats)) for oid,pats in sorted(pic.items()) if oid in footprint]
 write('pic18_matches.csv',picheld)
 sample=[]
 for r in random.Random(20261106).sample([r for r in out if 'US' in r['countries'].split(';')],20):
  g=groups[r['assignee_id']];p=g['sample'];d=atlas.dedupe(tables,name=p['name']);hits=sorted({h['id'] for st in d['steps'] for h in st['hits']})
  sample.append(dict(name=p['name'],assignee_id=r['assignee_id'],patent_id=p['patent_id'],grant_date=p['patent_date'],cpc=p['cpc'],city=p['city'],state=p['state'],country=p['country'],county_fips=p['county_fips'],atlas_ids=';'.join(hits),domain_check='not in bulk assignee table',street_check='not in disambiguated location table',source_url='https://api.uspto.gov/api/v1/datasets/products/PVGPATDIS',verdict='DUPLICATE_OF' if len(hits)==1 else 'STILL_UNCERTAIN',reason='held candidate; patent assignee does not establish current operation or polymer scope' if hits else 'settling fact: own-site current polymer process and organization identity; patent ownership alone insufficient',verified_new=0))
 write('sample.csv',sample)
 stats=dict(qualifying_patents=len(patents),organization_assignees=len(out),exact_name_candidates=sum(bool(r['atlas_ids']) for r in out),us_assignees=sum('US' in r['countries'].split(';') for r in out),pic18_location_assignees=sum(r['pic18_assignee_location'] for r in out),pic18_held_organization_candidates=len(picheld))
 (HERE/'counts.json').write_text(json.dumps(stats,indent=2)+'\n');print(stats)
if __name__=='__main__':main()
