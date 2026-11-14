# usage: mkdec.py out.csv spec...   spec: Mi:scope[:term][:quote]  or Pk(cands file idx):scope[:type:term][:quote] ; quote override with |
import csv,sys
M=list(csv.DictReader(open('cap_menu.csv')))
out=sys.argv[1]; cands=list(csv.DictReader(open(sys.argv[2]))); rows=[]
for spec in sys.argv[3:]:
    parts=spec.split('~')
    ref,scope=parts[0],parts[1]
    src=M[int(ref[1:])] if ref[0]=='M' else cands[int(ref[1:])]
    basis='menu' if ref[0]=='M' else 'narrative'
    ty,term=src['type'],src['term']
    if len(parts)>2 and parts[2]: ty,term=parts[2].split(':')
    q=parts[3] if len(parts)>3 and parts[3] else src['quote']
    if len(parts)>4 and parts[4]: basis=parts[4]
    rows.append(dict(site_id=src['site_id'],type=ty,term=term,scope=scope,basis=basis,url=src['url'],quote=q))
w=csv.DictWriter(open(out,'a'),fieldnames=['site_id','type','term','scope','basis','url','quote'],lineterminator='\n')
w.writerows(rows); print(len(rows))
