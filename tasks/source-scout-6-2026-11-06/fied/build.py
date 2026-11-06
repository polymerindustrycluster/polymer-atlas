"""NREL FIED 2017 (CC BY 4.0) -> facility frame for primary NAICS 3252/3255/326 and a seeded 20-facility sample matched to the Atlas.
Usage: python3 -I build.py   (reads PERSIST/fied/foundational_industry_data_2017.csv)"""
import csv,re,sys,hashlib,json,collections,sqlite3
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE.parent));import common
SRC=common.PERSIST/'fied'/'foundational_industry_data_2017.csv'
FRS=Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/cache/bulk/frs.sqlite')  # T2 ECHO exporter cache
def naics(v):
 """'326199.0' -> '326199'. Empty or non-numeric -> ''."""
 try:return str(int(float(v)))
 except (TypeError,ValueError):return ''
def in_slice(code):return bool(re.match(r'^(3252|3255|326)\d*$',code or ''))
def zip5(v):
 try:return str(int(float(v))).zfill(5)
 except (TypeError,ValueError):return ''
def rid(v):
 try:return str(int(float(v)))
 except (TypeError,ValueError):return ''
def main():
 # known answers: slice boundaries and float-formatted codes
 for c in ['326199','325211','325510','32551','3261']:assert in_slice(c),c
 for c in ['332618','325199','32519','3253','','3325']:assert not in_slice(c),c
 assert naics('326199.0')=='326199' and naics('')=='' and naics('x')=='' and zip5('2134.0')=='02134'
 csv.field_size_limit(10**9);units=0;fac={};allfac=set()
 for r in csv.DictReader(open(SRC,newline='',encoding='utf-8',errors='replace')):
  units+=1;k=rid(r['registryID']);allfac.add(k)
  c=naics(r['naicsCode'])
  if not in_slice(c):continue
  d=fac.setdefault(k,dict(registry_id=k,name=r['name'].strip(),street=r['locationAddress'].strip(),city=r['cityName'].strip(),state=r['stateCode'].strip(),zip=zip5(r['postalCode']),county=r['countyName'].strip(),primary_naics=c,eis_facility_id=rid(r['eisFacilityID']),ghgrp_id=rid(r['ghgrpID']),unit_rows=0))
  d['unit_rows']+=1
 frame=sorted(fac.values(),key=lambda r:r['registry_id']);assert len(frame)==len({r['registry_id'] for r in frame})
 common.write_csv(common.PERSIST/'fied'/'frame_full.csv',frame)  # 20,834 rows with names/addresses stay in persist
 common.write_csv(HERE/'frame.csv',[{k:r[k] for k in ('registry_id','state','primary_naics')} for r in frame])  # committed: keys + state + NAICS only
 A=common.Atlas();out=[];db=sqlite3.connect(f'file:{FRS}?mode=ro',uri=True)
 for r in common.draw(frame,'registry_id'):
  row=db.execute('select payload from records where id=?',(r['registry_id'],)).fetchone();f=json.loads(row[0]) if row else {}
  r=dict(r,frs_name=f.get('FAC_NAME',''),frs_street=f.get('FAC_STREET',''),frs_active_flag=f.get('FAC_ACTIVE_FLAG',''))
  # FIED names are FRS abbreviations ('CHEML TECH RBR'); match on both the FIED and the full FRS name, street likewise
  m1=A.match(r['name'],r['street'],r['city'],r['state'],r['zip'],registry=('FRS',r['registry_id']))
  m2=A.match(r['frs_name'] or r['name'],r['frs_street'] or r['street'],r['city'],r['state'],r['zip'],registry=('FRS',r['registry_id']))
  m={k:';'.join(sorted(set(filter(None,(m1[k]+';'+m2[k]).split(';'))))) for k in ('atlas_ids','site_hits','org_hits','registry_hits')}
  m['duplicate_of']=m1['duplicate_of'] or m2['duplicate_of'];out.append(dict(r,**m))
 common.write_csv(HERE/'sample_pre.csv',out)
 stats=dict(unit_rows=units,facilities_all=len(allfac),slice_facilities=len(frame),slice_unit_rows=sum(r['unit_rows'] for r in frame),
  slice_naics_prefix_counts=dict(sorted(collections.Counter(re.match(r'3252|3255|326',r['primary_naics']).group(0) for r in frame).items())),input_sha256=hashlib.sha256(SRC.read_bytes()).hexdigest())
 (HERE/'counts.json').write_text(json.dumps(stats,indent=1)+'\n');print(stats)
if __name__=='__main__':main()
