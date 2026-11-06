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
frame={str(x['id']):x for x in json.load(open(PRIVATE/'osu60.json'))}
held=list(csv.DictReader((ROOT/'data/people.csv').open()))
pending=list(csv.DictReader((PRIVATE/'pending_first_pass_people.csv').open()))
reviewed_rows=list(csv.DictReader((ROOT/'tasks/people-settle-2-2026-11-06/reviewed.csv').open()))
assert len({r['candidate_id'] for r in reviewed_rows})==len(reviewed_rows)
reviewed={r['candidate_id']:r for r in reviewed_rows}
assert len({r['person_id'] for r in held})==len(held)
canonical={r['person_id']:r for r in held}
parity_fields=('full_name','institution_org_id','role','role_as_published','research_specialties','public_profile_url')

schema=(ROOT/'docs/SCHEMA.md').read_text()
controlled=set(re.findall(r'`([a-z][a-z0-9_]*)`',schema.split('### 3.1 Processes')[1].split('### 3.3 Markets')[0]+schema.split('### 3.5 Research areas')[1].split('### 3.6')[0]))
for proposal in rows:
 assert set(proposal['research_specialties'].split(';'))<=controlled,('unsupported specialty',proposal['candidate_id'],proposal['research_specialties'])
seen=set()
for r in rows:
 cid=r['candidate_id'];assert cid in frame and cid not in seen;seen.add(cid)
 assert frame[cid]['org_id']==r['institution_org_id']=='ORG-001284'

 assert cid in reviewed,('missing parent allocation',cid)
 allocation=reviewed[cid]['allocated_person_id']
 assert allocation!='PERSON-002114',('retired ID',cid)
 assert allocation in canonical,('missing applied canonical record',cid,allocation)
 for field in parity_fields:
  assert r[field]==reviewed[cid][field]==canonical[allocation][field],('applied self parity',cid,allocation,field)
 home='osu.edu' # Institution domain inspected in own department affiliation statements.
 for z in [z for z in held if z['person_id']!=allocation]+pending:
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
   t=words(d['text']);qwords=words(q);surname=words(r['full_name'])[-1]
   assert any(t[i:i+len(qwords)]==qwords and surname in t[max(0,i-40):i+len(qwords)+40] for i in range(len(t)-len(qwords)+1))
   assert found(d['text'],r['role_as_published'])
 raw=' '.join(r.values());assert not re.search(r'[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}|\(at\)|\d{3}[ .-]\d{3}[ .-]\d{4}',raw)
assert len(rows)==2
dispositions=json.load(open(PRIVATE/'osu60/dispositions.json'))
assert len(dispositions)==60 and len({d['id'] for d in dispositions})==60
assert [d['id'] for d in dispositions]==[x['id'] for x in json.load(open(PRIVATE/'osu60.json'))]
assert {str(d['id']) for d in dispositions if d['verdict']=='VERIFIED'}==seen
# Institutional profile IDs and explicitly assigned lab URLs determine source ownership.
profile_owners={}
for person in frame.values():
 for u in person['urls']:
  path=urlparse(u).path.rstrip('/')
  if re.fullmatch(r'/people/[a-z]+\.\d+',path):
   assert path not in profile_owners or profile_owners[path]==person['id']
   profile_owners[path]=person['id']
def rendered_owner(u):
 if u=='https://cbe.osu.edu/nicholas-brunelli-catalytic-material-design-group':return 14271
 return profile_owners.get(urlparse(u).path.rstrip('/'))
assert rendered_owner('https://cbe.osu.edu/people/clay.32')==15660
assert rendered_owner('https://cbe.osu.edu/people/clay.32') not in (26582,20580)
assert rendered_owner('https://mae.osu.edu/people/kim.6776')!=16617
assert rendered_owner('https://cbe.osu.edu/nicholas-brunelli-catalytic-material-design-group')!=16285
for d in dispositions:
 observations=set()
 for z in d['sources']:
  if 'web primary-page' not in z.get('retrieval_route',''):continue
  assert rendered_owner(z['url'])==d['id'],('rendered source ownership',d['id'],z['url'])
  key=(z['url'],z['rendered_response_sha256'])
  assert key not in observations,('repeated observation',d['id'],key)
  observations.add(key)
assert all(d['deciding_fact'] for d in dispositions if d['verdict']=='REJECT')
assert all(d['settling_fact'] for d in dispositions if d['verdict']=='STILL_UNCERTAIN')
assert b'\r' not in (Path(__file__).parent/'verified.csv').read_bytes()
print('PASS id-exact60 accounting; six calibrated matcher checks; public proposal identities',len(rows),'raw quotes',2*len(rows),'title/surname/provenance/privacy/LF/main+pending dedupe/rendered-source ownership')

for witness in json.load(open(Path(__file__).parent/'specialty_witnesses.json')):
 assert witness['research_specialty'] in controlled
 assert len(witness['quote'].split())<=25
 doc=json.load(open(CACHE/(hashlib.sha256(witness['source_url'].encode()).hexdigest()+'.json')))
 assert found(doc['text'],witness['quote'])
 assert hashlib.sha256(doc['text'].encode()).hexdigest()==witness['sanitized_text_sha256']
print('PASS cached specialty witness')

print('Pending candidate people checked:',len(pending))
