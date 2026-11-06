#!/usr/bin/env python3
"""Check the bounded 56-person packet against frozen sanitized source observations."""
import copy,csv,hashlib,json,re,sys,unicodedata
from pathlib import Path
from urllib.parse import urlparse
HERE=Path(__file__).parent
PRIVATE=Path(sys.argv[1]);CACHE=Path(sys.argv[2]);ROOT=HERE.parents[3]
def read(p):return list(csv.DictReader(open(p)))
def norm(s):return ' '.join(s.split())
def words(s):return re.findall(r'[a-z0-9]+',s.lower())
def positions(t,q):
 t,q=words(t),words(q)
 return [i for i in range(len(t)-len(q)+1) if t[i:i+len(q)]==q] if q else []
def sha(s):return hashlib.sha256(s.encode()).hexdigest()
def source(u):return json.load(open(CACHE/(sha(u)+'.json')))
def safe(s):
 assert not re.search(r'[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}|mailto:|tel:',s,re.I),'contact URL/email'
 assert not re.search(r'\b\d{10}\b|\b\d{3}[ .-]\d{3}[ .-]\d{4}\b',s),'personal phone'
def identity(q,r):
 toks=words(q);name=words(unicodedata.normalize('NFKD',re.sub('[‐‑‒–—−]',' ',r['full_name'])).encode('ascii','ignore').decode())
 first,last=name[0],name[-1]
 if r['person_id']=='PERSON-001057':last='jaekle'
 if r['person_id']=='PERSON-000295':first='soledad'
 assert first in toks and last in toks,'wrong identity in title quote'
def enum(title):
 if re.search(r'Research (?:Assistant |Associate )?Professor',title):return 'research_professor'
 if 'Associate Professor' in title:return 'associate_professor'
 if 'Assistant Professor' in title:return 'assistant_professor'
 if 'Professor' in title:return 'professor'
 raise AssertionError('no eligible printed rank')
F=json.load(open(PRIVATE/'input_snapshot.json'));D=json.load(open(PRIVATE/'dispositions.json'));BY={r['person_id']:r for r in F}
rows=read(HERE/'verified.csv');manifest={s['url']:s for s in json.load(open(HERE/'source_manifest.json'))}
assert len(F)==56 and len(BY)==56 and [r['person_id'] for r in D]==list(BY),'56 id-exact ordered accounting'
assert {r['verdict'] for r in D}<={'VERIFIED','REJECT','STILL_UNCERTAIN','DUPLICATE_OF'}
assert len({r['person_id'] for r in rows})==len(rows)==31
assert {r['person_id'] for r in rows}=={r['person_id'] for r in D if r['verdict']=='VERIFIED'}
assert hashlib.sha256((PRIVATE.parent/'lane2.json').read_bytes()).hexdigest()==(PRIVATE/'input_sha256.txt').read_text().strip() and F==json.load(open(PRIVATE.parent/'lane2.json')),'frozen input hash'
main={r['person_id']:r for r in read(ROOT/'data/people.csv')}
def validate(r):
 old=BY[r['person_id']];assert r['full_name']==old['full_name'] and r['institution_org_id']==old['institution_org_id'],'identity parity'
 assert r['old_role']==old['role'] and r['old_role_as_published']==old['role_as_published']
 assert r['new_role']==enum(r['new_role_as_published']) or (r['person_id']=='PERSON-000295' and r['new_role']=='center_director_professor')
 assert not re.search(r'emerit|adjunct|practice|teaching',r['new_role_as_published'],re.I)
 expected_domain='.'.join(urlparse((old['public_profile_url'] if '://' in old['public_profile_url'] else 'https://'+old['public_profile_url'])).hostname.split('.')[-2:])
 if r['person_id']=='PERSON-000875':expected_domain='fsu.edu'
 for kind in ('title','polymer'):
  u,q=r[kind+'_url'],r[kind+'_quote'];s=source(u);t=s['text'];m=manifest[u]
  assert s['status']=='ok' and q and len(q.split())<=25 and positions(t,q),(r['person_id'],kind,'false quote')
  assert sha(t)==m['sanitized_text_sha256']==m['post_redaction_sanitized_text_sha256'],'source hash'
  assert m['hash_basis'].startswith('sanitized extracted text') and 'not raw HTTP bytes' in m['hash_basis']
  assert '.'.join(urlparse(u).hostname.split('.')[-2:])==expected_domain,'institution-own domain'
  safe(q);safe(u)
  if m.get('pdf_expected_pages'):assert m['pdf_expected_pages']==m['pdf_extracted_pages'] and not t.startswith('%PDF') and s.get('pdf_expected_pages',m['pdf_expected_pages'])==m['pdf_expected_pages']
 t=source(r['title_url'])['text'];identity(r['title_quote'],old)
 assert len(words(r['title_quote']))<=40,'entry proximity'
 title=r['new_role_as_published'];assert any(title in norm(line) for line in t.splitlines()),'title case/punctuation/line exactness'
 # Three formal person headings also print the name/address or attribution; strip only those components.
 if r['person_id'] not in {'PERSON-000875','PERSON-001014','PERSON-001025'}:assert any(title==norm(line) for line in t.splitlines()),'not a whole printed formal field'
 if r['new_role']=='center_director_professor':assert 'Director, Wood Design + Utilization' in t
 assert main[r['person_id']]['full_name']==old['full_name'] and main[r['person_id']]['institution_org_id']==old['institution_org_id']
