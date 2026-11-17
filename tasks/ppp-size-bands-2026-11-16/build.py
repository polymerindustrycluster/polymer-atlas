"""Owner-authorized blank-only historical PPP bands; reproducible from pre-pass shards."""
import argparse,csv,hashlib,io,json,subprocess,sys
from collections import defaultdict,Counter
from datetime import datetime
from decimal import Decimal,InvalidOperation
from pathlib import Path
D=Path(__file__).resolve().parent;ROOT=D.parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import atlas
from regions import PIC18
from build_form5500_spine import band_of,BANDS
from shard_io import append_sorted
P=Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/ppp-size-bands')
SOURCE=P.parent/'ppp-loan-scout';BASE=json.loads((D/'base.json').read_text())['base']
FIELDS={'organizations':'employee_band_ohio','sites':'employee_band_site'}
KEYS={'organizations':'org_id','sites':'site_id'}
ORDER=[b[2] for b in BANDS]+['5000+']
ALLOWED={'Corporation','Subchapter S Corporation','Limited  Liability Company(LLC)','Partnership','Limited Liability Partnership'}

def read(p):return list(csv.DictReader(p.open(newline='')))
def write(p,rows,fields):
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
def band(value):
 try:n=Decimal(value)
 except InvalidOperation:return ''
 return band_of(int(n)) if n.is_finite() and n>=1 and n==n.to_integral_value() else ''
def loan_date(r):return datetime.strptime(r['DateApproved'],'%m/%d/%Y').date().isoformat()
def safe(r):return r['BusinessType'] in ALLOWED and r['BorrowerName'].strip().upper() not in {'','N/A','NOT AVAILABLE','EXEMPTION 6'}
def loans():
 out=[]
 for m in json.loads((D/'source_manifest.json').read_text()):
  p=SOURCE/(m['file']+'.filtered.csv');assert hashlib.sha256(p.read_bytes()).hexdigest()==m['filtered_sha256']
  rr=read(p);assert len(rr)==m['counts']['retained'];out.extend(dict(r,source_url=m['url'],source_sha256=m['sha256']) for r in rr)
 assert len(out)==1953 and len({r['LoanNumber'] for r in out})==1953
 assert all(safe(r) for r in out)
 return out

