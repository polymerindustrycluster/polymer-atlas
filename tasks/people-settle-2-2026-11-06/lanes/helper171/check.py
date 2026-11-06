import csv,hashlib,json,re,sys,unicodedata
from pathlib import Path
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parents[4]
PRIVATE=Path('/Users/johnswanson/.bb/thread-storage/thr_mcdghpxw8c/people-settle-2-private')
sys.path.insert(0,str(PRIVATE/'tools'))
from fetch import found,words,CACHE
# Matcher calibration: exact known positives, affix negatives, wrong identity, removed rank.
assert found('Wang is an Associate Professor.','Associate Professor')
assert not found('depolymerization','polymer')
assert not found('polymeric','polymer')
assert not found('Professorship','Professor')
assert not found('Professor Kumar studies polymers. Wang studies metals.','Wang studies polymers')
assert not found('Fisch, Michael R. (1998), Instructor','Fisch, Michael R. (1998), Associate Professor')
def norm(s):return ''.join(words(unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode()))
rows=list(csv.DictReader((Path(__file__).parent/'verified.csv').open()))
def near(text,quote,surname):
 t,q=words(text),words(quote)
 return any(t[i:i+len(q)]==q and surname.lower() in t[max(0,i-40):i+len(q)+40] for i in range(len(t)-len(q)+1))
# Calibrate the inherited proximity check on five actual, manually bounded person entries.
for cid in ['21568','900','8328','8713','18213']:
 r=next(x for x in rows if x['candidate_id']==cid);u=r['gate_a_url'];d=json.loads((CACHE/(hashlib.sha256(u.encode()).hexdigest()+'.json')).read_text())
 assert near(d['text'],r['gate_a_quote'],words(r['full_name'])[-1])
assert not near('Fisch '+'gap '*41+'Associate Professor','Associate Professor','Fisch')
assert not near('Kumar is an Associate Professor. Wang is an Instructor.','Associate Professor','Wisner')
assert not found('Kumar is an Associate Professor. Wang is an Instructor.','Wang is an Associate Professor')
frame={str(x['id']):x for x in json.load(open(PRIVATE/'helper171.json'))}
held=list(csv.DictReader((ROOT/'data/people.csv').open()))
pending=list(csv.DictReader((PRIVATE/'pending_first_pass_people.csv').open()))
overrides={str(x['candidate_id']):x for x in json.load(open(PRIVATE/'helper/home_overrides.json'))}
ecosystem={x['org_id']:x for x in csv.DictReader((ROOT/'data/ecosystem.csv').open())}
allowed_specialties={'composites_unspecified','characterization_methods','polymer_physics','biomedical_polymers','composites_mechanics'}
def valid_specialties(value):return bool(value) and set(value.split(';'))<=allowed_specialties
assert valid_specialties('composites_unspecified')
assert not valid_specialties('Polymer composites and nanocomposites')
assert not valid_specialties('Polymeric sorbents')
applied_ids={'21568':'PERSON-002104','900':'PERSON-002105','574':'PERSON-002106','8328':'PERSON-002107','18213':'PERSON-002108','8713':'PERSON-002109','18181':'PERSON-002110'}
reviewed={r['candidate_id']:r for r in csv.DictReader((ROOT/'tasks/people-settle-2-2026-11-06/reviewed.csv').open())}
for r in rows:
 approved=reviewed[r['candidate_id']];assert approved['allocated_person_id']==applied_ids[r['candidate_id']]
 for k in ['full_name','institution_org_id','role','role_as_published','research_specialties','public_profile_url','gate_a_url','gate_a_quote','gate_b_url','gate_b_quote']:assert approved[k]==r[k],(r['candidate_id'],k,'reviewed-map mismatch')
 canonical=next(z for z in held if z['person_id']==approved['allocated_person_id'])
 assert all(canonical[k]==r[k] for k in ['full_name','institution_org_id','role','role_as_published','research_specialties','public_profile_url'])
seen=set()
for r in rows:
 cid=r['candidate_id'];assert cid in frame and cid not in seen;seen.add(cid)
 assert valid_specialties(r['research_specialties'])
 if cid in overrides:
  o=overrides[cid];assert o['discovery_org_id']==frame[cid]['org_id'] and o['proposed_institution_org_id']==r['institution_org_id']
  assert o['identity_home_url']==r['public_profile_url']
  d=json.loads((CACHE/(hashlib.sha256(o['identity_home_url'].encode()).hexdigest()+'.json')).read_text());assert d['status'].startswith('ok') and found(d['text'],o['identity_home_quote'])
 else:assert frame[cid]['org_id']==r['institution_org_id']
 home=urlparse(ecosystem[r['institution_org_id']]['website']).hostname.removeprefix('www.')
 for z in [z for z in held if z['person_id'] not in set(applied_ids.values())]+pending:
  a,b=words(z['full_name']),words(r['full_name'])
  assert norm(z['full_name'])!=norm(r['full_name']) and not (a and b and a[0]==b[0] and a[-1]==b[-1]),('identity duplicate',r['full_name'],z.get('person_id'))
 for g in 'ab':
  u,q=r[f'gate_{g}_url'],r[f'gate_{g}_quote'];h=urlparse(u).hostname
  assert h and (h==home or h.endswith('.'+home)) and '@' not in u,(cid,h,home)
  assert len(q.split())<=25
  d=json.loads((CACHE/(hashlib.sha256(u.encode()).hexdigest()+'.json')).read_text())
  assert d['status'].startswith('ok') and not d['text'].lstrip().startswith('%PDF')
  assert found(d['text'],q),(cid,g,'quote absent')
  if g=='a':
   assert near(d['text'],q,words(r['full_name'])[-1])
   assert found(d['text'],r['role_as_published'])
 raw=' '.join(r.values());assert not re.search(r'[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}|\(at\)|\d{3}[ .-]\d{3}[ .-]\d{4}',raw)
assert b'\r' not in (Path(__file__).parent/'verified.csv').read_bytes()
print('PASS 14 calibrated token/proximity/identity/defect checks + 3 controlled-tag checks; public proposal identities',len(rows),'raw quotes',2*len(rows),'title/surname/provenance/privacy/LF/main+pending dedupe; strict reviewed/canonical parity for seven allocated self IDs')
