"""USAspending FY2025 contract recipients (US-located) with >=1 award procured under NAICS 3252/3261/3262 -> UEI frame; seeded 20-recipient sample with
SAM-registered address from the recipient profile, matched to the Atlas (UEI link first). NAICS here is the AWARD's code, not the recipient's.
Usage: python3 -I build.py   (reads PERSIST/usaspending/recipients_fy2025.jsonl written by fetch_recipients.py; fetches 20 recipient profiles)"""
import json,sys,time,hashlib,urllib.request
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE.parent));import common
D=common.PERSIST/'usaspending';API='https://api.usaspending.gov/api/v2'
def get(path):
 for i in range(4):
  try:return json.load(urllib.request.urlopen(urllib.request.Request(API+path,headers={'User-Agent':'polymer-atlas-source-scout-6'}),timeout=60))
  except Exception as e:time.sleep(2*(i+1));err=e
 raise SystemExit(f'{path}: {err}')
def post(path,body):
 for i in range(4):
  try:return json.load(urllib.request.urlopen(urllib.request.Request(API+path,json.dumps(body).encode(),{'Content-Type':'application/json','User-Agent':'polymer-atlas-source-scout-6'}),timeout=60))
  except Exception as e:time.sleep(2*(i+1));err=e
 raise SystemExit(f'{path}: {err}')
def location(r):
 """SAM-registered address of the recipient: profile by recipient_id, else the recipient location on one of its awards."""
 if r.get('recipient_id'):
  p=get(f"/recipient/{r['recipient_id']}/");(D/'profiles').mkdir(exist_ok=True);(D/'profiles'/f"{r['uei']}.json").write_text(json.dumps(p,sort_keys=True));l=p['location'] or {};return p['name'],l.get('address_line1') or '',l.get('city_name') or '',l.get('state_code') or '',l.get('zip') or '',(p.get('parent_name') or '')
 d=post('/search/spending_by_award/',{"filters":{"award_type_codes":["A","B","C","D"],"time_period":[{"start_date":"2024-10-01","end_date":"2025-09-30"}],"naics_codes":{"require":["3252","3261","3262"]},"recipient_search_text":[r['uei']]},"fields":["Recipient Name","Recipient UEI","Recipient Location"],"limit":1,"page":1})['results']
 l=d[0]['Recipient Location'] if d else {};return r['name'],l.get('address_line1') or '',l.get('city_name') or '',l.get('state_code') or '',(l.get('zip5') or ''),''
def main():
 rows=[json.loads(l) for l in open(D/'recipients_fy2025.jsonl')]
 assert len(rows)==len({r['uei'] for r in rows}) and all(r['uei'] and len(r['uei'])==12 for r in rows)
 frame=[dict(uei=r['uei'],name=r['name'].strip(),fy2025_contract_usd=round(r['amount'],2),has_profile=int(bool(r.get('recipient_id')))) for r in rows]
 common.write_csv(HERE/'frame.csv',sorted(frame,key=lambda r:r['uei']))
 byuei={r['uei']:r for r in rows};A=common.Atlas();out=[]
 for r in common.draw(frame,'uei'):
  name,street,city,state,zip_,parent=location(byuei[r['uei']]);time.sleep(0.5)
  m=A.match(name,street,city,state,zip_,registry=('UEI',r['uei']));out.append(dict(r,sam_name=name,street=street,city=city,state=state,zip=zip_,parent_name=parent,**m))
 common.write_csv(HERE/'sample_pre.csv',out)
 stats=dict(recipients=len(rows),usa_located_filter=True,awards_count_independent=32651,fy2025_contract_usd_total=round(sum(r['amount'] for r in rows),2),input_sha256=hashlib.sha256((D/'recipients_fy2025.jsonl').read_bytes()).hexdigest())
 (HERE/'counts.json').write_text(json.dumps(stats,indent=1)+'\n');print(stats)
if __name__=='__main__':main()
