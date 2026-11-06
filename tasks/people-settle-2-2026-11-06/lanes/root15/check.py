import csv,hashlib,json,re,sys,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
PRIVATE=Path('/Users/johnswanson/.bb/thread-storage/thr_mcdghpxw8c/people-settle-2-private')
sys.path.insert(0,str(PRIVATE/'root15'))
from fetch_new import get,found,words
# Token boundaries and wrong-identity negative controls.
assert found('Kim is a Professor.','Kim is a Professor')
assert not found('polymeric','polymer')
assert not found('neuroplasticity','plastic')
assert not found('Professor Kumar studies polymers. Kim studies bone.','Kim studies polymers')
# Five known answers from actual new institutional sources, never search snippets.
a=get('https://medicine.osu.edu/departments/plastic-reconstructive-surgery/our-people')['text']
assert found(a,'Albert Chao MD FACS Professor and Acting Chair')
b=get('https://bme.osu.edu/directory/professional-practice-faculty')['text']
assert found(b,'Professional Practice Professor Biomedical Engineering') and found(b,'Ruegsegger Mark')
c=get('https://eed.osu.edu/people/grzybowski.3')['text']
assert found(c,'Emeritus Engineering Education') and found(c,'Deborah Grzybowski')
d=get('https://dentistry.osu.edu/faculty?name=Kim')['text']
assert found(d,'Do Gyoon Kim PhD Professor Research Program Director')
e=get('https://neurofilament.osu.edu/research/')['text']
assert found(e,'one of three classes of protein polymers that make up the axonal cytoskeleton')
frame=json.load(open(PRIVATE/'root15_followup.json'))
rows=json.load(open(PRIVATE/'root15/dispositions.json'))
assert len(rows)==len(frame)==15
assert [r['candidate_id'] for r in rows]==[r['id'] for r in frame]
assert len({r['candidate_id'] for r in rows})==15
assert sum(r['verdict']=='REJECT' for r in rows)==2
assert sum(r['verdict']=='STILL_UNCERTAIN' for r in rows)==13
assert all(r['verdict'] in ('REJECT','STILL_UNCERTAIN') for r in rows)
for r in rows:
 assert r.get('deciding_fact') if r['verdict']=='REJECT' else r.get('settling_fact')
 assert 1<=len(r['new_sources'])<=6
 for s in r['new_sources']:
  assert s['inspected_scope']
  if s['status']=='ok':assert s['raw_response_sha256']
  elif s['status']=='ok_rendered_cached':assert s['tool_response_sha256'] and s['availability_note']
  else:assert not s['status'].startswith('ok')
# Rejections bind target entries; both practice ranks are positively published.
for text,surname,title in [(b,'Ruegsegger','Professional Practice Professor Biomedical Engineering'),(c,'Grzybowski','Emeritus Engineering Education')]:
 t=words(text);q=words(title)
 assert any(t[i:i+len(q)]==q and surname.lower() in t[max(0,i-40):i+len(q)+40] for i in range(len(t)-len(q)+1))
pdf=get('https://dentistry.osu.edu/sites/default/files/2025-09/Oral-Bio-PhD-Handbook.pdf')
assert pdf['pdf_pages_expected']==pdf['pdf_pages_extracted']==55
assert found(pdf['text'],'Do Gyoon Kim PhD Division of Orthodontics Mechanisms of bone disease using a mechanobiologic approach')
def norm(s):return ''.join(words(unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode()))
main=list(csv.DictReader((ROOT/'data/people.csv').open()))
pending=list(csv.DictReader((PRIVATE/'pending_first_pass_people.csv').open()))
for r in frame:
 a=words(r['name'])
 for z in main+pending:
  b=words(z['full_name'])
  assert norm(r['name'])!=norm(z['full_name']) and not(a[0] in b and a[-1] in b),('identity hit',r['id'],z.get('person_id'))
public=list(csv.DictReader((Path(__file__).parent/'verified.csv').open()));assert public==[]
for f in ('verified.csv','README.md','source_manifest.json'):
 t=(Path(__file__).parent/f).read_text()
 assert not re.search(r'[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}|\d{3}[ .-]\d{3}[ .-]\d{4}',t)
 for r in frame:assert r['name'] not in t,('unpublished discovery name',r['id'],f)
print('PASS exact15 input-order dispositions:0 VERIFIED/2 REJECT/13 STILL_UNCERTAIN;5 actual-source known answers;4 boundary/identity controls;target-bound excluded ranks;55/55 PDF pages;source budgets/hashes;main+pending dedupe;empty public proposals/privacy;current pending candidate people',len(pending))
