#!/usr/bin/env python3
"""Screen all 42 LA CORROBORATED leads; reuse atlas entity/street normalization.
Adapted from L11 CORROBORATED prep.py; no data writes. Federal-only creates require
unambiguous held operator + explicit polymer manufacturing activity in a reliable ITA row.
"""
import csv,json,re,sys
from collections import defaultdict,Counter
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import atlas

def read(p):
 with open(p,newline='') as f:return list(csv.DictReader(f))
def write(p,rows,fields=None):
 with open(p,'w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields or list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 tables={}
 for name in ['organizations','sites','ecosystem']:
  t=atlas.Table(name)
  for p in (sorted((ROOT/'data').glob(name+'_*.csv')) if name!='ecosystem' else [ROOT/'data/ecosystem.csv']):
   for r in read(p):r['__file__']=str(p.relative_to(ROOT));r['__line__']=0;t.rows.append(r)
  tables[name]=t
 orgs={r['org_id']:r for r in tables['organizations'].rows};idx=defaultdict(set)
 for oid,r in orgs.items():
  for name in [r['legal_name']]+r['trade_names'].split(';'):
   key=atlas.name_key(name)
   if key:idx[key].add(oid)
 def terminal(oid):
  seen=set()
  while orgs[oid]['successor_org_id']:
   if oid in seen:return None
   seen.add(oid);oid=orgs[oid]['successor_org_id']
   if oid not in orgs:return None
  return oid
 def operators(names):return {terminal(oid) for n in names for oid in idx[atlas.name_key(n)]}
 # Three known held operator identities and one ambiguity injection before trusting the matcher.
 known=[]
 for needle in ['Plastipak Packaging','Nike IHM','Hydrite Chemical']:
  matches=[r for r in orgs.values() if needle.casefold() in r['legal_name'].casefold()]
  assert len(matches)==1,(needle,len(matches));r=matches[0]
  assert operators([r['legal_name']])=={terminal(r['org_id'])}
  known.append({'name':r['legal_name'],'expected_org_id':terminal(r['org_id']),'result':'PASS'})
 key=atlas.name_key(known[0]['name']);saved=idx[key].copy();idx[key].add(known[1]['expected_org_id'])
 assert len(operators([known[0]['name']]))==2;idx[key]=saved
 (H/'known-answers.json').write_text(json.dumps({'real_identity_answers':known,'injected_ambiguity':'rejected'},indent=2)+'\n')
 ita={r['establishment_id']:r for r in read(ROOT/'tasks/osha-ita-2026-11-01/establishments.csv')}
 cs=[r for r in read(ROOT/'tasks/lead-fusion-2026-11-01/clusters.csv') if r['state'] in ('LA',) and r['class']=='CORROBORATED']
 cs.sort(key=lambda c:(c['state'],-int(c['score']),c['cluster_id']));assert len(cs)==42
 write(H/'input.csv',cs);out=[];report={}
 for c in cs:
  fed=[ita[i[4:]] for i in c['sources_with_ids'].split(';') if i.startswith('ITA:')]
  names=[c['best_name']]+c['name_variants'].split(' | ')+[r['company_name'] for r in fed]+[r['establishment_name'] for r in fed]
  held=operators(names);d=atlas.dedupe(tables,name=c['best_name'],street=c['street'],city=c['city'],state=c['state'],zip_=c['zip5'])
  # Physical address wins over spelling of the postal city/ZIP, across all site shards.
  street=[r for r in tables['sites'].rows if r['state']==c['state'] and atlas.street_key(r['street_address'])==atlas.street_key(c['street'])]
  v='STILL_UNCERTAIN';oid='';dupe='';reason='Need a reliable plant-grain ITA witness; registry/employer-only families cannot attest this plant.'
  if street:v='DUPLICATE_OF';dupe=street[0]['site_id'];reason='Physical street/state already held; no create.'
  elif len(held)!=1 or None in held:reason='Need unambiguous operator identity at this street; exact legal/trade/federal-company names resolve '+str(sorted(x or 'unresolved successor' for x in held))+'.'
  elif fed:
   oid=next(iter(held));f=fed[0]
   if operators([f['company_name']])!={oid}:reason='Need primary confirmation that the filed company_name is this held operator; matching a plant label or parent-company variant alone is insufficient.'
   elif orgs[oid]['status']!='active':reason='Held operator status is not active; need a current operating/identity witness.'
   elif any(not r['street'] or not r['city'] or not r['zip5'] or r['state']!=c['state'] or atlas.street_key(r['street'])!=atlas.street_key(c['street']) or r['naics_code']!=f['naics_code'] or r['reliability']!='ok' for r in fed):reason='Need reconciled reliable federal street/state/NAICS across the linked ITA records.'
   elif not (f['naics_code'].startswith('326') or f['naics_code'] in {'325211','325212','325510','325520','325910'}) or re.search(r'remover|stripper|cleaner',f['industry_description'],re.I) or f['schema_2_2_signal']!='P' or not re.search(r'plastic|polymer|rubber|resin|paint|coating|\binks?\b',f['industry_description'],re.I):reason='Need an explicit polymer manufacturing activity witness; the filed description does not settle scope.'
   elif any(s['org_id']==oid and s['state']==c['state'] and atlas.squash(s['city'])==atlas.squash(f['city']) and not s['street_address'] for s in tables['sites'].rows):reason='Held operator has an unresolved blank-street site in this locality; need address resolution before a create.'
   else:v='VERIFIED';reason='Exact held operator identity; reliable ITA plant street/state and explicit filed polymer manufacturing activity. Provisional federal-only C, current operating status unknown.'
  out.append(dict(cluster_id=c['cluster_id'],state=c['state'],verdict=v,held_org_id=oid if v=='VERIFIED' else '',duplicate_of=dupe,establishment_id=fed[0]['establishment_id'] if fed else '',reason=reason))
  report[c['cluster_id']]={'house_dedupe':d,'exact_name_terminal_orgs':sorted(x or 'unresolved' for x in held),'street_hits':[r['site_id'] for r in street]}
 reviewed={r['cluster_id']:r['reason'] for r in read(H/'holds-reviewed.csv')}
 for row in out:
  if row['cluster_id'] in reviewed:row.update(verdict='STILL_UNCERTAIN',held_org_id='',reason=reviewed[row['cluster_id']])
 write(H/'verdicts.csv',out);(H/'dedupe.json').write_text(json.dumps(report,indent=2)+'\n')
 print(Counter((r['state'],r['verdict']) for r in out))
if __name__=='__main__':main()
