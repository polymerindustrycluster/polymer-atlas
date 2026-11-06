"""Public CDR source frame and packet only; no canonical writes or inferred CBI."""
import csv,sys,re,json,random,hashlib,io
from pathlib import Path
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'));import atlas
HERE=Path(__file__).parent
URL='https://www.epa.gov/system/files/other-files/2026-04/2024-cdr-public-csv-data.zip'
FIELDS=['SITE NAME','SITE ADDRESS LINE1','SITE ADDRESS LINE2','SITE CITY','SITE STATE','SITE POSTAL CODE','STANDARDIZED PARENT COMPANY NAME']

def in_slice(r):
 return any(re.match(r'^(3252\d{2}|326\d{3})\b',r.get('SITE NAICS CODE '+str(i),'') or '') for i in (1,2,3))

def write(name,rows):
 with (HERE/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)

def main():
 # Known NAICS boundaries; descriptions or incidental digits must not qualify.
 assert in_slice({'SITE NAICS CODE 1':'325211 Plastics Material and Resin Manufacturing'})
 assert in_slice({'SITE NAICS CODE 2':'326299 All Other Rubber Product Manufacturing'})
 assert in_slice({'SITE NAICS CODE 3':'326199 All Other Plastics Product Manufacturing'})
 for value in ['325199 All Other Basic Organic Chemical Manufacturing','CBI','NKRA','999999 polymer326199','332618 Other Fabricated Wire Product Manufacturing','']:
  assert not in_slice({'SITE NAICS CODE 1':value})
 raw=Path(sys.argv[1]).read_bytes();text=raw.decode('cp1252');rows=list(csv.DictReader(io.StringIO(text)));assert len(rows)==50433
 # Compare the independent primary CSV parser yield with recorded DuckDB census.
 groups=defaultdict(list)
 for r in rows:
  if in_slice(r):
   assert r['EPA-TSCA PROGRAM ID'].strip();groups[r['EPA-TSCA PROGRAM ID']].append(r)
 frame=[]
 for sid,records in sorted(groups.items()):
  d={'tsca_site_id':sid}
  for field in FIELDS:d[field.lower().replace(' ','_')]=';'.join(sorted({r[field].strip() for r in records if r[field].strip()}))
  d['reported_naics']=';'.join(sorted({r['SITE NAICS CODE '+str(i)] for r in records for i in (1,2,3) if r['SITE NAICS CODE '+str(i)]}))
  d['reported_activities']=';'.join(sorted({r['ACTIVITY'] for r in records if r['ACTIVITY']}));d['never_at_site_values']=';'.join(sorted({r['CHEM NEVER AT SITE'] for r in records if r['CHEM NEVER AT SITE']}))
  d['chemical_reporting_rows']=len(records);d['address_variants']=len({(r['SITE ADDRESS LINE1'],r['SITE CITY'],r['SITE STATE'],r['SITE POSTAL CODE']) for r in records});frame.append(d)
 assert len(frame)==len({r['tsca_site_id'] for r in frame})==290
 write('frame.csv',frame)
 tables=atlas.load_tables(ROOT/'data');sample=[]
 for r in random.Random(20261106).sample(frame,20):
  d=atlas.dedupe(tables,name=r['site_name'],street=r['site_address_line1'] if r['address_variants']==1 else None,city=r['site_city'],state=r['site_state'],zip_=r['site_postal_code'])
  hits={h['id'] for st in d['steps'] for h in st['hits']};exact={h['id'] for h in d['steps'][2]['hits'] if h['id'].startswith('SITE-')}
  verdict='DUPLICATE_OF' if len(exact)==1 else 'STILL_UNCERTAIN'
  sample.append(dict(r,atlas_ids=';'.join(sorted(hits)),verdict=verdict,duplicate_of=next(iter(exact)) if len(exact)==1 else '',verified_new=0,domain_check='not supplied in CDR site file',source_url=URL,source_vintage='2023',reason='held site/organization exact name or street candidate; dated report is not current operating status' if len(exact)==1 else 'settling fact: own-site current polymer process, operator identity and physical-site address; government reporting code/import address alone insufficient'))
 write('sample.csv',sample)
 stats=dict(input_chemical_reporting_rows=len(rows),all_tsca_site_ids=len({r['EPA-TSCA PROGRAM ID'] for r in rows if r['EPA-TSCA PROGRAM ID']}),slice_tsca_site_ids=len(frame),slice_chemical_reporting_rows=sum(r['chemical_reporting_rows'] for r in frame),input_sha256=hashlib.sha256(raw).hexdigest())
 (HERE/'counts.json').write_text(json.dumps(stats,indent=2)+'\n');print(stats)
if __name__=='__main__':main()
