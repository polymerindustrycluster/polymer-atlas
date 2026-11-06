from research import D
import csv,json,re,sys
rows=list(csv.DictReader((D/'frame.csv').open()))
for row in rows[int(sys.argv[1]):int(sys.argv[2])]:
 oid=row['org_id'];p=D/'raw'/oid/'routes.json';print('\n###',oid,row['legal_name'],'HQ',row['hq_city'])
 if not p.exists():continue
 for r in json.loads(p.read_text()):
  t=' '.join((D/r['raw_path']).read_text().split());print(r['kind'],r['source_ref'],r['http_status'],len(t))
  if r['availability']!='available':continue
  words=r'\b'+re.escape(row['hq_city'])+r'\b' if row['hq_city'] else 'NO-CITY-HELD'
  for m in list(re.finditer(words+'|manufactur|mold|extrud|compounding|formerly|Harwood|North America|Cleveland, L|USA Inc|Headquarters',t,re.I))[:14]:print(' ',t[max(0,m.start()-65):m.end()+130])
