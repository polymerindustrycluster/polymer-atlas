"""Check the public packet against the shared institutional raw-page cache."""
import csv,hashlib,json,re,sys,unicodedata
from pathlib import Path
from urllib.parse import urlparse
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fetch import CACHE,found,words
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
def near(text,quote,surname):
 t,q=words(text),words(quote)
 return any(t[i:i+len(q)]==q and surname.lower() in t[max(0,i-40):i+len(q)+40] for i in range(len(t)-len(q)+1))
def page(u):
 p=json.loads((CACHE/(hashlib.sha256(u.encode()).hexdigest()+'.json')).read_text())
 assert p['status']=='ok' and not p['text'].lstrip().startswith('%PDF-'),u
 return p['text']
def norm(s):return ''.join(words(unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode()))
# Known answers include real positives, wrong rank, wrong person, and a proximity defect.
f=page('https://chemistry.osu.edu/people/wyzgoski.1')
assert near(f,'Associate Professor','Wyzgoski')
assert not found(f,'Distinguished Professor of Polymer Physics')
assert not near(f,'Associate Professor','Boika')
assert not near('Wyzgoski '+'gap '*41+'Associate Professor','Associate Professor','Wyzgoski')
assert found(f,'advanced NMR studies of synthetic polymers')
assert not found('depolymerization','polymer')
assert not found('polymeric materials','polymer')
packet_files=[HERE/'verified.csv',HERE/'verified_more.csv']
rows=[r for path in packet_files for r in csv.DictReader(path.open())]
held=list(csv.DictReader((ROOT/'data/people.csv').open()))
integrated_names={'PERSON-002005': 'Faith Wyzgoski', 'PERSON-002007': 'Burcu Gurkan', 'PERSON-002009': 'John Robert Martin', 'PERSON-002010': 'Jonathan David Nickels', 'PERSON-002011': 'Junhang Dong', 'PERSON-002013': 'Allen Yi', 'PERSON-002014': 'Byung-Wook Park', 'PERSON-002016': 'Aleksander Skardal'}
integrated=set(integrated_names)
seen=set()
for r in rows:
 key=(norm(r['full_name']),r['institution_org_id']);assert key not in seen,key;seen.add(key)
 assert not any(norm(z['full_name'])==key[0] or (words(z['full_name']) and words(z['full_name'])[0]==words(r['full_name'])[0] and words(z['full_name'])[-1]==words(r['full_name'])[-1]) for z in held if z['person_id'] not in integrated),('global held identity',r['full_name'])
 for z in held:
  if z['person_id'] in integrated and norm(z['full_name'])==key[0]:
   assert all(z[k]==r[k] for k in ['institution_org_id','role','role_as_published','public_profile_url']),(r['full_name'],'integration mismatch')
 assert r['role'] in ['professor','associate_professor','assistant_professor','research_professor']
 for g in ['a','b']:
  u,q=r[f'gate_{g}_url'],r[f'gate_{g}_quote'];host=urlparse(u).hostname
  assert host and host.endswith('.edu') and '@' not in u,u
  assert len(q.split())<=25,(r['full_name'],g)
  assert found(page(u),q),(r['full_name'],g,'quote absent')
 assert near(page(r['gate_a_url']),r['gate_a_quote'],words(r['full_name'])[-1]),(r['full_name'],'surname distance')
 assert r['role_as_published'] and found(page(r['gate_a_url']),r['role_as_published']),(r['full_name'],'title absent')
admitted=[z for z in held if z['person_id'] in integrated]
assert all(norm(z['full_name'])==norm(integrated_names[z['person_id']]) for z in admitted),'integrated ID/name mapping differs'
if admitted:
 assert len(admitted)==len(rows) and {(norm(z['full_name']),z['institution_org_id']) for z in admitted}==seen,'integrated ID/name mapping differs'
for path in packet_files:
 raw=path.read_bytes();assert b'\r' not in raw
 assert not re.search(rb'[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}|\(at\)|\d{3}[ .-]\d{3}[ .-]\d{4}',raw)
print(f'PASS: 7 known-answer checks; {len(rows)} unique candidate-person packets; {2*len(rows)} raw quotes; all Gate-A surnames within40 words; global held-name exclusion; contact/URL/LF checks.')
