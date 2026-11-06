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
frame={str(x['id']):x for x in json.load(open(PRIVATE/'root8_followup.json'))}
held=list(csv.DictReader((ROOT/'data/people.csv').open()))
pending=list(csv.DictReader((PRIVATE/'pending_first_pass_people.csv').open()))
reviewed_rows=list(csv.DictReader((ROOT/'tasks/people-settle-2-2026-11-06/reviewed.csv').open()))
assert len({r['candidate_id'] for r in reviewed_rows})==len(reviewed_rows)
reviewed={r['candidate_id']:r for r in reviewed_rows}
assert len({r['person_id'] for r in held})==len(held)
canonical={r['person_id']:r for r in held}
parity_fields=('full_name','institution_org_id','role','role_as_published','research_specialties','public_profile_url')

def body(u):return json.loads((CACHE/(hashlib.sha256(u.encode()).hexdigest()+'.json')).read_text())['text']
assert found(body('https://u.osu.edu/smsl/'),'Professor Marcelo Dapino, Fellow of ASME and SPIE')
assert found(body('https://u.osu.edu/smsl/uam/uam-research/'),'Joining of Carbon Fiber Reinforced Polymer and Metal')
assert found(body('https://u.osu.edu/smsl/uam/uam-research/'),'carbon fiber fabric layers extending from the UAM structure are cured in a carbon fiber reinforced polymer (CFRP) part')
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
assert len(rows)==1
dispositions=json.load(open(PRIVATE/'root8/dispositions.json'))
assert len(dispositions)==8 and len({d['id'] for d in dispositions})==8
assert [d['id'] for d in dispositions]==[x['id'] for x in json.load(open(PRIVATE/'root8_followup.json'))]
assert {str(d['id']) for d in dispositions if d['verdict']=='VERIFIED'}==seen
assert all(d['deciding_fact'] for d in dispositions if d['verdict']=='REJECT')
assert all(d['settling_fact'] for d in dispositions if d['verdict']=='STILL_UNCERTAIN')
assert b'\r' not in (Path(__file__).parent/'verified.csv').read_bytes()
print('PASS id-exact8 accounting; six calibrated matcher checks; public proposal identities',len(rows),'raw quotes',2*len(rows),'title/surname/provenance/privacy/LF/main+pending dedupe')

print('Pending candidate people checked:',len(pending))
