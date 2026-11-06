#!/usr/bin/env python3
"""Assemble manually reviewed proposals; assert quote, vocab and frozen-frame coverage."""
from research import D,has
import csv,json,sys
from collections import Counter

def write(name,rows,cols):
 with (D/name).open('w') as f:
  w=csv.DictWriter(f,cols);w.writeheader();w.writerows(rows)
frame=list(csv.DictReader((D/'frame.csv').open())); ids={r['org_id'] for r in frame};assert len(ids)==len(frame)==68
v=json.loads((D.parents[2]/'docs/schema/vocab.json').read_text())['vocabularies']
routes=[]
for oid in sorted(ids):
 rr=json.loads((D/'raw'/oid/'routes.json').read_text());assert rr and any(r['kind']=='sitemap' for r in rr);assert any('product' in r['kind'] or r['kind']=='pdf' or 'capabilit' in r['source_ref'] or r['kind']=='sitemap_child' for r in rr)
 routes+=rr
packet=[]
for oid,field,value,quote,urlpart,reason in json.loads((D/'selections.json').read_text()):
 assert oid in ids; assert value in v[field.upper()]['values']
 matches=[r for r in routes if r['org_id']==oid and urlpart in r['source_ref'] and r['availability']=='available' and has((D/r['raw_path']).read_text(),quote)]
 assert matches,(oid,value,quote)
 r=matches[0];packet.append(dict(org_id=oid,field=field,value=value,quote=quote,source_ref=r['source_ref'],raw_path=r['raw_path'],reason=reason))
assert len(packet)==len({(r['org_id'],r['field'],r['value']) for r in packet})
assert not has((D/packet[0]['raw_path']).read_text(),'Mustee manufactures epoxy floor patches from natural rubber')
notes=json.loads((D/'holds.json').read_text()) if (D/'holds.json').exists() else {}
verdicts=[]
for row in frame:
 oid=row['org_id'];proposed=[r for r in packet if r['org_id']==oid];rr=[r for r in routes if r['org_id']==oid]
 if proposed: verdict='VERIFIED';fact='';reason='Explicit own-product or own-operation claim; '+ '; '.join(r['field']+'='+r['value'] for r in proposed)
 else:
  verdict='STILL_UNCERTAIN';fact='A retrievable own corporate product specification naming a §3.2 polymer material, or an explicit own §3.1 polymer-processing operation for '+row['legal_name']
  if oid=='ORG-001777': fact='An explicit primary DBA, owned-entity or merger bridge connecting American Consolidated Industries Inc to Anchor Industries Inc before attribution of Anchor capabilities'
  if oid=='ORG-000581': fact='An explicit own primary polymer material or extrusion-operation claim attributable to Speed North America, rather than SPEED Group generally'
  reason=notes.get(oid,'Own sitemap and product/capability routes exhausted without an explicit admissible polymer capability witness; unavailable routes establish availability only.')
 verdicts.append(dict(org_id=oid,legal_name=row['legal_name'],verdict=verdict,missing_fact=fact,reason=reason,route_count=len(rr)))
if '--check' in sys.argv:
 existing=list(csv.DictReader((D/'packet.csv').open()));assert existing==packet
 vv=list(csv.DictReader((D/'verdicts.csv').open()));assert len(vv)==68 and {r['org_id'] for r in vv}==ids
 assert all(r['verdict'] in {'VERIFIED','STILL_UNCERTAIN'} for r in vv)
 assert all(r['missing_fact'] for r in vv if r['verdict']=='STILL_UNCERTAIN')
 assert len(list(csv.DictReader((D/'routes.csv').open())))==len(routes)
else:
 write('packet.csv',packet,['org_id','field','value','quote','source_ref','raw_path','reason'])
 write('verdicts.csv',verdicts,['org_id','legal_name','verdict','missing_fact','reason','route_count'])
 write('routes.csv',routes,['org_id','kind','source_ref','final_url','http_status','availability','raw_path','error'])
print('PASS',len(frame),'unique frame organizations;',len(packet),'proposed field values;',dict(Counter(r['verdict'] for r in verdicts)), ';',len(routes),'logged attempts; wrong-quote negative PASS')
