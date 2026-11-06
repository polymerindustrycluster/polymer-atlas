"""Replay the reviewed L12 packet; existing evidence stays byte-for-byte by row."""
import csv, hashlib, json, re, sys, unicodedata
from urllib.parse import urlparse
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from shard_io import append_sorted
from fetch import found, words
DATE='2026-11-06'
# Held institutions with blank websites or an established second university domain.
DOMAIN_OVERRIDES={'ORG-001314':{'uc.edu'},'ORG-004686':{'uw.edu','washington.edu'},'ORG-002781':{'drexel.edu'},'ORG-001284':{'osu.edu','ohio-state.edu'}}
def on_domain(url, domains):
 h=urlparse(url).hostname or ''
 return any(h==d or h.endswith('.'+d) for d in domains)
def read(p):
 with open(p,newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
def write(p,rows,cols):
 with open(p,'w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=cols,lineterminator='\n');w.writeheader();w.writerows(rows)
def norm(s):
 s=''.join(c for c in unicodedata.normalize('NFKD',s).lower() if not unicodedata.combining(c))
 return ' '.join(w for w in re.findall(r'[^\W\d_]+',s) if len(w)>1)
def near(text,quote,surname):
 t,a,n=words(text),words(quote),words(surname)
 return bool(a) and bool(n) and any(t[i:i+len(a)]==a and all(x in t[max(0,i-40):i+len(a)+40] for x in n) for i in range(len(t)-len(a)+1))
def identity(s):
 t=norm(s).split()
 assert t,'empty name'
 return t[0],t[-1]
def main():
 data=ROOT/'data'
 p=read(data/'people.csv');byid={r['person_id']:r for r in p}
 proposals=read(HERE/'reviewed.csv')
 institutions={r['org_id']:r for f in [data/'ecosystem.csv',*sorted(data.glob('organizations_*.csv'))] for r in read(f)}
 # Expected cells are frozen before application, for fail-closed rebase/replay.
 expected=json.loads((HERE/'expected.json').read_text())
 raw={(r['url'],r['quote']):r for r in read(HERE/'rawcheck.csv')}
 additions=[];evidence=[];seen=set()
 for i,r in enumerate(proposals):
  pid=r['allocated_person_id']
  assert pid not in seen;seen.add(pid)
  for gate in ('a','b'):
   u,q=r[f'gate_{gate}_url'],r[f'gate_{gate}_quote']
   assert '@' not in u and u.startswith('https://'),u
   web=urlparse(institutions[r['institution_org_id']].get('website','')).hostname or ''
   domains=DOMAIN_OVERRIDES.get(r['institution_org_id'],{'.'.join(web.split('.')[-2:])} if web else set())
   assert domains and on_domain(u,domains),(pid,'source outside institution',u)
   assert len(q.split())<=25,(pid,gate,'quote too long')
   ck=raw[(u,q)]
   assert ck['found']=='yes'
   if gate=='a':assert ck['surname_near']=='yes'
  if not r['person_id']:
   assert 2000<=int(pid[7:])<=2499
   dup=[x['person_id'] for x in p if x['person_id']!=pid and (norm(x['full_name'])==norm(r['full_name']) or (x['institution_org_id']==r['institution_org_id'] and identity(x['full_name'])==identity(r['full_name'])))]
   assert not dup,(r['full_name'],dup)
   record={k:r.get(k,'') for k in p[0]}
   record.update(person_id=pid,sources=';'.join(dict.fromkeys([r['gate_a_url'],r['gate_b_url']])),verification_tier='C',last_verified=DATE)
   if pid in byid:assert byid[pid]==record,(pid,'create replay differs')
   else:additions.append(record)
  else:
   record=byid[pid]
   assert record['institution_org_id']==r['institution_org_id'] and record['full_name']==r['full_name'],(pid,'identity changed')
   changes={k:r[k] for k in ('role','role_as_published')}
   changes['sources']=';'.join(dict.fromkeys(record['sources'].split(';')+[r['gate_a_url'],r['gate_b_url']]))
   changes['last_verified']=DATE
   for k,v in changes.items():
    if k=='sources':
     assert all(u in v.split(';') for u in expected[pid][k].split(';'))
    else:assert record[k] in (expected[pid][k],v),(pid,k,'base changed')
    record[k]=v
  for gate in ('a','b','parent'):
   eid=r[f'evidence_{gate}_id']
   witness='a' if gate=='parent' else gate
   assert 280000<=int(eid[4:])<=284999,eid
   evidence.append(dict(evidence_id=eid,record_table='people',record_id=pid,claim_type='parent' if gate=='parent' else ('existence' if gate=='a' else 'scope'),
    claim_detail=f"role {r['role']}; title {r['role_as_published']}" if gate=='a' else (f"institution_org_id {r['institution_org_id']}; current appointment on institution-own profile" if gate=='parent' else 'Gate B: person-level polymer research stated'),
    source_class='own_site',source_ref=r[f'gate_{witness}_url'],observed_date=DATE,tier_effect='supports_A',
    created_by='codex atlas-L12-people-settle',notes=('Affiliation carried by the current own-institution rank/profile; raw words in order: ' if gate=='parent' else 'Raw words in order: ')+r[f'gate_{witness}_quote']))
 assert len({r['evidence_id'] for r in evidence})==len(evidence),'duplicate packet evidence IDs'
 existing={r['evidence_id']:r for r in read(data/'evidence_people.csv')}
 for r in evidence:
  if r['evidence_id'] in existing:assert existing[r['evidence_id']]==r,(r['evidence_id'],'ID collision')
 write(data/'people.csv',p,list(p[0]))
 if additions:append_sorted(data/'people.csv',additions,'person_id')
 append_sorted(data/'evidence_people.csv',[r for r in evidence if r['evidence_id'] not in existing],'evidence_id')
 print(f'{len(proposals)} reviewed people; {len(additions)} new people this replay; {len(evidence)} evidence observations')
if __name__=='__main__':main()
