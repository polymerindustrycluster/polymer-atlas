#!/usr/bin/env python3
"""Publish the held-only frozen quality packet; never writes canonical data."""
import csv,json,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[1]
def read(p):
 with open(p,newline='') as f:return list(csv.DictReader(f))
def validate(frame,verdicts):
 assert len(frame)==len(verdicts)==1 and {r['site_id'] for r in frame}=={r['site_id'] for r in verdicts}=={'SITE-012001'}
 assert all(r['verdict']=='STILL_UNCERTAIN' and r['reason'] for r in verdicts),'all five B claims unresolved'
 assert frame[0]['verification_tier']=='C' and not frame[0]['naics_primary'],'unexpected frozen site'
def main():
 frame=read(H/'input.csv');holds=read(H/'holds.csv');validate(frame,holds)
 with (H/'verdicts.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(holds[0]),lineterminator='\n');w.writeheader();w.writerows(holds)
 print(json.dumps({'merged_C_sites':1,'promoted':0,'holds':1,'canonical_edits':0,'new_evidence':0}))
if __name__=='__main__':main()
