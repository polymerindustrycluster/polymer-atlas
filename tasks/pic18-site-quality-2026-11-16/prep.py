import csv,json,sys,subprocess
from pathlib import Path
from collections import defaultdict
H=Path(__file__).resolve().parent; R=H.parents[1];sys.path.insert(0,str(R/'scripts'))
from regions import PIC18
CLAIMS=sorted(['existence','address','scope','code','parent','activity','liveness'])
def read(p):
 with open(p,newline='') as f:return list(csv.DictReader(f))
def write(p,rows):
 with open(p,'w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def strength(rows,c):
 rs=[r for r in rows if r['claim_type']==c];s=[r for r in rs if r['tier_effect'].startswith('supports_')]
 if any(r['tier_effect']=='contradicts' and r['observed_date']>=max((x['observed_date'] for x in s),default='') for r in rs):return 'contradicted'
 return max((r['tier_effect'][-1] for r in s),key=lambda x: {'U':0,'C':1,'B':2,'A':3}[x],default='missing')
def rank(sites,ev):
 by=defaultdict(list)
 for r in ev:
  if r['record_table']=='sites':by[r['record_id']].append(r)
 out=[]
 for s in sites:
  if s['county'] in PIC18 and s['verification_tier']=='C' and s['operating_status']=='active':
   st={c:strength(by[s['site_id']],c) for c in CLAIMS}
   out.append(dict(site_id=s['site_id'],site_name=s['site_name'],org_id=s['org_id'],below_B=sum(v not in ['A','B'] for v in st.values()),**st))
 return sorted(out,key=lambda x:(x['below_B'],x['site_id']))
if __name__=='__main__':
 frame=rank(read(R/'data/sites_OH.csv'),[r for p in (R/'data').glob('evidence_*.csv') for r in read(p)])
 write(H/'ranking.csv',frame);write(H/'input.csv',[s for r in frame[:80] for s in read(R/'data/sites_OH.csv') if s['site_id']==r['site_id']])
 (H/'baseline.json').write_text(json.dumps({'base':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()}))
 print(len(frame));print('\n'.join(str(x) for x in frame[:80]))
