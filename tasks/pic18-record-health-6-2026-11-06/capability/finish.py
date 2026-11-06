"""Freeze reviewed proposals and complete every initial class-a attempt outcome."""
from inventory import D,norm
from research import has
import csv,json,re
from collections import Counter
initial=json.loads((D/'initial_classifications.json').read_text());discovery=json.loads((D/'discovery.json').read_text());prior={u for v in json.loads((D/'prior_routes.json').read_text()).values() for u in v};rr=[]
for p in (D/'raw').glob('*/routes.json'):
 if p.parent.name.startswith('ORG-'):rr+=json.loads(p.read_text())
packet=[]
for oid,field,value,q,part,notes in json.loads((D/'selections.json').read_text()):
 matches=[r for r in rr if r['org_id']==oid and part in r['attempted_url'] and r['availability']=='available' and norm(r['attempted_url']) not in prior and norm(r['final_url']) not in prior and has((D/r['raw_path']).read_text(),q)]
 assert matches,(oid,value,q)
 r=matches[0];packet.append(dict(org_id=oid,field=field,value=value,quote=q,source_ref=r['attempted_url'],raw_path=r['raw_path'],source_class='own_site',observed_date='2026-11-06',notes=notes+' Preliminary proposal only; no data/tier/status/ring/parent/EVD motion.'))
SPECIAL={
'ORG-000049':('c','New solution page still describes Prophene tire-performance benefits/proprietary compound, not explicit adopted chemistry or own polymer production. Need own qualifying controlled capability, not customer tire processing.'),
'ORG-000078':('c','Fresh G+D group reports discuss recycled PVC cards, but do not establish held America entity/operator attribution. Need exact America manufacturing/material claim; no group transfer.'),
'ORG-000389':('c','New introduction describes textile adhesion/release-agent business but does not repair prior Grok146 customer-fabric/resin-use boundary. Need explicit admissible own polymer operation/material, not customer nylon ownership.'),
'ORG-000401':('c','New 3D printing service route406/504 and partner brochure does not establish held own production operation; printer sales/partner/customer deployment excluded. Need own production service statement.'),
'ORG-000581':('c','New English pages still attribute extrusion to SPEED Group, with North America only in footer. Need North America-specific own operation; no group process transfer.'),
'ORG-000635':('b','Fresh own catalogs describe nylon-filament brushes but do not establish own filament making/converting. Owner resin-use/owned-manufactured-polymer-product boundary, or explicit own polymer conversion witness needed; no nylon component gain forced.'),
'ORG-001183':('c','New Flex-N-Gate group plastics page and European CSR concern group/European plants, not held Ventra operator. Need exact Ventra attributable polymer production statement.'),
'ORG-001459':('c','New own-hosted USCG approval can establish RFD Beaufort identity/liferaft approval, but liferaft alone does not name controlled material or own polymer process. Need RFD-specific production/material witness.'),
'ORG-001595':('b','Fresh own RIGID product describes injection-molded case, but own molding operator not explicit. Owner resin-use/product-process attribution boundary or explicit own operator production statement needed; no process gain forced.'),
'ORG-001648':('c','Fresh own barrier table explicitly lists HDPE/co-extrusion but operator/making-versus-purchased-tube boundary remains unresolved in inspected passage. Need explicit held Worthington manufacture/conversion of that polymer product; proposal withheld.'),
'ORG-001714':('d','New own AML information sheet explicitly describes graphite/water lubricants, molybdenum disulfide and boron nitride coatings, without polymer binder/formation. Positive inorganic formulation lead requires scope re-verification; no status/ring change.'),
'ORG-001891':('c','Fresh Inflatable Images page describes reinforced-vinyl arch printing, but held Scherba legal/operator attribution and owned polymer-conversion context not independently settled here. Need explicit held operator bridge/production statement; proposal withheld conservatively.'),
'ORG-001922':('c','New FAQ repeats nylon bearing rings, not explicit own nylon processing. Prior Grok133 purchased-component refutation remains; need own polymer conversion, not another purchased-material statement.'),
'ORG-002080':('c','New Mitsubishi group carbon-fiber/corporate pages do not identify held Performance Polymers Inc operations. Need exact held-entity compounding/material production, not group portfolio transfer.'),
'ORG-002153':('c','New Alpha clip/JewelLok PDFs describe plastic components without controlled resin identity or explicit own polymer process/operator. Need adopted own corporate capability, not generic purchased plastic component.')}
classes=[]
for base in initial:
 r=base.copy();oid=r['org_id'];own=[p for p in packet if p['org_id']==oid];routes=[x for x in rr if x['org_id']==oid]
 if r['class']=='a':
  d=discovery.get(oid);searchroute=r['source_route'];tried=[x['attempted_url'] for x in routes];r['attempted_url']='; '.join(dict.fromkeys([searchroute]+tried));r['source_date']='2026-11-06'
  if own:
   r['work_outcome']='VERIFIED';r['raw_quote_evidence']=' | '.join(p['field']+'='+p['value']+' :: '+p['quote']+' :: '+p['source_ref']+' :: '+p['raw_path'] for p in own);r['missing_fact']='';r['postwork_recommended_class']=''
  else:
   r['work_outcome']='STILL_UNCERTAIN';cl,why=SPECIAL.get(oid,('c',r['settling_fact']+' The named bounded search and any fresh source fetches did not settle this fact; reviewed route results are not proof of internet absence.'))
   r['postwork_recommended_class']=cl;r['missing_fact']=why
   if d:
    r['raw_quote_evidence']='Discovery '+d['search_file']+'; '+str(len(d['new_candidates']))+' novel candidate URLs; '+str(len(d['excluded_tried_urls']))+' previously tried result URLs excluded. '
   r['raw_quote_evidence']+= ' | '.join(x['attempted_url']+' :: '+x['http_status']+' '+x['availability']+' :: '+x['raw_path'] for x in routes)
  assert r['attempted_url'] and r['work_outcome']!='PENDING'
 classes.append(r)
# Search requests are route attempts too, separately labeled; no search summary is evidence.
searchrows=[]
for r in initial:
 if r['class']=='a' and r['org_id'] in discovery:
  x=discovery[r['org_id']];searchrows.append(dict(org_id=r['org_id'],kind='official_domain_search',attempted_url=x['query'],final_url='',http_status='',availability='discovery_only',raw_path=x['search_file'],observed_date='2026-11-06',notes=str(len(x['new_candidates']))+' new result URL candidates; '+str(len(x['excluded_tried_urls']))+' known tried URLs excluded before fetch; search text never source evidence.'))
def write(name,rows,cols):
 with (D/name).open('w') as f:
  w=csv.DictWriter(f,cols);w.writeheader();w.writerows(rows)
write('packet.csv',packet,['org_id','field','value','quote','source_ref','raw_path','source_class','observed_date','notes']);write('classification_routes.csv',classes,list(classes[0]));write('routes.csv',searchrows+rr,['org_id','kind','attempted_url','final_url','http_status','availability','raw_path','observed_date','notes'])
print('Initial',dict(Counter(r['class'] for r in classes)),'outcomes',dict(Counter(r['work_outcome'] for r in classes if r['class']=='a')),'packet',len(packet),'values/',len({r['org_id'] for r in packet}),'organizations','new fetches',len(rr),'searches',len(searchrows))
