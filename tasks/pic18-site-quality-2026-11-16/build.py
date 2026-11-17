"""Idempotent, preflighted application; only the four authorized site columns may change."""
from prep import *
import argparse,hashlib
from site_corpus import on_page
from shard_io import append_sorted
ALLOWED={'verification_tier','last_verified','sources','notes'}
def plan(data=R/'data',task=H):
 inputs=read(task/'input.csv');vs=read(task/'verdicts.csv');witness=read(task/'witnesses.csv');new=read(task/'evidence.csv')
 assert len(inputs)==len(vs)==80 and len({v['site_id'] for v in vs})==80
 assert {s['site_id'] for s in inputs}=={v['site_id'] for v in vs}
 selected={v['site_id'] for v in vs if v['applied']=='yes'}
 assert selected=={w['site_id'] for w in witness}=={r['record_id'] for r in new}
 assert all(v['settling_fact'] and v['verdict']==('VERIFIED' if v['applied']=='yes' else 'STILL_UNCERTAIN') for v in vs)
 assert len({e['evidence_id'] for e in new})==len(new)
 assert all(379000<=int(e['evidence_id'][4:])<=380999 and e['tier_effect']=='supports_B' and e['record_table']=='sites' for e in new)
 for w in witness:
  text=Path(w['text_file']).read_text()
  assert hashlib.sha256(Path(w['text_file']).read_bytes()).hexdigest()==w['text_sha256']
  assert hashlib.sha256(Path(w['raw_file']).read_bytes()).hexdigest()==w['raw_sha256']
  assert on_page(w['quote'],text) and on_page(w['binding'],text)
  for e in new:
   if e['record_id']==w['site_id'] and e['source_class']=='own_site':assert e['source_ref']==w['url'] and e['claim_detail']==w['quote']
 ev=[r for p in data.glob('evidence_*.csv') for r in read(p)];byid={e['evidence_id']:e for e in ev};assert len(ev)==len(byid)
 pending=[]
 for e in new:
  if e['evidence_id'] in byid:assert byid[e['evidence_id']]==e
  else:pending.append(e)
 sites=read(data/'sites_OH.csv');by={s['site_id']:s for s in sites};updates={}
 for s in inputs:
  now=by[s['site_id']];assert all(now[k]==v for k,v in s.items() if k not in ALLOWED)
  if s['site_id'] not in selected:assert now==s;continue
  w=next(w for w in witness if w['site_id']==s['site_id'])
  target=dict(s,verification_tier='B',last_verified='2026-11-16',sources=s['sources']+';'+w['url'],notes=s['notes']+' | 2026-11-16 PIC-18 quality: seven must-have claims B+; banked ITA plus own-operator street/city/activity. Active status retained.')
  assert now in [s,target]
  rows=[e for e in ev if e['record_table']=='sites' and e['record_id']==s['site_id'] and e['evidence_id'] not in {x['evidence_id'] for x in new}]+[e for e in new if e['record_id']==s['site_id']]
  assert all(strength(rows,c) in ['A','B'] for c in CLAIMS)
  updates[s['site_id']]=target
 return [updates.get(s['site_id'],s) for s in sites],pending
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');a=ap.parse_args();sites,pending=plan()
 if a.apply:
  write(R/'data/sites_OH.csv',sites)
  if pending:append_sorted(R/'data/evidence_sites_OH.csv',pending,'evidence_id')
 print(json.dumps({'promotions':len(read(H/'witnesses.csv')),'new_evidence':len(pending)}))
