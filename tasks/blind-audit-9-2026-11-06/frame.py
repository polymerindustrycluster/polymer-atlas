"""Reproduce exact canonical new-ID frame from six pinned merge first-parent diffs."""
import csv,io,json,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent
FIELDS=['site_name','site_type','org_id','street_address','city','state','zip','county','ring_primary','naics_primary','naics_primary_source_type','operating_status','processes','materials']
def at(ref,path):return list(csv.DictReader(io.StringIO(subprocess.check_output(['git','show',ref+':'+path]).decode())))
def derive(meta):
 pin=meta['pinned_main']
 paths=subprocess.check_output(['git','ls-tree','--name-only',pin,'data/']).decode().splitlines()
 current={r['site_id']:r for p in paths if p.startswith('data/sites_') and not p.endswith('_all.csv') for r in at(pin,p)}
 org={r['org_id']:r for p in paths if p.startswith('data/organizations_') and not p.endswith('_all.csv') for r in at(pin,p)}
 result=[]
 for p in meta['prs']:
  sha=p['merge_sha'];files=subprocess.check_output(['git','diff-tree','--no-commit-id','--name-only','-r',sha+'^1',sha,'--','data/sites_*.csv']).decode().splitlines();new=[]
  for f in files:
   old={r['site_id'] for r in at(sha+'^1',f)};new.extend(r for r in at(sha,f) if r['site_id'] not in old)
  assert len(new)==p['published_creates']==p['derived_creates'],p['pr']
  for r in new:
   rr=current[r['site_id']];o=org[rr['org_id']]
   result.append(dict(site_id=r['site_id'],pr=str(p['pr']),lane=p['lane'],creation_tier=r['verification_tier'],current_tier=rr['verification_tier'],**{k:rr[k] for k in FIELDS},parent_name=o['legal_name'],parent_website=o['website']))
 assert len(result)==len({r['site_id'] for r in result})==110
 return sorted(result,key=lambda r:r['site_id'])
if __name__=='__main__':
 rows=derive(json.loads((H/'frame_provenance.json').read_text()))
 with (H/'frame.csv').open(newline='') as f:assert list(csv.DictReader(f))==rows,'frame differs from pinned git derivation'
 print('PASS 110 unique true creations; all six PR published counts reconciled; frame values reproduce; no evidence or metadata markers read')
