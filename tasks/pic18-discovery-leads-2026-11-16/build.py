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
 # Refuted creation IDs remain retired; this packet must never reapply them.
 for src in ('creates_orgs.csv','creates_sites.csv','evidence_orgs.csv','evidence_sites.csv'):
  assert not read(HERE/src), 'withdrawn create must remain empty'
 retired={r['record_id'] for r in read(HERE/'retired_ids.csv')}
 for pattern,key in [('organizations_*.csv','org_id'),('sites_*.csv','site_id'),('evidence_*.csv','evidence_id')]:
  assert not any(r[key] in retired for p in data.glob(pattern) for r in read(p)), 'retired ID in canonical data'
 return []
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--apply',action='store_true');a.add_argument('--data-dir',type=Path,default=ROOT/'data');args=a.parse_args();pending=plan(args.data_dir)
 if args.apply:
  backup=P/'pre-pass';backup.mkdir(exist_ok=True)
  for p,k,rows in pending:
   if rows:
    if not (backup/p.name).exists():shutil.copyfile(p,backup/p.name)
    append_sorted(p,rows,k)
 print('pending rows:',sum(len(r) for _,_,r in pending))
