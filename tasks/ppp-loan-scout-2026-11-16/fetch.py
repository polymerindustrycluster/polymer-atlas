"""Stream official release; never persist unfiltered raw borrower rows."""
import csv,hashlib,io,json,sys,urllib.request,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import atlas
import socket
_original_getaddrinfo=socket.getaddrinfo
def resolve(host,*args,**kwargs):
 try:return _original_getaddrinfo(host,*args,**kwargs)
 except socket.gaierror:
  if host!="data.sba.gov":raise
  with urllib.request.urlopen("https://dns.google/resolve?name=data.sba.gov&type=A",timeout=30) as f:
   answer=json.load(f)
  ip=next(a["data"] for a in answer["Answer"] if a["type"]==1)
  return _original_getaddrinfo(ip,*args,**kwargs)
socket.getaddrinfo=resolve
P=Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/ppp-loan-scout');P.mkdir(parents=True,exist_ok=True)
BASE='https://data.sba.gov/sites/default/files/distribution/SBA-OCA-2022-07-001/'
FIELDS='LoanNumber DateApproved BorrowerName BorrowerAddress BorrowerCity BorrowerState BorrowerZip ProjectCountyName JobsReported NAICSCode BusinessType'.split()
def norm(s):return re.sub(r'\b(inc|incorporated|llc|corp|corporation|co|company|the)\b','',re.sub('[^a-z0-9 ]',' ',s.lower())).strip()
def safe(r):
 return r['BusinessType'] in {'Corporation','Subchapter S Corporation','Limited  Liability Company(LLC)','Partnership','Limited Liability Partnership'} and r['BorrowerName'].strip().upper() not in {'','NOT AVAILABLE','EXEMPTION 6','N/A'}
def main():
 names=set()
 for f in (ROOT/'data').glob('organizations_*.csv'):
  for r in csv.DictReader(f.open()):names.add(norm(r['legal_name']));names.update(norm(x) for x in r['trade_names'].split(';') if x)
 receipts=[]
 for name in ['public_150k_plus_240930.csv','public_up_to_150k_9_240930.csv']:
  receipt=P/(name+'.json');out=P/(name+'.filtered.csv')
  if receipt.exists():receipts.append(json.loads(receipt.read_text()));continue
  h=hashlib.sha256();counts={'rows':0,'ohio':0,'privacy_excluded_ohio':0,'retained':0};size=0
  # Hash bytes while CSV consumes lines, including embedded quoted newlines.
  with urllib.request.urlopen(BASE+name,timeout=120) as response,out.open('w',newline='') as dest:
   assert response.status==200,response.status
   def lines():
    nonlocal size
    for b in response:
     h.update(b);size+=len(b);yield b.decode('cp1252')
   w=csv.DictWriter(dest,fieldnames=FIELDS,lineterminator='\n');w.writeheader()
   for r in csv.DictReader(lines()):
    counts['rows']+=1
    if r['BorrowerState']!='OH':continue
    counts['ohio']+=1
    if not safe(r):counts['privacy_excluded_ohio']+=1;continue
    if not (r['NAICSCode'].startswith(('325','326')) or norm(r['BorrowerName']) in names):continue
    w.writerow({k:r[k] for k in FIELDS});counts['retained']+=1
  rec=dict(file=name,url=BASE+name,release='2024-09-30',retrieved='2026-11-16',sha256=h.hexdigest(),bytes=size,counts=counts,filtered_sha256=hashlib.sha256(out.read_bytes()).hexdigest())
  receipt.write_text(json.dumps(rec,indent=2)+'\n');receipts.append(rec);print(json.dumps(rec),flush=True)
 (P/'manifest.json').write_text(json.dumps(receipts,indent=2)+'\n')
 assert sum(f.stat().st_size for f in P.glob('*'))<500_000_000
if __name__=='__main__':main()
