"""Preflight the fixed append-only discovery packet before writing any shard."""
import argparse,csv,hashlib,json,sys,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from shard_io import append_sorted
P=Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/pic18-discovery-leads')
def read(p):
 with Path(p).open(newline='') as f:return list(csv.DictReader(f))
def plan(data):
 pending=[]
 for src,dest,key,pattern,lo,hi in [('creates_orgs.csv','organizations_OH.csv','org_id','organizations_*.csv',14100,14299),('creates_sites.csv','sites_OH.csv','site_id','sites_*.csv',20200,20399),('evidence_orgs.csv','evidence_organizations_OH.csv','evidence_id','evidence_*.csv',381000,383999),('evidence_sites.csv','evidence_sites_OH.csv','evidence_id','evidence_*.csv',381000,383999)]:
  existing={}
  for p in data.glob(pattern):
   for r in read(p):
    assert r[key] not in existing,'duplicate existing ID'
    existing[r[key]]=(p.name,r)
  rows=read(HERE/src);assert len(rows)==len({r[key] for r in rows}),'duplicate packet ID'
  header=next(csv.reader((data/dest).open()))
  for r in rows:
   assert set(r)==set(header),'header mismatch'
   assert lo<=int(r[key].split('-')[1])<=hi,'outside reservation'
   if r[key] in existing:assert existing[r[key]]==(dest,r),'ID collision or changed packet'
  pending.append((data/dest,key,[r for r in rows if r[key] not in existing]))
 return pending
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--apply',action='store_true');a.add_argument('--data-dir',type=Path,default=ROOT/'data');args=a.parse_args();pending=plan(args.data_dir)
 if args.apply:
  backup=P/'pre-pass';backup.mkdir(exist_ok=True)
  for p,k,rows in pending:
   if rows:
    if not (backup/p.name).exists():shutil.copyfile(p,backup/p.name)
    append_sorted(p,rows,k)
 print('pending rows:',sum(len(r) for _,_,r in pending))
