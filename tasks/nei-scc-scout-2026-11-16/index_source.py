"""Stream Ohio rows from the downloaded Region 5 ZIP; discard national raw after indexing."""
import csv,io,json,zipfile,hashlib,urllib.request,zlib,struct
from pathlib import Path
P=Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/nei-scc-scout')
FIELDS=['eis facility id','tri facility id','site name','primary naics code','county','address','city','zip code','eis unit id','eis process id','scc','unit description','process description','calculation material','data tagged']
def main():
 if (P/'index_receipt.json').exists():return
 # The outer ZIP directory fixed this member range; fail if the member hash changes.
 if not (P/'r5.zip').exists():
  u='https://gaftp.epa.gov/air/nei/2023/data_summaries/2023nei_facility_process_byregion_21jul2026.zip'
  req=urllib.request.Request(u,headers={'Range':'bytes=28665921-57904414'})
  with urllib.request.urlopen(req,timeout=120) as response:
   assert response.status==206
   b=response.read(29238495)
  assert len(b)==29238494 and hashlib.sha256(b).hexdigest()=='5a9ee8467c5a675b8e1b038886048895c89142bdcd9545fd09700675fd3597fe'
  (P/'r5-range.bin').write_bytes(b);n,e=struct.unpack_from('<HH',b,26)
  (P/'r5.zip').write_bytes(zlib.decompress(b[30+n+e:],-15))
 rows=set();total=oh=0
 with zipfile.ZipFile(P/'r5.zip') as z:
  with z.open('emis_sum_proc_38215.csv') as f:
   for r in csv.DictReader(io.TextIOWrapper(f,encoding='utf-8-sig')):
    total+=1
    if r['state']!='OH':continue
    oh+=1;rows.add(tuple(r[k] for k in FIELDS))
 with (P/'ohio.csv').open('w') as f:
  w=csv.writer(f);w.writerow(FIELDS);w.writerows(sorted(rows))
 receipt=dict(region5_emission_rows=total,ohio_emission_rows=oh,ohio_distinct_projected_rows=len(rows),sha256=hashlib.sha256((P/'ohio.csv').read_bytes()).hexdigest(),range_sha256=hashlib.sha256((P/'r5-range.bin').read_bytes()).hexdigest(),range_bytes=(P/'r5-range.bin').stat().st_size,member='eis_report_38215_process_R5.zip',range='28665921-57904414',url='https://gaftp.epa.gov/air/nei/2023/data_summaries/2023nei_facility_process_byregion_21jul2026.zip')
 (P/'index_receipt.json').write_text(json.dumps(receipt,indent=2))
 for name in ('point.zip','r5.zip','r5-range.bin'):(P/name).unlink(missing_ok=True)
 print(receipt)
if __name__=='__main__':main()
