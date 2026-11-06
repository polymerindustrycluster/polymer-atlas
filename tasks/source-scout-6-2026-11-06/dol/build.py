"""DOL OFLC LCA Disclosure Data FY2025 Q4 (cumulative FY2025; Wayback capture 20260114000337 because www.dol.gov returns 403 here) ->
(employer, worksite) frame for employer NAICS 3252/326, Certified cases, US worksite; seeded 20-unit sample matched to the Atlas.
Only employer / trade name / address / NAICS / worksite / status columns are ever read (xlsx_to_csv.py); no worker, attorney, preparer or POC fields.
Usage: python3 -I build.py   (reads PERSIST/dol/lca_fy2025_q4_kept.csv)"""
import csv,re,sys,hashlib,json,collections
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE.parent));import common
atlas=common.atlas
SRC=common.PERSIST/'dol'/'lca_fy2025_q4_kept.csv'
def in_slice(code):return bool(re.match(r'^(3252|326)\d*$',(code or '').strip()))
def zip5(v):
 m=re.match(r'^\s*(\d{4,5})',str(v or ''));return m.group(1).zfill(5) if m else ''
def main():
 for c in ['326199','3261','32629','325211']:assert in_slice(c),c
 for c in ['541511','332618','32519','3253','','611310']:assert not in_slice(c),c
 assert zip5('2134')=='02134' and zip5('44316-0001')=='44316' and zip5('')==''
 rows=0;slice_cases=0;cert=0;units={};employers=set()
 for r in csv.DictReader(open(SRC,newline='')):
  rows+=1
  if not in_slice(r['NAICS_CODE']):continue
  slice_cases+=1
  if r['CASE_STATUS']!='Certified' or r['WORKSITE_STATE'] not in atlas.USPS or not r['WORKSITE_ADDRESS1'].strip():continue
  cert+=1;employers.add(r['EMPLOYER_NAME'].strip().upper())
  street=r['WORKSITE_ADDRESS1'].strip();k=(atlas.name_key(r['EMPLOYER_NAME']),atlas.street_key(street),atlas.squash(r['WORKSITE_CITY']),r['WORKSITE_STATE'])
  d=units.setdefault(k,dict(employer_name=r['EMPLOYER_NAME'].strip(),trade_name=r['TRADE_NAME_DBA'].strip(),street=street,city=r['WORKSITE_CITY'].strip().title(),state=r['WORKSITE_STATE'],zip=zip5(r['WORKSITE_POSTAL_CODE']),
   employer_street=r['EMPLOYER_ADDRESS1'].strip(),employer_city=r['EMPLOYER_CITY'].strip().title(),employer_state=r['EMPLOYER_STATE'],employer_site_is_worksite=int(atlas.street_key(r['EMPLOYER_ADDRESS1'])==k[1]),naics=set(),certified_cases=0))
  d['naics'].add(r['NAICS_CODE'].strip());d['certified_cases']+=1
 frame=[]
 for k,d in units.items():
  d=dict(d,naics=';'.join(sorted(d['naics'])));d['unit_key']='|'.join(k);frame.append(d)
 frame.sort(key=lambda r:r['unit_key']);assert len(frame)==len({r['unit_key'] for r in frame})
 common.write_csv(HERE/'frame.csv',frame,['unit_key','employer_name','trade_name','street','city','state','zip','employer_street','employer_city','employer_state','employer_site_is_worksite','naics','certified_cases'])
 A=common.Atlas();out=[]
 for r in common.draw(frame,'unit_key'):
  m=A.match(r['employer_name'],r['street'],r['city'],r['state'],r['zip'])
  if r['trade_name']:
   m2=A.match(r['trade_name'],r['street'],r['city'],r['state'],r['zip']);m={k:';'.join(sorted(set(filter(None,(m[k]+';'+m2[k]).split(';'))))) for k in ('atlas_ids','site_hits','org_hits','registry_hits')}|{'duplicate_of':m['duplicate_of'] or m2['duplicate_of']}
  out.append(dict(r,**m))
 common.write_csv(HERE/'sample_pre.csv',out)
 stats=dict(data_rows=rows,naics_slice_cases=slice_cases,certified_us_worksite_slice_cases=cert,slice_employers=len(employers),frame_employer_worksite_units=len(frame),
  units_where_worksite_is_employer_address=sum(r['employer_site_is_worksite'] for r in frame),input_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest())
 (HERE/'counts.json').write_text(json.dumps(stats,indent=1)+'\n');print(stats)
if __name__=='__main__':main()
