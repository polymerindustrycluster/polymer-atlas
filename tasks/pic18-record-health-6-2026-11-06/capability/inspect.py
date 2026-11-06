from research import D
import json,re,sys
rows=[r for r in json.loads((D/'initial_classifications.json').read_text()) if r['class']=='a']
for row in rows[int(sys.argv[1]):int(sys.argv[2])]:
 oid=row['org_id'];p=D/'raw'/oid/'routes.json'
 if not p.exists():continue
 print('\n###',oid)
 for r in json.loads(p.read_text()):
  t=' '.join((D/r['raw_path']).read_text().split());print(r['attempted_url'],r['http_status'],len(t))
  if r['availability']!='available':continue
  terms=r'polyurethane|polyethylene|polypropylene|polyvinyl|nylon|silicone|EPDM|extrud|injection mold|compression mold|thermoform|laminat|rubber|fiberglass|epoxy|compounding|Addipel|Performance Elastomers|North America|Wooster|Prophene|Faull|Lauren|PVC'
  for m in list(re.finditer(terms,t,re.I))[:14]:print(' ',t[max(0,m.start()-70):m.end()+145])