def plan(data):
 orgs={r['org_id']:r for p in data.glob('organizations_*.csv') for r in read(p)}
 sites=[r for p in data.glob('sites_*.csv') for r in read(p)]
 assert len({s['site_id'] for s in sites})==len(sites)
 byorg=defaultdict(list)
 for s in sites:byorg[s['org_id']].append(s)
 name_index=defaultdict(set)
 for oid,o in orgs.items():
  for field,n in atlas.org_name_fields(o):
   if atlas.name_key(n):name_index[atlas.name_key(n)].add(oid)
 strict=defaultdict(list);held=[]
 for r in loans():
  if not band(r['JobsReported']):continue
  for oid in sorted(name_index[atlas.name_key(r['BorrowerName'])]):
   ss=byorg[oid];active=[s for s in ss if s['operating_status']=='active']
   if len(active)!=1 or any(s['state']!='OH' or s['country'] not in ('','US','USA') for s in ss):continue
   s=active[0]
   if s['county'] not in PIC18 or s['city'].casefold()!=r['BorrowerCity'].casefold():continue
   if not s['street_address'] or not r['BorrowerAddress'] or atlas.street_key(s['street_address'])!=atlas.street_key(r['BorrowerAddress']):
    held.append(dict(org_id=oid,site_id=s['site_id'],loan_id=r['LoanNumber'],reason='active-site street missing or not equal'));continue
   strict[oid].append((s,r))
 approved={(u['record_table'],u['record_id']):u for u in read(D/'approved_fills.csv')}
 fills=[];evs=[]
 for oid,pairs in sorted(strict.items()):
  s,r=max(pairs,key=lambda pair:(loan_date(pair[1]),pair[1]['LoanNumber']))
  for table,record in [('organizations',orgs[oid]),('sites',s)]:
   if record[FIELDS[table]].strip():continue
   rid=record[KEYS[table]]
   if (table,rid) not in approved:continue
   allocation=approved[(table,rid)]
   assert allocation['new']==band(r['JobsReported']) and allocation['loan_id']==r['LoanNumber'],'approved proposal changed'
   eid=int(allocation['evidence_id'][4:])
   # Scope only permits the Ohio organization shard; never move or silently write another shard.
   if table=='organizations' and oid not in {o['org_id'] for o in read(data/'organizations_OH.csv')}:
    held.append(dict(org_id=oid,site_id=s['site_id'],loan_id=r['LoanNumber'],reason='organization outside authorized OH shard'));continue
   assert eid<=376999
   effect='supports_U' if record['verification_tier']=='U' else 'supports_B'
   ev=dict(evidence_id=f'EVD-{eid:06d}',record_table=table,record_id=rid,claim_type='size_band',
    claim_detail=f'{FIELDS[table]}={band(r["JobsReported"])}; SBA PPP BorrowerName="{r["BorrowerName"]}"; BorrowerAddress="{r["BorrowerAddress"]}"; BorrowerCity="{r["BorrowerCity"]}"; JobsReported="{r["JobsReported"]}"; DateApproved="{r["DateApproved"]}"; historical {loan_date(r)[:4]} borrower-reported employment figure, band only',
    source_class='government_filing',source_ref=f'{r["source_url"]} (SBA PPP LoanNumber {r["LoanNumber"]})',observed_date=loan_date(r),tier_effect=effect,
    created_by='codex ppp-size-bands-2026-11-16',notes=f'Owner John Swanson B-PPP 2026-11-16: Strict matches; historical {loan_date(r)[:4]} loan approval date {loan_date(r)}; employment reference period unspecified; retrieved 2026-11-16; release 2024-09-30; source SHA256 {r["source_sha256"]}; exact normalized legal/trade/recorded former name + active-site street key + city; single active site, all held sites Ohio; blank-only fill')
   fills.append(dict(record_table=table,record_id=rid,field=FIELDS[table],old='',new=band(r['JobsReported']),org_id=oid,site_id=s['site_id'],loan_id=r['LoanNumber'],borrower_name=r['BorrowerName'],jobs_reported=r['JobsReported'],loan_date=loan_date(r),evidence_id=ev['evidence_id']))
   evs.append(ev)
 return fills,evs,held,len(strict)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--apply',action='store_true');a=ap.parse_args()
 data=P/'pre-pass';fills,evs,held,n=plan(data)
 write(D/'fills.csv',fills,list(fills[0]));write(D/'evidence_rows.csv',evs,list(evs[0]));write(D/'holds.csv',held,['org_id','site_id','loan_id','reason'])
 (D/'counts.json').write_text(json.dumps(dict(base=BASE,strict_organizations=n,fills=dict(Counter(r['record_table'] for r in fills)),evidence_rows=len(evs),held_loan_org_pairs=len(held),loan_years=dict(Counter(r['loan_date'][:4] for r in fills))),indent=2)+'\n')
 if a.apply:
  existing={e['evidence_id']:e for p in (ROOT/'data').glob('evidence_*.csv') for e in read(p)}
  for e in evs:
   if e['evidence_id'] in existing:assert existing[e['evidence_id']]==e,'evidence ID collision'
  for table in FIELDS:
   target=ROOT/'data'/f'{table}_OH.csv';rows=read(target);updates={r['record_id']:r for r in fills if r['record_table']==table}
   for r in rows:
    if r[KEYS[table]] in updates:
     u=updates[r[KEYS[table]]];assert r[FIELDS[table]]=='' or (r[FIELDS[table]]==u['new'] and u['evidence_id'] in existing),'refuse existing band without this pass evidence'
     r[FIELDS[table]]=u['new']
   write(target,rows,list(rows[0]))
   ep=ROOT/'data'/f'evidence_{table}_OH.csv';have={r['evidence_id']:r for r in read(ep)}
   new=[r for r in evs if r['record_table']==table]
   for r in new:
    if r['evidence_id'] in have:assert have[r['evidence_id']]==r
   append_sorted(ep,[r for r in new if r['evidence_id'] not in have],'evidence_id')
 print(json.dumps(json.loads((D/'counts.json').read_text())))
if __name__=='__main__':main()
