"""L12 oracle: full input yield, scope-limited diff, append-only evidence and replay."""
import csv, hashlib, io, json, subprocess, sys
from build import HERE, ROOT, read, near, norm, identity, on_domain
from fetch import found, get

def require_claims(rows,pid):
 assert {'existence','scope','parent'} <= {e['claim_type'] for e in rows if e['record_id']==pid},(pid,'missing must-have claim')

def main():
 packet=read(HERE/'reviewed.csv')
 for name,n in [('census_verdicts.csv',79),('title_verdicts.csv',363)]:
  r=read(HERE/name);assert len(r)==n,(name,len(r))
  assert len({(x['source_list'],x['candidate_key']) for x in r})==n
  assert all(x['verdict'] in {'VERIFIED','REJECT','STILL_UNCERTAIN','DUPLICATE_OF'} and x['settling_fact'] for x in r)
 for pid in [r['person_id'] for r in packet if r['person_id']]:
  assert sum(x['person_id']==pid for x in packet)==1
 # Known answers fetched on own pages:3 positives and2 injected defects.
 for u,q,n in [
 ('https://www.ceas.uc.edu/academics/departments/chemical-environmental-engineering/research/research.html','Asst Professor (F2)','Yavitt'),
 ('https://www.chemistry.ucla.edu/directory/sletten-ellen-m/','Professor','Sletten'),
 ('https://cheme.stanford.edu/people/danielle-mai','Assistant Professor of Chemical Engineering','Mai')]:
  t=get(u)['text'];assert found(t,q) and near(t,q,n)
 assert not found(t,'Assistant Professor FICTITIOUS-RANK')
 for text,quote in [('depolymerization','polymer'),('polymers','polymer'),('biomaterials','materials'),('polymer advanced synthesis','polymer synthesis')]:
  assert not found(text,quote),(text,quote)
 assert found('polymer, synthesis','polymer synthesis')
 assert not near(t,'Assistant Professor of Chemical Engineering','Yavitt')
 assert not near('Professor','Professor','Иван')
 assert identity('И. И. Попов')==('попов','попов')
 assert identity('José R. López')==identity('Jose Lopez')
 assert on_domain('https://profiles.stanford.edu/x',{'stanford.edu'})
 assert not on_domain('https://stanford.edu.evil.example/x',{'stanford.edu'})
 # Recheck every admitted quote against fetched raw page text, never old lane summaries.
 for r in packet:
  for g in ('a','b'):
   t=get(r[f'gate_{g}_url'])['text'];q=r[f'gate_{g}_quote']
   assert found(t,q),(r['full_name'],g)
   if g=='a':assert near(t,q,r['full_name'].split()[-1]),r['full_name']
 base=(HERE/'base_commit.txt').read_text().strip()
 def before(file):
  txt=subprocess.check_output(['git','show',f'{base}:data/{file}'],cwd=ROOT,text=True)
  return list(csv.DictReader(io.StringIO(txt)))
 old=before('people.csv');now=read(ROOT/'data/people.csv')
 oldid={r['person_id']:r for r in old};nowid={r['person_id']:r for r in now}
 changed={r['person_id'] for r in packet if r['person_id']}
 assert set(oldid)<=set(nowid),'people deleted'
 for pid,r in oldid.items():
  for k,v in r.items():
   if pid not in changed or k not in {'role','role_as_published','sources','last_verified'}:
    assert nowid[pid][k]==v,(pid,k,'unexpected edit')
 new=[r for r in now if r['person_id'] not in oldid]
 assert len(new)==sum(not r['person_id'] for r in packet)
 for r in new:
  assert not [p['person_id'] for p in now if p['person_id']!=r['person_id'] and norm(p['full_name'])==norm(r['full_name'])],r['full_name']
 ev=read(ROOT/'data/evidence_people.csv');old_ev=before('evidence_people.csv')
 evmap={r['evidence_id']:r for r in ev}
 assert all(evmap.get(r['evidence_id'])==r for r in old_ev),'existing evidence changed'
 assert len(ev)-len(old_ev)==3*len(packet)
 assert len({r['evidence_id'] for r in ev})==len(ev)
 for r in packet:require_claims(ev,r['allocated_person_id'])
 pid=next(r['allocated_person_id'] for r in packet if not r['person_id'])
 damaged=[e for e in ev if not(e['record_id']==pid and e['claim_type']=='parent')]
 try:require_claims(damaged,pid)
 except AssertionError:pass
 else:raise AssertionError('injected missing-parent defect did not fail')
 for f in (HERE/'reviewed.csv',ROOT/'data/evidence_people.csv'):
  assert '@' not in f.read_text(),'email or email-bearing URL'
 files=[ROOT/'data/people.csv',ROOT/'data/evidence_people.csv']
 hashes=[hashlib.sha256(f.read_bytes()).hexdigest() for f in files]
 subprocess.run([sys.executable,str(HERE/'build.py')],check=True,cwd=ROOT)
 assert hashes==[hashlib.sha256(f.read_bytes()).hexdigest() for f in files],'non-idempotent replay'
 print(f'PASS:79 census candidates;363 source title candidates;{len(packet)} reviewed people;{len(new)} creates;append-only evidence;3 positive+7 negative known answers;missing-parent mutation;raw quotes;byte-identical replay')
if __name__=='__main__':main()
