#!/usr/bin/env python3
"""Replay open L4 packets on an isolated current-main copy and measure raw T1."""
import argparse,csv,io,json,math,subprocess,sys,tarfile,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PACKETS=[('133','agent/codex/pic18-record-health','pic18-record-health-2026-11-06'),('146','agent/codex/pic18-record-health-2','pic18-record-health-2-2026-11-06'),('154','agent/codex/pic18-record-health-3','pic18-record-health-3-2026-11-06'),('172','agent/codex/pic18-record-health-4','pic18-record-health-4-2026-11-06'),('183','agent/codex/pic18-record-health-5','pic18-record-health-5-2026-11-06')]
def unpack(ref,paths,d):
 raw=subprocess.check_output(['git','archive',ref,*paths],cwd=ROOT)
 with tarfile.open(fileobj=io.BytesIO(raw)) as t:t.extractall(d,filter='data')
def run(args,cwd):
 r=subprocess.run([sys.executable,*map(str,args)],cwd=cwd,capture_output=True,text=True)
 assert r.returncode==0,(args,r.stdout[-1000:],r.stderr[-2000:])
 return r.stdout.strip()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--include-round6',action='store_true');ap.add_argument('--snapshot-dir',type=Path);a=ap.parse_args()
 mainref=subprocess.check_output(['git','rev-parse','origin/main'],text=True,cwd=ROOT).strip()
 with tempfile.TemporaryDirectory(prefix='atlas-l4-projection-') as td:
  d=Path(td);unpack(mainref,['data','scripts','docs/schema/vocab.json','tasks/record-fixes-2026-11-03','tasks/census-gap-people-2026-11-03'],d)
  history=[]
  def measure(label):
   out=d/'health.csv';run([HERE/'health.py','--data-dir',d/'data','--output',out],ROOT)
   rows=list(csv.DictReader(out.open()));healthy=sum(int(r['healthy']) for r in rows)
   history.append(dict(stage=label,healthy=healthy,total=len(rows),percent=round(100*healthy/len(rows),2),needed_for_90=math.ceil(.9*len(rows))-healthy))
  measure('current main '+mainref[:7])
  for pr,ref,folder in PACKETS:
   sha=subprocess.check_output(['git','rev-parse',ref],text=True,cwd=ROOT).strip();unpack(sha,['tasks/'+folder],d)
   run([d/'tasks'/folder/'build.py','--data-dir',d/'data'],d);measure('PR'+pr+' '+sha[:7])
  if a.include_round6:
   # Round6 packet is copied from this checkout so the projection also runs before its commit.
   import shutil
   target=d/'tasks'/HERE.name;shutil.copytree(HERE,target,ignore=shutil.ignore_patterns('__pycache__','raw'))
   run([target/'build.py','--data-dir',d/'data'],d);measure('round6 working packet')
  if a.snapshot_dir:
   import shutil
   assert not a.snapshot_dir.exists(), 'refuse snapshot overwrite'
   shutil.copytree(d/'data',a.snapshot_dir/'data')
   shutil.copy2(d/'health.csv',a.snapshot_dir/'health.csv')
  with (HERE/'projection.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=history[0],lineterminator='\n');w.writeheader();w.writerows(history)
  print(json.dumps(history,indent=2))
if __name__=='__main__':main()