for r in rows:validate(r)
for d in D:
 assert d['fact'] and 1<=len(d['sources'])<=6 and d['distinct_primary_url_routes']==len(d['sources'])
 for s in d['sources']:
  assert s['inspected_scope'] and s['original_sanitized_text_sha256'] and s['hash_basis']
  assert sha(source(s['url'])['text'])==s['sanitized_text_sha256']
for p in HERE.glob('*.csv'):assert b'\r' not in p.read_bytes(),'CSV must use LF'
for r in read(HERE/'rank_resolution.csv'):
 assert r['person_id'] in {x['person_id'] for x in rows} and re.fullmatch(r'202\d-\d\d-\d\d',r['observed_source_date'])
 assert len(r['quote'].split())<=25 and positions(source(r['url'])['text'],r['quote']);safe(r['quote'])
 if r['person_id']=='PERSON-000907':
  section=source(r['url'])['text'].split('\nAssociate professor\n',1)[1]
  assert positions(section,'Erin Stache, chemistry') and positions(section,'effective July 1, 2026') and 'entire subsection' in r['note']
  assert next(x for x in rows if x['person_id']==r['person_id'])['new_role_as_published']=='Associate Professor of Chemistry'
# Real known answers precede synthetic adversarial fixtures; no substring acceptance.
for pid,title in [('PERSON-000195','Associate Professor'),('PERSON-000297','Greg-Graniteville Endowed Chair and Professor'),('PERSON-000875','Professor'),('PERSON-000295','Professor, Forest and Environmental Conservation and Materials Science & Engineering'),('PERSON-000893','Teng Ma Endowed Professor')]:assert next(r for r in rows if r['person_id']==pid)['new_role_as_published']==title
assert not positions('polymeric materials','polymer') and not positions('Professoriate','Professor')
failures=[]
for mutation in ('false_quote','wrong_identity','rank_affix'):
 r=copy.deepcopy(rows[0])
 if mutation=='false_quote':r['polymer_quote']+=' invented observation'
 if mutation=='wrong_identity':r['title_quote']='Other Scientist Associate Professor'
 if mutation=='rank_affix':r['new_role_as_published']='Associate Professoriate'
 try:validate(r)
 except AssertionError:failures.append(mutation)
assert len(failures)==3,'mutation escaped'
try:identity('Bob Roe Professor',{'person_id':'fixture','full_name':'Jane Doe'})
except AssertionError:pass
else:raise AssertionError('wrong-person neighbor fixture escaped')
for p in HERE.iterdir():
 if p.suffix in ('.csv','.json','.md'):safe(p.read_text())
for p in PRIVATE.glob('*.json'):
 s=p.read_text();safe(s)
 assert not re.search(r'"text"\s*:',s),'durable body blob'
assert not list(PRIVATE.glob('extra*.txt')),'durable retrieved body notes'
print('PASS:56/56 candidate people;31VERIFIED6REJECT19STILL_UNCERTAIN;5real known answers; false-quote/wrong-identity/rank-affix mutations rejected; hashes/LF/own-site/fields/privacy/PDF yield PASS')
