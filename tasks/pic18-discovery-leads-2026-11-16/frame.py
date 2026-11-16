"""Recompute the privacy-preserving rank frame from the two supplied lead caches."""
import csv,sqlite3,sys
from pathlib import Path
from build import ROOT,P,read
sys.path.insert(0,str(ROOT/'scripts'));import atlas
from regions import PIC18

def derive():
 S=P.parent;loans=read(S/'ppp-loan-scout/leads.csv');groups={}
 assert len(loans)==342 and len({atlas.name_key(r['BorrowerName']) for r in loans})==296
 for r in loans:
  k=atlas.name_key(r['BorrowerName']);v=dict(name=r['BorrowerName'],street=r['BorrowerAddress'],city=r['BorrowerCity'],jobs=float(r['JobsReported'] or 0),origin='PPP',domain='')
  if k not in groups or v['jobs']>groups[k]['jobs']:groups[k]=v
 cities={r['BorrowerCity'].upper() for r in loans}|{r['city'].upper() for f in (ROOT/'data').glob('sites_*.csv') for r in read(f) if r['state']=='OH' and r['county'] in PIC18}
 with sqlite3.connect(S/'sam-entity-scout/sam.sqlite') as c:
  c.row_factory=sqlite3.Row
  sam=[dict(r) for r in c.execute("select * from sam where state='OH' and uei not in(select uei from matches)") if r['city'].upper() in cities and any(x.startswith(('325','326')) for x in (str(r['naics'])+';'+str(r['listed_naics'])).replace('~',';').split(';'))]
 for r in sam:
  k=atlas.name_key(r['name'])
  if k in groups:groups[k]['origin']='PPP;SAM'
  else:groups[k]=dict(name=r['name'],street=r['street'],city=r['city'],jobs=0,origin='SAM',domain='')
 rows=sorted(groups.values(),key=lambda r:(-r['jobs'],atlas.name_key(r['name'])))[:80]
 return [dict(rank=str(i+1),**{k:str(v) for k,v in r.items()}) for i,r in enumerate(rows)],dict(ppp_loans=len(loans),ppp_names=296,sam_rows=len(sam),merged_names=len(groups),selected_names=len(rows))
if __name__=='__main__':
 rows,counts=derive();assert rows==read(P/'frame.csv'),'frame drift';print(counts)
