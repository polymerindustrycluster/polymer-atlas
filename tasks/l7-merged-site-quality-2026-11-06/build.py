"""Apply the frozen site-quality packet after all claim, source, field and ID preflights."""
import argparse,hashlib,json,sys
from collections import defaultdict
from pathlib import Path
from prep import read,write
from research import found
P=Path(__file__).resolve().parent;ROOT=P.parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from shard_io import append_sorted
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--data-dir',type=Path,default=ROOT/'data');a=ap.parse_args();data=a.data_dir
 before={r['site_id']:r for r in json.loads((P/'before.json').read_text())['sites']}
 frame=read(P/'input.csv');verdicts=read(P/'verdicts.csv');edits=read(P/'edits.csv');packet=read(P/'evidence_packet.csv')
 raw=read(P/'rawcheck.csv');witnesses={r['site_id']:r for r in read(P/'witnesses.csv')};eligibility={r['site_id']:r for r in read(P/'source_eligibility.csv')}
 assert len(frame)==len(verdicts)==len(before)==len({r['site_id'] for r in verdicts})==75
 assert set(before)=={r['site_id'] for r in frame}=={r['site_id'] for r in verdicts}
 upgraded={r['site_id'] for r in verdicts if r['verdict']=='VERIFIED'}
 assert len(upgraded)==31 and upgraded==set(witnesses)==set(eligibility)=={r['site_id'] for r in edits}
 assert all(r['verdict'] in {'VERIFIED','STILL_UNCERTAIN'} for r in verdicts)
 assert len(packet)==len({r['evidence_id'] for r in packet})==217
 assert all(207000<=int(r['evidence_id'][4:])<=209999 and r['record_id'] in upgraded for r in packet)
 assert {r['site_id'] for r in raw}==upgraded and len(raw)==31
 orgs={r['org_id']:r for p in data.glob('organizations_*.csv') for r in read(p)}
 for sid in upgraded:
  es=[r for r in packet if r['record_id']==sid]
  assert {r['claim_type'] for r in es}=={'existence','address','scope','code','parent','activity','liveness'} and len(es)==7,('must-have gap',sid)
  assert all(r['tier_effect']=='supports_B' for r in es)
  assert sum(r['source_class']=='own_site' and r['claim_type']=='scope' for r in es)==1
  r=next(r for r in raw if r['site_id']==sid);scope=next(e for e in es if e['claim_type']=='scope');w=witnesses[sid]
  text=Path(r['cache_file']).read_text()
  assert r['raw_check']=='PASS' and hashlib.sha256(Path(r['cache_file']).read_bytes()).hexdigest()==r['raw_sha256'],('raw receipt',sid)
  assert scope['claim_detail']==r['quote']==w['quote'] and scope['source_ref']==r['source_ref']==eligibility[sid]['source_ref']
  assert found(text,r['quote']) and found(text,w['location_anchor']),('raw quote/location',sid)
  o=orgs[before[sid]['org_id']];e=eligibility[sid]
  assert (o['parent_org_id'],o['ultimate_parent_name'])==(e['parent_org_id'],e['ultimate_parent_name']),('B-PARENT drift',sid)
  if sid in {'SITE-016502','SITE-016507'}:assert o['parent_org_id']=='ORG-002907','B-PARENT Amcor missing'
  if sid=='SITE-016110':assert o['ultimate_parent_name']=='Habasit AG','B-PARENT Habasit missing'
  if sid=='SITE-016109':assert found(text,'Copyright ©2024 by MAPEI Corporation'),'own-issued MAPEI publisher missing'
 owned=defaultdict(list)
 for sid in upgraded:owned[before[sid]['state']].append(sid)
 site_rows={state:read(data/f'sites_{state}.csv') for state in owned}
 byid={r['site_id']:r for rows in site_rows.values() for r in rows}
 held={}
 for p in data.glob('evidence_*.csv'):
  for e in read(p):
   assert e['evidence_id'] not in held,'existing duplicate evidence ID';held[e['evidence_id']]=(p.name,e)
 grouped=defaultdict(list)
 for e in packet:
  name=f"evidence_sites_{before[e['record_id']]['state']}.csv"
  if e['evidence_id'] in held:assert held[e['evidence_id']]==(name,e),('global evidence ID collision',e['evidence_id'])
  else:grouped[name].append(e)
 for e in edits:
  assert e['field'] in {'verification_tier','sources'} and e['old']==before[e['site_id']][e['field']]
  if e['field']=='verification_tier':assert (e['old'],e['new'])==('C','B')
  assert byid[e['site_id']][e['field']] in {e['old'],e['new']},('field drift',e['site_id'],e['field'])
 for sid in upgraded:
  expected=dict(before[sid]);actual=byid[sid]
  for e in edits:
   if e['site_id']==sid:expected[e['field']]=actual[e['field']]
  assert actual==expected,('unreviewed site field drift',sid)
 for e in edits:byid[e['site_id']][e['field']]=e['new']
 # Every source, claim, field drift and cross-shard ID is checked before any canonical write.
 for state,rows in site_rows.items():write(data/f'sites_{state}.csv',rows)
 for name,rows in grouped.items():append_sorted(data/name,rows,'evidence_id')
 print('PASS: 31 C→B sites / 62 cells / 217 append-only observations; complete B claims and source/ID preflights.')
if __name__=='__main__':main()
