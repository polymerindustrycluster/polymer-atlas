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
frame={str(x['id']):x for x in json.load(open(PRIVATE/'uc58.json'))}
held=list(csv.DictReader((ROOT/'data/people.csv').open()))
pending=list(csv.DictReader((PRIVATE/'pending_first_pass_people.csv').open()))
schema=(ROOT/'docs/SCHEMA.md').read_text()
materials=schema.split('### 3.2 Materials',1)[1].split('### 3.3',1)[0]
supplement=schema.split('### 3.5 Research areas',1)[1].split('### 3.6',1)[0]
assert '`pvc`' in materials and '`biomedical_polymers`' in supplement
specialties={'23173':'pvc','22917':'biomedical_polymers'}
assert {r['candidate_id']:r['research_specialties'] for r in rows}==specialties, 'unsupported specialty token'
reviewed_rows=list(csv.DictReader((Path(__file__).resolve().parents[2]/'reviewed.csv').open()))
assert len({r['candidate_id'] for r in reviewed_rows})==len(reviewed_rows)
reviewed={r['candidate_id']:r for r in reviewed_rows}
held_by_id={r['person_id']:r for r in held}
assert len(held_by_id)==len(held)
parity_fields=('full_name','institution_org_id','role','role_as_published','research_specialties','public_profile_url')
seen=set()
for r in rows:
 cid=r['candidate_id'];assert cid in frame and cid not in seen;seen.add(cid)
 assert frame[cid]['org_id']==r['institution_org_id']=='ORG-001314'
 home='uc.edu'
 applied=reviewed[cid];self_id=applied['allocated_person_id']
 assert self_id and self_id in held_by_id, (cid,'missing allocated endpoint')
 canonical=held_by_id[self_id]
 assert all(r[k]==applied[k]==canonical[k] for k in parity_fields), (cid,'applied canonical field mismatch')
 for z in [h for h in held if h['person_id']!=self_id]+pending:
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
assert b'\r' not in (Path(__file__).parent/'verified.csv').read_bytes()
d=json.load(open(PRIVATE/'uc58/dispositions.json'))
assert len(d)==58 and len({str(x['candidate_id']) for x in d})==58
assert [str(x['candidate_id']) for x in d]==list(frame)
assert {v:sum(x['verdict']==v for x in d) for v in ('VERIFIED','REJECT','STILL_UNCERTAIN','DUPLICATE_OF')}=={'VERIFIED':2,'REJECT':4,'STILL_UNCERTAIN':52,'DUPLICATE_OF':0}
assert {str(x['candidate_id']) for x in d if x['verdict']=='VERIFIED'}==seen
for x in d:
 assert x['sources'] and all(z.get('inspected_scope') for z in x['sources'])
 assert len(x['sources'])<=6,(x['candidate_id'],'source budget')
 assert x.get('deciding_fact') if x['verdict']=='REJECT' else x.get('settling_fact') if x['verdict']=='STILL_UNCERTAIN' else x.get('verdict_note')
# Real known answers: three excluded ranks and two material statements.
for suffix,title in [('thiels','Professor - Educator'),('elgafya','Professor - Educator'),('machasf','Research Associate - Physical Science')]:
 u='https://researchdirectory.uc.edu/p/'+suffix
 raw=json.loads((CACHE/(hashlib.sha256(u.encode()).hexdigest()+'.json')).read_text())['text']
 assert found(raw,title)
assert found(rows[0]['gate_b_quote'],'Polyvinyl Chloride')
assert found(rows[1]['gate_b_quote'],'biodegradable polymer')
u='https://researchdirectory.uc.edu/p/jiangjb'
t=json.loads((CACHE/(hashlib.sha256(u.encode()).hexdigest()+'.json')).read_text())['text']
i=t.index('Grant: #CHE-2347912');project=t[i:i+350]
assert all(s in project for s in ['Investigators:Jiang, Jianbing','05-01-2024','04-30-2027','Role:PI','Active'])
rank=list(csv.DictReader((Path(__file__).parent/'rank_resolution.csv').open()))
assert len(rank)==1 and rank[0]['candidate_id']=='23173'
x=rank[0];assert not re.search(r'[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}|\d{3}[ .-]\d{3}[ .-]\d{4}',' '.join(x.values()));u=x['source_url'];d=json.loads((CACHE/(hashlib.sha256(u.encode()).hexdigest()+'.json')).read_text())
assert found(d['text'],x['rank_quote']) and len(x['rank_quote'].split())<=25
assert found(d['text'],'October 2 2023') and x['published_date']=='2023-10-02'
assert hashlib.sha256(d['text'].encode()).hexdigest()==x['sanitized_text_sha256']
assert 'sanitized extracted text' in x['hash_basis'] and 'no raw HTTP bytes' in x['hash_basis']
u=x['identity_bridge_url'];d=json.loads((CACHE/(hashlib.sha256(u.encode()).hexdigest()+'.json')).read_text())
assert found(d['text'],'Jianbing Jimmy Jiang') and found(d['text'],'since August 2018')
assert rows[0]['gate_a_quote']=='Jianbing Jiang Assoc Professor'
assert rows[1]['gate_a_quote']=='Yoonjee Park Professor (F2)'
print('PASS 58 id-exact dispositions, source budgets, five real known answers, institution-owned dated rank/nickname bridge, current Jiang PI/date object, six calibrated matcher checks; public proposal identities',len(rows),'raw quotes',2*len(rows),'exact allocated-ID canonical parity/controlled specialties/direct mappings/title/surname/provenance/privacy/LF/main+pending dedupe;current pending candidate people',len(pending))
