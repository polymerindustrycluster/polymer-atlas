"""Paced FRS fetches using the already-proven first-pass helper, no canonical writes."""
import csv,importlib.util,json,time,sys
from pathlib import Path
TASK=Path(__file__).resolve().parent;ROOT=TASK.parents[1]
spec=importlib.util.spec_from_file_location('held_oh_address',ROOT/'tasks/oh-street-address-2026-11-06/build.py');frs=importlib.util.module_from_spec(spec);spec.loader.exec_module(frs);frs.TASK=TASK
read,write=frs.read,frs.write
def known():
 cases=[('110000745766','160 Parker Ct','Chardon','44024'),('110000391415','350 N Buckeye St','Bellevue','44811'),('110000383941','555 W Linfoot St','Wauseon','43567')]
 out=[]
 for rid,street,city,zip_ in cases:
  f=frs.facility(frs.fetch(rid,'known_raw'),rid)
  assert frs.streetkey(f['LocationAddress'])==frs.streetkey(street),(rid,f)
  assert frs.norm(f['CityName'])==frs.norm(city) and f['ZipCode'][:5]==zip_,f
  s=dict(city=city,zip=zip_,county=f['CountyName'])
  assert not frs.conflict(s,f)
  for field,value in [('city','WRONG CITY'),('zip','00000'),('county','WRONG COUNTY')]:assert frs.conflict(dict(s,**{field:value}),f)
  assert frs.conflict(s,dict(f,LocationAddress='PO BOX 99'))
  out.append(dict(registry_id=rid,expected_street=street,city=city,zip=zip_,result='PASS'));write(TASK/'known_answers.csv',out)
  print('KNOWN',rid,'PASS',flush=True);time.sleep(12)
 print('PASS3live known answers plus city/ZIP/county/PO-box mutations',flush=True)
def main():
 assert len(read(TASK/'known_answers.csv'))==3,'known gate incomplete'
 ids=sorted({r['registry_id'] for r in read(TASK/'registry_links_input.csv')});out=[]
 for rid in ids:
  try:
   if (TASK/'raw'/f'{rid}.json').exists():data=json.loads((TASK/'raw'/f'{rid}.json').read_text())
   else:data=frs.fetch(rid)
   f=frs.facility(data,rid);result='OK';error=''
  except Exception as ex:result='UNAVAILABLE';error=str(ex)
  out.append(dict(registry_id=rid,result=result,error=error));write(TASK/'fetch_log.csv',out)
  print(rid,result,error,flush=True);time.sleep(12)
 assert len(out)==len(ids)
 print('Fetch yield',len(out),'expected registry IDs',len(ids),'OK',sum(r['result']=='OK' for r in out),flush=True)
if __name__=='__main__':
 if '--known' in sys.argv:known()
 else:main()
