"""Rebuild held NEI scout packet from pinned Ohio and SCC indexes; never writes data/."""
import csv,sys,json,random,re,hashlib
from pathlib import Path
from collections import defaultdict
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'scripts'));from atlas import street_key
from regions import PIC18
P=Path('/Users/johnswanson/.bb/thread-storage/thr_9i2c6byhcz/2026-11-06-atlas/persist/nei-scc-scout')
SEED=20261116

def read(p):return list(csv.DictReader(p.open()))
def write(name,rows):
 assert rows,name
 with (HERE/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def relevant(r):
 s=' '.join(r.get(k,'') for k in ['scc level two','scc level three','scc level four']).lower()
 return r['data category']=='Point' and bool(re.search(r'\b(plastics?|rubber|resins?|polymers?|adhesive|ink)\b',s) or ('surface coating operations' in s and re.search(r'coating operation|coat application|coating application|coat operation|finish coating|coating line|coat, spray|coat, dip',s)))
def proposal(r):
 s=r['scc level four'].lower();cat=r['scc level three'].lower();tags=[]
 exact={'30801002':'extrusion_unspecified','30801007':'molding_unspecified','30801008':'calendering','30800772':'composites_pultrusion','30800111':'rubber_mixing_compounding','30800113':'rubber_extrusion','30800115':'rubber_calendering','30101809':'extrusion_unspecified'}
 if r['SCC'] in exact:tags.append(('processes',exact[r['SCC']],'exact'))
 if 'tire manufacture' in cat:tags.extend([('processes','tire_manufacturing','broader'),('materials','elastomers_rubber','broader')])
 if 'fiberglass resin products' in cat:tags.append(('materials','composites_frp','broader'))
 if 'foam production' in cat:tags.append(('materials','foams_polymeric','broader'))
 if 'synthetic rubber' in cat or 'rubber production' in cat or 'rubber and latex' in cat:tags.append(('materials','elastomers_rubber','broader'))
 if 'surface coating operations'==r['scc level two'].lower() and re.search(r'coating operation|coat application|coating application|coat operation|finish coating|coating line|coat, spray|coat, dip',s):tags.append(('processes','coating_applying','broader'))
 for term,tag in [('acrylic resins','acrylic_pmma'),('urea-formaldehyde','melamine_urea_formaldehyde'),('polyester resins','polyester_vinyl_ester_resins'),('polyurethane','polyurethane_pu'),('acrylonitrile butadiene styrene','abs'),('polystyrene resin','polystyrene_ps_hips')]:
  if term in (cat+' '+s):tags.append(('materials',tag,'judgment-call' if term=='acrylic resins' else 'broader'))
 return tags or [('','', 'judgment-call')]
def build():
 sites=read(ROOT/'data/sites_OH.csv');assert len({r['site_id'] for r in sites})==len(sites)
 orgs={r['org_id']:r for p in (ROOT/'data').glob('organizations_*.csv') if not p.name.endswith('_all.csv') for r in read(p)}
 addr=defaultdict(set);reg=defaultdict(set)
 for r in sites:
  if r['street_address']:addr[(street_key(r['street_address']),r['zip'][:5])].add(r['site_id'])
 for r in read(ROOT/'data/registry_links.csv'):
  if r['site_id']:reg[(r['registry'],r['registry_id'])].add(r['site_id'])
 source=read(P/'ohio.csv');scc={r['SCC']:r for r in read(P/'scc.csv')};codes={r['scc'] for r in source};mapping=[]
 for c in sorted(codes):
  if c not in scc or not relevant(scc[c]):continue
  r=scc[c]
  for field,tag,relation in proposal(r):mapping.append(dict(scc=c,description=' | '.join(r[k] for k in ['scc level two','scc level three','scc level four']),field=field,tag=tag,relation=relation,disposition='held',settling_fact='Owner capability-witness ruling; exact site/operator validation; 2023 process currency'))
 allowed={r['scc'] for r in mapping};matched=defaultdict(list);audit=[]
 for r in source:
  if r['scc'] not in allowed:continue
  ids=set(reg.get(('EIS',r['eis facility id']),set()))|set(reg.get(('TRI_TRIFID',r['tri facility id']),set()))
  basis='site_registry'
  if not ids:ids=addr.get((street_key(r['address']),r['zip code'][:5]),set());basis='street_zip'
  ids={i for i in ids if any(s['site_id']==i for s in sites)}
  audit.append(dict(eis_facility_id=r['eis facility id'],scc=r['scc'],atlas_site_ids=';'.join(sorted(ids)),match_basis=basis,disposition='unique_candidate' if len(ids)==1 else 'held',settling_fact='Own-site operator and establishment identity' if len(ids)==1 else 'Unique exact site linkage'))
  if len(ids)==1:matched[next(iter(ids))].append(r)
 frame=[]
 for s in sites:
  sid=s['site_id']
  if sid not in matched:continue
  rs=matched[sid];o=orgs[s['org_id']]
  frame.append(dict(site_id=sid,site_name=s['site_name'],county=s['county'],pic18=int(s['county'] in PIC18),operating_status=s['operating_status'],processes=s['processes'],materials=s['materials'],eis_ids=';'.join(sorted({r['eis facility id'] for r in rs})),nei_names=';'.join(sorted({r['site name'] for r in rs})),sccs=';'.join(sorted({r['scc'] for r in rs})),tag_candidate=int(any(m['tag'] and m['relation']!='judgment-call' and m['scc'] in {r['scc'] for r in rs} for m in mapping)),website=o['website'],disposition='held',settling_fact='Owner witness ruling and exact establishment corroboration'))
 sample=random.Random(SEED).sample(sorted(frame,key=lambda r:r['site_id']),20)
 for r in sample:r.update(verdict='STILL_UNCERTAIN',url='',quote='',assessment='Pending hand check')
 metrics=dict(seed=SEED,atlas_ohio_sites=len(sites),atlas_pic18_sites=sum(s['county'] in PIC18 for s in sites),ohio_index_rows=len(source),ohio_nei_facilities=len({r['eis facility id'] for r in source}),polymer_relevant_sccs=len(allowed),crosswalk_rows=len(mapping),candidate_source_rows=len(audit))
 for label,rs in [('ohio',frame),('pic18',[r for r in frame if r['pic18']])]:
  metrics[label]=dict(matched_sites=len(rs),blank_processes=sum(not r['processes'] for r in rs),blank_materials=sum(not r['materials'] for r in rs),either_blank=sum(not r['processes'] or not r['materials'] for r in rs),tag_candidate_sites=sum(r['tag_candidate'] for r in rs))
 write('crosswalk.csv',mapping);write('join_audit.csv',audit);write('frame.csv',frame)
 write('sample_frame.csv',sample)
 (HERE/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
 (HERE/'source_receipt.json').write_text((P/'index_receipt.json').read_text())
 print(json.dumps(metrics,indent=2))
if __name__=='__main__':build()
