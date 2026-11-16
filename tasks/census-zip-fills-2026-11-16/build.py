"""Apply the owner's 2026-11-16 Census ZIP reference-normalization ruling."""
import csv,io,json,re,subprocess
from pathlib import Path
from collections import Counter
P=Path(__file__).resolve().parent
R=P.parents[1]
BASE=(P/'base.txt').read_text().strip()
def read(p):return list(csv.DictReader(p.open(newline='')))
def write(p,rows,fields):
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
def baseline():
 return {p.name:list(csv.DictReader(io.StringIO(subprocess.check_output(['git','show',f'{BASE}:data/{p.name}'],text=True)))) for p in sorted((R/'data').glob('sites_*.csv'))}
def responses():
 rows=[r for p in sorted(P.glob('response_*.csv')) for r in csv.reader(p.open(newline=''))]
 assert len(rows)==5631 and len({r[0] for r in rows})==len(rows), 'response coverage/uniqueness'
 return {r[0]:r for r in rows}
def matched_zip(r):
 if r[2:4]!=['Match','Exact']:return None
 assert len(r)==12
 m=re.fullmatch(r'.*,\s*([0-9]{5})',r[4]);assert m, 'malformed Exact ZIP'
 return m[1]
def proposals(tables,res):
 frame={r['site_id']:r for n,rows in tables.items() if n!='sites_INTL.csv' for r in rows if r['street_address'].strip()}
 assert set(frame)==set(res), 'input yield'
 out=[];holds=[]
 for sid,r in frame.items():
  # A retained result is usable only for the same source address.
  assert res[sid][1]==', '.join(r[k] for k in ('street_address','city','state','zip')), ('input drift',sid)
  z=matched_zip(res[sid])
  if not r['zip'].strip():
   if z:out.append(dict(site_id=sid,zip=z,disposition='applied'))
   else:holds.append(dict(site_id=sid,result='/'.join(res[sid][2:4]),disposition='held',settling_fact='Unique Exact Census address result with a postal ZIP'))
 return out,holds
if __name__=='__main__':
 tables=baseline();res=responses();out,holds=proposals(tables,res);lookup={r['site_id']:r['zip'] for r in out}
 for name,old in tables.items():
  p=R/'data'/name;rows=read(p);dirty=False
  for r in rows:
   if r['site_id'] in lookup:
    z=lookup[r['site_id']];assert r['zip'] in ('',z), 'existing ZIP conflict'
    if r['zip']!=z:r['zip']=z;dirty=True
  if dirty:write(p,rows,list(rows[0]))
 write(P/'proposals.csv',out,['site_id','zip','disposition']);write(P/'holds.csv',holds,['site_id','result','disposition','settling_fact'])
 ids={r['site_id'] for r in out}
 stats=dict(frame=len(res),fills=len(out),holds=len(holds),tiers=dict(Counter(r['verification_tier'] for rows in tables.values() for r in rows if r['site_id'] in ids)))
 (P/'summary.json').write_text(json.dumps(stats,indent=2)+'\n');print(stats)
