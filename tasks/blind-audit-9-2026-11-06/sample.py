"""Predeclared lane×creation-tier stratified random draw, no source/evidence access."""
import csv,hashlib,json,random
from collections import Counter
from pathlib import Path
H=Path(__file__).resolve().parent
ALLOCATION={('L7-FL','C'):8,('L6-CA','C'):9,('L6-CA','B'):1,('L11-MI','C'):8,('L3-MO-SC-LA','B'):5,('L3-MO-SC-LA','C'):1,('L7-GA','C'):9,('L11-IL','C'):9}
SEED='BLIND-AUDIT-9-2026-11-06-v1'
def read(p):
 with open(p,newline='') as f:return list(csv.DictReader(f))
def draw(frame):
 assert len(frame)==len({r['site_id'] for r in frame})==110
 assert set(ALLOCATION)=={(r['lane'],r['creation_tier']) for r in frame}
 result=[]
 for (lane,tier),n in sorted(ALLOCATION.items()):
  candidates=sorted([r for r in frame if (r['lane'],r['creation_tier'])==(lane,tier)],key=lambda r:r['site_id'])
  rng=random.Random(int.from_bytes(hashlib.sha256((SEED+'|'+lane+'|'+tier).encode()).digest(),'big'))
  for r in sorted(rng.sample(candidates,n),key=lambda r:r['site_id']):result.append(dict(r,stratum_N=len(candidates),stratum_n=n,inclusion_probability=f'{n/len(candidates):.12f}'))
 assert len(result)==len({r['site_id'] for r in result})==50
 return result
def main():
 frame=read(H/'frame.csv');sample=draw(frame)
 for name,rows in [('sample.csv',sample)]+[(f'blind_{k}.csv',sample[i::3]) for i,k in enumerate('abc')]:
  with (H/name).open('w',newline='') as f:
   w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
 receipt={'seed':SEED,'rng':'Python Random seeded by SHA256(seed|lane|tier), sample sorted IDs per stratum','frame_sha256':hashlib.sha256((H/'frame.csv').read_bytes()).hexdigest(),'sample_sha256':hashlib.sha256((H/'sample.csv').read_bytes()).hexdigest(),'population':dict(Counter(r['creation_tier'] for r in frame)),'sample':dict(Counter(r['creation_tier'] for r in sample)),'blind_fields_withheld':['sources','notes','created_by','last_verified','evidence rows','original lane packets'],'frozen_utc':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()}
 (H/'draw.json').write_text(json.dumps(receipt,indent=2)+'\n');print(receipt)
if __name__=='__main__':main()
