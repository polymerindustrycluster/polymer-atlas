from research import D
import json,re,sys,csv
rows=list(csv.DictReader((D/'frame.csv').open()))
for row in rows[int(sys.argv[1]):int(sys.argv[2])]:
 d=D/'raw'/row['org_id']; f=d/'routes.json'
 if not f.exists():continue
 print('\n###',row['org_id'],row['legal_name'])
 for r in json.loads(f.read_text()):
  t=(D/r['raw_path']).read_text(); print(r['source_ref'],r['http_status'],len(t))
  if r['kind'].startswith('sitemap'):continue
  hits=list(re.finditer(r'polyurethane|epoxy|natural rubber|injection mold|compression mold|fiberglass|polyethylene|polypropylene|polycarbonate|extrud|vinyl|resin|composit|thermoform|silicone|rubber|mold making|compounding|polystyrene|foaming|molding|moulding|coating|adhesive|acrylic|laminat|pultrus|additive|fabricat',t,re.I))
  for m in hits[:14]: print(' ',t[max(0,m.start()-75):m.end()+125].replace('\n',' '))
