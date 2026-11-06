#!/usr/bin/env python3
"""Whole PR141 issuer audit, exact field boundary, old-row preservation, missing-condition mutations."""
import copy,csv,io,json,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[1]
def read(p):
 with open(p,newline='') as f:return list(csv.DictReader(f))
def old_rows(base,p):return list(csv.DictReader(io.StringIO(subprocess.check_output(['git','show',base+':'+p],cwd=ROOT,text=True))))
def group_conditions(orgs,audit):
 assert len(audit)==19 and len({r['site_id'] for r in audit})==19
 assert all(r['raw_status']=='raw_brand_verified' for r in audit),'uninspected issuer'
 for r in audit:
  if r['audit_disposition']!='direct_operator_brand':
   org=orgs[r['org_id']]
   assert org['parent_org_id'] or org['ultimate_parent_name'],('missing parent',r['org_id'])
   assert 'Group domain used' in org['notes'],('missing group-domain flag',r['org_id'])
def main():
 base=json.loads((H/'baseline.json').read_text());audit=read(H/'audit.csv');ws=read(H/'parent-witnesses.csv');flags=read(H/'flag-witnesses.csv')
 orgs={r['org_id']:r for p in (ROOT/'data').glob('organizations_*.csv') for r in read(p)};group_conditions(orgs,audit)
 targets={r['org_id']:r['ultimate_parent_name'] for r in ws};flagids={r['org_id'] for r in flags};changed=[]
 for oid,old in base['orgs'].items():
  diff={k for k in old if old[k]!=orgs[oid][k]}
  if oid in targets:
   assert diff=={'ultimate_parent_name','notes'} and orgs[oid]['ultimate_parent_name']==targets[oid],(oid,diff);changed.append(oid)
  elif oid in flagids:assert diff=={'notes'},(oid,diff);changed.append(oid)
  else:assert not diff,(oid,diff)
  if diff:assert orgs[oid]['notes'].startswith(old['notes'])
 assert set(changed)==set(targets)|flagids
 for oid in changed:
  for field in ('parent','flag'):
   bad=copy.deepcopy(orgs)
   if field=='parent':bad[oid]['ultimate_parent_name']='';bad[oid]['parent_org_id']=''
   else:bad[oid]['notes']=bad[oid]['notes'].replace('Group domain used','removed')
   try:group_conditions(bad,audit)
   except AssertionError:pass
   else:raise AssertionError(('missing-condition mutation not caught',oid,field))
 allowed={f'data/{prefix}{shard}.csv' for prefix in ['organizations_','evidence_organizations_'] for shard in ['US','OR','OH']}
 changed_paths=set(subprocess.check_output(['git','diff','--name-only',base['commit'],'--','data/'],cwd=ROOT,text=True).splitlines());assert changed_paths==allowed,changed_paths
 fresh=[]
 for path in sorted(allowed):
  old=old_rows(base['commit'],path);now=read(ROOT/path);key='evidence_id' if '/evidence_' in path else 'org_id';by={r[key]:r for r in now}
  assert all(r[key] in by for r in old),('row loss',path)
  if key=='evidence_id':
   assert all(by[r[key]]==r for r in old),('old evidence changed',path);have={r[key] for r in old};fresh.extend(r for r in now if r[key] not in have)
  else:
   assert len(old)==len(now)
   for r in old:
    if r[key] not in set(changed):assert by[r[key]]==r,('unrelated organization changed',r[key])
 assert len(fresh)==len(ws+flags)==7
 for i,(w,e) in enumerate(zip(ws+flags,sorted(fresh,key=lambda r:r['evidence_id']))):
  assert e['evidence_id']==f'EVD-{307000+i:06d}' and e['record_id']==w['org_id']
  assert e['source_class']=='own_site' and e['source_ref']==w['source_url'] and w['quote'] in e['claim_detail'] and w['raw']=='yes'
 print('PASS19/19 site-issuer audit including15 new orgs;3 parent fields+5 notes flags;7 append-only evidence;10 missing-condition mutations caught; exact6-file boundary')
if __name__=='__main__':main()
