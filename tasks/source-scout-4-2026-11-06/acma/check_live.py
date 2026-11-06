"""Reproduce public frame and seeded identities; no full roster/profile export."""
import csv,json,random,subprocess,tempfile
from pathlib import Path
from scout import frame
HERE=Path(__file__).parent
URL='https://acmanet.org/wp-json/mg/v1/content/directory?type=&state='
def main():
 with tempfile.TemporaryDirectory() as d:
  p=Path(d)/'list.json';status=subprocess.check_output(['curl','-LsS','--max-time','60','-A','Mozilla/5.0',URL,'-o',str(p),'-w','%{http_code}'],text=True)
  assert status=='200',f'route unavailable:HTTP{status}'
  source=json.loads(p.read_text());assert len(source)==len({r['recordId'] for r in source.values()})==252
  byname={r['name']:r for r in source.values()}
  for name,expected in [('3A Composites Core Materials','Supplier'),('AirTrac Transport LLC','Manufacturer'),('Abaris Training Resources, Inc. - Headquarters','Academic')]:assert byname[name]['organization-type']==expected
  rows=frame(source);assert len(rows)==98
  sample=random.Random(20261106).sample(rows,20);committed=list(csv.DictReader((HERE/'sample.csv').open()))
  assert [r['recordId'] for r in sample]==[r['record_id'] for r in committed]
  assert all(a['name']==b['name'] and (a['website'] or '')==b['website'] for a,b in zip(sample,committed))
 print('PASS:252 unique public listingIDs,98 scopedIDs,20 seeded identities;3 real category known answers')
if __name__=='__main__':main()
