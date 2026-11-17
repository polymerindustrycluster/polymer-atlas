import csv,sqlite3,sys,re,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];TASK=Path(__file__).resolve().parent
S=Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist')
sys.path.insert(0,str(ROOT/'scripts'))
from regions import PIC18
from atlas import street_key

def read(p):return list(csv.DictReader(open(p)))
def write(p,rows):
 with open(p,'w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def norm(s):return re.sub(r'[^a-z0-9]','',s.lower())
def main():
 sites=read(ROOT/'data/sites_OH.csv');frame=[s for s in sites if s['county'] in PIC18 and s['operating_status']=='active' and s['verification_tier'] in 'ABC' and not s['street_address']]
 leads={s['site_id']:[] for s in frame}
 for r in read(S/'ppp-loan-scout/matches.csv'):
  if r['site_id'] in leads:leads[r['site_id']].append(('PPP',re.sub(r'\s+0\.0$','',r['BorrowerAddress'])))
 db=sqlite3.connect(S/'sam-entity-scout/sam.sqlite')
 for sid,street in db.execute("select m.record_id,s.street from matches m join sam s using(uei) where m.class='name+city'"):
  if sid in leads:leads[sid].append(('SAM',street))
 frame=[s for s in frame if leads[s['site_id']]];write(TASK/'frame.csv',frame)
 lr=[dict(site_id=s['site_id'],lead_class=c,street=a) for s in frame for c,a in sorted(set(leads[s['site_id']]))];write(TASK/'leads.csv',lr)
 corpus=read(S/'pic18-corpus-2026-11-16/manifest.csv');out=[]
 for s in frame:
  for m in corpus:
   if m['org_id']!=s['org_id'] or not m['text_file']:continue
   p=Path(m['text_file']);p=p if p.is_absolute() else S/'pic18-corpus-2026-11-16'/p
   t=re.sub(r'\s+',' ',p.read_text())
   for c,a in leads[s['site_id']]:
    num=re.match(r'\d+\b',a)
    if not num:continue
    for match in re.finditer(r'\b'+num[0]+r'\b',t):
     q=t[max(0,match.start()-70):match.start()+230]
     if norm(s['city']) in norm(q):out.append(dict(site_id=s['site_id'],lead=a,url=m['url'],text_file=str(p),raw_file=m['raw_file'],sha256=m['sha256'],context=q))
 write(S/'pic18-street-leads/candidates.csv',out)
 print('frame',len(frame),'leads',len(lr),'candidates',len(out))
if __name__=='__main__':main()
