"""Apply reviewed street cells only; validate all witnesses and collisions before writing."""
import csv,sys,hashlib,re,json,shutil
from pathlib import Path
from scout import ROOT,TASK,S,read,write,norm
sys.path.insert(0,str(ROOT/'scripts'))
from shard_io import append_sorted
from atlas import street_key
from refetch import Text,words
CREATOR='atlas-w16-street-leads'
def key(s):return street_key(re.sub(r'(?<=[A-Za-z])\.(?=[A-Za-z])','',s))
def plan():
 frame=read(TASK/'frame.csv');p=read(TASK/'proposals.csv');leads=read(TASK/'leads.csv');by={s['site_id']:s for s in frame}
 assert len(p)==len(by)==len(frame)==173 and {r['site_id'] for r in p}==set(by)
 ev=[]
 for r in p:
  if r['disposition']!='applied':assert r['settling_fact'];continue
  s=by[r['site_id']];assert r['verdict']=='VERIFIED'
  assert any(key(r['street'])==key(l['street']) for l in leads if l['site_id']==r['site_id']),'lead street mismatch'
  path=Path(r['text_file']);assert path.exists()
  if r['source_class']=='own_site':
   stored=S/'pic18-corpus-2026-11-16'/r['raw_file'];assert hashlib.sha256(stored.read_bytes()).hexdigest()==r['sha256']
   text=re.sub(r'\s+',' ',path.read_text());assert r['quote'] in text
   assert not re.search(r'(?i)mail(?:ing)? address|p\.?\s*o\.?\s*box',r['quote'])
   raw=Path(r['fresh_file']).read_bytes();assert hashlib.sha256(raw).hexdigest()==r['fresh_sha256']
   t=Text();t.feed(raw.decode(errors='replace'));w=words(' '.join(t.parts));q=words(r['quote']);assert any(w[i:i+len(q)]==q for i in range(len(w)-len(q)+1)),'fresh quote absent'
   assert norm(s['city']) in norm(r['quote'])
  else:
   assert hashlib.sha256(path.read_bytes()).hexdigest()==r['sha256']
   field='establishment_id' if 'osha-ita-' in str(path) else 'est_key';row=next(x for x in read(path) if x[field]==r['source_key'])
   matches=read(path.parent/'site_matches.csv');assert any(m[field]==r['source_key'] and m['site_id']==r['site_id'] and m['org_id']==s['org_id'] and m['match_strength'] in ('exact','strong') for m in matches),'federal binding drift'
   assert row['street']==r['street'] and norm(row['city'])==norm(s['city']) and row['state']=='OH'
   assert not s['zip'] or s['zip'][:5]==row.get('zip5',row.get('zip'))[:5]
   name=row.get('establishment_name',row.get('name'));z=row.get('zip5',row.get('zip'))
   assert r['quote']==f'{name} | {row["street"]} | {row["city"]} | OH | {z}'
  eid=f'EVD-{385000+len(ev):06d}'
  ev.append(dict(evidence_id=eid,record_table='sites',record_id=r['site_id'],claim_type='address',claim_detail=f"street_address {r['street']}, {s['city']}, OH",source_class=r['source_class'],source_ref=r['source_ref'],observed_date=r['observed_date'],tier_effect='supports_A',created_by=CREATOR,notes=f"Quote (filing fields separated by |): {r['quote']}; source key {r['source_key']}; SHA-256 {r['fresh_sha256'] or r['sha256']}; checked 2026-11-16. Filing witness is historical, not an assertion of current occupancy. Only street_address changed."))
 return p,ev

def run(apply=False):
 p,ev=plan();sites=read(ROOT/'data/sites_OH.csv');by={s['site_id']:s for s in sites};frozen={s['site_id']:s for s in read(TASK/'frame.csv')};existing={}
 for f in (ROOT/'data').glob('evidence_*.csv'):
  for e in read(f):
   if e['evidence_id'] in {e['evidence_id'] for e in ev}:existing.setdefault(e['evidence_id'],[]).append((f.name,e))
 new=[]
 for e in ev:
  r=next(r for r in p if r['site_id']==e['record_id']);s=by[r['site_id']];old=frozen[r['site_id']]
  assert all(s[k]==v for k,v in old.items() if k!='street_address'),'frozen site drift'
  assert s['street_address'] in ('',r['street']),'street conflict'
  have=existing.get(e['evidence_id'],[]);assert not have or have==[('evidence_sites_OH.csv',e)],'ID collision'
  if not have:new.append(e)
 if apply:
  backup=S/'pic18-street-leads/backups';backup.mkdir(parents=True,exist_ok=True)
  for name in ('sites_OH.csv','evidence_sites_OH.csv'):
   if not (backup/name).exists():shutil.copyfile(ROOT/'data'/name,backup/name)
  for r in p:
   if r['disposition']=='applied':by[r['site_id']]['street_address']=r['street']
  if new:append_sorted(ROOT/'data/evidence_sites_OH.csv',new,'evidence_id')
  write(ROOT/'data/sites_OH.csv',sites)
 print(json.dumps(dict(input_sites=len(p),filled_sites=len(ev),held_sites=len(p)-len(ev),evidence_rows=len(ev))))
if __name__=='__main__':run('--apply' in sys.argv)
