"""Separate PBR fallback, never substituted for requested PTI/PTIO NAICS frame.
Input: official PermitbyRule.xlsx. Requires installed openpyxl, outputs task CSVs only.
"""
import csv,sys,re,json,hashlib,random
from pathlib import Path
from collections import defaultdict
import openpyxl
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'));import atlas
from regions import PIC18
HERE=Path(__file__).parent
PATTERN=re.compile(r'\b(polymer\w*|thermoplastic\w*|plastic\w*|rubber\w*|resin\w*|urethane\w*|composites?|extrus\w*|thermoform\w*)\b|injection.{0,12}mold',re.I)
URL='https://dam.assets.ohio.gov/raw/upload/v1719438323/epa.ohio.gov/Public/DAPC/PermitbyRule.xlsx'
FIELDS=['facility_id','effective_date','name','blank1','street','blank2','city','state','zip','county','regulator','received_date','unit_id','unit_description','pbr_type']
def write(name,rows):
 with (HERE/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 assert PATTERN.search('Thermoplastic molding operations') and PATTERN.search('MERCURY PLASTICS INC') and PATTERN.search('resin injection/compression molding')
 assert not PATTERN.search('Verizon emergency generator') and not PATTERN.search('Compositeur arts')
 source=Path(sys.argv[1]);w=openpyxl.load_workbook(source,read_only=True,data_only=True);it=iter(w.active.values)
 pre=[next(it) for _ in range(4)];assert pre[0]==('Active Permit By Rule List',)
 header=next(it);assert header[0]=='Facility Id' and header[14]=='PBR Type' and not any('NAICS' in str(v) for v in header)
 rows=[];blank=0
 for values in it:
  if not any(v is not None for v in values):blank+=1;continue
  assert len(values)==15 and values[0] and values[3] is None and values[5] is None
  rows.append({k:v.isoformat()[:10] if hasattr(v,'isoformat') else str(v or '') for k,v in zip(FIELDS,values)})
 assert len(rows)==19443 and blank==1
 for fid,name in [('02-28-00-0043','MERCURY PLASTICS INC'),('15-76-05-5084','AmbaFlex Manufacturing Inc.'),('16-77-01-0091','The University of Akron')]:
  known=[r for r in rows if r['facility_id']==fid];assert known and any(r['name']==name and PATTERN.search(r['name']+' '+r['unit_description']) for r in known)
 pic=[r for r in rows if r['county'] in PIC18];groups=defaultdict(list)
 for r in pic:
  if PATTERN.search(r['name']+' '+r['unit_description']):groups[r['facility_id']].append(r)
 tables=atlas.load_tables(ROOT/'data');out=[]
 for fid,rs in sorted(groups.items()):
  variants={(r['street'],r['city'],r['state'],r['zip']) for r in rs};assert len(variants)==1
  r=rs[0];ded=atlas.dedupe(tables,name=r['name'],street=r['street'],city=r['city'],state=r['state'],zip_=r['zip']);streetids={h['id'] for h in ded['steps'][2]['hits']};other={h['id'] for st in ded['steps'][:2]+ded['steps'][3:] for h in st['hits']}
  out.append(dict(facility_id=fid,name=';'.join(sorted({x['name'] for x in rs})),street=r['street'],city=r['city'],state=r['state'],zip=r['zip'],county=r['county'],unit_rows=len(rs),unit_ids=';'.join(sorted({x['unit_id'] for x in rs})),effective_dates=';'.join(sorted({x['effective_date'] for x in rs})),unit_descriptions=';'.join(sorted({x['unit_description'] for x in rs})),pbr_types=';'.join(sorted({x['pbr_type'] for x in rs})),site_hits=';'.join(sorted(streetids)),org_hits=';'.join(sorted(other)),source_url=URL,domain_check='no domain in workbook',naics_check='no NAICS in workbook; keyword fallback only',verdict='DUPLICATE_OF' if len(streetids)==1 else 'STILL_UNCERTAIN',duplicate_of=next(iter(streetids)) if len(streetids)==1 else '',verified_new=0,reason='singleton held site street/locality; reporting entry is not current operation' if len(streetids)==1 else 'settling fact: current polymer operator and site identity/address; PBR/name keywords are discovery only'))
 assert len(out)==len({r['facility_id'] for r in out})>=20
 write('pbr_frame.csv',out);sample=random.Random(20261106).sample(out,20);write('pbr_sample.csv',sample)
 stats=dict(input_unit_rows=len(rows),input_blank_rows=blank,ohio_facility_ids=len({r['facility_id'] for r in rows}),pic18_unit_rows=len(pic),pic18_facility_ids=len({r['facility_id'] for r in pic}),keyword_unit_rows=sum(r['unit_rows'] for r in out),keyword_facility_ids=len(out),report_generated=str(pre[2][0]),workbook_sha256=hashlib.sha256(source.read_bytes()).hexdigest())
 (HERE/'pbr_counts.json').write_text(json.dumps(stats,indent=2)+'\n');print(stats)
if __name__=='__main__':main()
